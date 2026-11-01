# PASADA coordinators, roadside placement and emergency beacons

Updated October 26, 2026. This records the user's revised hardware/placement concept and the working browser demonstration. It is not a surveyed cabinet inventory or an approved signal-controller interface.

## Unit count and responsibility

| Component | Current study proposal | Responsibility |
| --- | --- | --- |
| PASADA intersection coordinator | Three: CTRL-A, CTRL-B, CTRL-C; one per modeled intersection | Receive local pucks and emergency beacons; interpret its installed lane map; run local policy and request timing/priority through an agreed cabinet interface |
| Existing traffic signal controller/cabinet | Actual models and wiring not yet identified | Existing phase/output equipment; approved fixed timing, clearance and handback interface need confirmation with T.E.A.M./vendor |
| C2C LoRa receiver/gateway | One proposed receiver, separate from the three coordinators | Bridge intersection telemetry to the operator application; USB/serial or another approved connection remains to be implemented |
| Per-pole receiver/I/O modules | Not assumed in the default | Optional distributed hardware if the approved cabinet/radio design needs it; not separate, unsynchronized phase authorities |

Four visible traffic lights do not establish four independent timing controllers. The proposal uses one local PASADA decision unit per intersection, even when many signal heads serve that crossing. For this paper's three modeled intersections that means three local units. Adding a fourth intersection would require a fourth local coordinator. A central C2C receiver is a different role, not a fourth intersection controller.

This is a proposed integration architecture. We have not established the actual wiring or number of existing T.E.A.M. cabinets. Do not identify a roadside box as a controller cabinet from imagery alone. The current ESP-NOW peer inventory also exceeds a single radio group's budget, so receiver groups/additional hardware remain unresolved. Three coordinators plus a C2C receiver is a logical arrangement, not a final procurement count.

## Hardware stack specified by the user

**ESP32-C3 Super Mini + external RTC + LoRa module**, with ESP-NOW for local pucks and emergency-beacon reception.

- ESP32-C3: local computation, installed identities/geometry and protocol processing.
- External RTC: time reference and holdover, subject to the selected RTC, backup supply and drift. The part/model and accuracy budget are not selected in this draft.
- Clock synchronization: pucks use their coordinator's time reference. A common epoch, periodic resynchronization, reboot/session handling and permitted skew must be specified. Separate RTCs do not automatically agree.
- Elapsed timing: heartbeat/freshness timers use monotonic elapsed time rather than a calendar clock that can jump when synchronized. The browser uses synthetic elapsed seconds; the serial scaffold uses `millis()` for its heartbeat.
- LoRa: proposed coordinator-to-C2C telemetry. Module, permitted radio profile, antenna arrangement, receiver/gateway, packet budget, acknowledgments and deployment-specific settings are unselected. No LoRa link is implemented.

## Cabinet position and installer behavior

`intersections[].latitude/longitude` identify the crossing and remain available for traffic geometry and emergency approach matching. They are not cabinet coordinates.

A controller with unknown location has `latitude: null`, `longitude: null`, `location_status: unlocated`. It appears in the cabinet registry, not as a green triangle in the middle of the road. The installer requires actual proposed cabinet coordinates before virtual installation. Setting a cabinet position changes that device only; junction references and all puck coordinates remain intact. Supplied coordinates stay provisional, not automatically field-verified. Clear cabinet position returns it to unlocated.

The browser migrates only the known Mandaue sample's old centre-point placeholders. Custom/explicitly positioned cabinets are preserved, and the previous browser project is backed up. Sensors remain unchanged.

Controller JSON now contains a separate `intersection_reference`, hardware requirements, `controller_site_map` with incoming lane paths, local peer IDs/coordinates and enrolled beacon IDs. Cabinet position is `location`. When unlocated, `installation_ready` is false. The browser, provisioning client and serial scaffold reject installation of that pending configuration. The full project remains exportable for planning. Updated draft readers are needed to accept null controller positions; do not fabricate coordinates for an older reader.

The serial-only scaffold accepts at most 16,384 bytes of encoded device configuration. This accommodates the preloaded map/peer registry. Arduino compilation, actual flash, RTC operation and physical radio enrollment remain unverified.

## Beacon contract and moving demonstration

Schema: `pasada.beacon/0.1.0`. Example stream: `examples/beacon-packets.ndjson`; replay: `examples/beacon-replay.json`. The examples are synthetic, not observations from the Mandaue study or MIDAS runs.

| Field | Meaning |
| --- | --- |
| `beacon_id` | Enrolled hardware/device identity, such as EV-DEMO-01 |
| `vehicle_id` | Associated vehicle label; demonstration uses AMB-DEMO-01 |
| `boot_id`, `sequence` | Session and strictly increasing packet order |
| `timestamp_s` | Send time normalized to the receiving controller's clock domain; simulation uses elapsed seconds |
| `latitude`, `longitude` | Vehicle GPS position in EPSG:4326 |
| `position_accuracy_m` | Declared horizontal error estimate; the convention must be normalized for actual receivers |
| `reported_heading_deg`, `reported_speed_mps` | Optional vehicle-reported kinematics; the demo independently derives motion from fixes |
| `emergency_active` | Explicit request state; identity/authentication must still be verified |

A unique identifier is not proof of authorization. `BeaconTracker.receive` requires caller-supplied identity verification and an enrolled ID; a field inside the packet cannot assert that verification. The browser supplies a simulated verified registry. Cryptographic enrollment, MAC-to-ID binding, replay protection across boots, revocation and a real receiver are not implemented. Session changes are rejected until the receiver establishes a fresh verified session.

The demonstration implements:

1. Validate identity, ordering, timestamps and position; reject duplicates, future/old fixes and implausible jumps.
2. Compare timestamped fixes only after movement exceeds a heuristic uncertainty threshold. Estimate speed from distance/time and heading from the displacement bearing. Stationary/jitter-only fixes cannot establish a new approach. Once an approach is reliably acquired, fresh stationary fixes can retain its bounded request while the ambulance waits; speed/ETA remain unresolved until movement is measurable.
3. Match incoming road geometry using heading and position. A valid road approach can be identified while the individual lane remains unresolved. Even the displayed geometric lane candidate uses provisional, unsurveyed lane geometry.
4. Route the request to that intersection's coordinator using its installed map. Cabinet GPS is independent of this calculation.
5. Refresh a short freshness lease within a bounded encounter window. Release on stale fixes, inactive request, passing the reference or window expiry. A failed coordinator receives no applied request. C2C loss does not stop local inference.
6. Feed the synthetic local phase model. Minimum green, full yellow/all-red and pedestrian request bounds remain active. Matching an approach does not directly command a green.

Demo assumptions: 1 Hz packets; vehicle speed 6 m/s; synthetic accuracy input 0.5 m; freshness 3 s; maximum priority window 20 s; position-jump threshold 55 m/s; maximum approach search chainage 150 m. These are demonstration gates, not field-approved radio or traffic design values. Position accuracy in the example is not a claimed GPS-module specification.

The browser's NS/EW phase groups remain idealized. Heading does not establish turning intent; an actual cabinet needs approved movement/phase bindings and, where needed, route intent. GPS can span adjacent lanes, especially near buildings. Road/lane accuracy and uncertainty gates must be validated with the selected receiver and surveyed geometry.

## Review in the app

- Operations: choose a site and use **Ambulance demo**. The blue beacon moves on the map; the sidebar shows derived speed, heading and destination. The detailed beacon panel has the latest fix, motion window, lane uncertainty, ETA and lease.
- Pause beacons, then advance time: the request becomes stale and releases.
- Installation: set a cabinet position, inspect its JSON, and run virtual readback. Clear the position to return it to unlocated. This never energizes physical signal outputs.

## Source and reference record

- `01-RESEARCH-MASTERSHEET.xlsx`, **Notes Dump B7:B15, F11**: IDs, RTC, ESP-NOW/GPS/speed/heading beacon, installer, local fallback, C2C and pedestrian intent. The user subsequently specified roadside placement and ESP32-C3 Super Mini + RTC + LoRa.
- [User's MIDAS app](https://topnotcher.duckdns.org/midas/): reviewed the paired-replay presentation and standalone one-junction demonstration. Its CSBT–Fuente model and performance results were not imported as Mandaue evidence.
- [FHWA Traffic Signal Timing Manual, §4.1.2](https://ops.fhwa.dot.gov/publications/fhwahop08024/chapter4.htm): general distinction between signal heads, local cabinet controller and central monitoring. This archived manual is background, not a statement of T.E.A.M.'s installed equipment. See also [FHWA Traffic Signal Program Handbook](https://ops.fhwa.dot.gov/publications/fhwahop23041/fhwahop23041.pdf), traffic signal control assembly, p.100.
- [GPS.gov — GPS Accuracy](https://www.gps.gov/gps-accuracy): receiver/environment limitations and adjacent-lane uncertainty.
- [Espressif ESP32-C3 system time](https://docs.espressif.com/projects/esp-idf/en/v5.5.6/esp32c3/api-reference/system/system_time.html) and [ESP Timer](https://docs.espressif.com/projects/esp-idf/en/v5.5.6/esp32c3/api-reference/system/esp_timer.html): distinguish system time, elapsed time and clock sources. The selected external RTC still needs its own component specification.
