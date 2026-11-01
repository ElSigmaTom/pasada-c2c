import test from 'node:test';
import assert from 'node:assert/strict';
import {defaultProject,validateProject,validateReplay,deviceConfiguration,Engine,clone} from '../dist/core.js';
import {saveVehicle,ensureFleetRegistry,beaconAuthorization,BEACON_FIRMWARE} from '../dist/fleet.js';
import {BeaconTracker} from '../dist/beacons.js';
import {pointAlong} from '../dist/geometry.js';
import {activeIssues} from '../dist/operations-ui.js';

const record=(extra={})=>({id:'VEH-TEST-01',call_sign:'QA rescue unit',agency:'Test response agency',vehicle_type:'rescue',registration:'TEST-001',beacon_id:'BCN-TEST-01',hardware_uid:'TEST-UID-01',home_site_id:'J-C',authorization_status:'pending',authorization_reference:'',...extra});
const put=(project,input=record(),id)=>saveVehicle(project,input,{id,now:'2026-10-31T05:00:00Z'}).project;
function fix(p,id,sequence,station){const lane=p.intersections[0].lanes.find(l=>l.flow==='inbound'&&l.approach==='E'),ll=pointAlong(lane.path,station);return {schema:'pasada.beacon/0.1.0',beacon_id:'BCN-TEST-01',vehicle_id:id,boot_id:'qa-session',sequence,timestamp_s:sequence,latitude:ll[0],longitude:ll[1],position_accuracy_m:.5,emergency_active:true};}

test('registration creates a mobile beacon and preserves all road geometry and equipment',()=>{
 const p=defaultProject(),before=clone(p),next=put(p);
 assert.deepEqual(p,before);assert.deepEqual(next.intersections,p.intersections);assert.deepEqual(next.devices.filter(d=>d.role!=='beacon'),p.devices.filter(d=>d.role!=='beacon'));
 assert.deepEqual(validateProject(next),[]);const b=next.devices.find(d=>d.id==='BCN-TEST-01');assert.equal(b.location_status,'mobile');assert.equal(b.latitude,null);assert.equal(b.longitude,null);assert.equal(beaconAuthorization(next,b.id).allowed,false);
});
test('duplicate beacon, hardware UID, plate and road-device collision are rejected without mutation',()=>{
 const p=put(defaultProject()),before=clone(p);
 for(const extra of [{id:'VEH-TWO',registration:'TEST-002',hardware_uid:'OTHER'},{id:'VEH-TWO',beacon_id:'BCN-TWO',registration:'TEST-002'},{id:'VEH-TWO',beacon_id:'BCN-TWO',hardware_uid:'OTHER'},{id:'VEH-TWO',beacon_id:'CTRL-A',hardware_uid:'OTHER',registration:'TEST-002'}])assert.throws(()=>put(p,record(extra)));
 assert.deepEqual(p,before);
});
test('approved priority requires a recorded approval and exact vehicle/beacon pairing',()=>{
 const pending=put(defaultProject()),tracker=new BeaconTracker(pending),packet=fix(pending,'VEH-TEST-01',1,94);
 assert.equal(tracker.receive(packet,1,{identityVerified:true}).accepted,false);
 assert.throws(()=>put(pending,record({authorization_status:'approved'}),'VEH-TEST-01'),/approval reference/);
 const approved=put(pending,record({authorization_status:'approved',authorization_reference:'QA simulation approval'}),'VEH-TEST-01'),t=new BeaconTracker(approved);
 assert.equal(t.receive({...packet,vehicle_id:'WRONG'},1,{identityVerified:true}).accepted,false);
 const missing={...packet};delete missing.vehicle_id;assert.equal(t.receive(missing,1,{identityVerified:true}).accepted,false);
 assert.equal(t.receive(packet,1).accepted,false,'A registry entry cannot replace transport verification');
 assert.equal(t.receive(packet,1,{identityVerified:true}).accepted,true);
 assert.equal(t.receive(fix(approved,'VEH-TEST-01',2,88),2,{identityVerified:true}).track.priority_eligible,true);
});
test('suspension and revocation remove an existing tracked request and controller enrollment',()=>{
 for(const state of ['suspended','revoked']){
  const p=put(defaultProject(),record({authorization_status:'approved',authorization_reference:'QA simulation approval'})),t=new BeaconTracker(p);
  t.receive(fix(p,'VEH-TEST-01',1,94),1,{identityVerified:true});t.receive(fix(p,'VEH-TEST-01',2,88),2,{identityVerified:true});assert.equal(t.snapshot(2)[0].priority_eligible,true);
  p.vehicles.find(v=>v.id==='VEH-TEST-01').authorization_status=state;assert.equal(t.snapshot(2)[0].priority_eligible,false);assert.equal(t.snapshot(2)[0].status,'authorization inactive');
  assert.ok(!deviceConfiguration(p,'CTRL-A').controller_site_map.enrolled_beacon_ids.includes('BCN-TEST-01'));
 }
});
test('one firmware build produces distinct per-vehicle profiles, without a fabricated fixed GPS position',()=>{
 const p=put(defaultProject()),q=put(p,record({id:'VEH-TEST-02',beacon_id:'BCN-TEST-02',registration:'TEST-002',hardware_uid:'TEST-UID-02'}));
 const a=deviceConfiguration(q,'BCN-TEST-01'),b=deviceConfiguration(q,'BCN-TEST-02');
 assert.equal(a.installation_ready,true);assert.equal(a.location,null);assert.equal(a.location_status,'mobile');assert.equal(a.beacon_profile.firmware_build,BEACON_FIRMWARE);assert.equal(a.beacon_profile.firmware_build,b.beacon_profile.firmware_build);assert.notEqual(a.beacon_profile.vehicle_id,b.beacon_profile.vehicle_id);assert.equal(a.beacon_profile.priority_authorized,false);assert.equal(a.beacon_profile.key_material_included,false);assert.equal(a.beacon_profile.identity_enrollment,'not-provisioned');
 assert.deepEqual(validateProject(JSON.parse(JSON.stringify(q))),[]);
});
test('beacon reassignment preserves vehicle identity and disallows the old unbound beacon',()=>{
 const p=put(defaultProject()),q=put(p,record({beacon_id:'BCN-REPLACEMENT',authorization_status:'approved',authorization_reference:'QA replacement'}),'VEH-TEST-01');
 assert.equal(q.vehicles.find(v=>v.id==='VEH-TEST-01').beacon_id,'BCN-REPLACEMENT');assert.equal(beaconAuthorization(q,'BCN-TEST-01').allowed,false);assert.equal(beaconAuthorization(q,'BCN-REPLACEMENT','VEH-TEST-01').allowed,true);assert.deepEqual(validateProject(q),[]);
});
test('legacy installation upgrade preserves coordinates, while arbitrary legacy beacons await approval',()=>{
 const p=defaultProject();delete p.vehicles;p.devices.find(d=>d.role==='beacon').id='LEGACY-BCN';const before=clone(p),next=ensureFleetRegistry(p);assert.deepEqual(p,before);assert.deepEqual(next.devices,p.devices);assert.equal(next.vehicles[0].authorization_status,'pending');assert.deepEqual(validateProject(next),[]);
});
test('an approved registered vehicle can approach a different site from its administrative home',()=>{
 const p=put(defaultProject(),record({authorization_status:'approved',authorization_reference:'QA simulation approval'})),e=new Engine(p);e.startBeaconDemo('J-A','BCN-TEST-01');e.step(3);const t=e.snapshot().beacon_tracks[0];assert.equal(t.vehicle_id,'VEH-TEST-01');assert.equal(t.match.intersection_id,'J-A');assert.equal(t.priority_eligible,true);assert.deepEqual(validateReplay(e.replay()),[]);
 const rejected=new Engine(put(defaultProject()));assert.throws(()=>rejected.startBeaconDemo('J-A','BCN-TEST-01'));
});
test('operator attention reflects current faults and clears after recovery rather than retaining old event warnings',()=>{
 const p=defaultProject(),e=new Engine(p),healthy=e.snapshot();assert.equal(activeIssues(p,healthy,true).length,0);assert.equal(activeIssues(p,healthy,false)[0].id,'c2c');const failed=clone(healthy);failed.intersections[0].mode='CABINET_BACKUP';assert.equal(activeIssues(p,failed,true)[0].severity,'error');assert.equal(activeIssues(p,healthy,true).length,0);
});
