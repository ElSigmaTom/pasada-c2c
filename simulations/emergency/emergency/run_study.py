"""Matched emergency journeys; native SUMO, geometry-only beacon control, no blue-light shortcuts."""
import argparse,concurrent.futures,copy,csv,hashlib,json,math,os,pathlib,subprocess,sys,time,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'learning'))
import environment as em
from common import stage_plans,write_json,write_xml,write_csv
from beacon import Receiver,EmergencySupervisor
OUT=ROOT/'results/emergency_nov01';SEEDS=[7300,7301,7302]
CASES=[s+'_'+p for s in ['J1','J2','J3','CORRIDOR'] for p in ['AM','PM']]
ARMS=['fixed','local','priority20']

def approach_shape(net,edge):
 chain=[net.getEdge(edge)];seen={edge};length=chain[0].getLength()
 while length<260:
  current=chain[0];shape=current.getShape();d=(shape[1][0]-shape[0][0],shape[1][1]-shape[0][1]);dl=math.hypot(*d)
  if current.getFromNode().getType().startswith('traffic_light'):break
  candidates=[]
  for prev in current.getIncoming():
   if prev.getID() in seen or prev.getID().startswith(':') or not any(l.allows('passenger') for l in prev.getLanes()):continue
   s=prev.getShape();v=(s[-1][0]-s[-2][0],s[-1][1]-s[-2][1]);vl=math.hypot(*v)
   cosine=(v[0]*d[0]+v[1]*d[1])/max(1e-6,vl*dl)
   if cosine>.5:candidates.append((-cosine,prev.getID(),prev))
  if not candidates:break
  prev=sorted(candidates)[0][2];chain.insert(0,prev);seen.add(prev.getID());length+=prev.getLength()
 result=[]
 for edge in chain:
  for q in edge.getShape():
   if not result or math.dist(q,result[-1])>.01:result.append(list(q))
 return result

def prepare():
 import sumolib
 catalog=json.loads((ROOT/'model/sensors/catalog.json').read_text());moves=json.loads((ROOT/'data/reference_movements.json').read_text())
 net=sumolib.net.readNet(str(ROOT/'network/mandaue.net.xml'),withInternal=True)
 tree=ET.parse(ROOT/'scenarios/CORRIDOR_AM.rou.xml').getroot();candidates=[]
 for r in tree.findall('route'):
  es=r.get('edges').split();matched=[m for m in moves if any(a==m['from_gateway'] and b==m['to_gateway'] for a,b in zip(es,es[1:]))]
  if len(matched)!=3 or {m['site_id'] for m in matched}!={'J1','J2','J3'}:continue
  if not any(m['id'] in ['J3_m02','J3_m08'] for m in matched):continue
  candidates.append((sum(net.getEdge(e).getLength() for e in es),r.get('id'),matched))
 assert candidates,'No route through all sites and the A. Soriano/Ouano through movement'
 _,route_id,matched=min(candidates,key=lambda z:(z[0],z[1]));local_routes={m['site_id']:m['id'] for m in matched}
 manifest={'network_route':route_id,'isolated_movements':local_routes,'dispatch_s':1800,'selection':'Shortest existing simple three-site journey containing A. Soriano/Ouano through movement; local probes use its matching movement visits. Selected geometrically before performance runs.','cases':{}}
 for case in CASES:
  base=ROOT/'scenarios'/f'{case}.sumocfg';cfg=ET.parse(base).getroot();dest=ROOT/'emergency/inputs'/case;sd=dest/'scenarios';sd.mkdir(parents=True,exist_ok=True)
  route=(base.parent/cfg.find('input/route-files').get('value')).resolve();rt=ET.parse(route).getroot()
  original_n=len(rt.findall('vehicle'));typ=copy.deepcopy(rt.find('vType[@id="EMERGENCY_VEHICLE"]'));typ.set('id','EV_PROBE_TYPE');typ.set('guiShape','emergency');typ.set('color','1,0,0');ET.SubElement(typ,'param',key='has.bluelight.device',value='false');rt.insert(0,typ)
  rid=route_id if case.startswith('CORRIDOR') else local_routes[case.split('_')[0]]
  assert rt.find(f'route[@id="{rid}"]') is not None
  v=ET.Element('vehicle',id='EV_PROBE',type='EV_PROBE_TYPE',route=rid,depart='1800.000',departLane='free',departSpeed='0',departPosLat='free')
  ET.SubElement(v,'param',key='cohort',value='controlled_emergency_probe')
  vehicles=rt.findall('vehicle')
  for x in vehicles:rt.remove(x)
  vehicles.append(v);vehicles.sort(key=lambda x:(float(x.get('depart')),x.get('id')));rt.extend(vehicles)
  write_xml(sd/f'{case}.rou.xml',rt)
  for field in ['input/net-file','gui_only/gui-settings-file']:
   item=cfg.find(field);item.set('value',os.path.relpath((base.parent/item.get('value')).resolve(),sd).replace(os.sep,'/'))
  adds=cfg.find('input/additional-files');adds.set('value',','.join(os.path.relpath((base.parent/x).resolve(),sd).replace(os.sep,'/') for x in adds.get('value').split(',')))
  cfg.find('input/route-files').set('value',f'{case}.rou.xml');write_xml(sd/f'{case}.sumocfg',cfg)
  cp=dest/'model/sensors/catalog.json';cp.parent.mkdir(parents=True,exist_ok=True);cp.write_bytes((ROOT/'model/sensors/catalog.json').read_bytes())
  case_net=sumolib.net.readNet(str((sd/cfg.find('input/net-file').get('value')).resolve()),withInternal=True)
  sites=['J1','J2','J3'] if case.startswith('CORRIDOR') else [case.split('_')[0]]
  geom={s:{'tls':catalog[s]['tls'],'junction_polygon':[list(q) for q in case_net.getNode(catalog[s]['tls']).getShape()],'approaches':[approach_shape(case_net,x['approach_edge']) for x in stage_plans(s,case.split('_')[1])]} for s in sites}
  write_json(dest/'geometry.json',geom)
  manifest['cases'][case]={'probe_route':rid,'original_scheduled':original_n,'with_probe':original_n+1,'route_sha256':hashlib.sha256((sd/f'{case}.rou.xml').read_bytes()).hexdigest()}
 write_json(ROOT/'emergency/input_manifest.json',manifest);return manifest

class HookSupervisor(EmergencySupervisor):
 def tick(self,now,healthy):
  self.driver.before_tick(now)
  super().tick(now,healthy)

class EmergencyEnvironment(em.Environment):
 def push_states(self):
  super().push_states()
  if hasattr(self,'driver'):self.driver.after_states(self.now)

class Driver:
 def __init__(self,env,geometry,arm):
  self.env=env;self.arm=arm;self.enabled=arm.startswith('priority');self.receiver=Receiver(geometry,60. if arm=='priority60' else 20.)
  self.last_tick=-1;self.next_send=0.;self.sequence=0;self.pending=[];self.alive=False;self.depart=None;self.arrival=None;self.position_log=[];self.truth={};self.signal_index_stage={}
  for sid,c in env.controllers.items():
   self.signal_index_stage[sid]={idx:i for i,p in enumerate(c.plans) for idx,char in enumerate(p['green']) if char in 'gG'}
 def before_tick(self,now):
  if now==self.last_tick:return
  self.last_tick=now;c=self.env.conn
  if 'EV_PROBE' in c.simulation.getDepartedIDList():self.alive=True;self.depart=now
  if 'EV_PROBE' in c.simulation.getArrivedIDList():self.alive=False;self.arrival=now
  if self.alive:
   # getNextTLS is evaluator-only; Receiver sees only the packet below and provisioned geometry.
   upcoming=c.vehicle.getNextTLS('EV_PROBE');present=set()
   for tls,index,distance,state in upcoming:
    sid=next((s for s in self.env.sites if self.env.catalog[s]['tls']==tls),None)
    if sid is None:continue
    present.add(sid);stage=self.signal_index_stage[sid].get(index)
    if distance<=150 and sid not in self.truth:self.truth[sid]={'site':sid,'approach_start_s':now,'true_stage':stage,'stopline_pass_s':None}
   for sid,e in self.truth.items():
    if sid not in present and e['stopline_pass_s'] is None:e['stopline_pass_s']=now
   if now>=self.next_send:
    self.next_send=now+1.;self.sequence+=1;x,y=c.vehicle.getPosition('EV_PROBE')
    packet={'beacon':'REGISTERED_PROBE','vehicle':'EV_PROBE','authorized':True,'emergency_active':True,'session':1,'sequence':self.sequence,'time':now,'x':x,'y':y,'hacc':.5}
    self.pending.append((now+.5,packet));self.position_log.append({'time_s':now,'x':x,'y':y,'speed_m_s':c.vehicle.getSpeed('EV_PROBE'),'road':c.vehicle.getRoadID('EV_PROBE')})
  while self.pending and self.pending[0][0]<=now:
   _,packet=self.pending.pop(0);self.receiver.receive(packet,now)
  for sid,ctrl in self.env.controllers.items():
   request=self.receiver.active(sid,now)
   ctrl.set_request(request if self.enabled else None,now)
 def after_states(self,now):
  self.receiver.observe_green(self.env.controllers,now)

def run(case,arm,seed,tag='main',gui=False):
 import libsumo
 dest=ROOT/'emergency/inputs'/case
 folder=OUT/tag/f'seed{seed}'/case/arm if not gui else ROOT/'results/emergency_viewings'/str(time.time_ns())/case/arm
 if (folder/'emergency_metrics.json').exists():return json.loads((folder/'emergency_metrics.json').read_text())
 em.ROOT=dest
 if not gui:
  libsumo.getConnection=lambda label='default':libsumo;em.traci=libsumo
 env=EmergencyEnvironment(case,folder,'fixed' if arm=='fixed' else 'rule',seed,horizon=14400,gui=gui)
 env.controllers={s:HookSupervisor(stage_plans(s,env.period),'fixed' if arm=='fixed' else 'rule') for s in env.sites}
 driver=Driver(env,json.loads((dest/'geometry.json').read_text()),arm);env.driver=driver
 for ctrl in env.controllers.values():ctrl.driver=driver
 env.push_states()
 try:
  while env.now<14400:
   actions={s:env.observer.rule(s,c,env.now) if arm!='fixed' else 0 for s,c in env.controllers.items()}
   _,_,_,_=env.step(actions)
   if env.now>=4200 and driver.arrival is not None:break
 finally:metrics=env.close()
 from output_integrity import mirror_native_outputs
 mirror_native_outputs(folder)
 trips={t.get('id'):t.attrib for t in ET.parse(folder/'tripinfo.xml').getroot().findall('tripinfo')};ev=trips.get('EV_PROBE',{})
 import gzip
 probe={'scheduled_s':1800.,'completed':float(ev.get('arrival',-1))>=0,'depart_s':float(ev.get('depart',-1)),'arrival_s':float(ev.get('arrival',-1)),
 'dispatch_to_arrival_s':float(ev['arrival'])-1800 if float(ev.get('arrival',-1))>=0 else None,
 **{k:float(ev[k]) if float(ev.get('depart',-1))>=0 and k in ev else None for k in ['duration','departDelay','waitingTime','timeLoss','waitingCount','routeLength']}}
 route=ET.parse(dest/'scenarios'/f'{case}.rou.xml').getroot();book={v.get('id'):float(v.get('depart')) for v in route.findall('vehicle') if v.get('id')!='EV_PROBE' and 600<=float(v.get('depart'))<4200}
 counts={'completed':0,'active':0,'uninserted':0};accum=0.;background=[]
 for vid,scheduled in book.items():
  t=trips.get(vid,{});depart=float(t.get('depart',-1));arrival=float(t.get('arrival',-1))
  kind='completed' if 0<=arrival<=4200 else 'active' if 0<=depart<=4200 else 'uninserted'
  counts[kind]+=1;spent=(arrival if kind=='completed' else 4200)-scheduled;accum+=spent
  background.append({'id':vid,'scheduled_s':scheduled,'status_at_4200':kind,'accumulated_s':spent})
 errors=[]
 for sid,c in env.controllers.items():
  transitions=[{'time':0.,'stage':0,'aspect':'green'}]
  for event in c.events:
   if (event['stage'],event['aspect'])!=(transitions[-1]['stage'],transitions[-1]['aspect']):transitions.append(event)
  for a,b in zip(transitions,transitions[1:]):
   if a['aspect']=='yellow' and b['aspect']=='all_red' and abs(b['time']-a['time']-4)>1e-6:errors.append([sid,'yellow',a,b])
   if a['aspect']=='all_red' and b['aspect']=='green' and abs(b['time']-a['time']-4)>1e-6:errors.append([sid,'all_red',a,b])
   if a['aspect']=='green' and b['aspect']=='yellow' and b['time']-a['time']<10:errors.append([sid,'minimum_green',a,b])
 wrong=[];unverified=[]
 for sid,e in driver.receiver.encounters.items():
  actual=driver.truth.get(sid,{}).get('true_stage')
  if actual is None:unverified.append(sid)
  if actual is not None and actual!=e['stage']:wrong.append({'site':sid,'predicted':e['stage'],'true':actual})
 record={'case':case,'arm':arm,'seed':seed,'tag':tag,'actual_end_s':env.now,'beacon_cap_s':60 if arm=='priority60' else 20,'probe':probe,
 'ordinary_scheduled':len(book),'ordinary_counts':counts,'ordinary_mean_accumulated_s':accum/len(book),'ordinary_completion_percent':100*counts['completed']/len(book),
 'collisions':metrics['collision_events'],'teleports':metrics['teleports'],'phase_errors':errors,'wrong_approach_matches':wrong,'unverified_approach_matches':unverified,'encounters':driver.receiver.encounters,'ground_truth_encounters':driver.truth,
 'route_sha256':hashlib.sha256((dest/'scenarios'/f'{case}.rou.xml').read_bytes()).hexdigest(),'ordinary_measurement_cutoff_s':4200,
 'counterfactual_baseline':'fixed and local arms log eligible beacon observations but apply no priority','physical_beacon_verified':False}
 write_csv(folder/'ordinary_cohort.csv',background);write_csv(folder/'beacon_packets.csv',driver.receiver.packet_log);write_csv(folder/'probe_positions.csv',driver.position_log)
 write_json(folder/'beacon_events.json',driver.receiver.events);write_json(folder/'emergency_metrics.json',record)
 return record

def tasks():
 return [(c,a,s,'main') for s in SEEDS for c in CASES for a in ARMS]+[(c,'priority60',s,'cap_sensitivity') for s in SEEDS for c in ['J3_AM','J3_PM']]

def freeze():
 manifest=prepare();OUT.mkdir(parents=True,exist_ok=True)
 files=[ROOT/'emergency'/n for n in ['beacon.py','run_study.py','input_manifest.json','test_beacon.py']]
 files += [ROOT/'learning'/n for n in ['common.py','control.py','environment.py']]
 files += [p for prefix in ['emergency/inputs','scenarios','network','data','model/sensors'] for p in (ROOT/prefix).rglob('*') if p.is_file()]
 protocol={'version':'emergency-2026-11-01-v1','tasks':tasks(),'dispatch_s':1800,'demand':'Original full-count background plus ONE identical controlled probe in every arm; not an observed emergency incident.',
 'source':manifest,'cutoff_ordinary_s':4200,'maximum_EV_horizon_s':14400,'stopping':'After 4200 and EV arrival, else 14400; incomplete EVs remain censored.',
 'beacon':{'frequency_hz':1,'delivery_delay_s':.5,'freshness_s':3,'fix_window_s':5,'minimum_fixes':3,'nominal_error_bound_m':.5,'position_model':'Exact SUMO coordinates as ideal GNSS fixes; no sampled position noise or physical RF measurement.','gate_m':150,'heading_gate_degrees':45,'lateral_gate_m':12,'caps_s':[20,60],'cap_semantics':'Elapsed from first accepted request INCLUDING transition time. No renewal for the same site encounter.'},
 'control':'Protected stage transfer after >=10s green, 4s yellow, 4s all red; no abrupt conflicting green. Cyclic local operation resumes on release. No pedestrian inputs in this motor-only test.',
 'EV_behavior':'Same passenger-class 5m/2m ordinary driver proxy in all arms, emergency GUI shape only; no bluelight device, red-light exemption, speed/lane mode override or teleport.',
 'fingerprints':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
 target=OUT/'protocol.json'
 if target.exists():assert json.loads(target.read_text())==protocol,'Frozen protocol changed'
 else:write_json(target,protocol)
 return protocol

def launch(t):
 c,a,s,tag=t;folder=OUT/tag/f'seed{s}'/c/a;folder.mkdir(parents=True,exist_ok=True)
 proc=subprocess.run([sys.executable,__file__,'--case',c,'--arm',a,'--seed',str(s),'--tag',tag],capture_output=True,text=True)
 (folder/'execution.log').write_text(proc.stdout+proc.stderr)
 if proc.returncode:raise RuntimeError(str(t)+' '+(proc.stdout+proc.stderr)[-2000:])
 r=json.loads((folder/'emergency_metrics.json').read_text());print(json.dumps({'case':c,'arm':a,'seed':s,'end':r['actual_end_s'],'EV_s':r['probe']['dispatch_to_arrival_s'],'requests':len(r['encounters']),'wrong_matches':len(r['wrong_approach_matches']),'collisions':r['collisions']}),flush=True);return r

def main():
 p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');p.add_argument('--prepare',action='store_true');p.add_argument('--jobs',type=int,default=4);p.add_argument('--case',choices=CASES,default='J3_AM');p.add_argument('--arm',choices=ARMS+['priority60'],default='priority20');p.add_argument('--seed',type=int,default=7200);p.add_argument('--tag',default='pilot');p.add_argument('--gui',action='store_true');a=p.parse_args()
 if a.prepare:print(json.dumps(prepare()));return
 if a.all:
  freeze()
  with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:rows=list(pool.map(launch,tasks()))
  write_json(OUT/'measurements.json',rows);print('COMPLETED '+str(len(rows))+' emergency experiment runs',flush=True)
 else:
  if not (ROOT/'emergency/input_manifest.json').exists():prepare()
  print(json.dumps(run(a.case,a.arm,a.seed,a.tag,a.gui)),flush=True)
if __name__=='__main__':main()

