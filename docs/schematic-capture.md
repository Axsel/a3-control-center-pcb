# Phase 2 schematic capture plan

The KiCad project is native version 10.0.6. Detailed capture is generated from
a reviewed Python connectivity description and then accepted only after KiCad
ERC, exported PDF inspection, pin-map checks, and host-side visual review.

## Sheet organization

1. Root: functional block overview and inter-sheet ports.
2. USB and power: USB-C, ESD, current limiter, 3V3 buck, 5V_FT buck-boost and
   rail test points.
3. ESP32 and UI: module, EN/BOOT/automatic programming, UART, buttons, LEDs,
   OLED and expansion/debug header.
4. CAN_HS: TCAN332, selectable termination, optional choke/bypass, protection
   and connector.
5. CAN_FT: MCP2515, 16 MHz oscillator, TJA1055T/3, mode/error signals,
   configurable ISO 11898-3 termination/bias, protection and connector.
6. Video: GPIO25 input, population-selectable coupling/conditioning, THS7314,
   75-ohm source resistor, protection and RCA.

## Capture gates

- Every IC pin number is checked against the linked manufacturer datasheet.
- Every standard-library symbol and footprint is audited; library presence does
  not constitute approval.
- Custom symbols presently audited: TJA1055T/3, THS7314, TPS63070,
  PESD2CAN24T-Q, and the ABM3BAIG four-pad crystal pin map.
- TPS63070 uses project-local `TI_RNM0015A_VQFN-HR-15`, captured from TI
  drawing 4222000/B. KiCad parses the unusual SMD/custom-pad construction;
  the independent dimensional land/paste audit was completed on 2026-10-04.
  JLC DFM review of the documented pads 4/5 inner-heel relief remains a gate.
- KiCad 10 contains `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`;
  its contact lands, alignment holes, shell slots, body envelope, and PCB-edge
  datum passed an independent overlay against GCT drawing B1 on 2026-10-04.
  Mixed SMT/PTH assembly handling and a physical fit check remain gates.
  RCJ-014 now uses a project-local four-round-hole footprint captured from Same Sky
  engineering drawing A7. The OLED interface is locked to DFRobot DFR0486 over
  a keyed JST-PH/Gravity cable and uses the official KiCad connector footprint.
- J20 and J40 are Phoenix Contact 1715734, three independent potentials at
  5.08 mm pitch, using KiCad's dedicated MKDS footprint. The internally
  commoned `-B-` product variant is prohibited.
- TPS62132 uses the official KiCad RGT-compatible 3 x 3 mm VQFN footprint with
  a 1.68 x 1.68 mm exposed pad, matching TI drawing RGT0016C.
- Video output uses the documented default GPIO25/THS7314 DC-output population.
  Optional paths remain DNP. Coupling, amplitude, and sink compatibility are
  explicitly deferred to assembled-board bring-up for Revision A.
- CAN_FT RTH/RTL are captured as matched 1.2 kΩ configuration resistors with
  two normally-open solder jumpers. They must be enabled together only after
  the vehicle topology is known and must never be replaced by a 120-ohm
  differential part.

## Automation environment

Create the ignored environment and install the pinned generator dependency:

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements-schematic.txt
```

The generator must use both symbol roots:

```text
hardware/lib
KiCad 10 official Symbols extension
```

The installed `kicad-sch-api` wheel identifies itself internally as 0.5.5 even
though PyPI distributes it as 0.5.6. Generated output was independently parsed
by KiCad 10.0.6; the package version string is not treated as validation.

## Current status

The project now contains detailed `USB + Power`, `ESP32 + UI`, `CAN_HS`,
`CAN_FT`, and `Composite Video` sheets.
Captured and primary-source checked items include USB-C CC resistors, USB ESD,
CP2102N external-3.3-V operation and VBUS divider, the Espressif crossed-NPN
automatic-programming circuit, TPS2553 input limiting, TPS62132 3.3 V power,
TPS63070 5 V fault-tolerant-CAN power, the ESP32 module, manual controls, OLED
header, indicators, TCAN332 high-speed CAN, MCP2515/TJA1055 fault-tolerant CAN,
bus protection, configurable termination, the population-optioned THS7314
video path, RCA connector symbol, and test points.

ERC for the captured sheets has zero violations. TPS63070 and RCA footprints
are present, parse in KiCad 10.0.6, and passed independent dimensional audits
against TI 4222000/B and Kycon A7. JLC acceptance of the RCA plated-slot aspect
ratio and the U5 heel relief remains a manufacturing gate, not an ERC exception.

The generator places labels directly on pins to guarantee connectivity, so the
CAN and video sheets are electrically auditable but visually crowded. A host KiCad 10
wire/label placement pass is required before schematic review signoff. The two
0-ohm link pairs provide routing breaks only; a future common-mode choke is not
drop-in compatible unless its exact four-pad footprint is selected and the PCB
is revised accordingly.

The default video population is 100 nF 50 V X7R input coupling, THS7314 channel 1,
75 Ω source termination, and DC output through bridged JP60. JP61/output AC
coupling and JP62/passive drive are DNP experiments and are explicitly
interlocked; only one output-selection jumper may ever be closed.
