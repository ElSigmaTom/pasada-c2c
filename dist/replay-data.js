export const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const REPLAY_BASE=new URL('./replays/',import.meta.url);
export const ARM_LABELS={fixed:'Fixed baseline',rule:'PASADA local',local:'PASADA local',priority20:'Beacon priority · 20 s',priority60:'Beacon priority · 60 s'};
export const SITE_LABELS={J1:'A.C. Cortes / D.M. Cortes',J2:'D.M. Cortes / C. Ouano–F. Mendoza',J3:'A. Soriano / Ouano / S.B. Cabahug',CORRIDOR:'Connected three-intersection corridor'};
export function atOrBefore(rows,t,key='time_s'){
 let lo=0,hi=rows.length;while(lo<hi){const mid=(lo+hi)>>>1;if(Number(rows[mid][key])<=t)lo=mid+1;else hi=mid;}return lo?rows[lo-1]:null;
}
export function signalAt(run,site,t){return atOrBefore(run.supervisor_events[site]||[],t,'time')||run.initial_states[site];}
export function sampleAt(run,site,t){return atOrBefore(run.sensor_trace.filter(x=>x.site===site),t);}
export function matchingRuns(manifest,state){return manifest.runs.filter(r=>r.study===state.study&&r.layout===state.layout&&r.period===state.period&&r.seed===Number(state.seed));}
export function clock(t){return new Date(Math.max(0,t)*1000).toISOString().slice(11,19);}
export function timeRange(geometry,focus){
 const sites=geometry.signals.filter(s=>focus==='all'||s.site===focus),xs=sites.map(s=>s.x),ys=sites.map(s=>s.y),pad=geometry.layout==='CORRIDOR'&&focus==='all'?160:210;
 return [Math.min(...xs)-pad,Math.min(...ys)-pad,Math.max(...xs)+pad,Math.max(...ys)+pad];
}
export function vehicleState(motion,t){
 if(!motion||t<motion.capture_window_s[0]||t>motion.capture_window_s[1])return [];
 const i=Math.min(motion.frames.length-1,Math.floor((t-motion.capture_window_s[0])/motion.sample_s)),a=motion.frames[i],b=motion.frames[Math.min(i+1,motion.frames.length-1)],mix=b[0]===a[0]?0:(t-a[0])/(b[0]-a[0]),next=new Map(b[1].map(x=>[x[0],x]));
 return a[1].map(v=>{const n=next.get(v[0]);return n?[v[0],v[1]+(n[1]-v[1])*mix,v[2]+(n[2]-v[2])*mix,v[3]+(((n[3]-v[3]+540)%360)-180)*mix]:v;});
}

const cache=new Map();
export async function jsonFile(path,gzip=false){
 const url=new URL(path,REPLAY_BASE);if(cache.has(url.href))return cache.get(url.href);
 const promise=(async()=>{const r=await fetch(url);if(!r.ok)throw Error(`Could not load ${path} (${r.status}).`);if(!gzip)return r.json();const raw=await r.arrayBuffer(),signature=new Uint8Array(raw,0,Math.min(2,raw.byteLength));if(signature[0]!==31||signature[1]!==139)return JSON.parse(new TextDecoder().decode(raw));if(typeof DecompressionStream==='undefined')throw Error('Recorded runs need a browser with gzip decompression, such as current Chrome or Edge.');return new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'))).json();})();
 cache.set(url.href,promise);try{return await promise;}catch(e){cache.delete(url.href);throw e;}
}
