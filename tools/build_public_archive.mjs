/* Deterministic sample, assigned a calendar date solely to exercise date-range downloads. */
import fs from 'node:fs/promises';
import {defaultProject,Engine} from '../dist/core.js';
import {publicRecord} from '../dist/public-data.js';
const project=defaultProject(),engine=new Engine(project,{scenario:'balanced',record:false});
const anchor=Date.parse('2026-10-30T00:00:00Z');
const intersections=project.intersections.map(j=>({id:j.id,name:j.name.replace(/^\d+ · /,''),lanes:j.lanes.map(l=>({id:l.id,road_name:l.road_name,flow:l.flow}))}));
const detectors=project.devices.filter(d=>d.role==='sensor'&&(d.placement==='downstream'||d.placement==='upstream'&&d.offset_m===60));
if(detectors.length!==intersections.reduce((n,j)=>n+j.lanes.length,0))throw Error('Every lane needs exactly one counting boundary.');
let previous=engine.snapshot();const records=[];
for(let minute=0;minute<60;minute++){
 const next=engine.step(60);
 for(const d of detectors){
  const site=intersections.find(j=>j.id===d.intersection_id),lane=site.lanes.find(l=>l.id===d.lane_id);
  const current=next.intersections.find(j=>j.id===site.id).device_counts[d.id],prior=previous.intersections.find(j=>j.id===site.id).device_counts[d.id];
  const delta=current-prior;if(!Number.isSafeInteger(delta)||delta<0)throw Error('Counter discontinuity; do not publish as zero.');
  records.push(publicRecord({intersection_id:site.id,intersection_name:site.name,lane_id:lane.id,road_name:lane.road_name,flow:lane.flow,period_start_utc:new Date(anchor+minute*60000).toISOString(),period_end_utc:new Date(anchor+(minute+1)*60000).toISOString(),vehicle_count:delta,observed_seconds:60,expected_seconds:60,quality:'complete',source:'synthetic'}));
 }
 previous=next;
}
const archive={schema:'pasada.public-traffic/0.1.0',release_id:'synthetic-balanced-20261030-v1',source:'synthetic',calibrated:false,description:'Deterministic queue-model demonstration. Calendar anchor assigned for interface testing; not observed traffic.',timezone:'Asia/Manila',coverage_start_utc:new Date(anchor).toISOString(),coverage_end_utc:new Date(anchor+3600000).toISOString(),base_interval_seconds:60,intersections,records};
await fs.mkdir(new URL('../dist/data/',import.meta.url),{recursive:true});
await fs.writeFile(new URL('../dist/data/archive.json',import.meta.url),JSON.stringify(archive));
console.log(`Published sample fixture: ${records.length} lane-minutes, ${intersections.length} intersections; synthetic only.`);
