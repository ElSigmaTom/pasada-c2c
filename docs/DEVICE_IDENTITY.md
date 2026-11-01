# Puck identity · proposal for discussion

Status: **draft, not adopted**. No permanent puck UID has been issued by this simulation. The existing `PUCK-…` values remain unique planning references inside the installation project; they are retained so saved projects, replays, lane mappings and provisioning examples continue to work.

## Keep hardware identity separate from placement

| Record | Purpose | Behavior when a puck is moved or replaced |
| --- | --- | --- |
| `hardware_uid` | Immutable identity of a physical puck, assigned and verified during enrollment. | Moving a puck retains its hardware UID. A replacement puck has a different UID. |
| Planning / installation reference | Human-readable identity of a detector position in the installation. | A replacement can occupy the same position reference. A move changes the assignment, not the identity of the physical board. |
| Commissioning binding | Links hardware UID, position reference, controller, lane, coordinates, firmware and installation revision. | Keep assignment dates and replacement history; supersede old bindings rather than silently rewriting them. |

A possible **position-label** format for discussion is `MD01-N-L02-U030`: study site, approach, lane and upstream station. A downstream position could use an exit marker rather than an upstream distance. This is an example, not the accepted convention. Formalize municipality/site codes, lane numbering direction, turn-pocket handling, maximum field lengths, downstream naming and revision rules before adopting any format.

For the permanent hardware identity, decide an enrollment/registry scheme independently of road position. An opaque provisioned UUID is one possible approach; the manufacturing serial and radio addresses can be recorded as separate attributes. No UUIDs, MAC-derived IDs, radio keys or physical-device bindings are fabricated by the browser demo. The registry must enforce uniqueness and track replacements. An identifier by itself does not authenticate a device; enrollment and protected radio credentials are separate requirements.

## Current UI behavior

- The installer opens with the three configured study intersections and no device overlay.
- Hovering a crossing shows its name and a selectable cursor. Clicking selects the site, highlights it and displays only its proposed devices and lane borders.
- Puck hover labels show the existing planning reference, lane and detector offset, plus an explicit hardware-UID-not-assigned status.
- Clicking a puck opens the configurator. No new identifier is generated simply by hovering, selecting or moving a puck.
- Device dragging is off by default in preview. Enable dragging explicitly, or use the existing coordinate and two-border alignment controls.
- The proposed identity approach is available from the installer and Technical handoff. It does not change the current export schema or require a final hardware convention yet.

## Scale and map provider

The overlay is drawn from latitude/longitude and metre-based lane paths: 5/30/60 m upstream and one counter per outgoing lane. A metre scale bar follows map zoom. Proposed physical puck footprints use the Rev B body diameter of 123 mm; on-screen click markers are enlarged so they remain usable. These markers do not represent a detection radius, validated magnetic coverage or surveyed installation positions.

The running prototype uses Leaflet with Esri satellite imagery and OpenStreetMap street tiles. It is not an embedded Google Maps implementation. Each selected crossing has an **Open this crossing in Google Maps** link for the same coordinates. That external map does not carry PASADA's editable overlay.

Embedding Google Maps itself requires a project API key. Google's documentation, checked on 26 October 2026, describes a Maps Demo Key for eligible prototyping accounts, or a standard key with billing for production. No Cloud project, billing account, key or new access grant was created in this task. A future provider integration should use an appropriately restricted key and preserve the installation coordinates independently of the basemap.

Official setup: https://developers.google.com/maps/documentation/javascript/get-api-key

Demo-key scope: https://developers.google.com/maps/documentation/javascript/demo-key
