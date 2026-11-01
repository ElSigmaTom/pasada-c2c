# Recorded study results in the public demo

1 November 2026. `dist/study/` is a read-only evidence viewer. It is separate from the interactive queue-model simulation, the public traffic-data sample and actual roadside telemetry.

The reviewer can switch Traffic control / Emergency beacon, connected network / isolated site, and AM/PM. All cases retain the source tables, including unfavorable outcomes, unfinished trips and ordinary-traffic costs. Downloads contain the reviewed source tables, protocol and audit summaries plus package/member SHA-256 fingerprints. The complete native outputs/reproduction scripts stay in their original packages.

`tools/import_study_results.py` copied `manuscript_tables.json`, `protocol.json` and `audit.json` from these completed releases:

- `PASADA_Matched_SUMO_Comparison.zip`, Library identity `libfile_541c037705688191a616391a712aa3dd`: 48 reconstructed motor-only SUMO 1.28.0 runs, fixed versus existing independent local puck-score rule, seeds 7100–7102, 600 s warmup + 3,600 s study, demand factor 1.00. Primary all-demand accrued time includes not-inserted and active journeys at the common cutoff; completed-trip duration is secondary. Accrued time is a lower bound on eventual journey time. The candidate is not trained RL or a demonstrated exact max-pressure implementation.
- `PASADA_Emergency_Beacon_Comparison.zip`, Library identity `libfile_c9c5f3ab55e48191bd4c8f2ca571f725`: 72 main runs plus six predeclared 60 s cap sensitivities. Fixed / local / local+20 s beacon, seeds 7300–7302. One identical probe per arm; ideal GNSS/delivery; no blue-light exemptions. Front stop-line crossing during an active cap is not full rear clearance or clinical response time.

The importer checks the release run counts but does not rerun the studies, repeat their audits, train any model or independently certify the source claims. Reported audit counts are copied source evidence. Zero recorded collisions/teleports in these finite runs does not establish field safety. Sample SD over three paired seeds is not a confidence interval. Physical sensing/radio/security, pedestrians, competing emergency vehicles and field acceptance remain outside the demonstrated scope.

Keep `dist/study/results.json` source metadata intact when republishing. The Python/SUMO beacon experiment has its own documented implementation; its results do not establish that the browser beacon tracker has been upgraded to the same algorithm. See source protocol files in the results download for the exact experiment definitions.
