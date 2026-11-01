"""Matched motor-only fixed/PASADA rule comparison. No training or parameter search.
Run from the project root: python measurement/paired_study.py --all --jobs 4
Each fresh run is retained, including failures. Original releases are not overwritten.
"""
import argparse, concurrent.futures, csv, hashlib, json, os, pathlib, statistics, subprocess, sys, time, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'learning'))
OUT=ROOT/'results/paired_nov01'
SEEDS=[7100,7101,7102]
CASES=[s+'_'+p for s in ['J1','J2','J3','CORRIDOR'] for p in ['AM','PM']]

def write_json(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2))
def write_csv(p,rows):
 if not rows:return
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def setup():
 OUT.mkdir(parents=True,exist_ok=True)
 files=[p for folder in ['scenarios','network','data','model/sensors'] for p in (ROOT/folder).rglob('*') if p.is_file()]
 files += [ROOT/'learning'/n for n in ['common.py','control.py','environment.py']]+[pathlib.Path(__file__)]
 protocol={'protocol':'paired-local-rule-2026-11-01-v1','controllers':['fixed','rule'],'seeds':SEEDS,'cases':CASES,
 'selection':'Existing transparent rule fixed before these measurements; no fitting or learned-checkpoint selection.',
 'demand_scale':1.0,'warmup_s':600,'study_s':[600,4200],'cutoff_s':4200,'step_s':0.5,'sample_s':5,
 'primary':'Study-cohort mean accumulated scheduled-to-exit time at common cutoff, including unfinished and uninserted trips; a restricted lower bound, not an estimate of eventual travel time.',
 'secondary':['completed-cohort duration and p95','completed-cohort waitingTime/timeLoss/waitingCount','study-hour arrivals','study-cohort completion/active/uninserted counts','incoming-approach halting vehicles and farthest-stopped tail extent'],
 'source_scope':'Team manual hourly class/site marginals; reconstructed routes/arrival times and conditional fixed signal program; lane-based motor-only model.',
 'queue_definition':'Incoming approach halting count at speed <=0.1 m/s sampled every5s; tail extent is distance from lane end to rearmost stopped vehicle rear on modeled incoming edges. Exact SUMO state is evaluation-only.',
 'acceptance':'Finite motor-only simulation diagnostics, not full Table4 field/pedestrian acceptance. Any collision/teleport is retained and flagged; no failed seed removed.',
 'fingerprints':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
 target=OUT/'protocol.json'
 if target.exists():
  old=json.loads(target.read_text());assert old==protocol,'Protocol changed; use a new output version.'
 else:write_json(target,protocol)
 return protocol

def inputs(case):
 cfg=ROOT/'scenarios'/f'{case}.sumocfg';r=ET.parse(cfg).getroot()
 path=(cfg.parent/r.find('input/route-files').get('value')).resolve()
 book={v.get('id'):{'scheduled':float(v.get('depart')),'class':v.get('type'),'route':v.get('route')} for v in ET.parse(path).getroot().findall('vehicle')}
 return book,path

def run(case,mode,seed,gui=False):
 import numpy as np
 import environment as em
 if not gui:
  import libsumo
  libsumo.getConnection=lambda label='default':libsumo
  em.traci=libsumo
 from common import stage_plans
 folder=OUT/f'seed{seed}'/case/mode
 if (folder/'measurement.json').exists():
  return json.loads((folder/'measurement.json').read_text())
 book,route=inputs(case)
 cohort={k:v for k,v in book.items() if 600<=v['scheduled']<4200}
 env=em.Environment(case,folder,mode,seed,horizon=4200,gui=gui)
 # Ground-truth evaluation channels never enter PuckObserver.rule.
 groups={}
 for sid in env.sites:
  for i,stage in enumerate(stage_plans(sid,env.period)):
   edge=stage['approach_edge']
   lanes=sorted({v[0] for links in env.conn.trafficlight.getControlledLinks(env.catalog[sid]['tls']) for v in links if v and v[0].rsplit('_',1)[0]==edge})
   assert lanes,(sid,edge)
   groups[(sid,i)]=lanes
 lengths={l:env.conn.lane.getLength(l) for ls in groups.values() for l in ls}
 samples=[]
 try:
  while env.now<4200:
   actions={s:env.observer.rule(s,c,env.now) if mode=='rule' else 0 for s,c in env.controllers.items()}
   obs,reward,terminal,truncated=env.step(actions)
   if env.now>600:
    for (sid,stage),lanes in groups.items():
     halt=0;tails=[]
     for lane in lanes:
      halt+=env.conn.lane.getLastStepHaltingNumber(lane)
      stopped=[v for v in env.conn.lane.getLastStepVehicleIDs(lane) if env.conn.vehicle.getSpeed(v)<=0.1]
      tail=max((lengths[lane]-env.conn.vehicle.getLanePosition(v)+env.conn.vehicle.getLength(v) for v in stopped),default=0.)
      tails.append(tail)
     samples.append({'time_s':env.now,'site':sid,'stage':stage,'halting_vehicles':halt,'tail_extent_m':round(max(tails,default=0),3)})
   if terminal or truncated:break
 finally:metrics=env.close()
 trips={t.get('id'):t.attrib for t in ET.parse(folder/'tripinfo.xml').getroot().findall('tripinfo')}
 assert len(trips)==len(set(trips))
 completed=[];active=0;uninserted=0;accum=0.;triprows=[]
 for vid,v in cohort.items():
  t=trips.get(vid,{});dep=float(t.get('depart',-1));arr=float(t.get('arrival',-1))
  status='completed' if arr>=0 else 'active' if dep>=0 else 'uninserted'
  if status=='completed':completed.append(t)
  elif status=='active':active+=1
  else:uninserted+=1
  spent=(arr if arr>=0 else 4200)-v['scheduled'];assert spent>=-1e-5;accum+=spent
  triprows.append({'id':vid,'class':v['class'],'scheduled_s':v['scheduled'],'status':status,'depart_s':dep,'arrival_s':arr,'accumulated_time_at_cutoff_s':spent,
   **{k:float(t[k]) if k in t and dep>=0 else None for k in ['duration','departDelay','waitingTime','timeLoss','waitingCount','routeLength']}})
 def mean(key):return float(np.mean([float(t[key]) for t in completed])) if completed else None
 def p95(key):return float(np.percentile([float(t[key]) for t in completed],95)) if completed else None
 # A sample sums each physical approach once across the selected network.
 bytime={}
 for r in samples:bytime[r['time_s']]=bytime.get(r['time_s'],0)+r['halting_vehicles']
 queues=list(bytime.values())
 phase_errors=[]
 for sid,c in env.controllers.items():
  ev=c.events
  for prev,nxt in zip(ev,ev[1:]):
   if prev['aspect']=='yellow' and abs(nxt['time']-prev['time']-4)>1e-6:phase_errors.append([sid,'yellow',prev,nxt])
   if prev['aspect']=='all_red' and abs(nxt['time']-prev['time']-4)>1e-6:phase_errors.append([sid,'all_red',prev,nxt])
   if prev['aspect']=='green' and nxt['aspect']=='yellow' and nxt['time']-prev['time']<10:phase_errors.append([sid,'min_green',prev,nxt])
  greens=[x['stage'] for x in ev if x['aspect']=='green']
  if any(b!=(a+1)%4 for a,b in zip(greens,greens[1:])):phase_errors.append([sid,'cycle'])
 record={**metrics,'measurement_version':'paired-local-rule-2026-11-01-v1','study_cohort_scheduled':len(cohort),'study_cohort_completed':len(completed),'study_cohort_active':active,'study_cohort_uninserted':uninserted,
 'study_completion_percent':100*len(completed)/len(cohort),'study_all_vehicle_accumulated_s':accum,'study_mean_accumulated_s':accum/len(cohort),
 'study_completed_mean_duration_s':mean('duration'),'study_completed_p95_duration_s':p95('duration'),'study_completed_mean_depart_delay_s':mean('departDelay'),
 'study_completed_mean_wait_s':mean('waitingTime'),'study_completed_mean_time_loss_s':mean('timeLoss'),'study_completed_mean_stops':mean('waitingCount'),
 'study_hour_exits_all_cohorts':sum(600<=float(t.get('arrival',-1))<=4200 for t in trips.values()),
 'study_mean_approach_halting_vehicles':float(np.mean(queues)),'study_p95_approach_halting_vehicles':float(np.percentile(queues,95)),'study_max_approach_halting_vehicles':max(queues),
 'study_max_tail_extent_m':max(r['tail_extent_m'] for r in samples),'queue_sample_times':len(queues),'phase_errors':phase_errors,'route_sha256':hashlib.sha256(route.read_bytes()).hexdigest()}
 assert len(cohort)==len(completed)+active+uninserted
 assert metrics['scheduled_due']==metrics['arrived']+metrics['unfinished']+metrics['uninserted_due']
 write_csv(folder/'cohort_trips.csv',triprows);write_csv(folder/'approach_queues.csv',samples);write_json(folder/'measurement.json',record)
 from output_integrity import mirror_native_outputs
 mirror_native_outputs(folder)
 return record

def launch(task):
 case,mode,seed=task
 cmd=[sys.executable,str(pathlib.Path(__file__).resolve()),'--case',case,'--mode',mode,'--seed',str(seed)]
 proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 folder=OUT/f'seed{seed}'/case/mode
 (folder/'execution.log').write_text(proc.stdout)
 if proc.returncode:raise RuntimeError(f'{task}: {proc.stdout[-2500:]}')
 r=json.loads((folder/'measurement.json').read_text())
 print(json.dumps({k:r[k] for k in ['case','mode','seed','study_cohort_completed','study_cohort_uninserted','collision_events','wall_s']}),flush=True)
 return r

def main():
 p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');p.add_argument('--jobs',type=int,default=4);p.add_argument('--case',choices=CASES);p.add_argument('--mode',choices=['fixed','rule']);p.add_argument('--seed',type=int,default=7100);p.add_argument('--gui',action='store_true');a=p.parse_args()
 if a.all:
  setup();tasks=[(case,mode,seed) for seed in SEEDS for case in CASES for mode in ['fixed','rule']]
  with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:rows=list(pool.map(launch,tasks))
  write_json(OUT/'run_measurements.json',rows);write_csv(OUT/'run_measurements.csv',[{k:v for k,v in r.items() if not isinstance(v,(dict,list))} for r in rows])
  print('COMPLETED '+str(len(rows))+' paired experiment runs',flush=True)
 else:
  assert a.case and a.mode
  print(json.dumps(run(a.case,a.mode,a.seed,a.gui)),flush=True)
if __name__=='__main__':main()

