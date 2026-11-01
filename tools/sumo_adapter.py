#!/usr/bin/env python3
"""Observe an existing SUMO study and export PASADA replay JSON. No signal writes."""
import argparse
import json
import os
from pathlib import Path
import sys

DIRECTIONS = ('N', 'E', 'S', 'W')

def validate_mapping(project, mapping):
    sites = {j['id'] for j in project['intersections']}
    entries = mapping.get('intersections', [])
    if {j.get('project_intersection_id') for j in entries} != sites or len(entries) != len(sites):
        raise ValueError('Mapping must cover every project intersection exactly once.')
    for entry in entries:
        if not entry.get('sumo_tls_id') or 'REPLACE' in entry['sumo_tls_id']:
            raise ValueError('Replace all SUMO TLS placeholders with actual IDs.')
        lanes = entry.get('approach_lanes', {})
        if set(lanes) != set(DIRECTIONS) or not all(isinstance(lanes[d], list) for d in DIRECTIONS):
            raise ValueError('Provide N/E/S/W approach lane lists. Use [] for absent approaches.')
        flat = [lane for d in DIRECTIONS for lane in lanes[d]]
        if not flat or len(flat) != len(set(flat)) or any(not isinstance(x, str) for x in flat):
            raise ValueError('Approach lane lists require unique actual lane IDs.')
        if set(entry.get('exit_lanes', {})) - set(DIRECTIONS):
            raise ValueError('Exit lane keys must be N/E/S/W.')
    return entries

def load_traci():
    home = os.environ.get('SUMO_HOME')
    if home:
        sys.path.append(str(Path(home) / 'tools'))
    try:
        import traci
        return traci
    except ImportError as exc:
        raise RuntimeError('SUMO/TraCI is unavailable. Install SUMO and set SUMO_HOME, or install its traci package in your own environment.') from exc

def observe(traci, project, mapping, duration, step_length=1):
    entries = validate_mapping(project, mapping)
    tls_ids, lane_ids = set(traci.trafficlight.getIDList()), set(traci.lane.getIDList())
    for entry in entries:
        if entry['sumo_tls_id'] not in tls_ids:
            raise ValueError(f"Unknown SUMO TLS: {entry['sumo_tls_id']}")
        all_lanes = [x for v in entry['approach_lanes'].values() for x in v]
        all_lanes += [x for v in entry.get('exit_lanes', {}).values() for x in v]
        missing = set(all_lanes) - lane_ids
        if missing:
            raise ValueError(f'Unknown mapped lanes: {sorted(missing)}')
    frames, events = [], []
    previous_exit = {j['project_intersection_id']: set() for j in entries}
    departures = {j['project_intersection_id']: 0 for j in entries}
    previous_phase = {}
    for _ in range(int(duration / step_length)):
        traci.simulationStep()
        t = float(traci.simulation.getTime())
        sites = []
        for entry in entries:
            jid, tls = entry['project_intersection_id'], entry['sumo_tls_id']
            phase_index = traci.trafficlight.getPhase(tls)
            signal = traci.trafficlight.getRedYellowGreenState(tls)
            label = entry.get('phase_labels', {}).get(str(phase_index), f'SUMO_PHASE_{phase_index}')
            queues = {d: sum(traci.lane.getLastStepHaltingNumber(lane) for lane in entry['approach_lanes'][d]) for d in DIRECTIONS}
            exits = entry.get('exit_lanes', {})
            downstream = {d: sum(traci.lane.getLastStepVehicleNumber(lane) for lane in exits.get(d, [])) for d in DIRECTIONS}
            current_exit = {v for lanes in exits.values() for lane in lanes for v in traci.lane.getLastStepVehicleIDs(lane)}
            # First-frame occupancy is a baseline, not a measured exit passage.
            if frames:
                departures[jid] += len(current_exit - previous_exit[jid])
            previous_exit[jid] = current_exit
            sites.append({'id': jid, 'phase': label, 'signal_state': signal,
                          'mode': 'SUMO_OBSERVED', 'queues': queues, 'downstream': downstream,
                          'arrived': None, 'departed': departures[jid] if exits else None,
                          'ped_wait_s': None, 'device_health': {}})
            if previous_phase.get(jid) != phase_index:
                events.append({'schema': 'pasada.event/0.1.0', 'sequence': len(events)+1,
                               't': t, 'source': 'sumo', 'intersection_id': jid,
                               'kind': 'SUMO_PHASE_OBSERVED', 'severity': 'info',
                               'message': f'SUMO phase {phase_index}; signal state {signal}. Observer made no timing change.'})
            previous_phase[jid] = phase_index
        frames.append({'t': t, 'intersections': sites, 'events': []})
    supplied = mapping.get('provenance', {})
    return {'schema': 'pasada.replay/0.1.0', 'project': project,
            'provenance': {'source': 'sumo', 'calibrated': supplied.get('calibrated', False),
                           'calibration_declaration': 'Copied from user-supplied mapping; not verified by adapter.',
                           'description': supplied.get('description', 'Observed SUMO run. Demand and calibration status must be documented separately.'),
                           'controller': 'existing SUMO program; observer only',
                           'queue_measure': 'Lane halting count, not magnetometer-derived queue estimate.',
                           'departure_measure': 'New vehicle IDs entering mapped exit lanes after first frame.'},
            'frames': frames, 'events': events}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sumocfg', required=True, type=Path)
    p.add_argument('--mapping', required=True, type=Path)
    p.add_argument('--project', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--duration', type=int, default=300)
    p.add_argument('--sumo', default='sumo', help='SUMO or sumo-gui binary')
    p.add_argument('--seed', type=int, default=42)
    args = p.parse_args(argv)
    if not 1 <= args.duration <= 20000:
        p.error('duration must be 1–20,000 seconds')
    try:
        project = json.loads(args.project.read_text(encoding='utf-8'))
        mapping = json.loads(args.mapping.read_text(encoding='utf-8'))
        validate_mapping(project, mapping)
        traci = load_traci()
        traci.start([args.sumo, '-c', str(args.sumocfg.resolve()), '--seed', str(args.seed), '--step-length', '1', '--no-step-log', 'true'])
        try:
            result = observe(traci, project, mapping, args.duration)
        finally:
            traci.close()
        result['provenance'].update({'sumocfg': args.sumocfg.name, 'seed': args.seed})
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(f'Wrote {len(result["frames"])} observed SUMO frames to {args.output}. No signal commands sent.')
    except (ValueError, OSError, RuntimeError, KeyError) as exc:
        p.exit(2, f'Error: {exc}\n')

if __name__ == '__main__':
    main()
