# Manufacturing plan

## Approved fabrication target

Revision A targets **JLCPCB Standard PCBA**. The initial order configuration is:

- four-layer rigid FR-4, 1.6 mm finished thickness;
- green solder mask and white legend;
- ENIG surface finish;
- 1 oz finished outer copper and 0.5 oz finished inner copper;
- L1 components/signals, L2 uninterrupted GND, L3 power/slow signals, and L4
  components/signals;
- mixed SMT and THT assembly, with the OLED module fitted by the user;
- single-board delivery initially; add JLC tooling rails/fiducials only if the
  assembly quotation or panelization requires them.

The accepted provisional board size is 100 x 70 mm. JLCPCB does not require a
preferred rectangular increment for ordinary routed boards; price principally
tracks area and selected process options. This outline remains compact while
meeting the currently published 70 x 70 mm minimum single-board size for
Standard PCBA. Four 3.2 mm NPTH mounting holes support a later custom printed
enclosure without increasing the PCB outline.

The embedded KiCad stackup is synchronized to JLC's published standard 1.6 mm
four-layer 7628 construction: 0.2104 mm 7628 prepreg outside a 1.065 mm
NP-155F core, with 1 oz outer and 0.5 oz inner copper. JLC can change available
laminates, so compare the final quotation against the controlled order sheet.
Do not infer USB impedance from nominal board thickness alone.

## Board rules

The ordinary routing defaults remain conservative. Fine-pitch/package-internal
features use current JLCPCB four-layer capabilities only where the component
manufacturer's land pattern requires them:

| Item | Revision A rule |
|---|---:|
| Ordinary netclass width / clearance | 0.20 mm / 0.20 mm |
| Project hard minimum width / clearance | 0.15 mm / 0.15 mm |
| TPS63070 RNM package-internal clearance rule | 0.09 mm; manufacturer land pattern only |
| Preferred power trace width | 0.50 mm or wider after current review |
| Preferred via finished drill / diameter | 0.20 mm / 0.45 mm |
| PTH annular ring | at least 0.25 mm where footprint permits |
| Copper to routed board edge | at least 0.50 mm |
| Silkscreen line / text height | at least 0.15 mm / 1.0 mm |
| SMD courtyard spacing | follow JLC package-pair guidance; normally >=0.5 mm and >=1.0 mm around QFN |

Revision A is locked to JLC's standard/no-impedance-requirement 1.6 mm,
four-layer 7628 construction with 1 oz outer and 0.5 oz inner copper. USB D+/D-
are 0.20 mm, short, and primarily referenced to continuous L2, but the Type-C
orientation crossover is not a continuously coupled, field-solved 90-ohm pair.
Do not select paid controlled impedance for Revision A; validate CP2102N
full-speed enumeration during bring-up. The complete rationale and order values
are in `manufacturing/jlcpcb-order-parameters.md`. CAN and composite video are
routed with controlled return paths but without fabricated impedance claims.

- Prefer 0603 passives, SOIC/TSSOP where available, and manufacturer-recommended
  QFN land patterns for the unavoidable regulators and CP2102N.
- Through-hole RCA, CAN terminal blocks, buttons, and optional jumper headers may
  be hand/secondary assembled if this improves mechanical strength.
- Use project-local symbols/footprints for KLPX RCA, TPS63070, and any part not
  unambiguously represented by installed KiCad libraries. The USB4105, Phoenix
  1715734 terminal blocks, and JST-PH OLED connector use audited official KiCad
  footprints. The DFR0486 module is user-fit and cable mounted. Record drawing
  revision in footprint properties.
- Add fiducials, tooling/handling clearance, readable connector polarity and bus
  labels, test-point labels, board revision/date, and an antenna keepout note.
- Run ERC/DRC without blanket suppressions. Every waiver needs a reason in this
  file. No DRC exclusions exist yet.
- Manufacturing exports go to `manufacturing/generated/` and are ignored until
  a reviewed release is copied into a versioned release directory.

## Pre-release checks

- schematic/PCB netlist parity and pin-number audit (board-only H1-H4 excepted);
- footprint dimensions against current manufacturer drawings;
- BOM lifecycle and stock review at two major distributors;
- assembly capability for 0.5 mm QFN/DFN and exposed pads;
- JLC/LCSC stock and basic/extended classification checked immediately before
  order; use pre-order/global sourcing for exact approved MPNs rather than
  silently substituting parts;
- impedance and return-path review for USB, CAN, and video;
- antenna edge/keepout inspection in Gerber and 3D views;
- ERC, DRC, drill, solder-mask sliver, annular ring, courtyard, and polarity
  reports archived with the release.

## 2026-10-04 pre-release audit package

The local `manufacturing/generated/rev-a-audit/` package has been generated from
the fully routed board. It is an engineering audit, not an order release.

| Audit item | Result |
|---|---|
| Board | 100 x 70 mm nominal, four layers, 1.58 mm modeled thickness |
| Footprints | 134 total; all on top side |
| Routing | 274 vias; 0.15 mm project minimum trace/clearance; 0.20 mm minimum drill |
| ERC | 0 violations |
| DRC | 0 violations; 0 unconnected items |
| Strict DRC audit | 0 violations after temporarily enabling all five normally ignored rule categories |
| Gerbers/drills | Generated for all production layers; separate PTH/NPTH drills and maps |
| Assembly filtering | 92 automatic-SMT candidates, 5 required manual/wave-assembly connectors, 6 DNP, and 31 PCB features |
| Mechanical output | Top/bottom renders, assembly PDF, and STEP generated |

Raw KiCad BOM/CPL output is retained only for comparison. KiCad did not exclude
parts whose population state existed only in the value text, so C63 and the DNP
resistors appeared in that output. `scripts/export_jlc.py` is now the controlled
assembly export path and emits `assembly-population.csv`, candidate BOM/CPL files,
and a blocking readiness report. The explicit default DNP set is C63, R4, R24,
R25, R61, and R63. Solder jumpers, test points, and mounting holes are fabricated
features and never placement items. J1/J10/J20/J40/J60 are all required in the
BOM and CPL for JLC manual/wave assembly; none may be silently depopulated.
The controlled order remarks and connector orientations are in
`manufacturing/jlcpcb-assembly-notes.md`.

The candidate BOM includes only exact-MPN LCSC catalog identities already
verified in `bom/jlcpcb-verified-parts.csv`; unresolved JLCPCB/LCSC fields remain
blank. As of the 2026-10-05 qualification pass, **all 97** BOM-candidate
references have approved LCSC/JLC identities. C1 is PSA FV32N472J102EFG /
C5156737 from JLC global inventory: 4.7 nF, 1 kV, C0G, +/-5%, 1210. D078
accepts its commercial/non-AEC-Q200 qualification for Revision A prototypes
while retaining the former TDK automotive part as the preferred production
upgrade. At the same audit the original
non-reel CP2102N and USB4105 catalog items were out of stock; TJA1055, video ESD,
crystal, and the exact three-button requirement also had insufficient or low
stock. The three buttons were subsequently changed to footprint-compatible
TL3301NF260QG / C273528. The current consolidated JLC workbook allocates all 6
required switches from JLCPCB for two assembled boards, closing the earlier
duplicate-line and availability issue for this quotation. U2 was changed only to Silicon Labs' `R` tape-and-reel ordering
suffix, CP2102N-A02-GQFN28R / C964632, with 40,263 live units; its silicon,
revision, package, and footprint are unchanged. The remaining constrained parts
need an order-time reservation, pre-order, global-sourcing, or consignment
decision. The candidate filenames and readiness report prevent
accidental order upload.

The STEP exporter could not locate library models for L1, L2, U4, and Y40. This
does not affect their footprints, copper, paste, or fabrication data, but the
mechanical model is incomplete until those four bodies are supplied or mapped.

KiCad's project configuration normally ignores missing-courtyard,
track-not-centered-on-via, tuning-profile-geometry, footprint-filter-mismatch,
and footprint-type-mismatch checks. These are rule-category settings rather than
per-item exclusions. For the audit, all five were temporarily changed to warning
in a complete project copy containing the same `.kicad_dru`, footprint table,
and local library. The strict run also returned 0 violations and 0 unconnected
items; its report is archived as `reports/drc-strict.rpt`. The production project
settings were not changed. There are no item-level DRC exclusions.

### JLC-specific release blockers

1. Kycon specifies a 2.20 x 1.20 mm plated slot for one J60 contact. It is
   faithfully present in the drill output, but its 1.83:1 length/width ratio is
   below JLC's general guidance that a slot be at least twice as long as wide.
   Submit the files for JLC DFM confirmation; do not enlarge the slot without a
   new Kycon mechanical tolerance review.
2. Confirm JLC manual/wave assembly for all five connectors. J1 has SMT contacts
   plus plated shell stakes; J10/J20/J40/J60 are THT. All are deliberately in
   both the BOM and CPL and must be selected in JLC's component-matching step.
3. The U5, U10, J1, and J60 independent dimensional audits are complete. Retain
   the documented U5/J60 DFM gates plus physical connector fit checks.
4. Arrange global sourcing/consignment for C1 and perform polarity/rotation review in JLC's online
   assembly viewer.
5. Keep the documented default video population for the prototype order.
   Electrical-level and JVC compatibility validation is owner-deferred to
   assembled-board bring-up; do not interpret the deferral as a passed test.

## Current layout-stage DRC status

The 2026-10-04 reviewed placement and routed subsystems have zero
courtyard-overlap, shorting-item, hole-clearance, and board-edge violations.
USB data, the TPS62132 switch node, and MCP2515 oscillator routes are clean.
The named continuous L2 GND zone is filled, connected to `/GND`, and respects
the ESP32 antenna keepout. Both converter islands, the L3 protected-USB and
5V_FT trunks, the branched +3V3 distribution tree, the complete CAN_HS path,
and the TJA1055-to-J40 FT-CAN physical path pass electrical DRC.

An independent gerbv 2.9.6 review of all copper, mask, paste, legend, outline,
and drill outputs was completed on 2026-10-04. Separate layer renders and parser
logs are archived under `manufacturing/generated/rev-a-audit/review/`; findings
and the X2-metadata warning limitation are recorded in
`docs/rev-a-fabrication-review.md`. No new fabrication-data defect was found.

The independent
RTH/RTL termination branches, local MCP2515-to-TJA1055 TX/RX routes, pull-up
spine, mode-pin ground defaults, and ERR/STB/EN routes are also complete. The
MCP2515 MOSI, MISO, SCK, CS, INT, their pull-ups, and the complete reset RC
network are DRC-clean. The complete USB programming block is routed and
electrically DRC-clean: CP2102N UART0 TX/RX, crossed DTR/RTS transistor network,
EN/GPIO0 pullups, RESET/BOOT buttons, and all four associated test points. The
GPIO27 status LED, OLED connector power/ground, complete GPIO21/GPIO22 SDA/SCL
routes, and optional DNP pullups are also routed and clean. The I2C pair avoids
L2 and preserves the continuous ground plane. The optional user button is now
complete, including its pullup and ground return. The default local video chain
from GPIO25 through R60/C60, U60, R62, D60, and J60 is routed. TP13/TP60 and the
DNP AC-coupled/passive experiment branches are also connected on isolated
corridors; no video trace uses L2. The
+3V3 tree includes reviewed L4 bridges only where needed to cross the L3 5 V
corridor; L2 remains continuous GND. A final deterministic cleanup group has
also completed additional local grounds, duplicate button contacts, and the
5V_FT test point. The subsequent USB/power finishing pass connects the USB-C
ground tabs, all four shield stakes and shield capacitor, raw VBUS contact
pairs, connector-side ESD-array supply/ground, TPS2553 input/test path, and
additional local returns. Follow-on cleanup connects the regulator pull-up
branches, CAN_HS/CAN_FT test points, and locally relocated GPIO34/DAC2/GPIO14
probe points without long cross-board stubs. The same pass now also completes
both ESP32 ground-pad escapes, the protected-5-V test point, USB shield RC
link, CP2102N reset pull-up, local U4 power-good/output connections, and the
USB-UART protected-5-V bypass, and the complete U5 enable/power-good pull-up
network and the TPS2553 fault output through R9. The Type-C CC1/CC2 pulldowns
are relocated below the receptacle and fully routed without disturbing the USB
differential pair or L2 ground plane. The TPS2553 ILIM resistor is also local
to U3 and fully connected. The VBUS-sense divider, USB fault test point, raw
VBUS bulk capacitor, and protected-5-V bulk capacitor complete the remaining
power-support routes. The deterministic full rebuild now reports **0
unconnected items**. The
deterministic silkscreen DFM pass leaves **0 DRC violations**: crowded reference
fields are retained on F.Fab/assembly outputs rather than F.SilkS, and the
project-local RCA footprint has a clipped body outline around its shield pads.
There are no copper, mask, courtyard, keepout, hole, edge, or silkscreen errors.
The following footprint and
manufacturing reviews remain:

- TPS63070 U5 pads 4 and 5 use a controlled 0.08 mm trim at only their mutually
  facing inner heel ends, preserving both manufacturer-pattern outer toes.
  This resolves the former 0.025 mm copper gap and solder-mask-bridge errors at
  the project's 0.09 mm package rule. Verify copper, paste, and mask in final
  Gerbers and include the change in the JLCPCB DFM review.
- The GCT USB4105 official footprint's signal copper is 0.1944 mm from its two
  locating NPTHs. The project board-level hole clearance is 0.19 mm to model
  that audited connector geometry; all freely placed copper still targets at
  least 0.20 mm from routed holes/slots.
- The 0.20 mm thermal drills in the official TPS62132 footprint and ESP32 module
  land pattern are within JLCPCB's published multilayer capability and match its
  preferred minimum drill, but may affect price when the pad diameter is below
  the no-surcharge threshold.

JLCPCB's capability page checked 2026-10-03 lists 0.09/0.09 mm minimum
width/spacing for multilayer 1 oz work, 0.20 mm preferred via drills, and
0.15 mm absolute multilayer drill capability. These are capabilities, not
instructions to route ordinary nets at the minimum.

## JLCPCB references

- PCB manufacturing capabilities: https://jlcpcb.com/capabilities/pcb-capabilities/
- PCBA capabilities: https://jlcpcb.com/capabilities/pcb-assembly-capabilities
- KiCad BOM/CPL export fields: https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad
- Ordering and slot guidance: https://jlcpcb.com/help/article/instructions-for-ordering
- Current multilayer structures: https://jlcpcb.com/help/article/multi-layer-pcb-standard-laminated-structures
- Impedance calculator instructions: https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator
- SMD spacing: https://jlcpcb.com/help/article/minimum-spacing-for-smd-components
