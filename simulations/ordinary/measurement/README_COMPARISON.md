# Matched Mandaue fixed-time / PASADA comparison

Completed 1 November 2026. This package contains **48 actual SUMO 1.28.0 runs**:
three isolated intersections and a connected network, AM/PM, fixed/local rule,
three seeds (7100, 7101, 7102). No new model training or parameter search occurred.

The candidate is the existing transparent puck-occupancy/passage rule in
learning/control.py, not a trained neural policy or a proven exact max-pressure
implementation. The network's three controllers act independently; road traffic
connects them. There are no C2C coordination overrides in these runs.

## Open the evidence

- results/paired_nov01/manuscript_tables.json: Tables 8–10 and paired changes.
- summary_by_case.csv: run-level-statistic means and sample SD by case/control.
- paired_changes.json: each seed's paired change and mean/sample SD.
- run_measurements.csv / .json: all 48 run records.
- seed*/CASE/CONTROL/cohort_trips.csv: one record per scheduled study trip.
- approach_queues.csv: incoming-approach congestion samples every five seconds.
- sensor_trace.csv / supervisor_events.json: observer and signal-state records.
- audit.json / output_audit.csv: independent checks of inputs, native outputs,
  372 movement/class constraints and 389,220 study-cohort records.
- common_completed_trip_check.csv: an ancillary check using the same completed
  vehicle IDs in each matched pair; it is not a full-demand estimate.
- paired_effects.png / .pdf: print-ready comparison figure.

Complete native SUMO outputs are the SHA256-checked tripinfo.xml.gz,
summary.xml.gz and collisions.xml.gz beside native_outputs.json. They were
captured immediately after SUMO closed and parsed independently. One later
uncompressed tripinfo copy differed from its complete mirror; the complete,
verified mirror is authoritative. Uncompressed duplicates are excluded from
this package. Python's gzip module or a standard archive utility opens them.

## Measurements and their limits

Each run starts empty, uses a 600 s synthetic warmup, then schedules the recorded
one-hour class totals from 600 to 4200 s at factor **1.00**, without teleports.
The study cohort excludes warmup vehicles, although warmup traffic remains
physically present. Every study vehicle is classified at the common 4200 s
cutoff as completed, active, or not inserted. Corridor unique journeys are
15,509 AM / 14,702 PM; do not add site totals, because a journey can visit
multiple sites. Local/corridor movement-class marginals match exactly.

Completed-trip travel time is SUMO duration (actual insertion to arrival).
Waiting is stopped time at <=0.1 m/s, timeLoss is slower-than-ideal travel and
already includes stopped loss, and stops are waitingCount episodes. These are
not HCM intersection control delay or LOS. The run-level 95th percentile is
averaged over the three seeds; the table does not pool their trips.

The primary all-demand measure averages, over **all** study vehicles, elapsed
time from scheduled departure to arrival or the common cutoff if unfinished.
It includes insertion waiting and in-network travel, and is a lower bound on
eventual journey time. Its smaller improvements cannot be replaced by the
larger completed-only travel-time reductions. Error bars are sample SD over
three paired seeds, not confidence intervals.

Halting counts sum vehicles on the modeled incoming signal-approach edges.
The tail extent is signal-lane-end distance to the rearmost stopped vehicle's
rear, not a continuously observed contiguous jam length. It is bounded by the
modeled approach edges; upstream spillback and uninserted demand still matter.
Exits in hour counts all vehicles arriving between 600 and 4200 s, including
warmup vehicles, and is different from study-cohort completions.

## What the evidence says

Connected AM / PM completed mean travel: 473.4 -> 368.2 s and 443.1 -> 313.7 s.
All-demand accrued-time reduction: 5.78 +/- 0.48% and 6.73 +/- 0.39% (sample SD).
Study-cohort completion increases by 4.81 and 3.76 percentage points. Large
insertion backlogs remain. A.C. Cortes has higher 95th-percentile travel times
and slightly lower completion; A. Soriano PM has more stop episodes. No blanket
claim that every traveler or every metric improves is supported.

The 48 current runs record zero collisions, zero teleports and no audited
cyclic/minimum-green/yellow/all-red violations. This is a finite motor-only
experiment, not complete pedestrian/emergency/roadside acceptance. The source
provides representative G/Y/R summaries rather than full phase plans; the fixed
program is reconstructed, with assumed splits/order/offsets and 4 s all-red.
Turning allocations, arrival times, lane geometry and lane-based motorcycle
behavior require field validation. Ideal SUMO point events are not physical
magnetometer accuracy or radio tests. Recorded emergency-class vehicles behave
as ordinary vehicles; no emergency preemption or pedestrian service is tested.

The prior V2 learned-model collision at J2 PM seed5101 remains in
prior_learned_failure/. It is a separate archived experiment, not one of these
48 rule/fixed runs. Its learned bundle remains on hold. The original complete
PASADA_SUMO_Starter.zip release is preserved separately.

## Watch it yourself

Use a normal desktop SUMO 1.28.0 installation with sumo-gui, Python 3.10+,
and set SUMO_HOME to that installation if needed. In the extracted root:

    python -m pip install -r requirements_comparison.txt
    python measurement/watch.py --case J3_AM --mode fixed --seed 7100
    python measurement/watch.py --case J3_AM --mode rule --seed 7100

Use J1_AM, J1_PM, J2_AM, J2_PM, J3_AM, J3_PM, CORRIDOR_AM or CORRIDOR_PM.
Opening a .sumocfg alone runs fixed control; the Python runner is required
for PASADA. Keep Scale Traffic at 1.0. Each viewing gets a fresh output folder
and does not replace the measured comparison. Headless pip SUMO does not supply
a desktop display or necessarily sumo-gui; use the desktop SUMO installation
for animation.

To reproduce the measurements:

    python measurement/paired_study.py --all --jobs 4
    python measurement/analyze_paired.py

The runner resumes included measurements. To execute all 48 again, first move
results/paired_nov01 to a different name, preserving it for comparison. Inputs,
seeds, controller rule and protocol remain frozen; a changed experiment needs
a new output version and explicit protocol, not overwriting unfavorable runs.

## Source and attribution

Original package: PASADA_SUMO_Starter.zip, Library identity
libfile_56ab08aaade081918dcd5522dc73300c, version 5. Source team manual traffic
study: Transpo_ Signal Timing Optimization(2).pdf, pp.33–39, 53–55 and 61–63.
The source PDF is not redistributed. OSM attribution and reconstruction notes
are included. See source_source_notes/ for the original baseline audit.

Eclipse SUMO. (n.d.). TripInfo. https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html
Eclipse SUMO. (n.d.). Traffic lights. https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html

