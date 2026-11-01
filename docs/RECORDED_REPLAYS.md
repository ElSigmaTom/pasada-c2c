# Recorded study playback

Open **Study replays** in C2C (`#replays`). The dark map starts at A. Soriano with individual vehicles from the matched AM capture.

- Wheel zoom follows the pointer; drag to pan. Touch pointers support pan/pinch. Arrow keys pan, +/− zoom and Home fits the study area.
- J1/J2/J3 focus controls and the minimap navigate the corridor. Zoom-out and pan limits retain the native model in view.
- Hover a puck, vehicle, signal or intersection for an in-map description. Click to pin it. Puck coordinates and lane IDs are optional geometry details; intersection cards offer Focus.
- Compare opens two views with the same camera and clock. Single-map mode gives vehicles more screen space.
- Choose replay opens all 126 runs. Runs without ordinary vehicle captures offer the available AM/7100 capture explicitly.
- Details opens Summary, Events and Source on demand. Cutoff accounting remains separate from the current replay time. There are no permanent description paragraphs or results tables below the map.

Visual direction follows the user's [MIDAS reference](https://topnotcher.duckdns.org/midas/): dark roads, distinct vehicles and visible three-lamp model signal cases. Native Mandaue geometry, detector positions, trajectories and phase data are retained. Indicator placement is schematic, not a pole or cabinet survey.

## Imported evidence

- 48 original ordinary runs: eight layout/period cases, fixed/local rule, seeds 7100–7102.
- 78 original emergency runs: 72 main runs plus six J3 cap-sensitivity runs, seeds 7300–7302. The extra pilot is excluded.
- Exact archived controller transitions, 5 s aggregate sensor traces, ordinary approach-queue observations, original final accounting and source/member SHA-256 fingerprints.
- Original 1 Hz emergency probe positions, beacon packets and events.
- Four frozen SUMO networks with native lane, movement and TLS IDs. All 46/30/42 detector instances and 118 corridor detectors remain, including side-access boundaries and shifted actual chainages. Positions are on their native lane-centre polylines within rounding tolerance.

Native junction labels refer to the SUMO signal model, not surveyed physical cabinets. Recorded study geometry is independent of the editable installation planner. Binding those different versions remains a separate commissioning/mapping task; the replay never changes the saved installation project or feeds evaluation-only fields into the local controller.

## Ordinary traffic motion

The original archives did not save ordinary-vehicle FCD trajectories. Eight observer-only AM/seed-7100 reproductions capture actual vehicle positions at 1 Hz from 1,200–2,400 s. Their **complete** sensor traces, exact signal events and core final counts match the archived originals. Original multi-seed study results are unchanged.

`dist/replays/motion-manifest.json` retains verification flags and byte hashes. Motion is shown only for those matching runs and within that capture interval. Bodies use their recorded width/length behind SUMO's front-bumper position; display interpolation occurs between successive captured points. Other runs still replay their recorded aggregate/controller channels. Individual detector occupancy and hardware health were not saved and are not manufactured.

## Files and reproduction

`dist/replays/manifest.json` indexes lazy-loaded gzip JSON runs and four plain-JSON geometries. Current Chrome/Edge supports the required `DecompressionStream`; the page reports unsupported browsers and failed reads. The site works as static hosting under a GitHub repository prefix and requires no running SUMO server for playback.

- `tools/import_recorded_replays.py`: extracts the original two result ZIPs and preserves provenance.
- `tools/capture_study_motion.py --source <LEAR_SUMO_Simulations> --output <fresh-folder> --case J3_AM --arm rule`: observer-only capture using SUMO/libsumo 1.28.0 and the unchanged frozen study inputs.
- `tools/render_replay_videos.py`: source-backed 1080p/H.264 evidence clips.
- `tools/render_browser_walkthroughs.py`: captioned actual-browser stills plus the actual exported profile. It does not invent a native USB dialog or physical write/readback.
- `tools/build_video_overview.py`: 78 s V00 montage retaining each source clip's labels and simulated clock.

Video V00–V08 links, descriptions, placeholder references and access status are maintained in the native AI Scratchpad. The user delegates insertion into the paper to their thesis writer. Uploaded files are verified by Drive metadata; upload does not establish anonymous access or completed Drive playback processing. Before external judging, set the intended viewer permissions and check playback and the final paper links while signed out.

## Evidence limits

V01–V04 show matched AM/seed-7100 motion reproductions, not historical FCD. V06 uses original J3 AM/seed-7300 probe records and retains the unfavorable 20 s priority outcome. V05 is the separate synthetic browser fault scenario (3 s yellow / 2 s all-red), while the SUMO study uses four stages and 4 s / 4 s. V07/V08 are captioned browser walkthroughs; no physical board, radio, cabinet, firmware writing or reboot retention was verified.

All cases use reconstructed demand constrained by the team's manual vehicle-class/site totals. These are motor-only simulations, not field effects or trained neural-policy results.
