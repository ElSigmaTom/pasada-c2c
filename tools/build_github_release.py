#!/usr/bin/env python3
"""Export a GitHub-ready source tree without Sites identity, Git metadata or runtime state."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
destination=ROOT/'dist/downloads/PASADA_GitHub_Pages.zip'
roots=['.github','dist','docs','examples','firmware','models','tests','tools','data']
files=[ROOT/n for n in ['README.md','GITHUB_PAGES.md','package.json']]
for name in roots:
    for path in sorted((ROOT/name).rglob('*')):
        relative=path.relative_to(ROOT)
        if not path.is_file() or path.is_symlink() or '__pycache__' in relative.parts or path.suffix=='.pyc' or path==destination or path==ROOT/'dist/downloads/PASADA_Chain_Draft_v0.1.zip':continue
        files.append(path)
destination.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(destination) as z:
    names=z.namelist()
    assert '.github/workflows/pages.yml' in names and 'dist/index.html' in names and 'GITHUB_PAGES.md' in names
    assert not any(n.startswith(('.git/','.openai/')) or n=='.env' for n in names)
    assert 'dist/downloads/PASADA_GitHub_Pages.zip' not in names
print(f'GitHub-ready package: {len(files)} files, {destination.stat().st_size:,} bytes. Extract contents at repository root.')
