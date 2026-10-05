# ESP32 GPIO allocation

This table is the ESP32-WROOM-32E-N4 hardware/firmware contract for Revision A.
It avoids all flash-connected GPIO6–GPIO11 (which are not brought out on 32E),
keeps the five strapping pins free of circuitry
that can alter boot state, and uses input-only pins only as inputs. Any change
must also change `firmware/pinmap.h`.

| GPIO | Name | Direction | Function | Safety rationale |
|---:|---|---|---|---|
| 0 | `BOOT` | input | Manual/automatic download strap | Required strap; 10 k pull-up, button/transistor only pull low |
| 1 | `UART0_TX` | output | ESP32 debug/program TX to CP2102N RX | Boot log is expected; test point provided |
| 3 | `UART0_RX` | input | CP2102N TX to ESP32 program RX | Dedicated UART0; test point provided |
| 4 | `CAN_FT_CS` | output | MCP2515 chip select | Non-strap; external/default high; right-edge module pin simplifies SPI routing |
| 13 | `CAN_FT_INT` | input | MCP2515 active-low interrupt | Non-strap; external pull-up; lower-edge module pin simplifies routing |
| 14 | `EXP_GPIO14` | I/O | Expansion spare | Non-strap; header only |
| 16 | `CAN_HS_TX` | output | TWAI TX to TCAN332 TXD | GPIO matrix capable; non-strap |
| 17 | `CAN_HS_RX` | input | TCAN332 RXD to TWAI RX | GPIO matrix capable; non-strap |
| 18 | `CAN_FT_SCK` | output | MCP2515 SPI clock | VSPI conventional pin; non-strap |
| 19 | `CAN_FT_MISO` | input | MCP2515 SPI SO | VSPI conventional pin; non-strap |
| 21 | `OLED_SDA` | I/O OD | SSD1306 I2C data | Non-strap |
| 22 | `OLED_SCL` | output OD | SSD1306 I2C clock | Non-strap |
| 23 | `CAN_FT_MOSI` | output | MCP2515 SPI SI | VSPI conventional pin; non-strap |
| 25 | `VIDEO_DAC` | analog out | DAC1 composite source | Reserved; I2S0/DAC DMA candidate |
| 26 | `DAC2_RESERVED` | analog out | Future audio/alternate video | Not connected to ordinary loads; test pad optional |
| 27 | `STATUS_LED` | output | Active-high LED through resistor | Non-strap; relocated LED load does not affect boot |
| 32 | `CAN_FT_STB` | output | TJA1055 standby control | Non-strap; hardware default selects a safe non-driving mode |
| 33 | `CAN_FT_EN` | output | TJA1055 enable control | Non-strap; hardware default selects a safe non-driving mode |
| 34 | `EXP_GPIO34` | input | Expansion/test-point spare | Input-only; no boot-strap effect |
| 35 | `CAN_FT_ERR` | input | TJA1055T/3 open-drain error/wake | Input-only is appropriate; external 3.3 V pull-up required |
| 36 | `USER_BUTTON` | input | Optional active-low user button | Input-only; external pull-up required |

## Deliberately unused/restricted

| GPIO | Reason |
|---:|---|
| 2, 5, 12, 15 | Boot strapping pins; held free for Revision A |
| 6–11 | Connected to module SPI flash; never expose or allocate |
| 26 | Preserved as DAC2/future audio unless review explicitly releases it |
| 39 | Input-only spare; may be exposed at a test pad after layout review |

EN is not a GPIO allocation. It receives the Espressif-recommended pull-up/RC,
manual reset button, auto-program transistor network, and a test point.

## Resource conflicts

- Composite video consumes DAC1, I2S0's DAC path, DMA bandwidth, and realtime
  scheduling capacity. It does not consume the VSPI pins or TWAI hardware.
- Wi-Fi/Bluetooth can preempt CPU time and disturb video timing even with DMA;
  coexistence is a validation item, not a guaranteed feature.
- MCP2515 SPI should initially run conservatively (for example 8 MHz or less),
  below its 10 MHz datasheet limit, until signal integrity is measured.
