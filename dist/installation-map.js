/* Installation preview helpers. Planning references are not physical hardware identities. */
import {laneEnvelope,pathLength} from './geometry.js';
export const PROPOSED_PUCK_DIAMETER_M=.123;
export function installationDevices(project,siteId){return siteId?project.devices.filter(d=>d.intersection_id===siteId):[];}
export function installationBoundsPoints(project,siteId){const site=project.intersections.find(j=>j.id===siteId);if(!site)return project.intersections.map(j=>[j.latitude,j.longitude]);const points=[[site.latitude,site.longitude]];for(const lane of site.lanes||[])if(lane.path?.length>1){const length=Math.min(pathLength(lane.path),lane.flow==='inbound'?65:(site.downstream_offset_m||10)+8),band=laneEnvelope(lane,length);points.push(...band.left,...band.right);}for(const d of installationDevices(project,siteId).filter(d=>['sensor','controller'].includes(d.role)))if(Number.isFinite(d.latitude)&&Number.isFinite(d.longitude))points.push([d.latitude,d.longitude]);return points;}
export function planningIdentity(device){return {reference:device.id,kind:'planning reference',status:device.hardware_uid?'hardware UID recorded; enrollment unverified':'hardware UID not assigned',hardware_uid:device.hardware_uid||null};}
export function googleMapsUrl(site){return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${site.latitude},${site.longitude}`)}`;}
