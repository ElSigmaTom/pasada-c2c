**Current model update:** MODELS_REPORT.md documents the later simulation-trained checkpoints and C exports. Statements below saying no weights were included describe the preceding readiness audit. Its source-data limitations remain applicable.

# Historical calibration-readiness audit (before the trained pilot)

Updated 26 October 2026. This addendum audits the existing manually collected study data and sets out a deployable-model path. **No traffic behavior has been fitted, no new controller has been enabled, and no trained weights are included.** The 40 checked baseline runs and their inputs are unchanged.

## Can the existing manual collection do the job?

Potentially yes: new field collection is not automatically necessary. The source paper's method (PDF pp.41–44) describes video/manual counts by vehicle class and left/through/right movement. Its conclusion (p.74) reports recording movements, queue lengths, travel times and signal timings. Those original tally sheets, event records or retained videos may provide much of what we need.

The available published tables, however, contain site/hour/class totals, rather than those raw observations. The existing performance tables on pp.55–57 accompany SUMO results; the displayed queue calculation uses simulation arrivals and waiting time. They are not independent measured queue traces. A statement that data were collected does not supply the actual values needed for fitting.

| Existing information | What it supports now | What it cannot identify alone |
|---|---|---|
| 48 site/hour/class count rows, pp.53–54 | Total count constraints and class composition | Approach shares, turn shares, arrival time profile and OD |
| Representative G/Y/R summaries, pp.54–55 | Conditional cycle candidates and a signal-consistency check | Complete movement-specific phase programs or offsets |
| SUMO performance/derived queues, pp.55–57 | Context or source-model reproduction after recovering its files | Independent calibration of field queues or motorcycle discharge |
| Manual/video observation described, pp.41–44 and 74 | A concrete recovery route for richer data | Values until original sheets/video are available |

Manual counting is a suitable source format. The information retained in the record matters: a total of 6,580 motorcycles does not reveal how many turned left, how fast they discharged, or whether they rode side by side. The source J1 AM motorcycle fraction is 6,580/8,297 = 79.31%, which makes this distinction particularly consequential.

## Audit completed using the available records

The new audit script reads the existing source counts and completed run outputs. It computes vehicle mix and compares actual gateway exits over simulation seconds 600–4,200 against the source hour totals. It does not compare scheduled trips against themselves. It also does not alter demand to make results look closer.

These are **conditional count screens**, not validation scores: the source must first confirm whether totals represent entering vehicles counted once, how days were aggregated, and which counting lines were used. Simulation gateway counts include warmup vehicles crossing during the same hour. GEH is supplied as a diagnostic formula, with no automatic calibration-pass claim.

| Full-demand case | Site | Source hour total | Simulated gateway exits | Signed difference |
|---|---|---:|---:|---:|
| CORRIDOR_AM | J1 | 8,297 | 3,452 | -58.4% |
| CORRIDOR_AM | J2 | 3,580 | 1,033 | -71.1% |
| CORRIDOR_AM | J3 | 5,579 | 1,317 | -76.4% |
| CORRIDOR_PM | J1 | 6,208 | 3,290 | -47.0% |
| CORRIDOR_PM | J2 | 4,942 | 1,331 | -73.1% |
| CORRIDOR_PM | J3 | 6,053 | 1,700 | -71.9% |
| J1_AM | J1 | 8,297 | 3,637 | -56.2% |
| J1_PM | J1 | 6,208 | 3,552 | -42.8% |
| J2_AM | J2 | 3,580 | 1,374 | -61.6% |
| J2_PM | J2 | 4,942 | 1,479 | -70.1% |
| J3_AM | J3 | 5,579 | 1,656 | -70.3% |
| J3_PM | J3 | 6,053 | 1,840 | -69.6% |

Under the entering-once interpretation, the current reference does not reproduce the recorded hourly crossings. Finishing trips in the long drain is not a count fit for the measured hour. Existing volume data are already useful for exposing this discrepancy; they cannot tell us uniquely whether the cause is count scope, reconstructed phases, directional demand, lane/turn geometry, motorcycle lane use, or a combination. Fitting many unknowns to one aggregate would hide that ambiguity.

New evidence: `audit/available_data_volume_fit.csv` has the 12 site/layout comparisons; `available_data_class_volume_fit.csv` has 96 class comparisons; `source_motorcycle_composition.csv` has six observed class-mix summaries; `available_observation_inventory.json` identifies the evidence boundary. Reproduce with:

```sh
python scripts/audit_available_observations.py
```

## Recover and calibrate in this order

1. **Resolve observation meaning.** Recover survey dates, time windows, count locations, entering/exiting convention, class definitions and whether published counts are sums, daily averages or one selected day. Recover complete observed phase plans and offsets. Retain original files and distinguish actual recordings from reconstructed values.
2. **Fit demand from movements.** Map each approach/exit to `calibration/movement_catalog.csv`, retain vehicle classes, and use the finest actual time interval available. An hourly turn table is useful even when five-minute counts are unavailable; within-hour timing then remains an assumption. Fit connected route visits consistently, with one vehicle per journey. SUMO's routeSampler supports edge/turn count constraints; aggregate counts do not uniquely recover OD.
3. **Fit behavior against independent observations.** Compare measured queue trajectories, discharge passage times and travel times with the same locations, windows and definitions in SUMO. Use recorded motorcycle spacing/side-by-side behavior to evaluate a sublane model; retain lane-based behavior as an explicit proxy until supported. Saturation headway must be measured during sustained queued discharge; green onset and the startup portion must be marked. In side-by-side mixed traffic, a single sequential headway is insufficient on its own.
4. **Validate on a different recorded period/day.** Use available raw dates for train/calibration/validation separation. Do not split adjacent samples of the same queue into supposedly independent periods. If only averaged tables remain, independent empirical validation is not available yet. Report actual study-hour throughput and unserved demand alongside queues/travel times.

Blank CSV headers and a movement catalog are in `calibration/`. They are an intake guide, not additional observations. Existing spreadsheets, scans, photographs of tally sheets or videos can be mapped to them; the user does not need to retype everything first.

## Max-pressure and a trainable policy are different choices

Ordinary max-pressure computes a stage score from upstream/downstream queue information, turn ratios and service capacities, then selects service by a rule. It does not inherently need neural-network training. A cyclic/constrained variant is a useful lightweight adaptive comparator for this project. Do not assume the guarantees of an idealized unlimited-storage queue model transfer to our finite corridor with estimated detections and signal-clearance constraints.

A tuned weighted-pressure controller can optimize a small parameter vector offline. That is parameter optimization, not automatically reinforcement learning. A separate compact Double DQN policy can learn green-extension decisions in SUMO and export only its selected inference weights. PressLight is an example of pressure-inspired reinforcement learning, rather than plain untrained max-pressure. The user's PASADA sample has not been received or classified yet.

| Controller | PC work | Local ESP32-C3 work | Proposed role |
|---|---|---|---|
| Reconstructed/verified fixed-time | Recover and calibrate field plan | Execute configured plan | Reference control |
| Cyclic/constrained max-pressure | Specify estimator, service weights and constraints; optionally tune parameters | Compute pressure/decision rule | First adaptive comparator |
| Compact Double DQN | Train with SUMO interaction, validation and robustness checks | Run frozen network and preprocessing | Trainable candidate after calibration/input contract |

## Align the policy with PASADA hardware

The current RESEARCH MASTERSHEET describes approach pucks at 5, 30 and 60 m, downstream sensors proposed for outgoing counts, heartbeat monitoring, and whole-intersection fallback. Their actual installation and detection performance remain unverified.

These point sensors provide occupancy/passage observations; they do not directly provide an exact movement queue. Persistent occupation at 60 m is a congestion cue, not a complete measurement of a queue longer than 60 m or conclusive proof of oversaturation. Turning intent is also unavailable from an upstream point detector alone. Any movement-queue estimator must expose its assumptions and uncertainty; full max-pressure cannot silently consume simulator-only downstream queues.

- Train policy observations from virtual versions of the intended pucks: occupancy, passage rates, timestamps/freshness, controller phase and elapsed timing; downstream/neighbor features only when that telemetry is actually specified and available.
- SUMO exact queues/trajectories may supply training rewards and evaluation truth. They must not be deployed inputs unless an equivalent real observer exists. A teacher using richer state does not remove the student's observability limit.
- After calibration, randomize plausible demand/turn/behavior values and detection misses, false detections, latency, clock error and outages. Randomized assumptions are not new field observations.
- Start with fixed phase order and two actions: extend the current green by a configured increment, or request the next permitted stage. Five seconds is a candidate decision increment, not an approved field timing. During yellow/all-red, hold the prescribed transition; do not accept a conflicting policy action.
- A separate supervisor enforces phase legality, minimum/maximum green, pedestrian service/wait limits, emergency precedence, yellow/all-red, stale-sensor fallback for the whole intersection and sustained-heartbeat recovery. The learned model cannot bypass it. Actual pedestrian timings still need to be added to the motor-only reference before pedestrian claims are tested.

## Offline training and export path

1. Freeze the calibrated SUMO version and sensor/estimator contract. Keep field periods and demand realizations separate for evaluation.
2. Train on the three isolated geometries, then on the corridor with independent agents using the same local feature contract. A shared initial network can be conditioned on verified site configuration and fine-tuned per junction. Coordination features require explicit messages and stale-data handling; training centrally does not authorize perfect local information at inference.
3. Use a reward balancing delay/backlog and throughput, with transition/pedestrian/emergency limits enforced outside the reward. Count uninserted demand so the agent cannot appear successful by leaving vehicles outside the network. Test the same held-out demand, seeds and actuation constraints for fixed-time, pressure and learned controllers.
4. Export preprocessing, feature order, normalization, weights, allowed actions, site configuration and version. The example architecture already in `model/decision_contract.json` is provisional: 32→32→16→2 ReLU, 1,618 parameters, 6,472 bytes of float32 parameters only. Neither 32 features nor the architecture is final; activations, tensor arena, firmware, radio and stacks consume additional memory.
5. Evaluate int8 quantization or a direct C inference implementation. Verify PC/export outputs and selected actions, exact-board peak memory, inference latency under radio/RTC load and fault transitions. Espressif provides TFLite Micro support and reports an ESP32-C3 example, but no project-specific board benchmark has been performed here.

A policy can be trained in the present assumed simulator as a **preliminary simulation experiment**. It cannot presently be described as trained on a field-calibrated model or ready for road deployment.

## What to provide next

- The original manual tally sheets/workbooks or retained observation videos, including dates and class/movement labels. Prioritize movement counts plus complete phase/event records; queue/discharge footage fills the motorcycle-performance gap.
- A ZIP of the PASADA SUMO example including `.sumocfg`, referenced `.net.xml`, `.rou.xml`, additional/TLS/detector files, Python/TraCI controller scripts, and any model weights/configuration with dependencies or run instructions. A GUI screenshot or `.sumocfg` alone cannot reveal the control algorithm. Scripts are needed to see whether the code uses max-pressure, a trained policy, or a hybrid, and whether it reads simulator-only information.

## Primary references

- SUMO count reconstruction and ambiguity: https://sumo.dlr.de/docs/Demand/Routes_from_Observation_Points.html
- SUMO turn-count/routeSampler inputs: https://sumo.dlr.de/docs/Tools/Turns.html
- SUMO sublane behavior and parameters: https://sumo.dlr.de/docs/Simulation/SublaneModel.html
- Lioris and Varaiya, *Variants of max pressure control for a network of signalized intersections*, pressure definition and scheduling: https://connected-corridors.berkeley.edu/sites/default/files/Variants%20of%20Max%20Pressure%20Control%20for%20Signalized%20Intersections.pdf
- PressLight authors' implementation/paper citation: https://github.com/wingsweihua/presslight
- Espressif TFLite Micro, including ESP32-C3 example benchmark: https://github.com/espressif/esp-tflite-micro
- Espressif ESP32-C3 datasheet: https://documentation.espressif.com/esp32-c3_datasheet_en.html
- User's RESEARCH MASTERSHEET design checked 26 October 2026: https://docs.google.com/spreadsheets/d/1shrMPCeYoXxVgBCjtYuszS3Dr_BKjSz9p1VjPYDywzU/edit
- User-provided signal-timing study, PDF pp.41–44, 53–57, 73–74; source PDF not redistributed.
