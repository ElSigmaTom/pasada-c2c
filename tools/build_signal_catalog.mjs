// Compile only signalized installation candidates into the browser payload.
import fs from 'node:fs/promises';
import {analyzeJunctions,signalizedJunctions,junctionsInRadius} from '../dist/junction-analysis.js';
import {defaultProject} from '../dist/core.js';
const network=JSON.parse(await fs.readFile(new URL('../data/signal-road-network.json',import.meta.url),'utf8'));
const all=analyzeJunctions(network),project=defaultProject();
const junctions=signalizedJunctions(all,project).filter(c=>junctionsInRadius([c],network.source.center,network.source.max_radius_m,network.source.max_radius_m).length);
const catalog={source:{...network.source,eligibility:'Mapped vehicle traffic signals on the motor-road graph, or the three user-confirmed study intersections',analysis:'signalized-junctions-v1'},junctions};
await fs.writeFile(new URL('../dist/signal-junctions.js',import.meta.url),'// Traffic-signal road geometry © OpenStreetMap contributors, ODbL 1.0.\nexport const SIGNAL_CATALOG = '+JSON.stringify(catalog)+';\n');
console.log(JSON.stringify({roads:network.ways.length,nodes:network.nodes.length,junctions:junctions.length,radii_km:Object.fromEntries([2,5,10].map(km=>[km,junctionsInRadius(junctions,network.source.center,km*1000,network.source.max_radius_m).length]))}));
