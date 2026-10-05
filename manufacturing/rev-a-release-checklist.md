# Revision A release checklist

This checklist controls promotion of the local audit package into an orderable
JLCPCB release. A checked item needs retained evidence, not only verbal review.

## Electrical and layout

- [x] KiCad 10.0.6 schematic ERC: 0 violations.
- [x] KiCad 10.0.6 PCB DRC: 0 violations and 0 unconnected items.
- [x] Temporary strict DRC with all normally ignored categories enabled: 0
  violations and 0 unconnected items.
- [x] Four-layer Gerbers and separate plated/non-plated drills generated.
- [x] Continuous L2 ground plane and ESP32 antenna keepout present.
- [x] Default/DNP assembly population expressed explicitly.
- [x] Verify schematic-to-PCB reference/value parity after the final BOM edit.
- [x] Review Gerber copper, mask, paste, polarity, and legends in an independent
  viewer and archive screenshots.
- [x] Project owner reviewed the local board/assembly renders visually on
  2026-10-04; no visual issue reported.
- [x] Lock the JLC four-layer stack and document the full-speed USB geometry
  disposition; reconfirm the controlled order parameters before payment.

## Components and footprints

- [x] Replace the insufficient-stock TL3301NF160QG buttons with audited,
  footprint-compatible TL3301NF260QG / C273528 devices.
- [x] Consolidated SW1-SW3 row allocates 6 TL3301NF260QG/C273528 switches from
  JLCPCB in the current two-assembly quotation.
- [x] Replace unavailable C1 with verified PSA FV32N472J102EFG / C5156737,
  preserving 4.7 nF, 1 kV, C0G, and 1210; commercial/non-AEC-Q200 prototype
  qualification is accepted under D078.
- [x] Reject JLC's unsafe C1 suggestion C1210X201F1HACAUTO/C2309638.
- [x] Replace delayed/zero-stock L1/L2 with verified WPN4020H2R2MT/C98361 and
  XGL4020-152MEC/C7417180; re-check and reserve live stock at order time.
- [x] Resolve CP2102N availability using the manufacturer-defined tape-and-reel
  order code CP2102N-A02-GQFN28R / C964632; no silicon/package change.
- [ ] Resolve exact USB4105-GF-A availability without changing its audited land
  pattern or silently substituting a connector.
- [ ] Resolve low-stock TJA1055T/3/2Z by reservation, pre-order, or global source.
- [ ] Confirm J1 mixed SMT-contact/PTH-stake assembly process with JLC.
- [ ] Accept J1's difficult-processing surcharge only after written confirmation
  that both SMT contacts and PTH shell stakes will be assembled.
- [ ] Confirm J10, J20, J40, and J60 manual/wave assembly with JLC; no connector
  may be left unpopulated in the final component-matching selection.
- [x] Overlay U5 RNM0015A pads/paste/mask against TI drawing 4222000/B.
- [x] Overlay U10 land pattern and antenna keepout against Espressif guidance.
- [x] Overlay J1 contacts, holes, shell slots, outline, and board-edge datum
  against GCT USB4105 drawing B1.
- [ ] Print J1, J10, J20, J40, and RCJ-014 J60 footprints at 1:1 and physically fit parts.
- [x] Eliminate J60 plated-slot DFM risk by selecting the four-round-hole RCJ-014.
- [ ] Review every CPL orientation in the JLC placement viewer.

## Prototype-risk validation

- [x] Video-validation disposition recorded: owner accepts deferral until
  assembled Revision A hardware; this does not count as functional validation.
- [ ] MCP2515 16 MHz oscillator startup/frequency validated with selected crystal
  and 18 pF capacitors.
- [ ] CAN_HS termination and protection bench tested.
- [ ] CAN_FT RTH/RTL values confirmed for the actual vehicle network topology.

## Required post-assembly video validation (not a prototype-order blocker)

- [ ] PAL test pattern verified into 75 ohms on an oscilloscope.
- [ ] NTSC timing and amplitude verified into 75 ohms on an oscilloscope.
- [ ] PAL and NTSC checked on a known monitor/capture device.
- [ ] JVC KD-X560BT rear-camera input compatibility verified.
- [ ] Video stressed with CAN traffic and Wi-Fi/Bluetooth activity.

## Release package

- [x] Set the requested Revision A assembled prototype quantity to 2 boards.
- [ ] Confirm the JLC quotation accepts 2 assembled boards for the selected
  Standard PCBA mixed SMT/THT process.
- [x] Re-run `scripts/export_jlc.py`; the candidate BOM/CPL contain all 97
  approved catalog identities. The readiness report intentionally retains
  process/fit/stock-at-order blockers.
- [x] Re-run ERC/DRC after D079: ERC 0; PCB DRC 0; unconnected 0.
- [ ] Regenerate Gerber, drill, BOM, CPL, assembly drawing, IPC-D-356, and STEP.
- [ ] Generate fabrication and assembly ZIP files separately.
- [ ] Add stackup/order parameters, version, date, and checksum manifest.
- [ ] Copy reviewed files to a tracked versioned release directory.
- [ ] Run JLC online DFM and save the resulting review evidence.

Do not order from `manufacturing/generated/rev-a-audit/`; it is intentionally an
ignored working directory.
