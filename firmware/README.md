# Firmware interface contract

Target module: `ESP32-WROOM-32E-N4`. This remains a classic dual-core ESP32, so
the move from the originally requested ESP32-WROOM-32 does not change GPIOs,
peripheral drivers, flash size, DAC video method, or firmware target selection.

- `CAN_HS`: ESP32 TWAI on GPIO16/GPIO17. Bus speed is application-defined and
  must match the attached ISO 11898-2 network.
- `CAN_FT`: MCP2515 on VSPI with a 16 MHz crystal, separate CS and active-low
  interrupt. TJA1055T/3 supports up to 125 kbit/s; start bring-up at 125 kbit/s
  only when the network termination is known.
- OLED: DFRobot DFR0486 over I2C on GPIO21/GPIO22, address 0x3C. Verify bus
  discovery during bring-up before initializing the framebuffer.
- Programming/debug: UART0 through CP2102N; automatic DTR/RTS plus manual BOOT
  and EN.
- Composite video: GPIO25 DAC1 using I2S0/DAC continuous DMA. PAL monochrome is
  the first target; NTSC remains a required option. Start with test patterns.
- GPIO26 remains reserved as DAC2/future audio or alternate video.

Include `pinmap.h` rather than duplicating raw GPIO numbers in application code.
Initialize TJA1055 mode GPIOs to the safe state before enabling MCP2515 traffic.
