"""Ideal beacon packets, a geometry-only approach receiver and guarded preemption."""
import math
from collections import deque
import numpy as np
from control import Supervisor

def project(point,shape):
 best=None;travel=0.;total=sum(math.dist(a,b) for a,b in zip(shape,shape[1:]))
 for a,b in zip(shape,shape[1:]):
  dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
  if length<1e-6:continue
  raw=((point[0]-a[0])*dx+(point[1]-a[1])*dy)/(length*length);u=max(0.,min(1.,raw))
  closest=(a[0]+u*dx,a[1]+u*dy);dist=math.dist(point,closest)
  r={'distance':dist,'remaining':total-travel-u*length,'direction':(dx/length,dy/length),'raw':raw}
  if best is None or dist<best['distance']:best=r
  travel+=length
 return best

def inside(p,poly):
 x,y=p;flag=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:flag=not flag
 return flag

def outside_margin(p,poly,margin=5.):
 return not inside(p,poly) and min(project(p,[a,b])['distance'] for a,b in zip(poly,poly[1:]+poly[:1]))>margin

class Receiver:
 def __init__(self,geometry,cap=20.,gate=150.):
  self.geometry=geometry;self.cap=cap;self.gate=gate;self.fixes=deque();self.last_sequence=-1;self.events=[];self.encounters={};self.packet_log=[];self.last_fix=None
 def receive(self,p,now):
  reason=None
  if p.get('beacon')!='REGISTERED_PROBE' or p.get('vehicle')!='EV_PROBE' or not p.get('authorized') or not p.get('emergency_active'):reason='registration_or_active'
  elif p.get('session')!=1:reason='session'
  elif p['sequence']<=self.last_sequence:reason='duplicate_or_out_of_order'
  elif now-p['time']>3 or now<p['time']:reason='stale_or_future'
  elif not all(math.isfinite(p[k]) for k in ['x','y','hacc']) or p['hacc']<0:reason='bad_fix'
  if reason:
   self.packet_log.append({'received_s':now,**p,'status':reason});return
  self.last_sequence=p['sequence'];self.last_fix=p;self.fixes.append(p)
  while self.fixes and p['time']-self.fixes[0]['time']>5:self.fixes.popleft()
  pos=(p['x'],p['y']);motion=None
  if len(self.fixes)>=3:
   first=self.fixes[0];delta=(p['x']-first['x'],p['y']-first['y']);length=math.hypot(*delta)
   if length>first['hacc']+p['hacc']+1.:motion=(delta[0]/length,delta[1]/length)
  status='motion_valid' if motion is not None else 'no_reliable_heading'
  for sid,g in self.geometry.items():
   if sid in self.encounters:
    e=self.encounters[sid]
    if inside(pos,g['junction_polygon']):e['entered_polygon']=True
    if e['entered_polygon'] and e.get('release_s') is None and outside_margin(pos,g['junction_polygon']):
     self.release(sid,now,'GNSS_exit_boundary')
    continue
   if motion is None:continue
   candidates=[]
   for i,shape in enumerate(g['approaches']):
    z=project(pos,shape)
    if z and z['distance']<=12 and 0<=z['remaining']<=self.gate and np.dot(motion,z['direction'])>=math.cos(math.pi/4):
     candidates.append((z['distance'],i,z['remaining']))
   candidates.sort()
   if not candidates:continue
   if len(candidates)>1 and candidates[1][0]-candidates[0][0]<2:
    status='ambiguous_approach';continue
   _,stage,distance=candidates[0]
   e={'site':sid,'stage':stage,'request_s':now,'request_source_time_s':p['time'],'distance_at_request_m':distance,'expires_s':now+self.cap,'release_s':None,'release_reason':None,'entered_polygon':False,'first_compatible_green_s':None}
   self.encounters[sid]=e;self.events.append({'time_s':now,'site':sid,'kind':'qualified_request','stage':stage,'cap_s':self.cap});status='qualified'
  self.packet_log.append({'received_s':now,**p,'status':status})
 def release(self,sid,now,reason):
  e=self.encounters[sid]
  if e['release_s'] is None:
   e['release_s']=now;e['release_reason']=reason;self.events.append({'time_s':now,'site':sid,'kind':'release','reason':reason,'stage':e['stage']})
 def active(self,sid,now):
  e=self.encounters.get(sid)
  if e is None or e['release_s'] is not None:return None
  if now>=e['expires_s']:self.release(sid,now,'encounter_cap');return None
  if self.last_fix is None or now-self.last_fix['time']>3:self.release(sid,now,'stale_beacon');return None
  return e
 def observe_green(self,controllers,now):
  for sid,e in self.encounters.items():
   c=controllers[sid]
   if e['first_compatible_green_s'] is None and c.stage==e['stage'] and c.aspect=='green':e['first_compatible_green_s']=now

class EmergencySupervisor(Supervisor):
 def __init__(self,plans,mode):
  super().__init__(plans,mode);self.request=None;self.release_pending=False;self.was_priority=False
 def set_request(self,request,now):
  if self.request is not None and request is None and self.was_priority:
   self.release_pending=True;self.events.append({'time':now,'stage':self.stage,'aspect':self.aspect,'reason':'beacon request released'})
  self.request=request
 def command(self,now,action):
  if self.request is not None or self.release_pending:return
  super().command(now,action)
 def tick(self,now,healthy):
  if self.request is None and not self.release_pending:
   self.was_priority=False;return super().tick(now,healthy)
  # A failed puck does not disable a healthy coordinator's beacon input.
  if not healthy:
   self.fallback=True;self.healthy_since=None
  elif self.fallback and self.healthy_since is None:self.healthy_since=now
  elapsed=now-self.since;target=None if self.request is None else self.request['stage']
  if self.aspect=='green':
   if target==self.stage:
    self.was_priority=True
    if elapsed>=self.maximum():self.change('yellow',now,'beacon maximum green')
   elif elapsed>=self.minimum():
    self.change('yellow',now,'beacon transfer' if target is not None else 'beacon release clearance')
  elif self.aspect=='yellow' and elapsed>=4:self.change('all_red',now,'yellow completed')
  elif self.aspect=='all_red' and elapsed>=4:
   self.stage=target if target is not None else (self.stage+1)%4
   self.release_pending=False;self.was_priority=target is not None
   self.change('green',now,'beacon priority green' if target is not None else 'beacon cyclic return')

