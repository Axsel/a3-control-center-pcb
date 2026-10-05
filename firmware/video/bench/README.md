# Composite-video bench target

This isolated ESP-IDF target generates a static PAL or NTSC test signal on
DAC1/GPIO25. It exists to validate Revision A's THS7314/75-ohm output stage; it
is not yet the production application.

## Dependency and license boundary

`fetch-dependencies.sh` fetches aquaticus' `esp32_composite_video_lib` at exact
commit `a1f5c7669aa274f148157947cdb7c94459e23777`. The dependency is
GPL-3.0-or-later and its fetched directory is ignored by this repository. Any
distributed firmware image linked with it must comply with the GPL. The final
product firmware may either comply with that license or replace the bench
implementation after hardware feasibility is proven.

The dependency directly controls classic-ESP32 I2S0/APLL/DAC registers and was
tested upstream with ESP-IDF 4.4. Use the final 4.4 release, ESP-IDF v4.4.8, for
this reproducibility target. Do not assume it builds unchanged on ESP-IDF 5.x.

## Build and flash

```sh
./fetch-dependencies.sh
. /path/to/esp-idf-v4.4.8/export.sh
idf.py set-target esp32
idf.py build
idf.py -p /dev/your-serial-device flash monitor
```

In this project container, ESP-IDF v4.4.8 and its ARM64 tools are installed in
the ignored `.tools/` directory. From the repository root, the wrapper avoids
manual environment setup:

```sh
scripts/idf44.sh firmware/video/bench build
scripts/idf44.sh firmware/video/bench -p /dev/your-serial-device flash monitor
```

The serial device must be passed through to the container. Alternatively, use
an ESP-IDF v4.4.8 installation on the macOS host to flash the same project.

The default is 320x200 PAL with eight-step grayscale bars. Run
`idf.py menuconfig`, then use `A3 video bench` to select PAL/NTSC and black,
white, grayscale bars, or checkerboard. Rebuild after changing the selection.

The library uses I2S0 DMA at 7.375 MHz for the selected PAL mode and 6.136 MHz
for NTSC. It always outputs through DAC channel 1, so the compile-time assertion
will fail if `firmware/pinmap.h` stops assigning video to GPIO25.

## Known upstream caveat

Do not call the upstream `video_test_ntsc(VIDEO_TEST_PM5544)` helper: at the
pinned commit its NTSC PM5544 case mistakenly initializes `VIDEO_MODE_PAL`.
This target uses `video_graphics()` and fills its own framebuffer, avoiding that
path and the bundled test-image assets.

See [`BUILD-VERIFICATION.md`](BUILD-VERIFICATION.md) for the exact toolchain,
commits, image sizes, and hashes from the verified PAL and NTSC builds.
