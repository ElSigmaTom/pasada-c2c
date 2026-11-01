# Source audit: what we can use now

Source: the user-provided 83-page signal-timing thesis. Page references below refer to PDF pages, which match the printed page numbers in this section. The source PDF has not been redistributed in this package.

| Source | Usable information | Limitation for PASADA |
|---|---|---|
| pp. 33–38 | Corridor diagram, photographs, junction context; reported separations 548.71 m and 596.19 m | Geometry and exact length reference points require confirmation against the survey date and OSM. |
| pp. 53–54, Tables 4.1.1–4.1.3 | One-hour AM/PM vehicle totals by source class at each site | No approach-to-exit turning matrix, within-hour variation, or synchronized recording dates in these tables. Counting scope must be confirmed. |
| pp. 54–55, Table 4.1.4 | Green/yellow/red summaries in four time windows | No complete, approach-specific baseline phase program, movement mapping, offset, or distinct all-red clearance in this summary. |
| pp. 61–63 | Optimized timings and movement sketches | Useful clues, but the displayed timing semantics do not establish an executable conflict-free cycle. |
| pp. 55–57, 65–69 | Reported simulation performance and aggregate volume-fit checks | These do not replace raw field observations, the original simulation files, or holdout validation of queues, discharge, and travel times. |

## Source numerical totals

These are arithmetic sums of the listed class rows, not new counts or reconstructed entering flows.

| Site | 07:00–08:00 | 17:00–18:00 |
|---|---:|---:|
| J1: A.C. Cortes | 8,297 | 6,208 |
| J2: D.M. Cortes | 3,580 | 4,942 |
| J3: A. Soriano / Ouano | 5,579 | 6,053 |

Do not sum all three site totals to obtain corridor vehicle demand: one vehicle may be counted at several intersections. Confirm whether counts are unique entering crossings, both entering and exiting observations, or another aggregation before generating flows. The separate source classes PUV, PUJ, and PUB need mutually exclusive definitions; retain the source labels until clarified. J1's AM motorcycle share is approximately 79.3% of the listed total, making lane use and discharge behavior material to calibration.

## Timing issues that block a faithful baseline

- Table 4.1.4 gives one green/yellow/red triple per intersection and window. For example, J1 AM is 66/4/133 s. These cannot describe every signal movement at a multi-phase junction. The arithmetic sum is not an independently verified cycle program.
- Tables on pp. 61–63 label a column “All Red,” including 21, 24, 32, and 41 s entries. On p. 60, the calculation explicitly calls the matching value ordinary red time, using `r = C_total - (g_total + yellow)`. Therefore those table values must not be copied into SUMO as whole-intersection clearance without clarification.
- On p. 62, the J1 AM greens for the four displayed movement groups total 219 s while the table gives a 73 s cycle. The groups could represent overlapping signal groups or another interpretation, but they cannot simply be entered as four sequential 73 s-cycle stages. Recover the actual phase sequence and permitted overlaps.
- The p. 51 cycle-length adjustment and p. 60 worked example need reconciliation before reuse. The worked example adds 600% to the initial value (seven times the initial cycle). The stated 90–120 s range is also described as about four minutes on p. 51. Do not carry this adjustment into the PASADA baseline by assumption.

## Network and measurement issues

The source explicitly omits the manually controlled crossing between J2 and J3 as a separate analytical junction (pp. 33–34), and describes its primary focus as A. Soriano with corridor boundary inputs. A connected simulation must revisit that omission: the crossing, loading activity, side access, queues, and pedestrian conflicts can change propagation between the main sites. Record its location and control from video/field records; do not assign an arbitrary enforcer schedule.

The J2 figure shows a staggered C. Ouano / F. Mendoza arrangement. In the imported draft, the F. Mendoza node `1108661284` remains a priority node near the C. Ouano signal. Verify whether and how it is actually controlled. J1 and J3 each comprise multiple OSM nodes grouped into generated SUMO controllers; the grouping needs a stop-line and conflict review.

The import preserves warnings about ignored turn restrictions, junction joining, turning geometry, and possible missing turning lanes. Keep the warning log and audit the study approaches before interpreting traffic results. OSM is a current snapshot; its lanes and restrictions may differ from the study's survey period.

SUMO stopped waiting time, time loss, travel time, and HCM control delay have different definitions. Do not assign HCM LOS directly from network-wide average stopped waiting time. Similarly, a network-level Little's-law estimate is not a measured approach queue in metres; peak buildup violates the simple steady-state interpretation. Measure approach queues and discharge explicitly.

## Minimum useful recovery

First choice: obtain the original `.sumocfg`, `.net.xml`, route/demand files, additional/TLS files, scripts, SUMO version, and raw field records. Audit them rather than assuming they are calibrated.

Otherwise recover time-stamped approach/movement counts by vehicle class (15-minute bins are a practical starting format; finer arrival timestamps are better), several full observed signal cycles, yellow/all-red intervals, pedestrian operation, lane/turn restrictions, queues/discharge headways, and video dates. For the connected case, add common-clock recording, signal offsets, link travel times, side-access flows, and the intermediate crossing's operation.


## Refinement addendum — 26 October 2026

PDF page 73 states that the authors reduced recorded traffic by 50% in their simulation. Full-count performance must therefore not be validated directly against their published simulation results. Current primary cases retain scale 1.0; ST50 cases use 0.5 as a declared source-load sensitivity, not an exact source-model reproduction.

Current geometry explicitly joins J1/J3 physical nodes through a preserved netconvert patch. The old import and its warnings remain available. Current local/corridor movement-class matrices are matched. Candidate signal cycles use G+Y+R conditionally; phase splits/order, offsets, all-red and boundary arrival times remain assumptions. See BASELINE_REPORT.md and audit/reference_assumptions.json for the authoritative refined scope.
