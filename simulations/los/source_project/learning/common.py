from pathlib import Path
import os,sys,csv,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
# Installed SUMO tools are authoritative. This also supports the pip distribution.
if os.environ.get('SUMO_HOME'):
 sys.path.insert(0,str(Path(os.environ['SUMO_HOME'])/'tools'))
try:import sumolib,traci
except ImportError:
 try:
  import sumo
  sys.path.insert(0,str(Path(sumo.__file__).parent/'tools'));import sumolib,traci
 except ImportError:raise RuntimeError('Install requirements.txt or set SUMO_HOME to your SUMO installation.')
sys.path.insert(0,str(ROOT/'scripts'))
from run_simulations import find_binary
SITES=['J1','J2','J3'];CASES=[f'{s}_{p}' for s in SITES+['CORRIDOR'] for p in ['AM','PM']]
def write_json(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix(path.suffix+'.writing');temp.write_text(json.dumps(value,indent=2));temp.replace(path)
def write_xml(path,root):
 ET.indent(root);ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
def write_csv(path,rows):
 if not rows:return
 with Path(path).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def stage_plans(site,period):
 rows=[r for r in csv.DictReader((ROOT/'audit/reference_signal_stages.csv').open()) if r['site']==site and r['period']==period]
 result=[]
 for stage in range(4):
  r=[x for x in rows if int(x['stage'])==stage]
  result.append({x['kind']:x['state'] for x in r}|{'duration':float(next(x['duration_s'] for x in r if x['kind']=='green')),'approach_edge':r[0]['approach_edge']})
 return result

def model_fingerprint(site):
 import hashlib
 c=json.loads((ROOT/'model/sensors/catalog.json').read_text())[site]
 features=json.loads((ROOT/'model/sensors/feature_contract.json').read_text())
 body={'sensors':c,'ordered_features':features['ordered_features'],'formulas':features['formulas'],'AM':stage_plans(site,'AM'),'PM':stage_plans(site,'PM'),
       'local_network_sha256':hashlib.sha256(ET.tostring(ET.parse(ROOT/f'network/isolated_{site}.net.xml').getroot())).hexdigest(),
       'corridor_network_sha256':hashlib.sha256(ET.tostring(ET.parse(ROOT/'network/mandaue.net.xml').getroot())).hexdigest()}
 return hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()
