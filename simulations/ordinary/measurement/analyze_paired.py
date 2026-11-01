"""Independent output audit, seed summaries, tables and monochrome comparison figure."""
import csv,gzip,hashlib,json,pathlib,statistics,sys,xml.etree.ElementTree as ET
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'results/paired_nov01'
sys.path.insert(0,str(ROOT/'measurement'))
from paired_study import inputs,CASES,SEEDS,write_csv,write_json

def analyze():
 protocol=json.loads((OUT/'protocol.json').read_text())
 assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in protocol['fingerprints'].items())
 measurements=[];audits=[];common=[];raw_differences=[]
 for case in CASES:
  book,path=inputs(case);cohort={k:v for k,v in book.items() if 600<=v['scheduled']<4200}
  for seed in SEEDS:
   pair={}
   for mode in ['fixed','rule']:
    folder=OUT/f'seed{seed}'/case/mode;rec=json.loads((folder/'measurement.json').read_text())
    records=json.loads((folder/'native_outputs.json').read_text());native={}
    for name,spec in records.items():
     data=gzip.decompress((folder/spec['mirror']).read_bytes())
     assert len(data)==spec['bytes'] and hashlib.sha256(data).hexdigest()==spec['sha256']
     if (folder/name).exists() and data!=(folder/name).read_bytes():raw_differences.append(str((folder/name).relative_to(ROOT)))
     native[name]=ET.fromstring(data)
    trips={t.get('id'):t.attrib for t in native['tripinfo.xml'].findall('tripinfo')}
    rows=list(csv.DictReader((folder/'cohort_trips.csv').open()));assert {r['id'] for r in rows}==set(cohort)
    byid={r['id']:r for r in rows};counts={'completed':0,'active':0,'uninserted':0};accum=0.;dur=[];wait=[];loss=[];stops=[]
    for vid,v in cohort.items():
     t=trips.get(vid,{});dep=float(t.get('depart',-1));arr=float(t.get('arrival',-1))
     kind='completed' if arr>=0 else 'active' if dep>=0 else 'uninserted';counts[kind]+=1
     accum+=(arr if arr>=0 else 4200)-v['scheduled'];assert byid[vid]['status']==kind
     if kind=='completed':
      for a,key in [(dur,'duration'),(wait,'waitingTime'),(loss,'timeLoss'),(stops,'waitingCount')]:a.append(float(t[key]))
    assert rec['study_cohort_scheduled']==len(cohort)==sum(counts.values())
    for k,v in counts.items():assert rec['study_cohort_'+k]==v
    assert abs(accum-rec['study_all_vehicle_accumulated_s'])<1e-5
    for vals,k in [(dur,'duration_s'),(wait,'wait_s'),(loss,'time_loss_s'),(stops,'stops')]:assert abs(statistics.mean(vals)-rec['study_completed_mean_'+k])<1e-8
    assert len(native['collisions.xml'].findall('collision'))==rec['collision_events']
    assert rec['queue_sample_times']==720
    queue=list(csv.DictReader((folder/'approach_queues.csv').open()));assert len(queue)==720*(12 if case.startswith('CORRIDOR') else 4)
    assert len({float(q['time_s']) for q in queue})==720
    measurements.append(rec);pair[mode]=byid
    audits.append({'case':case,'mode':mode,'seed':seed,'cohort_accounting':'PASS','native_output_hashes':'PASS','source_hashes':'PASS','queue_sample_counts':'PASS','collision_events':rec['collision_events'],'teleports':rec['teleports'],'phase_errors':len(rec['phase_errors'])})
   shared=[vid for vid in cohort if pair['fixed'][vid]['status']==pair['rule'][vid]['status']=='completed']
   common.append({'case':case,'seed':seed,'common_completed_n':len(shared),**{mode+'_mean_scheduled_to_arrival_s':statistics.mean(float(pair[mode][vid]['arrival_s'])-cohort[vid]['scheduled'] for vid in shared) for mode in ['fixed','rule']}})
 # Match all class/movement constraints in the source reconstruction, without double-counting corridor trips.
 movement=list(csv.DictReader((ROOT/'audit/matched_movement_counts.csv').open()))
 assert all(r['isolated_planned_study_hour_visits']==r['corridor_planned_study_hour_visits'] for r in movement)
 class_counts=list(csv.DictReader((ROOT/'data/source_class_counts.csv').open()))
 from collections import Counter
 expected={(r['site_id'],'AM' if r['window_start_local']=='07:00' else 'PM',r['source_vehicle_class']):int(r['reported_count']) for r in class_counts}
 for case in [c for c in CASES if not c.startswith('CORRIDOR')]:
  site,period=case.split('_');book,_=inputs(case)
  actual=Counter(v['class'] for v in book.values() if 600<=v['scheduled']<4200)
  wanted={k[2].replace(' ','_'):v for k,v in expected.items() if k[:2]==(site,period)}
  assert actual==Counter(wanted),(case,actual,wanted)
 metrics=['study_completed_mean_duration_s','study_completed_p95_duration_s','study_completed_mean_wait_s','study_completed_mean_time_loss_s','study_completed_mean_stops','study_cohort_scheduled','study_cohort_completed','study_cohort_active','study_cohort_uninserted','study_mean_accumulated_s','study_completion_percent','study_mean_approach_halting_vehicles','study_p95_approach_halting_vehicles','study_max_approach_halting_vehicles','study_max_tail_extent_m','study_hour_exits_all_cohorts']
 summary=[];paired=[]
 for case in CASES:
  for mode in ['fixed','rule']:
   rr=[r for r in measurements if r['case']==case and r['mode']==mode];assert len(rr)==3
   record={'case':case,'mode':mode,'replications':3}
   for metric in metrics:
    vals=[r[metric] for r in rr];record[metric]=statistics.mean(vals);record[metric+'_sd']=statistics.stdev(vals)
   summary.append(record)
  changes=[];pps=[];travel=[]
  for seed in SEEDS:
   b=next(r for r in measurements if r['case']==case and r['seed']==seed and r['mode']=='fixed');p=next(r for r in measurements if r['case']==case and r['seed']==seed and r['mode']=='rule')
   assert b['route_sha256']==p['route_sha256'] and b['scheduled_due']==p['scheduled_due']
   reduction=100*(b['study_mean_accumulated_s']-p['study_mean_accumulated_s'])/b['study_mean_accumulated_s']
   pp=p['study_completion_percent']-b['study_completion_percent']
   changes.append(reduction);pps.append(pp);travel.append(100*(b['study_completed_mean_duration_s']-p['study_completed_mean_duration_s'])/b['study_completed_mean_duration_s'])
  paired.append({'case':case,'all_demand_time_reduction_percent':statistics.mean(changes),'all_demand_time_reduction_sd':statistics.stdev(changes),'completion_change_pp':statistics.mean(pps),'completion_change_pp_sd':statistics.stdev(pps),'completed_travel_reduction_percent':statistics.mean(travel),'paired_seeds':SEEDS,'all_demand_changes_by_seed':changes,'completion_changes_by_seed':pps})
 write_csv(OUT/'summary_by_case.csv',summary);write_json(OUT/'paired_changes.json',paired);write_csv(OUT/'common_completed_trip_check.csv',common);write_csv(OUT/'output_audit.csv',audits)
 audit={'status':'PASS','runs':len(measurements),'source_movement_cells_checked':len(movement),'cohort_vehicle_records_checked':sum(r['study_cohort_scheduled'] for r in measurements),'collisions':sum(r['collision_events'] for r in measurements),'teleports':sum(r['teleports'] for r in measurements),'phase_errors':sum(len(r['phase_errors']) for r in measurements),'canonical_native_outputs':'SHA256-checked complete .xml.gz mirrors captured immediately after SUMO close; XML parsed and trip accounting recomputed independently.','post_process_raw_copies_differing_from_canonical':raw_differences,'note':'Output/accounting checks and finite motor-only diagnostics, not field/pedestrian acceptance.'}
 write_json(OUT/'audit.json',audit)
 table8=[['Case','Control','Travel s','P95 travel s','Waiting s','Time lost s','Stops / veh']]
 table9=[['Case','Control','Scheduled','Completed','Active','Not inserted','Accrued s / veh']]
 table10=[['Case','Control','Mean halted','P95 halted','Max tail m','Exits in hour']]
 for r in summary:
  case=r['case'].replace('CORRIDOR','Network').replace('_',' ');control='Fixed' if r['mode']=='fixed' else 'PASADA'
  def f(key):return f"{r[key]:,.1f}"
  table8.append([case,control,*[f(k) for k in ['study_completed_mean_duration_s','study_completed_p95_duration_s','study_completed_mean_wait_s','study_completed_mean_time_loss_s','study_completed_mean_stops']]])
  table9.append([case,control,f"{r['study_cohort_scheduled']:,.0f}",*[f(k) for k in ['study_cohort_completed','study_cohort_active','study_cohort_uninserted','study_mean_accumulated_s']]])
  table10.append([case,control,*[f(k) for k in ['study_mean_approach_halting_vehicles','study_p95_approach_halting_vehicles','study_max_tail_extent_m','study_hour_exits_all_cohorts']]])
 write_json(OUT/'manuscript_tables.json',{'table8':table8,'table9':table9,'table10':table10,'paired':paired,'audit':audit})
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
 fig,axes=plt.subplots(1,2,figsize=(8,5.2),sharey=True,gridspec_kw={'width_ratios':[1,1]})
 y=np.arange(len(CASES))
 axes[0].errorbar([r['all_demand_time_reduction_percent'] for r in paired],y,xerr=[r['all_demand_time_reduction_sd'] for r in paired],fmt='o',color='black',capsize=3,markersize=5)
 axes[1].errorbar([r['completion_change_pp'] for r in paired],y,xerr=[r['completion_change_pp_sd'] for r in paired],fmt='s',mfc='white',mec='black',color='black',capsize=3,markersize=5)
 axes[0].set_yticks(y,[c.replace('CORRIDOR','Network').replace('_',' ') for c in CASES]);axes[0].invert_yaxis()
 axes[0].set_xlabel('Accrued time reduction (%)');axes[1].set_xlabel('Completion change (percentage points)')
 axes[0].set_title('A. All scheduled study trips',fontsize=10);axes[1].set_title('B. Trips completed by cutoff',fontsize=10)
 for ax in axes:
  ax.axvline(0,color='0.45',lw=.8);ax.grid(axis='y',color='0.9',lw=.5);ax.spines[['top','right']].set_visible(False)
 fig.subplots_adjust(left=.16,right=.98,bottom=.2,top=.91,wspace=.23)
 fig.text(.16,.05,'Positive values favor PASADA. Points: mean paired change across three seeds.\nBars: ±1 sample SD; not confidence intervals. Common cutoff: 4,200 s.',fontsize=9)
 fig.savefig(OUT/'paired_effects.png',dpi=230);fig.savefig(OUT/'paired_effects.pdf');plt.close(fig)
 print(json.dumps({'audit':audit,'paired_changes':paired},indent=2))
if __name__=='__main__':analyze()

