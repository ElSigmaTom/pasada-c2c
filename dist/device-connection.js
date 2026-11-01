import {deviceConfiguration,SETTINGS,CONTROLLER_HARDWARE} from './core.js';
const copy=x=>JSON.parse(JSON.stringify(x));
// USB vendor filtering identifies a candidate serial interface, not a board model or firmware.
export const USB_FILTERS=Object.freeze([{usbVendorId:0x303a}]);
export function installationScopes(project){return [...project.intersections.map(j=>({id:j.id,name:j.mapped_name||j.name,kind:'Study site'})),...(project.installation_plans||[]).map(p=>({id:p.id,name:p.name,kind:'Saved plan'}))];}
export function installationContext(project,siteId){
 const original=project.intersections.find(j=>j.id===siteId),saved=project.installation_plans?.find(p=>p.id===siteId);
 if(!original&&!saved)throw Error('Choose a saved intersection plan.');
 const site=copy(original||saved.site);site.timing??={...SETTINGS};site.model??='pressure-v0';site.controller_device_id??=`CTRL-${site.id}`;
 const devices=copy(original?project.devices.filter(d=>d.intersection_id===siteId&&d.role!=='beacon'):saved.devices);
 if(!devices.some(d=>d.role==='controller'))devices.push({id:site.controller_device_id,role:'controller',intersection_id:site.id,latitude:null,longitude:null,location_status:'unlocated',hardware:copy(CONTROLLER_HARDWARE)});
 return {site,devices,profileFor:id=>deviceConfiguration({...copy(project),intersections:[site],devices,vehicles:[]},id)};
}
export function requestDevicePort(serial){if(!serial?.requestPort)throw Error('Use desktop Chrome or Edge on HTTPS to open the device chooser.');return serial.requestPort({filters:USB_FILTERS.map(f=>({...f}))});}
export function candidateInfo(port){const info=port.getInfo();if(info.usbVendorId!==0x303a)throw Error('Choose an Espressif USB serial device.');return {usbVendorId:info.usbVendorId,usbProductId:info.usbProductId,board_verified:false,firmware_installed:false};}
