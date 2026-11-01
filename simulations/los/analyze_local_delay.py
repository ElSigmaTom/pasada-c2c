"""Aggregate local passage delay with explicit censoring and seed-level records."""
import csv
import json
from pathlib import Path
import statistics

BASE = Path(__file__).resolve().parent / 'results'
SEEDS = [7100, 7101, 7102]
CASES = [f'{s}_{p}' for s in ['J1', 'J2', 'J3', 'CORRIDOR'] for p in ['AM', 'PM']]

def band(seconds):
    if seconds is None:
        return 'Not estimated'
    for limit, grade in [(10, 'A'), (20, 'B'), (35, 'C'), (55, 'D'), (80, 'E')]:
        if seconds <= limit:
            return grade
    return 'F'

def write_csv(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

def main():
    runs = []
    for seed in SEEDS:
        for case in CASES:
            for mode in ['fixed', 'rule']:
                folder = BASE / f'runs/seed{seed}/{case}/{mode}'
                audit = json.loads((folder / 'local_audit.json').read_text())
                assert audit['valid'], audit
                passages = list(csv.DictReader((folder / 'local_passages.csv').open()))
                keys = [(x['vehicle'], x['site'], x['stage']) for x in passages]
                assert len(keys) == len(set(keys)), (folder, 'duplicate passage')
                assert all(float(x['local_time_loss_s']) >= 0 and float(x['exit_s']) >= float(x['entry_s']) for x in passages)
                selected = [x for x in passages if 600 <= float(x['exit_s']) <= 4200]
                unresolved_file = folder / 'open_local_passages.csv'
                unresolved = list(csv.DictReader(unresolved_file.open())) if unresolved_file.exists() else []
                sites = ['J1', 'J2', 'J3'] if case.startswith('CORRIDOR') else [case.split('_')[0]]
                for site in sites:
                    rows = [x for x in selected if x['site'] == site]
                    open_rows = [x for x in unresolved if x['site'] == site]
                    delay = statistics.mean(float(x['local_time_loss_s']) for x in rows) if rows else None
                    for stage in range(4):
                        stage_rows = [x for x in rows if int(x['stage']) == stage]
                        stage_mean = statistics.mean(float(x['local_time_loss_s']) for x in stage_rows) if stage_rows else None
                        runs.append({'case': case, 'site': site, 'period': case.split('_')[-1], 'mode': mode,
                            'seed': seed, 'aggregation': f'stage_{stage}', 'n_cleared': len(stage_rows),
                            'mean_local_loss_s': stage_mean, 'screening_band': band(stage_mean),
                            'n_open_at_cutoff': sum(int(x['stage']) == stage for x in open_rows)})
                    runs.append({'case': case, 'site': site, 'period': case.split('_')[-1], 'mode': mode,
                        'seed': seed, 'aggregation': 'intersection', 'n_cleared': len(rows),
                        'mean_local_loss_s': delay, 'screening_band': band(delay), 'n_open_at_cutoff': len(open_rows)})
    write_csv(BASE / 'run_local_delay.csv', runs)
    summaries = []
    for layout in ['isolated', 'connected']:
        for site in ['J1', 'J2', 'J3']:
            for period in ['AM', 'PM']:
                entry = {'layout': layout, 'site': site, 'period': period}
                for mode in ['fixed', 'rule']:
                    case = f'{site if layout == "isolated" else "CORRIDOR"}_{period}'
                    selected = [x for x in runs if x['case'] == case and x['site'] == site and
                                x['mode'] == mode and x['aggregation'] == 'intersection']
                    assert len(selected) == 3 and all(x['mean_local_loss_s'] is not None for x in selected)
                    values = [x['mean_local_loss_s'] for x in selected]
                    entry[mode + '_mean_s'] = statistics.mean(values)
                    entry[mode + '_sd_s'] = statistics.stdev(values)
                    entry[mode + '_band'] = band(statistics.mean(values))
                    entry[mode + '_mean_cleared'] = statistics.mean(x['n_cleared'] for x in selected)
                    entry[mode + '_mean_open'] = statistics.mean(x['n_open_at_cutoff'] for x in selected)
                    entry[mode + '_seed_bands'] = '/'.join(x['screening_band'] for x in selected)
                entry['mean_difference_s'] = entry['fixed_mean_s'] - entry['rule_mean_s']
                summaries.append(entry)
    write_csv(BASE / 'table10A_local_delay.csv', summaries)
    (BASE / 'summary.json').write_text(json.dumps({'run_records': runs, 'table10A': summaries,
        'accepted_runs': 48, 'classification': 'bounded local time-loss screening; simulation-based LOS estimate'}, indent=2))
    for row in summaries:
        print(f"{row['layout']:9} {row['site']} {row['period']}: "
              f"{row['fixed_mean_s']:.1f} +/- {row['fixed_sd_s']:.1f} {row['fixed_band']} -> "
              f"{row['rule_mean_s']:.1f} +/- {row['rule_sd_s']:.1f} {row['rule_band']}")

if __name__ == '__main__':
    main()
