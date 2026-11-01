# PASADA · Installation to operations draft

Version 0.1 · Prepared October 26, 2026

## 1. What this draft delivers

**Technical handoff is the project’s build package.** Share it with the hardware/enclosure designer, firmware developer or installation team so they can continue the work from the same drawings, source files and configuration interfaces. It provides a four-sheet viewer and download of the supplied **Rev B technical drawings (21 October 2026)**, a complete source ZIP and a clear readiness list. The original PDF is unchanged at `dist/drawings/PASADA_Technical_Drawings_RevB.pdf`; see `DRAWINGS_REVB.md` for its sheet register and limitations. Every sheet remains **concept / not for fabrication**. Editable CAD, separate XYZ data and wiring schematics were not supplied.

The browser application connects the installer and operations views through one versioned installation project. A device ID, geographic position, lane assignment or timing-profile edit is retained when the same project is exported and imported into C2C.

C2C opens on the Mandaue study corridor selected by the user from paper p.33, with junction details on pp.36–38. It has a navy/gold T.E.A.M. concept theme, typographic agency wordmark and larger controls. It is a proposed interface for the Traffic Enforcement Agency of Mandaue, not an adopted agency system. Orange circles show upstream pucks, cyan circles downstream counters, green triangles only for controllers with assigned cabinet coordinates and a blue diamond the demonstration beacon. Device timeout is red.

| Paper number / app ID | Study crossing | Planning latitude | Planning longitude |
| --- | --- | ---: | ---: |
| 1 / J-A | A.C. Cortes × D.M. Cortes | 10.3304625 | 123.9478423 |
| 2 / J-B | D.M. Cortes × C. Ouano / adjacent F. Mendoza | 10.3262472 | 123.9452764 |
| 3 / J-C | A. Soriano / Ouano × S.B. Cabahug | 10.3245890 | 123.9413340 |

The paper reports 548.71 m for 1–2 and 596.19 m for 2–3. The road-following overlay displays those reported lengths without stretching coordinates. Site 2 follows the compound crossing on p.37. The manually controlled crossing between 2 and 3 is a boundary influence rather than a fourth signalized site. See `MAP_DATA.md` for geometry provenance and lane/taper assumptions.

Every incoming lane has 5/30/60 m upstream pucks along its planned vehicle-path centre from an editable signal reference. Every outgoing lane has one counter, initially 10 m after its exit reference. Selecting a puck shows its centreline and both lane boundaries. Widths and signal proxies remain provisional; physical magnetic coverage has not been measured.

Dragging a puck translates its entire row. Installation → Lane layout edits reference coordinates, heading, lateral centre shift and downstream distance while preserving upstream chainages. Adding a lane creates a complete detector group. Validation rejects missing, duplicated or misaligned detectors. The generated Colon sample migrates with a downloadable browser backup; custom/calibrated projects are preserved.

Read `CONTROLLERS_AND_BEACONS.md` for controller count, roadside placement, the RTC/LoRa stack and moving-beacon protocol. Cabinet locations start unknown and are never replaced with junction-centre coordinates.

Read `LEAR_ALIGNMENT.md` for the attached judging criteria, dates, entry framing, deliverables to assign and evidence still needed.

## 2. Deliverable status

| Deliverable | Implemented in this version | Remaining work |
| --- | --- | --- |
| Installer | Device batch, locations, roles, timing profiles, project validation, JSON exports | Real USB UI and authenticated radio commissioning |
| Provisioning verification | Exact virtual JSON readback and retained identity; optional SHA-256 fingerprint on secure origins | Board reboot-retention and radio pairing checks |
| C2C | Satellite/street maps, device selection, health colors, states, logs and replay controls | Agency camera feeds, operator identities and durable server telemetry |
| Local control | Synthetic per-intersection policy, intergreens, fallback/recovery, bounded emergency requests | Approved cabinet interface and physical output implementation |
| Experiments | Four synthetic scenarios, three paired seeds, CSV/JSON and conservation checks | Connect the actual calibrated SUMO experiments and statistical evaluation |
| SUMO integration | Read-only observer exports replay from supplied TLS/lane mappings | Actual study mapping and execution in an installed SUMO environment |
| Firmware | Serial protocol, persistent configuration, explicit readiness flags | MMC5603 driver, time synchronization, ESP-NOW, LoRa, authentication and local timing executor |
| Component visuals | Isometric explanatory diagrams of puck, controller and beacon | Dimensioned enclosure design and engineering/product renders |

The notes defer the physical showcase until finalist selection. This draft supports a submission-stage demonstration without representing the concept diagrams, virtual devices or synthetic engine as built hardware.

## 3. Walkthrough for a presentation

1. **Plan.** Show the paper-designated Mandaue corridor and three study names. Show the unlocated cabinet registry, then edit a cabinet only when its coordinates are known. Inspect lane-centred puck positions separately.
2. **Configure.** Select the puck, show its ID, intersection, approach, lane, location, detector function and nominal offset.
3. **Provision.** Choose Install on virtual device. The log explicitly identifies the virtual transport, persistence, exact readback and simulated reboot. No physical board is flashed.
4. **Transfer.** Export the project and import it. Inspect the same device in C2C at the same coordinates. Both screens consume the same project contract.
5. **Operate.** Run the resilience scenario. The first sensor stops reporting at 40 s, the heartbeat timeout is reached at 44 s, and the intersection requests fixed fallback. An emergency request occurs at 65 s. The sensor resumes at 90 s; after 60 s of uninterrupted healthy reporting, adaptive restoration is requested and applied at a clearance boundary.
6. **Inspect.** Select the failed device and view its log. Explain that the whole associated intersection falls back while other intersections continue independently.
7. **Disconnect.** Disconnect C2C. The received view freezes and its age increases while each local engine continues. Reconnection restores the current received state.
8. **Evaluate.** Run a paired comparison and inspect every seed, throughput, remaining queue, request-wait proxy and conservation result. The prototype reports adverse results as well as improvements.

The live simulation is paused initially. Use +10 s for repeatable presentation pacing or select 10× speed. Reset starts a new synthetic run. Importing an external replay makes its controls observational; fault and emergency injection are disabled for that imported recording.

## 4. Shared configuration

`pasada.project/0.1.0` contains project identity, provenance, intersections, device registry, public communication settings and a simulation-only security declaration. See `examples/project.json` and `INTERFACES.md`.

The public project intentionally contains no encryption keys. `esp_now_channel` and the peer budget describe a planned radio profile. LoRa remains unselected. These fields do not pair radios, select a deployment LoRa profile or create encrypted links. The installation remains in planning mode because its mapped lane coverage exceeds a single 17-peer radio group at every site. The installer reports those capacity issues and retains all required pucks; it does not silently omit lanes or claim radio readiness.

Each role-specific `pasada.device/0.1.0` export includes its own identity, project/site references, location, sensor mapping where applicable, timing profile, model and `output_mode: serial-only`. The firmware scaffold and CLI reject a physical-output configuration.

The browser installer verifies exact JSON persistence. When Web Crypto is available it also records SHA-256; on an insecure development origin it records an explicitly non-cryptographic FNV-1a fingerprint. Neither is a device authentication mechanism. Both remain virtual-record checks.

## 5. Controller behavior in the synthetic engine

The browser model has a separate local state machine for each configured junction. It uses two alternating axes, NS and EW. Each green change traverses its full yellow and all-red stages. A decision requests a transition; it cannot directly bypass the state machine.

The `pressure-v0` model is a bounded queue-pressure heuristic using idealized upstream queue and downstream occupancy. It is not a trained RL model. The map installation has 106 planning pucks: J-A has 30 upstream pucks on ten incoming lanes and ten counters; J-B has 24 upstream pucks on eight incoming lanes and eight counters; J-C has 24 upstream pucks on eight incoming lanes and ten counters. Field inventory and turn pockets need survey before procurement. The A. Soriano merge retains distinct centres for asymmetric lane allocation. Required detectors are kept despite unresolved receiver grouping. The traffic engine still uses idealized approach groups and does not estimate queues from magnetic signals.

| Condition | Draft behavior |
| --- | --- |
| Normal operation | Minimum green, pressure response and maximum-green limit apply |
| Required sensor timeout | Whole intersection requests fixed fallback; transitions retain clearance |
| Heartbeats resume | Fixed operation continues during a continuous recovery interval |
| Healthy interval completed | Adaptive restoration is requested at the next clearance boundary |
| Another timeout during recovery | Recovery interval restarts |
| Emergency request, controller alive | Requests its axis after minimum green; maximum green and request-wait checks remain active |
| PASADA controller timeout | Separate modeled cabinet executor supplies fixed operation; the dead auxiliary controller does not process priority |
| C2C connection lost | Local control continues and the received C2C view freezes |

The firmware does not yet implement this state machine. The separate cabinet executor is a simulation assumption that must be resolved with the controller vendor/technical team. The real approved fixed-plan owner, watchdog handback, emergency handling, occupied crossings and clearance timing require that interface definition.

Pedestrians are modeled as service requests rather than moving persons. The request-wait threshold and service interval are useful software constraints but do not establish physical crossing clearance, accessibility or field safety. Timing-profile numbers are draft assumptions.

Neighbor IDs are retained in the project. Routed corridor traffic, LoRa neighbor coordination, remote model deployment and model training are not implemented by the browser engine.

## 6. Evidence and experiments

Four synthetic scenarios are included: balanced arrivals, uneven demand with a reversal, a downstream blockage, and a sensor-failure/emergency/recovery sequence. Each paired experiment uses seeds 11, 42 and 93 with identical arrivals for fixed and adaptive control.

| Metric | Definition |
| --- | --- |
| Arrived | All generated vehicles entering the model queue |
| Departed | Vehicles served past the modeled stop line |
| Remaining | Vehicles still queued when the run ends |
| Queue area | Sum of queued vehicles after service at each one-second step, in vehicle-seconds |
| Mean queue | Queue area divided by elapsed simulation seconds |
| Stopped time per arrival | Queue area divided by all arrivals, including unfinished vehicles |
| Maximum pedestrian request wait | Longest time any modeled service request has waited, including pending requests |
| Conservation error | Arrived − departed − remaining; must be zero |

Stopped time per arrival is not SUMO `timeLoss`, completed-trip travel time or a field-calibrated delay estimate. Physical pucks provide detections/occupancy; deriving full queues requires a separately validated estimator. The model currently uses exact synthetic queue state. Sustained-queue alerts use an explicit demonstration rule (≥10 vehicles on an approach for 20 s), not a validated 60 m detector interpretation.

The new Boundary passage counts panel totals inflow from the 60 m boundary puck on each incoming lane and outflow from each outgoing lane's single counter. The 5 m and 30 m detectors are excluded from the inflow total to avoid triple counting. Each modeled entry/exit increments exactly one boundary counter. Conservation in this simplified model compares inflow − outflow with queued storage. A physical detection area also contains moving vehicles; real storage cannot be equated to queue length without that additional model. Synthetic counter values are generated by the engine and do not simulate radio packet loss or real detector errors.

Reuse the team's existing calibrated SUMO work rather than replacing it with these synthetic figures. Preserve its CCTV extraction, demand assumptions, network, controller version, random seeds and comparison lineage in the real experiment handoff.

## 7. Connect SUMO

SUMO is not bundled. Install it locally and expose TraCI through `SUMO_HOME/tools` or your Python environment. First export the final installation project from the app. Copy `examples/sumo_mapping.example.json` and replace all TLS and lane placeholders with actual IDs from the study.

```sh
python tools/sumo_adapter.py --sumocfg path/to/study.sumocfg \
  --mapping path/to/study-mapping.json --project path/to/PASADA_installation.json \
  --output output/study-replay.json --duration 300 --seed 42
```

The adapter makes **no signal writes**. It observes the controller already configured in the SUMO study. Import the resulting replay into C2C. Phase labels are optional; only use NS/EW labels when the actual SUMO program and lane mapping support them. Otherwise the UI displays the observed phase index with no fabricated signal indication.

Queue values are mapped lane halting counts. Departures, when exit lanes are supplied, count new vehicle IDs entering those lanes after the first-frame baseline. Arrival counts, pedestrian request waits and physical device health remain unreported. A replay import does not turn missing health into online status. Calibration metadata is copied from the supplied mapping and explicitly identified as user-declared.

For a new OSM geometry export:

```sh
python tools/import_osm.py --osm study-area.osm.xml --output output/study.net.xml
```

Geometry import does not establish traffic demand, turning proportions, controller phases or calibration. Inspect road directions, lane permissions, crossings and TLS mapping in SUMO/netedit. The OSM wrapper does not overwrite or modify the existing study unless you explicitly select that output path.

## 8. Physical-device path

The ESP32-C3 firmware scaffold is `firmware/pasada_serial_draft/pasada_serial_draft.ino`. Open it in Arduino IDE with Arduino-ESP32 board support and ArduinoJson 7. Select the actual ESP32-C3 board and appropriate USB CDC setting for the module. The draft was not compiled or flashed in the authoring environment.

It implements newline-delimited JSON `get_info`, `set_config` and `get_config` commands. Configuration is stored through ESP32 Preferences and loaded at boot. Heartbeats identify uptime, sequence and explicit `sensor_ready: false`, `radio_ready: false`, `clock_synchronized: false`, and `physical_outputs_enabled: false`. Uptime is not presented as a synchronized Unix timestamp.

Test the local file-backed simulator first:

```sh
python tools/provision.py --simulate --config examples/device.json --store output/virtual-devices.json
```

After compiling and installing the serial scaffold yourself, install `pyserial` in your local environment and use the actual port:

```sh
python tools/provision.py --port COM5 --config examples/device.json
```

This verifies live serial identity and exact configuration readback. It does not claim reboot retention or radio verification. Reboot the board and repeat `get_config` before recording that separate test as passed. The optional `--flash` argument accepts an explicitly supplied merged ESP32-C3 image; the correct image/address remain the firmware builder's responsibility. The browser UI does not invoke it.

Before a physical demonstration, implement and bench-check the MMC5603 driver/baseline/hysteresis, actual ESP32-C3 pin assignments, power assembly, antenna/enclosure behavior, heartbeat power budget, radio peer/key provisioning and time synchronization. The current components list includes changing charger selections and older annotations; reconcile it against the actual purchased modules and the Rev B planning envelopes rather than inferring wiring from this software draft. Rev B sheet 03 shows the proposed nonmetallic sidecar beside the existing cabinet; it does not establish cabinet coordinates or an approved signal interface. Its RFM95W and DS3231 reference geometry does not finalize the electrical design or bill of materials.

## 9. Verification and next release

The draft includes Node tests for identities, schemas, paired demand, conservation, phase clearance, sensor timeouts, continuous recovery, emergency constraints, pedestrian request bounds, C2C loss and replay provenance. Python tests cover provisioning persistence, rejecting physical outputs, complete lane mappings and observing a stubbed TraCI API.

Browser verification covers satellite rendering, virtual commissioning, navigation, replay controls, paired comparison and configuration forms. See `VERIFICATION.md` for the actual completed record. Stubbed tests do not establish a working connection to an installed SUMO engine or physical hardware.

The next implementation release should survey cabinet locations and lane inventory, import the actual calibrated Mandaue study, and agree on the existing cabinet interface. After that, implement sensor firmware and authenticated radio provisioning, then test actual fallback/handback with the appropriate technical team. Government data publication and authority CCTV integration require their own interfaces and access; they are not claimed by this draft.

## 10. Source pointers

- Research requirements: RESEARCH MASTERSHEET, `Notes Dump!B7:C15`, `A16`, and its hardware sheet/annotations. The workbook was read without modification.
- [Espressif ESP-NOW API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/network/esp_now.html): Security, Add Paired Device, Send ESP-NOW Data. Defines peer/channel/key requirements and the distinction between MAC delivery and application receipt.
- [Espressif esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32c3/): flashing, provisioning, chip information and verification.
- [SUMO TraCI traffic-light retrieval](https://sumo.dlr.de/docs/TraCI/Traffic_Lights_Value_Retrieval.html): phase/program/signal observation.
- [SUMO TripInfo](https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html): waiting/time-loss definitions for real study results.
- [SUMO pedestrians](https://sumo.dlr.de/docs/Simulation/Pedestrians.html): sidewalks, crossings and walking areas for physical pedestrian simulation.
- [SUMO OSM import](https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html): network conversion and typemap considerations.
- [Leaflet reference](https://leafletjs.com/reference.html): geographic map, markers, dragging, tile layers and attribution. Bundled Leaflet 1.9.4 retains its license under `dist/vendor/`.
- Satellite service: ArcGIS World Imagery. Displayed service attribution: Esri, Vantor, Earthstar Geographics and the GIS User Community. Imagery is not real-time traffic footage. No imagery tiles are bundled or downloaded in bulk.

## Lane-layout correction · revision 2

The original sample used shared diagonal bearings and one upstream detector per approach. That layout has been replaced by individual road-following lane paths, separate inbound/outbound flow directions, and full per-lane coverage. Original saved sample projects are migrated automatically once, retaining a browser backup. Custom projects and archived replay geometry are not silently replaced.

Geometry uses mapped signal/crossing references, not surveyed signal-pole positions. Incoming lane references and outgoing exit references are independently editable. See `MAP_DATA.md` for provenance and `tests/geometry.test.mjs` for distance, completeness, direction, migration and counter checks.


## Lane borders and research reference · 26 October 2026

Map strokes now represent the two lane borders, with the puck halfway between them. The earlier continuous centre guides have been removed. Select a puck and use **Centre between lane borders** to align its complete row to two opposite imagery picks. Width and midpoint update together; 5/30/60 m chainages and one exit counter per lane are retained. Picks remain unsurveyed, and a single cross-section does not calibrate the full curved lane. See `MAP_DATA.md` for input checks and retained provenance.

The Technical handoff includes a source-to-design note for the attached Tubaishat, Shang & Shi (2007) study. Read `RESEARCH_BASIS.md` for page pointers, applicability and limits. Its architecture is related work, not PASADA test results.


## Installation picker and provisional identity · 26 October 2026

Open Installation, hover one of the three study intersections and click its area, map label or site button. The app highlights that crossing, fits the local metre-based geometry and shows its planned pucks. Hover a puck for its planning reference; click it to open the configuration panel. Use All intersections to return to the corridor picker. Selection alone does not change the project or provision hardware. Device dragging is an explicit preview option. Existing coordinate and two-border alignment controls remain available after selecting a device.

The UI distinguishes temporary planning references from permanent hardware UIDs. Read `DEVICE_IDENTITY.md` before designing enrollment and the device registry. The example position-label format is a proposal; no final UID convention has been adopted or silently applied. Google Maps opens externally at the selected crossing; the embedded map currently remains the existing Esri/OSM implementation.
