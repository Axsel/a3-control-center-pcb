# Power budget

These are allocation figures, not measured consumption. They deliberately give
the ESP32 a 500 mA transient allowance. Rev A must be measured during bring-up.

## 3.3 V rail

| Load | Typical | Plausible worst case | Basis |
|---|---:|---:|---|
| ESP32-WROOM-32E-N4 | 160 mA | 500 mA | Wi-Fi activity; 500 mA design allowance for supply transients |
| TCAN332 | 2 mA | 70 mA | Recessive vs loaded dominant/short transient allocation |
| MCP2515 at 16 MHz | 5 mA | 10 mA | Datasheet typical/max operating allocation |
| DFRobot DFR0486 SSD1306 module | 22.75 mA | 30 mA | Manufacturer full-screen figure; 30 mA design allowance includes variation |
| CP2102N | 10 mA | 15 mA | Typical bridge current plus margin |
| THS7314 and video load | 16 mA | 30 mA | Datasheet quiescent plus line-drive allowance |
| LEDs, pull-ups, misc. | 4 mA | 24 mA | Conservative LED currents and expansion margin |
| **Total** | **217 mA** | **689 mA** | **0.72 W typical, 2.27 W peak** |

Selected `TPS62132RGTR` is a fixed 3.3 V, 3 A synchronous buck. Its rating is
well above the estimated peak, which leaves transient and future-expansion
margin. Use the current TI reference values (nominal 2.2 uH, 10 uF input,
22 uF output as a starting point), add local ESP32 bulk capacitance, and verify
stability, DC bias derating, ripple, and layout against the current datasheet.
Revision A uses Sunlord `WPN4020H2R2MT` for L1: 2.2 uH +/-20%, 4.3 A rated
current, 6.1 A minimum/7.6 A typical saturation current, and 48 mOhm maximum
DCR. It exceeds TI's 3.8 A recommended-current entry for the 2.2 uH option and
has ample margin over the estimated 689 mA board peak. It is not documented as
AEC-Q200 and is therefore a prototype sourcing choice, not an automotive
qualification claim.

## 5 V fault-tolerant CAN rail

| Load | Typical | Plausible worst case |
|---|---:|---:|
| TJA1055T/3 VCC + BAT | 13 mA | 30 mA |

The TJA1055 VCC range is 4.75–5.25 V and BAT operating minimum is 5.0 V. USB
VBUS may legally be 4.75 V before any board loss. A `TPS63070RNMR` buck-boost
set to 5.0 V therefore generates `+5V_FT`; raw VBUS is not used as an in-spec
TJA1055 supply. The large current capability is not needed, but the part is
active, regulates above/below 5 V, and provides comfortable headroom.

## USB input estimate

Assuming 90% typical and 85% peak 3.3 V conversion efficiency, plus FT rail
losses:

- typical input: approximately 180 mA at 5 V;
- plausible simultaneous peak: approximately 570 mA at 5 V;
- required source rating: 5 V at 1.0 A or greater.

The peak estimate exceeds legacy USB 2.0's 500 mA configured-current ceiling.
Revision A therefore requires a USB source rated at least 5 V / 1 A and is not
guaranteed to operate reliably from an unconfigured 500 mA legacy port. The
USB-UART remains a USB 2.0 device and no USB-PD negotiation is implemented.
This limitation must appear in the silkscreen/user documentation and must be
checked during bring-up under simultaneous radio, CAN, OLED, and video load.

Use `TPS2553DBVR` after VBUS for controlled rise, adjustable current limiting,
fault indication, and reverse-voltage protection. The current limit is set by
28.7 kΩ to approximately 0.901 A nominal (approximately 0.833–0.979 A device
range before resistor tolerance) from the current TI equations. Add
connector-side ESD, input/output bulk
capacitors selected within USB inrush constraints, and test points on protected
5 V and 3.3 V. Do not add a redundant resettable fuse unless the final safety
review shows a benefit over the active limiter.

## Decoupling intent

- 100 nF at every IC supply pin/group, with datasheet-required bulk parts.
- ESP32: local 10 uF plus 100 nF at the module and 47–100 uF low-ESR bulk nearby,
  validated against USB inrush and regulator transient response.
- TJA1055: 100 nF at VCC and BAT filtering per NXP application circuit.
- THS7314: 100 nF directly at supply plus local bulk; keep its return out of
  switching-current loops.

References: https://www.ti.com/product/TPS62132,
https://www.ti.com/product/TPS63070, https://www.ti.com/product/TPS2553,
and https://www.nxp.com/docs/en/data-sheet/TJA1055.pdf.
