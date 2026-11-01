# PASADA · LEAR entry and evidence plan

Prepared October 26, 2026 from the supplied paper and judging mechanics. Transfer this material into the prescribed entry form, which was not included in the mechanics attachment.

## Proposed entry framing

**PASADA: lane sensing and local traffic-control coordination for Mandaue's three-intersection study corridor.**

PASADA proposes in-pavement magnetic sensing connected to local intersection controllers, an installer that assigns identities and lane locations, and a C2C view for T.E.A.M. operators. The demonstration follows A.C. Cortes → D.M. Cortes → A. Soriano/Ouano Avenue, selected on paper p.33. The intended benefit is a consistent chain from installation to local decisions and operator visibility, including degraded-mode handling. Benefits remain hypotheses until measured.

The paper's Webster/HCM/SUMO work is the research baseline, not evidence that PASADA has achieved those results. Cite the paper separately from PASADA's contribution. T.E.A.M. agency approval or adoption has not been established.

## Judging alignment

| Criterion | Weight | Available in the draft | Evidence to complete |
| --- | ---: | --- | --- |
| Disruptive | 40% | Shared lane/device identity; installer readback; local-control/C2C separation; fault demo | Compare existing offerings. Identify the unmet need and distinguish PASADA's contribution from established technologies. |
| Impact | 30% | Reproducible synthetic comparisons; passage counters; retained unfinished queues | Calibrated corridor runs with matched demand and multiple seeds: delay, queues, throughput, stops and unfinished vehicles; uncertainty. Measure energy/emissions inputs separately before claiming environmental gains. |
| Relevance | 15% | Mandaue map, proposed T.E.A.M. workflow, fault/priority handling | Operator feedback; cabinet compatibility; detection tests by vehicle class; power/enclosure checks; physical pedestrian-clearance design and maintenance plan. |
| Clarity | 10% | Traceable installation-to-operations walkthrough; visible provenance | Entry narrative and labelled demo recording. Identify every result as measured, simulated or proposed. |
| Market opportunity | 5% | Proposed municipal pilot and repeatable installation workflow | Costed BOM, pavement/installation work, receiver groups, maintenance, support, procurement route, buyer validation and supported business model. |

Disruptive and Impact account for 70% of the judging weight. Prioritize evidence of the actual contribution and measured outcomes.

## Demonstration sequence

1. Show the paper's three Mandaue sites and two reported distances. Distinguish study selection from unsurveyed device positions.
2. Show three local coordinators with unlocated roadside cabinets and a separate proposed C2C receiver. Zoom to a lane. Show the expected vehicle-path centre, lane boundaries, 5/30/60 m upstream pucks and one counter per outgoing lane. Adjust a full row sideways in the installer.
3. Run virtual installation for one device. Show identity, persistence and readback; state that no physical board or radio is connected.
4. Inspect the same exported installation in C2C. Demonstrate a moving beacon, derived heading/speed, local approach matching and stale-fix release, then fault timeout, full clearance transitions, fallback and recovery.
5. Show passage balance and a paired synthetic experiment. Explain that physical counts, moving-vehicle storage and the calibrated corridor are not connected.
6. Present the next evidence milestone: mapped SUMO replay and bench-verified sensing/controller chain.

## Deliverables and owners to assign

| Deliverable | Current artifact | Completion condition |
| --- | --- | --- |
| Study geometry | C2C, installation JSON, `MAP_DATA.md` | Survey lanes/centres, turn pocket, stop lines and cabinets; confirm compound site 2 movement mapping. |
| Installer software | Placement/configuration app; virtual readback; serial client | Real-board readback/reboot retention, authenticated pairing and receiver grouping. |
| Sensor chain | Puck concept and serial firmware scaffold | Vehicle-class/speed detection logs, missed/double counts, lateral coverage, heartbeat and power measurements. |
| Local control | Synthetic bounded policy and resilience scenarios | Calibrated network, approved phase/interface design. No physical cabinet output is implemented. |
| Operations | Satellite C2C, health/events, replay and export | T.E.A.M. workflow review, authorized feeds, operator access and persistent telemetry. |
| Evaluation | Paired synthetic seeds/scenarios; SUMO observer adapter | Run actual calibrated corridor; document seeds, demand, turns, warm-up, policies and uncertainty; retain outputs. |
| LEAR package | This brief and app | Prescribed form, eligible roster, adviser, university endorsement, novelty comparison, evidence figures and cost model. |

The 106-puck plan is not a final procurement quantity. Field lane inventory/tapers and radio grouping remain unresolved. The paper excludes pedestrian/bicycle simulation; PASADA retains the previously requested pedestrian protection as a proposed extension. A synthetic request-wait check does not establish physical crossing clearance.

## Mechanics from the attachment

| Item | Attached rule |
| --- | --- |
| Eligibility | Currently enrolled engineering students and recent engineering graduates from the second semester of SY 2025–2026 |
| University | Official approval and endorsement required |
| Team | Maximum four members and one faculty adviser |
| Entry | Prescribed format; on or before October 30, 2026 |
| Prototype | Not required; submission is considered an advantage |
| Finalists | Five; announced November 11, 2026 |
| Presentation submission | On or before November 20, 2026 |
| Final judging | November 25, 2026; Lear PETC, MEPZ 2, Lapu-Lapu City, Cebu |

No entry has been submitted and no contact with T.E.A.M., the university or organizers has been made through this draft.

## Sources

- `Transpo_ Signal Timing Optimization.pdf`: p.33/Figure 3.1 area and distances; p.34 minor-crossing scope; pp.36–38 junction illustrations; pedestrian/bicycle exclusion in its scope.
- `IO Mechanics and Criteria for Judging(3).pdf`: p.1 mechanics/dates; p.2 criteria/weights.
- [Mandaue City official T.E.A.M. page](https://www.mandauecity.gov.ph/about/offices/traffic-enforcement-agency-of-mandaue): agency name; verified October 26, 2026.
- OpenStreetMap road data and Esri imagery: see `MAP_DATA.md`. These are not an engineering survey.


## Related work added · Tubaishat et al. (2007)

See `RESEARCH_BASIS.md` for exact page/section pointers and a source-to-design mapping. The attached study supplies prior art for per-lane magnetic sensing, one local intersection control agent and coordination between agents. Avoid claiming those concepts alone as PASADA's innovation. Explain the particular implementation and installation/emergency/C2C workflow and substantiate its contribution with comparisons and measurements. The paper does not establish PASADA's detector spacing, MMC5603 detection accuracy, local field suitability or performance improvement.
