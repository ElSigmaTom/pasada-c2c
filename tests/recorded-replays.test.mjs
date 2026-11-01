import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {atOrBefore,signalAt,matchingRuns,vehicleState} from '../dist/study-replay.js';
const root=new URL('../dist/replays/',import.meta.url),manifest=JSON.parse(fs.readFileSync(new URL('manifest.json',root)));
const load=r=>JSON.parse(gunzipSync(fs.readFileSync(new URL(r.file,root))));
test('recorded library preserves 48 ordinary and 78 emergency runs, every matched seed and adverse outcomes',()=>{
 assert.equal(manifest.runs.length,126);assert.equal(manifest.runs.filter(r=>r.study==='ordinary').length,48);assert.equal(manifest.runs.filter(r=>r.study==='emergency').length,78);assert.equal(new Set(manifest.runs.map(r=>r.id)).size,126);
 for(const study of ['ordinary','emergency'])for(const layout of ['J1','J2','J3','CORRIDOR'])for(const period of ['AM','PM'])for(const seed of study==='ordinary'?[7100,7101,7102]:[7300,7301,7302]){
  const runs=matchingRuns(manifest,{study,layout,period,seed});assert.ok(runs.some(r=>r.arm==='fixed'));assert.ok(runs.some(r=>r.arm===(study==='ordinary'?'rule':'local')));if(study==='emergency')assert.ok(runs.some(r=>r.arm==='priority20'));
 }
});
test('every imported trace retains its identity, original accounting, ordered sample times and unreported detector occupancy',()=>{
 for(const meta of manifest.runs){const r=load(meta);assert.equal(r.id,meta.id);assert.deepEqual(r.metrics,meta.metrics);assert.ok(r.unreported_channels.includes('per-detector occupancy'));assert.match(r.provenance.archive_sha256,/^[a-f0-9]{64}$/);assert.ok(Object.keys(r.provenance.members).length>=3);
  for(const site of meta.sites){const rows=r.sensor_trace.filter(x=>x.site===site);assert.ok(rows.length);assert.ok(rows.every((x,i)=>x.time_s>=(rows[i-1]?.time_s??0)&&x.time_s<=meta.horizon_s));assert.ok(r.initial_states[site]);}
  if(meta.study==='ordinary')assert.equal(r.metrics.study_cohort_scheduled,r.metrics.study_cohort_completed+r.metrics.study_cohort_active+r.metrics.study_cohort_uninserted);else assert.ok(r.probe_positions.length>0);
 }
});
test('native detector coordinates stay at lane centres, including shifted actual chainages and side access',()=>{
 for(const [layout,file]of Object.entries(manifest.geometry)){const g=JSON.parse(fs.readFileSync(new URL(file,root)));assert.equal(g.layout,layout);assert.equal(g.detectors.length,{J1:46,J2:30,J3:42,CORRIDOR:118}[layout]);const lanes=new Map(g.lanes.map(l=>[l.id,l]));
  for(const d of g.detectors){const lane=lanes.get(d.lane);assert.ok(lane);let nearest=Infinity;for(let i=1;i<lane.shape.length;i++){const a=lane.shape[i-1],b=lane.shape[i],dx=b[0]-a[0],dy=b[1]-a[1],u=Math.max(0,Math.min(1,((d.x-a[0])*dx+(d.y-a[1])*dy)/(dx*dx+dy*dy||1)));nearest=Math.min(nearest,Math.hypot(d.x-a[0]-dx*u,d.y-a[1]-dy*u));}assert.ok(nearest<.002,`${d.id} ${nearest}`);assert.equal(d.occupancy_history,'unreported');}
 }
});
test('half-second native clearance transitions change at the exact event, independently of 5 second sensor samples',()=>{
 const r=load(manifest.runs.find(r=>r.id==='ordinary-J1_AM-fixed-7100'));const e=r.supervisor_events.J1[0];assert.equal(signalAt(r,'J1',e.time-.01).aspect,'green');assert.equal(signalAt(r,'J1',e.time).aspect,'yellow');assert.equal(signalAt(r,'J1',e.time+4).aspect,'all_red');assert.equal(signalAt(r,'J1',e.time+8).aspect,'green');
});
test('sampling never shows a future record and missing history stays absent',()=>{const rows=[{time_s:5,n:1},{time_s:10,n:2}];assert.equal(atOrBefore(rows,4),null);assert.equal(atOrBefore(rows,9).n,1);assert.equal(atOrBefore(rows,10).n,2);assert.equal(atOrBefore([],50),null);});
test('motion capture stops outside its interval and interpolates headings across north without rotating backwards',()=>{
 const m={capture_window_s:[1,2],sample_s:1,frames:[[1,[[0,0,0,350]]],[2,[[0,2,4,10]]]]};assert.deepEqual(vehicleState(m,0),[]);assert.deepEqual(vehicleState(m,3),[]);assert.deepEqual(vehicleState(m,1.5),[[0,1,2,360]]);
});
test('all eight motion overlays are matched reproductions with intact bytes and one-second samples',()=>{
 const m=JSON.parse(fs.readFileSync(new URL('motion-manifest.json',root)));assert.equal(Object.keys(m.captures).length,8);
 for(const [id,c]of Object.entries(m.captures)){assert.ok(manifest.runs.some(r=>r.id===id));assert.ok(c.passed&&c.sensor_trace_semantic_equal&&c.supervisor_events_equal&&c.core_metrics_equal);const bytes=fs.readFileSync(new URL(c.file,root));assert.equal(createHash('sha256').update(bytes).digest('hex'),c.motion_sha256);const data=JSON.parse(gunzipSync(bytes));assert.equal(data.seed,7100);assert.equal(data.sample_s,1);assert.deepEqual(data.capture_window_s,[1200,2400]);assert.equal(data.frames.length,1201);assert.ok(data.frames.every((f,i)=>f[0]===1200+i&&f[1].every(v=>v.length===4&&v.every(Number.isFinite))));}
});
