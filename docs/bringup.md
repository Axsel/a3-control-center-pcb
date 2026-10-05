# Revision A bring-up plan

1. Inspect assembly, polarity, QFN exposed pads, connector pin numbering, antenna
   keepout, solder bridges, and unpopulated configuration links.
2. Confirm the fitted module marking is ESP32-WROOM-32E-N4 and inspect its
   thermal ground land and antenna keepout, then measure resistance from
   protected 5 V, 3.3 V, and +5V_FT to
   ground; compare against a recorded golden-board baseline.
3. Power protected 5 V from a current-limited bench supply before connecting a
   computer. Ramp current limit and check heating.
4. Verify 3.3 V and +5V_FT accuracy, startup, ripple, and ESP32 load transients.
5. Connect USB through a current meter; verify enumeration, CP2102N TX/RX, and
   no VBUS backfeed while unpowered.
6. Verify manual BOOT/EN and automatic DTR/RTS programming, including the modem-
   signal combination that must not hold reset indefinitely.
7. Flash minimal GPIO-safe firmware and validate all test points.
8. Fit the approved OLED module; scan I2C, display a static pattern, and verify
   the effective pull-up resistance.
9. Test CAN_HS first without termination, then with the 120 ohm link only in a
   valid two-end network. Measure differential waveform and error counters.
10. Read/write MCP2515 registers, confirm the 16 MHz oscillator and interrupt,
    then run internal/controlled loopback.
11. Verify TJA1055 mode pins, RXD and ERR pull-ups, +5V_FT, distributed
    termination, and 125 kbit/s communication on a real ISO 11898-3 network.
    JP40 and JP41 must remain open or be bridged together; never enable only
    one line termination.
12. Probe raw GPIO25 into high impedance only; check DAC levels and DMA timing.
13. Fit the default video driver path (JP60 bridged; JP61/JP62 open) and test
    into a precision 75 ohm termination. Never close multiple video-path
    jumpers simultaneously.
14. Build and flash `firmware/video/bench` using its pinned ESP-IDF v4.4.8
    environment. Start with PAL black, then white, grayscale bars, and
    checkerboard. Black is the initial sync/blanking test; do not infer output
    amplitude from an unterminated scope input.
15. Verify on a known monitor/capture device, then the JVC KD-X560BT.
16. Stress video while both CAN buses, Wi-Fi, and Bluetooth are active; log DMA
    underruns, CAN errors, resets, rail droop, and visible artifacts.

## Composite-video bench procedure

1. Confirm JP60 is closed, JP61 and JP62 are open, R60=33 Ω, C60=100 nF,
   R62=75 Ω, and no solder bridge selects a second output path.
2. With no RCA cable attached, power from the current-limited supply and verify
   U60's 3.3 V supply and absence of abnormal heating.
3. Flash the default PAL build. Probe TP13/TP60 using a high-impedance scope
   input and verify the approximately 64 µs line period and 4.7 µs sync width.
4. Connect the intended RCA cable to a precision 75 Ω termination at its far
   end. Probe TP62 at that termination. Expect approximately 1.0 Vpp total and
   0.3 V sync depth; use the limits and result table in `docs/video.md`.
5. Select black, white, bars, and checkerboard one build at a time. Record TP13,
   TP61, and terminated TP62 captures if levels or clamp settling are suspect.
6. Select NTSC in `idf.py menuconfig`, rebuild, and repeat timing/amplitude
   measurements. Test both standards on a known-good composite sink before the
   JVC head unit.
7. Test the JVC with a safe bench harness and its camera/reverse-trigger input
   configured per the JVC manual. The RCA carries only CVBS and ground.
8. Only after a stable unloaded test, add worst-case dual-CAN traffic. Then test
   Wi-Fi and Bluetooth separately and together while watching video jitter,
   CAN error counters, reset cause, and 3.3 V ripple.

No physical video-validation item is passed by the successful firmware build.

Do not connect the prototype to an in-vehicle network until bench fault tests,
ground-offset review, and connector/protection checks pass.
