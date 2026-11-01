# PASADA interfaces · 0.1

All distances are metres; timing-profile durations and replay times are seconds. Geographic coordinates are WGS84 latitude/longitude (`EPSG:4326`). The app validates public projects before accepting imports. A project file contains no private radio keys.

## Installation project

Schema: `pasada.project/0.1.0`. Authoritative examples: `examples/project.json`; implementation: `dist/core.js`, `defaultProject()` and `validateProject()`.

| Field | Meaning |
| --- | --- |
| `project.id`, `project.name` | Installation identity |
| `project.layout_provenance` | Basis and uncertainty of geographic positions |
| `provenance` | Traffic/example source; not a claim of surveyed location |
| `intersections[]` | Site IDs, coordinates, names, neighbor IDs, local model and timing profile |
| `intersections[].location_status` | `unconfirmed` or operator-declared `verified` study-site identity |
| `intersections[].lanes[]` | Physical lane IDs, flow direction, road paths and signal/exit references; actual SUMO lane IDs remain in the adapter mapping |
| `devices[]` | Unique device IDs, role, site mapping, coordinates and proposed placement; unlocated controllers use explicit null coordinates |
| `devices[].commissioning` | Planned or simulated verification state; independent of runtime heartbeat health |
| `communications` | Public channel/budget settings and proposed LoRa link |
| `security` | `mode: simulation`, `key_material_included: false` |

Validation requires one mapped controller per intersection, unique IDs, valid sensor-to-lane assignments, valid coordinates (or explicit unlocated controller status), integer timing assumptions, `min ≤ fixed ≤ max` green, a modeled service interval fitting the minimum green, a feasible request-wait bound and a heartbeat timeout spanning at least two intervals. The encrypted peer budget remains at most 17 per radio group. When `communications.provisioning_state` is `planning`, an over-budget layout remains editable and exports explicit unresolved topology status. The installer displays every capacity issue. A non-planning configuration is rejected if it exceeds the declared budget; this is not proof of physical provisioning.

The browser draft represents idealized N/E/S/W approaches. Absent or differently directed real approaches must be handled by the actual SUMO mapping and a subsequent generalized controller implementation. Re-labeling the map does not validate its synthetic junction geometry.

## Device configuration and serial protocol

`deviceConfiguration(project, id)` generates `pasada.device/0.1.0`. It includes the unique device role and references, location, optional sensor metadata, channel, timing, model, firmware version, `security_mode: simulation`, and `output_mode: serial-only`.

Commands and responses are newline-delimited JSON. Each request carries a unique `request_id`; clients match it so asynchronous heartbeats do not become configuration responses.

```json
{"request_id":"example-1","command":"get_info"}
```

```json
{"request_id":"example-1","ok":true,"protocol":"pasada.serial/0.1.0","output_mode":"serial-only","sensor_ready":false,"radio_ready":false}
```

`set_config` carries the complete configuration under `config`. `get_config` returns it under `config`. The Python client verifies semantic JSON equality. No serial command enables physical outputs, selects radio keys or actuates a signal. Reboot-retention verification is separate from immediate readback.

## Replay

Schema: `pasada.replay/0.1.0`. It embeds the installation project so a replay retains its geographic/device identities. Required traffic provenance is `source: synthetic` or `source: sumo`. The `calibrated` field is descriptive source metadata, not an assertion verified by the viewer.

`frames[]` contains strictly increasing `t` and exactly one entry per mapped intersection. Each site supplies `id`, `phase`, `mode`, four `queues` values, optional downstream values, `arrived`, `departed`, and `ped_wait_s`. Use explicit `null` for unreported cumulative flow or pedestrian request wait. `device_health` is optional; missing entries display as unreported, never online.

The viewer supports up to 20,000 frames and imports up to 25 MB. The built-in synthetic engine records its first 3,600 steps. Export an appropriately sized segment for longer real runs.

For imported SUMO runs, `SUMO_PHASE_n` is an opaque observed program index. A user-supplied `phase_labels` mapping may replace it only after actual phase semantics are checked. The observer also retains the raw `signal_state` string. It sends no TraCI signal-change commands.

## Events

Schema: `pasada.event/0.1.0`. Fields: sequence, simulation time `t`, source, event kind, intersection reference or null, human-readable message and severity. The browser exports newline-delimited JSON. Messages are escaped before display.

Key synthetic kinds: `FAULT_DETECTED`, `FALLBACK_ACTIVE`, `RECOVERY_STARTED`, `RECOVERY_READY`, `ADAPTIVE_RESTORED`, `EMERGENCY_REQUEST`, `PEDESTRIAN_REQUEST`, `C2C_DISCONNECTED`, `C2C_RECONNECTED`, `SUSTAINED_QUEUE`. SUMO observer events use `SUMO_PHASE_OBSERVED` and do not imply device health.

## Model contract

`models/registry.json` documents the available policies. Local state-machine constraints own final phase changes. A future RL plugin must produce a bounded request, report its input schema/version and model hash, and pass offline guardrail tests before any activation path is implemented. There is no arbitrary executable model upload in this draft.

## Radio and controller interface work still required

Define authenticated device enrollment, secret provisioning, loss/replacement and revocation, peer limits, channel/frequency planning, packet sequence/acknowledgment, duplicate/stale-message handling, clock synchronization and offline boot behavior. Plain public JSON imports cannot provide these mechanisms.

Specify the exact existing cabinet interface, ownership of approved fixed timings, watchdog handback and the permitted timing/phase request API. Public project topology, live secret storage and research-data export should remain separate artifacts. C2C is a management/observation client; local execution does not require a permanent central timing server.

## Road-following layout revisions 2 and 3

`intersections[].layout_revision` of 2 or 3 enables complete lane-coverage validation. Each lane has a unique ID, road/arm name, inbound/outbound `flow`, lane number, WGS84 `path`, and its first point as an editable signal or exit reference. Distances are measured as metre chainage along the lane path, including bends and lateral lane separation.

Each inbound lane has exactly three upstream pucks with `offset_m: 5, 30, 60`. Each outbound lane has exactly one counter at the site's `downstream_offset_m` (default 10 m). Generated devices include reference latitude/longitude and `alignment: lane-path`. A puck coordinate must match its path chainage within 5 cm of calculation tolerance; this is software consistency, not survey accuracy.

Replay frames may include `device_counts` and `lane_counts`, whose values must be nonnegative numbers. Only the upstream 60 m puck contributes to boundary inflow. Every modeled departure increments exactly one downstream device. Missing counter telemetry remains unreported; 5/30 m detections are not added to cumulative inflow.


## Controller placement and beacon extension

Controller `location` is independent of `intersection_reference`. An unlocated device export has `installation_ready: false` and is rejected by provisioning. `controller_site_map` preloads incoming lane paths, peer positions and enrolled beacon IDs; `hardware` records the required ESP32-C3 Super Mini, external RTC and LoRa. Encoded serial configuration limit: 16,384 bytes.

Optional replay `frames[].beacon_tracks` records validated synthetic fixes, derived kinematics, approach/lane ambiguity and the local request/freshness state. The UI never infers actual radio authentication from the unique ID. See `CONTROLLERS_AND_BEACONS.md` and the beacon examples for the complete draft contract and its limits.
