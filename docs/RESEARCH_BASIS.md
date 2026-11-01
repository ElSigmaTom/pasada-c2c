# Research basis · Tubaishat, Shang & Shi (2007)

## Reference and source

M. Tubaishat, Y. Shang and H. Shi, **Adaptive Traffic Light Control with Wireless Sensor Networks**, 2007 IEEE Consumer Communications and Networking Conference (CCNC), pp. 187–191. DOI: [10.1109/CCNC.2007.44](https://doi.org/10.1109/CCNC.2007.44).

Read from the user's five-page attachment `tubaishat2007(1).pdf`. Page references below use the printed proceedings pages; PDF page 1 is printed p.187. Bibliographic DOI/venue metadata was cross-checked against the DBLP record; the technical analysis is based on the attached primary paper. The publisher page could not be retrieved in this session. The original research PDF is not redistributed in the app's source ZIP.

## Why it is relevant to PASADA

The paper separates roadside wireless sensing, local intersection control and coordination among intersection agents. Figure 1 and Sections III-D / IV-A (p.189, PDF p.3) show detectors assigned to individual lanes before and after an intersection, with a nearby intersection control agent coordinating the signals. This is a useful architectural precedent for per-lane pucks and one PASADA local coordinator per intersection.

Figure 1 is a schematic, not a set of construction coordinates. It does not specify PASADA's 5, 30 and 60 m upstream offsets or validate the current Mandaue lane layout. The text uses a general distance d to allow communication and control processing. Lane counts, movement permissions and controller locations must come from the target site, not from the example figure.

## Source-to-design mapping

| Primary paper location | What it supports | PASADA action / limit |
| --- | --- | --- |
| Figure 1; Sections III-D, IV-A, p.189 | Per-lane sensing on approaches and exits; a local agent coordinates the intersection's lights. | Keep lane identity explicit, pucks under the expected vehicle path, and one local coordination authority per study intersection. Actual cabinet locations remain unlocated. |
| Section III-B, p.188 | Magnetic detection of passing vehicles; discussion of a localized vertical-axis response. | Treat as a bench-test hypothesis for MMC5603 orientation, baseline and adjacent-lane rejection. Compare all axes and vehicle types; do not assume the older sensor's results transfer. |
| Section IV-B.1, p.189 | Sensor reporting includes lane number, vehicle count and the duration over which data were collected. | Hardware telemetry should carry device/lane identity, sequence, a measurement window, passage/occupancy state and clock quality. Preserve count continuity through retransmissions and resets. The live packet transport is unfinished. |
| Section III-C, pp.188–189 | A scheduled access scheme (PEDAMACS/TDMA) addresses radio delay and energy use. | Evaluate delay, packet delivery, synchronization and energy under the actual ESP-NOW/LoRa load. ESP-NOW is not PEDAMACS; adding an RTC alone does not implement a time-slot schedule. |
| Section IV-B.3–4, p.189 | Local and neighboring intersection decisions differ; coordination is a separate behavior. | Distinguish local timing from corridor coordination and C2C monitoring. Neighbor identifiers and LoRa hardware alone are not a tested coordination algorithm. |
| Section V and Figures 3–7, pp.190–191 | GLD traffic simulation and waiting-time observations. | Use as methodological background, not Mandaue validation or a transferable percentage improvement. Produce paired calibrated SUMO runs with identical demand/seeds, consistent metrics and unfinished-vehicle counts. |

## Vehicle counts and conservation

The paper's exit detectors support observing downstream flow, but counts alone do not uniquely identify which incoming vehicle took which turn when movements mix. Movement-level attribution needs phase, route or other matching evidence. PASADA's conservation boundary also needs initial storage, moving vehicles, side-road entries/exits, missed detections and consistent time windows.

Keep the current layout requirement: **5 / 30 / 60 m upstream per incoming lane; one downstream counter per outgoing lane**. Only the selected outer upstream boundary (currently 60 m) contributes to inflow totals. Do not add the 5 m and 30 m readings to that count. They are observations of the same traffic at other stations.

## What to claim for LEAR

Use this paper in the related literature and architecture rationale. Decentralized magnetic sensing and adaptive local intersection control already have published precedent. PASADA should explain its particular combination of installation/commissioning, lane-mapped sensing, authenticated emergency-beacon handling, local recovery behavior and T.E.A.M.-oriented C2C workflow, then demonstrate what is implemented and measure its benefit. This is a contribution statement to test against other work, not proof that the combination is novel.

The paper's discussion of a 99% detection rate cites earlier work by Cheung et al.; it is not a measured accuracy result for PASADA, the MMC5603, or the current enclosure. Do not copy it into the prototype's results. No multi-year battery life, magnetic coverage or hardware performance is established by this app.
