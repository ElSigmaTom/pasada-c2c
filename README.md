# PASADA — C2C workspace and reproducible SUMO study

An intersection-based traffic-control research prototype for the A. Soriano Avenue study corridor in Mandaue City. This repository combines the C2C interface, installation planning, public-data explorer, recorded study playback and the sources needed to rerun the traffic experiments locally.

- **Live C2C demo:** [Open the PASADA Traffic Command Center](https://elsigmatom.github.io/pasada-c2c/)
- **Public traffic-data explorer:** https://elsigmatom.github.io/pasada-c2c/data/
- **Simulation recordings:** https://drive.google.com/drive/folders/111gF90cHlVBLqiu7t6FuT0E34uJ2aUpA?usp=sharing
- **Simulation sources and verification:** [simulations/README.md](simulations/README.md)

## View the website locally

From the repository root, with Python 3 installed:

```sh
python -m http.server 8000 --directory dist
```

Open http://localhost:8000. Internet access is needed for external map tiles. The static interface needs no JavaScript build step. Opening index.html directly does not provide the HTTP origin required by browser modules. GitHub Pages must serve the existing dist/ application; adding simulations/ does not change the site's publishing folder.

## Explore the C2C

1. **Control center:** select an intersection to inspect its phase, queue estimates, alerts and timestamped event history. Expand diagnostics for device details and boundary-passage balance.
2. **Emergency fleet:** register a vehicle, bind its beacon and review approach, motion and packet-freshness diagnostics. **Install beacon** opens the selected vehicle's configuration. The design uses a shared firmware build with distinct per-vehicle identity/configuration; vehicle registration, installation verification and priority approval are separate steps.
3. **Installation → Area planner:** choose a 2 / 5 / 10 km analysis radius (5 km by default), select a mapped signalized intersection, adjust incoming/outgoing lane rows, and save the installation plan. Each incoming lane has upstream pucks at 5, 30 and 60 m; each outgoing lane has one downstream counter. The planning count is 3 × incoming lanes + outgoing lanes.
4. **Install devices:** choose the planned component and connect its ESP32-C3 board by USB. Download the matching device profile for firmware/configuration commissioning. Save/export the plan and resume the remaining devices later. The current browser screen selects a serial interface and exports a profile; an end-to-end browser firmware writer is not included. Use the compatible firmware/toolchain and verify configuration readback and retention after reboot before accepting a physical installation.
5. **Study replays / Study results:** inspect the saved ordinary and emergency SUMO comparisons. Replays present recorded runs; new native SUMO runs use the Python instructions below.
6. **Experiments:** compare fixed/adaptive policies on matched synthetic arrival streams and seeds. Export CSV/JSON. These browser queue-model examples are separate from the measured SUMO study.
7. **Public traffic data:** choose intersections, a Philippine-time range and 1/5/15/60-minute grouping; preview and download CSV or JSON. Coverage and source metadata accompany the counts. The bundled sample archive is marked synthetic; it is not a field traffic archive. Incoming counts use the 60 m boundary, avoiding repeated counting at 5/30 m. Passage counts across multiple sites are not unique people.

Plans are saved in the browser. Use the plan export and Workspace → Export project to keep a portable copy. Surveyed stop-line, cabinet and lane references must replace provisional planning geometry before deployment. Security-head enclosure fasteners require a matching service driver held by authorized maintenance personnel; they deter casual opening without establishing theft resistance.

## Map views and installation geometry

The default **Clean geometry** view uses flat Mandaue building footprints and road surfaces, following the supplied Fuente reference. **Satellite reference** remains available for geographic inspection. Regional road context continues beyond the local extract when zooming out; external basemap and imagery providers require internet access. See [Clean C2C geometry](docs/CLEAN_GEOMETRY_VIEW.md) for provenance and the SUMO integration boundary.

In **Installation → Configured sites**, select a study crossing to reveal its proposed devices. Hover a puck for its planning reference; click it to configure it. The 5 / 30 / 60 m upstream chainages follow each individual lane path. Pucks belong at the expected vehicle centre, halfway between lane borders. **Lane layout** edits lane/signal references; **Centre between lane borders** aligns a selected row using two imagery picks. Lane widths, turn pockets and signal references require site verification.

Controller cabinets start unlocated. Enter the surveyed roadside cabinet coordinates after T.E.A.M. identifies the boxes; an intersection reference is not a cabinet position. The proposed architecture has one ESP32-C3 Super Mini + external RTC + LoRa coordinator per study intersection, plus a separate C2C receiver. The browser demonstration does not establish physical radio or cabinet operation. See [Controllers and beacons](docs/CONTROLLERS_AND_BEACONS.md) and [Device identity](docs/DEVICE_IDENTITY.md).

Browser-local workspaces are specific to each browser and site origin. To move a configured project between the original hosted site and GitHub Pages, use **Workspace → Export project**, then **Workspace → Import project / replay** at the destination. Plans and fleet records do not automatically synchronize between computers or judges.

## Recorded study playback

Open **Study replays** to compare all 126 original saved ordinary/emergency runs inside C2C. The viewer supports wheel zoom, drag/pinch navigation, a minimap, junction focus, seeking, playback speed and keyboard controls. Hover intersections, detectors or vehicles for local inspectors; comparison and detailed records open on demand.

The eight matched AM motion captures and original emergency-probe positions retain their source labels and evidence limits. See [Recorded replay scope and provenance](docs/RECORDED_REPLAYS.md). **Study results** provides the saved traffic-control and emergency-beacon tables, protocols, audits and source fingerprints. These viewers inspect completed records; native SUMO reruns follow the instructions below.

For the separate browser demonstration, use **Details & simulation tools** in Control center to select a traffic scenario, inspect event history, stop/restore a heartbeat or simulate an ambulance approach. The moving ambulance demo emits synthetic 1 Hz beacons; pausing packets tests stale-fix release. **Installation → Configured sites → Install on virtual device** exercises simulated persistence and readback. These browser functions are distinct from USB selection and physical commissioning.

## Run the SUMO simulations yourself

Install desktop **Eclipse SUMO 1.28.0**, including sumo-gui, and **Python 3.12**. Make sure `sumo --version` and `sumo-gui --version` work in the same terminal. Install the experiment's Python dependencies in a virtual environment:

```sh
python -m venv .venv
```

Activate it with `.venv\Scripts\activate` on Windows Command Prompt, `.venv\Scripts\Activate.ps1` in PowerShell, or `source .venv/bin/activate` on macOS/Linux. Then:

```sh
python -m pip install -r simulations/ordinary/requirements_comparison.txt
cd simulations/ordinary
python measurement/watch.py --case J3_AM --mode fixed --seed 7100
```

Press the green Play button in SUMO-GUI if the simulation is paused. After closing that run, show the paired PASADA control:

```sh
python measurement/watch.py --case J3_AM --mode rule --seed 7100
```

The Python runner applies the local decision rule and clearance constraints. Opening a .sumocfg file alone does not activate PASADA. Both viewing commands create fresh output folders, leaving the delivered study records intact. On Linux use a graphical desktop/session for SUMO-GUI. If the GUI binary is missing, install the desktop SUMO distribution rather than relying only on the pip package.

| Layout | AM case | PM case |
| --- | --- | --- |
| J1 — A.C. Cortes Avenue intersection | J1_AM | J1_PM |
| J2 — D.M. Cortes Street intersection | J2_AM | J2_PM |
| J3 — A. Soriano Avenue / Ouano intersection | J3_AM | J3_PM |
| Connected three-intersection network | CORRIDOR_AM | CORRIDOR_PM |

Change `--case` to inspect each isolated intersection or the connected network. Use the same case and seed when comparing policies. The connected case models vehicles travelling between sites; it does not implement a central MARL controller.

### Emergency beacon comparison

From the repository root:

```sh
cd simulations/emergency
python -m pip install -r requirements_emergency.txt
python emergency/run_study.py --case CORRIDOR_AM --arm fixed --seed 7300 --tag replay --gui
python emergency/run_study.py --case CORRIDOR_AM --arm local --seed 7300 --tag replay --gui
python emergency/run_study.py --case CORRIDOR_AM --arm priority20 --seed 7300 --tag replay --gui
```

Run these sequentially, closing each GUI before the next. `fixed` is the fixed-plan baseline; `local` uses the local PASADA rule without priority; `priority20` enables the 20 s emergency encounter cap, including clearance time. The identical probe is scheduled at simulation time 1,800 s. `priority60` belongs only to the predeclared J3_AM/J3_PM sensitivity cases. Each GUI run writes to a new emergency_viewings folder. The probe has an emergency visual shape but no red-light exemption, blue-light bypass or privileged driving shortcut.

### Verify the reported results

The full records are supplied. Analysis can be repeated without first rerunning traffic:

```sh
cd simulations/ordinary
python measurement/analyze_paired.py
```

From the repository root, separately:

```sh
cd simulations/emergency
python emergency/analyze.py
python -m unittest discover -s emergency -p test_beacon.py -v
```

And for local delay / LOS estimates:

```sh
cd simulations/los
python -m pip install -r requirements.txt
python analyze_local_delay.py
```

See [simulations/README.md](simulations/README.md) for fresh full reruns, record locations, integrity checks and interpretation. The supplied ordinary/emergency runners resume existing complete records: merely running --all over them does not execute every simulation again.

## What the study establishes

The accepted ordinary comparison uses a transparent local pressure-dependent rule, not a trained neural policy. It retains eight AM/PM cases, two controls and three seeds (48 runs). Emergency evaluation retains 72 main runs and six cap-sensitivity runs. Forty-eight passive measurement reruns add bounded junction time-loss / LOS estimates without retuning the policy. Unfavorable cases remain included; a lower delay does not necessarily change the LOS letter band.

Manual class/site counts anchor the reconstructed demand. Detailed routes, within-hour arrivals and vehicle behavior retain reconstruction assumptions. The ordinary primary metric includes completed, active and not-yet-inserted vehicles at a common cutoff. Completed-trip means and bounded local time-loss estimates answer different questions. The LOS estimate is not a formal field-calibrated HCM assessment. Do not extrapolate these model results to guaranteed commuter time savings, nationwide benefits, physical beacon performance or road-safety certification.

The public website's synthetic engine, archived native SUMO experiments and physical device commissioning each retain their source labels. No field cabinet, LoRa link, production database, CCTV connection or physical firmware write is established by the simulations. Retain the source/coverage labels and video evidence limits when presenting the project.

## Source layout

| Path | Purpose |
| --- | --- |
| `dist/` | Static C2C application, bundled Leaflet, public-data explorer and recorded study viewers |
| `dist/drawings/` | Concept engineering drawings and sheet previews |
| `dist/geometry.js`, `dist/road-layouts.js`, `dist/layout-ui.js` | Metre-based lane placement, road geometry and layout editing |
| `dist/core.js` | Shared configuration validation, virtual devices and the synthetic queue engine |
| `data/` | Bundled geographic source data and attribution |
| `examples/` | Example projects, device profiles, replays and lane mappings |
| `models/registry.json` | Draft model contracts |
| `tools/import_osm.py` | OpenStreetMap-to-SUMO conversion wrapper |
| `simulations/ordinary/` | Matched fixed/local-rule source, frozen inputs and 48 recorded runs |
| `simulations/emergency/` | Matched probe source, beacon supervisor and all 78 recorded runs |
| `simulations/los/` | Passive local-delay measurement source and 48 reruns |
| `simulations/SOURCE_INTEGRITY.json` | Delivered file hashes and recovered dependency provenance |
| `docs/` | Architecture, installation, interface and evidence notes |
| `firmware/pasada_serial_draft/` | ESP32-C3 serial/configuration scaffold |
| `tools/sumo_adapter.py` | Read-only TraCI observer for creating C2C replay data |
| `tools/provision.py` | File-backed simulator or serial configuration client |
| `tests/` | Browser-contract and Python tool tests |

Start with the [Implementation guide](docs/IMPLEMENTATION_GUIDE.md), [Area installation guide](docs/AREA_INSTALLATION.md), [C2C and fleet workflow](docs/C2C_AND_FLEET.md) and [Recorded replay guide](docs/RECORDED_REPLAYS.md).

Technical drawings, firmware scaffolds and build notes remain in the source package for the development team. The original four-sheet Rev B mechanical reference is documented in [the Rev B drawing register](docs/DRAWINGS_REVB.md); use each drawing's stated revision and verification status. Drawings remain concepts, not fabrication approvals.

The [Research basis](docs/RESEARCH_BASIS.md) connects the attached Tubaishat et al. (2007) study to the design. The [LEAR alignment notes](docs/LEAR_ALIGNMENT.md) record the competition criteria and evidence plan. These references do not substitute for PASADA's own validation.

Keep the supplied OpenStreetMap/Leaflet attribution, `OSM_ATTRIBUTION.txt` and source notes in the simulation folders. Recorded measurement archives and code are retained for verification; do not silently replace them with new or selected runs.

## Website code checks

```sh
node --test tests/*.test.mjs
python -m unittest discover -s tests -p "test_*.py" -v
node --check dist/app.js
```

These are website/tool checks; some Python adapter tests use an explicit API stub. Native SUMO analysis, experiment tests and reruns are documented separately above. These checks do not establish Arduino compilation, physical firmware writing, radio delivery or field acceptance.

## GitHub Pages publishing

The existing `.github/workflows/pages.yml` workflow verifies the website and publishes `dist/`. In the repository, use **Settings → Pages → Build and deployment → Source → GitHub Actions**. Keep the current publishing workflow/settings when adding `simulations/`; the static website does not execute native SUMO or require a live Python server.

The live demo is linked at the top. See [GitHub's publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) for the hosting setting.
