/* Vehicle identity and beacon enrollment. Browser workspace records only;
 * protected transport credentials and agency authentication are external. */
export const BEACON_FIRMWARE='pasada-beacon-0.1.0';
export const VEHICLE_TYPES=Object.freeze({ambulance:'Ambulance',fire:'Fire truck',rescue:'Rescue / disaster response',police:'Police response',escort:'Protective escort / PSG',other:'Other authorized vehicle'});
export const AUTHORIZATION_STATES=Object.freeze({pending:'Pending',approved:'Approved',suspended:'Suspended',revoked:'Revoked'});
const copy=x=>JSON.parse(JSON.stringify(x));
const clean=x=>String(x??'').trim();
const identifier=x=>typeof x==='string'&&/^[A-Za-z0-9_-]{1,64}$/.test(x);
const normalized=x=>clean(x).replace(/\s+/g,'').toUpperCase();

export function defaultDemoVehicle(createdAt='2026-10-26T00:00:00+08:00'){
 return {id:'AMB-DEMO-01',call_sign:'Demo ambulance',agency:'PASADA demonstration',vehicle_type:'ambulance',registration:'',beacon_id:'EV-DEMO-01',hardware_uid:'',home_site_id:'J-A',authorization_status:'approved',authorization_reference:'SIMULATION ONLY',created_at:createdAt,updated_at:createdAt,demo:true};
}
export function fleetRecords(project){return project.vehicles??project.devices.filter(d=>d.role==='beacon').map((d,i)=>d.id==='EV-DEMO-01'?defaultDemoVehicle(project.project.created_at):{id:`LEGACY-${i+1}`,call_sign:d.id,agency:'Unassigned',vehicle_type:'other',registration:'',beacon_id:d.id,hardware_uid:d.hardware_uid||'',home_site_id:d.intersection_id,authorization_status:'pending',authorization_reference:'',created_at:project.project.created_at,updated_at:project.project.created_at});}
export function ensureFleetRegistry(project){const p=copy(project);if(p.vehicles===undefined)p.vehicles=fleetRecords(p);return p;}

export function validateFleet(project){
 if(project.vehicles===undefined)return [];
 const errors=[],ids=new Set(),beacons=new Set(),hardware=new Set(),plates=new Set();
 if(!Array.isArray(project.vehicles)||project.vehicles.length>100)return ['Vehicle registry must contain 0–100 vehicles.'];
 for(const v of project.vehicles){
  if(!v||typeof v!=='object'){errors.push('Invalid vehicle record.');continue;}
  if(!identifier(v.id)||ids.has(v.id))errors.push('Vehicle IDs must be unique and use letters, numbers, hyphens or underscores.');ids.add(v.id);
  if(typeof v.call_sign!=='string'||!v.call_sign.trim()||v.call_sign.length>80)errors.push(`${v.id}: enter a vehicle call sign (up to 80 characters).`);
  if(typeof v.agency!=='string'||!v.agency.trim()||v.agency.length>120)errors.push(`${v.id}: enter the operating agency (up to 120 characters).`);
  if(!Object.hasOwn(VEHICLE_TYPES,v.vehicle_type))errors.push(`${v.id}: select a supported vehicle type.`);
  if(!Object.hasOwn(AUTHORIZATION_STATES,v.authorization_status))errors.push(`${v.id}: invalid authorization status.`);
  if(!identifier(v.beacon_id)||beacons.has(v.beacon_id))errors.push(`${v.id}: a beacon may be assigned to only one vehicle.`);beacons.add(v.beacon_id);
  if(!project.devices.some(d=>d.id===v.beacon_id&&d.role==='beacon'))errors.push(`${v.id}: assigned beacon is not in the device inventory.`);
  if(!project.intersections.some(j=>j.id===v.home_site_id))errors.push(`${v.id}: select a valid home service site.`);
  for(const [key,max]of [['registration',32],['hardware_uid',80],['authorization_reference',160]])if(typeof v[key]!=='string'||v[key].length>max)errors.push(`${v.id}: invalid ${key}.`);
  const hw=normalized(v.hardware_uid),plate=normalized(v.registration);
  if(hw&&hardware.has(hw))errors.push(`${v.id}: this hardware UID is already assigned.`);if(hw)hardware.add(hw);
  if(plate&&plates.has(plate))errors.push(`${v.id}: this plate / registration is already registered.`);if(plate)plates.add(plate);
  if(v.authorization_status==='approved'&&!clean(v.authorization_reference))errors.push(`${v.id}: an approval reference is required for approved priority.`);
 }
 return [...new Set(errors)];
}

export function saveVehicle(project,input,{id,now=new Date().toISOString()}={}){
 const p=ensureFleetRegistry(project),old=id?p.vehicles.find(v=>v.id===id):null;
 if(id&&!old)throw Error('Vehicle record not found.');
 const record={id:old?.id||clean(input.id),call_sign:clean(input.call_sign),agency:clean(input.agency),vehicle_type:clean(input.vehicle_type),registration:clean(input.registration).toUpperCase(),beacon_id:clean(input.beacon_id),hardware_uid:clean(input.hardware_uid),home_site_id:clean(input.home_site_id)||p.intersections[0].id,authorization_status:clean(input.authorization_status)||'pending',authorization_reference:clean(input.authorization_reference),created_at:old?.created_at||now,updated_at:now,...(old?.demo?{demo:true}:{})};
 if(!identifier(record.id)||!identifier(record.beacon_id))throw Error('Use letters, numbers, hyphens or underscores for vehicle and beacon IDs (maximum 64).');
 const existing=p.devices.find(d=>d.id===record.beacon_id);
 if(existing&&existing.role!=='beacon')throw Error('This beacon ID belongs to a road device. Choose a different ID.');
 if(!old&&p.vehicles.some(v=>v.id===record.id))throw Error('Vehicle ID already exists.');
 if(!existing)p.devices.push({id:record.beacon_id,role:'beacon',intersection_id:record.home_site_id,latitude:null,longitude:null,location_status:'mobile',firmware:BEACON_FIRMWARE,commissioning:{state:'planned',transport:'simulated'}});
 if(old)p.vehicles[p.vehicles.findIndex(v=>v.id===old.id)]=record;else p.vehicles.push(record);
 const errors=validateFleet(p);if(errors.length)throw Error(errors[0]);
 const beacon=p.devices.find(d=>d.id===record.beacon_id);beacon.hardware_uid=record.hardware_uid||undefined;beacon.vehicle_id=record.id;beacon.firmware=BEACON_FIRMWARE;beacon.commissioning={state:'planned',transport:'simulated'};
 return {project:p,vehicle:record};
}

export function beaconAuthorization(project,beaconId,vehicleId){
 const device=project.devices.find(d=>d.id===beaconId&&d.role==='beacon');if(!device)return {allowed:false,reason:'Beacon is not enrolled'};
 // Legacy replay contracts retain their original behavior. Editing/importing
 // a working installation upgrades it explicitly with ensureFleetRegistry.
 if(project.vehicles===undefined)return {allowed:true,legacy:true,vehicle:null};
 const vehicle=project.vehicles.find(v=>v.beacon_id===beaconId);
 if(!vehicle)return {allowed:false,reason:'Beacon has no registered vehicle'};
 if(vehicleId!==undefined&&vehicle.id!==vehicleId)return {allowed:false,reason:'Vehicle / beacon identity mismatch',vehicle};
 return {allowed:vehicle.authorization_status==='approved',reason:AUTHORIZATION_STATES[vehicle.authorization_status]||'Unknown authorization',vehicle};
}
export function beaconProfile(project,beaconId){
 const vehicle=fleetRecords(project).find(v=>v.beacon_id===beaconId),device=project.devices.find(d=>d.id===beaconId&&d.role==='beacon');
 if(!device||!vehicle)return null;
 return {vehicle_id:vehicle.id,call_sign:vehicle.call_sign,agency:vehicle.agency,vehicle_type:vehicle.vehicle_type,registration:vehicle.registration,beacon_id:beaconId,hardware_uid:vehicle.hardware_uid||null,firmware_build:BEACON_FIRMWARE,authorization_status:vehicle.authorization_status,priority_authorized:beaconAuthorization(project,beaconId,vehicle.id).allowed,telemetry_period_s:1,position_source:'onboard-positioning',identity_enrollment:'not-provisioned',security_mode:'simulation',key_material_included:false};
}

export function fleetTelemetry(project,frame){return fleetRecords(project).map(vehicle=>{const track=(frame?.beacon_tracks||[]).find(t=>t.beacon_id===vehicle.beacon_id&&t.vehicle_id===vehicle.id),device=project.devices.find(d=>d.id===vehicle.beacon_id);return {...vehicle,track:track||null,setup_state:device?.commissioning?.state||'planned'};});}
