# Composite video feasibility

## Recommendation

Use GPIO25/DAC1 driven by I2S0 DMA, AC-couple into one channel of a THS7314,
then use the amplifier's fixed 2 V/V gain and a 75 ohm source resistor. With a
75 ohm receiver termination, the divider cancels the gain and the load sees the
DAC waveform amplitude: firmware should synthesize approximately 1.0 Vpp CVBS
at its DAC output codes. Add a low-capacitance ESD device at the RCA and keep a
short, ground-referenced analog path.

The selected `THS7314DR` is active, SOIC-8, runs at 3.3 V, includes an 8.5 MHz
5th-order SDTV reconstruction filter and sync-tip clamp, and is specified to
drive 75 ohm video lines. Use one channel. The two unused inputs/outputs require
a final connection rule from TI support/datasheet review before capture. Include
0 ohm/DNP footprints so the bench can compare buffered, passive, and alternate
coupling configurations without cutting traces.

```text
GPIO25/DAC1 -- small series option -- C_IN -- THS7314 clamp/filter/gain
                                          -- 75R source -- low-C ESD -- RCA center
Board GND ------------------------------------------------------------ RCA shell
```

The 75 ohm is source termination, not a local shunt. The JVC provides the 75 ohm
load. A local 75 ohm shunt would halve the level again and overload the driver.
Provision a DNP output coupling capacitor/bypass option only for experiments;
the default is DC output from the THS7314 after its input clamp. Verify sync tip,
blanking, black, white, and 1.0 Vpp at the far end of a cable with the actual
75 ohm load before freezing values.

This architecture is now captured on the video sheet. JP60 is bridged for the
default buffered DC output. The 470 µF output-coupling path and passive DAC path
are DNP behind normally-open JP61/JP62; the schematic explicitly forbids closing
more than one output path. `PESD5V0U1BA-Q` provides 2.9 pF typical bidirectional
ESD protection at the RCA in the original automotive-qualified selection.
Revision A prototypes instead fit `HPESD5V0U1BA-Q` / C25503782 because JLC
could not match the Nexperia device. The HXY part is bidirectional, 5 V,
SOD-323, and 2.5 pF maximum, so the expected video loading is acceptable. It is
not AEC-Q101-qualified and has a narrower -40 to +125 C operating range; retain
the Nexperia device as the preferred later-production choice. The RCA footprint
remains a mechanical drawing gate.

## Options assessed

| Option | Parts / PCB | Signal quality | Firmware / resources | Decision |
|---|---|---|---|---|
| A. Internal DAC + passive network | Lowest | DAC output impedance and 75 ohm sag are not adequately specified; short protection weak | I2S0 DMA, 8-bit levels | Keep as DNP experiment only |
| B. Internal DAC + filter/video driver | Moderate; one SOIC-8 plus passives | Defined 75 ohm drive, reconstruction filter, ESD and short-current isolation | Same as A | **Revision A recommendation** |
| C. Digital peripheral/resistor DAC + buffer | More GPIOs/resistors and matching sensitivity | Can improve level count but adds digital edge energy | More GPIO/I2S formatting; conflicts with pin budget | Not selected |
| D. External video DAC/encoder | Highest cost and sourcing burden | Best defined analog output; possible color support | Additional SPI/I2S and driver work | Not justified for simple UI |

## Electrical levels

The conventional target is 1.0 Vpp into 75 ohm, with approximately 0.3 V sync
below blanking/black and approximately 0.7 V picture range above black for
luma. PAL and NTSC differ primarily in timing and color encoding, not the basic
1 Vpp terminated interface. Exact code values cannot be finalized from the
ESP32 ideal transfer equation alone because DAC gain/offset, supply noise, and
loaded behavior vary. Calibrate code levels on the prototype.

Espressif documents an 8-bit DAC transfer from code 0–255 to nominal 0–Vref and
places DAC1/DAC2 on GPIO25/GPIO26. It does not provide a guaranteed 75 ohm line
drive specification. This is the reason direct connection is not the released
architecture.

## Generation method and resource estimate

ESP-IDF can connect the ESP32 DAC digital controller to I2S0 and continuously
feed it using DMA. Existing implementations demonstrate PAL and NTSC on GPIO25;
they are feasibility evidence, not electrical reference designs. Start with
monochrome/non-interlaced PAL, scanline buffers, and an application framebuffer.

Recommended first UI mode: 320x240 or 320x200, 1 bit/pixel. A 320x240 1-bpp
framebuffer is 9,600 bytes; 2 bpp is 19,200 bytes; 8 bpp is 76,800 bytes. Full
720x576 at 8 bpp would be 414,720 bytes before DMA, stacks, CAN buffers, or Wi-Fi
and is not a responsible target in 520 KiB SRAM. Color PAL/NTSC also needs phase-
accurate subcarrier synthesis and materially increases timing risk.

The sample stream is expected in the several-MHz range; one public ESP-IDF
implementation uses 13.5 MHz. DMA removes per-sample CPU writes but scanline
generation/refill deadlines remain. I2S0 is occupied. SPI, TWAI, UART, and I2C
remain separate peripherals, but interrupts and memory contention can still
cause artifacts. Wi-Fi/Bluetooth coexistence is **unproven** and should be
treated as best-effort until stress-tested.

### Reproducible Revision A bench implementation

`firmware/video/bench` now provides the first buildable test-pattern target.
It pins aquaticus' `esp32_composite_video_lib` commit
`a1f5c7669aa274f148157947cdb7c94459e23777` and ESP-IDF v4.4.8. The target
uses I2S0/APLL DMA into DAC1/GPIO25, a 320x200 8-bpp framebuffer, and selectable
PAL (7.375 MHz sample clock) or NTSC (6.136 MHz). It provides black, white,
eight-step grayscale, and checkerboard patterns without LVGL or the upstream
test-image assets.

This is a **bench feasibility implementation**, not an approved production
dependency. The library is GPL-3.0-or-later, directly accesses ESP32/IDF 4.4
registers, and has limited maintenance history. A distributed image linked
with it must comply with the GPL. After electrical validation, choose between
GPL-compliant product firmware and a separately implemented/approved renderer.

The pinned upstream source has a known defect in
`video_test_ntsc(VIDEO_TEST_PM5544)`: that case initializes PAL timing. The A3
bench application avoids all `video_test_*` helpers and calls the correctly
mapped `video_graphics()` PAL/NTSC modes directly.

Separate PAL and NTSC configurations were compiled successfully in this
repository with ESP-IDF v4.4.8 on 2026-10-04. Each application image is 0x2cf10
bytes (180 KiB), leaving 82% of the 1 MiB factory application partition free.
Their distinct embedded mode strings and SHA-256 hashes were verified. This
proves build compatibility only; no waveform or display acceptance is claimed
until real hardware is measured.

## JVC KD-X560BT compatibility

JVC documents a yellow rear-view-camera RCA input, a 320x240 display, and a
video input level of **1.0 Vp-p / 75 ohm**. The Europe and America manuals do
not state whether the camera input accepts PAL, NTSC, or both. Therefore:

- connector: confirmed RCA camera input;
- nominal level and impedance: confirmed 1.0 Vpp / 75 ohm;
- PAL acceptance: **UNKNOWN**;
- NTSC acceptance: **UNKNOWN**;
- DC coupling/clamp behavior: **UNKNOWN**.

PAL remains the first firmware target because of the deployment region, but
both formats must be bench-tested on the actual head unit before claiming
compatibility. For Revision A, the owner accepts performing that test after the
assembled boards arrive. The reverse-trigger wire is a head-unit installation
concern, not a proprietary signal on the RCA connector.

## Grounding and protection

RCA shell connects to the local ground plane near the video driver; do not
isolate it by default. A vehicle installation can create ground-loop current
between USB power ground and radio chassis. Test for visible hum bars and ground
offset. If observed, resolve system grounding or add an external video isolation
accessory; do not casually split the PCB plane under the signal.

## Deferred assembled-board experiment

The owner elected on 2026-10-04 to defer this experiment until assembled
Revision A boards arrive. This accepts the possibility of a video-stage rework
or Revision B change. It is not a passed validation result and does not relax
the following bring-up work:

1. Use the assembled Revision A board with its fitted ESP32-WROOM-32E,
   GPIO25 test points, and default video-path population.
2. Confirm JP60 is bridged and JP61/JP62 are open, then connect the onboard
   THS7314, 75 ohm source resistor, RCA cable, and a real 75 ohm load.
3. Generate sync-only, black, white, grayscale bars, and text in PAL, then NTSC.
4. Measure at a real 75 ohm load: amplitude, sync width, line/frame rate, rise
   time, DAC monotonicity, and supply-noise feedthrough.
5. Test a known composite monitor/capture device, then the KD-X560BT.
6. Repeat while TWAI and MCP2515 are busy and while Wi-Fi/Bluetooth are enabled.

### Measurement points and acceptance record

Use a short ground spring, not a long probe ground lead. First probe TP13 or
TP60 (`VIDEO_DAC`) with at least 1 MΩ input. The pinned reference generates DAC
codes 0/23/77 for nominal sync/black/white, corresponding ideally to roughly
0/0.30/1.0 V at 3.3 V Vref. These are diagnostic expectations, not guaranteed
ESP32 DAC limits.

With JP60 bridged and JP61/JP62 open, TP61 is the THS7314 output before R62 and
TP62 is the protected RCA node after the 75 Ω source resistor. TP61 or an
unterminated TP62 can show about twice the final amplitude. The released
acceptance measurement is TP62/RCA into a precision 75 Ω termination at the
far end of the intended cable:

| Test | PAL target | NTSC target | Rev A result |
|---|---:|---:|---|
| Total level, sync tip to white | 1.0 Vpp nominal; 0.9–1.1 Vpp initial acceptance | same | NOT TESTED |
| Sync tip to blanking/black | 0.30 V nominal; 0.25–0.35 V initial acceptance | same | NOT TESTED |
| Horizontal period | 64.0 µs, ±1% | 63.55 µs, ±1% | NOT TESTED |
| Horizontal sync width | 4.7 µs, ±10% | 4.7 µs, ±10% | NOT TESTED |
| Field period, non-interlaced reference | about 19.97 ms | about 16.65 ms | NOT TESTED |
| Eight grayscale steps monotonic | yes | yes | NOT TESTED |
| Known composite monitor locks | required | required | NOT TESTED |
| JVC KD-X560BT locks and displays stable image | required to claim compatibility | required to claim compatibility | NOT TESTED |

Record scope screenshots, cable length, termination location, 3.3 V rail,
firmware binary checksum, and fitted jumper/component values. If amplitude is
wrong, do not compensate in firmware until TP13, TP61, and TP62 have isolated
whether the error is DAC scaling, amplifier/clamp behavior, missing 75 Ω load,
or source-termination population.

## References

- ESP-IDF DAC/I2S DMA: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/dac.html
- TI THS7314: https://www.ti.com/lit/ds/symlink/ths7314.pdf
- JVC Europe manual: https://manuals.jvckenwood.com/download/files/B5A-2954-10b_E_ENG.pdf
- bitluni feasibility code: https://github.com/bitluni/ESP32CompositeVideo
- ESP-IDF 13.5 MHz example implementation: https://github.com/aquaticus/esp32_composite_video_lib
