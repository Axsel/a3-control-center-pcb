# Revision A placement strategy

This strategy controls routing. The accepted provisional board outline is
100 x 70 mm. Reliability, probing access, and connector strength take priority
over further area reduction.

```text
                  TOP / VEHICLE HARNESS EDGE
  +----------------------------------------------------------------+
  |  ESP32 antenna over edge/keepout       CAN_HS      CAN_FT       |
  |  [no copper/components all layers]     protect     protect      |
  |  ESP32 module                          TCAN332     TJA1055      |
  |                                        term/choke   term/bias    |
  |                                                                |
  |  USB-C   input       3V3 buck       MCP2515 + crystal           |
  |  + ESD   limiter     (tight loop)    (short SPI/clock)          |
  |  CP2102N auto-program                                         |
  |                                                                |
  |  BOOT EN   debug/test header      keyed OLED cable connector   |
  |                                                    video amp   |
  |  mounting hole                         quiet analog path  RCA   |
  +----------------------------------------------------------------+
                  BOTTOM / USER-FACING EDGE
```

## Placement rules

1. Put the ESP32-WROOM-32E antenna at the board edge. Apply the manufacturer
   keepout on every copper layer and keep components/traces out of it; no
   interpretation of the old WROOM-32 footprint is permitted.
2. Place USB-C shell stakes at a board edge. Put USB ESD directly behind the
   receptacle, then route the shortest practical nominal USB differential path to CP2102N without
   plane splits on L2.
3. Keep the TPS62132 switch node, inductor, and input/output capacitors in the
   smallest practical loop. Keep both switching regulators away from the RCA
   quadrant and ESP32 antenna.
4. Put CAN protection and optional common-mode elements immediately behind
   each CAN connector. Keep CAN_HS and CAN_FT physical-layer circuitry distinct
   and label both connectors prominently.
5. Keep the MCP2515 crystal and load capacitors tight to OSC1/OSC2. SPI may be
   longer than the oscillator loop but stays over continuous L2 ground.
6. Place THS7314, coupling option, source resistor, and video ESD next to the
   RCA. Route `VIDEO_DAC` away from switch nodes, USB edges, crystals, and CAN
   connectors, with an uninterrupted ground reference.
7. Put BOOT, EN, the keyed DFR0486 OLED cable connector, status LED, and debug
   points where they remain reachable with cables installed. The OLED itself is
   front-panel/enclosure mounted. Label every test point on silkscreen.
8. Place at least three global fiducials if JLC Standard PCBA requires panel
   rails; local QFN fiducials are optional unless requested by the assembler.
9. Use four 3.2 mm NPTH holes for M3 enclosure posts. Keep the screw-head
   courtyard free of copper, parts, and enclosure ribs.

## Layer use

- L1: components, critical/short signals, USB, CAN and video routes.
- L2: continuous ground plane; do not route signals or split it.
- L3: 3V3, protected 5V, 5V_FT distribution and slow signals while preserving
  broad ground return coupling where possible.
- L4: secondary signals and optional components; ground pour stitched to L2.

Critical routing starts only after the associated connector/module footprint
has passed its manufacturer-drawing audit.

## First-pass placement status — 2026-10-03

All 130 schematic footprints have been transferred through KiCad 10's managed
Update PCB flow. Four board-only mounting holes bring the placed footprint count
to 134 inside the 100 x 70 mm outline. The repeatable source is
`scripts/place_pcb.py`; rerunning it intentionally resets component coordinates
and must not be done after manual routing starts.

- ESP32 antenna faces the top edge with its all-layer keepout intact.
- USB-C is on the left edge; the ESD/bridge/autoprogram cluster follows inward.
- CAN_HS and CAN_FT connectors and protection occupy separate right-edge zones.
- MCP2515/crystal and TJA1055 remain a distinct central-right block.
- THS7314 and the experimental video coupling network occupy the lower-right
  quiet zone next to the RCA connector.
- BOOT, EN, USER, OLED, and named test points remain accessible from the lower
  edge.
- Provisional M3 NPTH centers, in KiCad board coordinates, are H1 (24, 32), H2
  (116, 24), H3 (24, 86), and H4 (116, 59) mm. H1 is deliberately below the
  antenna keepout; H4 braces the connector side above the board-edge RCA.
- USB-C was moved inward far enough that the official shell stakes meet the
  0.50 mm copper-to-edge rule while the receptacle remains board-edge usable.
- The TPS62132 was rotated so VIN faces the protected USB source and SW faces
  its inductor. The switch node is now short and broad. The TPS63070 island was
  tightened without violating component courtyards, but its RNM land-pattern
  DFM gate remains open.
- The MCP2515 crystal/load capacitors were tightened and its two oscillator
  nets are routed without DRC errors.
- USB data, the TPS62132 switch node, and MCP2515 oscillator nets are routed.
  A filled continuous L2 GND zone is present and respects the ESP32 all-layer
  antenna keepout. Shared rails and the remaining signals are still unrouted.
- Both switching-converter local loops, feedback/soft-start connections, and
  local ground drops are routed. Protected USB 5 V and regulated 5V_FT use
  explicit 0.8 mm L3 trunks; 5V_FT reaches all TJA1055 supply pins and local
  bypass capacitors.
- TPS63070 L2 orientation was corrected so L1 and L2 reach their respective
  switch pins without crossing. The feedback-divider high-impedance ends face
  the IC and remain outside the switch-current loops.
- KiCad DRC finds no courtyard overlaps, accidental shorts, board-edge errors,
  or errors in the routed USB/power/clock nets. Final reference placement and
  silkscreen cleanup remain outstanding.

The 100 x 70 mm outline and asymmetric post pattern are accepted provisional
mechanicals for a future printed enclosure. Further routing and zones must
preserve the hole courtyards. No manufacturing files should be generated from
this state.
