# Area-based installation planning · 31 October 2026

## Operator workflow

Installation opens **Area planner** with **traffic-light intersections only**. Choose a 2, 5 or 10 km radius around the study corridor centre (10.32765, 123.94465). The default is 5 km. Search by road name or junction ID, or show saved eligible plans. There is no all-roads selection mode. Hover a junction for its name; click its map target or list entry to preview a template. Map targets also accept Enter or Space.

The template puts 5, 30 and 60 m detectors on every incoming lane and one counter 10 m downstream on every outgoing lane. Pucks sit on the planned lane centre, halfway between the displayed borders. Lane counts, widths and the signal-reference distance can be edited per road arm. Geometry and counts update together. Hover shows the unique planning ID; click shows latitude, longitude and local X/Y. **Position details → Show coordinates on puck hover** adds those coordinates to the tooltip. Local X/Y means metres east/north of the junction; geographic coordinates are WGS84 latitude/longitude, not screen pixels.

**Save installation plan** stores a new plan in this browser's project. **Export plan** downloads the standalone `pasada.installation-plan/0.1.0` record. Workspace → Export project includes all saved plans. Saved plans reopen with their edited lane settings. They do not add intersections to the active traffic model or claim a commissioned controller. Existing study crossings keep their original geometry and edits; **Customize study devices** opens the established Configured sites workflow. Vehicle beacons remain a separate installation workspace.

## Road data and method

The expanded snapshot comes from the [OpenStreetMap Overpass API](https://overpass-api.de/api/interpreter), retrieved 31 October 2026 (OSM base timestamp 09:07:04 UTC). The exact query is retained in `tools/build_signal_roads.py` and the source metadata. It fetches `highway=traffic_signals` nodes within 10.5 km and road ways within 200 m of those signals, with complete way-node geometry. This is a signal-centered road extract, not a claim that every road inside the circle has been analyzed. The sanitized source retains 9,546 motor-road nodes and 2,317 public motor-road ways. Contributor account metadata and unrelated building/POI data are excluded. Existing clean-map footprints and the continuous regional basemap remain available.

The topology pass follows the distinction described in the [OSMnx topology documentation](https://osmnx.readthedocs.io/en/stable/getting-started.html#topology-clean-up): a shared road node can be a junction, while a geometric crossing without a shared node is not an intersection. It is not an OSMnx execution. The pass:

1. Keeps public motor-road classes and removes footways, parking/service roads and explicitly private/no-access roads.
2. Finds nodes with at least three distinct road neighbors; degree-two bends and way splits do not become junctions.
3. Consolidates branch nodes connected within 32 m, subject to a 48 m maximum cluster span. Known compound study sites are shown once each using the existing study mapping.
4. Traces outgoing road shapes, retaining curvature. At another branch it follows only a clearly straighter continuation (under 35°, with at least a 20° margin over a competing continuation). Ambiguous and short paths stop. Crossing a nearby junction is flagged for detector-attribution review.
5. Associates a `highway=traffic_signals` node only when it belongs to the junction or its connected motor-road approach within 45 m of a group node. If multiple groups could claim one signal, only the nearest connected group owns that evidence. A nearby light does not automatically qualify both intersections. A pedestrian-only `highway=crossing` / `crossing=traffic_signals` record or a disconnected signal point does not qualify a junction.
6. Reads one-way direction, reverse one-way and [OSM directional lane tags](https://wiki.openstreetmap.org/wiki/Key:lanes). Incoming and outgoing lanes are offset for right-hand traffic, including asymmetric lane counts. One-way carriageways are centred independently. Shared centre/turn lanes are not silently treated as fixed directional lanes.

Only candidates with assigned motor-road signal evidence, plus the three user-established signalized study intersections, enter the browser catalog. Current counts are **12 at 2 km, 47 at 5 km and 118 at 10 km**. They are mapped candidates, not an authority-approved current signal inventory. OSM [traffic-signal tagging](https://wiki.openstreetmap.org/wiki/Tag:highway%3Dtraffic_signals) can abstract an entire junction or individual approaches; ownership and grouping prevent duplicate signal icons from directly becoming duplicate selectable junctions. Missing or outdated map tags can omit a real signalized intersection. Confirm the inventory with the responsible authority.

`dist/signal-junctions.js` contains only the compiled eligible catalog, keeping the wider source analysis out of page startup. Search, radius changes, saved-plan filtering and selection all use the same strict eligibility filter. New plan saving also rejects a source without mapped signal evidence. Historical non-signalized plans remain valid in older project exports but stay hidden in this planner; their geometry is not deleted. The two legacy `dist/road-network.*` files retain the earlier 2 km topology fixture for regression checks and are not used for the current planner.

## Placement assumptions and limits

The default reference is 12 m outward along each road arm from its junction node. This is an editable proxy for the actual signal/stop-line location. Detector offsets are measured along the lane curve from that reference, rather than from a screen-space diagram. A mapped lane count is used where available; missing directional allocation is flagged as an assumption. Missing widths use 3.2 m per lane. The settings allow 0–8 lanes per direction, 2.2–4.5 m widths and a 0–40 m reference distance.

Templates with short, ambiguous, roundabout or reversible-lane geometry can show partial geometry but cannot be saved/exported as complete plans until the issue is resolved. They do not extrapolate a missing 60 m road segment. The algorithm cannot certify signal locations, lane markings, turn pockets, vehicle coverage, authority jurisdiction, counts across intervening side streets or installation suitability. A nearby-junction warning requires review even when all stations fit. The search circle is not a T.E.A.M. jurisdiction boundary.

Public planning IDs retain the candidate, source arm, travel direction, lane and station, for example `PUCK-OSM-…-IN-L1-U30`. They remain provisional position references. A permanent physical hardware UID, protected identity enrollment and commissioning are separate records. IDs remain stable for the same source candidate/arm/lane/station; future OSM topology edits can change the source reference and need reconciliation.

The supported radius is bounded at 10 km, not unlimited live map analysis. It can span neighboring cities. Extending coverage requires fresh signal evidence, buffered road geometry and checks of topology and jurisdiction. No public Overpass request is issued for each visitor interaction. Source attribution and ODbL terms remain in the app and dataset.

## Developer entry points

- `dist/junction-analysis.js`: topology, unique signal ownership, eligibility, lane templates and plan validation.
- `dist/area-planner.js`: eligible map targets, editor, hover IDs, coordinates, saving and exports.
- `dist/signal-junctions.js`: compiled signalized-junction catalog loaded by the browser.
- `data/signal-road-network.json`: sanitized signal-centered source network, query and coverage metadata.
- `tools/build_signal_roads.py`: sanitizes an Overpass JSON response and rejects incomplete ways/responses.
- `tools/build_signal_catalog.mjs`: analyzes the source and compiles only eligible candidates.
- `tests/signalized-installation.test.mjs`: no unsignalized selection/saving, no pedestrian-only or disconnected-light qualification, unique signal ownership, historical-plan preservation and expanded coverage.
- `tests/junction-analysis.test.mjs`: direction, chainage, midpoint, customization and geometry validation regressions.

After downloading a complete response to the documented query:

```sh
python tools/build_signal_roads.py --input /path/to/response.json --output data/signal-road-network.json
node tools/build_signal_catalog.mjs
```

Update the recorded query, date and coverage when refreshing the source. The helpers do not issue a public query for each visitor interaction. Data © OpenStreetMap contributors, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). The build package retains the sanitized network so analysis can be reproduced without another download.
