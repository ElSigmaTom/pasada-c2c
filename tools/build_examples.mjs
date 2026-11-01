import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {defaultProject,deviceConfiguration,Engine,validateReplay} from '../dist/core.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const p=defaultProject(),e=new Engine(p,{scenario:'resilience'});e.step(180);const r=e.replay();if(validateReplay(r).length)throw Error('Example replay validation failed');
const beaconEngine=new Engine(p);beaconEngine.startBeaconDemo('J-A');beaconEngine.step(24);
const output={
 'project.json':p,
 'controller-pending-location.json':deviceConfiguration(p,p.intersections[0].controller_device_id),
 'beacon-replay.json':beaconEngine.replay(),
 'device.json':deviceConfiguration(p,p.devices.find(d=>d.role==='sensor').id),
 'synthetic-replay.json':r,
 'sumo_mapping.example.json':{schema:'pasada.sumo-mapping/0.1.0',provenance:{calibrated:false,description:'REPLACE with the actual demand/calibration lineage of the existing SUMO study.'},intersections:p.intersections.map(j=>({project_intersection_id:j.id,sumo_tls_id:`REPLACE_WITH_SUMO_TLS_FOR_${j.id}`,approach_lanes:Object.fromEntries(['N','E','S','W'].map(d=>[d,[`REPLACE_${j.id}_${d}_IN_LANE`]])),exit_lanes:Object.fromEntries(['N','E','S','W'].map(d=>[d,[`REPLACE_${j.id}_${d}_OUT_LANE`]])),phase_labels:{}}))}
};
for(const [name,value] of Object.entries(output))await fs.writeFile(path.join(root,'examples',name),JSON.stringify(value,null,2));
await fs.writeFile(path.join(root,'examples','beacon-packets.ndjson'),beaconEngine.beaconPackets.map(p=>JSON.stringify(p)).join('\n')+'\n');
console.log('Generated project, device, replay and explicit SUMO mapping examples.');
