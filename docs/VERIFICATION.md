# Verification record · PASADA draft 0.1

## Signalized intersections only and wider coverage · 31 October 2026

Installation now admits only junctions with mapped motor-road traffic-signal evidence or the three user-established signalized study sites. The all-roads mode is removed. Supported radii are 2 / 5 / 10 km, defaulting to 5 km. A new signal-centered source (OSM base 2026-10-31T09:07:04Z) retains 9,546 motor-road nodes and 2,317 ways. The compiled browser catalog contains 118 eligible groups: 12 within 2 km, 47 within 5 km and 118 within 10 km. It does not establish current signal operation, authority jurisdiction or complete field inventory.

Each mapped signal is assigned to one nearest connected junction group. Pedestrian-crossing-only tags, disconnected signal points and unsignalized road branches do not independently qualify. New-plan saving rejects a source without signal evidence. Previously saved non-signalized plans remain valid in historical project exports but are hidden from selection. Only the compact eligible catalog is loaded by the page; the larger sanitized network stays in the source package for reproducible preprocessing.

All 81 Node tests and 7 Python tool tests pass (88 total), with five new checks for strict eligibility/save rejection, pedestrian/disconnected exclusions, unique signal ownership between neighboring junctions, preservation of historical plans and expanded catalog/radius bounds. Existing detector-chainage, curve midpoint, direction, registry, controller and replay checks continue to pass. Syntax and whitespace checks pass.

Browser review confirmed the 5 km default, 47 visible eligible targets, 118 at 10 km, no P. Gomez unsignalized matches, loaded regional road tiles, and eligible-plan customization/saving (D.M. Cortes / Don G. LL. Ouano: 24 → 27 pucks after adding an incoming lane). Saved filtering listed that eligible plan. The existing A. Soriano layout still displayed 34 pucks and 8 incoming / 10 outgoing lanes. No hardware, cabinet actuation or field survey is implied.

## Area-based installation templates · 31 October 2026

76 Node tests and 7 Python tool tests pass (83 total). The nine new geometry/contract checks cover shared-node topology versus disconnected geometric crossings, connected-fragment consolidation, reverse one-way and asymmetric lane counts, curved lane centres and 5/30/60 m chainages, one counter per outgoing lane, stable planning references during customization, short-path rejection, independent saved-plan round trips and corruption rejection, metric radius filtering, and all three study mappings / buffered extract coverage. Syntax and whitespace checks pass.

The retained OSM road extract has 7,071 nodes and 1,691 public motor-road ways. Browser checks showed 146 displayed candidates at 1 km and 367 at 2 km after known compound-study deduplication, with 11 signal-tagged candidates at 1 km. These are mapping candidates, not a verified signal inventory. The selected S.B. Cabahug / P. Gomez template initially showed 16 pucks (4 incoming / 4 outgoing lanes); changing an incoming arm from one to two lanes regenerated 19 pucks (5 / 4). Width 3.4 m and reference 18 m survived save and reload. The downloaded plan retained those settings, 19 matching devices and passed standalone validation. Invalid lane pairs disabled Save; correcting both fields restored it. Numeric edits now read the whole visible settings group, so changing one-way allocation through a temporary zero-lane state does not retain an obsolete value.

Browser checks also confirmed default ID/station tooltips, optional WGS84 plus local east/north coordinates, click-through puck details at 1.70 m to each border for a 3.4 m lane, saved-plan filtering, radius and signal filters, clean/satellite switching and the existing A. Soriano study's 34-puck layout through Customize study devices. Saving does not increase the active study-intersection count. No physical positioning, detection coverage, signal locations, jurisdiction, protected enrollment or new calibrated traffic simulation is certified.

See `AREA_INSTALLATION.md` for algorithms, sources, thresholds, reference assumptions, blocked layouts, source-refresh procedure and the saved-plan schema. The earlier controller/fleet and study behavior remains covered by the full passing suite.

## Operator workspace and vehicle registry · 31 October 2026

All 67 Node tests and 7 Python tool tests pass (74 total). The nine new Node checks cover atomic registration and unchanged road geometry; identity/plate/hardware collisions; approval and exact vehicle/beacon pairing; continuing transport-verification requirements; suspension/revocation; shared firmware with distinct mobile configurations; beacon replacement; legacy installation migration; cross-site approaches and replay validation; and current fault summaries. JavaScript syntax checks pass for the app, core and new fleet/operations modules.

Browser checks confirmed registration defaults to Pending, editing to Approved requires a reference, beacon-ID search works, registration survives reload, and suspension persists. The registered test unit's Install beacon link opened the matching configuration; its download contained the matching vehicle, beacon and hardware IDs, null fixed location, a shared firmware profile and no protected keys. Virtual persistence/readback/reboot verification completed. Its approved synthetic approach produced a moving marker, its registered call sign and approximately 22 km/h in the compact priority panel. The project download retained both the registry and suspended status and passed project validation. A separately generated mobile-beacon configuration also passed the Python file-backed provisioning simulator.

The road picker still displayed 40 / 32 / 34 pucks for the three selected crossings. Disconnecting C2C raised the compact active-alert panel and reconnecting cleared it. The navy/gold map-led desktop layout, folded diagnostics, fleet-to-installation path and workspace export were inspected. A form named-property collision discovered during browser testing was repaired by reading the form's id attribute explicitly. No live agency database, credentials, physical beacon firmware/radio, cabinet actuation or calibrated Mandaue simulation was tested.

The UI reference and workflow guide is `docs/C2C_AND_FLEET.md`. The native research mastersheet received 13 dated recommendations in AI Scratchpad rows 44–56 with existing formatting preserved and content read back. The native LEAR draft received two scoped changes: registration/shared-firmware clarification in PAPER PROPER and the required fixed-plan fallback correction in IMPACT. All other paper content and prior scratchpad entries were retained.

## Automated checks completed

15 Node tests passed for the shared project contract, role-specific exports, invalid identities/lane mappings/keys, peer budgets, deterministic scenarios, paired arrivals, vehicle conservation, full intergreen stages, local sensor fallback, continuous recovery, C2C independence, modeled controller backup, bounded emergency requests, pedestrian request bounds and replay provenance/validation.

6 Python tests passed for file-backed provisioning persistence, rejecting physical-output configurations, complete SUMO mappings, rejecting TLS placeholders, observing a stubbed TraCI API and rejecting unknown TLS identities before stepping the simulation.

JavaScript syntax checks and Python compilation checks passed. The provisioning CLI was also run end to end against its explicitly file-backed simulated device. Its result reported radio verification false and physical outputs disabled.

## Browser checks completed

- Satellite imagery loaded successfully over Metro Colon with all three provisional site groups and the controller/puck overlays visible.
- Installation navigation, device selection, configuration fields and the placement editor rendered successfully.
- Virtual commissioning completed persistence, exact JSON readback, a simulated record reload and an explicit simulated-verification result.
- Project export initiated and produced a downloaded file.
- A paired experiment ran in the browser and displayed all six runs, matched arrivals, conservation checks and explicit synthetic provenance.
- The resilience scenario reached sensor timeout at 44 s and fixed fallback after complete yellow/all-red at 56 s; the other two local controllers remained adaptive.

The browser tool stalled during the subsequent file-chooser import check. Interactive project/replay import and timing-profile editing are implemented but were not fully browser-verified. Contract/replay round trips and experiment calculations were covered by the automated tests above.

## Not verified in the authoring environment

- Execution against an installed SUMO or netconvert binary; neither was available.
- The actual three study TLS/lane mappings, final study locations or surveyed device placement.
- Arduino compilation, flash, physical USB configuration, reboot retention or MMC5603 sensing.
- ESP-NOW/LoRa range, packet delivery, key enrollment or radio encryption.
- Existing traffic cabinet integration, physical signal output, real crossing clearance or live fallback/handback.
- Agency CCTV integration or a persistent multi-operator C2C backend.

Stubbed TraCI tests establish adapter data handling only. Synthetic queue/request tests establish behavior within the simplified engine only. They are not field readiness or calibrated-study results.

## Lane-layout revision 2 verification

27 Node tests passed, including 12 new geometry/layout tests. They cover exact per-lane 5/30/60 m chainages on curves, lane separation, one-way directions, one downstream counter per outgoing lane, preserving companion offsets during edits, adding a complete lane group, rejecting missing/duplicate/misaligned detectors, inflow/outflow tally consistency, missing telemetry, unresolved radio capacity, and migrating only the old generated sample. Six Python tool tests also passed (33 tests total).

Browser checks verified all three coverage rows, the lane-reference editor save path, synthetic inflow/outflow/storage balance and satellite rendering of the road-following layout. No field lane count, width, stop-line coordinate or hardware counter measurement is certified by these checks.

## Mandaue / LEAR revision 3

The supplied paper's p.33 and junction figures on pp.36–38 were inspected. All three anchors and the two connected road paths were checked against OpenStreetMap and satellite imagery. Paper distances are retained as reported values, independently of measured GIS path lengths. The earlier Colon browser checks above are historical; the current default is Mandaue.

32 Node tests and 6 Python tests pass (38 total). New checks cover the Mandaue anchors, connected corridor, sample migration/custom-study preservation, lane-centre envelope, lateral group adjustment, distinct opposing rows through the A. Soriano merge and malformed optional study geometry. Existing controller, vehicle-conservation, replay and adapter checks continue to pass. JavaScript syntax passes.

Browser checks verified the T.E.A.M. concept identity, all three Mandaue coverage rows, study-site editor and paper-layout restore, the lateral-adjustment save path, selected A. Soriano lane boundaries with 5/30/60 m labels, and the LEAR criteria/date/evidence panel. The source package and examples are regenerated with the same Mandaue defaults.

Study selection is now supplied by the user; surveyed lane/cabinet positions and actual TLS/movement mappings remain unverified. The short A. Soriano turn pocket and compound site 2 require field mapping. No actual calibrated SUMO execution, magnetic coverage, radio network, hardware or cabinet actuation was verified. The T.E.A.M. interface is a proposed concept, with no agency adoption asserted.


## Roadside coordinator and GPS beacon revision

46 Node tests and 7 Python tests pass (53 total). New checks cover explicit unlocated controllers, partial/invalid coordinates, independent cabinet versus lane geometry, placement migration, preloaded lane/peer configuration, caller-verified identities, sequence/session/freshness rejection, consecutive-fix motion, stationary and moving-away vehicles, lane uncertainty, bounded leases, waiting on an acquired approach, stale/pass-by release, C2C loss, coordinator failure and replay validation. The provisioning test rejects an unlocated controller and verifies the expanded located configuration through the file-backed simulator.

Browser checks verified zero controller triangles for unknown cabinets, three unlocated registry rows, blank cabinet fields and disabled virtual installation, cabinet-coordinate save, full expanded virtual JSON readback, and clearing back to unlocated. The temporary browser test coordinates were cleared. A 1 Hz synthetic beacon displayed 21.6 km/h, derived heading, destination CTRL-A with cabinet unassigned, and a bounded request. Pausing packets and advancing time displayed stale/released status.

The user's MIDAS app and RESEARCH MASTERSHEET Notes Dump were reviewed as context. No MIDAS performance numbers or its CSBT–Fuente geometry were represented as Mandaue evidence. RTC drivers, LoRa/ESP-NOW transport, cryptographic identity, Arduino compilation, physical flash, actual cabinet location/interface and field GPS accuracy remain unverified.


## Rev B technical handoff · 26 October 2026

Replaced the generic hardware concept sketches with the supplied four-page Rev B PDF and rendered sheet previews. Original PDF retained unchanged; the source ZIP includes that PDF, all previews and `docs/DRAWINGS_REVB.md`. The handoff now explains its audience, groups source files by build role, distinguishes browser exports from bundled examples, and lists unfinished physical integration. No controller coordinates, lane geometry, timing logic or firmware outputs were changed.

Checks: JavaScript syntax passed; the original PDF matches the supplied attachment byte-for-byte (SHA-256 `6935dd91c9f1016d27a977b45bef1792ef0450edf7e9510f382ff722efaef1bf`); static download targets exist; all 43 ZIP entries were inspected and the PDF, previews, guide and application match source. Browser review confirmed all four previews load, sheet selection and matching PDF page links, and no horizontal page overflow at the inspected desktop width. The original PDF opened and rendered in the browser at sheet 02. Automated download-event capture timed out, so download completion was not recorded through that API. These checks concern the handoff assets/UI; no hardware or traffic-performance validation is implied.


## Lane-border display and alignment · 26 October 2026

Removed the continuous lane-centre guide strokes. Each lane now has two dashed draft boundaries; the selected row is inside its lane band, with a short cross-section at the selected detector. Border geometry uses a local perpendicular at each station, including curved paths. This is a drawing correction, not a claim of surveyed pavement-marking coordinates. Existing project coordinates and cabinet locations are not automatically shifted.

Added a two-border alignment action in Installation and Operations. Two opposite imagery picks set the midpoint and width of the selected lane, translate its entire puck row, preserve the required offsets and retain unsurveyed pick provenance. In picker mode markers cannot intercept edge clicks; instruction space is reserved to prevent the map jumping between picks. Imported replay editing is rejected. Subsequent lane moves invalidate old pick provenance.

Validation: all 50 Node tests passed, including every generated puck's midpoint/half-width relationship, two-border alignment in either pick order, unchanged other lanes/cabinets, rejection without mutation, outgoing-counter alignment and exported pick provenance. JavaScript syntax passed. Browser testing confirmed a zoom-21 map view, first/second pick prompts, successful row alignment, equal half-width diagram labels, and Undo restoring the original layout. A map-zoom animation race was corrected by using nonanimated positioning for alignment. The 106-puck count and 5/30/60 m upstream plus one downstream counter per lane remain unchanged. Hardware deployment accuracy is not established.

Read all five pages of the attached Tubaishat et al. (2007) study and added source-to-design notes to Technical handoff and `RESEARCH_BASIS.md`. The paper itself is not bundled. No claim of detector accuracy, battery lifetime or performance gain was imported into PASADA results.

Final browser review also checked selected lane rows at all three study intersections and the research-basis disclosure. Installation now has a Focus lane button so the two borders and selected row can be inspected without starting calibration.


## Intersection picker and planning identities · 26 October 2026

Installation now opens on a clean study overview with three selectable crossings and no puck overlay. Hover reveals each crossing's name and a pointer cursor. Clicking an area, label or site button highlights the crossing, fits its local geographic extent and displays only its infrastructure. Keyboard Enter selection is supported. All intersections clears the displayed devices without editing project data. Operations retains the complete corridor.

Puck tooltips show the existing planning reference, road/lane, detector station and unassigned hardware-UID status. Explicit tooltip widths prevent long labels collapsing into narrow columns. Clicking opens the configurator. Dragging is disabled by default and can be enabled explicitly. Existing two-border alignment, cancellation, cabinet configuration, inventory and project settings remain accessible. `DEVICE_IDENTITY.md` records a draft separation between immutable hardware identity and installation-position labels; no ID convention has been adopted and existing IDs are retained.

Scale: latitude/longitude and metre-based lane geometry determine positions, spacing and physical footprint circles. Fractional zoom improves fitting without stretching geometry. Click symbols are enlarged and the UI says so. The proposed body diameter is 123 mm; no detection radius or field-accuracy claim is made.

Validation: all 54 Node tests passed, including selected-site filtering, local extents, unchanged project data, planning-vs-hardware identity and Google Maps coordinate URLs. Syntax passed. Browser checks confirmed: three initial selectable areas and zero pucks; actual hover name, pointer cursor and highlight; A/B/C site counts of 40/32/34 pucks with no other-site pucks; keyboard selection; area, map-label and site-button clicks; clearing; puck hover ID and configuration; identity proposal; coordinator routing; drag enable/disable with unchanged coordinates; border-picker cancellation without movement; and restoration of all 106 pucks in Operations. A Leaflet layer-initialization issue was repaired by setting the map view before attaching interactive geometry.

The selected C crossing's Google Maps link opened at 10.324589, 123.941334. The running embedded map remains Esri/OSM; Google Maps API embedding is not configured. Official Google setup documentation was checked, including its prototype demo-key option. No API key, Cloud project, billing change or access grant was created.


## Fuente-style clean geography and view switching · 29 October 2026

Reviewed the supplied Fuente screenshot and archive, including its OSM attribution, geographic network and `export_web_replay.py` road/building/landmark pipeline. The default C2C and installer now render flat Mandaue geographic geometry, using a bundled 29 October OSM snapshot and the existing installation lane paths. The Fuente network was not substituted for the study corridor. Building footprints retain mapped courtyard holes, and road widths remain tagged or provisional as documented in `CLEAN_GEOMETRY_VIEW.md` and `data/OSM_ATTRIBUTION.md`.

Clean geometry and Satellite reference buttons are available in both map views, with the OSM street alternative and optional paper corridor in Layers. The same marker coordinates, zoom and intersection selection are retained on a background switch. Imagery alignment explicitly opens satellite. Default geometry rendering uses no imagery tiles. All existing device IDs, null cabinet positions, lane paths and puck offsets remain unchanged.

Validation: 57 Node tests and 7 Python tests passed. New checks establish that all 106 pucks lie inside their rendered lane polygons, rendering leaves the project unchanged, the footprint data is closed/geographic and covers the actual Mandaue sites, and unrelated custom locations do not acquire Mandaue context. JavaScript syntax checks passed. Browser checks confirmed both backgrounds, zero raster tiles / one vector canvas in clean mode, identical equipment marker positions on switching, the 40/32/34 selected-site counts, unchanged selected C intersection on a satellite switch, the selected A and C road/lane views, the side-panel intersection focus, and the synthetic ambulance displaying 21.6 km/h with a controller/approach match over the vector map.

The visual revision does not connect a live SUMO server, run the uploaded Fuente scenario, add actual vehicle trajectories or validate field equipment locations. Telemetry remains labelled synthetic/imported.


## Continuous clean-map coverage · 29 October 2026

Corrected the fixed-extract black void. Clean geometry now includes a continuous Esri Dark Gray road/context base and labels. The local canvas is transparent below zoom 16 and clips its opaque background to its own source extent at closer zooms. The full viewport is no longer filled black above the regional basemap. Both map views now support zoom 3–21. Below zoom 15 a clickable study-area label replaces visually overlapping lane/device symbols; selecting it returns to the study corridor without changing project data. Regional tile failures show a connection warning. Satellite remains a separate background and switching preserves zoom and equipment coordinates.

Validation: 58 Node tests passed and JavaScript syntax passed. A regression check verifies that the regional layer has no local bounding-box restriction and that the local canvas issues no opaque fills at zooms 3, 10, 12, 14 and 15. Browser review verified loaded continuous roads at zooms 14, 13 and 12 across Mandaue/Cebu/Mactan, all 16 regional tiles loaded at zoom 12, switching to satellite and back at the same zoom, and the study-area button returning to zoom 16 with all 107 placed puck/beacon markers retained. The initial attempted OSM tile background returned policy-block images in this preview; it was replaced with the verified Esri provider before publication. No extra map renderer dependency was retained.

Regional services are online dependencies. The local 934-footprint snapshot remains the detailed installation context, not worldwide building coverage. Current source attribution and Esri's March 2028 legacy-service retirement are recorded in `CLEAN_GEOMETRY_VIEW.md`.


## 31 October 2026 — Public traffic-data interface

- Added the read-only `/data/` explorer and a C2C Tools & reference link. Visitors choose intersection(s), Philippine local date/time and 1/5/15/60-minute aggregation, preview paginated data, and download CSV/JSON, metadata and a dictionary. The sample is 3,240 synthetic lane-minutes for 30 October 2026 08:00–09:00 PHT; the date is an interface-test anchor, not observed traffic.
- 90 Node tests and 7 Python tests pass (97 total). Nine new public-data tests cover UTC conversion/calendar validity, half-open range/site filtering, count conservation, missing/invalid intervals versus measured zero, duplicate rejection, query bounds, allowlisted exports and CSV escaping. JavaScript syntax checks pass.
- Browser QA verified default 216 rows, J-C-only selection at 72 rows, stale-download disabling, no-data ranges, no-selection validation, 5-minute aggregation at 648 rows and pagination. Actual downloaded JSON contained only J-C with explicit synthetic provenance; CSV contained 648 public aggregate rows for three sites. Missing ranges show blank passage summaries rather than zero.
- The concurrently added AI Scratchpad checkbox and new recommendations are preserved. `docs/SCRATCHPAD_REVIEW.md` records existing versus pending evidence for rows 57–64 and 75–86.
- No field ingestion, durable archive backend, public SQL, custom DNS, observed release, new physical integration, model execution or calibrated full-demand SUMO run is claimed.


## 1 November 2026 — Saved plan to native USB chooser

- Added Area planner → Save installation plan → Install devices → individual component → Connect device. The primary action calls the browser's native Web Serial device chooser with an Espressif vendor filter. A matching USB interface does not verify board model or installed firmware.
- The user's latest clarification deliberately defers firmware development/flashing for this milestone. No new firmware source/build, flash library, board writes, readback or reboot-verification workflow is delivered. Existing firmware scaffolds are unchanged.
- 94 Node tests and 7 Python checks pass (101 total). Four new tests verify exact saved-plan device/coordinate/profile preservation, study-site mappings, chooser filtering/cancellation/unsupported-browser behavior, and no false hardware-completion status. JS syntax checks pass.
- Browser review verified Save gating, a saved 32-puck + one-coordinator site, component selection and a real downloaded U05 profile with the correct site/lane/coordinates. The HTTP preview correctly reports that USB selection requires a supported browser and HTTPS. Native device availability depends on the user's local computer; no physical board was connected or flashed in this session.
- The scratchpad's newer research/SUMO/schematic records are retained. The local-autonomy/coordination gate in row 93 is respected; no model training or implementation was started. See docs/USB_INSTALLATION.md for the simplified scope and remaining firmware boundary.


## 1 November 2026 — GitHub Pages preparation and recorded study viewer

- Added the documented GitHub Actions Pages workflow, `.nojekyll`, a GitHub-ready source ZIP exporter and the exact repository setup guide. No destination repository was supplied or created, and no GitHub-hosted deployment was claimed. The current public Site remains available.
- Imported source tables/protocols/audit summaries from the completed 48-run matched study and 78-run emergency study. Package and member hashes accompany the download. The read-only `study/` page provides case/period selection, primary all-demand and secondary completed-trip metrics, ordinary-traffic costs, cap sensitivity and unfavorable cases. It does not rerun SUMO or upgrade the browser control algorithm.
- 96 Node checks and 7 Python checks pass (103 total). Two added source-release checks cover all eight cases, fingerprints, source separation and retained unfavorable outcomes. Existing JavaScript syntax checks and `tools/check_static_site.py` pass; 55 local HTML/module/CSS references resolve under a repository prefix.
- Browser QA served the app under `/pasada-c2c/`, checked all 16 study/case/period combinations, C2C stepping to 00:10, the 47-signalized-intersection installer and the 216-row public sample preview. Actual GitHub workflow execution and the final GitHub Pages URL remain pending a repository.
- The GitHub export omits Git history, Sites identity and runtime/private workspace files. The live Site's audience is preserved. Library source packages are read-only evidence; original data, papers and completed experiments were not rewritten or rerun.


## 1 November 2026 — Completed P1 electrical handoff exposed

- Added a separate P1 electrical section ahead of the unchanged Rev B mechanical gallery: three original SVG sheet previews, original vector PDF, editable KiCad ZIP and source README/pin map. No circuit redraw or firmware work occurred.
- Original PDF SHA-256: e10bf0efad9e4f130fa2471636245c8071ae819fdb9b0dbc81a0b427a64308da. Original source ZIP SHA-256: 0bb608cf0e10a19a7ad37c7c21258d0dc2a451e1796d2745f4d2da3bcbf36dda. The deployed copies are byte-identical to the completed Library sources.
- Handoff wording now distinguishes completed schematic drafting from pending actual carrier/pin verification and physical wiring/cabinet acceptance. No full ERC, fabrication or bench verification is claimed. Scratchpad row 116's publication request is addressed; rows 99–100 remain physical integration work.

- Follow-up asset/link validation resolves 74 local HTML/module/CSS references, including literal links in generated UI templates. Browser QA under `/pasada-c2c/` loaded all three P1 SVG previews and resolved the PDF, source-package and GitHub-release links.

### Recorded study release — 1 November 2026

- 103 Node tests and 7 Python tests pass (110 total), covering 126 original run identities, source hashes, cohort balance, half-second transitions, detector lane centres, sampling without future records, and eight matched motion overlays.
- Browser QA exercised both experiments across four layouts and AM/PM (16 combinations), synchronized seeking, play/pause and captured ordinary motion. Additional seeds and the 60 s cap sensitivity are checked separately.
- All eight representative AM/7100 captures match the complete archived sensor traces, exact supervisor events and core final counts. The original 48 + 78 results remain unchanged.
- V00–V08 are H.264, 1920 × 1080 clips. V01–04 use labeled matched reproductions; V06 uses original probe traces; V05 uses the synthetic browser engine; V07/V08 are captioned actual-browser stills and profile export. The native USB dialog, physical writing and readback were not captured.
- Drive metadata verifies all nine uploaded videos, their MIME types, byte sizes and parent folder. Only owner permission was observed. Anonymous viewer access, Drive playback processing and final paper-link insertion are pending and recorded for the thesis writer in the AI Scratchpad.
- The recorded native SUMO lane/TLS/detector mapping is independent of the editable installation template. This release does not verify that template in the field.

### Interactive dark replay redesign — 1 November 2026

- 110 Node tests and 7 Python tests pass (117 total), including pointer-anchored zoom, shared-coordinate pan, pinch midpoint preservation, reversible transforms, nearest-marker selection and native-coverage bounds. Original replay assets are unchanged.
- Browser checks cover hover cards, intersection pin/focus, wheel zoom anchored to the cursor, a measured 40/25 px shared drag in both comparison panes, minimap navigation, playback and all 16 experiment/layout/period selections.
- The page uses one large dark map by default; comparison, run selection and Summary/Events/Source are on demand. Individual AM vehicle captures start at 1,200 s rather than an empty warmup. Model traffic-light heads display native signal states.
- The redesign does not add unrecorded sensor occupancy, hardware health or new measured simulation outcomes.
