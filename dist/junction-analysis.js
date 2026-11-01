/* Topology-based discovery and editable, metre-based installation templates.
 * Geometric crossings without a shared OSM node do not become junctions. */
import {distanceM,pathLength,slicePath,offsetPath,bearingDeg,makeLanePucks,LAYOUT_REVISION} from './geometry.js';
const copy=x=>JSON.parse(JSON.stringify(x));
const integer=x=>/^\d+$/.test(String(x??''))?Number(x):null;
const direction=b=>['N','E','S','W'][Math.floor((b+45)%360/90)];
const key=(a,b)=>[a,b].sort().join(':');

export function analyzeJunctions(network){
 const nodes=new Map(network.nodes.map(n=>[n.id,n])),adj=new Map(),edges=new Map();
 for(const way of network.ways){
  const t=way.tags;if(['private','no'].includes(t.access)||['private','no'].includes(t.motor_vehicle))continue;
  for(let i=1;i<way.nodes.length;i++){
   const a=way.nodes[i-1],b=way.nodes[i];if(a===b||!nodes.has(a)||!nodes.has(b))continue;
   const k=key(a,b),edge={a,b,way,forwardA:a,length:distanceM(nodes.get(a).point,nodes.get(b).point)};
   if(edges.has(k))continue;edges.set(k,edge);
   for(const [from,to]of [[a,b],[b,a]]){if(!adj.has(from))adj.set(from,new Map());adj.get(from).set(to,edge);}
  }
 }
 const branches=[...adj].filter(([,neighbors])=>neighbors.size>=3).map(([id])=>id).sort((a,b)=>Number(a)-Number(b)),branchSet=new Set(branches),assigned=new Set(),groups=[];
 // Merge only connected, short, same-level junction fragments; no planar crossing test.
 for(const seed of branches){if(assigned.has(seed))continue;const group=[seed],queue=[seed];assigned.add(seed);
  while(queue.length){const start=queue.shift();for(const [next,e]of adj.get(start)||[]){let previous=start,current=next,length=e.length;const seen=new Set([start]);
   while(length<=32&&!seen.has(current)){seen.add(current);if(branchSet.has(current)){if(!assigned.has(current)&&group.every(id=>distanceM(nodes.get(id).point,nodes.get(current).point)<=48)){assigned.add(current);group.push(current);queue.push(current);}break;}
    const onward=[...(adj.get(current)||[])].filter(([id])=>id!==previous);if(onward.length!==1)break;const [id,edge]=onward[0];previous=current;current=id;length+=edge.length;
   }
  }}groups.push(group);
 }
 const results=[];
 for(const group of groups){const members=new Set(group),arms=[],used=new Set();
  for(const start of group)for(const [first,initial]of adj.get(start)||[]){if(members.has(first))continue;const path=[nodes.get(start).point],ids=[start],visited=new Set([start]);let previous=start,current=first,edge=initial,walk=0,endsInside=false;
   for(let guard=0;guard<300;guard++){
    if(visited.has(current))break;visited.add(current);path.push(nodes.get(current).point);ids.push(current);walk+=edge.length;
    if(members.has(current)){endsInside=true;break;}
    if(walk>=145)break;
    let next=[...(adj.get(current)||[])].filter(([id])=>id!==previous&&!visited.has(id));
    if(next.length>1){const heading=bearingDeg([nodes.get(previous).point,nodes.get(current).point]);next=next.map(x=>({x,angle:Math.abs((bearingDeg([nodes.get(current).point,nodes.get(x[0]).point])-heading+540)%360-180)})).filter(x=>x.angle<35).sort((a,b)=>a.angle-b.angle);if(!next.length||next[1]&&next[1].angle-next[0].angle<20)break;next=[next[0].x];}
    if(next.length!==1)break;const [id,e]=next[0];if(String(e.way.tags.layer||'0')!==String(initial.way.tags.layer||'0'))break;
    // Follow the geometric continuation through split ways, never through another branch.
    previous=current;current=id;edge=e;
   }
   if(endsInside||path.length<2)continue;const armKey=key(start,first);if(used.has(armKey))continue;used.add(armKey);
   const t=initial.way.tags,awayForward=initial.forwardA===start,oneway=t.oneway==='-1'?-1:['yes','1','true'].includes(t.oneway)||t.junction==='roundabout'?1:0;
   const total=integer(t.lanes),both=integer(t['lanes:both_ways'])||0;let f=integer(t['lanes:forward']),b=integer(t['lanes:backward']),assumed=false;
   if(oneway){const count=total||f||b||1;f=oneway===1?count:0;b=oneway===-1?count:0;assumed=!total&&!integer(t['lanes:forward'])&&!integer(t['lanes:backward']);}
   else{const usable=total===null?null:Math.max(0,total-both);if(f===null&&b!==null&&usable!==null)f=usable-b;if(b===null&&f!==null&&usable!==null)b=usable-f;
    if(f===null||b===null){assumed=true;f=f??(usable!==null?Math.ceil(usable/2):1);b=b??(usable!==null?Math.floor(usable/2):1);}}
   f=Math.max(0,Math.min(8,f));b=Math.max(0,Math.min(8,b));const inbound=awayForward?b:f,outbound=awayForward?f:b;
   const widthMatch=/^([\d.]+)\s*(?:m)?$/.exec(t.width||''),width=widthMatch&&total?Number(widthMatch[1])/total:3.2;
   arms.push({id:`N${start}T${first}`,name:t.name||t.ref||'Unnamed road',path,osm_way_id:initial.way.id,node_ids:ids,bearing:bearingDeg(path),inbound,outbound,width_m:width>=2.2&&width<=4.5?width:3.2,lane_source:assumed?'Assumed · check lane counts':'OSM lane tags',width_source:widthMatch&&total?'OSM width / lanes':'Assumed 3.2 m',signal_node_ids:ids.filter(id=>nodes.get(id).tags?.highway==='traffic_signals'&&group.some(g=>distanceM(nodes.get(id).point,nodes.get(g).point)<=45)),crosses_junction:ids.slice(1).some(id=>branchSet.has(id)&&!members.has(id)),roundabout:t.junction==='roundabout'||['alternating','reversible'].includes(t.oneway)});
  }
  if(arms.length<3)continue;arms.sort((a,b)=>a.bearing-b.bearing||a.id.localeCompare(b.id));
  const point=[0,1].map(i=>group.reduce((s,id)=>s+nodes.get(id).point[i],0)/group.length),names=[...new Set(arms.map(a=>a.name))];
  results.push({id:`OSM-${group[0]}`,node_ids:group,point,name:names.slice(0,3).join(' × '),arms,signal_tag:false,signal_node_ids:[],complex:arms.some(a=>a.roundabout),source:'OpenStreetMap road topology'});
 }
 // One mapped signal can authorize only its nearest connected junction group.
 // Mid-block pedestrian crossings tagged only highway=crossing do not qualify.
 const owners=new Map();for(const c of results)for(const id of new Set([...c.node_ids.filter(id=>nodes.get(id).tags?.highway==='traffic_signals'),...c.arms.flatMap(a=>a.signal_node_ids)])){const distance=Math.min(...c.node_ids.map(n=>distanceM(nodes.get(n).point,nodes.get(id).point))),old=owners.get(id);if(!old||distance<old.distance||distance===old.distance&&c.id<old.candidate.id)owners.set(id,{candidate:c,distance});}
 for(const [id,{candidate}]of owners){candidate.signal_tag=true;candidate.signal_node_ids.push(id);}
 return results;
}

export function junctionsInRadius(candidates,center,radiusM,maxRadius=2000){if(!Number.isFinite(radiusM)||radiusM<250||radiusM>maxRadius)throw Error(`Choose a radius from 0.25 to ${maxRadius/1000} km.`);return candidates.filter(c=>distanceM(center,c.point)<=radiusM);}
export function candidateForStudy(c,project){return project.intersections.find(j=>distanceM(c.point,[j.latitude,j.longitude])<55);}
// Known configured study crossings are user-established signalized intersections.
export function signalizedJunctions(candidates,project){
 const best=new Map();for(const c of candidates){const j=candidateForStudy(c,project);if(j&&(!best.has(j.id)||distanceM(c.point,[j.latitude,j.longitude])<distanceM(best.get(j.id).point,[j.latitude,j.longitude])))best.set(j.id,c);}
 return candidates.filter(c=>{const j=candidateForStudy(c,project);if(j&&best.get(j.id).id!==c.id)return false;return c.signal_tag===true||!!(j&&(j.signalized===true||project.study_area?.id==='MANDAUE-PAPER-P33'&&['J-A','J-B','J-C'].includes(j.id)));});
}
export function defaultArmSettings(candidate){return Object.fromEntries(candidate.arms.map(a=>[a.id,{inbound:a.inbound,outbound:a.outbound,width_m:a.width_m,reference_m:12}]));}

export function createJunctionPlan(candidate,settings=defaultArmSettings(candidate)){
 const lanes=[],issues=[],warnings=[];
 if(candidate.complex)issues.push('Roundabout or reversible-lane geometry needs a manual layout before this plan can be saved.');
 for(const arm of candidate.arms){if(arm.crosses_junction)warnings.push(`${arm.name}: the approach passes a nearby junction; check detector attribution and spacing.`);const s=settings[arm.id];if(!s)throw Error('Missing road-arm settings.');const ni=Number(s.inbound),no=Number(s.outbound),width=Number(s.width_m),ref=Number(s.reference_m);
  if(![ni,no].every(n=>Number.isInteger(n)&&n>=0&&n<=8)||ni+no<1)throw Error('Use 0–8 lanes per direction and at least one lane per road arm.');
  if(!Number.isFinite(width)||width<2.2||width>4.5||!Number.isFinite(ref)||ref<0||ref>40)throw Error('Use a lane width of 2.2–4.5 m and a reference distance of 0–40 m.');
  for(const flow of ['inbound','outbound'])for(let number=1;number<=(flow==='inbound'?ni:no);number++){
   // Right-hand traffic: incoming lanes lie left while looking away from the crossing.
   const offset=ni&&no?((flow==='inbound'?-(number-.5):(number-.5))+(ni-no)/2)*width:(number-((flow==='inbound'?ni:no)+1)/2)*width;
   const shifted=offsetPath(arm.path,offset),need=ref+(flow==='inbound'?65:18);
   if(pathLength(shifted)<need){issues.push(`${arm.name}: ${flow} path is too short for the complete detector row before the next junction. Adjust the reference or map this arm manually.`);continue;}
   const path=slicePath(shifted,ref,need);lanes.push({id:`${candidate.id}-${arm.id}-${flow==='inbound'?'IN':'OUT'}-L${number}`,arm_id:arm.id,road_name:arm.name,approach:direction(arm.bearing),flow,lane_number:number,lane_width_m:width,path,reference:path[0],lateral_offset_m:offset,reference_status:'Automatic junction-edge proxy; verify the actual signal / stop line.',geometry_source:`OSM way ${arm.osm_way_id}; ${arm.lane_source}; ${arm.width_source}`});
  }
 }
 const site={id:candidate.id,name:candidate.name,latitude:candidate.point[0],longitude:candidate.point[1],layout_revision:LAYOUT_REVISION,downstream_offset_m:10,lanes};
 if(!lanes.some(l=>l.flow==='inbound')||!lanes.some(l=>l.flow==='outbound'))issues.push('Map both incoming and outgoing lanes before saving this plan.');
 return {schema:'pasada.installation-plan/0.1.0',id:candidate.id,name:candidate.name,source:{provider:'OpenStreetMap contributors',node_ids:candidate.node_ids,reference_status:'unsurveyed',signal_tag:candidate.signal_tag,signal_node_ids:candidate.signal_node_ids||[]},settings:copy(settings),site,devices:makeLanePucks(site),issues:[...new Set(issues)],warnings:[...new Set(warnings)],status:'planning',updated_at:new Date().toISOString()};
}

export function saveJunctionPlan(project,plan){
 if(plan.source?.signal_tag!==true)throw Error('Only intersections with mapped traffic-light evidence can be saved as new plans.');if(plan.issues.length)throw Error('Resolve the geometry issues before saving.');const p=copy(project);p.installation_plans??=[];const index=p.installation_plans.findIndex(x=>x.id===plan.id);if(index<0)p.installation_plans.push(copy(plan));else p.installation_plans[index]=copy(plan);return p;
}
export function validateInstallationPlans(plans){
 if(plans===undefined)return [];if(!Array.isArray(plans)||plans.length>100)return ['Use up to 100 saved installation plans.'];const ids=new Set(),deviceIds=new Set(),issues=[];
 for(const p of plans){if(p?.schema!=='pasada.installation-plan/0.1.0'||typeof p.id!=='string'||ids.has(p.id)||p.site?.id!==p.id||!Array.isArray(p.site?.lanes)||p.site.lanes.length>150||!Array.isArray(p.devices)||p.devices.length>500||!Array.isArray(p.issues)||p.issues.length){issues.push('Invalid or duplicate installation plan.');continue;}ids.add(p.id);
  try{if(!p.settings||typeof p.settings!=='object'||Array.isArray(p.settings)||Object.values(p.settings).some(s=>!s||![s.inbound,s.outbound].every(n=>Number.isInteger(n)&&n>=0&&n<=8)||s.inbound+s.outbound<1||!Number.isFinite(s.width_m)||s.width_m<2.2||s.width_m>4.5||!Number.isFinite(s.reference_m)||s.reference_m<0||s.reference_m>40))throw Error();const laneIds=new Set();for(const l of p.site.lanes){if(!l||typeof l.id!=='string'||laneIds.has(l.id)||!['inbound','outbound'].includes(l.flow)||!Number.isFinite(l.lane_width_m)||l.lane_width_m<2.2||l.lane_width_m>4.5||!Array.isArray(l.path)||l.path.length<2||l.path.length>1000||l.path.some(ll=>!Array.isArray(ll)||ll.length!==2||!ll.every(Number.isFinite)||Math.abs(ll[0])>90||Math.abs(ll[1])>180))throw Error();laneIds.add(l.id);}const expected=makeLanePucks(p.site);if(expected.length!==p.devices.length||!expected.length)throw Error();for(const d of expected){const actual=p.devices.find(x=>x.id===d.id);if(!actual||actual.role!=='sensor'||!Number.isFinite(actual.latitude)||!Number.isFinite(actual.longitude)||Math.abs(actual.latitude)>90||Math.abs(actual.longitude)>180||!Number.isFinite(d.latitude)||!Number.isFinite(d.longitude)||deviceIds.has(d.id)||distanceM([d.latitude,d.longitude],[actual.latitude,actual.longitude])>.05||actual.offset_m!==d.offset_m||actual.placement!==d.placement||actual.lane_id!==d.lane_id||actual.intersection_id!==p.id)throw Error();deviceIds.add(d.id);}}catch{issues.push(`${p.id}: invalid detector geometry or identities.`);}
 }
 return issues;
}
