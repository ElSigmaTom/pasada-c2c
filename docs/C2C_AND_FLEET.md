# C2C workspace and emergency fleet · 31 October 2026

## Operator view

The primary workspace is Control center, Emergency fleet and Installation. The Control center opens on the corridor map, four summary values, a list of the three intersections, the selected intersection's phase and queues, current faults and current emergency priority. The study label is **Study area: A. SORIANO AVENUE**. Clean geometry and satellite reference remain selectable.

Engineering explanations, the event history and synthetic fault controls are inside **Details & simulation tools**. Experiments and Technical handoff sit under **Tools & reference**. Project import and export are inside **Workspace**. Removing the two survey banners does not validate the cabinet coordinates or change the detector geometry; those details remain in Installation and the handoff.

One compact source badge identifies Simulation or SUMO replay. Active faults remain visible. A quiet main screen should not conceal a loss of telemetry, fixed fallback, or a pending priority request.

The layout recommendations draw on official product descriptions of [Yunex Yutraffic Symphony](https://www.yunextraffic.com/portfolio/urban/mobility-management/yutraffic-symphony/) (map access and an action center) and [Q-Free Kinetic Signals](https://www.q-free.com/q-free-launches-kinetic-signals-one-of-the-most-powerful-and-forward-thinking-central-traffic-signal-management-systems-available/) (map status, intersection details and notifications). The resulting layout is our interpretation for PASADA, not a reproduction of either product or of T.E.A.M.'s existing software.

## Register, then install

1. Open **Emergency fleet → Register vehicle**. Enter the call sign, operating agency, class and beacon ID. A plate and a physical hardware UID are optional. The workspace generates the vehicle reference. These references are provisional, not an approved agency naming standard.
2. Registration starts **Pending**. Approval requires a reference. Pending, suspended and revoked records cannot request priority in the simulator. The browser's editable setting is not live agency authorization.
3. Choose **Install beacon** on that vehicle's record. Installation opens the matching vehicle and beacon. Download the public configuration or choose **Verify in simulator** for virtual persistence, readback and identity-retention checks.
4. Use the same firmware build for every unit, with a different configuration for each vehicle. `pasada-beacon-0.1.0` identifies the intended common profile; no compiled beacon firmware binary or GPS/radio implementation is supplied by this UI change.
5. For a simulated approach, expand **Beacon configuration** in an approved vehicle's record and choose **Test approach in simulator**. The moving beacon uses that registered vehicle/beacon pair and the existing freshness, heading, speed and bounded-request logic.

| Identity | Purpose |
| --- | --- |
| Vehicle ID | Stable registry reference for the vehicle record |
| Beacon ID | Application/radio identity of its currently assigned beacon |
| Hardware UID | Real physical-unit identifier, read during commissioning |
| Authorization | Current permission to form a priority request |
| Session and sequence | Packet freshness and replay handling within a verified identity |

One beacon may belong to only one vehicle. Vehicle IDs, beacon IDs, nonempty plates and nonempty hardware UIDs must be unique. Replacing a beacon leaves the old device in inventory but removes its authorization unless it is explicitly reassigned. The record's home service site is administrative; it does not prevent the vehicle approaching another configured crossing. New mobile beacons have no invented fixed GPS location. A marker appears when position telemetry is available.

## Integration boundary

Records and simulator authorization are saved in this browser and travel with the installation-project JSON. They are not shared automatically with other operator computers. The bundled demo ambulance remains clearly labeled as an example.

The simulation checks the registered pair as well as the existing caller-verified transport identity. Registration alone cannot authenticate a radio packet. The public profile contains no keys; protected credential enrollment, hardware attestation, a shared agency registry, operator roles, audit history and distribution of revocations to intersection controllers remain integration work. A revoked or suspended record loses simulator priority immediately, without resetting traffic queues or the scenario clock. Physical controllers require their own reliable authorization updates.

Vehicle classes are index categories. Selecting an escort or PSG class does not confer a superior priority rank. The agency must define arbitration for competing requests, request expiry and the applicable signal/pedestrian protections. The browser implementation does not actuate signals or verify live emergency status.

## Where to continue

- `dist/fleet.js`: registry validation, binding, authorization and public beacon profiles.
- `dist/fleet-ui.js`: records, registration and linked beacon setup.
- `dist/operations-ui.js`: compact operator view and current-issue summaries.
- `dist/beacons.js`: verified telemetry, freshness, motion and request eligibility.
- `docs/CONTROLLERS_AND_BEACONS.md`: roadside coordinators, positioning and transport boundaries.
- `tests/fleet.test.mjs`: identity, authorization, replacement, export and compatibility checks.
