# Clean geographic C2C view · 29 October 2026

The default C2C view now follows the flat geographic presentation in the supplied Fuente screenshot and `PASADA Fuente.7z` source. Satellite roof photography is replaced by muted, flat building footprints, dark road surfaces, lane borders and geographic place/street labels. North-up orientation, metre scale, three Mandaue study sites and T.E.A.M. branding are retained.

The Fuente exporter (`export_web_replay.py`) was reviewed for its road/building/landmark geometry pipeline. Its Fuente road network is not used as the Mandaue network. `data/mandaue-2026-10-29.osm` contains the separately retrieved Mandaue context, and `data/OSM_ATTRIBUTION.md` records its origin and license. `tools/build_vector_map.py` produces the bundled context in `dist/map-data.js`; `dist/vector-map.js` renders it on a geographic canvas beneath Leaflet's equipment overlays.

**Regional coverage correction:** Esri's Dark Gray Base and Dark Gray Reference supply a continuous online road basemap beyond the local extract. At zoom 16+ the detailed local geometry is painted only within its source extent. Outside that extent the canvas stays transparent, exposing the wider road network. Below zoom 16 the local detail canvas remains transparent throughout, so zooming out cannot cover the regional map with an opaque black rectangle. The map supports zoom levels 3–21; below 15 individual equipment and lane graphics are replaced visually by a clickable study-area label. Equipment records remain unchanged. Regional tiles need connectivity; a failed regional request is disclosed rather than silently presented as empty geography.

Provider services: `https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer` and `https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer`. Service attribution: Esri, HERE, Garmin, OpenStreetMap contributors and the GIS user community. The app conservatively uses native tiles through zoom 16 and overzooms beneath local detail at closer scales. These legacy raster services are scheduled for retirement in March 2028; replace them with a supported basemap service before then. See [Esri's migration schedule](https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/announcements/sunsetting-legacy-basemaps).

The context contains 934 mapped building footprints, 16 land/green/water shapes, 966 road/walkway ways and 278 deduplicated named places. Only features in the viewport are drawn. Street/place labels are collision filtered. These counts describe the snapshot, not a complete inventory of actual buildings or lanes.

Road widths use explicit OSM widths or lane tags where available and planning assumptions otherwise. The installation lane paths provide the lane surfaces at the three sites. Rendering never relocates the existing project, equipment, lane references or 5/30/60 m stations. Building courtyards retain mapped holes. No field survey or measured lane-width accuracy is claimed.

## Operator controls

- **Clean geometry** is the default map in C2C and Installation.
- **Satellite reference** switches the C2C background for imagery checks. Layers also offers satellite and OSM street maps in Installation.
- **Paper study corridor** is optional in Layers, keeping the default uncluttered.
- Select an intersection in the side panel to inspect it; Fit study area returns to all three. Existing puck hover/click, installer selection, equipment configuration and synthetic emergency beacon remain available.
- Two-border imagery alignment automatically opens the satellite reference. Cancelling/finishing retains the existing alignment behavior.

## SUMO boundary

This change replaces the visual map layer. It does not execute the uploaded Fuente Python scripts, replace the Mandaue model with Fuente, connect a live SUMO process, or invent individual-vehicle trajectories. Current C2C values remain explicitly synthetic or imported replay data. The Fuente screenshot's actual-run replay status does not apply to the Mandaue app.

A future georeferenced Mandaue SUMO network can supply lane polygons and live/replayed vehicles through the same geographic layer stack. It still needs actual lane/movement/TLS mapping, traffic demand and validation. The existing read-only SUMO adapter is unchanged.
