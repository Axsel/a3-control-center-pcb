# Revision A fabrication-output review

Review date: 2026-10-05

Scope: the ignored `manufacturing/generated/rev-a-audit/` package generated
from `hardware/dual_can_esp32.kicad_pcb`. This is retained review evidence, not
authorization to order the board.

## Independent rendering

The Gerbers and Excellon drills were independently rasterized with gerbv 2.9.6
using `scripts/render_gerber_review.sh`. The ten images and parser logs are in
`manufacturing/generated/rev-a-audit/review/`.

gerbv 2.9.6 does not understand the KiCad 10 X2 `TF`, `TA`, `TO`, and `TD`
attributes and records warnings for that metadata. It nevertheless parses and
renders the underlying RS-274X geometry. KiCad's `.gbrjob` file remains the
authority for layer function and polarity; JLC's viewer must be checked again
before release. gerbv also labels the intentionally empty bottom paste and
bottom legend files as probable RS-274D; their emptiness was confirmed against
the board statistics and the absence of bottom-mounted components.

## Findings

- The closed outline is 100.0 x 70.0 mm in the board statistics. The 100.05 x
  70.05 mm job-file envelope includes half of the 0.05 mm profile stroke.
- Four positive copper layers are present in the correct order: F.Cu, continuous
  L2 GND, L3 power/slow signals, and B.Cu.
- L2 is continuous except for the intentional ESP32 antenna keepout extending
  to the top board edge. No signal track crosses the keepout.
- Front and back copper align with the PTH and NPTH drill data and remain inside
  the routed outline.
- Front solder-mask and paste apertures align with their pads. The custom U5
  split-paste pattern and ESP32 exposed-pad array are present.
- Bottom paste and bottom legend are intentionally empty because Revision A has
  no bottom-mounted components or bottom-side legend.
- Front legend is upright from the component side, contains connector/interface
  labels and polarity/orientation marks, and does not expose a new clipping or
  pad-overlap defect.
- Drill inventory is internally consistent: 306 plated holes, including four
  USB shell slots and two RCA slots, plus six NPTH holes (two J1 locators and
  four 3.2 mm mounting holes).
- The two J60 plated slots remain exactly 2.20 x 1.20 mm and 2.00 x 1.00 mm.
  Their geometry is correct, but the former still requires JLC DFM acceptance.
- Mask polarity is negative and all other exported layers are positive as
  declared in the Gerber job file.

## Result

No new fabrication-data defect was found. The independent visual Gerber/drill
review gate is closed for the current board revision. It must be repeated after
any PCB geometry, footprint, mask, paste, legend, outline, or drill change.
The Gerbers, drills, job file, statistics, and gerbv renders were refreshed
after synchronizing the embedded KiCad stackup to JLC's 7628 construction. The
project owner also reported the local visual review as acceptable on 2026-10-04.
They were refreshed again on 2026-10-05 after replacing L1 with the Sunlord
WPN4020H2R2MT manufacturer land pattern and moving the adjacent protected-5-V
via clear of its terminal. ERC and full-track DRC returned zero violations and
zero unconnected items after this change.

Open gates remain: JLC online DFM/viewer and final-quotation stackup confirmation,
C1 sourcing, stock reservation, mixed SMT/PTH handling for J1, physical
connector fit checks. Composite-video bench validation is deferred by owner
direction to assembled-board bring-up and is an accepted prototype risk rather
than a claim of compatibility.

For the physical connector checks, print
`manufacturing/generated/rev-a-audit/mechanical/connector-fit-1to1.pdf` on A4
landscape with **Actual size / 100%** selected and all fit-to-page scaling
disabled. Before fitting parts, measure the printed board rectangle and confirm
it is exactly 100 x 70 mm. Check J1, J10, J20, J40, and J60 pin/slot entry plus
body and board-edge alignment; retain a signed/photo record with the release.
