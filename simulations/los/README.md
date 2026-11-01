# PASADA local-delay and LOS-estimate supplement

1 November 2026. This package adds 48 passive measurement reruns of the accepted fixed-versus-local-rule experiment. It does not train or tune the controller. The original route, fleet, signal and demand inputs remain unchanged.

## Interpretation

The reported quantity is cumulative vehicle timeLoss gained within a route-specific junction area. Entry is requested up to 200 m of normal approach-road edges before the signal, stopping at the network origin or a preceding signal. Exit is up to 50 m on the immediate outgoing edge, clipped by the available edge or actual route end. Vehicles born inside an area start at insertion with zero accumulated loss, avoiding silent omission. Sub-step boundary crossings are interpolated where consecutive samples are on the same edge. Exact boundaries are in each run folder.

Means cover local passages clearing the measurement area from 600 to 4200 s, including warmup vehicles still present. Each run weights individual passages, equivalently weighting approach means by cleared count. Mean and sample SD then summarize three seeds. The LOS estimate applies the HCM signalized delay thresholds to this bounded local time-loss proxy. It is not a formal field-calibrated HCM capacity analysis. Queues outside the area, non-signal interactions, clipped acceleration and incomplete passages limit interpretation. Not-inserted demand is excluded from the local estimate and remains in the original all-demand ledger. Open local passages and their accrued loss are retained separately.

All cases remain in estimated band F. A lower delay does not imply a better letter grade. Connected J3 PM is unfavorable for PASADA and remains included.

| Layout | Site | Peak | Fixed mean ± SD (s) | Local mean ± SD (s) | Estimated band |
|---|---|---|---:|---:|---|
| isolated | J1 | AM | 335.4 ± 1.7 | 323.4 ± 10.6 | F → F |
| isolated | J1 | PM | 291.0 ± 0.5 | 272.3 ± 14.3 | F → F |
| isolated | J2 | AM | 310.2 ± 2.4 | 299.6 ± 8.3 | F → F |
| isolated | J2 | PM | 414.2 ± 3.1 | 331.3 ± 8.4 | F → F |
| isolated | J3 | AM | 313.8 ± 9.0 | 284.8 ± 8.2 | F → F |
| isolated | J3 | PM | 376.0 ± 5.0 | 331.0 ± 25.1 | F → F |
| connected | J1 | AM | 295.9 ± 0.2 | 264.2 ± 2.0 | F → F |
| connected | J1 | PM | 255.2 ± 0.7 | 217.1 ± 3.7 | F → F |
| connected | J2 | AM | 215.2 ± 1.0 | 180.5 ± 3.9 | F → F |
| connected | J2 | PM | 233.9 ± 4.9 | 176.4 ± 5.9 | F → F |
| connected | J3 | AM | 332.5 ± 3.3 | 322.2 ± 7.9 | F → F |
| connected | J3 | PM | 296.9 ± 5.9 | 322.8 ± 13.4 | F → F |

## Audit and contents

- `results/table10A_local_delay.csv`, `summary.json`, `run_local_delay.csv`: manuscript values and per-seed/per-stage records.
- `results/runs/seed*/CASE/CONTROL/local_passages.csv`: vehicle-level cleared passages, with entry, exit and local loss.
- `open_local_passages.csv`: unfinished local passages with accrued loss at cutoff.
- `measurement_boundaries.json`: route-specific observation boundaries.
- `native_reproduction_audit.json`: all 48 native trip-record sets, supervisor events and observer traces match the original accepted archive.
- `protocol.json`, `audit.json`: method, boundaries, seeds and per-run acceptance.
- Native `tripinfo.xml.gz`, `summary.xml.gz` and `collisions.xml.gz` are compressed mirrors; their raw byte fingerprints are in `native_outputs.json`. One compressed mirror was restored from the exact manifest-matching native bytes; `mirror_repair_log.json` records that recovery.
- `source_project/`: frozen simulation inputs and runner dependencies. Its missing `audit/reference_signal_stages.csv` dependency was recovered from `LEAR_SUMO_Simulations_GitHub_Ready.zip`; the SHA-256 is in the protocol. Original baseline measurement JSON records support the wrapper's reproduction checks.

## Reproduce

Use Python 3.12 and SUMO 1.28.0 on a supported system. From this folder:

```sh
python -m pip install -r requirements.txt
python analyze_local_delay.py
```

The supplied results are already complete. To execute the simulations again, first preserve `results/runs/` under a different name. Keep `source_project/results/paired_nov01/`, which supplies the original comparison measurements. Then run:

```sh
python measure_trajectory_delay.py --all --jobs 4
python analyze_local_delay.py
```

A selected case can use `--case J3_AM --mode rule --seed 7100`. All eight case names, both controls and three seeds are fixed in the protocol. A valid saved audit is resumed; an invalid output folder must be preserved and moved before rerunning. No failed policy outcome is discarded. The earlier E3 diagnostics are not the accepted measurement method.

## Sources and attribution

Original accepted archive: PASADA_Matched_SUMO_Comparison.zip; exact SHA-256 in `results/protocol.json`. The base network is an OpenStreetMap reconstruction; retain the source project's OSM attribution. Manual class/site totals are the project team's counts; routes, timing detail, motorcycle behavior and within-hour arrivals retain the original reconstruction limits. No physical radio, sensor, cabinet or field LOS performance is established.

Eclipse SUMO. (n.d.). Vehicle value retrieval. https://sumo.dlr.de/docs/TraCI/Vehicle_Value_Retrieval.html
Federal Highway Administration. (2008). Traffic signal timing manual. https://ops.fhwa.dot.gov/publications/fhwahop08024/chapter3.htm
