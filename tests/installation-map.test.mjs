import test from 'node:test';
import assert from 'node:assert/strict';
import {defaultProject,clone} from '../dist/core.js';
import {distanceM} from '../dist/geometry.js';
import {installationDevices,installationBoundsPoints,planningIdentity,googleMapsUrl} from '../dist/installation-map.js';

test('no installation devices appear before choosing a site; switching scopes devices without mutation',()=>{
 const p=defaultProject(),before=clone(p);assert.deepEqual(installationDevices(p,null),[]);
 for(const site of p.intersections){const ds=installationDevices(p,site.id);assert.ok(ds.length);assert.ok(ds.every(d=>d.intersection_id===site.id));assert.equal(ds.filter(d=>d.role==='sensor').length,p.devices.filter(d=>d.intersection_id===site.id&&d.role==='sensor').length);}
 assert.deepEqual(installationDevices(p,null),[]);assert.deepEqual(p,before);
});
test('the selected preview fits only local lane borders and placed infrastructure, with no null cabinet coordinates',()=>{
 const p=defaultProject();for(const site of p.intersections){const points=installationBoundsPoints(p,site.id);assert.ok(points.length>20);assert.ok(points.every(pt=>pt.length===2&&pt.every(Number.isFinite)));assert.ok(points.every(pt=>distanceM(pt,[site.latitude,site.longitude])<200));for(const d of installationDevices(p,site.id).filter(d=>d.role==='sensor'))assert.ok(points.some(pt=>distanceM(pt,[d.latitude,d.longitude])<.01));}
 assert.deepEqual(installationBoundsPoints(p,null),p.intersections.map(j=>[j.latitude,j.longitude]));
});
test('planning labels remain provisional and do not fabricate a physical hardware UID',()=>{
 const p=defaultProject(),d=p.devices.find(d=>d.role==='sensor'),before=clone(d),identity=planningIdentity(d);assert.equal(identity.reference,d.id);assert.equal(identity.hardware_uid,null);assert.equal(identity.kind,'planning reference');assert.match(identity.status,/not assigned/);assert.deepEqual(d,before);
 const recorded=planningIdentity({...d,hardware_uid:'example-enrolled-id'});assert.equal(recorded.hardware_uid,'example-enrolled-id');assert.match(recorded.status,/unverified/);
});
test('external Google Maps links use the chosen intersection coordinates',()=>{
 const p=defaultProject();for(const site of p.intersections){const url=new URL(googleMapsUrl(site));assert.equal(url.origin,'https://www.google.com');assert.equal(url.pathname,'/maps/search/');assert.equal(url.searchParams.get('api'),'1');assert.equal(url.searchParams.get('query'),`${site.latitude},${site.longitude}`);}
});
