# Hardware workspace

Phase 2 contains a native KiCad 10.0.6 project, a complete hierarchical
schematic, a four-layer 100 x 70 mm PCB with all 130 electrical footprints plus
four board-only M3 mounting holes functionally placed, JLCPCB-oriented custom
design rules, and project-local library tables. USB data, both converter local
power stages, protected USB 5 V and 5V_FT distribution, and the MCP2515 crystal
nets are routed over a filled continuous L2 ground plane. The rest of the board
is intentionally still in routing development; this is not a manufacturing
release.

Project-local symbol and footprint libraries contain the Kycon KLPX RCA and
TPS63070 RNM0015A land patterns. The DFR0486 OLED is cable mounted through an
official-library JST-PH footprint; any device whose installed-library
pin/package mapping cannot be proven from its datasheet remains a local-library
candidate. The KiCad 10 official USB4105 footprint is present and matches the
selected GCT family. Its signal/contact orientation and edge-mounted
shell-stake clearances have been checked in the current placement; a final
drawing/Gerber overlay is still required before release.

The MCU is `ESP32-WROOM-32E-N4`. Its KiCad footprint has been checked for the 38
castellated pads, thermal ground land/vias, module outline, and antenna keepout
against Figure 13 of Espressif datasheet v2.1. The antenna is placed at the top
board edge; the keepout must be rechecked in final Gerbers after zones exist.

J20/J40 use Phoenix Contact item 1715734 (`MKDS 1,5/ 3-5,08`) and the audited
KiCad 10 official 5.08 mm MKDS footprint. This is the three-independent-potential
part; the similarly named internally commoned `-B-` variant is not acceptable.
