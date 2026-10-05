# Scripts

- `kicad-cli`: runs the installed KiCad 10.0.6 CLI with the matching Flatpak
  runtime and official-library paths inside this container.
- `kicad-gui`: runs KiCad 10.0.6 against the container X display; normally used
  only for project-managed operations unavailable in `kicad-cli`, such as
  Update PCB from Schematic.
- `kicad-python`: exposes KiCad 10.0.6's `pcbnew` Python module from the matching
  Flatpak runtime.
- `place_pcb.py`: deterministic Revision A first-pass placement for all 130
  electrical footprints and four board-only M3 mounting holes. It creates no
  tracks or zones. It resets every footprint position, so do not run it after
  manual routing begins without deliberately discarding those placement edits.
- `route_critical.py`: idempotently replaces only the four USB data-net routes.
  It implements the reviewed Type-C orientation-contact crossovers, ESD-array
  path, and CP2102N connection. KiCad 10 requires `BOARD.Delete()` for replaced
  tracks; using `Remove()` can crash before the board is saved.
- `route_power_clock.py`: idempotently replaces the TPS62132 switch-node route
  and MCP2515 oscillator routes. It deliberately leaves shared rails and GND
  untouched.
- `route_local_power.py`: replaces a named KiCad group containing both converter
  local loops, feedback/soft-start wiring, local output distribution, and the
  associated L2 ground drops.
- `route_5v_distribution.py`: replaces a named KiCad group containing the L3
  protected-USB and 5V_FT trunks, TJA1055 supply escapes, and supply-capacitor
  ground drops.
- `route_3v3_distribution.py`: replaces a named KiCad group containing the
  0.8 mm +3V3 distribution tree, short bottom-layer crossings at the 5 V
  corridor, primary IC supply escapes, and local bypass-capacitor ground drops.
- `route_can_hs.py`: replaces a named KiCad group containing the complete
  ESP32-TWAI-to-TCAN332 logic routes, CANH/CANL connector routes, TVS ground,
  and selectable 120 ohm termination. TP21 remains deferred to final cleanup.
- `route_can_ft_bus.py`: replaces a named KiCad group containing the TJA1055
  physical-layer routes, connector-side TVS return, J40 connection, and the
  two independently selectable ISO 11898-3 RTH/RTL termination branches.
- `route_can_ft_controller.py`: replaces a named KiCad group containing the
  local MCP2515 TXCAN/RXCAN links to the TJA1055. ESP32 SPI and mode/control
  signals are deliberately handled in a later routing pass.
- `route_can_ft_support.py`: replaces a named KiCad group containing the +3V3
  pull-up spine, STB/EN ground defaults, and the complete MCP2515 reset RC
  network and signal escape.
- `route_can_ft_control.py`: routes TJA1055 ERR/STB/EN between ESP32 and U41,
  including R43/R44/R45. It uses staggered L4 trunks, short L3 approaches, and
  one short L1 crossover where the RXCAN pull-up branch blocks EN.
- `route_can_ft_spi.py`: routes the reviewed partial ESP32-to-MCP2515 SPI
  bundle. MOSI uses an upper L3 corridor with an L4 controller approach; SCK
  uses L4 with two short L3 crossings; MISO uses a separate crossing lane and
  a short L3 approach beneath U40.
- `route_can_ft_select_irq.py`: completes MCP2515 CS and INT, including R50 and
  relocated R41. INT uses GPIO13 and a lower L4 corridor; CS uses GPIO4 and the
  clear L1 channel beneath U40. The GPIO/pull-up placements are defined by
  `generate_schematic.py` and `place_pcb.py`.
- `route_programming.py`: routes the complete CP2102N/ESP32 programming block:
  UART0 TX/RX, the crossed DTR/RTS two-NPN network, EN and GPIO0, their pullups,
  BOOT/RESET buttons, and TP6/TP7/TP10/TP11. Short L3 crossings preserve L2 as
  continuous ground. UART test points are placed beside the routed trunks to
  avoid long diagnostic stubs through the lower CAN-control corridors.
- `route_ui.py`: routes the GPIO27 status LED and the complete OLED interface.
  J10 power/ground, optional DNP R24/R25 pullups, and the long GPIO21/GPIO22
  SDA/SCL runs are complete. The I2C pair uses L3/B.Cu escape and perimeter
  corridors so the L2 ground plane remains uninterrupted. It also completes
  the GPIO user-button pullup, switch contact, and local ground return.
- `route_video.py`: routes the locally complete default composite-video chain:
  DAC-side R60/C60 fanout, THS7314 input/supply/grounds, buffered output,
  75-ohm R62 source path, ESD, RCA connector, and associated test points. It
  also routes the long GPIO25 feed and the isolated DNP AC-coupled and passive
  experiment branches without placing signals on L2.
- `route_final_cleanup.py`: runs last and idempotently closes audited auxiliary
  connections and local ground returns that span multiple functional blocks.
  It currently completes switch duplicate contacts, the 5V_FT test point,
  selected USB/power grounds, and remaining local/test-point joins while
  preserving the clean critical-route groups.
- `clean_silkscreen.py`: runs after routing and deterministically hides only
  crowded F.SilkS reference fields (their F.Fab/assembly references remain)
  and clips the redundant RCA body outline at its shield pads. Functional
  connector, polarity, and interface legends are retained.
- `export_jlc.py`: generates an explicit population manifest plus candidate
  JLCPCB BOM and full SMT/THT CPL files. It excludes the documented DNP parts,
  solder jumpers, test points, and mounting holes rather than trusting value
  text. All five physical connectors remain required BOM/CPL entries for JLC
  manual/wave assembly. Candidate files remain blocked until their readiness
  report has no open items and every BOM row has an approved live LCSC number.
- `render_gerber_review.sh`: uses independent gerbv rasterization to create
  separate copper/drill, mask, paste, legend, and inner-layer review images in
  the ignored audit package. gerbv 2.9.x logs unsupported KiCad X2 attributes;
  these are metadata warnings, not geometry parse failures.
- `add_zones.py`: idempotently creates and refills the named continuous In1.Cu
  (`GND plane`) zone with a 0.55 mm board-edge inset. Footprint keepouts remain
  authoritative, including the ESP32 antenna keepout.
- `requirements-schematic.txt`: pinned dependency for reproducible native
  KiCad schematic generation.
- `generate_schematic.py`: reviewed connectivity source for the KiCad
  hierarchy. Run from the repository root with the project venv and the local
  plus KiCad 10 symbol-library paths described in `docs/schematic-capture.md`.

For a clean deterministic rebuild before manual routing, run `place_pcb.py`,
`route_critical.py`, `route_power_clock.py`, `add_zones.py`,
`route_local_power.py`, `route_5v_distribution.py`, then
`route_3v3_distribution.py`, `route_can_hs.py`, `route_can_ft_bus.py`, then
`route_can_ft_controller.py`, `route_can_ft_support.py`, and
`route_can_ft_control.py`, `route_can_ft_spi.py`, and
`route_can_ft_select_irq.py`, followed by `route_programming.py`, `route_ui.py`,
`route_video.py`, `route_final_cleanup.py`, and finally `clean_silkscreen.py`,
all through
`scripts/kicad-python`. Do not rerun
`place_pcb.py` once manual placement edits exist. The grouped scripts replace
only their own objects. Future reproducible ERC/DRC checks, BOM generation,
pinmap consistency checks, and manufacturing exports also belong here.
