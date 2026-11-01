import test from 'node:test';
import assert from 'node:assert/strict';
import {analyzeJunctions,signalizedJunctions,junctionsInRadius,createJunctionPlan,saveJunctionPlan,validateInstallationPlans,candidateForStudy} from '../dist/junction-analysis.js';
import {defaultProject,clone} from '../dist/core.js';
import {distanceM} from '../dist/geometry.js';
import {SIGNAL_CATALOG} from '../dist/signal-junctions.js';

const o=[10.32765,123.94465],ll=(x,y)=>[o[0]+y/111195,o[1]+x/109395];
function network(signal=true){return {nodes:[{id:'1',point:o,tags:signal?{highway:'traffic_signals'}:{}},{id:'2',point:ll(0,200)},{id:'3',point:ll(200,0)},{id:'4',point:ll(0,-200)},{id:'5',point:ll(-200,0)}],ways:[{id:'10',nodes:['2','1','4'],tags:{highway:'primary',name:'North South',lanes:'2'}},{id:'11',nodes:['5','1','3'],tags:{highway:'secondary',name:'East West',lanes:'2'}}]};}

test('unsignalized junctions cannot be selected or saved as new installation plans',()=>{
 const p=defaultProject(),unlit=analyzeJunctions(network(false));assert.equal(unlit.length,1);assert.deepEqual(signalizedJunctions(unlit,p),[]);assert.throws(()=>saveJunctionPlan(p,createJunctionPlan(unlit[0])),/traffic-light/);
 const lit=analyzeJunctions(network());assert.equal(signalizedJunctions(lit,p).length,1);assert.deepEqual(lit[0].signal_node_ids,['1']);assert.equal(saveJunctionPlan(p,createJunctionPlan(lit[0])).installation_plans.length,1);
});
test('pedestrian-crossing tags and isolated signal nodes do not qualify a vehicle junction',()=>{
 const n=network(false);n.nodes[0].tags={highway:'crossing',crossing:'traffic_signals'};n.nodes.push({id:'99',point:ll(2,2),tags:{highway:'traffic_signals'}});assert.deepEqual(signalizedJunctions(analyzeJunctions(n),defaultProject()),[]);
});
test('one approach signal is assigned to one connected junction, not its nearby unsignalized neighbor',()=>{
 const n=network(false);n.nodes.push({id:'6',point:ll(70,0)},{id:'7',point:ll(70,200)},{id:'8',point:ll(30,0),tags:{highway:'traffic_signals'}});n.ways[1].nodes=['5','1','8','6','3'];n.ways.push({id:'12',nodes:['6','7'],tags:{highway:'residential',name:'Side street'}});
 const c=analyzeJunctions(n);assert.equal(c.length,2);assert.equal(c.filter(c=>c.signal_tag).length,1);assert.equal(c.find(c=>c.signal_tag).id,'OSM-1');assert.deepEqual(c.find(c=>c.id==='OSM-6').signal_node_ids,[]);
});
test('old non-signalized saved plans remain exportable without making their junction selectable',()=>{
 const plan=createJunctionPlan(analyzeJunctions(network(false))[0]);assert.deepEqual(validateInstallationPlans([plan]),[]);const p=defaultProject();p.installation_plans=[plan];const before=clone(p);assert.deepEqual(signalizedJunctions(analyzeJunctions(network(false)),p),[]);assert.deepEqual(p,before);
});
test('expanded catalog has unique eligible junctions and distinct signal ownership at 2, 5 and 10 km',()=>{
 const {source,junctions}=SIGNAL_CATALOG,p=defaultProject(),eligible=signalizedJunctions(junctions,p),signals=new Set();assert.equal(source.max_radius_m,10000);assert.ok(junctions.length>30);assert.equal(new Set(junctions.map(j=>j.id)).size,junctions.length);
 for(const c of junctions){assert.ok(c.signal_tag||candidateForStudy(c,p));assert.ok(distanceM(c.point,source.center)<=10000);for(const id of c.signal_node_ids){assert.ok(!signals.has(id));signals.add(id);}}
 const counts=[2000,5000,10000].map(r=>junctionsInRadius(eligible,source.center,r,source.max_radius_m).length);assert.ok(counts[0]<counts[1]&&counts[1]<counts[2]);assert.throws(()=>junctionsInRadius(eligible,source.center,11000,source.max_radius_m));
 assert.deepEqual([...new Set(eligible.map(c=>candidateForStudy(c,p)?.id).filter(Boolean))].sort(),['J-A','J-B','J-C']);
 for(const c of eligible.filter(c=>!candidateForStudy(c,p))){const plan=createJunctionPlan(c);if(!plan.issues.length)assert.deepEqual(validateInstallationPlans([plan]),[]);}
});
