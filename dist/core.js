import {validateInstallationPlans} from './junction-analysis.js';
import {LAYOUT_REVISION,roadLayoutFor,lanesForLayout,makeLanePucks,coverageIssues,radioCapacityIssues,distanceM,slicePath,pathLength,bearingDeg} from './geometry.js';
import {STUDY_AREA} from './road-layouts.js';
import {BeaconTracker,demoPosition} from './beacons.js';
import {defaultDemoVehicle,validateFleet,beaconProfile,beaconAuthorization,BEACON_FIRMWARE} from './fleet.js';
/* PASADA draft. Pure, dependency-free contracts and deterministic queue model. */
export const VERSION = '0.1.0';
export const DIRECTIONS = ['N','E','S','W'];
export const SETTINGS = Object.freeze({min_green_s:10,max_green_s:30,fixed_green_s:20,yellow_s:3,all_red_s:2,pedestrian_service_s:7,pedestrian_max_wait_s:90,heartbeat_s:1,heartbeat_timeout_s:5,recovery_stable_s:60,downstream_capacity_veh:18});
export const SCENARIOS = {
 balanced:{name:'Balanced arrivals',description:'Similar demand on both axes. Synthetic arrivals; independent junctions.'},
 tidal:{name:'Uneven demand',description:'More north–south arrivals, then a demand reversal at 120 seconds.'},
 blocked:{name:'Downstream blockage',description:'The eastbound exit is blocked from 60–150 seconds.'},
 resilience:{name:'Fault, emergency & recovery',description:'Sensor stops at 40 s; emergency request at 65 s; sensor returns at 90 s.'}
};
export const clone = x => JSON.parse(JSON.stringify(x));
export const CONTROLLER_HARDWARE=Object.freeze({mcu:'ESP32-C3 Super Mini',rtc:{required:true,model:'UNSELECTED',purpose:'Retained time reference; synchronization protocol required'},lora:{required:true,module:'UNSELECTED',profile:'UNSELECTED',purpose:'Intersection telemetry to C2C receiver'},esp_now:{purpose:'Local puck and emergency-beacon reception'},physical_interface:'UNCONFIRMED'});
export const hasDevicePosition=d=>finite(d?.latitude)&&finite(d?.longitude);
const controllerArchitecture=()=>({controller_placement_revision:1,local_coordinators:'one per study intersection',signal_heads:'Multiple signal heads share an intersection phase authority; not independent timing controllers',c2c_receiver:{quantity:1,status:'proposed',location_status:'unlocated',role:'LoRa telemetry gateway, separate from intersection coordinators'},clock:'External RTC retained time; explicit synchronization needed. Monotonic elapsed time for timeouts.'});
export function defaultProject(){
 const intersections=['A','B','C'].map((x,i)=>{const layout=roadLayoutFor(`J-${x}`);return {id:`J-${x}`,name:layout.name,study_number:layout.study_number,mapped_name:layout.mapped_name,layout_note:layout.layout_note||'',signal_node_id:layout.signal_node_id,location_status:'verified',latitude:layout.center[0],longitude:layout.center[1],position:{x:25+i*25,y:50},neighbor_ids:(i===0?['J-B']:i===1?['J-A','J-C']:['J-B']),controller_device_id:`CTRL-${x}`,timing:{...SETTINGS},model:'pressure-v0',layout_revision:LAYOUT_REVISION,downstream_offset_m:10,lanes:lanesForLayout(layout)};});
 const devices=[];
 for(const j of intersections){devices.push({id:j.controller_device_id,role:'controller',intersection_id:j.id,latitude:null,longitude:null,location_status:'unlocated',mounting:'roadside-cabinet-proposed',hardware:clone(CONTROLLER_HARDWARE),firmware:'pasada-controller-draft-0.1',commissioning:{state:'planned',transport:'simulated'}});devices.push(...makeLanePucks(j));}
 devices.push({id:'EV-DEMO-01',role:'beacon',intersection_id:'J-A',latitude:10.33090,longitude:123.94810,firmware:BEACON_FIRMWARE,commissioning:{state:'planned',transport:'simulated'}});
 return {schema:'pasada.project/0.1.0',project:{id:'PASADA-MANDAUE-LEAR',name:'Mandaue study corridor · PASADA / LEAR',created_at:'2026-10-26T00:00:00+08:00',coordinate_reference:'EPSG:4326',layout_provenance:'Study selection from user-supplied paper p.33; junction details pp.36–38. OSM road paths reviewed against satellite imagery. Lane widths, turn pockets and exact signal / stop-line / cabinet positions need survey.'},study_area:clone(STUDY_AREA),architecture:controllerArchitecture(),provenance:{source:'synthetic',calibrated:false,description:'Mandaue geographic planning configuration with synthetic traffic. Not the paper’s calibrated SUMO dataset.'},communications:{sensor_link:'esp-now',coordination_link:'lora-proposed',esp_now_channel:6,encrypted_peer_budget:17,provisioning_state:'planning',lora_profile:'UNSELECTED'},security:{mode:'simulation',key_material_included:false},intersections,devices,vehicles:[defaultDemoVehicle()]};
}

// Replace only the generated Colon sample. The caller backs it up before saving.
export function migrateStudyProject(input){
 const p=clone(input),pins={'J-A':[10.2963015,123.8982804],'J-B':[10.2967376,123.8990448],'J-C':[10.2954634,123.8965401]};
 if(p.project?.id==='PASADA-MANDAUE-LEAR'&&p.study_area?.id==='MANDAUE-PAPER-P33'&&!p.architecture?.controller_placement_revision){p.architecture=controllerArchitecture();for(const d of p.devices.filter(d=>d.role==='controller')){const j=p.intersections.find(j=>j.id===d.intersection_id);d.hardware=clone(CONTROLLER_HARDWARE);if(!d.location_status&&j&&hasDevicePosition(d)&&distanceM([d.latitude,d.longitude],[j.latitude,j.longitude])<1){d.latitude=null;d.longitude=null;d.location_status='unlocated';d.mounting='roadside-cabinet-proposed';d.commissioning={state:'planned',transport:'simulated'};}}return {project:p,changed:true,kind:'controller'};}
 if(p.project?.id!=='PASADA-DEMO'||p.provenance?.calibrated===true||p.provenance?.source==='sumo'||p.intersections?.length!==3||p.intersections.some(j=>!pins[j.id]||distanceM([j.latitude,j.longitude],pins[j.id])>30))return {project:p,changed:false};
 return {project:defaultProject(),changed:true,kind:'study'};
}

function finite(x){return typeof x==='number'&&Number.isFinite(x);}
export function validateProject(p){
 const e=[];if(!p||typeof p!=='object')return ['Project must be an object.'];
 if(p.schema!=='pasada.project/0.1.0')e.push('Unsupported project schema.');
 if(typeof p.project?.id!=='string'||!p.project.id||typeof p.project?.name!=='string'||!p.project.name)e.push('Project ID and name are required.');
 if(!Array.isArray(p.intersections)||!p.intersections.length||p.intersections.length>12)e.push('Use 1–12 intersections.');
 if(!Array.isArray(p.devices)||!p.devices.length||p.devices.length>250)e.push('Use 1–250 devices.');
 if(e.length)return e;
 if(p.intersections.some(j=>!j||typeof j!=='object')||p.devices.some(d=>!d||typeof d!=='object'))return ['Intersection and device entries must be objects.'];
 const ids=new Set(), js=new Set();
 for(const j of p.intersections){
  if(typeof j.id!=='string'||!j.id||js.has(j.id))e.push(`Invalid or duplicate intersection ID: ${j.id}`);js.add(j.id);
  if(typeof j.name!=='string'||!j.name)e.push(`${j.id}: name required.`);
  if(!finite(j.latitude)||Math.abs(j.latitude)>90||!finite(j.longitude)||Math.abs(j.longitude)>180)e.push(`${j.id}: invalid coordinates.`);
  if(!finite(j.position?.x)||j.position.x<10||j.position.x>90||!finite(j.position?.y)||j.position.y<20||j.position.y>80)e.push(`${j.id}: schematic position must be x 10–90 and y 20–80.`);
  if(!['pressure-v0','fixed-v0'].includes(j.model))e.push(`${j.id}: unsupported model.`);
  for(const [k,v] of Object.entries(SETTINGS))if(!Number.isInteger(j.timing?.[k])||j.timing[k]<=0||j.timing[k]>600)e.push(`${j.id}: invalid ${k}; use a positive whole number.`);
  const t=j.timing||{};
  if(t.max_green_s<t.min_green_s||t.fixed_green_s<t.min_green_s||t.fixed_green_s>t.max_green_s)e.push(`${j.id}: green timings must satisfy min ≤ fixed ≤ max.`);
  if(t.min_green_s<t.pedestrian_service_s)e.push(`${j.id}: minimum green must cover the modeled pedestrian service interval.`);
  if(t.pedestrian_max_wait_s<t.max_green_s+2*(t.yellow_s+t.all_red_s)+t.pedestrian_service_s)e.push(`${j.id}: pedestrian limit is infeasible for this two-phase draft.`);
  if(t.heartbeat_timeout_s<2*t.heartbeat_s)e.push(`${j.id}: heartbeat timeout must allow at least two heartbeat intervals.`);
  if(!Array.isArray(j.lanes)||!j.lanes.length)e.push(`${j.id}: lane mappings are required.`);
  else if(j.layout_revision){const laneIds=new Set();for(const l of j.lanes){if(!l||!l.id||laneIds.has(l.id)||!DIRECTIONS.includes(l.approach)||!['inbound','outbound'].includes(l.flow)||!Array.isArray(l.path)||l.path.length<2||l.path.some(p=>!Array.isArray(p)||!finite(p[0])||!finite(p[1])||Math.abs(p[0])>90||Math.abs(p[1])>180))e.push(`${j.id}: invalid road lane geometry.`);laneIds.add(l?.id);}if(!j.lanes.some(l=>l.flow==='inbound')||!j.lanes.some(l=>l.flow==='outbound'))e.push(`${j.id}: incoming and outgoing lanes are required.`);if(!finite(j.downstream_offset_m)||j.downstream_offset_m<=0||j.downstream_offset_m>200)e.push(`${j.id}: invalid downstream counter offset.`);}
  else if(!DIRECTIONS.every(d=>j.lanes.some(l=>l&&l.approach===d&&typeof l.id==='string')))e.push(`${j.id}: four legacy approach mappings are required.`);
 }
 for(const d of p.devices){
  if(typeof d.id!=='string'||!d.id||ids.has(d.id)||!/^[A-Za-z0-9_-]{1,64}$/.test(d.id))e.push(`Invalid or duplicate device ID: ${d.id}`);ids.add(d.id);
  if(!['sensor','controller','beacon'].includes(d.role))e.push(`${d.id}: unsupported role.`);
  if(!js.has(d.intersection_id))e.push(`${d.id}: unknown intersection.`);
  const unlocated=(d.role==='controller'&&d.location_status==='unlocated'||d.role==='beacon'&&d.location_status==='mobile')&&d.latitude===null&&d.longitude===null;
  if(!unlocated&&(!finite(d.latitude)||Math.abs(d.latitude)>90||!finite(d.longitude)||Math.abs(d.longitude)>180))e.push(`${d.id}: invalid coordinates.`);
  if(d.role==='sensor'){
   if(!DIRECTIONS.includes(d.approach)||!['upstream','downstream'].includes(d.placement)||!finite(d.offset_m)||d.offset_m<0||d.offset_m>200)e.push(`${d.id}: invalid sensor placement.`);
   if(!p.intersections.find(j=>j.id===d.intersection_id)?.lanes?.some(l=>l&&l.id===d.lane_id&&l.approach===d.approach))e.push(`${d.id}: lane mapping does not match approach.`);
  }
 }
 for(const j of p.intersections){
  if(p.devices.filter(d=>d.intersection_id===j.id&&d.role==='controller').length!==1)e.push(`${j.id}: exactly one controller is required.`);
  if(!p.devices.some(d=>d.id===j.controller_device_id&&d.role==='controller'&&d.intersection_id===j.id))e.push(`${j.id}: controller mapping mismatch.`);
  const peers=p.devices.filter(d=>d.intersection_id===j.id&&['sensor','beacon'].includes(d.role)).length;
  if(p.communications?.provisioning_state!=='planning'&&peers>(p.communications?.encrypted_peer_budget||0))e.push(`${j.id}: encrypted peer budget exceeded (${peers}).`);
  for(const x of j.neighbor_ids||[])if(!js.has(x)||x===j.id)e.push(`${j.id}: invalid neighbor ${x}.`);
 }
 if(p.study_area!==undefined){const a=p.study_area;if(!a||typeof a!=='object'||typeof a.id!=='string'||!Array.isArray(a.corridor_links)||a.corridor_links.length>12)e.push('Invalid study-area metadata.');else for(const l of a.corridor_links){if(!l||!js.has(l.from_site)||!js.has(l.to_site)||l.from_site===l.to_site||!finite(l.reported_distance_m)||l.reported_distance_m<=0||l.reported_distance_m>100000||!Array.isArray(l.path)||l.path.length<2||l.path.length>2000||l.path.some(x=>!Array.isArray(x)||!finite(x[0])||Math.abs(x[0])>90||!finite(x[1])||Math.abs(x[1])>180))e.push('Invalid study-corridor link or coordinates.');}}
 if(!Number.isInteger(p.communications?.esp_now_channel)||p.communications.esp_now_channel<1||p.communications.esp_now_channel>11)e.push('Draft radio profile supports ESP-NOW channels 1–11.');
 if(!Number.isInteger(p.communications?.encrypted_peer_budget)||p.communications.encrypted_peer_budget<1||p.communications.encrypted_peer_budget>17)e.push('Encrypted peer budget must be 1–17.');
 if(p.security?.key_material_included!==false)e.push('Public configuration must exclude key material.');
 if(p.security?.mode!=='simulation')e.push('This draft only supports simulation security mode.');
 const secret=/^(pmk|lmk|private_key|secret_key|password|token)$/i;
 function scan(v){if(v&&typeof v==='object')for(const [k,x] of Object.entries(v)){if(secret.test(k))e.push(`Secret field ${k} is forbidden in this export.`);scan(x);}}scan(p);
 if(!e.length)e.push(...coverageIssues(p),...validateFleet(p),...validateInstallationPlans(p.installation_plans));
 return [...new Set(e)];
}
export function deviceConfiguration(p,id){
 const d=p.devices.find(x=>x.id===id);if(!d)throw Error('Unknown device.');
 const j=p.intersections.find(x=>x.id===d.intersection_id);
 const located=hasDevicePosition(d),profile=d.role==='beacon'?beaconProfile(p,d.id):null;
 return {schema:'pasada.device/0.1.0',project_id:p.project.id,device_id:d.id,role:d.role,intersection_id:j.id,location:located?{latitude:d.latitude,longitude:d.longitude}:null,location_status:d.location_status||'provisional',installation_ready:d.role==='beacon'?!!profile:located,beacon_profile:profile||undefined,intersection_reference:{latitude:j.latitude,longitude:j.longitude,purpose:'Junction reference; not the cabinet position'},hardware:d.role==='controller'?clone(d.hardware||CONTROLLER_HARDWARE):undefined,sensor:d.role==='sensor'?{lane_id:d.lane_id,approach:d.approach,placement:d.placement,offset_m:d.offset_m,reference_latitude:d.reference_latitude??null,reference_longitude:d.reference_longitude??null}:null,controller_site_map:d.role==='controller'?{enrolled_beacon_ids:p.devices.filter(x=>x.role==='beacon'&&beaconAuthorization(p,x.id).allowed).map(x=>x.id),incoming_lanes:j.lanes.filter(l=>l.flow==='inbound').map(l=>({id:l.id,approach:l.approach,width_m:l.lane_width_m,path:slicePath(l.path,0,Math.min(120,pathLength(l.path))).map(p=>p.map(n=>Number(n.toFixed(7))))})),peers:p.devices.filter(x=>x.intersection_id===j.id&&x.id!==d.id).map(x=>({id:x.id,role:x.role,lane_id:x.lane_id,latitude:x.latitude,longitude:x.longitude}))}:undefined,controller_id:j.controller_device_id,esp_now_channel:p.communications.esp_now_channel,timing:clone(j.timing),model:j.model,security_mode:'simulation',output_mode:'serial-only',radio_capacity_resolved:!radioCapacityIssues(p).some(x=>x.intersection_id===j.id),firmware_version:VERSION};
}
export function validateReplay(r){
 if(r?.schema!=='pasada.replay/0.1.0')return ['Unsupported replay schema.'];
 const e=validateProject(r.project);if(e.length)return e;
 if(!['synthetic','sumo'].includes(r.provenance?.source))e.push('Replay provenance must be synthetic or sumo.');
 if(!Array.isArray(r.frames)||!r.frames.length||r.frames.length>20000)return [...e,'Replay requires 1–20,000 frames.'];
 let last=-1;const ids=r.project.intersections.map(j=>j.id);
 const beaconIds=new Set(r.project.devices.filter(d=>d.role==='beacon').map(d=>d.id));
 for(const [i,f]of r.frames.entries()){
  if(!f||typeof f!=='object'){e.push(`Frame ${i}: expected an object.`);continue;}
  if(!finite(f.t)||f.t<0||f.t<=last)e.push(`Frame ${i}: time must increase.`);last=f.t;
  if(f.beacon_tracks!==undefined){if(!Array.isArray(f.beacon_tracks)||f.beacon_tracks.length>100)e.push(`Frame ${i}: invalid beacon tracks.`);else for(const t of f.beacon_tracks){if(!t||!beaconIds.has(t.beacon_id)||typeof t.status!=='string'||!Number.isSafeInteger(t.sequence)||!finite(t.latitude)||Math.abs(t.latitude)>90||!finite(t.longitude)||Math.abs(t.longitude)>180||!finite(t.position_accuracy_m)||t.position_accuracy_m<=0||!finite(t.age_s)||t.age_s<0||t.speed_mps!==null&&(!finite(t.speed_mps)||t.speed_mps<0)||t.heading_deg!==null&&(!finite(t.heading_deg)||t.heading_deg<0||t.heading_deg>=360)||t.match&&(!ids.includes(t.match.intersection_id)||!['NS','EW'].includes(t.match.axis)||typeof t.match.road_name!=='string')||t.local_request&&(!['NS','EW'].includes(t.local_request.axis)||!finite(t.local_request.until)))e.push(`Frame ${i}: invalid beacon fix or matching record.`);}}
  if(!Array.isArray(f.intersections)||f.intersections.length!==ids.length){e.push(`Frame ${i}: intersection coverage mismatch.`);continue;}
  const found=new Set();
  for(const j of f.intersections){
   if(!j||typeof j!=='object'){e.push(`Frame ${i}: invalid intersection object.`);continue;}
   if(!ids.includes(j.id)||found.has(j.id))e.push(`Frame ${i}: invalid intersection ID.`);found.add(j.id);
   if(typeof j.phase!=='string'||typeof j.mode!=='string')e.push(`Frame ${i}: phase and mode required.`);
   if(!DIRECTIONS.every(d=>finite(j.queues?.[d])&&j.queues[d]>=0)||Object.keys(j.queues||{}).some(d=>!DIRECTIONS.includes(d)))e.push(`Frame ${i}: invalid queue values.`);
   if(j.downstream&&!DIRECTIONS.every(d=>finite(j.downstream[d])&&j.downstream[d]>=0))e.push(`Frame ${i}: invalid downstream values.`);
   if(j.ped_wait_s!==null&&(!finite(j.ped_wait_s)||j.ped_wait_s<0))e.push(`Frame ${i}: invalid pedestrian wait.`);
   if(j.arrived!==null&&(!finite(j.arrived)||j.arrived<0)||j.departed!==null&&(!finite(j.departed)||j.departed<0))e.push(`Frame ${i}: invalid cumulative flow.`);
   for(const key of ['device_counts','lane_counts'])if(j[key]&&(!Object.values(j[key]).every(v=>finite(v)&&v>=0)||Array.isArray(j[key])))e.push(`Frame ${i}: invalid passage counts.`);
  }
  if(e.length>15)break;
 }
 return [...new Set(e)];
}
function random(seed){let s=seed>>>0;return ()=>{s=(Math.imul(1664525,s)+1013904223)>>>0;return s/4294967296;};}
function poisson(rate,r){let x=0,p=1,limit=Math.exp(-rate);do{x++;p*=r();}while(p>limit);return x-1;}
export function demandAt(seed,t,idx,d,scenario){
 const r=random((seed+Math.imul(t+1,2654435761)+idx*1973+DIRECTIONS.indexOf(d)*101)>>>0);
 let rate=.18;
 if(scenario==='tidal'){const ns=d==='N'||d==='S';rate=((t<120)===ns)?.34:.065;}
 if(scenario==='blocked')rate=.24;
 return poisson(rate,r);
}
export class Engine{
 constructor(project,{seed=42,scenario='balanced',policy='adaptive',record=true}={}){
  const e=validateProject(project);if(e.length)throw Error(e.join('\n'));
  this.project=clone(project);this.seed=seed;this.scenario=scenario;this.policy=policy;this.record=record;this.t=0;this.c2cOnline=true;this.events=[];this.frames=[];this.failed=new Set();this.lastSeen={};this.emergencies={};this.eventSeq=0;this.history=[];this.beaconTracker=new BeaconTracker(this.project);this.beaconDemo=null;this.beaconPackets=[];this.beaconStates={};
  for(const d of project.devices)this.lastSeen[d.id]=0;
  this.nodes=project.intersections.map(j=>({id:j.id,phase:'NS_GREEN',elapsed:0,policy:policy==='fixed'||j.model==='fixed-v0'?'fixed':'adaptive',health:'healthy',healthySince:null,queues:Object.fromEntries(DIRECTIONS.map(d=>[d,[]])),downstream:Object.fromEntries(DIRECTIONS.map(d=>[d,0])),credits:Object.fromEntries(DIRECTIONS.map(d=>[d,0])),arrived:0,departed:0,area:0,maxQueue:0,pedRequests:{NS:null,EW:null},pedServed:0,pedMaxWait:0,oversatSince:null,oversatReported:false,lane_counts:Object.fromEntries(j.lanes.filter(l=>l.flow).map(l=>[l.id,0])),device_counts:Object.fromEntries(project.devices.filter(d=>d.intersection_id===j.id&&d.role==='sensor'&&(d.placement==='downstream'||d.offset_m===60)).map(d=>[d.id,0]))}));
  this.log('SYSTEM_START',null,'Synthetic queue model started. No field actuation.','info');
 }
 log(kind,id,message,severity='info'){this.events.push({schema:'pasada.event/0.1.0',sequence:++this.eventSeq,t:this.t,source:'synthetic',kind,intersection_id:id,message,severity});if(this.events.length>2000)this.events.shift();}
 setDeviceOnline(id,online){if(!this.project.devices.some(d=>d.id===id))throw Error('Unknown device.');if(online){this.failed.delete(id);this.log('DEVICE_RECONNECTED',this.project.devices.find(d=>d.id===id).intersection_id,`${id} resumed simulated heartbeats.`);}else{this.failed.add(id);this.log('HEARTBEAT_STOPPED',this.project.devices.find(d=>d.id===id).intersection_id,`${id} stopped simulated heartbeats.`,'warning');}}
 setC2C(online){this.c2cOnline=online;this.log(online?'C2C_RECONNECTED':'C2C_DISCONNECTED',null,online?'C2C telemetry connection restored.':'C2C disconnected. Local intersection control continues.','info');}
 requestEmergency(id,axis='NS',duration=20){if(!['NS','EW'].includes(axis))throw Error('Invalid axis.');this.emergencies[id]={axis,until:this.t+duration};this.log('EMERGENCY_REQUEST',id,`Simulated authorized beacon requests ${axis} priority for ${duration} s.`,'warning');}
 startBeaconDemo(siteId,beaconId=null){const site=this.project.intersections.find(j=>j.id===siteId),device=this.project.devices.find(d=>d.role==='beacon'&&(!beaconId||d.id===beaconId)&&beaconAuthorization(this.project,d.id).allowed);if(!site||!device)throw Error('A study site and enrolled demonstration beacon are required.');const lane=site.lanes.find(l=>l.flow==='inbound'&&['E','W'].includes(l.approach)&&pathLength(l.path)>=110)||site.lanes.find(l=>l.flow==='inbound');if(!lane)throw Error('No mapped incoming lane.');this.beaconTracker=new BeaconTracker(this.project);for(const [id,r]of Object.entries(this.emergencies))if(r.beacon_id)delete this.emergencies[id];this.beaconDemo={beacon_id:device.id,site_id:siteId,lane,start_s:this.t,start_distance_m:Math.min(100,pathLength(lane.path)-2),speed_mps:6,sequence:0,paused:false,finished:false,boot_id:`demo-${this.t}-${this.eventSeq}`};this.beaconPackets=[];this.beaconStates={};this.log('BEACON_DEMO_STARTED',siteId,`${device.id}: synthetic GPS stream at 1 Hz; target ${lane.road_name}. Identity is simulated, not cryptographically verified.`,'warning');}
 pauseBeaconDemo(){if(this.beaconDemo){this.beaconDemo.paused=!this.beaconDemo.paused;this.log(this.beaconDemo.paused?'BEACON_STREAM_PAUSED':'BEACON_STREAM_RESUMED',this.beaconDemo.site_id,'Synthetic packet transmission '+(this.beaconDemo.paused?'paused; the local freshness lease will expire.':'resumed.'));}}
 _stepBeacons(){const demo=this.beaconDemo;if(demo&&!demo.paused&&!demo.finished&&!this.failed.has(demo.beacon_id)){const remaining=demo.start_distance_m-demo.speed_mps*(this.t-demo.start_s);if(remaining>=-12){const position=demoPosition(demo.lane,remaining),packet={schema:'pasada.beacon/0.1.0',beacon_id:demo.beacon_id,vehicle_id:beaconAuthorization(this.project,demo.beacon_id).vehicle?.id||'AMB-DEMO-01',boot_id:demo.boot_id,sequence:++demo.sequence,timestamp_s:this.t,latitude:position[0],longitude:position[1],position_accuracy_m:.5,reported_heading_deg:bearingDeg([demoPosition(demo.lane,remaining+1),position]),reported_speed_mps:demo.speed_mps,emergency_active:true,source:'synthetic'};this.beaconPackets.push(packet);this.beaconTracker.receive(packet,this.t,{identityVerified:true});}else demo.finished=true;}
  const tracks=this.beaconTracker.snapshot(this.t);for(const track of tracks){const site=track.match?.intersection_id||demo?.site_id;if(this.beaconStates[track.beacon_id]!==track.status){this.log('BEACON_TRACK',site,`${track.beacon_id}: ${track.status}${track.match?'; '+track.match.road_name:''}.`,track.priority_eligible?'warning':'info');this.beaconStates[track.beacon_id]=track.status;}}
  for(const site of this.project.intersections){const eligible=tracks.filter(t=>t.priority_eligible&&t.match?.intersection_id===site.id&&this.deviceHealth(this.project.devices.find(d=>d.id===site.controller_device_id))!=='offline').sort((a,b)=>a.eta_s-b.eta_s||a.beacon_id.localeCompare(b.beacon_id));if(eligible.length){const track=eligible[0],old=this.emergencies[site.id];this.emergencies[site.id]={axis:track.match.axis,until:Math.min(track.lease_end_s,track.received_at_s+this.beaconTracker.freshness_s),beacon_id:track.beacon_id};if(old?.beacon_id!==track.beacon_id)this.log('EMERGENCY_APPROACH_MATCHED',site.id,`${track.beacon_id} → ${site.controller_device_id}; ${track.match.road_name}; bounded ${track.match.axis} request after motion matching.`,'warning');}else if(this.emergencies[site.id]?.beacon_id){delete this.emergencies[site.id];this.log('EMERGENCY_BEACON_RELEASED',site.id,'Beacon request released; normal clearance and pedestrian constraints remain in force.');}}
 }
 requestPedestrian(id,axis='EW'){const n=this.nodes.find(x=>x.id===id);if(!n||!['NS','EW'].includes(axis))throw Error('Invalid pedestrian request.');if(n.pedRequests[axis]===null)n.pedRequests[axis]=this.t;this.log('PEDESTRIAN_REQUEST',id,`${axis} crossing service requested.`);}
 deviceHealth(d){const j=this.project.intersections.find(j=>j.id===d.intersection_id),age=this.t-(this.lastSeen[d.id]??0);return age>=j.timing.heartbeat_timeout_s?'offline':this.failed.has(d.id)?'suspect':'online';}
 step(count=1){for(let k=0;k<count;k++)this._step();return this.snapshot();}
 _step(){
  this.t++;
  this._stepBeacons();
  const firstSensor=this.project.devices.find(d=>d.role==='sensor');
  if(this.scenario==='resilience'){
   if(this.t===40&&firstSensor)this.setDeviceOnline(firstSensor.id,false);
   if(this.t===65)this.requestEmergency(this.nodes[0].id,'EW');
   if(this.t===90&&firstSensor)this.setDeviceOnline(firstSensor.id,true);
  }
  for(const d of this.project.devices){const j=this.project.intersections.find(j=>j.id===d.intersection_id);if(!this.failed.has(d.id)&&this.t%j.timing.heartbeat_s<1)this.lastSeen[d.id]=this.t;}
  for(const [idx,n]of this.nodes.entries()){
   const j=this.project.intersections[idx],s=j.timing;
   const all=this.project.devices.filter(d=>d.intersection_id===j.id&&d.role!=='beacon');
   const bad=all.filter(d=>this.deviceHealth(d)==='offline');
   const controllerBad=bad.some(d=>d.role==='controller');
   if(bad.length){
    if(n.health!=='fault')this.log('FAULT_DETECTED',j.id,`${bad.map(d=>d.id).join(', ')} timed out. Fixed fallback requested at a clearance boundary.`,'error');
    n.health='fault';n.healthySince=null;
   }else if(n.health==='fault'){
    n.health='recovering';n.healthySince=this.t;this.log('RECOVERY_STARTED',j.id,`All required heartbeats restored. Observing ${s.recovery_stable_s} s stability.`);
   }else if(n.health==='recovering'&&this.t-n.healthySince>=s.recovery_stable_s){n.health='healthy';this.log('RECOVERY_READY',j.id,'Stable recovery satisfied. Adaptive return requested at a clearance boundary.');}
   const wanted=n.health!=='healthy'||this.policy==='fixed'||j.model==='fixed-v0'?'fixed':'adaptive';
   n.controllerBad=controllerBad;n.wantedPolicy=wanted;
   for(const d of DIRECTIONS){
    const inbound=j.lanes.filter(l=>l.flow==='inbound'&&l.approach===d);
    const arrivals=j.layout_revision&&!inbound.length?0:demandAt(this.seed,this.t,idx,d,this.scenario);
    for(let a=0;a<arrivals;a++){n.queues[d].push(this.t);if(inbound.length){const lane=inbound[(n.arrived+a)%inbound.length];n.lane_counts[lane.id]++;const detector=this.project.devices.find(x=>x.lane_id===lane.id&&x.intersection_id===j.id&&x.offset_m===60&&x.placement==='upstream');if(detector)n.device_counts[detector.id]++;}}
    n.arrived+=arrivals;
    const blocked=this.scenario==='blocked'&&d==='E'&&this.t>=60&&this.t<150;
    n.downstream[d]=Math.max(0,n.downstream[d]-(blocked?0:.7));
   }
   if(this.t%45===0){const axis=this.t%90===0?'NS':'EW';if(n.pedRequests[axis]===null)n.pedRequests[axis]=this.t;}
   const axis=n.phase.slice(0,2),green=n.phase.endsWith('_GREEN');
   if(green){
    if(n.pedRequests[axis]!==null&&n.elapsed<=s.min_green_s-s.pedestrian_service_s){n.pedMaxWait=Math.max(n.pedMaxWait,this.t-n.pedRequests[axis]);n.pedRequests[axis]=null;n.pedServed++;}
    for(const d of axis==='NS'?['N','S']:['E','W']){
     n.credits[d]=Math.min(1,n.credits[d]+.5);
     if(n.queues[d].length&&n.downstream[d]<s.downstream_capacity_veh&&n.credits[d]>=1){n.queues[d].shift();n.downstream[d]++;const exits=j.lanes.filter(l=>l.flow==='outbound'&&l.approach!==d);if(exits.length){const lane=exits[n.departed%exits.length];n.lane_counts[lane.id]++;const detector=this.project.devices.find(x=>x.lane_id===lane.id&&x.intersection_id===j.id&&x.placement==='downstream');if(detector)n.device_counts[detector.id]++;}n.departed++;n.credits[d]-=1;}else if(!n.queues[d].length)n.credits[d]=0;
    }
   }
   const total=DIRECTIONS.reduce((a,d)=>a+n.queues[d].length,0);n.area+=total;n.maxQueue=Math.max(n.maxQueue,total);
   for(const a of ['NS','EW'])if(n.pedRequests[a]!==null)n.pedMaxWait=Math.max(n.pedMaxWait,this.t-n.pedRequests[a]);
   const saturated=DIRECTIONS.some(d=>n.queues[d].length>=10);
   if(saturated){if(n.oversatSince===null)n.oversatSince=this.t;if(!n.oversatReported&&this.t-n.oversatSince>=20){this.log('SUSTAINED_QUEUE',j.id,'Synthetic queue ≥10 vehicles on an approach for 20 s. Not a calibrated 60 m detector threshold.','warning');n.oversatReported=true;}}
   else{n.oversatSince=null;n.oversatReported=false;}
   n.elapsed++;
   if(green){
    const other=axis==='NS'?'EW':'NS';
    const pressure=a=>[...a].reduce((v,d)=>v+n.queues[d].length-n.downstream[d],0);
    const emergency=this.emergencies[j.id];
    const ev=emergency&&emergency.until>this.t&&!controllerBad?emergency.axis:null;
    const pedDue=n.pedRequests[other]!==null&&this.t-n.pedRequests[other]+s.yellow_s+s.all_red_s>=s.pedestrian_max_wait_s-s.pedestrian_service_s;
    let change=false;
    if(n.elapsed>=s.min_green_s){
     if(n.elapsed>=s.max_green_s||pedDue||wanted!==n.policy)change=true;
     else if(ev)change=ev!==axis;
     else if(n.policy==='fixed')change=n.elapsed>=s.fixed_green_s;
     else change=pressure(other)>pressure(axis)+2||[...axis].every(d=>!n.queues[d].length)&&[...other].some(d=>n.queues[d].length);
    }
    if(change){n.phase=axis+'_YELLOW';n.elapsed=0;}
   }else if(n.phase.endsWith('_YELLOW')&&n.elapsed>=s.yellow_s){n.phase='ALL_RED_TO_'+(axis==='NS'?'EW':'NS');n.elapsed=0;}
   else if(n.phase.startsWith('ALL_RED')&&n.elapsed>=s.all_red_s){
    const next=n.phase.endsWith('NS')?'NS':'EW';
    if(n.policy!==wanted){n.policy=wanted;this.log(wanted==='fixed'?'FALLBACK_ACTIVE':'ADAPTIVE_RESTORED',j.id,wanted==='fixed'?'Fixed timings active after yellow and all-red.':'Adaptive operation restored after yellow and all-red.',wanted==='fixed'?'warning':'info');}
    n.phase=next+'_GREEN';n.elapsed=0;
   }
  }
  const f=this.snapshot();if(this.record&&this.frames.length<3600)this.frames.push(f);
  this.history.push({t:this.t,queue:f.intersections.reduce((s,j)=>s+Object.values(j.queues).reduce((a,b)=>a+b,0),0)});if(this.history.length>240)this.history.shift();
 }
 snapshot(){return {t:this.t,beacon_tracks:this.beaconTracker.snapshot(this.t).map(t=>({...t,local_request:t.match?clone(this.emergencies[t.match.intersection_id]||null):null})),intersections:this.nodes.map((n,i)=>({id:n.id,phase:n.phase,phase_elapsed_s:n.elapsed,mode:n.controllerBad?'CABINET_BACKUP':n.health==='recovering'?'RECOVERING':n.policy==='fixed'?'FIXED_FALLBACK':'ADAPTIVE',pending_mode:n.policy!==n.wantedPolicy?n.wantedPolicy:null,queues:Object.fromEntries(DIRECTIONS.map(d=>[d,n.queues[d].length])),downstream:clone(n.downstream),arrived:n.arrived,departed:n.departed,lane_counts:clone(n.lane_counts),device_counts:clone(n.device_counts),queue_area_veh_s:n.area,stopped_time_per_arrival_s:n.arrived?n.area/n.arrived:0,ped_wait_s:Math.max(0,...Object.values(n.pedRequests).filter(x=>x!==null).map(x=>this.t-x)),ped_max_wait_s:n.pedMaxWait,health:n.health,device_health:Object.fromEntries(this.project.devices.filter(d=>d.intersection_id===n.id).map(d=>[d.id,this.deviceHealth(d)]))})),events:this.events.filter(e=>e.t===this.t).map(clone)};}
 metrics(){const ns=this.nodes,arrived=ns.reduce((s,n)=>s+n.arrived,0),departed=ns.reduce((s,n)=>s+n.departed,0),remaining=ns.reduce((s,n)=>s+DIRECTIONS.reduce((a,d)=>a+n.queues[d].length,0),0),area=ns.reduce((s,n)=>s+n.area,0);return {duration_s:this.t,arrived,departed,remaining,queue_area_veh_s:area,mean_queue_veh:this.t?area/this.t:0,stopped_time_per_arrival_s:arrived?area/arrived:0,max_pedestrian_request_wait_s:Math.max(...ns.map(n=>n.pedMaxWait)),conservation_error:arrived-departed-remaining};}
 replay(){return {schema:'pasada.replay/0.1.0',project:clone(this.project),provenance:{source:'synthetic',calibrated:false,description:'Deterministic queue model, not SUMO. Queue and pedestrian request proxies only.',seed:this.seed,scenario:this.scenario,policy:this.policy},frames:clone(this.frames),events:clone(this.events)};}
}
export function runExperiment(project,{scenario='tidal',duration=240,seeds=[11,42,93]}={}){
 const runs=[];
 for(const seed of seeds)for(const policy of ['fixed','adaptive']){const engine=new Engine(project,{seed,scenario,policy,record:false});engine.step(duration);runs.push({seed,policy,...engine.metrics()});}
 return {schema:'pasada.experiment/0.1.0',source:'synthetic',calibrated:false,scenario,duration_s:duration,seeds,runs,notes:'Paired arrival streams. No field performance claim. Stopped time per arrival includes unfinished vehicles; this is not SUMO timeLoss.'};
}
export function metricCSV(result){const keys=['seed','policy','duration_s','arrived','departed','remaining','queue_area_veh_s','mean_queue_veh','stopped_time_per_arrival_s','max_pedestrian_request_wait_s','conservation_error'];return [keys.join(','),...result.runs.map(r=>keys.map(k=>r[k]).join(','))].join('\n');}
