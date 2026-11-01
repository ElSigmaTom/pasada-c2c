# PASADA wiring schematics - prototype revision P1

Prepared 31 October 2026. Three separate native KiCad 7 schematics, manually routed,
with monochrome vector PDF sheets and editable color SVG exports. These are electrical
schematics, not physical placement or enclosure drawings. No image generation was used.

## Open the drawings

Open any file in `kicad/` using KiCad's Schematic Editor. Symbols are embedded in each
file, including module-specific symbols, so no additional symbol-library installation is
needed to view the drawings. The three assemblies are separate circuits with separate
microcontrollers. A simultaneous three-device demonstrator requires one C3 board per assembly.

- `01_sensor_puck.kicad_sch`: solar, charger, protected battery, buck-boost, MCU and magnetometer.
- `02_emergency_beacon.kicad_sch`: USB-powered MCU, GPS UART, enable contact and status LED.
- `03_intersection_coordinator.kicad_sch`: USB-powered MCU, RTC/coin cell, LoRa, RF supply and logic service port.

The PDF is sized for A3 landscape. Zoom freely; it contains vector lines and text.
SVGs retain a conventional colored schematic appearance. Dots connect branches;
crossing wires without a dot do not connect. Identical net labels connect within an assembly.
An X at a pin means deliberately unconnected. DNP means do not populate unless the stated
condition is met. The run link JP101 is a removable two-pin header/shunt.

## Confirmed core and proposed additions

The puck follows the current selected hardware: ESP32-C3 SuperMini, PCBfun MMC5603
carrier, CN3065 solar-charge carrier, TPS63020 carrier set to 3.3 V, conventional 1S LiPo,
optional common-port protection and the SS12D06 enable-control switch. It does not use
the older BQ25185/Adafruit 6092 charger notes still present elsewhere in the sheet.

You authorized proposing the missing prototype parts. These choices are shown explicitly:

| Assembly | Proposed part / power arrangement |
| --- | --- |
| Beacon | Adafruit Ultimate GPS v3 breakout #746, UART version with nine-pin JP1; regulated 5 V through the MCU's onboard USB-C. |
| Coordinator | DS3231SN in SOIC-16 on a passive SOIC adapter, CR2032 backup, AP2112K-3.3 in SOT25/SOT-23-5 on a suitable carrier, regulated USB 5 V. |
| Coordinator interface | Four-pin 3.3 V logic UART service/gateway connector only. No existing traffic cabinet terminal allocation has been assumed. |

The added resistors, LED, 1 uF regulator ceramics and run jumper are engineering support
parts, not claims that they are already owned or included in the original order.
The CSV lists parts per assembly. RF band and antenna selection remain open.

## MCU pin assignments

These are explicit firmware assignments, not assumptions about a library's default pins.
ESP32-C3 peripherals must be initialized with the GPIO matrix mappings below.

| Assembly | MCU GPIO | Connected terminal / function |
| --- | --- | --- |
| Puck U104 | 6 | U105 SDA |
| Puck U104 | 7 | U105 SCL |
| Beacon U201 | 20 / UART RX | GPS JP1 pin 5, TX |
| Beacon U201 | 21 / UART TX | GPS JP1 pin 4, RX |
| Beacon U201 | 0 | Active-low emergency-enable contact, 10 k pullup and 100 nF filter |
| Beacon U201 | 3 | Status LED through 1 k resistor |
| Coordinator U301 | 0 / SDA | DS3231SN pad 15 |
| Coordinator U301 | 1 / SCL | DS3231SN pad 16 |
| Coordinator U301 | 5 / SCK | RFM95W pad 4 |
| Coordinator U301 | 6 / MOSI | RFM95W pad 3 |
| Coordinator U301 | 7 / MISO | RFM95W pad 2 |
| Coordinator U301 | 10 / NSS | RFM95W pad 5, 10 k pullup to MCU 3.3 V |
| Coordinator U301 | 3 / RESET | RFM95W pad 6, 10 k pullup to RF 3.3 V |
| Coordinator U301 | 4 / IRQ | RFM95W pad 14, DIO0 |
| Coordinator U301 | 21 / TX | J302 pad 3, service/gateway TX |
| Coordinator U301 | 20 / RX | J302 pad 4, service/gateway RX |

GPIO2, GPIO8 and GPIO9 have no external loads in all three circuits. USB uses the onboard
connector; GPIO18/19 are not invented header pins. Keep runtime logs on native USB when
UART0 is used for GPS or the service port. An eventual cabinet adapter must reject boot
noise and invalid frames; that protocol and safety interface are not specified by this port.

## Power-path details

### Puck

The protection board uses a common charge/discharge port. Cell positive/negative go to
B+/B-. All charger and load connections use P+/P-, including the system ground. Do not
short B- to P- externally. If the pack already has adequate verified protection, use its
protected terminals and omit the redundant separate protection board accordingly; do
not bypass protection on an unprotected cell.

Set and measure the TPS63020 carrier output at 3.30 V before attaching the electronics.
JP101 is fitted for battery operation and removed before plugging USB into U104 for
USB-powered programming. This disconnects the external regulator output from the MCU
supply. The SuperMini 5V header is left unconnected in the puck.

SW101 controls enable current only, through R101. Its contact numbering must be checked
with a continuity meter. The selected TPS carrier's EN pad, onboard pullup and any fixed
enable link must be identified before fitting this connection. Do not ground a hard-wired
enable link or use this small switch to interrupt the main battery load.

The solar panel's measured open-circuit voltage must stay within the CN3065 carrier/IC
input rating; 5.5 V nominal does not establish its actual open-circuit voltage. The IC's
specified operating input is 4.4-6 V. Do not parallel its USB input with a solar source
without an appropriate input-source arrangement.

The selected CN3065 carrier has not been verified for programmed charge current, battery
temperature sensing or charging behavior under operating load. The drawing does not
invent a separate load-sharing output or accessible TEMP pad. IC thermal regulation does
not establish battery-temperature protection. Resolve these items before sealed outdoor use.

MMC5603 VIN is the intended carrier supply input; 3Vo is an output and is left open.
R103/R104 are initially DNP because suitable pullups may already be on the carrier.
100 nF means 0.1 uF / code 104; do not substitute 100 uF because of the inconsistent
shopping-row label. Keep regulator power loops away from the magnetometer physically.

### Beacon and coordinator

Their onboard USB-C connectors are the sole 5 V entry points for these prototypes. The
5V header then supplies the GPS VIN or the RF regulator. Do not connect an independent
5 V source to that header while USB power is present. The GPS's regulator output is not
tied to the MCU's regulator output. GPS logic is 3.3 V even with 5 V supplied to GPS VIN.

The coordinator's AP2112K powers the RFM95W only, keeping radio transmit current off the
unverified SuperMini peripheral-regulator budget. Its input/output 1 uF ceramics remain
required. C303/C304 provide local RF bulk/bypass support; verify startup, RF TX supply
dips, current and regulator temperature on the actual assembly.

DS3231SN pads 5-12 are explicitly grounded, as required by its datasheet. CR2032 is a
primary backup cell and is not charged. Do not transpose this bare-IC pin numbering onto
a commercial RTC breakout; breakout headers have different numbering and may add a
charging circuit. RTC retention alone does not provide controller-failure handback.

J302 is not a lamp-power connector. Its pins are 1=MCU 3.3 V, 2=GND, 3=MCU TX and
4=MCU RX. Native-cabinet protocol, voltage levels, isolation, watchdog and safe handback
must be designed with the cabinet supplier. No mains or raw vehicle 12/24 V enters these
drawings. A suitably protected external USB adapter is a separate power-source component.

## Terminal identification and verification limits

The SuperMini pin IDs use its header labels (5V, GND, 3V3, GPIO numbers), not the chip's
package pad numbers. Carrier terminal IDs use their electrical labels; the diagrams do
not assert a physical left-to-right pad order for uninspected Shopee carriers. The GPS
numbers are the manufacturer's JP1 pad numbers; the DS3231SN, AP2112K and RFM95W
numbers identify the actual device/module pads.

Clear front/back photos of the actual CN3065, TPS63020, protection and MMC5603 carriers
would permit final terminal/order verification. Confirm the SuperMini variant against its
silkscreen as well. These are prototype review schematics, not a fabrication or field-installation release.

KiCad 7.0.11 successfully parsed all three native files and exported the PDF, SVG and XML
netlists. The included audit evaluates 52 explicit connectivity assertions against those
exported netlists, including battery protection returns, isolated regulator outputs, signal
pairing, every RTC ground-required pad and unused strapping pins. All passed for P1.
This is not a full ERC, a circuit simulation, a PCB layout check or a physical electrical test.

`wire_connections.csv` contains actual exported net membership. `BOM_and_pins.csv`
contains component and pin names. `connectivity_audit.json` retains each checked condition.
The generation and export/audit scripts are provided for reproducibility; editing in KiCad
does not require running them. Rebuilding the source scripts uses Python plus sexpdata
and the KiCad 7 standard symbol library; exporting uses kicad-cli, Poppler and pypdf for merging.

## Source references

- User reference: ESP-Phone schematic. https://github.com/ElSigmaTom/ESP-Phone/blob/main/esp_phone.png
- Current hardware selections: RESEARCH MASTERSHEET, HARDWARE and Notes Dump tabs, read 31 October 2026.
- Hope Microelectronics. RFM95W/96W/98W datasheet, version 2.0, section 1.4. https://www.hoperf.com/uploads/RFM95W-V2.0_1695351437.pdf
- Analog Devices / Maxim Integrated. (2015). DS3231 datasheet, revision 10, page 9. https://www.analog.com/media/en/technical-documentation/data-sheets/DS3231.pdf
- Diodes Incorporated. (2017). AP2112 datasheet, pages 1-2. https://www.diodes.com/datasheet/download/AP2112.pdf
- Texas Instruments. TPS63020 datasheet. https://www.ti.com/lit/ds/symlink/tps63020.pdf
- Consonance. CN3065 datasheet, revision 1.0. https://files.seeedstudio.com/wiki/Lipo_Rider_Pro/res/DSE-CN3065.pdf
- MEMSIC. (2022). MMC5603NJ datasheet, revision B. https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5603NJDatasheetRev.B.pdf
- Adafruit. Ultimate GPS v3 pinouts. https://learn.adafruit.com/adafruit-ultimate-gps/pinouts
- Adafruit. Ultimate GPS board CAD, JP1 pin map. https://github.com/adafruit/Adafruit-Ultimate-GPS/blob/master/Adafruit%20Ultimate%20GPS.sch
- Adafruit. MMC5603 carrier pinouts (reference carrier; selected PCBfun board still needs inspection). https://learn.adafruit.com/adafruit-mmc5603-triple-axis-magnetometer/pinouts
- Apache NuttX. Tenstar Robot ESP32-C3 SuperMini, pin mapping. https://nuttx.incubator.apache.org/docs/latest/platforms/risc-v/esp32c3/boards/esp32c3-supermini/index.html
- Espressif Systems. ESP32-C3 hardware schematic checklist. https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html

Native passives, switches, RF symbol geometry and connectors derive from KiCad 7's standard
symbol library; see `KICAD_SYMBOL_LICENSE.txt`. Module-specific symbols and the manual
interconnection design were authored for this prototype. The generic RFM95W symbol uses
the shared W-series 16-pad pinout; it does not select an operating band.
