#!/usr/bin/env python3
"""Check local HTML/module/CSS links as a GitHub Pages project site under /pasada-c2c/."""
from pathlib import Path
import re,sys
from urllib.parse import urljoin,urlparse,unquote
ROOT=Path(__file__).resolve().parents[1]/'dist'
BASE='https://example.github.io/pasada-c2c/'
failures=[];checked=0
for source in ROOT.rglob('*'):
    if not source.is_file() or source.suffix not in ('.html','.js','.css') or 'vendor' in source.parts:continue
    text=source.read_text()
    if source.suffix=='.html':refs=re.findall(r'(?:href|src)=["\']([^"\']+)',text)
    elif source.suffix=='.js':refs=re.findall(r'(?:\bfrom\s+|\bimport\s*\(|\bfetch\s*\()\s*["\']([^"\']+)',text)+re.findall(r'(?:href|src)=["\']([^"\']+)',text)
    else:refs=re.findall(r'url\(["\']?([^\s)"\']+)',text)
    for ref in refs:
        if ref.startswith(('#','data:','mailto:','javascript:')) or '${' in ref or '<' in ref:continue
        target=urlparse(urljoin(BASE+source.relative_to(ROOT).as_posix(),ref))
        if target.netloc!='example.github.io':continue
        if not target.path.startswith('/pasada-c2c/'):
            failures.append(f'{source.relative_to(ROOT)}: escapes project prefix: {ref}');continue
        relative=unquote(target.path[len('/pasada-c2c/'):]);p=ROOT/relative
        if target.path.endswith('/'):p=p/'index.html'
        if not p.is_file():failures.append(f'{source.relative_to(ROOT)}: missing {ref}')
        checked+=1
if failures:print('\n'.join(failures));sys.exit(1)
print(f'{checked} local HTML/module/CSS references resolve under /pasada-c2c/.')
