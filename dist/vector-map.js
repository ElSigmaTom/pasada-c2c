/* Flat geographic context, following the supplied Fuente geometry approach.
 * Roads/buildings © OpenStreetMap contributors, ODbL. Local detail sits above
 * a continuous, dark-styled road basemap rather than replacing the whole world.
 */
import {MAP_DATA} from './map-data.js';
import {distanceM,laneEnvelope,pathLength} from './geometry.js';

export const MAP_PALETTE=Object.freeze({background:'#101318',building:'#292d35',buildingEdge:'#454a55',green:'#1d2926',water:'#172932',road:'#15181e',roadEdge:'#575b64',walk:'#34383f',lane:'#252a32',laneBorder:'#9097a1',label:'#aaaeb8'});
export const LOCAL_DETAIL_MIN_ZOOM=15.5;
export function localDetailVisible(zoom){return zoom>=LOCAL_DETAIL_MIN_ZOOM;}
export function localContextBounds(){const [west,south,east,north]=MAP_DATA.source.bbox;return [[south,west],[north,east]];}

// Do not relocate lanes or devices to make the background look tidier. This
// function is also used for operator-adjusted/imported geographic lane paths.
export function planningSurfaces(project){
 return project.intersections.flatMap(site=>site.lanes.filter(lane=>Array.isArray(lane.path)&&lane.path.length>=2).map(lane=>{
  const band=laneEnvelope(lane,pathLength(lane.path));
  return {site_id:site.id,lane_id:lane.id,flow:lane.flow,ring:[...band.left,...[...band.right].reverse()],left:band.left,right:band.right,reference:lane.path[0]};
 }));
}
export function contextApplies(project){const [west,south,east,north]=MAP_DATA.source.bbox;return project.intersections.some(j=>j.latitude>=south&&j.latitude<=north&&j.longitude>=west&&j.longitude<=east);}
export function contextSummary(project){return project&&!contextApplies(project)?'Continuous road map · configured lane geometry':`Continuous road map · ${MAP_DATA.buildings.length} local footprints`;}

export function createVectorBase(L,project){
 const surfaces=planningSurfaces(project),hasContext=contextApplies(project);
 const Layer=L.Layer.extend({
  onAdd(map){
   this._map=map;
   if(!map.getPane('geometryBase')){const pane=map.createPane('geometryBase');pane.style.zIndex='250';pane.style.pointerEvents='none';}
   this._canvas=L.DomUtil.create('canvas','vector-base-canvas leaflet-zoom-hide',map.getPane('geometryBase'));
   this._canvas.setAttribute('aria-label','Clean geographic map: flat building footprints and road surfaces');
   this._canvas.setAttribute('role','img');this._canvas.dataset.context=hasContext?'mandaue':'custom';
   this._queue=()=>{if(!this._frame)this._frame=requestAnimationFrame(()=>{this._frame=null;this.draw();});};
   map.on('move zoomend resize viewreset',this._queue);this.draw();
  },
  onRemove(map){map.off('move zoomend resize viewreset',this._queue);if(this._frame)cancelAnimationFrame(this._frame);this._canvas.remove();this._map=null;},
  draw(){
   const map=this._map;if(!map)return;
   const size=map.getSize(),ratio=Math.min(window.devicePixelRatio||1,2),canvas=this._canvas;
   canvas.width=Math.round(size.x*ratio);canvas.height=Math.round(size.y*ratio);canvas.style.width=size.x+'px';canvas.style.height=size.y+'px';L.DomUtil.setPosition(canvas,map.containerPointToLayerPoint([0,0]));
   // Keep the canvas transparent outside the local extract. An opaque canvas
   // used to hide the rest of the road network and produced the black void.
   const c=canvas.getContext('2d');c.scale(ratio,ratio);
   const zoom=map.getZoom(),bounds=map.getBounds().pad(.12),center=map.getCenter();
   if(!localDetailVisible(zoom))return;
   const metre=1/(156543.03392*Math.cos(center.lat*Math.PI/180)/2**zoom);
   const projected=ps=>ps.map(p=>map.latLngToContainerPoint(p));
   const visible=ps=>{let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;for(const p of ps){minX=Math.min(minX,p.x);maxX=Math.max(maxX,p.x);minY=Math.min(minY,p.y);maxY=Math.max(maxY,p.y);}return maxX>=-40&&maxY>=-40&&minX<=size.x+40&&minY<=size.y+40;};
   const path=(ps,close=false)=>{c.beginPath();ps.forEach((p,i)=>i?c.lineTo(p.x,p.y):c.moveTo(p.x,p.y));if(close)c.closePath();};
   const polygon=(shape,fill,stroke=null)=>{const rings=shape.rings.map(projected);if(!visible(rings[0]))return;c.beginPath();for(const ring of rings){ring.forEach((p,i)=>i?c.lineTo(p.x,p.y):c.moveTo(p.x,p.y));c.closePath();}c.fillStyle=fill;c.fill('evenodd');if(stroke){c.lineWidth=.65;c.strokeStyle=stroke;c.stroke();}};
   if(hasContext){
    const [[south,west],[north,east]]=localContextBounds(),nw=map.latLngToContainerPoint([north,west]),se=map.latLngToContainerPoint([south,east]);
    c.save();c.beginPath();c.rect(nw.x,nw.y,se.x-nw.x,se.y-nw.y);c.clip();c.fillStyle=MAP_PALETTE.background;c.fillRect(nw.x,nw.y,se.x-nw.x,se.y-nw.y);
    for(const land of MAP_DATA.land)polygon(land,land.kind==='water'?MAP_PALETTE.water:MAP_PALETTE.green);
    for(const building of MAP_DATA.buildings)polygon(building,MAP_PALETTE.building,MAP_PALETTE.buildingEdge);
    const roads=MAP_DATA.roads.map(r=>({...r,ps:projected(r.path)})).filter(r=>visible(r.ps));
    c.lineCap='round';c.lineJoin='round';
    for(const r of roads){path(r.ps);c.lineWidth=Math.max(1,r.width_m*metre)+1.4;c.strokeStyle=r.kind==='walk'?MAP_PALETTE.walk:MAP_PALETTE.roadEdge;c.stroke();}
    for(const r of roads){path(r.ps);c.lineWidth=Math.max(.7,r.width_m*metre);c.strokeStyle=r.kind==='walk'?MAP_PALETTE.walk:MAP_PALETTE.road;c.stroke();}
    c.restore();
   }
   // The installation lane paths determine the road bands around each study
   // site, so each puck remains between its own two borders at every zoom.
   for(const surface of surfaces){const ps=projected(surface.ring);if(!visible(ps))continue;path(ps,true);c.fillStyle=MAP_PALETTE.lane;c.fill();}
   if(zoom>=17.25){
    c.lineCap='butt';c.strokeStyle=MAP_PALETTE.laneBorder;c.lineWidth=Math.min(1,.11*metre);c.setLineDash([Math.max(2,2*metre),Math.max(2,3*metre)]);c.globalAlpha=.5;
    for(const surface of surfaces)for(const border of [surface.left,surface.right]){const ps=projected(border);if(visible(ps)){path(ps);c.stroke();}}
    c.globalAlpha=1;c.setLineDash([]);
   }
   // Label collision checks keep the overview readable; footprints are exact
   // OSM rings, while labels may move along their source road segment.
   const occupied=[];
   const label=(text,p,angle=0,kind='place')=>{
    const upper=kind==='street',font=upper?'9px ui-monospace,monospace':'10px ui-monospace,monospace';c.font=font;
    const w=Math.min(c.measureText(text).width,260)+10,h=14,rotW=Math.abs(Math.cos(angle))*w+Math.abs(Math.sin(angle))*h,rotH=Math.abs(Math.sin(angle))*w+Math.abs(Math.cos(angle))*h;
    const box={x:p.x-rotW/2,y:p.y-rotH/2,w:rotW,h:rotH};if(box.x<8||box.y<8||box.x+box.w>size.x-8||box.y+box.h>size.y-15||occupied.some(b=>box.x<b.x+b.w&&box.x+box.w>b.x&&box.y<b.y+b.h&&box.y+box.h>b.y))return;
    occupied.push(box);c.save();c.translate(p.x,p.y);c.rotate(angle);c.font=font;c.textAlign='center';c.textBaseline='middle';c.lineWidth=3;c.strokeStyle=MAP_PALETTE.background;c.strokeText(text,0,0,260);c.fillStyle=upper?'#8f959f':'#c2c5cd';c.fillText(text,0,0,260);c.restore();
   };
   // Reserve room around intersection labels and the HUD.
   occupied.push({x:48,y:5,w:300,h:65});
   for(const j of project.intersections){const p=map.latLngToContainerPoint([j.latitude,j.longitude]);occupied.push({x:p.x-30,y:p.y-55,w:210,h:90});}
   if(hasContext){
    const names=new Set();
    const candidates=MAP_DATA.roads.filter(r=>r.name&&r.kind==='road').map(r=>({r,len:pathLength(r.path)})).sort((a,b)=>b.len-a.len);
    for(const {r} of candidates){if(names.has(r.name))continue;let best=null;for(let i=1;i<r.path.length;i++){const a=map.latLngToContainerPoint(r.path[i-1]),b=map.latLngToContainerPoint(r.path[i]),len=a.distanceTo(b),mid=L.point((a.x+b.x)/2,(a.y+b.y)/2);if(len>48&&mid.x>30&&mid.y>50&&mid.x<size.x-30&&mid.y<size.y-25&&(!best||len>best.len))best={a,b,len,mid};}if(!best)continue;let angle=Math.atan2(best.b.y-best.a.y,best.b.x-best.a.x);if(angle>Math.PI/2)angle-=Math.PI;if(angle<-Math.PI/2)angle+=Math.PI;label(r.name.toUpperCase(),best.mid,angle,'street');names.add(r.name);}
    if(zoom>=16.5){for(const place of MAP_DATA.places){if(!bounds.contains(place.point))continue;if(project.intersections.every(j=>distanceM(place.point,[j.latitude,j.longitude])>650))continue;label(place.name,map.latLngToContainerPoint(place.point));}}
   }
   if(!hasContext){c.font='11px ui-monospace,monospace';c.fillStyle=MAP_PALETTE.label;c.fillText('Custom project · configured lane geometry',18,size.y-15);}
  }
 });
 // A native dark road basemap supplies continuous context beyond the extract.
 // Local planning geometry and equipment retain their own geographic layer.
 const credit='Basemap © <a href="https://www.esri.com/" target="_blank" rel="noopener">Esri</a>, HERE, Garmin, <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap contributors</a> and the GIS user community';
 const regional=L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',{maxNativeZoom:16,maxZoom:21,minZoom:3,className:'clean-context-tiles',attribution:credit});
 const regionalLabels=L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',{maxNativeZoom:16,maxZoom:21,minZoom:3,className:'clean-context-labels'});
 regional.on('tileload',()=>regional._map?.fire('geometrycoverage',{available:true}));
 regional.on('tileerror',()=>regional._map?.fire('geometrycoverage',{available:false}));
 return L.layerGroup([regional,regionalLabels,new Layer()]);
}
