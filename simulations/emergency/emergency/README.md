# PASADA emergency-beacon experiment — 1 November 2026

78 actual SUMO 1.28.0 runs: 72 main comparisons and 6 predeclared cap sensitivities.
All probes finished. Native output, input and phase-state audits passed; there
were zero recorded collisions, zero teleports, zero incorrect/unverified
approach matches and no first matches after stop-line passage. Ten separate
software tests cover registration binding, duplicates/staleness, stationary
jitter, ambiguous approach rejection, timeout, full clearance and puck fallback.
These are simulation/software results, not physical beacon or road acceptance.

## Experiment

Fixed timing, local PASADA without a beacon, and the same local PASADA with a
20 s encounter cap are compared at J1/J2/J3 and the connected network, AM/PM,
seeds 7300/7301/7302. A separate 60 s cap is tested only at J3 AM/PM. One
technical pilot at seed7200 is excluded from the 78-run analysis and retained
as pilot evidence. No policy was selected or retrained from the reported runs.

Background traffic retains the original 100% source-count reconstruction.
Exactly ONE controlled emergency probe is added at scheduled time1800s in
every arm, including periods with no observed emergency vehicles. This is an
experiment, not a claim that an emergency was manually observed. A simple
existing three-site route containing the A.Soriano/Ouano through movement is
selected by geometry, before outcomes; isolated probes use its matching local
movement visits. The probe has identical 5m/2m passenger-proxy behavior in all
arms, with emergency GUI shape. SUMO blue-light privileges, red-light bypass,
speed-mode overrides, free lane passage and teleports are not used.

The receiver sees 1Hz ideal coordinates as GNSS packets, with a nominal 0.5m
error bound and a fixed 0.5s delivery delay. No sampled GNSS error or physical
radio is claimed. At least three fixes in5s and displacement exceeding the
error-radius sum plus1m are required. A provisioned approach map, 150m approach
gate, 12m lateral gate and45degree heading gate determine the incoming stage.
Registration/active/session/sequence/freshness are checked as software fields;
this is not a cryptographic or hardware authentication test. SUMO route and
next-TLS queries are used by the evaluator only, never to choose the request.

Priority may transfer to the requested protected motor stage after at least
10s current green and complete4s yellow/4s all-red. A current matching green
can be retained within the supervisor's maximum. Fresh position retains the
request, with GNSS exit release or staleness/cap release. The20s or60s cap
starts at first accepted request, INCLUDING transition time; it does not renew
for the same encounter. Ordinary cyclic local operation resumes via clearance.
There are no pedestrians, competing emergencies or coordinator-death cases in
the traffic runs. The separate unit test covers a healthy coordinator in puck
fallback, not a complete physical failure test.

## Measurements

- total: scheduled-start-to-arrival, including SUMO insertion waiting;
- road: actual insertion-to-arrival travel;
- insertion delay, stopped waiting, time loss and stop episodes;
- accepted-request-to-first-compatible-green;
- front stop-line passage while the request is still active, not full rear
  clearance of the junction;
- ordinary traffic accumulated time and completion at the common4200s cutoff;
- all native collisions/teleports and the guarded signal transition sequence.

The background uses600s warmup plus3600s of study demand. If needed, runs
continue until the emergency probe arrives (maximum14400s); ordinary traffic
is always evaluated at4200s. Extending the run for the probe never converts
late ordinary trips into study-hour completions. Probe travel and traffic
counts are paired by identical demand file and seed. Summary values are means
of three trials; variation is sample SD, not a confidence interval. Network
request metrics pool nine site encounters (three per journey), versus three
encounters per isolated case. Scheduled-start totals are not clinical dispatch
response times or independently measured road travel.

## Main outcomes

Network on-road probe means (s):

| Period | Fixed | Local, no beacon | Local +20s beacon |
|---|---:|---:|---:|
| AM |774.3|761.0|543.8|
| PM |1054.7|773.2|565.5|

Beacon-versus-local mean time saved:217.2s AM /207.7s PM. Ordinary accumulated
time increased0.04% /0.05% on average; ordinary completion fell0.16/0.15pp.
This is not a claim of zero cost to other traffic.

At isolated J3 AM, the20s beacon worsened total time from872.3 to942.5s versus
local control; the60s sensitivity reduced it to765.3s. J3 PM total time was
355.0s local,266.5s with20s and238.3s with60s. One PM seed worsened with60s,
so longer service is not an established universal optimum. At A.C.Cortes the
probe remained much slower than the fixed reference in total time; insertion
backlog is substantial, particularly PM. These unfavorable cases remain in
all summaries. Default green response can improve without the vehicle passing
during its short window. Figures use actual event timestamps to show this.

## Inspect and reproduce

- results/emergency_nov01/protocol.json: frozen task list and source hashes.
- input_manifest.json and inputs/: probe route, added demand and installed map.
- summary.csv, paired_changes.json, request_episodes.csv: reviewed measurements.
- manuscript_tables.json: paper Tables11–13.
- audit.json / audit_by_run.csv: independent output/accounting/state audit.
- main/seed*/CASE/ARM/: per-run metrics, beacon packets/events, probe positions,
  ordinary cohort at4200s, supervisor events and native SUMO XML.gz mirrors.
- cap_sensitivity/: six separate60s runs; pilot/: excluded technical check.

Native outputs are complete SHA256-verified .xml.gz copies captured after SUMO
closed, with native_outputs.json. Uncompressed duplicates are not bundled.
The original matched ordinary experiment and its48 outputs remain a separate
archive; its source files and results have not been overwritten.

Extract the complete folder, install Python3.10+ and desktop SUMO1.28.0 with
sumo-gui, then open a terminal in the extracted root:

    python -m pip install -r requirements_emergency.txt
    python emergency/run_study.py --case CORRIDOR_AM --arm fixed --seed 7300 --tag replay --gui
    python emergency/run_study.py --case CORRIDOR_AM --arm local --seed 7300 --tag replay --gui
    python emergency/run_study.py --case CORRIDOR_AM --arm priority20 --seed 7300 --tag replay --gui

Commands are also provided in RUN_COMMANDS.txt. Use J1_AM/J1_PM/J2_AM/J2_PM/J3_AM/J3_PM/
CORRIDOR_AM/CORRIDOR_PM, or priority60 for the J3 sensitivity. Keep Scale Traffic
at1.0. Set SUMO_HOME to the installed SUMO directory when needed. Each GUI
viewing writes to a fresh emergency_viewings folder, preserving measured runs.
Opening a.sumocfg alone does not activate the beacon supervisor.

To inspect/reproduce the recorded experiment:

    python -m unittest discover -s emergency -p test_beacon.py -v
    python emergency/run_study.py --all --jobs 4
    python emergency/analyze.py

The runner resumes saved measurements. To execute all78 again, move
results/emergency_nov01 to a different name first and retain the delivered ZIP.
A changed policy, route, cap or input needs a separate protocol/output version.

Original source reconstruction: PASADA_SUMO_Starter.zip version5,
libfile_56ab08aaade081918dcd5522dc73300c; team manual Mandaue counts/timing study.
OSM attribution and original reconstruction/source notes are included.

Eclipse SUMO.(2026,May4).Emergency. https://sumo.dlr.de/docs/Simulation/Emergency.html
Eclipse SUMO.(n.d.).TripInfo. https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html
Federal Highway Administration.(2023).Manual on uniform traffic control devices
(11th ed.),Section4F.19. https://mutcd.fhwa.dot.gov/pdfs/11th_Edition/part4.pdf

