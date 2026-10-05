# Build verification

Verified in the project container on 2026-10-04.

| Item | Value |
|---|---|
| ESP-IDF release | v4.4.8 |
| ESP-IDF commit | `e499576efdb086551abe309a72899302f82077b7` |
| Video library commit | `a1f5c7669aa274f148157947cdb7c94459e23777` |
| Target | classic ESP32 |
| Compiler | xtensa-esp32-elf GCC 8.4.0, Espressif 2021r2-patch5 |
| Optimization | performance (`-O2`) |
| Default pattern | eight-step grayscale bars, 320x200, 8 bpp |

Both configurations compile and link successfully:

| Configuration | Image size | SHA-256 |
|---|---:|---|
| PAL | 0x2cf10 bytes | `d1390f5944b104a0cec7de63bd4e94f4f5d92908237f9debbe6db311252c94da` |
| NTSC | 0x2cf10 bytes | `baee9ba4f30faf86e06f595e99aebe7f92f08fb2ea6f8f21128bb96ddec2d337` |

The PAL ELF contains only the selected PAL startup message; the separately
configured NTSC ELF contains the selected NTSC startup message. Build artifacts
remain ignored. This record establishes source/tool compatibility, not correct
analog output or display compatibility.
