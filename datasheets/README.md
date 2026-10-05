# Datasheet and reference index

Primary sources checked for Phase 1 (accessed 2026-10-02):

| Item | Revision/status | URL |
|---|---|---|
| ESP32-WROOM-32 (original request) | v3.8, NRND; superseded in this design | https://documentation.espressif.com/esp32-wroom-32_datasheet_en.html |
| ESP32-WROOM-32E/32UE | v2.1; selected 32E-N4 | https://documentation.espressif.com/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.html |
| Espressif GPIO/module migration FAQ | recommends WROOM-32E/32UE over WROOM-32/32D/32U | https://docs.espressif.com/projects/esp-faq/en/latest/software-framework/peripherals/gpio.html |
| ESP32 hardware guidelines | current | https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html |
| TCAN33x | Rev F, May 2025 | https://www.ti.com/lit/ds/symlink/tcan332.pdf |
| MCP2515 | DS20001801K, 2021 | https://ww1.microchip.com/downloads/en/DeviceDoc/MCP2515-Family-Data-Sheet-DS20001801K.pdf |
| TJA1055 | Rev 5 | https://www.nxp.com/docs/en/data-sheet/TJA1055.pdf |
| TJA1055 application hints | Rev 1.5 | https://www.nxp.com/docs/en/application-note/AH0801.pdf |
| PESD2CAN24T-Q | 9 February 2024; selected | https://assets.nexperia.com/documents/data-sheet/PESD2CAN24T-Q.pdf |
| ABM3BAIG-16.000MHZ-12-2-T | active, AEC-Q200; selected | https://abracon.com/parametric/crystals/ABM3BAIG-16.000MHZ-12-2-T |
| CP2102N | Rev 1.5 | https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf |
| TPS62132 | active | https://www.ti.com/lit/ds/symlink/tps62132.pdf |
| TPS63070 | active | https://www.ti.com/product/TPS63070 |
| TPS2553 | active | https://www.ti.com/lit/ds/symlink/tps2553.pdf |
| THS7314 | active, Rev A | https://www.ti.com/lit/ds/symlink/ths7314.pdf |
| PESD5V0U1BA-Q | 3 May 2022; selected for video | https://assets.nexperia.com/documents/data-sheet/PESD5V0U1BA-Q.pdf |
| HXY HPESD5V0U1BA-Q | 2025-04-03 catalog datasheet; selected Revision A prototype substitute for D60 | https://datasheet.lcsc.com/datasheet/pdf/e7458a6d3eb28a9711b7018a1df1410e.pdf?productCode=C25503782 |
| USBLC6-2 | active | https://www.st.com/en/protections-and-emi-filters/usblc6-2.html |
| GCT USB4105 | active | https://gct.co/connector/usb4105 |
| Kycon KLPX RCA | current drawing | https://www.kycon.com/2013Catalogpage/RCA/KLPX.pdf |
| Kycon KLPX-0848A-2-x engineering drawing | Rev A7, 2020-12-10 | https://www.kycon.com/Pub_Eng_Draw/KLPX-0848A-2-x.pdf |
| Same Sky RCJ-01 RCA family | selected RCJ-014; drawing dated 2026-08-12 | https://www.sameskydevices.com/product/resource/rcj-01.pdf |
| Phoenix Contact CAN terminal block | 1715734, MKDS 1,5/ 3-5,08 | https://www.phoenixcontact.com/en-pc/products/pcb-terminal-block-mkds-15-3-508-1715734 |
| DFRobot DFR0486 OLED | active module documentation | https://wiki.dfrobot.com/dfr0486/ |
| TDK CGA6M1C0G3A472G200AC | production, AEC-Q200 | https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA6M1C0G3A472G200AC |
| KEMET high-voltage C0G SMD | C1009, 2023-08-18; C1210C472JDGACTU evaluated but not selected | https://content.kemet.com/datasheets/KEM_C1009_C0G_SMD.pdf |
| PSA FV high-voltage MLCC series | FV-000-001-25, 2022-10-12; selected C1 FV32N472J102EFG / C5156737 | https://www.rxelectronics.pt/datasheet/f0/fv42x102k302efg.pdf |
| E-Switch TL3301NF260QG | P010517 Rev E; selected for SW1-SW3 | https://www.lcsc.com/product-detail/C273528.html |
| Bourns SRP4020FA | selected L1 SRP4020FA-2R2M | https://www.bourns.com/docs/Product-Datasheets/SRP4020FA.pdf |
| Coilcraft XGL4020 | selected L2 XGL4020-152MEC | https://www.coilcraft.com/getmedia/76c9c081-4945-4c85-9129-9356e1ad6734/xgl4020.pdf |
| Panasonic EEE-FK | selected optional EEEFK0J471GP | https://na.industrial.panasonic.com/products/capacitors/aluminum-electrolytic-capacitors/series/88994 |
| JVC Europe manual | B5A-2954-10 b | https://manuals.jvckenwood.com/download/files/B5A-2954-10b_E_ENG.pdf |
| JLCPCB manufacturing capabilities | live service specification | https://jlcpcb.com/capabilities/Capabilities |
| JLCPCB PCBA capabilities | live service specification | https://jlcpcb.com/capabilities/pcb-assembly-capabilities |
| JLCPCB multilayer structures | live service specification | https://jlcpcb.com/help/article/multi-layer-pcb-standard-laminated-structures |

Do not commit downloaded PDFs without checking redistribution terms and the need
for an immutable design archive. Record checksums and revision dates if local
copies are later approved.

## Phase 2 pin-audit record

- `TJA1055T/3`: NXP Rev. 5 Table 3 checked. Pin sequence is INH, TXD, RXD,
  ERR, STB, EN, WAKE, RTH, RTL, VCC, CANH, CANL, GND, BAT.
- `THS7314DR`: TI SLOS513A pin table checked. Pins 1-3 are channel inputs,
  pin 4 is VS+, pin 5 is GND, and pins 6-8 are channel outputs 3-1.
- `TPS63070RNMR`: TI SLVSC58B pin table and RNM0015A package drawing checked.
  The package is an asymmetric 15-pin VQFN-HR and must not use a generic
  rectangular QFN footprint.
- `TPS2553DBV`: TI SLVS841F pin table checked: 1 IN, 2 GND, 3 active-high EN,
  4 active-low open-drain FAULT, 5 ILIM, and 6 OUT.
- `TPS62132RGT`: TI drawing RGT0016C checked: 3.0 x 3.0 mm body, 0.5 mm pitch,
  and 1.68 x 1.68 mm exposed pad. The matching official KiCad footprint is
  selected.
- `TPS63070RNMR`: TI drawing 4222000/B was inspected in addition to the pin
  table. Pins 1-6, 14, and 15 use ordinary NSMD lands; pins 7-13 use unusual
  solder-mask-defined copper. A generic QFN footprint is prohibited.
- `TCAN332DR`: TI Rev F pin table checked: 1 TXD, 2 GND, 3 VCC, 4 RXD,
  5/8 NC, 6 CANL, and 7 CANH.
- `MCP2515-I/SO`: Microchip DS20001801K SOIC-18 pin table checked. VDD is
  2.7-5.5 V; the selected 3.3 V supply is valid and SPI remains below 10 MHz.
- `PESD2CAN24T-Q`: Nexperia pin table and CAN application checked. Pins 1/2
  are the two bus-line terminals and pin 3 is the common transient return.
- `ABM3BAIG-16.000MHZ-12-2-T`: Abracon product data checked: 16 MHz
  fundamental, 12 pF load, 50 Ω ESR, four-pad 5032 package; pads 2/4 are case
  ground and pads 1/3 are the resonator terminals.
- `PESD5V0U1BA-Q`: Nexperia data checked: SOD323, bidirectional, 5 V
  standoff, 2.9 pF typical/3.5 pF maximum capacitance at 0 V, AEC-Q101, and
  listed for audio/video equipment.
- `RCJ-014`: Same Sky RCJ-01 drawing checked. Manufacturer pin 1 is the shell
  and uses three 2.6 mm PCB holes; pin 2 is the RCA center contact and uses a
  1.7 mm hole positioned 4.5 mm forward. The local footprint preserves this
  numbering and geometry.
- `Phoenix Contact 1715734`: current product data checked: three independent
  potentials, 5.08 mm pitch, 15.24 mm width, 0.9 x 0.9 mm pins, 1.3 mm PCB
  holes, and 3.5 mm solder-pin length. KiCad 10's dedicated footprint matches
  the pitch, body width, hole, and pad dimensions. The `-B-` variant is not a
  substitute because its potentials are internally connected.
- `DFRobot DFR0486`: manufacturer wiki, schematic V1.0, and dimension drawing
  checked. The module is 41.20 x 26.20 mm with 35 x 20 mm mounting centers,
  accepts 3.3-5 V, uses I2C address 0x3C, and specifies about 22.75 mA at full
  screen. Connector order is VCC, GND, SCL, SDA. Its schematic shows onboard
  10 kΩ pull-ups and level shifting, so R24/R25 remain DNP.
- `PSA FV32N472J102EFG`: selected Revision A C1, 1210 high-voltage MLCC,
  4.7 nF, 1 kVDC, C0G, +/-5%, 3.30 x 2.50 x 2.00 mm nominal. It preserves the
  electrical and land-pattern requirements but is commercial/non-AEC-Q200;
  the former TDK automotive part remains the preferred production upgrade.
- `Bourns SRP4020FA-2R2M`: selected 2.2 uH TPS62132 inductor, AEC-Q200,
  23.5 mOhm maximum DCR, and 3.8 A Isat at 20% inductance drop. The local
  footprint implements Bourns' 3.8 x 1.4 mm recommended lands.
- `Coilcraft XGL4020-152MEC`: selected 1.5 uH TPS63070 inductor. Coilcraft
  documents XGL4020 as the value-for-value XFL4020 drop-in family; the existing
  `L_Coilcraft_XxL4020` land pattern remains valid.
- `Panasonic EEEFK0J471GP`: current EEE-FK listing checked: 470 uF, 6.3 V,
  8.0 mm diameter, 10.2 mm length, -55 to 105 C. It is DNP by default and only
  supports the optional video output AC-coupling experiment.
