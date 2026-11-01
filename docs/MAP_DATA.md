# Mandaue study area and placement provenance

**Display update, 29 October 2026:** the default is now the flat geographic view described in `CLEAN_GEOMETRY_VIEW.md`, inspired by the supplied Fuente source. Geographic placement is unchanged. Satellite imagery remains an optional reference, including for two-border alignment. The newer Mandaue context snapshot is in `data/` with attribution; the original planning lane derivation below remains applicable.

The selected study area is from the user-supplied **Transpo_ Signal Timing Optimization.pdf**, page 33, Figure 3.1. Its full title is *A Mathematical Model for Signal-Timing Optimization and Traffic-Flow Impact Analysis at A. Soriano Avenue Intersection*. Junction illustrations on pp.36–38 were inspected. This replaces the earlier generated Metro Colon sample.

| Paper site | App ID | Crossing | Planning reference, EPSG:4326 |
| --- | --- | --- | --- |
| 1 · A.C. Cortes Avenue | J-A | A.C. Cortes × D.M. Cortes | 10.3304625, 123.9478423 |
| 2 · D.M. Cortes Street | J-B | D.M. Cortes × C. Ouano / adjacent F. Mendoza | 10.3262472, 123.9452764 |
| 3 · A. Soriano Avenue | J-C | A. Soriano / Ouano × S.B. Cabahug | 10.3245890, 123.9413340 |

The paper reports 548.71 m for 1–2 and 596.19 m for 2–3. These are labelled **reported paper distances** in the app. The OSM paths measure approximately 552.33 m and 599.09 m; coordinates are not stretched to force agreement. The app is north-up; the paper illustration is rotated. Site 2 includes the adjacent F. Mendoza arms pictured on p.37. The small manually controlled crossing between sites 2 and 3 is a boundary influence, not a fourth modeled signalized study site (pp.33–34).

Road coordinates, names, direction and lane tags were retrieved from OpenStreetMap on October 26, 2026 using its read-only map endpoint. `dist/road-layouts.js` contains derived paths and source way/node IDs. Source data is © OpenStreetMap contributors under the [Open Database License](https://www.openstreetmap.org/copyright). Satellite tiles are separately supplied by Esri World Imagery and are not bundled. Layouts were visually reviewed against imagery.

## Vehicle-path centres

Pucks lie on individual planned lane centrelines, halfway between draft lane boundaries, beneath the expected centre of passing vehicles. The map now draws the two lane borders, not a continuous centre guide through each puck row. Borders are visible at lane-level zoom (19+); selecting a puck highlights its lane band and a short cross-section through the selected detector. The puck is the midpoint of that cross-section. Assumed widths are 2.9–3.1 m; these are not measured lane widths or validated magnetic coverage.

Every incoming lane has three pucks at 5, 30 and 60 m upstream along its path from an editable signal/stop-line proxy. Every outgoing lane has one counter, initially 10 m beyond its exit reference. The 10 m exit distance is a configurable draft choice. Dragging a puck moves its whole lane group. The lane editor adjusts reference coordinates, heading and lateral centre position while preserving upstream chainages.

Separate carriageways keep separate axes. A. Soriano's merge uses a shared road axis with asymmetric 2-in/3-out allocation, preventing opposing rows from overlapping. Two continuous incoming lanes are represented: the short turn pocket cannot be extended as an independent physical lane to 60 m. Confirm the pocket and full lane inventory before installation. Adjacent F. Mendoza arms assume one lane per direction where map tags omit counts.

| Site | Incoming lanes | Upstream pucks | Outgoing lanes / counters |
| --- | ---: | ---: | ---: |
| J-A | 10 | 30 | 10 |
| J-B | 8 | 24 | 8 |
| J-C | 8 | 24 | 10 |
| Total | 26 | 78 | 28 |

The plan has 106 pucks, three proposed controllers and one demonstration beacon (110 devices). This is not a final procurement inventory. Each site exceeds the single 17-peer draft group budget; receiver grouping and physical topology remain unresolved. Controller coordinates start null with status unlocated. Junction references remain separate; controller triangles appear only after cabinet coordinates are assigned.

## Counting boundary

Only the outer 60 m detector contributes to synthetic inflow; 5 m and 30 m detections are not added again. Each modeled exit increments one outgoing counter. The toy balance is inflow − outflow − queued storage. A real boundary must include moving vehicles, initial occupancy, lane changes, turns and side-road entries/exits. Site 2's close crossings need movement-level boundary mapping before physical conservation claims.

## Agency and saved projects

The [official Mandaue City portal](https://www.mandauecity.gov.ph/about/offices/traffic-enforcement-agency-of-mandaue) identifies the **Traffic Enforcement Agency of Mandaue (T.E.A.M.)**. The app uses a navy/gold concept theme and typographic agency wordmark, not a reproduced official seal. It does not assert endorsement, adoption, access to existing systems or a verified copy of the agency's C2C interface.

The generated Colon sample migrates only when its sample ID and all three original references match within 30 m, and it is not a calibrated or SUMO project. The previous project is retained at browser key `pasada-draft-project-v1-before-mandaue-p33` and can be downloaded from the migration notice. Custom/calibrated projects are preserved. Exports retain source records, routes and reported paper distances.

Reference: [OSM bounding-box map API](https://wiki.openstreetmap.org/wiki/API_v0.6#Retrieving_map_data_by_bounding_box:_GET_/api/0.6/map). No changes were uploaded to OpenStreetMap.

## Two-border alignment · 26 October 2026

The earlier default overlay displayed lane centrelines as continuous strokes. These looked like borders with pucks sitting on them. Those guide strokes have been removed. The two displayed borders lie half the lane width from the lane path; all 5/30/60 m stations and the downstream counter use that path as their midpoint. This display correction does not claim to have surveyed the painted road markings.

To correct a real imagery mismatch, select a puck and choose **Centre between lane borders**. The installer zooms to that detector. Click the two actual opposite lane markings, at the same cross-section beside the selected detector. The complete row moves to their midpoint and the draft width becomes the distance between the picks. Input checks reject borders less than 1.8 m or more than 6 m apart and picks that run along rather than across the lane. Existing path shape, upstream chainages, device IDs and the downstream counter rule are retained.

The two picked points and station are retained in `lane.border_alignment`, marked operator imagery picks / unsurveyed. Dragging or otherwise moving the lane clears this now-stale reference. The original project is available through the existing Undo layout action. Other lanes and cabinet coordinates do not move. One cross-section only calibrates that lane locally; it does not establish widths or border curvature everywhere. Align each lane to appropriate imagery or survey data before installation.

## Intersection picker · 26 October 2026

Installation now starts with only three selectable study crossings. Geographic hit areas and labels show the crossing name on hover, use a pointer cursor and support click/keyboard selection. Choosing a site highlights it, fits its local detector/lane geometry and reveals only that site's installation overlay. All intersections clears the overlay; it does not delete project devices. Operations continues to show the full corridor. Existing pucks and lane geometry are not changed by site selection.

Puck hover labels explicitly identify provisional planning references. Click a puck for configuration; dragging is disabled until enabled in the preview. Physical footprints use the proposed Rev B diameter of 0.123 m, with separate enlarged click markers. The scale bar follows zoom; marker size is not a magnetic detection footprint. See `DEVICE_IDENTITY.md` for the proposed identity separation and provider notes.
