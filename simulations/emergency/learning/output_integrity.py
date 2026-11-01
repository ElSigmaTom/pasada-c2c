"""Keep byte-checked compressed mirrors of native SUMO XML outputs."""
import gzip,hashlib,json,os,shutil,xml.etree.ElementTree as ET
from pathlib import Path

NAMES=['tripinfo.xml','summary.xml','collisions.xml']
def native_bytes(folder,name):
 folder=Path(folder);record=json.loads((folder/'native_outputs.json').read_text())[name]
 raw=gzip.decompress((folder/record['mirror']).read_bytes())
 assert len(raw)==record['bytes'] and hashlib.sha256(raw).hexdigest()==record['sha256']
 ET.fromstring(raw)
 return raw

def mirror_native_outputs(folder):
 folder=Path(folder);records={}
 for name in NAMES:
  source=folder/name;ET.parse(source)
  raw=source.read_bytes();target=folder/(name+'.gz')
  with target.open('wb') as out:
   with gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0) as compressed:compressed.write(raw)
   out.flush();os.fsync(out.fileno())
  assert gzip.decompress(target.read_bytes())==raw
  records[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'mirror':target.name}
 (folder/'native_outputs.json').write_text(json.dumps(records,indent=2))
 return records
