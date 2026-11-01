# Mandaue geographic context

## Signalized installation catalog · 31 October 2026

The current planner uses `dist/signal-junctions.js`, compiled from `data/signal-road-network.json`. Source: https://overpass-api.de/api/interpreter, OSM base timestamp 2026-10-31T09:07:04Z, retrieved 31 October 2026. The exact query is retained in source metadata and `tools/build_signal_roads.py`: traffic-signal nodes within 10.5 km of 10.32765, 123.94465 plus complete road geometry within 200 m of those signals. Sanitized public motor-road data contains 9,546 nodes and 2,317 ways, with no contributor account metadata. Data © OpenStreetMap contributors, ODbL 1.0. Only signalized candidates are compiled for browser use. The display supports 2 / 5 / 10 km radii; the 5 km default has 47 mapped candidates. This does not define T.E.A.M. jurisdiction or certify a current signal inventory. Rebuild and matching details are in `docs/AREA_INSTALLATION.md`.

The earlier datasets below are retained for local footprints and regression/reproducibility; they are not the current signalized selection catalog.

## Installation road-network extract · 31 October 2026

`dist/road-network.json` and `dist/road-network.js` retain public motor-road topology from https://api.openstreetmap.org/api/0.6/map?bbox=123.9230,10.3060,123.9663,10.3493 (retrieved 31 October 2026). Data © OpenStreetMap contributors, ODbL 1.0. The extract supports a 2 km analysis radius about 10.32765, 123.94465, with buffer for approach tracing. It contains 7,071 retained road nodes and 1,691 ways; no OSM account metadata is retained. See `docs/AREA_INSTALLATION.md` for reproducible analysis and its limits. This dataset adds road analysis; the prior footprint dataset below is unchanged.

Data © OpenStreetMap contributors, available under ODbL 1.0.

- Source: https://api.openstreetmap.org/api/0.6/map?bbox=123.9370,10.3200,123.9535,10.3355
- Retrieved: 29 October 2026
- Attribution: https://www.openstreetmap.org/copyright
- License: https://opendatacommons.org/licenses/odbl/1-0/
- Snapshot: `mandaue-2026-10-29.osm`
- Rebuild: `python tools/build_vector_map.py --osm data/mandaue-2026-10-29.osm --output dist/map-data.js`

The supplied PASADA Fuente archive's `export_web_replay.py` was reviewed as the reference for flat geographic road, building, greenery and place-label layers. Fuente geometry was not moved or stretched into the Mandaue study area. The new context uses Mandaue OSM coordinates and the existing project's lane paths, preserving all device positions and 5/30/60 m stations.

Building polygons are mapped footprints with courtyard holes retained where available, not photographs, surveyed roof outlines or invented blocks. Road widths use OSM width/lane tags where available and explicit planning assumptions otherwise. Existing planning lanes remain the device-placement reference. Mapped context does not establish field accuracy or execute SUMO.
