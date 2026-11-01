"""Four-stage cyclic supervisor and pulse-count conservation observer."""
from collections import deque
import numpy as np

class Supervisor:
 def __init__(self,plans,mode):
  self.plans=plans;self.mode=mode;self.stage=0;self.aspect='green';self.since=0.;self.last_green=[0.]*4;self.fallback=False;self.fault_clear=False;self.healthy_since=None;self.recovery_s=60.;self.events=[]
 def minimum(self):return 10.
 def maximum(self):return max(30.,min(180.,2*self.plans[self.stage]['duration']))
 def legal(self,now):return self.aspect=='green' and now-self.since>=self.minimum()
 def mask(self,now):return np.array([True,self.legal(now)])
 def state(self):return self.plans[self.stage][self.aspect]
 def change(self,aspect,now,reason):
  self.aspect=aspect;self.since=now;self.events.append({'time':now,'stage':self.stage,'aspect':aspect,'reason':reason})
  if aspect=='green':
   self.last_green[self.stage]=now;self.fault_clear=False
 def command(self,now,action):
  if self.mode!='fixed' and not self.fallback and action==1 and self.legal(now):self.change('yellow',now,'policy advance')
 def tick(self,now,healthy):
  if not healthy:
   if not self.fallback:
    self.events.append({'time':now,'stage':self.stage,'aspect':self.aspect,'reason':'whole-intersection fallback'});self.fault_clear=True
   self.fallback=True;self.healthy_since=None
  elif self.fallback and self.healthy_since is None:self.healthy_since=now
  elapsed=now-self.since
  if self.aspect=='green':
   fixed=self.mode=='fixed' or self.fallback
   limit=self.plans[self.stage]['duration'] if fixed else self.maximum()
   # A newly detected fault can safely finish minimum green then clear to fixed control.
   if self.fallback and self.fault_clear:limit=min(limit,self.minimum())
   if elapsed>=limit:self.change('yellow',now,'fixed boundary' if fixed else 'maximum green')
  elif self.aspect=='yellow' and elapsed>=4:self.change('all_red',now,'yellow completed')
  elif self.aspect=='all_red' and elapsed>=4:
   self.stage=(self.stage+1)%4
   if healthy and self.fallback and self.healthy_since is not None and now-self.healthy_since>=self.recovery_s:
    self.fallback=False;self.events.append({'time':now,'stage':self.stage,'aspect':self.aspect,'reason':'healthy recovery at stage boundary'})
   self.change('green',now,'clearance completed')

class PuckObserver:
 def __init__(self,catalog,seed=0,miss=0.,false_rate=0.,omit_side=False,initial_stock_known=False):
  self.initial_stock_known={sid:initial_stock_known for sid in catalog};self.catalog=catalog;self.rng=np.random.default_rng(seed);self.miss=miss;self.false_rate=false_rate;self.omit_side=omit_side
  self.rows={r['id']:r for c in catalog.values() for r in c['rows']};self.seen={r:set() for r in self.rows};self.count={r:0 for r in self.rows};self.history={r:deque() for r in self.rows};self.occ={r:0. for r in self.rows};self.heartbeat={r:0. for r in self.rows};self.stock={s:0 for s in catalog};self.minimum={s:0 for s in catalog};self.maximum={s:0 for s in catalog};self.closed={s:not omit_side for s in catalog}
 def subscribe(self,conn):
  tc=conn.constants if hasattr(conn,'constants') else __import__('traci').constants
  self.id_var=tc.LAST_STEP_VEHICLE_ID_LIST;self.occ_var=tc.LAST_STEP_OCCUPANCY
  for row in self.rows.values():
   for i in range(len(row['lanes'])):conn.inductionloop.subscribe(row['id']+f'_L{i}',[self.id_var,self.occ_var])
 def update(self,results,now,dt,fault_row=None):
  for rid,row in self.rows.items():
   sid=rid.split('_')[0]
   if self.omit_side and rid in self.catalog[sid]['extra_side_rows']:continue
   if rid==fault_row:continue
   if any(rid+f'_L{i}' not in results for i in range(len(row['lanes']))):continue
   self.heartbeat[rid]=now
   ids=set();occs=[]
   for i in range(len(row['lanes'])):
    value=results.get(rid+f'_L{i}',{});ids.update(value.get(self.id_var,[]) or []);occs.append(float(value.get(self.occ_var,0))/100)
   # IDs implement an ideal passage-event backend only; identities never enter model features.
   new=ids-self.seen[rid];self.seen[rid].update(ids)
   n=int(self.rng.binomial(len(new),1-self.miss))+int(self.rng.poisson(self.false_rate*dt))
   self.count[rid]+=n;self.history[rid].append((now,n))
   while self.history[rid] and self.history[rid][0][0]<now-10:self.history[rid].popleft()
   # Smooth point occupancy over ~5 seconds; no simulator speed or queue query.
   mean=sum(occs)/max(1,len(occs));self.occ[rid]+=(1-np.exp(-dt/5))*(mean-self.occ[rid])
  for sid,c in self.catalog.items():
   self.stock[sid]=sum(self.count[r] for r in c['boundary_in'])-sum(self.count[r] for r in c['boundary_out'])
   self.minimum[sid]=min(self.minimum[sid],self.stock[sid]);self.maximum[sid]=max(self.maximum[sid],self.stock[sid])
   if not self.healthy(sid,now):self.initial_stock_known[sid]=False  # dead puck implies unrecoverable passages unless independently reconciled
 def rate(self,rid):return sum(n for _,n in self.history[rid])/10
 def healthy(self,sid,now):
  required=[r['id'] for r in self.catalog[sid]['rows'] if not (self.omit_side and r['id'] in self.catalog[sid]['extra_side_rows'])]
  return all(now-self.heartbeat[r]<=3. for r in required)
 def features(self,sid,ctrl,now):
  c=self.catalog[sid];x=[]
  for i,rows in enumerate(c['stage_rows']):
   lanes=max(1,c['stage_lane_counts'][i]);out=c['stage_outputs'][i]
   x.extend([self.occ[rows[str(o)]] for o in [5,30,60]])
   x.extend([min(2,self.rate(rows['60'])/lanes),min(2,self.rate(rows['5'])/lanes),max((self.occ[r] for r in out),default=0),min(2,(now-ctrl.last_green[i])/300),lanes/4])
  x.extend([float(ctrl.stage==i) for i in range(4)])
  elapsed=(now-ctrl.since)/max(10,ctrl.plans[ctrl.stage]['duration']) if ctrl.aspect=='green' else -1.
  trusted=self.initial_stock_known[sid] and self.miss==0 and self.false_rate==0 and self.closed[sid] and self.minimum[sid]>=0 and self.healthy(sid,now)
  stock=max(0,self.stock[sid])/c['stock_scale_vehicles'] if self.closed[sid] and self.initial_stock_known[sid] else 0
  netflow=sum(self.rate(r) for r in c['boundary_in'])-sum(self.rate(r) for r in c['boundary_out'])
  x.extend([min(2,elapsed),min(3,stock),max(-2,min(2,netflow/5)) if self.closed[sid] else 0,float(trusted)])
  x=np.asarray(x,np.float32);assert x.shape==(40,) and np.all(np.isfinite(x));return x
 def rule(self,sid,ctrl,now):
  if not ctrl.legal(now):return 0
  x=self.features(sid,ctrl,now);scores=[]
  for i in range(4):
   z=x[i*8:(i+1)*8];scores.append(10*(z[0]+2*z[1]+3*z[2])+z[3]-8*z[5])
  current=ctrl.stage;other=(current+1)%4
  return int(scores[other]>scores[current]+3 or (scores[current]<.5 and scores[other]>.5))
