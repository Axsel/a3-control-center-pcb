# Footprint audit

This register records the mechanical source and verification state for parts
that can materially compromise Revision A. Library presence alone is not
approval. All dimensions are millimetres.

| Ref(s) | Part / package | Footprint | Source dimensions checked | State |
|---|---|---|---|---|
| U5 | TI TPS63070RNMR / RNM0015A | `A3_Control_Center:TI_RNM0015A_VQFN-HR-15` | TI drawing 4222000/B: 2.5 x 3.0 nominal body; 0.5 mm pitch; 0.60 x 0.25 mm perimeter lands; 1.70 x 0.25 mm lands 9-11; asymmetric copper/mask/paste for 7-13 | **Independent dimensional audit complete 2026-10-04.** All origins, pitches, outer extents, mask and split-paste dimensions match the TI example. Pads 4/5 intentionally retain the documented 0.08 mm inner-heel relief while preserving the TI outer toe at 1.45 mm; JLC DFM review of that relief remains required |
| J60 | Same Sky RCJ-014 | `A3_Control_Center:RCJ-014` | RCJ-01 drawing 2026-08-12: three 2.6 mm shell holes on 5.0 mm centers; 1.7 mm center-contact hole 4.5 mm forward; 11.6 mm maximum shell width | **Independent dimensional audit complete 2026-10-05.** Project footprint uses manufacturer numbering (pin 1 shell, pin 2 center), round plated holes, and the official pattern; no routed slots remain. Confirm JLC wave/manual assembly and physical plug access |
| J20, J40 | Phoenix Contact 1715734 | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | 5.08 pitch, 15.24 width, 0.9 x 0.9 pins, 1.3 drill, 9.8 length | Audited against current manufacturer data; selected |
| U10 | ESP32-WROOM-32E-N4 | `RF_Module:ESP32-WROOM-32E` | Espressif v2.1: 18.0 x 25.5 body; 38 perimeter lands, 1.5 x 0.9 at 1.27 pitch; exposed-pad array; antenna-area restriction | **Independent dimensional/keepout audit complete 2026-10-04.** The official KiCad 10 land pattern matches the Espressif dimensions, includes the exposed-pad via array, and applies a conservative all-copper-layer no-track/no-via/no-pad/no-pour/no-footprint antenna keepout. U10 is placed with the antenna-end body edge 0.075 mm inside the routed PCB edge; DRC confirms the keepout is respected |
| J1 | GCT USB4105-GF-A | `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` | GCT drawing B1: 0.30/0.60 x 1.15 contact lands; 0.50 signal pitch; 5.78 alignment-hole centers; four shell slots; 8.94 x 7.35 body envelope; PCB-edge datum | **Independent drawing overlay complete 2026-10-04.** Contact lands, two 0.65 mm NPTHs, four 0.60 x 1.40/1.70 mm plated shell slots, outline and PCB-edge datum match. JLC mixed SMT/PTH process confirmation and a physical 1:1 fit check remain required |
| J10 / MOD_OLED | JST B4B-PH-K-S / DFRobot DFR0486 | `Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical`; module is cable mounted | PH2.0-4P connector; DFR0486 41.20 x 26.20 body, 35 x 20 mounting-hole centers, pin order VCC/GND/SCL/SDA | Selected; verify cable keying and enclosure display position during fit check |
| L1 | Sunlord WPN4020H2R2MT | `A3_Control_Center:WPN4020H` | 4.0 x 4.0 x 2.0 mm body; manufacturer recommended 1.1 x 3.7 mm pads at 3.0 mm center spacing | **Independent dimensional audit complete 2026-10-05.** Project-local land pattern follows WPN4020H series specification Rev.08; not documented AEC-Q200 |
| L2 | Coilcraft XGL4020-152MEC | `Inductor_SMD:L_Coilcraft_XxL4020` | 4.0 x 4.0 x 2.1 mm body; Coilcraft identifies XGL4020 as the XFL4020 drop-in family and retains the 0.98 x 3.4 mm pads at 2.37 mm centers | Selected under D079; no footprint or routing change |
| C1 | PSA FV32N472J102EFG | `Capacitor_SMD:C_1210_3225Metric` | PSA FV-series ordering code: 1210, 3.30 +/-0.40 x 2.50 +/-0.30 x 2.00 +/-0.20 mm, 4.7 nF, 1 kVDC, C0G, +/-5% | Selected for Revision A under D078; existing generic 1210 land pattern remains suitable; commercial/non-AEC-Q200 qualification is accepted for prototypes |
| C63 | Panasonic EEEFK0J471GP | `Capacitor_SMD:CP_Elec_8x10` | 8.0 mm diameter, 10.2 mm height; 470 uF/6.3 V | Selected DNP option; final Panasonic land-overlay and polarity check required |
| SW1, SW2, SW3 | E-Switch TL3301NF260QG | `Button_Switch_SMD:SW_Push_1P1T_NO_E-Switch_TL3301NxxxxxG` | E-Switch P010517: 6.00 mm square body, 11.20 x 5.90 mm pad extents, 7.00 x 3.10 mm pad-center pattern, 4.40 mm maximum height | **Same-family substitution audited 2026-10-04.** Mechanical envelope and recommended PCB layout match the former TL3301NF160QG drawing; only operating force and actuator color change |

## Manufacturing rules

- Do not replace Phoenix 1715734 with `MKDS 1,5/3-B-5,08`; the `B` device has
  internally connected positions and would short CANH, CANL, and GND.
- TPS63070 custom-pad polygons and paste apertures must be reviewed in Gerber,
  not only in the footprint editor.
- J60 now uses four round plated holes from the Same Sky drawing, eliminating
  the former Kycon plated-slot DFM exception. Confirm all three duplicated pin-1
  shell stakes are present in drill and assembly outputs.
- A 1:1 paper or acetate fit check is required for every THT connector before
  release.
- The U10 antenna keepout is functional copper/RF geometry, not documentation;
  do not move the module inward, add copper, or place enclosure metal above the
  antenna region without repeating the RF review.
