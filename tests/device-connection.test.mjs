import test from 'node:test';
import assert from 'node:assert/strict';
import {defaultProject,clone} from '../dist/core.js';
import {SIGNAL_CATALOG} from '../dist/signal-junctions.js';
import {createJunctionPlan,saveJunctionPlan,candidateForStudy} from '../dist/junction-analysis.js';
import {installationScopes,installationContext,requestDevicePort,candidateInfo,USB_FILTERS} from '../dist/device-connection.js';
function savedProject(){const base=defaultProject(),candidate=SIGNAL_CATALOG.junctions.find(c=>!candidateForStudy(c,base)&&!createJunctionPlan(c).issues.length),plan=createJunctionPlan(candidate);return {project:saveJunctionPlan(base,plan),plan};}
test('saved-plan connection preserves every puck identity and coordinate without activating the site',()=>{
 const {project,plan}=savedProject(),before=clone(project),context=installationContext(project,plan.id);
 assert.deepEqual(context.devices.filter(d=>d.role==='sensor'),plan.devices);assert.equal(context.devices.filter(d=>d.role==='controller').length,1);assert.equal(context.devices.find(d=>d.role==='controller').latitude,null);
 const puck=plan.devices[0],profile=context.profileFor(puck.id);assert.equal(profile.device_id,puck.id);assert.equal(profile.intersection_id,plan.id);assert.equal(profile.location.latitude,puck.latitude);assert.equal(profile.sensor.lane_id,puck.lane_id);assert.equal(profile.controller_id,`CTRL-${plan.id}`);
 assert.deepEqual(project,before);assert.equal(project.intersections.length,3);assert.ok(installationScopes(project).some(s=>s.id===plan.id&&s.kind==='Saved plan'));
});
test('study component lists retain real assignments and exclude mobile vehicle beacons',()=>{
 const project=defaultProject(),c=installationContext(project,'J-C');assert.equal(c.devices.filter(d=>d.role==='sensor').length,34);assert.equal(c.devices.filter(d=>d.role==='controller')[0].id,'CTRL-C');assert.ok(c.devices.every(d=>d.role!=='beacon'));assert.equal(c.profileFor('CTRL-C').installation_ready,false);assert.throws(()=>installationContext(project,'UNKNOWN'));
});
test('native chooser uses the Espressif USB filter and cancellation propagates without writing',async()=>{
 let calls=0;const port={getInfo:()=>({usbVendorId:0x303a,usbProductId:0x1001}),open:()=>{throw Error('Must not open or write a port.');}};
 assert.equal(await requestDevicePort({requestPort:async options=>{calls++;assert.deepEqual(options,{filters:USB_FILTERS});return port;}}),port);assert.equal(calls,1);
 await assert.rejects(requestDevicePort({requestPort:async()=>{const e=Error('Cancelled');e.name='NotFoundError';throw e;}}),{name:'NotFoundError'});assert.throws(()=>requestDevicePort(undefined),/Chrome or Edge/);
});
test('USB selection never proves board identity or firmware installation',()=>{
 const info=candidateInfo({getInfo:()=>({usbVendorId:0x303a,usbProductId:0x1001})});assert.equal(info.board_verified,false);assert.equal(info.firmware_installed,false);assert.throws(()=>candidateInfo({getInfo:()=>({usbVendorId:0x1234})}));
});
