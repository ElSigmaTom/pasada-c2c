# PASADA chain draft · 0.1

A working draft connecting installation planning, virtual device provisioning, a satellite C2C map, local controller behavior, synthetic experiments and SUMO replay import.

The C2C now opens on a compact map-led operator view. **Emergency fleet** registers vehicles and binds one beacon to each; **Install beacon** carries that record into configuration and virtual readback. Use a shared firmware build with unique per-vehicle configuration. Read `docs/C2C_AND_FLEET.md` for the workflow, identity contract, UI references and remaining shared-registry/security integration.

Start with `docs/IMPLEMENTATION_GUIDE.md` and `docs/CONTROLLERS_AND_BEACONS.md`. Technical drawings, firmware scaffolds and build notes remain in the source package for the development team. The operator website no longer includes a Technical handoff page. Review `docs/DRAWINGS_REVB.md` for the sheet register and open design details; the original PDF is included unchanged in `dist/drawings/`. All sheets remain concept / not for fabrication. All configuration and traffic in the bundled example is demonstration data. The map follows paper p.33: A.C. Cortes, D.M. Cortes, and A. Soriano/Ouano Avenue in Mandaue City. C2C has a T.E.A.M. concept theme. See `docs/LEAR_ALIGNMENT.md` for judging weights, dates and evidence still needed. Pucks follow individual road lane paths: 5/30/60 m upstream per incoming lane and one counter per outgoing lane. Signal references and lane widths remain provisional and editable. The map shows the two lane borders with pucks at their midpoint; **Centre between lane borders** aligns a selected row to two imagery picks. `docs/RESEARCH_BASIS.md` connects the attached Tubaishat et al. (2007) paper to the design and contribution statement.

## Run locally

Requires Python 3 for the static server; no JavaScript build or package installation is needed.

```sh
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. Keep internet access enabled for satellite tiles. The browser saves the installation locally; use Export project to move it between computers. Opening `index.html` directly as a local file does not provide the HTTP origin needed by browser modules.

## Try the chain

Installation opens **Area planner**: choose a 2 / 5 / 10 km radius (5 km by default), select a mapped signalized intersection and customize its lane-centred detector template. Save/export plans separately from the active study sites. Configured sites retains the existing three-crossing device workflow. See `docs/AREA_INSTALLATION.md` for data coverage, assumptions and the topology method.

1. Review the paper-designated Mandaue corridor. Open Installation → Lane layout to refine vehicle-path centres, signal references and lane inventory.
2. In Installation, hover and click a study crossing to reveal its local overlay. Hover pucks for provisional planning references; click a puck to configure it. Selection targets are enlarged while geometry and the scale bar use metres. Controller cabinet locations start unlocated. Enter their roadside cabinet coordinates in Installation after T.E.A.M. identifies the boxes. Align puck rows beneath the expected vehicle centre; selected lanes show draft boundaries.
3. Select a device → Install on virtual device. This saves and verifies a browser-persisted simulated device record.
4. Export project, then import it. C2C uses the same identifiers, placements and timing profiles.
5. In Control center, select “Fault, emergency & recovery” and start replay. Use 10× speed to see the complete scenario.
6. Run Experiments and inspect both policies and all three paired seeds. Export CSV/JSON.
7. Connect the actual SUMO study with `tools/sumo_adapter.py`, then import its replay JSON.

Use **Ambulance demo** in Operations for a moving 1 Hz synthetic beacon. Pause its packets to test stale-fix release. Three intersection coordinators use the proposed ESP32-C3 Super Mini + external RTC + LoRa stack; a C2C receiver is a separate role.

## Source layout

| Path | Purpose |
| --- | --- |
| `dist/` | Browser app; Leaflet bundled locally |
| `dist/drawings/` | Supplied original Rev B PDF and exact rendered sheet previews |
| `docs/DRAWINGS_REVB.md` | Drawing register, relationship to the software plan and remaining build details |
| `dist/geometry.js`, `dist/road-layouts.js`, `dist/layout-ui.js` | Road data, metre-based placement, coverage and layout editing |
| `dist/core.js` | Shared validation, device configuration and synthetic queue engine |
| `tools/sumo_adapter.py` | Read-only TraCI observer → C2C replay |
| `tools/provision.py` | Explicit file-backed simulator or serial-only configuration client |
| `tools/import_osm.py` | OSM file → SUMO network conversion wrapper |
| `firmware/pasada_serial_draft/` | ESP32-C3 serial protocol and persistent configuration scaffold |
| `examples/` | Project, device, replay and lane-mapping examples |
| `models/registry.json` | Available draft model contracts |
| `tests/` | Controller/contract tests and Python tool tests |
| `docs/` | Implementation plan, interfaces and verification record |

## Check the draft

```sh
node --test tests/*.test.mjs
python -m unittest discover -s tests -p "test_*.py" -v
node --check dist/app.js
```

The included SUMO tests use an explicit API stub. SUMO, Arduino compilation and physical hardware were unavailable in the authoring environment; they are not represented as verified.

This draft has no connection to field signal equipment, authority CCTV, LoRa radios, cloud databases or the existing calibrated study. Its built-in engine uses independent idealized four-approach junctions rather than a routed corridor. It is a functional integration draft, not measured performance evidence.

## Clean C2C geometry

The default map now uses flat Mandaue building footprints and road geometry, following the supplied Fuente reference. Satellite remains an optional reference. Read `docs/CLEAN_GEOMETRY_VIEW.md` for provenance, rendering and the separate SUMO integration boundary. Rebuild bundled context with `python tools/build_vector_map.py --osm data/mandaue-2026-10-29.osm --output dist/map-data.js`.

Clean view coverage now continues beyond the local extract using a regional Esri road basemap. Zooming out shows Metro Cebu; a study-area label returns to the detailed corridor. The local detail canvas does not cover the wider map with black. Regional context requires connectivity; see the map guide for provider lifecycle information.


## Share with LEAR judges

See [GITHUB_PAGES.md](GITHUB_PAGES.md) for the ready-to-use GitHub Pages workflow and project upload package. The public app includes a separate recorded SUMO results viewer at `study/`; the interactive C2C remains a browser queue-model demonstration. Physical firmware writing remains deferred.

## Recorded study playback

Open **Study replays** to compare the 126 original saved runs directly in C2C. See [replay scope and provenance](docs/RECORDED_REPLAYS.md), including the separate matched AM vehicle captures and video evidence limits.

Study replays support wheel zoom, drag/pinch navigation, minimap, junction focus and keyboard controls. Hover for local inspectors; comparison and detailed records open on demand.
