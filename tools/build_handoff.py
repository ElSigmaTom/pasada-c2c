#!/usr/bin/env python3
"""Package source without credentials, Git metadata, generated downloads or local runtime data."""
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
dest=ROOT/'dist'/'downloads';dest.mkdir(parents=True,exist_ok=True)
archive=dest/'PASADA_Chain_Draft_v0.1.zip'
roots=['.github','dist','docs','examples','firmware','models','tests','tools','data']
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for name in ['README.md','GITHUB_PAGES.md','package.json']:
        z.write(ROOT/name,'PASADA_Chain_Draft_v0.1/'+name)
    for name in roots:
        for p in sorted((ROOT/name).rglob('*')):
            relative=p.relative_to(ROOT)
            if p.is_file() and 'downloads' not in relative.parts and '__pycache__' not in relative.parts and p.suffix!='.pyc':
                z.write(p,'PASADA_Chain_Draft_v0.1/'+str(relative))
shutil.copy2(ROOT/'docs'/'IMPLEMENTATION_GUIDE.md',dest/'IMPLEMENTATION_GUIDE.md')
shutil.copy2(ROOT/'docs'/'LEAR_ALIGNMENT.md',dest/'LEAR_ALIGNMENT.md')
shutil.copy2(ROOT/'docs'/'CONTROLLERS_AND_BEACONS.md',dest/'CONTROLLERS_AND_BEACONS.md')
shutil.copy2(ROOT/'docs'/'DRAWINGS_REVB.md',dest/'DRAWINGS_REVB.md')
shutil.copy2(ROOT/'docs'/'RESEARCH_BASIS.md',dest/'RESEARCH_BASIS.md')
shutil.copy2(ROOT/'docs'/'DEVICE_IDENTITY.md',dest/'DEVICE_IDENTITY.md')
shutil.copy2(ROOT/'docs'/'CLEAN_GEOMETRY_VIEW.md',dest/'CLEAN_GEOMETRY_VIEW.md')
shutil.copy2(ROOT/'docs'/'C2C_AND_FLEET.md',dest/'C2C_AND_FLEET.md')
shutil.copy2(ROOT/'docs'/'AREA_INSTALLATION.md',dest/'AREA_INSTALLATION.md')
shutil.copy2(ROOT/'docs'/'PUBLIC_TRAFFIC_DATA.md',dest/'PUBLIC_TRAFFIC_DATA.md')
shutil.copy2(ROOT/'docs'/'USB_INSTALLATION.md',dest/'USB_INSTALLATION.md')
shutil.copy2(ROOT/'GITHUB_PAGES.md',dest/'GITHUB_PAGES.md')
shutil.copy2(ROOT/'docs'/'STUDY_RESULTS.md',dest/'STUDY_RESULTS.md')
print(f'Packaged {archive.name}: {archive.stat().st_size} bytes')
