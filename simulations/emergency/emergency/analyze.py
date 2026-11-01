"""Audit native outputs independently, then summarize all predeclared emergency runs."""
import csv,gzip,hashlib,json,math,pathlib,statistics,sys,xml.etree.ElementTree as ET
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'learning'));sys.path.insert(0,str(ROOT/'emergency'))
from common import write_json,write_csv
from run_study import OUT,CASES,ARMS,SEEDS

def native(folder):
 spec=json.loads((folder/'native_outputs.json').read_text());result={}
 for name,s in spec.items():
  data=gzip.decompress((folder/s['mirror']).read_bytes());assert len(data)==s['bytes'] and hashlib.sha256(data).hexdigest()==s['sha256'];result[name]=ET.fromstring(data)
 return result

def analyze():
 protocol=json.loads((OUT/'protocol.json').read_text());assert len(protocol['tasks'])==78
 assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in protocol['fingerprints'].items())
 rows=[];episode_rows=[];auditrows=[];late=[]
 for case,arm,seed,tag in protocol['tasks']:
  folder=OUT/tag/f'seed{seed}'/case/arm;r=json.loads((folder/'emergency_metrics.json').read_text());xml=native(folder)
  trips={t.get('id'):t.attrib for t in xml['tripinfo.xml'].findall('tripinfo')};ev=trips.get('EV_PROBE',{})
  assert float(ev.get('arrival',-1))==r['probe']['arrival_s'];assert float(ev.get('depart',-1))==r['probe']['depart_s']
  if r['probe']['completed']:
   assert abs(float(ev['arrival'])-1800-r['probe']['dispatch_to_arrival_s'])<1e-8
   assert abs(float(ev['duration'])+float(ev['departDelay'])-r['probe']['dispatch_to_arrival_s'])<.011
  base=ROOT/'scenarios'/f'{case}.sumocfg';cfg=ET.parse(base).getroot();orig=ET.parse(base.parent/cfg.find('input/route-files').get('value')).getroot()
  generated=ET.parse(ROOT/'emergency/inputs'/case/'scenarios'/f'{case}.rou.xml').getroot()
  original_vehicles={v.get('id'):v for v in orig.findall('vehicle')};new_vehicles={v.get('id'):v for v in generated.findall('vehicle')}
  assert set(new_vehicles)==set(original_vehicles)|{'EV_PROBE'}
  for vid,v in original_vehicles.items():
   assert v.attrib==new_vehicles[vid].attrib
   assert [(x.tag,x.attrib) for x in v]==[(x.tag,x.attrib) for x in new_vehicles[vid]]
  assert generated.find('vType[@id="EV_PROBE_TYPE"]').get('vClass')=='passenger'
  assert generated.find('vType[@id="EV_PROBE_TYPE"]/param[@key="has.bluelight.device"]').get('value')=='false'
  book={vid:float(v.get('depart')) for vid,v in original_vehicles.items() if 600<=float(v.get('depart'))<4200}
  counts={'completed':0,'active':0,'uninserted':0};spent=0.;ordinary_completed=[]
  for vid,start in book.items():
   t=trips.get(vid,{});dep=float(t.get('depart',-1));arr=float(t.get('arrival',-1))
   k='completed' if 0<=arr<=4200 else 'active' if 0<=dep<=4200 else 'uninserted';counts[k]+=1;spent+=(arr if k=='completed' else 4200)-start
   if k=='completed':ordinary_completed.append(t)
  assert counts==r['ordinary_counts'];assert sum(counts.values())==r['ordinary_scheduled']==len(book)
  assert abs(spent/len(book)-r['ordinary_mean_accumulated_s'])<1e-7
  assert len(xml['collisions.xml'].findall('collision'))==r['collisions']
  phases=json.loads((folder/'supervisor_events.json').read_text());phase_errors=[]
  for sid,events in phases.items():
   changes=[{'time':0.,'stage':0,'aspect':'green','reason':'initial'}]
   for event in events:
    if (event['stage'],event['aspect'])!=(changes[-1]['stage'],changes[-1]['aspect']):changes.append(event)
   for a,b in zip(changes,changes[1:]):
    duration=b['time']-a['time']
    if a['aspect']=='green':assert b['aspect']=='yellow' and duration>=10
    if a['aspect']=='yellow':assert b['aspect']=='all_red' and abs(duration-4)<1e-9
    if a['aspect']=='all_red':assert b['aspect']=='green' and abs(duration-4)<1e-9
    if b['reason']=='beacon priority green':
     e=r['encounters'][sid];assert arm.startswith('priority') and b['stage']==e['stage'] and e['request_s']<=b['time']<min(e['expires_s'],e['release_s'] or math.inf)
   for a,b in zip([e for e in changes if e['aspect']=='green'],[e for e in changes if e['aspect']=='green'][1:]):
    assert b['stage']==(a['stage']+1)%4 or b['reason']=='beacon priority green'
  assert not r['phase_errors']
  for sid,e in r['encounters'].items():
   tr=r['ground_truth_encounters'].get(sid,{});passed=tr.get('stopline_pass_s');latency=None if e['first_compatible_green_s'] is None else e['first_compatible_green_s']-e['request_s']
   if passed is not None and passed<e['request_s']:late.append([case,arm,seed,sid])
   episode_rows.append({'case':case,'arm':arm,'seed':seed,'tag':tag,'site':sid,'request_s':e['request_s'],'green_s':e['first_compatible_green_s'],'request_to_green_s':latency,'stopline_pass_s':passed,'release_s':e['release_s'],'release_reason':e['release_reason'],'cap_s':r['beacon_cap_s'],'passed_while_request_active':passed is not None and e['request_s']<=passed<=min(e['expires_s'],e['release_s'] or math.inf)})
  r['ordinary_completed_mean_wait_s']=statistics.mean(float(t['waitingTime']) for t in ordinary_completed)
  rows.append(r);auditrows.append({'case':case,'arm':arm,'seed':seed,'tag':tag,'source_background_identical':'PASS','probe_extra_one':'PASS','native_hashes_and_XML':'PASS','cohort_accounting':'PASS','signal_transition_audit':'PASS','collisions':r['collisions'],'wrong_approach_matches':len(r['wrong_approach_matches']),'unverified_matches':len(r['unverified_approach_matches'])})
 summary=[]
 for case in CASES:
  for arm in ARMS+(['priority60'] if case.startswith('J3_') else []):
   rr=[r for r in rows if r['case']==case and r['arm']==arm];assert len(rr)==3
   out={'case':case,'arm':arm,'runs':3,'probe_completed':sum(r['probe']['completed'] for r in rr)}
   for key in ['dispatch_to_arrival_s','duration','departDelay','waitingTime','timeLoss','waitingCount']:
    vals=[r['probe'][key] for r in rr if r['probe'][key] is not None]
    out[key]=statistics.mean(vals) if vals else None;out[key+'_sd']=statistics.stdev(vals) if len(vals)>1 else None
   for key in ['ordinary_mean_accumulated_s','ordinary_completion_percent','ordinary_completed_mean_wait_s']:
    vals=[r[key] for r in rr];out[key]=statistics.mean(vals);out[key+'_sd']=statistics.stdev(vals)
   eps=[e for e in episode_rows if e['case']==case and e['arm']==arm]
   lats=[e['request_to_green_s'] for e in eps if e['request_to_green_s'] is not None]
   out.update({'qualified_requests':len(eps),'green_observed':len(lats),'request_to_green_s':statistics.mean(lats) if lats else None,'passed_active_n':sum(e['passed_while_request_active'] for e in eps),'expired_n':sum(e['release_reason']=='encounter_cap' for e in eps)})
   summary.append(out)
 pairs=[]
 for case in CASES:
  for candidate,baseline in [('priority20','fixed'),('priority20','local')]+([('priority60','priority20')] if case.startswith('J3_') else []):
   vv=[]
   for seed in SEEDS:
    p=next(r for r in rows if r['case']==case and r['seed']==seed and r['arm']==candidate);b=next(r for r in rows if r['case']==case and r['seed']==seed and r['arm']==baseline)
    assert p['route_sha256']==b['route_sha256'] and p['ordinary_scheduled']==b['ordinary_scheduled']
    vv.append({'seed':seed,'EV_seconds_saved':None if not (p['probe']['completed'] and b['probe']['completed']) else b['probe']['dispatch_to_arrival_s']-p['probe']['dispatch_to_arrival_s'],
     'EV_time_reduction_percent':None if not (p['probe']['completed'] and b['probe']['completed']) else 100*(b['probe']['dispatch_to_arrival_s']-p['probe']['dispatch_to_arrival_s'])/b['probe']['dispatch_to_arrival_s'],
     'ordinary_time_cost_percent':100*(p['ordinary_mean_accumulated_s']-b['ordinary_mean_accumulated_s'])/b['ordinary_mean_accumulated_s'],
     'ordinary_completion_change_pp':p['ordinary_completion_percent']-b['ordinary_completion_percent']})
   q={'case':case,'candidate':candidate,'baseline':baseline,'by_seed':vv}
   for key in ['EV_seconds_saved','EV_time_reduction_percent','ordinary_time_cost_percent','ordinary_completion_change_pp']:
    z=[v[key] for v in vv if v[key] is not None];q[key]=statistics.mean(z) if len(z)==3 else None;q[key+'_sd']=statistics.stdev(z) if len(z)==3 else None
   pairs.append(q)
 write_csv(OUT/'summary.csv',summary);write_json(OUT/'paired_changes.json',pairs);write_csv(OUT/'request_episodes.csv',episode_rows);write_csv(OUT/'audit_by_run.csv',auditrows)
 audit={'status':'PASS','runs':len(rows),'main_runs':72,'cap_sensitivity_runs':6,'EVs_completed':sum(r['probe']['completed'] for r in rows),'collisions':sum(r['collisions'] for r in rows),'teleports':sum(r['teleports'] for r in rows),'wrong_approach_matches':sum(len(r['wrong_approach_matches']) for r in rows),'unverified_matches':sum(len(r['unverified_approach_matches']) for r in rows),'late_first_matches':late,'phase_checks':'Native event states checked independently: minimum green, full yellow/all-red, request-bound priority jumps and cyclic ordinary return.','physical_authentication_or_radio_test':False}
 write_json(OUT/'audit.json',audit)
 def cell(v):return '—' if v is None else f'{v:,.1f}'
 def get(case,arm):return next(r for r in summary if r['case']==case and r['arm']==arm)
 t11=[['Case','Fixed total s','Local total s','Beacon total s','Fixed road s','Local road s','Beacon road s']]
 t12=[['Case','Stopped s F/L/P','Stops F/L/P','Green lag s F/L/P','Pass in cap P','Ordinary time Δ%','Completion Δpp']]
 t13=[['Case','20 s total','60 s total','EV time saved %','Ordinary time Δ%','Pass 20 / 60']]
 for case in CASES:
  rs=[get(case,a) for a in ARMS];label=case.replace('CORRIDOR','Network').replace('_',' ')
  t11.append([label,*[cell(r['dispatch_to_arrival_s']) for r in rs],*[cell(r['duration']) for r in rs]])
  pair=next(q for q in pairs if q['case']==case and q['candidate']=='priority20' and q['baseline']=='local')
  t12.append([label,' / '.join(cell(r['waitingTime']) for r in rs),' / '.join(cell(r['waitingCount']) for r in rs),' / '.join(cell(r['request_to_green_s']) for r in rs),f"{rs[2]['passed_active_n']}/{rs[2]['qualified_requests']}",f"{pair['ordinary_time_cost_percent']:+.2f}",f"{pair['ordinary_completion_change_pp']:+.2f}"])
  if case.startswith('J3_'):
   a,b=get(case,'priority20'),get(case,'priority60');q=next(x for x in pairs if x['case']==case and x['candidate']=='priority60')
   t13.append([label,cell(a['dispatch_to_arrival_s']),cell(b['dispatch_to_arrival_s']),f"{q['EV_time_reduction_percent']:+.1f}",f"{q['ordinary_time_cost_percent']:+.2f}",f"{a['passed_active_n']}/{a['qualified_requests']} / {b['passed_active_n']}/{b['qualified_requests']}"])
 write_json(OUT/'manuscript_tables.json',{'table11':t11,'table12':t12,'table13':t13,'summary':summary,'pairs':pairs,'audit':audit})
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
 fig=plt.figure(figsize=(8,8));gs=fig.add_gridspec(2,1,height_ratios=[3,1.5],hspace=.52);ax=fig.add_subplot(gs[0]);y=np.arange(8)
 for arm,off,marker in [('fixed',-.18,'o'),('local',0,'s'),('priority20',.18,'^')]:
  rs=[get(c,arm) for c in CASES];ax.errorbar([r['dispatch_to_arrival_s'] for r in rs],y+off,xerr=[r['dispatch_to_arrival_s_sd'] for r in rs],fmt=marker,mfc='white' if arm!='priority20' else 'black',mec='black',color='black',capsize=2,markersize=4,label={'fixed':'Fixed','local':'Local, no beacon','priority20':'Local + 20 s beacon'}[arm])
 ax.set_yticks(y,[c.replace('CORRIDOR','Network').replace('_',' ') for c in CASES]);ax.set_ylim(7.6,-1.1);ax.set_xlabel('Scheduled-start-to-arrival time (s)');ax.set_title('A. Same emergency probe; three controls',fontsize=11);ax.grid(axis='y',color='.9');ax.spines[['right','top']].set_visible(False);ax.legend(fontsize=8.5,loc='upper center',ncol=3,frameon=False,columnspacing=1)
 ax=fig.add_subplot(gs[1]);reference=next(r for r in rows if r['case']=='J3_AM' and r['arm']=='priority20' and r['seed']==7300);e=reference['encounters']['J3'];truth=reference['ground_truth_encounters']['J3'];origin=e['request_s']
 times=[0,e['first_compatible_green_s']-origin,e['release_s']-origin,truth['stopline_pass_s']-origin];labels=['Request accepted','Compatible green','Request released','Stop-line passage']
 ax.scatter(times,range(4),color='black',s=20);ax.set_yticks(range(4),labels);ax.invert_yaxis();ax.set_xlabel('Seconds after the accepted request');ax.set_title('B. A. Soriano AM, seed 7300: response versus passage',fontsize=10)
 ax.axvline(20,color='.5',ls='--',lw=.8)
 for x,y0 in zip(times,range(4)):ax.annotate(f'{x:.1f} s',(x,y0),xytext=(5,5),textcoords='offset points',fontsize=9)
 ax.set_xlim(-5,max(times)*1.18+5);ax.set_ylim(3.6,-.7);ax.spines[['right','top']].set_visible(False);ax.grid(axis='x',color='.9');fig.subplots_adjust(left=.23,right=.98,bottom=.16,top=.95)
 fig.text(.23,.02,'Means ± sample SD over three seeds; ideal beacon input.\nTotal includes insertion waiting. The 20 s cap is measured from request acceptance.',fontsize=9)
 fig.savefig(OUT/'emergency_comparison.png',dpi=230);fig.savefig(OUT/'emergency_comparison.pdf');plt.close(fig)
 print(json.dumps({'audit':audit,'summary':summary,'pairs':pairs},indent=2))
if __name__=='__main__':analyze()

