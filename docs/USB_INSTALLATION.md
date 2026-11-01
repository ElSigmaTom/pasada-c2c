# Saved plan → browser device chooser

1 November 2026 · Scope follows the user's latest clarification: a simple native browser hardware-selection dialog, with firmware work deferred.

## Operator flow

1. Open Installation, choose a signalized intersection, and save its plan.
2. Select **Install devices →** below the plan, or **Installation → Install devices** to choose any saved plan or study site.
3. Select an individual puck or its planned intersection coordinator.
4. Plug in the board using a data USB cable and select **Connect device**. The browser's own serial chooser lists matching connected hardware; it handles device insertion/removal while open. Cancelling leaves the plan intact.

Use desktop Chrome or Edge and HTTPS. This implementation filters native Espressif USB serial interfaces with vendor ID `0x303A`. A USB-UART adapter with a different vendor ID is not included in this initial filter. An interface match is not proof of ESP32-C3 model, board role, hardware UID or firmware compatibility. The page reports only Device selected and USB VID/PID after a selection; unplugging clears it. Nothing opens/writes/flashes the port. No firmware binary is required or delivered for this change.

Saved area plans are resolved directly, retaining their puck IDs, lane geometry and coordinates. One unlocated planned coordinator is included when a saved plan has only pucks. Its position is not fabricated at the junction centre. Existing study device identities are reused. Mobile vehicle beacons remain in the existing vehicle-registration workflow. No additional intersection is activated in Operations.

The optional **Download device profile** action exports the selected plan/device configuration using the existing `pasada.device/0.1.0` contract. Planning IDs are not hardware identities, and downloading a profile does not install it. An unlocated coordinator remains `installation_ready: false`.

For the P1 puck, retain the schematic requirement to remove JP101 before USB-powered programming. No circuit or pin-map changes were made.

## Developer notes

- `dist/device-connection.js`: saved-plan context, per-device profile export and native `navigator.serial.requestPort({filters})` invocation.
- `dist/device-installer.js`: compact component picker and connection status; no custom USB chooser or fake success animation.
- `dist/area-planner.js`: post-save Install devices action. Unsaved geometry edits disable the handoff until saved again.
- `dist/app.js`: installer mode, callbacks and cleanup. The legacy configured-study virtual commissioning screen remains separately labeled.
- `tests/device-connection.test.mjs`: plan/profile preservation, existing study IDs, cancellation/unsupported browser and no implied hardware verification.

The newer user clarification narrows AI Scratchpad row 103 for this milestone. Actual firmware flashing, protected enrollment, configuration readback/hash and reboot retention remain a separate future integration; do not mark those complete or start creating role firmware merely to demonstrate this dialog.

Official implementation references:

- Chrome Web Serial guide (requestPort, filtering, device events): https://developer.chrome.com/docs/capabilities/serial
- Espressif USB serial hardware identification: https://docs.espressif.com/projects/rust/no_std-training/02_1_hardware.html
- ESP32-C3 serial connection: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/get-started/establish-serial-connection.html
