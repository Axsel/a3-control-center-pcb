# KiCad toolchain

The macOS host and Linux container both target **KiCad 10.0.6**. The container
has the official Flathub aarch64 build installed system-wide with its matching
symbols, footprints, templates, and 3D models.

Docker blocks the namespace creation normally performed by `flatpak run`.
The project wrapper invokes the installed executable with its matching runtime
loader directly:

```sh
./scripts/kicad-cli version
./scripts/kicad-cli sch erc hardware/dual_can_esp32.kicad_sch
./scripts/kicad-cli pcb drc hardware/dual_can_esp32.kicad_pcb
```

The wrapper also exports the KiCad 10 official-library variables. It assumes
the current aarch64 Flatpak layout and GNOME SDK 51 runtime; rerun the toolchain
validation after any Flatpak update.

## Installed container resources

- Application: `org.kicad.KiCad`, stable, aarch64, version 10.0.6
- Symbols: `org.kicad.KiCad.Library.Symbols`
- Footprints: `org.kicad.KiCad.Library.Footprints`
- 3D models: `org.kicad.KiCad.Library.Packages3D`
- Templates: `org.kicad.KiCad.Library.Templates`
- Project command wrapper: `scripts/kicad-cli`
- Application-resource compatibility link: `/app` points to the active KiCad
  Flatpak deployment so hard-coded schema lookups resolve.
- Runtime compatibility links for `_eeschema.kiface`, `_pcbnew.kiface`, and
  `_cvpcb.kiface` point back to the application plugins. These are needed
  because direct loader execution makes KiCad infer the runtime as its prefix.

## Still needed from the host/user for Phase 2

- JLCPCB is selected; its locked Revision A order parameters are recorded in
  `manufacturing/jlcpcb-order-parameters.md` and must be reconfirmed at order time.
- Whether host-global third-party libraries are in use. Project-local libraries
  are preferred for reproducibility.
- Confirmation that standard KiCad 10 libraries are acceptable. Any required
  third-party library should be copied into a project-local library.

## Validation gate

Before drawing circuitry, run and record:

```text
./scripts/kicad-cli version
symbol library discovery
footprint library discovery
creation/open/save of a minimal project
headless ERC and DRC on that minimal project
```

After project files exist, the host KiCad application remains the visual review
authority. Container checks complement visual inspection of the schematic,
footprints, placement, routing, and 3D view.

Validation on 2026-10-02 used the installed `StickHub` demo: both headless ERC
and headless DRC completed with zero violations. This proves the schematic and
PCB engines can load and execute; project-specific ERC/DRC begins in Phase 2.
