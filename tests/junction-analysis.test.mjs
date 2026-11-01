import test from 'node:test';
import assert from 'node:assert/strict';
import {analyzeJunctions,junctionsInRadius,createJunctionPlan,defaultArmSettings,saveJunctionPlan,validateInstallationPlans,candidateForStudy,signalizedJunctions} from '../dist/junction-analysis.js';
import {pointAlong,distanceM,laneCrossSection,pathLength} from '../dist/geometry.js';
import {defaultProject,validateProject,clone} from '../dist/core.js';
import {ROAD_NETWORK} from '../dist/road-network.js';

const origin=[10.32765,123.94465],ll=(x,y)=>[origin[0]+y/111195,origin[1]+x/109395];
const network=(extra={})=>({nodes:[{id:'1',point:origin,tags:{highway:'traffic_signals'}},{id:'2',point:ll(0,180)},{id:'3',point:ll(180,0)},{id:'4',point:ll(0,-180)},{id:'5',point:ll(-180,0)}],ways:[{id:'10',nodes:['2','1','4'],tags:{highway:'primary',name:'North South',lanes:'4','lanes:forward':'1','lanes:backward':'3'}},{id:'11',nodes:['5','1','3'],tags:{highway:'secondary',name:'East West',lanes:'2'}}],...extra});

test('only shared topological road nodes form junctions, never geometric bridge crossings or degree-two bends',()=>{
 const n=network(),c=analyzeJunctions(n);assert.equal(c.length,1);assert.equal(c[0].arms.length,4);
 const disconnected=network({nodes:[...n.nodes,{id:'99',point:origin}],ways:[n.ways[0],{...n.ways[1],nodes:['5','99','3'],tags:{...n.ways[1].tags,layer:'1',bridge:'yes'}}]});assert.equal(analyzeJunctions(disconnected).length,0);
});
test('short connected intersection fragments merge without merging a nearby unconnected crossing',()=>{
 const n=network();n.nodes.push({id:'6',point:ll(12,0)},{id:'7',point:ll(12,180)});n.ways[1].nodes=['5','1','6','3'];n.ways.push({id:'12',nodes:['6','7'],tags:{highway:'residential',name:'Side street'}});
 const c=analyzeJunctions(n);assert.equal(c.length,1);assert.deepEqual(c[0].node_ids,['1','6']);assert.equal(c[0].arms.length,5);
});
test('one-way and reversed one-way tags respect OSM way direction; asymmetric directional lanes stay on the correct side',()=>{
 const n=network();n.ways[1].tags={...n.ways[1].tags,oneway:'-1',lanes:'2'};const c=analyzeJunctions(n)[0],east=c.arms.find(a=>a.bearing>45&&a.bearing<135),west=c.arms.find(a=>a.bearing>225&&a.bearing<315);
 assert.equal(east.inbound,2);assert.equal(east.outbound,0);assert.equal(west.inbound,0);assert.equal(west.outbound,2);
 const north=c.arms.find(a=>a.bearing<45||a.bearing>315);assert.equal(north.inbound,1);assert.equal(north.outbound,3);
 const plan=createJunctionPlan(c);assert.deepEqual(plan.issues,[]);assert.equal(plan.site.lanes.filter(l=>l.arm_id===north.id).length,4);
 const offsets=plan.site.lanes.filter(l=>l.arm_id===north.id).map(l=>l.lateral_offset_m).sort((a,b)=>a-b);for(const [i,expected]of [-4.8,-1.6,1.6,4.8].entries())assert.ok(Math.abs(offsets[i]-expected)<1e-9);assert.ok(Math.abs(offsets[0]+offsets.at(-1))<1e-9);
});
test('curved approaches preserve per-lane 5/30/60 metre stations and one downstream counter, centred between their borders',()=>{
 const c=analyzeJunctions(network())[0];c.arms[0].path=[origin,ll(8,45),ll(0,100),ll(-10,180)];const plan=createJunctionPlan(c);assert.deepEqual(plan.issues,[]);const ids=new Set();
 for(const lane of plan.site.lanes){const ds=plan.devices.filter(d=>d.lane_id===lane.id);assert.deepEqual(ds.map(d=>d.offset_m),lane.flow==='inbound'?[5,30,60]:[10]);for(const d of ds){assert.ok(!ids.has(d.id));ids.add(d.id);assert.ok(d.id.length<=64);const center=pointAlong(lane.path,d.offset_m),cross=laneCrossSection(lane,d.offset_m);assert.ok(distanceM(center,[d.latitude,d.longitude])<.001);assert.ok(Math.abs(distanceM(center,cross.left)-distanceM(center,cross.right))<.001);}}
});
test('lane count, width and reference customization regenerates complete groups with stable identities and no mutation',()=>{
 const c=analyzeJunctions(network())[0],before=clone(c),settings=defaultArmSettings(c),a=c.arms[0],first=createJunctionPlan(c,settings);settings[a.id]={inbound:2,outbound:1,width_m:3.5,reference_m:18};const next=createJunctionPlan(c,settings);
 assert.deepEqual(c,before);assert.deepEqual(next.issues,[]);assert.equal(next.site.lanes.filter(l=>l.arm_id===a.id).length,3);assert.equal(next.devices.filter(d=>d.lane_id.includes(a.id)).length,7);assert.equal(next.devices.find(d=>d.id===first.devices[0].id)?.id,first.devices[0].id);assert.ok(next.site.lanes.filter(l=>l.arm_id===a.id).every(l=>l.lane_width_m===3.5));
 settings[a.id].width_m=0;assert.throws(()=>createJunctionPlan(c,settings));settings[a.id].width_m=3.5;settings[a.id].inbound=.5;assert.throws(()=>createJunctionPlan(c,settings));
});
test('short or ambiguous approaches do not invent road beyond the mapped path and cannot be saved as complete plans',()=>{
 const c=analyzeJunctions(network())[0];c.arms[0].path=[origin,ll(0,25)];const plan=createJunctionPlan(c);assert.ok(plan.issues.some(s=>s.includes('too short')));assert.throws(()=>saveJunctionPlan(defaultProject(),plan));assert.equal(pathLength(c.arms[0].path)<30,true);
});
test('saved plans round-trip separately from active sites and corrupted detector coordinates are rejected',()=>{
 const p=defaultProject(),before=clone(p),plan=createJunctionPlan(analyzeJunctions(network())[0]),next=saveJunctionPlan(p,plan);
 assert.deepEqual(p,before);assert.deepEqual(next.intersections,p.intersections);assert.deepEqual(next.devices,p.devices);assert.deepEqual(validateProject(next),[]);assert.deepEqual(validateProject(JSON.parse(JSON.stringify(next))),[]);assert.equal(saveJunctionPlan(next,plan).installation_plans.length,1);
 for(const damage of [q=>q[0].devices[0].latitude=null,q=>q[0].devices[0].longitude+=.001,q=>q.push(clone(q[0])),q=>q[0].devices.pop(),q=>q[0].site.lanes[0].lane_width_m=-2,q=>Object.values(q[0].settings)[0].width_m=0]){const q=clone(next.installation_plans);damage(q);assert.ok(validateInstallationPlans(q).length);}
});
test('radius filtering is metric, bounded by extract coverage and independent of map zoom',()=>{
 const cs=[{id:'near',point:ll(100,0)},{id:'far',point:ll(1500,0)}];assert.deepEqual(junctionsInRadius(cs,origin,500).map(c=>c.id),['near']);assert.equal(junctionsInRadius(cs,origin,2000).length,2);assert.throws(()=>junctionsInRadius(cs,origin,3000));assert.throws(()=>junctionsInRadius(cs,origin,NaN));
});
test('bundled Mandaue topology covers all three configured study sites and all supported radius circles',()=>{
 const cs=analyzeJunctions(ROAD_NETWORK),p=defaultProject(),near=junctionsInRadius(cs,ROAD_NETWORK.source.center,1000);assert.ok(near.length>20);assert.deepEqual([...new Set(cs.map(c=>candidateForStudy(c,p)?.id).filter(Boolean))].sort(),['J-A','J-B','J-C']);
 const [w,s,e,n]=ROAD_NETWORK.source.bbox;for(const boundary of [[s,origin[1]],[n,origin[1]],[origin[0],w],[origin[0],e]])assert.ok(distanceM(origin,boundary)>2200);
 for(const c of near){const plan=createJunctionPlan(c);if(!plan.issues.length)assert.deepEqual(validateInstallationPlans([plan]),[]);}
});
