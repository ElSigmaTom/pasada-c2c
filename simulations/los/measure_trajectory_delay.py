"""Track bounded junction time loss, including vehicles born inside the region.

Observations only: import the frozen paired runner; never modify its routes,
vehicle types, controller or RNG. A separate output directory holds the rerun.
"""
import argparse
import concurrent.futures
import csv
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
ROOT = BASE / 'source_project'
OUT = BASE / 'results/runs'
sys.path[:0] = [str(BASE / 'runtime'), str(ROOT / 'measurement'), str(ROOT / 'learning')]
import libsumo
import sumolib
import traci.constants as C
import paired_study as study
from common import stage_plans

VARIABLES = [C.VAR_ROAD_ID, C.VAR_ROUTE_INDEX, C.VAR_LANEPOSITION, C.VAR_TIMELOSS]

def save_csv(path, rows):
    if not rows:
        return
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def run(case, mode, seed):
    study.OUT = OUT
    folder = OUT / f'seed{seed}' / case / mode
    folder.mkdir(parents=True, exist_ok=True)
    existing = folder / 'local_audit.json'
    if existing.exists():
        saved = json.loads(existing.read_text())
        if saved.get('valid'):
            print(json.dumps(saved), flush=True)
            return saved
        raise RuntimeError('Preserve the invalid output folder, then rerun into a fresh folder.')
    source = ROOT / f'scenarios/{case}.sumocfg'
    cfg = ET.parse(source).getroot()
    net = sumolib.net.readNet(str((source.parent / cfg.find('input/net-file').get('value')).resolve()))
    route = ET.parse((source.parent / cfg.find('input/route-files').get('value')).resolve()).getroot()
    routes = {r.get('id'): r.get('edges').split() for r in route.findall('route')}
    vehicles = {v.get('id'): v.get('route') for v in route.findall('vehicle')}
    sites = ['J1', 'J2', 'J3'] if case.startswith('CORRIDOR') else [case.split('_')[0]]
    targets = {s['approach_edge']: (sid, i) for sid in sites
               for i, s in enumerate(stage_plans(sid, case.split('_')[-1]))}
    windows = {}
    boundaries = []
    for rid, edges in routes.items():
        result = []
        for j, edge in enumerate(edges[:-1]):
            if edge not in targets:
                continue
            sid, stage = targets[edge]
            remaining = 200.
            k = j
            while k > 0 and remaining > net.getEdge(edges[k]).getLength():
                remaining -= net.getEdge(edges[k]).getLength()
                previous = net.getEdge(edges[k - 1])
                if previous.getToNode().getType().startswith('traffic_light'):
                    remaining = 0.
                    break
                k -= 1
            pos = max(0., net.getEdge(edges[k]).getLength() - remaining) if remaining else 0.
            finish = min(50., net.getEdge(edges[j + 1]).getLength() - .01)
            w = {'site': sid, 'stage': stage, 'incoming': edge,
                 'entry_index': k, 'entry_edge': edges[k], 'entry_pos_m': pos,
                 'exit_index': j + 1, 'exit_edge': edges[j + 1], 'exit_pos_m': finish}
            result.append(w)
            boundaries.append({'route': rid, **w})
        windows[rid] = result
    (folder / 'measurement_boundaries.json').write_text(json.dumps(boundaries, indent=2))
    native_step = libsumo.simulationStep
    previous = {}
    tracking = {}
    completed = []
    pending_arrivals = []

    def progress_passed(state, index, position):
        ri = int(state[C.VAR_ROUTE_INDEX])
        return ri > index or (ri == index and
               (state[C.VAR_ROAD_ID].startswith(':') or float(state[C.VAR_LANEPOSITION]) >= position))

    def at_boundary(old, now, index, position, current_time):
        current_loss = float(now[C.VAR_TIMELOSS])
        if old and old[C.VAR_ROUTE_INDEX] == now[C.VAR_ROUTE_INDEX] == index and not now[C.VAR_ROAD_ID].startswith(':'):
            a = float(old[C.VAR_LANEPOSITION]); b = float(now[C.VAR_LANEPOSITION])
            f = min(1., max(0., (position - a) / (b - a))) if b > a else 1.
            return float(old[C.VAR_TIMELOSS]) + f * (current_loss - float(old[C.VAR_TIMELOSS])), current_time - .5 + .5 * f
        return current_loss, current_time

    def observed_step(*args, **kwargs):
        value = native_step(*args, **kwargs)
        now = float(libsumo.simulation.getTime())
        for vid in libsumo.simulation.getDepartedIDList():
            libsumo.vehicle.subscribe(vid, VARIABLES)
            tracking[vid] = [dict(w, entry_loss=None, entry_time=None, done=False)
                             for w in windows[vehicles[vid]]]
        states = libsumo.vehicle.getAllSubscriptionResults()
        for vid, current in states.items():
            prior = previous.get(vid)
            for w in tracking.get(vid, []):
                if w['done']:
                    continue
                if w['entry_loss'] is None and progress_passed(current, w['entry_index'], w['entry_pos_m']):
                    if prior is None and w['entry_index'] == 0:
                        loss, time = 0., now
                    else:
                        loss, time = at_boundary(prior, current, w['entry_index'], w['entry_pos_m'], now)
                    w['entry_loss'] = loss; w['entry_time'] = time
                if w['entry_loss'] is not None and progress_passed(current, w['exit_index'], w['exit_pos_m']):
                    # On an internal lane after the incoming approach, routeIndex
                    # may still refer to the incoming edge; the route index test
                    # above therefore does not prematurely finish that crossing.
                    loss, time = at_boundary(prior, current, w['exit_index'], w['exit_pos_m'], now)
                    completed.append({'vehicle': vid, 'site': w['site'], 'stage': w['stage'],
                        'entry_s': w['entry_time'], 'exit_s': time,
                        'local_time_loss_s': max(0., loss - w['entry_loss']), 'exit_kind': 'boundary'})
                    w['done'] = True
            previous[vid] = current
        for vid in libsumo.simulation.getArrivedIDList():
            for w in tracking.get(vid, []):
                if not w['done'] and w['entry_loss'] is not None:
                    pending_arrivals.append((vid, w))
                    w['done'] = True
            previous.pop(vid, None)
        return value

    libsumo.simulationStep = observed_step
    record = study.run(case, mode, seed)
    trips = {x.get('id'): x.attrib for x in ET.parse(folder / 'tripinfo.xml').getroot().findall('tripinfo')}
    for vid, w in pending_arrivals:
        trip = trips[vid]
        completed.append({'vehicle': vid, 'site': w['site'], 'stage': w['stage'],
            'entry_s': w['entry_time'], 'exit_s': float(trip['arrival']),
            'local_time_loss_s': max(0., float(trip['timeLoss']) - w['entry_loss']), 'exit_kind': 'route_end'})
    active = []
    for vid, stages in tracking.items():
        for w in stages:
            if not w['done'] and w['entry_loss'] is not None:
                active.append({'vehicle': vid, 'site': w['site'], 'stage': w['stage'],
                    'entry_s': w['entry_time'], 'cutoff_s': 4200.,
                    'accrued_local_time_loss_s': max(0., float(previous[vid][C.VAR_TIMELOSS]) - w['entry_loss'])})
    seen = {(v['vehicle'], v['site'], v['stage']) for v in completed}
    missed = []
    for vid, trip in trips.items():
        if float(trip.get('arrival', -1)) < 0:
            continue
        for w in windows[vehicles[vid]]:
            if (vid, w['site'], w['stage']) not in seen:
                missed.append([vid, w['site'], w['stage']])
    old = json.loads((ROOT / f'results/paired_nov01/seed{seed}/{case}/{mode}/measurement.json').read_text())
    checks = ['study_cohort_completed', 'study_cohort_active', 'study_cohort_uninserted',
              'study_mean_accumulated_s', 'study_completed_mean_duration_s',
              'study_completed_mean_wait_s', 'collision_events', 'teleports']
    differences = {k: {'original': old[k], 'supplement': record[k]} for k in checks
                   if abs(old[k] - record[k]) > 1e-7}
    audit = {'case': case, 'mode': mode, 'seed': seed, 'original_metric_differences': differences,
             'missing_completed_trip_measurements': missed, 'n_local_passages': len(completed),
             'n_open_local_passages': len(active), 'valid': not differences and not missed}
    save_csv(folder / 'local_passages.csv', completed)
    save_csv(folder / 'open_local_passages.csv', active)
    (folder / 'local_audit.json').write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit), flush=True)
    return audit

def worker(task):
    case, mode, seed = task
    folder = OUT / f'seed{seed}' / case / mode
    folder.mkdir(parents=True, exist_ok=True)
    p = subprocess.run([sys.executable, __file__, '--case', case, '--mode', mode,
                        '--seed', str(seed)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (folder / 'supplement_execution.log').write_text(p.stdout)
    if p.returncode:
        raise RuntimeError(f'{task}: {p.stdout[-2200:]}')
    audit = json.loads((folder / 'local_audit.json').read_text())
    print(json.dumps({k: v for k, v in audit.items() if k != 'missing_completed_trip_measurements'}), flush=True)
    return audit

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=study.CASES)
    parser.add_argument('--mode', choices=['fixed', 'rule'])
    parser.add_argument('--seed', type=int, default=7100)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if args.all:
        tasks = [(c, m, s) for s in study.SEEDS for c in study.CASES for m in ['fixed', 'rule']]
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            audit = list(pool.map(worker, tasks))
        (OUT.parent / 'audit.json').write_text(json.dumps(audit, indent=2))
    else:
        run(args.case, args.mode, args.seed)
