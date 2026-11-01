# AI Scratchpad reconciliation — 31 October 2026

The native sheet was re-read while editing. Another author added **Done / verified** and rows 73–86 after the initial read. Those changes are retained. Do not add a competing dropdown column or treat historical checked simulation records as new field verification. Original request rows stay unchanged; the developer response is appended with evidence and precise remaining scope.

## Requests in rows 57–64

| Request | Existing evidence | Remaining work |
| --- | --- | --- |
| Persistent coordinator alert / prefilled replacement | `dist/operations-ui.js` has a current-fault attention panel; `dist/app.js` routes a selected coordinator into Installation. | Persistent bottom-right alert with last-heartbeat age/reason and correct UNREACHABLE distinction is not implemented. Real replacement enrollment, radio/RTC and operator checks remain pending. |
| Installer map / retained time | Lane-centred geometry, device/role config, shared JSON and virtual readback exist in `dist/core.js`, `dist/app.js`, `dist/area-planner.js`. | Actual cabinet survey, approved cabinet interface/fixed-plan IDs, complete movement/phase mapping, UTC/sensor synchronization and reboot retention remain unverified. |
| Message envelope / ACK / security | `docs/INTERFACES.md`, configuration validation and host provisioning scaffold exist. | Appendix D is still a proposed wire contract; no complete ESP-NOW/LoRa binary codec, protected key/nonce enrollment or physical ACK/retry transport is demonstrated. |
| Beacon sliding window | `dist/beacons.js` and `tests/beacons.test.mjs` verify existing two-fix motion inference, freshness, sequence/session, revocation and approach matching. | The newer at-least-three-fix sliding-window/error-radius rule in row 61 is not implemented. Historical checked two-fix behavior does not complete that new request. |
| Radio capacity / 60–100 m tests | Installer peer-budget warnings retain all required pucks. | Receiver grouping and actual buried/enclosed load/range/latency tests are pending. No radio range or encrypted peer capacity is newly verified here. |
| Local policy / MARL / LoRa rollout | The deterministic queue model exercises bounded local control and synthetic fallback, not an embedded learned model. | No calibrated network MPC/MAPPO experiment, embedded inference, targeted LoRa model chunks/ACK/activation/rollback or physical cabinet handback was implemented in this revision. |
| SUMO / full Mandaue replay | `tools/sumo_adapter.py` is a read-only TraCI observation adapter with documented mappings. | Actual full-demand, calibrated connected Mandaue runs and matched evidence remain pending. No synthetic archive is relabeled as a SUMO or observed release. |

## Public data requests in rows 83–85

The new `/data/` page implements multi-intersection selection, Philippine date/time input, aggregation, paginated preview, coverage, CSV/JSON, metadata and dictionary downloads. It loads only a public aggregate fixture and does not read browser project/fleet state. This completes a bounded **synthetic download-interface** milestone, not the whole live public-archive request.

Persistent radio ingestion, approved observed releases, a server-side archive/API, optional approach filters, Parquet/GeoJSON exports and a custom hostname remain pending. Only available count fields and resolutions are offered. Detailed schema, limitations and reproducible tests are in `docs/PUBLIC_TRAFFIC_DATA.md`.

Requests 75–82 and 86 are retained as proposals. This reconciliation neither selects a final control algorithm nor authorizes a physical signal integration. The public archive is separate from local signal control; no telemetry or supervisor service was added by this UI change.
