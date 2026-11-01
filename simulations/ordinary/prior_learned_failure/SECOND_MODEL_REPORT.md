# PASADA second model experiment

28 October 2026 · SUMO 1.28.0 · release 3.1 · research simulation

The three selected models and their C99 exports are included. **HOLD: a selected policy failed a held-out simulation safety diagnostic. See the failed-run table below. This is a completed comparison under assumed demand, not a field-calibrated controller.** Full results include every predeclared test case and the failed J2 training episode.

Use **RUN_MODELS_V2.bat** or **MODEL_V2_QUICKSTART.md** to view one junction or the corridor. The original fixed baseline and first-model release remain available.

## What changed

The first learner trained for only 1,500 s per episode but was evaluated over 4,200 s. Its timing ratio also conflated elapsed seconds with the AM/PM reference duration. V2 uses full-window episodes, an explicit 43-feature timing interface, an unclipped positively rescaled training reward and a rule-imitation warm start. The original sensor positions, closed counting boundary, counts, route tables and geometry are unchanged; all 81 baseline input hashes match the prior release.

The 43→32→16→2 network has **1,970 float32 parameters / 7,880 bytes of weights per site**. Four extra timing fields replace one old ratio: elapsed green, remaining yellow, remaining all-red and configured reference green. Those fields come from the controller. Puck occupancy, count rates, downstream occupancy, stock and trust still provide the traffic observations. IDs, exact queues, speeds and route intentions are excluded from the policy inputs.

## Training and selection

The supervised warm start uses legal-action states from the preserved original replay archive: first ten episodes for fitting, last two for teacher-fidelity checks. Training then proposes eight 4,200 s Double DQN episodes per site, with AM/PM, 0.6/1.0 loads, ±30 s departure jitter, missed/false count pulses and outages. Gamma is 0.995 per five-second decision; learning rate 0.0002, batch 64, replay capacity 20,000 and target copy every 100 updates. Time-limit truncation bootstraps. Per-episode configs, randomized demand, metrics, detector traces and collision logs are retained. Repeated training trip/summary XML files are removed only after parsing their metrics; the failed J2 episode retains those raw files.

Checkpoint selection uses only validation seeds 4100/4101 and the mean AM/PM cost ratio to the rule. Proposed candidates are the imitation-only warm start and checkpoints after 4/8 reinforcement-learning episodes. Final-test seeds never select weights.

| Site | Selected RL episodes | Selected policy | Validation cost change vs rule |
|---|---|---|---|
| J1 | 4 | rule-imitation warm start plus Double DQN | +0.03% |
| J2 | 4 | rule-imitation warm start plus Double DQN | -2.19% |
| J3 | 0 | rule imitation student | -0.53% |

J3 is therefore an **imitation-only student**, with zero reinforcement-learning updates in its selected weights. Calling all three selections successful Double DQN improvements would be inaccurate. J1/J3 finished all eight training episodes; J2 stopped during its fifth.

### Preserved training failure

J2 seed 22004, scale 0.6, with 1% misses and 0.0002 false pulses per row per second recorded a motorcycle/wing-van junction collision at 3,853 s. It occurred at the unsignalized right-before-left node `282921470`, approximately 180 m from the main J2 signal. The in-progress learner was abandoned. J2 selection uses only its already completed candidates 0/4; candidate 8 is unavailable.

Fixed, rule and frozen checkpoint-4 replays used a byte-identical demand file and each recorded zero collisions/teleports. The failed exploratory signal-request schedule was also replayed separately without learning; its result is preserved in `audit/second_model_schedule_replay.json`. The request-schedule replay reproduced the original collision record and sampled cost exactly. These diagnostics do not establish a resolved root cause or enter the held-out performance table. `audit/second_model_deviation.json` records the protocol deviation before final testing; no seed was silently skipped and collision checks were retained.

## Fresh ideal-pulse comparison

64 runs: eight cases × fixed/rule/first-model/V2 × fresh seeds 5100/5101. Each covers 0–4,200 s, including the 600 s warmup and 3,600 s demand schedule, without the extended drain. Each matched comparison shares scheduled demand and vehicle-behavior seed. The underlying reconstructed route table is shared across seeds; these are not independent field days or new turning-demand samples.

The objective is **5 × (halting vehicles + vehicles awaiting insertion + 0.05 × running vehicles)** sampled every five seconds and summed through the horizon. It includes uninserted demand and is not HCM control delay. The training rescaling does not change this reported objective. Completed-only travel statistics are retained in the raw metrics but cannot represent vehicles still waiting or unfinished.

Mean paired percentage change versus fixed timing over two seeds; **negative is better**. Remaining vehicles are unfinished plus scheduled-but-uninserted V2 vehicles at 4,200 s.

| Case | Rule cost | First DDQN cost | V2 cost | V2 mean remaining |
|---|---|---|---|---|
| J1_AM | -1.31% | -1.09% | -1.47% | 5,388 |
| J1_PM | +1.80% | +6.79% | -1.62% | 3,194 |
| J2_AM | -0.35% | +1.75% | -0.92% | 2,542 |
| J2_PM* | +0.72% | +2.58% | -1.57% | 3,970 |
| J3_AM | -2.18% | -5.47% | -2.99% | 4,478 |
| J3_PM | -4.23% | -0.56% | -2.83% | 4,824 |
| CORRIDOR_AM | -5.48% | -2.46% | -1.92% | 12,012 |
| CORRIDOR_PM | -3.17% | +3.00% | +2.10% | 11,438 |

An asterisk identifies a case with a recorded final safety failure. That run remains visible; collision-action=warn lets the simulation continue, so its post-collision cost cannot support an acceptable-performance claim.

Raw equal-weight mean of all eight case percentages (including any safety-failed run): rule **-1.77%**, first DDQN **+0.57%**, V2 **-1.40%**. This descriptive mean mixes isolated and corridor scenarios; it is not a citywide benefit estimate. Two seeds support a preliminary repeatability check, not a significance claim. Keep weaker cases and substantial residual demand visible. Downstream-puck benefit has not been isolated by sensor ablation.

The rule is a weighted sensor-occupancy/arrival score with a downstream penalty and cyclic phase order. It is **not a calibrated classical max-pressure controller**. The three corridor agents act locally; no learned intercontroller messaging is implemented.

## Count uncertainty and puck outage

16 further runs use seed 6100, four cases and the same four modes. J1/J3 AM have 2% independently missed passage pulses plus Poisson false counts at 0.001 per row per second; their occupancy readings remain ideal. J2/corridor PM lose one required puck during 1,800–1,860 s (J1 is affected in the corridor). These are declared synthetic tests, not measured magnetometer error distributions.

| Case | Disturbance | Rule cost vs fixed | First DDQN vs fixed | V2 vs fixed |
|---|---|---|---|---|
| J1_AM | count noise | -1.39% | -0.98% | -0.51% |
| J2_PM | one puck outage | -1.92% | +2.24% | -1.74% |
| J3_AM | count noise | -4.79% | -5.43% | -3.64% |
| CORRIDOR_PM | one puck outage | -2.99% | +1.96% | +1.99% |

The fixed comparator keeps its reference plan when an unused sensor fails. Adaptive controllers use the same whole-intersection fallback and 60 s healthy recovery. For the V2 outage runs:

| Case | Fallback starts (s) | Adaptation resumes (s) | Max sampled stock error (vehicles) |
|---|---|---|---|
| J2_PM | 1803.0 | 1952.0 | 11 |
| CORRIDOR_PM | 1803.0 | 1922.0 | 6 |

**Heartbeat recovery does not recover lost counts.** Absolute inventory remains invalid after the outage; the model receives a withheld stock field and trust=0 until independent reconciliation. Raw balances remain in the logs. Inventory truth is queried only for evaluation, every 30 s, and never fed to the controller. The original ideal-boundary audits are preserved; noise/fault drift is not silently reset. Knowing the injected noise configuration allows the simulator to withhold trust; a real receiver still needs independent integrity diagnostics.

## Safety and export checks

| Failed final case | Mode | Seed | Collisions | Teleports |
|---|---|---|---|---|
| J2_PM | v2 | 5101 | 1 | 0 |

**The selected V2 bundle is held for diagnosis. Its weights remain frozen and available for research; they are not replaced using final-test outcomes.**

All 80 final output sets were parsed (240 trip/summary/collision XML files). Five incomplete raw outputs were reproduced with identical saved metrics except wall-clock runtime; the exact cases and comparisons are recorded in `audit/second_model_output_repairs.json`. Byte-checked `.xml.gz` mirrors accompany the native XML files and supply the canonical archived bytes. They recorded **1 recorded collision event(s) and 0 teleports**. Every recorded phase transition passed checks for cyclic order, minimum green, 4 s yellow and 4 s all-red. Warning counts and every run's safety outcome are in `results/models_v2/safety_summary.csv`. The separate failed training episode remains disclosed above. Passing a finite simulation suite does not establish field safety.

Fifteen targeted unit tests passed. Frozen selected model hashes and all six old/new model compatibility checks passed. The C99 exports matched Python actions on **1,536 states** (512/site), including illegal-advance masking. Maximum absolute output difference was 7.63e-06; maximum normalized relative difference was 9.69e-07. J3 outputs are classification logits; their ordering selects the action. Desktop numerical parity does not establish ESP32-C3 latency or total firmware memory.

## Scope and next step

Resolve and validate any failed junction interaction before promoting a learned controller or claiming a usable optimization. Retain the reconstructed fixed plan as the reference and compare the transparent rule with the selected learned policy in every case before making a PASADA performance claim. A new training iteration needs a new reserved validation/test split. Recovering original turning, queue/discharge, signal and motorcycle observations remains necessary for field calibration; aggregate class totals do not identify these parameters uniquely.

Upstream requested offsets are 5/30/60 m, with post-intersection passage rows and all modeled side boundaries included. Exact actual chainages remain in `model/sensors/puck_locations.csv`. Conservation estimates total stored vehicles, **N=N0+all boundary entries−all boundary exits**, not per-approach queues. The upstream 5 m count is not confirmed discharge. Real deployment needs a known initial inventory and a complete observed boundary.

This motor-only pilot still excludes pedestrian service and emergency-beacon preemption, including emergency service during fallback. Radio/RTC packet handling, physical magnetometer pulse resolution/crosstalk, motorcycle filtering, surveyed geometry, approved clearances and exact ESP32-C3 firmware/board tests remain unfinished. The C exports provide inference weights and functions, not a finished traffic-signal driver.

## Reproduce the J2 held-out failure

```sh
python learning/experiment_v2.py run --case J2_PM --mode v2 --seed 5101 --tag diagnosis --gui
```

Inspect unsignalized node `282921470` at 1,085 s. The recorded pair is container van `J2_CORRIDOR_PM_00776` and stationary motorcycle `J2_CORRIDOR_PM_03365`. Compare the same case/seed with `--mode fixed` and `--mode rule`. Separate diagnosis folders preserve the delivered test evidence. Next, validate this side junction's actual priority, stop-line placement, internal turn paths and blocked-exit behavior against site evidence before changing geometry or vehicle assumptions. A repair requires matched comparator reruns and a compatible newly reserved model-validation/test campaign; disabling collision detection or skipping the failing seed is not a repair.

## Reproduce and inspect

- `MODEL_V2_QUICKSTART.md` and `RUN_MODELS_V2.bat`: launch instructions and reproduction commands.
- `learning/experiment_v2.py`: training/evaluation; `report_v2.py`: generate tables and audits from all results.
- `audit/second_model_protocol.json`: original frozen protocol; `second_model_deviation.json`: explicit J2 deviation.
- `model/trained_v2/`: selected weights, provenance and available checkpoints; `model/export_v2/`: C99 headers.
- `results/models_v2/test_comparison.json`, `robust_comparison.json`, CSV summaries and per-run folders: complete evidence.
- `results/models_v2/training/J2/episode04/`: failed exploratory run; `safety_regression/` and `safety_schedule_replay/`: separate replay evidence.
- `audit/second_model_release_checks.json`, `model_export_parity_v2.json`: release checks and C numerical parity.

Primary references: [Double DQN](https://arxiv.org/abs/1509.06461), [SUMO E1 observations](https://sumo.dlr.de/docs/TraCI/Induction_Loop_Value_Retrieval.html), [SUMO collision diagnostics](https://sumo.dlr.de/docs/Simulation/Safety.html). Original baseline provenance and OSM attribution remain included.
