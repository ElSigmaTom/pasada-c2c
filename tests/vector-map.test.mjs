import test from 'node:test';
import assert from 'node:assert/strict';
import {defaultProject} from '../dist/core.js';
import {MAP_DATA} from '../dist/map-data.js';
import {planningSurfaces,contextApplies,createVectorBase,localContextBounds} from '../dist/vector-map.js';

function inside(point,ring){const [y,x]=point;let yes=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const [yi,xi]=ring[i],[yj,xj]=ring[j];if((yi>y)!==(yj>y)&&x<(xj-xi)*(y-yi)/(yj-yi)+xi)yes=!yes;}return yes;}

test('clean road polygons retain every planned puck inside its own lane at all three Mandaue sites',()=>{
 const project=defaultProject(),before=structuredClone(project),surfaces=planningSurfaces(project);
 for(const puck of project.devices.filter(d=>d.role==='sensor')){
  const lane=surfaces.find(s=>s.site_id===puck.intersection_id&&s.lane_id===puck.lane_id);
  assert.ok(lane,`Missing road surface for ${puck.id}`);
  assert.ok(inside([puck.latitude,puck.longitude],lane.ring),`${puck.id} is outside its rendered lane`);
 }
 assert.deepEqual(project,before,'Map rendering must not relocate equipment or lane paths');
});

test('context is Mandaue geographic source data, with valid closed building footprints',()=>{
 const project=defaultProject();assert.ok(contextApplies(project));
 const [west,south,east,north]=MAP_DATA.source.bbox;
 for(const j of project.intersections)assert.ok(j.latitude>south&&j.latitude<north&&j.longitude>west&&j.longitude<east);
 assert.equal(MAP_DATA.source.provider,'OpenStreetMap contributors');assert.ok(MAP_DATA.buildings.length>900);
 for(const b of MAP_DATA.buildings)for(const ring of b.rings){assert.ok(ring.length>=4);assert.deepEqual(ring[0],ring.at(-1));assert.ok(ring.flat().every(Number.isFinite));}
 assert.ok(MAP_DATA.roads.some(r=>r.name==='A.C. Cortes Avenue'));assert.ok(MAP_DATA.roads.some(r=>r.name==='D.M. Cortes Avenue'));assert.ok(MAP_DATA.roads.some(r=>r.name==='S.B. Cabahug Street'));
});

test('a custom Fuente project does not inherit Mandaue context',()=>{
 const p=defaultProject();p.intersections.forEach(j=>{j.latitude=10.3095;j.longitude=123.893;});assert.equal(contextApplies(p),false);
});

test('zooming out retains a continuous base and the local canvas cannot cover it with black',()=>{
 const fills=[],L={Layer:{extend:definition=>class{constructor(){Object.assign(this,definition);}}},DomUtil:{setPosition(){}},tileLayer:(url,options)=>({url,options,on(){return this;}}),layerGroup:layers=>layers};
 const layers=createVectorBase(L,defaultProject()),regional=layers[0],detail=layers.at(-1);
 assert.equal(regional.options.bounds,undefined,'The regional map must not be clipped to the local extract');
 assert.ok(regional.options.minZoom<=3);
 for(const zoom of [3,10,12,14,15]){
  const c={scale(){},fillRect(...args){fills.push(args);}};
  detail._map={getSize:()=>({x:900,y:600}),containerPointToLayerPoint:x=>x,getZoom:()=>zoom,getBounds:()=>({pad(){return this;}}),getCenter:()=>({lat:10.3,lng:123.9})};
  detail._canvas={style:{},getContext:()=>c};
  globalThis.window={devicePixelRatio:1};
  try{detail.draw();}finally{delete globalThis.window;}
 }
 assert.equal(fills.length,0,'Regional zoom must remain transparent above the continuous road map');
 const [[south,west],[north,east]]=localContextBounds();assert.ok(south<north&&west<east);
});
