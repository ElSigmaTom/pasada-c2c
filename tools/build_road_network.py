#!/usr/bin/env python3
"""Retain road topology and lane tags from an OSM XML map extract (no account metadata)."""
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

KEEP = {'highway', 'name', 'ref', 'oneway', 'junction', 'lanes', 'lanes:forward',
        'lanes:backward', 'lanes:both_ways', 'width', 'access', 'motor_vehicle',
        'bridge', 'tunnel', 'layer', 'service', 'traffic_signals', 'turn:lanes',
        'turn:lanes:forward', 'turn:lanes:backward'}
MOTOR = {'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential',
         'living_street', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link'}

def build(source):
    root = ET.parse(source).getroot()
    tags = lambda el: {t.get('k'): t.get('v') for t in el.findall('tag') if t.get('k') in KEEP}
    ways = []
    for w in root.findall('way'):
        t = tags(w)
        if t.get('highway') not in MOTOR or t.get('access') in ('private', 'no') or t.get('motor_vehicle') in ('private', 'no'):
            continue
        ways.append({'id': w.get('id'), 'nodes': [n.get('ref') for n in w.findall('nd')], 'tags': t})
    used = {n for w in ways for n in w['nodes']}
    nodes = [{'id': n.get('id'), 'point': [float(n.get('lat')), float(n.get('lon'))], 'tags': tags(n)}
             for n in root.findall('node') if n.get('id') in used]
    bounds = root.find('bounds')
    return {'source': {'provider': 'OpenStreetMap contributors', 'license': 'ODbL 1.0',
                       'retrieved': '2026-10-31', 'url': 'https://api.openstreetmap.org/api/0.6/map?bbox=123.9230,10.3060,123.9663,10.3493',
                       'bbox': [float(bounds.get(k)) for k in ('minlon', 'minlat', 'maxlon', 'maxlat')],
                       'center': [10.32765, 123.94465], 'max_radius_m': 2000,
                       'coordinates': 'EPSG:4326; [latitude, longitude]', 'purpose': 'Installation planning; no jurisdiction or surveyed lane accuracy asserted'},
            'nodes': nodes, 'ways': ways}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--osm', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    data = build(a.osm)
    a.output.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    a.output.with_suffix('.js').write_text('// Road topology © OpenStreetMap contributors, ODbL 1.0.\nexport const ROAD_NETWORK = '+json.dumps(data, ensure_ascii=False, separators=(',', ':'))+';\n')
    print(json.dumps({'nodes':len(data['nodes']), 'roads':len(data['ways'])}))
