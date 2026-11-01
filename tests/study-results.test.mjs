import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const results=JSON.parse(fs.readFileSync(new URL('../dist/study/results.json',import.meta.url)));
test('recorded SUMO release has both completed study protocols and source fingerprints',()=>{
 assert.equal(results.source,'recorded-sumo');assert.equal(results.matched.audit.runs,48);assert.equal(results.emergency.audit.runs,78);
 for(const source of [results.matched,results.emergency]){assert.match(source.package_sha256,/^[a-f0-9]{64}$/);for(const hash of Object.values(source.members))assert.match(hash,/^[a-f0-9]{64}$/);assert.ok(source.protocol);}
});
test('every viewer case has matching ordinary and emergency tables, including negative outcomes',()=>{
 for(const site of ['J1','J2','J3','CORRIDOR'])for(const period of ['AM','PM']){
  const key=`${site}_${period}`,label=(site==='CORRIDOR'?'Network':site)+' '+period;
  assert.ok(results.matched.tables.paired.some(r=>r.case===key));for(const t of ['table8','table9','table10'])assert.equal(results.matched.tables[t].filter(r=>r[0]===label).length,2);
  assert.ok(results.emergency.tables.pairs.some(r=>r.case===key&&r.baseline==='local'&&r.candidate==='priority20'));for(const t of ['table11','table12'])assert.equal(results.emergency.tables[t].filter(r=>r[0]===label).length,1);
 }
 assert.ok(results.matched.tables.paired.find(r=>r.case==='J1_PM').completion_change_pp<0);
 assert.ok(results.emergency.tables.pairs.find(r=>r.case==='J2_AM'&&r.baseline==='local'&&r.candidate==='priority20').EV_seconds_saved<0);
 const sample=JSON.parse(fs.readFileSync(new URL('../dist/data/archive.json',import.meta.url)));assert.equal(sample.source,'synthetic');
});
