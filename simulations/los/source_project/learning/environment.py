"""TraCI environment: observations from point detectors, truth for reward/audit only."""
import copy,hashlib,math,os,random,time,xml.etree.ElementTree as ET
import numpy as np
from common import *
from control import Supervisor,PuckObserver

class Environment:
 def __init__(self,case,folder,mode='rule',seed=42,horizon=4200,scale=1.,jitter=0.,miss=0.,false_rate=0.,gui=False,fault=None,truth_audit=False):
  self.case=case;self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True);self.mode=mode;self.seed=seed;self.horizon=horizon;self.scale=scale;self.gui=gui;self.fault=fault;self.truth_audit=truth_audit
  self.sites=SITES if case.startswith('CORRIDOR') else [case.split('_')[0]];self.period=case.split('_')[-1]
  all_catalog=json.loads((ROOT/'model/sensors/catalog.json').read_text());self.catalog={s:all_catalog[s] for s in self.sites}
  source=ROOT/f'scenarios/{case}.sumocfg';cfg=ET.parse(source).getroot()
  def relative(path):return os.path.relpath(path,self.folder).replace(os.sep,'/')
  net=(source.parent/cfg.find('input/net-file').get('value')).resolve();cfg.find('input/net-file').set('value',relative(net))
  route=(source.parent/cfg.find('input/route-files').get('value')).resolve()
  if scale!=1 or jitter:
   routes=ET.parse(route).getroot();rng=random.Random(seed*101+17);vehicles=[]
   for v in list(routes.findall('vehicle')):
    routes.remove(v)
    if rng.random()>scale:continue
    depart=max(0,float(v.get('depart'))+rng.uniform(-jitter,jitter))
    if depart>=horizon:continue
    v.set('depart',f'{depart:.3f}');vehicles.append(v)
   vehicles.sort(key=lambda v:float(v.get('depart')));routes.extend(vehicles);write_xml(self.folder/'demand.rou.xml',routes);route=self.folder/'demand.rou.xml'
  self.scheduled=[float(v.get('depart')) for v in ET.parse(route).getroot().findall('vehicle')]
  self.scheduled_due=sum(x<horizon for x in self.scheduled)
  cfg.find('input/route-files').set('value',relative(route))
  additions=[(source.parent/x).resolve() for x in cfg.find('input/additional-files').get('value').split(',') if not x.endswith('_crossings.add.xml')]
  sensor_xml=ET.Element('additional')
  for c in self.catalog.values():
   for row in c['rows']:
    for i,lane in enumerate(row['lanes']):ET.SubElement(sensor_xml,'inductionLoop',id=row['id']+f'_L{i}',lane=lane,pos=str(row['pos_m']),length='0',period='60',file='NUL' if os.name=='nt' else '/dev/null',friendlyPos='true')
  write_xml(self.folder/'pucks.add.xml',sensor_xml);additions.append(self.folder/'pucks.add.xml')
  cfg.find('input/additional-files').set('value',','.join(relative(a) for a in additions))
  cfg.find('time/end').set('value',str(horizon));cfg.find('processing/scale').set('value','1');cfg.find('random_number/seed').set('value',str(seed))
  for child in cfg.find('output'):
   if child.tag.endswith('-output'):child.set('value',Path(child.get('value')).name)
  cfg.find('report/error-log').set('value','warnings.log')
  settings=cfg.find('gui_only/gui-settings-file');settings.set('value',relative((source.parent/settings.get('value')).resolve()))
  write_xml(self.folder/'run.sumocfg',cfg)
  self.log=(self.folder/'sumo.log').open('w');label='pasada_'+str(os.getpid())+'_'+str(time.time_ns())
  cmd=[find_binary(gui),'-c',str(self.folder/'run.sumocfg'),'--no-step-log','true','--start','--quit-on-end']
  if gui:cmd+=['--delay','30']
  traci.start(cmd,label=label,stdout=self.log);self.conn=traci.getConnection(label)
  self.observer=PuckObserver(self.catalog,seed+900,miss,false_rate,initial_stock_known=True);self.observer.subscribe(self.conn)
  self.controllers={s:Supervisor(stage_plans(s,self.period),mode) for s in self.sites}
  self.states={};self.now=0.;self.inserted=0;self.arrived=0;self.cost=0.;self.teleports=0;self.collision_steps=0;self.trace=[];self.audit=[];self.return_sum=0.;self.started=time.time();self.next_truth=0.
  route_tree=ET.parse(route).getroot();used=sorted({e for r in route_tree.findall('route') for e in r.get('edges').split()})
  for e in used:self.conn.edge.subscribe(e,[traci.constants.LAST_STEP_VEHICLE_HALTING_NUMBER])
  self.halting_var=traci.constants.LAST_STEP_VEHICLE_HALTING_NUMBER
  self.push_states()
 def push_states(self):
  for s,c in self.controllers.items():
   state=c.state()
   if state!=self.states.get(s):self.conn.trafficlight.setRedYellowGreenState(self.catalog[s]['tls'],state);self.states[s]=state
 def observations(self):return {s:self.observer.features(s,c,self.now) for s,c in self.controllers.items()}
 def masks(self):return {s:c.mask(self.now) for s,c in self.controllers.items()}
 def stock_truth(self,sid):
  c=self.catalog[sid];full=set(c['region_full_edges']);part=c['region_partial_edges'];nodes=c['region_nodes'];total=0
  for v in self.conn.vehicle.getIDList():
   edge=self.conn.vehicle.getRoadID(v)
   if edge in full or any(edge.startswith(':'+n+'_') for n in nodes):total+=1
   elif edge in part:
    pos=self.conn.vehicle.getLanePosition(v);b=part[edge]
    if (b['sign']==1 and pos>=b['pos_m']) or (b['sign']==-1 and pos<b['pos_m']):total+=1
  return total
 def step(self,actions):
  for s,c in self.controllers.items():c.command(self.now,int(actions.get(s,0)))
  self.push_states();until=min(self.horizon,self.now+5)
  while self.now<until-1e-8:
   self.conn.simulationStep();self.now=float(self.conn.simulation.getTime());dt=.5
   self.inserted+=self.conn.simulation.getDepartedNumber();self.arrived+=self.conn.simulation.getArrivedNumber()
   self.teleports+=self.conn.simulation.getStartingTeleportNumber();self.collision_steps+=int(self.conn.simulation.getCollidingVehiclesNumber()>0)
   bad=None
   if self.fault and self.fault['start']<=self.now<self.fault['end']:
    sid=self.fault['site'];bad=self.catalog[sid]['boundary_in'][0]
   self.observer.update(self.conn.inductionloop.getAllSubscriptionResults(),self.now,dt,bad)
   for s,c in self.controllers.items():c.tick(self.now,self.observer.healthy(s,self.now))
   self.push_states()
  edge_results=self.conn.edge.getAllSubscriptionResults();halt=sum(int(v.get(self.halting_var,0)) for v in edge_results.values());pending=len(self.conn.simulation.getPendingVehicles());running=self.conn.vehicle.getIDCount()
  step_cost=5*(halt+pending+.05*running);self.cost+=step_cost;reward=max(-20.,-step_cost/500);self.return_sum+=reward
  for s,c in self.controllers.items():
   self.trace.append({'time_s':self.now,'site':s,'stage':c.stage,'aspect':c.aspect,'fallback':c.fallback,'healthy':self.observer.healthy(s,self.now),'boundary_entries':sum(self.observer.count[r] for r in self.catalog[s]['boundary_in']),'boundary_exits':sum(self.observer.count[r] for r in self.catalog[s]['boundary_out']),'stock_raw':self.observer.stock[s],'stock_negative_ever':self.observer.minimum[s]<0,'absolute_stock_initialized':self.observer.initial_stock_known[s],'halting_network':halt,'pending_insertion':pending,'arrived_cumulative':self.arrived})
  if self.truth_audit and self.now>=self.next_truth:
   for s in self.sites:
    truth=self.stock_truth(s);self.audit.append({'time_s':self.now,'site':s,'estimated_stock_raw':self.observer.stock[s],'truth_stock':truth,'error':self.observer.stock[s]-truth})
   self.next_truth=self.now+30
  terminal=self.conn.simulation.getMinExpectedNumber()==0
  return self.observations(),reward,terminal,self.now>=self.horizon
 def close(self):
  self.conn.close();self.log.close()
  root=ET.parse(self.folder/'tripinfo.xml').getroot();trips=root.findall('tripinfo');arrived=[t for t in trips if float(t.get('arrival'))>=0];unfinished=[t for t in trips if float(t.get('depart'))>=0 and float(t.get('arrival'))<0];undeparted=[t for t in trips if float(t.get('depart'))<0 and float(t.get('departDelay',0))>=0]
  collisions=ET.parse(self.folder/'collisions.xml').getroot().findall('collision')
  def avg(key):return float(np.mean([float(t.get(key)) for t in arrived])) if arrived else None
  def due(t):
   # Output includes undeparted trips; only departures due within this horizon matter.
   return float(t.get('depart'))>=0
  residual=max(0,self.scheduled_due-len(arrived)-len(unfinished))
  metrics={'case':self.case,'mode':self.mode,'seed':self.seed,'horizon_s':self.horizon,'training_load_scale':self.scale,'scheduled_due':self.scheduled_due,'inserted':self.inserted,'arrived':len(arrived),'unfinished':len(unfinished),'uninserted_due':residual,'completed_only_mean_wait_s':avg('waitingTime'),'completed_only_mean_time_loss_s':avg('timeLoss'),'completed_only_mean_duration_s':avg('duration'),'cost_vehicle_seconds_sampled':self.cost,'reward_sum':self.return_sum,'collision_events':len(collisions),'teleports':self.teleports,'wall_s':round(time.time()-self.started,3),'field_validated':False,'sensor_miss_probability':self.observer.miss,'false_pulses_per_row_second':self.observer.false_rate,'absolute_stock_initialized_at_end':self.observer.initial_stock_known,'observer_min_raw':self.observer.minimum,'observer_max_raw':self.observer.maximum,'fault':self.fault,'stock_truth_max_abs_error':max((abs(a['error']) for a in self.audit),default=None)}
  write_json(self.folder/'metrics.json',metrics);write_csv(self.folder/'sensor_trace.csv',self.trace)
  if self.audit:write_csv(self.folder/'stock_truth_audit.csv',self.audit)
  write_json(self.folder/'supervisor_events.json',{s:c.events for s,c in self.controllers.items()})
  return metrics
