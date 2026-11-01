import sys, pathlib, json, gzip, time, math, argparse
p=argparse.ArgumentParser(description='Observer-only 1Hz traffic capture from the frozen LEAR study source, without changing controller inputs.')
p.add_argument('--source',type=pathlib.Path,required=True,help='Extracted LEAR_SUMO_Simulations directory')
p.add_argument('--output',type=pathlib.Path,required=True,help='Fresh capture-output directory')
p.add_argument('--case',required=True,choices=[s+'_AM' for s in ['J1','J2','J3','CORRIDOR']])
p.add_argument('--arm',required=True,choices=['fixed','rule'])
a=p.parse_args()
root=a.source.resolve()
sys.path.insert(0,str(root/'learning'))
import libsumo, environment as em
libsumo.getConnection=lambda label='default':libsumo
em.traci=libsumo
case=a.case;mode=a.arm
out=a.output.resolve()/case/mode
if out.exists():raise RuntimeError("Capture destination already exists; select a fresh output directory.")
out.mkdir(parents=True)
start=time.monotonic();env=em.Environment(case,out,mode,7100,horizon=4200)
frames=[];ids=[];idmap={};vehicles={};tstep=libsumo.simulationStep
V=libsumo.vehicle;C=libsumo.constants
vars=[C.VAR_POSITION,C.VAR_ANGLE,C.VAR_LENGTH,C.VAR_WIDTH,C.VAR_TYPE]
def observe(*args,**kwargs):
 tstep(*args,**kwargs);t=libsumo.simulation.getTime()
 if 1200<=t<=2400 and t==int(t):
  present=set(V.getIDList())
  for v in present-idmap.keys():
   idmap[v]=len(ids);ids.append(v);V.subscribe(v,vars)
  states=V.getAllSubscriptionResults();rows=[]
  for v in sorted(present):
   vals=states.get(v,{})
   if C.VAR_POSITION not in vals:continue
   x,y=vals[C.VAR_POSITION];i=idmap[v]
   vehicles[str(i)]=[round(vals[C.VAR_LENGTH],2),round(vals[C.VAR_WIDTH],2),str(vals[C.VAR_TYPE])]
   rows.append([i,round(x,2),round(y,2),round(vals[C.VAR_ANGLE],1)])
  frames.append([int(t),rows])
libsumo.simulationStep=observe
try:
 while env.now<4200:
  actions={s:env.observer.rule(s,c,env.now) if mode=='rule' else 0 for s,c in env.controllers.items()}
  _,_,term,trunc=env.step(actions)
  if term or trunc:break
finally:
 metrics=env.close()
libsumo.simulationStep=tstep
payload={'schema':'pasada.motion-capture/1','case':case,'arm':mode,'seed':7100,'capture_window_s':[1200,2400],'sample_s':1,'position_reference':'SUMO front bumper center; x/y metres in native network','provenance':'Observer-only deterministic reproduction from frozen LEAR source; compare archived sensor trace before release. Not historical FCD.','vehicle_ids':ids,'vehicles':vehicles,'frames':frames}
p=out/'motion.json.gz'
with gzip.open(p,'wt',encoding='utf-8') as f:json.dump(payload,f,separators=(',',':'))
print(json.dumps({'case':case,'mode':mode,'frames':len(frames),'bytes':p.stat().st_size,'wall_s':round(time.monotonic()-start,2),'metrics':metrics}),flush=True)
