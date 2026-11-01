# Data files and intake rules

`source_class_counts.csv`: transcription of Tables 4.1.1–4.1.3 on PDF pp. 53–54. Counts retain the source category labels. Date, count scope, approach, movement, and class definitions are not inferred. `source_site_totals.csv` sums the listed rows per site/window only.

`source_timing_summaries.csv`: transcription of Table 4.1.4 on pp. 54–55. These are source green/yellow/red triples, not an executable signal program. The red column is not an all-red-clearance column. No verified cycle length or phase mapping is inferred.

Files ending in `_template.csv` are empty templates, deliberately containing only headers. `vehicle_behavior_assumptions.csv` contains the uncalibrated vehicle proxies used by the first runs; `demand_settings.json` contains the stated local demand/control assumptions. Do not substitute zeros for unknown observations. Record local video times with timezone `Asia/Manila` and date, plus a known common-clock reference for corridor measurements.

| Template | One row means | Key rules |
|---|---|---|
| `turn_counts_template.csv` | One observed vehicle-class movement within an interval at one site | Identify the incoming and outgoing approach/edge; use mutually exclusive classes; specify entering-count convention. `count_vehicles` is a nonnegative integer. Do not estimate turning counts by splitting a total without marking the assumption. |
| `signal_phases_template.csv` | One stage of one observed time-of-day program | List all permitted movements/signal states, stage type, duration, order, and next stage. Use distinct green/yellow/all_red types. `offset_s` needs a common reference timestamp. Record pedestrian states and observed control overrides. |
| `field_validation_template.csv` | One independent field observation over a defined interval | Name metric, location/movement, aggregation, units, sample size, and source. Queue metres and queue vehicle counts are different metrics. |
| `link_observations_template.csv` | One observed inter-site/link interval | Count boundary entries/exits and side flows, record starting/ending storage where available, travel-time distribution, and intermediate control. Internal detector counts do not create new demand. |
| `sensor_channels_template.csv` | One planned or measured puck channel | Map sensor ID, lane/edge, offset from stop line, detection/event definitions, sample/window duration, latency/health availability, and error-evidence source. Values remain unset until supported. |

Use source evidence (video filename/timecode, survey sheet, controller export) rather than undocumented recollection. Preserve raw values separately from corrections and assumptions. Record software and network versions when mapping approaches to SUMO edges; generated IDs can change after geometry edits.

The proposed 15-minute count interval is an intake convenience, not an assertion that the source contains 15-minute data. If raw event timestamps exist, retain them and derive interval counts reproducibly. The source collection dates and any day-to-day variation still need recovery.
