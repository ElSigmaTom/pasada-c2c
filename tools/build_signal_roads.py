#!/usr/bin/env python3
"""Sanitize a signal-centered Overpass response for reproducible offline analysis."""
import argparse
import json
from pathlib import Path
from build_road_network import KEEP, MOTOR

QUERY='[out:json][timeout:35];node["highway"="traffic_signals"](around:10500,10.32765,123.94465)->.s;way(around.s:200)["highway"]->.w;(.s;.w;>;);out body;'
KEEP=KEEP|{'crossing','crossing:signals','traffic_signals:direction','direction'}

def build(path):
    data=json.loads(path.read_text())
    if data.get('remark'):
        raise ValueError('Incomplete source response: '+data['remark'])
    nodes={str(e['id']): e for e in data['elements'] if e['type']=='node'}
    ways=[]
    for e in data['elements']:
        if e['type']!='way':
            continue
        t=e.get('tags',{})
        if t.get('highway') not in MOTOR or t.get('access') in ('private','no') or t.get('motor_vehicle') in ('private','no'):
            continue
        ids=[str(n) for n in e['nodes']]
        if not all(n in nodes for n in ids):
            raise ValueError('Incomplete way geometry.')
        ways.append({'id':str(e['id']),'nodes':ids,'tags':{k:v for k,v in t.items() if k in KEEP}})
    used={n for w in ways for n in w['nodes']}
    clean=[{'id':nid,'point':[e['lat'],e['lon']],'tags':{k:v for k,v in e.get('tags',{}).items() if k in KEEP}} for nid,e in nodes.items() if nid in used]
    return {'source':{'provider':'OpenStreetMap contributors','license':'ODbL 1.0','retrieved':'2026-10-31','osm_base':data.get('osm3s',{}).get('timestamp_osm_base'),
                      'url':'https://overpass-api.de/api/interpreter','query':QUERY,'center':[10.32765,123.94465],'max_radius_m':10000,
                      'coverage':{'type':'signal-centered road neighborhoods','signal_query_radius_m':10500,'road_buffer_m':200},
                      'coordinates':'EPSG:4326; [latitude, longitude]','purpose':'Signalized-intersection installation planning; not an authority inventory or jurisdiction boundary'},
            'nodes':clean,'ways':ways}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();d=build(a.input);a.output.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
    print(json.dumps({'nodes':len(d['nodes']),'ways':len(d['ways'])}))
