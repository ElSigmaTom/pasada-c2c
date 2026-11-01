# Native SUMO experiment sources

Use Python 3.12 and desktop Eclipse SUMO 1.28.0. Install the corresponding requirements.txt/requirements_comparison.txt/requirements_emergency.txt. Keep every folder's network, scenarios, data, model, learning and audit dependencies together. The root README provides GUI viewing commands and four-layout case names.

## View or analyze first

Fresh ordinary GUI: from ordinary/, run `python measurement/watch.py --case CORRIDOR_AM --mode rule --seed 7100`. Choose fixed for baseline. Fresh emergency GUI: from emergency/, run `python emergency/run_study.py --case CORRIDOR_AM --arm priority20 --seed 7300 --tag replay --gui`. Choose fixed/local for the matched controls. These GUI viewing paths preserve the delivered measurements. Start playback in SUMO-GUI and keep the Python runner open.

Reaggregate recorded ordinary data with `python measurement/analyze_paired.py`, emergency data with `python emergency/analyze.py`, and LOS data from los/ with `python analyze_local_delay.py`. Inspect audit results and retained adverse cases, not only pooled improvements.

## Execute fresh full experiments

Work on a copy of this package. First move the specified output directory to a clearly named backup outside its original path. Do not delete the delivered records. Full runners resume existing complete measurements, so moving the directory is necessary for an actual fresh simulation. Keep the folder-specific frozen inputs unchanged.

| From folder | Preserve/move before rerun | Commands |
| --- | --- | --- |
| ordinary/ | results/paired_nov01/ | `python measurement/paired_study.py --all --jobs 4` then `python measurement/analyze_paired.py` |
| emergency/ | results/emergency_nov01/ | `python emergency/run_study.py --all --jobs 4` then `python emergency/analyze.py` |
| los/ | results/runs/ only | `python measure_trajectory_delay.py --all --jobs 4` then `python analyze_local_delay.py` |

For LOS, keep source_project/results/paired_nov01/: it is the original comparison reference for reproduction checks. A selected LOS rerun accepts `--case J3_AM --mode rule --seed 7100`. Use fewer --jobs if memory is limited. GUI runs require a display; headless batch runs use libsumo. An existing mismatched protocol deliberately stops a run: preserve it and use a fresh output copy rather than weakening the check.

## Evidence locations

| Experiment | Principal records |
| --- | --- |
| Ordinary | ordinary/results/paired_nov01/summary_by_case.csv, paired_changes.json, manuscript_tables.json, audit.json |
| Ordinary individual trips | ordinary/results/paired_nov01/seed*/CASE/CONTROL/cohort_trips.csv; approach_queues.csv; measurement.json |
| Emergency | emergency/results/emergency_nov01/; emergency/analyze.py writes the experiment summaries there |
| Emergency individual runs | main/seed*/CASE/ARM/emergency_metrics.json, ordinary_cohort.csv, beacon_packets.csv, beacon_events.json, probe_positions.csv |
| Cap sensitivity | emergency/results/emergency_nov01/cap_sensitivity/ |
| Local delay / estimated LOS | los/results/table10A_local_delay.csv, summary.json, run_local_delay.csv and runs/ |
| Native SUMO output | Per-run tripinfo.xml.gz, summary.xml.gz, collisions.xml.gz and native_outputs.json |

Compressed XML files are the archived native outputs; Python's gzip module or a standard archive utility can read them. New runs may also produce uncompressed XML. Maintain the original native-output fingerprints. C2C browser experiment percentages and public sample counts are not inputs to the manuscript's native SUMO results.

## Control and interpretation

The ordinary rule reads the modeled puck observation contract, adjusts service locally and preserves the signal supervisor's clearance/cyclic constraints. Evaluation-only SUMO ground truth is not a policy input. It is a fixed transparent rule, without model training or parameter search in this release. Connected traffic moves between intersections; control remains local rather than MARL. Emergency requests are qualified from modeled position history and geometry before protected stage transfer. All controls retain identical background demand and probe behavior.

Ordinary metrics include the full scheduled cohort at a common cutoff, plus completed-trip and queue diagnostics. The local-delay supplement uses bounded junction-area timeLoss and retains open passages; its HCM-threshold letter is an estimate, not formal field LOS. A result can improve delay while remaining F. Retain unfavorable network/evening and emergency cases. No physical RF, GNSS error distribution, firmware write or live road performance is validated here.

## Source integrity and dependency recovery

SOURCE_INTEGRITY.json records the SHA-256 of every delivered simulation file, excluding itself. Existing source/output bytes are retained. The ordinary and emergency archives lacked a required audit/reference_signal_stages.csv; the full audit/ dependencies were restored from the existing LEAR_SUMO_Simulations_GitHub_Ready.zip source. These restored files are listed separately in the manifest. Existing experimental protocol files are not rewritten to conceal that addition. The LOS package retains its own recovery and native-reproduction audit.

Keep the OpenStreetMap attribution and source_notes/. Manual counts and signal assumptions are documented in each package; reconstructed detail must not be described as an observed movement-by-movement field calibration. Use the root README and source notes together when reproducing the work.
