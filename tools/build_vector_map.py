#!/usr/bin/env python3
"""Build the clean C2C context layer from a local, attributed OSM snapshot.

Source data is geographic, never inferred from a screenshot. This prepares map
geometry only; it does not convert the network to SUMO or run a simulation.
"""
import argparse
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET


def build(source):
    root = ET.parse(source).getroot()
    nodes = {n.get('id'): [round(float(n.get('lat')), 7), round(float(n.get('lon')), 7)]
             for n in root.findall('node')}
    ways = {w.get('id'): w for w in root.findall('way')}
    tags = lambda e: {t.get('k'): t.get('v') for t in e.findall('tag')}
    points = lambda w: [nodes[n.get('ref')] for n in w.findall('nd') if n.get('ref') in nodes]
    buildings, land, roads, places = [], [], [], []
    used = set()

    def land_kind(t):
        if t.get('natural') == 'water' or t.get('waterway') in ('riverbank', 'dock'):
            return 'water'
        if t.get('landuse') in ('grass', 'forest', 'recreation_ground', 'meadow', 'cemetery') or t.get('leisure') in ('park', 'garden', 'pitch') or t.get('natural') in ('wood', 'grassland', 'scrub'):
            return 'green'
        return None

    def stitch(refs):
        pieces = [points(ways[r]) for r in refs if r in ways]
        rings = []
        while pieces:
            ring = pieces.pop(0)
            while ring and ring[0] != ring[-1]:
                for i, part in enumerate(pieces):
                    if part and part[0] == ring[-1]:
                        ring += part[1:]; pieces.pop(i); break
                    if part and part[-1] == ring[-1]:
                        ring += list(reversed(part))[1:]; pieces.pop(i); break
                else:
                    break
            if len(ring) >= 4 and ring[0] == ring[-1]:
                rings.append(ring)
        return rings

    def contained(point, ring):
        y, x = point
        inside = False
        for (y1, x1), (y2, x2) in zip(ring, ring[1:]):
            if (y1 > y) != (y2 > y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1:
                inside = not inside
        return inside

    # Retain courtyard holes instead of filling them as solid roofs.
    for relation in root.findall('relation'):
        t = tags(relation)
        kind = 'building' if t.get('building') not in (None, 'no') else land_kind(t)
        if t.get('type') != 'multipolygon' or not kind:
            continue
        members = [m for m in relation.findall('member') if m.get('type') == 'way']
        outers = stitch([m.get('ref') for m in members if m.get('role', '') in ('outer', '')])
        inners = stitch([m.get('ref') for m in members if m.get('role') == 'inner'])
        for outer in outers:
            rings = [outer] + [inner for inner in inners if contained(inner[0], outer)]
            (buildings if kind == 'building' else land).append({'id': 'r'+relation.get('id'), 'rings': rings, 'kind': kind})
        if outers:
            used.update(m.get('ref') for m in members)

    for wid, way in ways.items():
        t, ps = tags(way), points(way)
        if len(ps) < 2:
            continue
        closed = len(ps) >= 4 and ps[0] == ps[-1]
        building = t.get('building') not in (None, 'no')
        kind = land_kind(t)
        if closed and wid not in used and (building or kind):
            (buildings if building else land).append({'id':'w'+wid, 'rings':[ps], 'kind':'building' if building else kind})
        hw = t.get('highway')
        if hw and hw not in ('proposed', 'construction', 'platform'):
            walk = hw in ('footway', 'path', 'pedestrian', 'steps', 'cycleway')
            default = 1.6 if walk else {'motorway':10.5,'trunk':10,'primary':9,'secondary':7,'tertiary':6,'residential':5.5,'service':3.5}.get(hw, 5.5)
            explicit = re.match(r'^([\d.]+)\s*(?:m)?$', t.get('width', ''))
            lane_count = re.match(r'^([1-9]\d?)$', t.get('lanes', ''))
            width = float(explicit[1]) if explicit else float(lane_count[1])*3 if lane_count else default
            roads.append({'id':wid, 'path':ps, 'width_m':round(max(1,min(width,24)),1), 'kind':'walk' if walk else 'road', 'name':t.get('name',''), 'width_source':'OSM width' if explicit else 'OSM lanes × 3 m' if lane_count else 'planning assumption'})
        if t.get('name') and (building or any(k in t for k in ('amenity','shop','tourism','office','leisure'))):
            body = ps[:-1] if closed else ps
            places.append({'name':t['name'], 'point':[round(sum(p[0] for p in body)/len(body),7),round(sum(p[1] for p in body)/len(body),7)]})
    # Prefer named footprint labels to duplicate point-of-interest labels.
    for node in root.findall('node'):
        t=tags(node)
        if t.get('name') and any(k in t for k in ('amenity','shop','tourism','office')):
            places.append({'name':t['name'],'point':nodes[node.get('id')]})
    seen=set()
    places=[p for p in places if not (p['name'] in seen or seen.add(p['name']))]
    return {'source':{'provider':'OpenStreetMap contributors','license':'ODbL 1.0','retrieved':'2026-10-29','bbox':[123.937,10.32,123.9535,10.3355],'url':'https://api.openstreetmap.org/api/0.6/map?bbox=123.9370,10.3200,123.9535,10.3355','reference':'Fuente export_web_replay.py: footprint / land / road geometry approach','geometry':'EPSG:4326; [latitude, longitude]','scope':'Geographic context and planning lane surfaces; not a SUMO execution or surveyed road inventory'},'buildings':buildings,'land':land,'roads':roads,'places':places}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--osm', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    data=build(args.osm)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text('// Geographic context © OpenStreetMap contributors, ODbL.\nexport const MAP_DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
    print(json.dumps({k:len(data[k]) for k in ('buildings','land','roads','places')}))
