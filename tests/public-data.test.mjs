import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {manilaToUTC,toManilaInput,queryArchive,toCSV,FIELDS} from '../dist/public-data.js';
const archive=JSON.parse(fs.readFileSync(new URL('../dist/data/archive.json',import.meta.url))),start=Date.parse(archive.coverage_start_utc),end=Date.parse(archive.coverage_end_utc);
const params={siteIds:['J-A'],start,end,minutes:15};
test('Philippine local input is independent of browser timezone and rejects invalid dates',()=>{
 assert.equal(manilaToUTC('2026-10-30T08:00'),start);assert.equal(toManilaInput(start),'2026-10-30T08:00');
 assert.throws(()=>manilaToUTC('2026-02-30T08:00'));assert.throws(()=>manilaToUTC('2026-10-30T25:00'));assert.throws(()=>manilaToUTC('2026-10-30'));
});
test('one-site query respects half-open time range and preserves boundary totals',()=>{
 const r=queryArchive(archive,params);assert.equal(r.rows.length,20*4);assert.equal(r.metadata.coverage_percent,100);
 assert.ok(r.rows.every(r=>r.intersection_id==='J-A'&&Date.parse(r.period_start_utc)>=start&&Date.parse(r.period_end_utc)<=end));
 const expected=archive.records.filter(r=>r.intersection_id==='J-A').reduce((s,r)=>s+r.vehicle_count,0);assert.equal(r.rows.reduce((s,r)=>s+r.vehicle_count,0),expected);
 const a=queryArchive(archive,{...params,end:start+60000,minutes:1}),b=queryArchive(archive,{...params,start:start+60000,end:start+120000,minutes:1});assert.equal(a.rows.length,20);assert.ok(a.rows.every(r=>r.period_end_utc===b.rows[0].period_start_utc));
});
test('multiple selected intersections retain lane-level rows and explicit source',()=>{
 const r=queryArchive(archive,{...params,siteIds:['J-A','J-C']});assert.equal(r.rows.length,(20+18)*4);assert.deepEqual([...new Set(r.rows.map(r=>r.intersection_id))],['J-A','J-C']);assert.ok(r.rows.every(r=>r.source==='synthetic'));
});
test('missing minute is not replaced with zero or a complete aggregate',()=>{
 const a=structuredClone(archive);a.records=a.records.filter(r=>!(r.intersection_id==='J-A'&&r.lane_id===a.intersections[0].lanes[0].id&&r.period_start_utc===a.coverage_start_utc));const r=queryArchive(a,params),partial=r.rows.find(r=>r.quality==='incomplete');assert.equal(partial.vehicle_count,null);assert.equal(partial.observed_seconds,840);assert.equal(r.metadata.missing_lane_seconds,60);assert.ok(r.metadata.coverage_percent<100);
});
test('invalid counter interval is unavailable, while an observed zero remains valid',()=>{
 const a=structuredClone(archive),record=a.records.find(r=>r.intersection_id==='J-A');record.vehicle_count=-1;const r=queryArchive(a,{...params,end:start+60000,minutes:1});assert.equal(r.rows.length,19);assert.equal(r.metadata.missing_lane_seconds,60);
 record.vehicle_count=0;const zero=queryArchive(a,{...params,end:start+60000,minutes:1}).rows.find(r=>r.lane_id===record.lane_id);assert.equal(zero.vehicle_count,0);assert.equal(zero.quality,'complete');
});
test('outside coverage returns no fabricated data and partial outer range exposes missing time',()=>{
 const empty=queryArchive(archive,{...params,start:end,end:end+60000});assert.equal(empty.rows.length,0);assert.equal(empty.metadata.coverage_percent,0);
 const r=queryArchive(archive,{...params,start:start-60000,minutes:5});assert.ok(r.metadata.coverage_percent<100);assert.ok(r.rows.some(r=>r.quality==='incomplete'));
});
test('invalid sites, reversed ranges, unsupported bins and duplicate archive keys fail',()=>{
 for(const p of [{siteIds:[]},{siteIds:['J-X']},{end:start},{start:start+1},{end:start+32*86400000},{minutes:2}])assert.throws(()=>queryArchive(archive,{...params,...p}));
 const a=structuredClone(archive);a.records.push(a.records[0]);assert.throws(()=>queryArchive(a,params),/Duplicate/);
});
test('public JSON fields are allowlisted and CSV escapes text and spreadsheet formulas',()=>{
 const a=structuredClone(archive);a.secret='KEY';a.intersections[0].name='=HYPERLINK("example")';a.records[0].vehicle_id='EV-1';a.records[0].radio_key='KEY';const r=queryArchive(a,params);
 assert.deepEqual(Object.keys(r.rows[0]),FIELDS);assert.ok(!JSON.stringify(r).includes('radio_key'));assert.ok(!JSON.stringify(r).includes('EV-1'));assert.ok(toCSV(r.rows).includes("'="));assert.ok(toCSV([{...r.rows[0],road_name:'a,b\n"c"'}]).includes('"a,b\n""c"""'));
});
test('sample counts match the same synthetic engine once per lane boundary',async()=>{
 const {defaultProject,Engine}=await import('../dist/core.js');const p=defaultProject(),engine=new Engine(p,{scenario:'balanced',record:false}),frame=engine.step(3600);
 for(const j of frame.intersections){const rows=archive.records.filter(r=>r.intersection_id===j.id);assert.equal(rows.filter(r=>r.flow==='inbound').reduce((s,r)=>s+r.vehicle_count,0),j.arrived);assert.equal(rows.filter(r=>r.flow==='outbound').reduce((s,r)=>s+r.vehicle_count,0),j.departed);}
});
