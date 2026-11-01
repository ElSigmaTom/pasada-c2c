# PASADA technical drawings · Rev B

Supplied reference: **PASADA_Technical_Drawings_RevB.pdf**, four A3 landscape sheets, dated 21 October 2026. Added to the technical handoff on 26 October 2026. The original PDF is retained unchanged in `dist/drawings/`; the adjacent PNGs are rendered screen previews of its four pages.

## Purpose of the handoff

The Technical handoff page is a build package for the hardware/enclosure designer, firmware developer, installation team and research team. It collects the supplied drawings, software source, configuration interfaces and unfinished work so another person can continue the project. Routine monitoring happens in Control center; site/device planning happens in Installation.

Download the complete build package from that page. The package includes the original PDF, all previews, this guide, the application, tools, firmware scaffold and example configuration/replays. Export the current browser installation separately; the ZIP contains the bundled example rather than the user's browser-local edits.

## Sheet register

All dimensions below are proposed millimetres from the supplied PDF, not measured purchased parts.

| PDF page / sheet | Subject | Reference envelope / purpose |
| --- | --- | --- |
| 1 / 01 | Sensor puck / updated assembly | Ø123 body; proposed 48.5 overall including panel/adhesive; assumed Ø110 usable cavity. Internal plan, section and height stack. |
| 2 / 02 | Sensor puck / renderer handoff | Exploded arrangement and enlarged part envelopes. Use sheet 01 for assembled heights. Exploded offsets are illustrative. |
| 3 / 03 | Intersection controller | Proposed 180 × 140 × 65 body; ESP32-C3 SuperMini, RFM95W and DS3231 reference modules; reserves for protection and signal interface. |
| 4 / 04 | Emergency beacon / vehicle unit | Proposed 120 × 80 × 45 body; ESP32-C3 and GNSS reference layout; protected regulated external 5 V supply. |

## How the drawings fit the current software plan

- **Puck:** MMC5603 sensing and ESP32-C3 are the physical reference. Sheet 01 allocates a solar panel, LiPo, CN3065 charger and TPS63020 module. These are mechanical envelopes, not a verified electrical circuit or a final purchasing list. Sensor baseline, enclosure effects, power budget and closed-lid RF remain bench work. Sheet 02 excludes internal LoRa.
- **Controller/coordinator:** Sheet 03 proposes a nonmetallic sidecar beside the existing signal cabinet. The current study plan is one PASADA local unit per intersection: three local units for the three study intersections, plus a separate proposed C2C receiver/gateway. The sheet describes one unit; it does not establish the corridor quantity, cabinet coordinates or existing signal-controller interface. Cabinet locations remain unlocated in the app until supplied through Installation. No enclosure drawing creates a surveyed map position.
- **Controller power and I/O:** Sheet 03 assumes protected external regulated 12 V DC and a low-voltage supervisory interface. C5–C8 are reserved volumes, not selected products. Mains, lamp drivers, UPS and safety-interlock hardware are not included. Independent RTC/LoRa modules do not establish automatic failover, synchronization or an approved signal interface.
- **Beacon:** Sheet 04 shows GNSS and ESP-NOW with no internal battery or LoRa. It calls for an external protected regulated 5 V vehicle adapter. The browser's moving beacon is a synthetic software demonstration; the drawing does not verify live location accuracy, individual-lane classification or authenticated radio reception.
- **Road placement:** This enclosure reference does not change the current 5/30/60 m upstream detectors per incoming lane, one downstream counter per outgoing lane, or lateral placement under the expected vehicle centre. Those remain in the installation geometry and need field verification.

## Status and missing deliverables

Every sheet is explicitly **CONCEPT / NOT FOR FABRICATION**. Check actual module dimensions and usable cavity before making a carrier. Do not infer hole patterns, wire routes, pin assignments or connector cut-outs from component envelopes. The puck seals and fasteners are undetailed; controller ports/glands depend on the selected connectors; beacon input port and bracket remain unselected.

The supplied attachment is the four-page PDF only. Editable CAD, separate XYZ coordinates, dimension/source schedules, wiring schematics and a complete fabrication pack were not attached. Sheet 02 mentions additional pack information; it is not included or invented here.

Next work: measure the actual parts, complete electrical and mechanical details, bench-test sensing/power/RF, implement authenticated radios and RTC synchronization, survey the cabinet/lane positions, and agree on the cabinet interface, watchdog and handback with its technical team. The existing serial firmware is a configuration scaffold, with physical outputs disabled.

For screen review, select a sheet on Technical handoff. Open the original PDF for vector detail; print on A3 at 100% to retain its declared scale, using its scale check. Screen thumbnails are not dimensioning tools.
