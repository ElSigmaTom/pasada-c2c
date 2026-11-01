export const MIN_SCALE=.08,MAX_SCALE=20;
export const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
export function project(c,x,y,w,h){return[w/2+(x-c.x)*c.scale,h/2-(y-c.y)*c.scale];}
export function unproject(c,x,y,w,h){return[c.x+(x-w/2)/c.scale,c.y-(y-h/2)/c.scale];}
export function fitCamera(b,w,h,padding=35){return{x:(b[0]+b[2])/2,y:(b[1]+b[3])/2,scale:clamp(Math.min((w-padding*2)/Math.max(1,b[2]-b[0]),(h-padding*2)/Math.max(1,b[3]-b[1])),MIN_SCALE,MAX_SCALE)};}
export function zoomCamera(c,factor,p,w,h){const[x,y]=unproject(c,...p,w,h),scale=clamp(c.scale*factor,MIN_SCALE,MAX_SCALE);return{x:x-(p[0]-w/2)/scale,y:y+(p[1]-h/2)/scale,scale};}
export function panCamera(c,dx,dy){return{...c,x:c.x-dx/c.scale,y:c.y+dy/c.scale};}
export function pinchCamera(c,start,mid,factor,w,h){const[x,y]=unproject(c,...start,w,h),scale=clamp(c.scale*factor,MIN_SCALE,MAX_SCALE);return{x:x-(mid[0]-w/2)/scale,y:y+(mid[1]-h/2)/scale,scale};}
export function visibleBounds(c,w,h){return[c.x-w/(2*c.scale),c.y-h/(2*c.scale),c.x+w/(2*c.scale),c.y+h/(2*c.scale)];}
export function fitSignals(g,focus,w,h){const s=g.signals.filter(s=>focus==='all'||s.site===focus),p=focus==='all'&&s.length>1?130:135,x=s.map(s=>s.x),y=s.map(s=>s.y);return fitCamera([Math.min(...x)-p,Math.min(...y)-p,Math.max(...x)+p,Math.max(...y)+p],w,h);}
export function constrainCamera(c,g,w=0,h=0){
 const b=g.location.convBoundary.split(',').map(Number),mw=b[2]-b[0],mh=b[3]-b[1],min=w&&h?Math.max(MIN_SCALE,.85*Math.min(w/(mw+80),h/(mh+80))):MIN_SCALE,scale=clamp(c.scale,min,MAX_SCALE),hw=w/(2*scale),hh=h/(2*scale);
 const x=w?(hw*2>=mw?(b[0]+b[2])/2:clamp(c.x,b[0]+hw*.3,b[2]-hw*.3)):clamp(c.x,b[0]-120,b[2]+120),y=h?(hh*2>=mh?(b[1]+b[3])/2:clamp(c.y,b[1]+hh*.3,b[3]-hh*.3)):clamp(c.y,b[1]-120,b[3]+120);return{x,y,scale};
}
export function closestHit(hits,x,y,radius=9){let best=null,d=radius;for(const hit of hits){const n=Math.hypot(hit.x-x,hit.y-y);if(n<=d){best=hit;d=n;}}return best;}
