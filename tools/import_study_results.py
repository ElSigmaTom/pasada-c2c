#!/usr/bin/env python3
"""Copy reviewed result tables/protocols from completed study packages; never run SUMO."""
from pathlib import Path
import argparse,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
def extract(path,folder,library_id):
    with zipfile.ZipFile(path) as z:
        prefix=path.stem+'/'+folder+'/'
        members={}
        for name in ['manuscript_tables.json','protocol.json','audit.json']:
            raw=z.read(prefix+name)
            members[name]={'sha256':hashlib.sha256(raw).hexdigest(),'data':json.loads(raw)}
    return {'package':path.name,'library_file_id':library_id,'package_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'members':{k:v['sha256'] for k,v in members.items()},'tables':members['manuscript_tables.json']['data'],'protocol':members['protocol.json']['data'],'audit':members['audit.json']['data']}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--matched',type=Path,required=True);p.add_argument('--emergency',type=Path,required=True);args=p.parse_args()
    result={'schema':'pasada.study-results/0.1.0','study_date':'2026-11-01','source':'recorded-sumo','simulator':'SUMO 1.28.0','scope':'Reconstructed motor-only Mandaue experiments. Separate from the interactive browser queue model. Not field results or trained RL.','matched':extract(args.matched,'results/paired_nov01','libfile_541c037705688191a616391a712aa3dd'),'emergency':extract(args.emergency,'results/emergency_nov01','libfile_c9c5f3ab55e48191bd4c8f2ca571f725')}
    assert result['matched']['audit']['runs']==48 and result['emergency']['audit']['runs']==78
    out=ROOT/'dist/study/results.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Imported source tables/protocols for 48 matched + 78 emergency SUMO runs. No rerun.')
if __name__=='__main__':main()
