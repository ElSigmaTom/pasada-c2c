**Scope:** this report concerns the preserved fixed-time reference. The newer trained-controller experiment is in MODELS_REPORT.md.

# Refined baseline report — 26 October 2026

**Outcome:** a repeatable reconstructed fixed-time simulation reference for the three isolated junctions and their connected corridor, each in AM and PM. PASADA is disabled. Mechanical checks pass; field calibration remains incomplete.

## Changes that matter

1. **Corrected physical junction geometry.** The imported J3 controller spanned several separate physical junction nodes and short internal road sections. Diagnostic vehicle states showed mutual blocking lasting over 1,300 s. Explicit netconvert node joins now model J3 as one physical junction; J1's corresponding signal-node cluster is also joined. J2's staggered F. Mendoza connection remains separate. The raw import and plain-XML patch are preserved. This fixes a modeling artifact; its benefit must not be credited to PASADA.
2. **Controlled demand scale.** Primary configurations and the launcher explicitly use 1.0. The supplied GUI screenshot showed Scale Traffic 4.5, which changes demand. Independent checks also found the former model could jam at 1.0, so resetting scale alone was insufficient.
3. **Matched planned demand.** Isolated routes now derive movement/class visits from the same canonical corridor journeys. Planned study-hour source class marginals are preserved, local/corridor movement matrices match, and each isolated map is genuinely cropped. Local departure schedules are assumed boundary injections, not observed downstream arrival times.
4. **Declared fixed reference signals.** Each AM/PM cycle candidate uses the source representative G+Y+R conditionally. Four protected motor-arm stages share the available green according to planned approach volume per motor lane, with a 10 s green floor. Yellow is 4 s from the source summaries; 4 s all-red is assumed and checked in simulation. Offsets are zero. This reconstructs a usable reference; it does not establish the actual field program.
5. **Longer diagnostic horizon and honest backlog accounting.** No planned demand after 4,200 s; runs continue to 14,400 s. Junction collision checks remain on, the default minGap collision threshold is retained, and automatic teleports are disabled. Uninserted and unfinished vehicles remain in the results.

## Source boundary

The source's PDF page 73 explicitly states that recorded traffic was reduced by 50% for its simulation. Therefore its reported performance cannot directly validate our full-demand runs. The optional ST50 scenarios reproduce that load factor only; the source's complete executable model is unavailable.

PDF pages 54–55 provide representative signal summaries, not full movement-specific phase plans. Their G/Y/R sums provide these **conditional cycle candidates**, not verified observed cycles:

| Site | AM candidate cycle | PM candidate cycle |
|---|---:|---:|
| J1 | 203 s | 378 s |
| J2 | 106 s | 141 s |
| J3 | 104 s | 214 s |

The paper's optimized timing tables are not substituted for the existing baseline. Its “All Red” table labels also conflict with a worked ordinary-red calculation; those values are not treated as clearance intervals. See `DATA_AUDIT.md`.

## Results of the checked release

SUMO 1.28.0; step 0.5 s. Forty runs: eight full-demand cases at seeds 42/43/44 (24), eight ST50 cases at seed 42, and eight scale-0.1 diagnostic cases at seed 42. All output XML sets were parsed after completion. Every run exited successfully, with **zero recorded collision events and zero teleports**. All eight low-load and eight half-load cases cleared by the horizon. This is mechanical acceptance, not field validation.

Full-demand seed-42 totals below **include synthetic warmup**. Arrivals are through 14,400 s, not one-hour throughput.

| Case | Scheduled | Arrived | Still in network | Not yet inserted | Arrivals in final 600 s |
|---|---:|---:|---:|---:|---:|
| CORRIDOR_AM | 18,154 | 15,656 | 149 | 2,349 | 220 |
| CORRIDOR_PM | 17,215 | 15,192 | 157 | 1,866 | 314 |
| J1_AM | 9,680 | 9,680 | 0 | 0 | 0 |
| J1_PM | 7,243 | 7,243 | 0 | 0 | 0 |
| J2_AM | 4,177 | 3,618 | 80 | 479 | 112 |
| J2_PM | 5,766 | 4,546 | 82 | 1,138 | 141 |
| J3_AM | 6,508 | 4,565 | 58 | 1,885 | 112 |
| J3_PM | 7,062 | 6,250 | 62 | 750 | 167 |

J1 clears in both periods. J2/J3 and the corridor retain full-demand queues across all three seeds, but every residual-demand case continues to discharge in the final 600 s. Low-load clearance and late discharge support removal of the original persistent model standstill. They do not prove all possible deadlocks are eliminated, nor that the residual queues match field conditions. Source-hour gateway exits and backlog at 4,200 s are reported separately in the CSV outputs.

**Warnings are retained.** Across the 40 runs there are eight emergency-braking warnings. Motor-only J2/J3 programs also report missing-green warnings for unused nonmotor-only signal links (J2 index 6; J3 index 7). No supplied route uses these links; input validation checks that every used signal connection receives green. There are no person or bicycle flows. These programs must not be used to assess pedestrian/bicycle service. Zero collision events does not mean zero warnings or validated road safety.

## Interpretation limits and next baseline inputs

- Hourly source counts constrain class/site totals, not unique OD or turning proportions. Canonical journeys provide one plausible flow-consistent reconstruction. Their source priors and count assumptions remain explicit.
- Imported lane counts, lane use, stop lines, restrictions and speeds require survey verification. Joining physical nodes fixes a known artifact; it does not survey the junction.
- LC2013 represents motorcycles in lanes. Filtering and side-by-side discharge are not represented. With the source's high motorcycle share, this can materially bias capacity. PUV/PUJ/PUB definitions and vehicle proxies also need confirmation.
- No pedestrian demand, observed manual-enforcer operation, loading activity calibration, emergency preemption, sensor faults or PASADA control is included. Adjacent accesses can affect corridor queues.
- Completed-only averages omit unserved demand. Always report insertion delay/backlog, unfinished trips and study-hour crossings alongside waiting, time loss and travel time. The extended drain cannot substitute for hourly capacity.
- Three seeds test stochastic behavior around one fixed canonical arrival/OD realization. They do not establish robustness to uncertain turning counts or alternate demand histories.

To turn this reference into an empirical baseline, prioritize complete observed phase sequences/splits/offsets, synchronized approach-to-exit counts and arrival profiles, and independent queue/discharge/travel observations. Then calibrate motorcycle lane use and verify pedestrian/manual-control service. Freeze a new version and validate on an independent period before attributing gains to PASADA. Until then, any comparison would be conditional on the declared reconstructed inputs.

## Reproduction and evidence

`HOW_TO_RUN.md` contains the Windows launcher, four situation mappings and full headless reproduction commands. `audit/baseline_acceptance.json`, `input_validation.json`, `isolation_validation.json`, `matched_movement_counts.csv` and `reference_signal_stages.csv` supply acceptance evidence. `results/validation_summary.csv` covers all 40 runs, `reference_summary.csv` covers the 16 prepared full/half-load cases, and `source_hour_crossings.csv` covers the hour separately. Raw outputs and portable per-run configurations are included. `audit/legacy_v1/` is historical only.


## Available-data audit addendum

See CALIBRATION_AND_TRAINING.md and audit/available_data_volume_fit.csv. Under the unconfirmed entering-once source interpretation, actual study-hour gateway counts do not match the published totals (for example, isolated J1 AM: 3,637 simulated versus 8,297 reported). This release therefore remains an uncalibrated reconstructed reference. The source says richer manual/video observations were recorded, but their raw values are not present in the available published tables. No simulation inputs or controller behavior changed for this addendum.
