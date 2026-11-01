# Primary technical sources

Original sources checked 23 October 2026; installation, output, and movement-model guidance checked again 26 October 2026. The confidential user-provided thesis is referenced by page in DATA_AUDIT.md and is not bundled.

- SUMO OSM import, lane-connection guessing, and generated network limitations: https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html
- SUMO traffic-light definitions and TraCI transition handling: https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html
- SUMO fitting routes to turning/edge counts: https://sumo.dlr.de/docs/Tools/Turns.html
- SUMO demand from observations: https://eclipse.dev/sumo/docs/Demand/Routes_from_Observation_Points.html
- SUMO TripInfo definitions and unfinished trips: https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html
- SUMO sublane model: https://sumo.dlr.de/docs/Simulation/SublaneModel.html
- Espressif ESP32-C3 specifications (400 KB internal SRAM; total is not all free application RAM): https://www.espressif.com/products/socs/esp32-c3
- Espressif TensorFlow Lite Micro component, including C3 example performance: https://github.com/espressif/esp-tflite-micro
- Espressif ESP-NN, including C3 support: https://github.com/espressif/esp-nn
- ESP-DL current getting-started targets: https://docs.espressif.com/projects/esp-dl/en/latest/getting_started/readme.html
- Double DQN method, van Hasselt et al., Deep Reinforcement Learning with Double Q-learning: https://arxiv.org/abs/1509.06461
- Official Ouano Avenue naming and distinction from Don Andres Soriano Avenue: https://issuances-library.senate.gov.ph/legislative%2Bissuances/Republic%20Act%20No.%2011730

Model selection, network dimensions, decision interval, training protocol, and acceptance gates in this package are proposed engineering choices, not claims that these sources validated PASADA at these sites.

Sources for running the new scenarios:

- Official SUMO downloads, including Windows 1.28.0 installer: https://sumo.dlr.de/docs/Downloads.php
- Official SUMO GUI tutorial: https://sumo.dlr.de/docs/Tutorials/Hello_SUMO.html
- Summary output definitions, including insertion backlog: https://sumo.dlr.de/docs/Simulation/Output/Summary.html
- Class-specific edge counts and the `left` measure: https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Traffic_Measures.html
- SUMO safety-model and lane-change considerations: https://sumo.dlr.de/daily/userdoc/Simulation/Safety.html


## Refined reference methods

- Source study PDF p.73: recorded traffic reduced by 50%; the PDF remains unbundled.
- SUMO node joins and physical junction reconstruction: https://sumo.dlr.de/docs/Networks/PlainXML.html#joining_nodes
- OSM import caveats and unjoined junctions: https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html
- GUI traffic scaling: https://sumo.dlr.de/docs/SUMO-GUI.html
- Simulation scale and options: https://sumo.dlr.de/docs/sumo.html
- Collision/minGap/junction checks: https://sumo.dlr.de/docs/Simulation/Safety.html
- Motorcycle sublane modeling (not enabled in this reference): https://sumo.dlr.de/docs/Simulation/SublaneModel.html
- Output semantics: https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html and https://sumo.dlr.de/docs/Simulation/Output/Summary.html
