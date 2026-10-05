# A3 Control Center PCB

Revision A design for a USB-powered ESP32-WROOM-32E-N4 controller with independent
high-speed and fault-tolerant CAN buses, a replaceable SSD1306 OLED, and an
analog composite-video output.

## Status

Phase 1 architecture was approved on 2026-10-02. The Phase 2 schematic and
100 x 70 mm four-layer PCB are electrically complete for USB/power, ESP32/UI,
CAN_HS, CAN_FT, and composite video. A deterministic 19-stage layout rebuild
under KiCad 10.0.6 now reports **ERC 0, DRC 0, and 0 unconnected items**. A local
pre-release manufacturing audit package exists under
`manufacturing/generated/rev-a-audit/`, but no order-ready manufacturing release
has been created. LCSC identities are qualified for all 97 candidate
references; high-voltage C1 now uses PSA FV32N472J102EFG / C5156737 from JLC
global sourcing. The U5, U10, J1, and J60 critical footprints have passed
independent dimensional audits; JLC confirmation of the RCA plated slot, USB
connector assembly handling, physical connector fit checks, stock reservation,
and purchasing/source resolution remain release gates. The three-button part
identity is resolved by an audited same-footprint change to
TL3301NF260QG/C273528; the current consolidated JLC workbook allocates all six
needed switches. The former CP2102N stock gate is closed by using
Silicon Labs' electrically identical tape-and-reel order code
CP2102N-A02-GQFN28R/C964632. The project owner has
accepted deferring composite-video electrical and JVC compatibility validation
until assembled Revision A boards arrive; those tests remain mandatory during
bring-up but are no longer a prototype-order blocker.
The manufacturing contract requires JLCPCB to fit every board connector:
J1/J10/J20/J40/J60 are present in both the candidate BOM and full CPL for
manual/wave assembly; the user is not expected to solder connectors.
An independent layer-by-layer Gerber/drill render review is also complete, with
its evidence and limitations recorded in `docs/rev-a-fabrication-review.md`.

The originally requested ESP32-WROOM-32 was replaced with the manufacturer-
recommended `ESP32-WROOM-32E-N4` after project-owner authorization. The change
preserves the classic ESP32 architecture, 4 MB flash, PCB antenna, DAC1/DAC2,
TWAI, firmware pin map, and module envelope while avoiding an NRND part. The
manufacturer land pattern and antenna keepout for the 32E are mandatory.

## Repository map

- `docs/`: architecture, interfaces, calculations, decisions, and test plans
- `hardware/`: KiCad 10 project, design rules, and project-local libraries
- `datasheets/`: source index; vendor PDFs are not copied into Git by default
- `bom/`: controlled, provisional BOM
- `firmware/`: synchronized GPIO contract and video feasibility notes
- `scripts/`: KiCad CLI wrapper plus validation/export automation
- `manufacturing/`: controlled release area; generated files are ignored

The remaining JLC engineering and global-sourcing questions are consolidated
in `manufacturing/jlcpcb-support-request.md` for submission before payment.

## Tooling note

The container now has KiCad 10.0.6 and its matching official symbols,
footprints, templates, and 3D models. Use `./scripts/kicad-cli`; headless ERC and
DRC were validated against an installed reference project. Installation details
and the remaining Phase 2 inputs are recorded in `docs/toolchain.md`.
