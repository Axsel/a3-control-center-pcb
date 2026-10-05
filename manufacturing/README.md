# Manufacturing releases

`generated/rev-a-audit/` contains the current local pre-release audit package:

- all four copper layers, masks, paste, legends, and board-edge Gerbers;
- plated/non-plated drill files, drill maps, and drill report;
- ERC, DRC, IPC-D-356, and board-statistics reports;
- top/bottom renders, top assembly drawing and preview, STEP mechanical export,
  complete schematic PDF and per-sheet SVG/PNG previews;
- an A4, 1:1 front-fabrication connector-fit PDF (print at Actual size / 100%);
- raw KiCad BOM/position exports for comparison only; and
- an explicit population manifest plus candidate JLCPCB BOM/CPL files generated
  by `scripts/export_jlc.py`.

`jlcpcb-assembly-notes.md` is the controlled complete-assembly instruction:
all five board connectors are mandatory JLC manual/wave-assembly items. Copy
its PCBA remark into the order and retain JLC's written process confirmation.
`jlcpcb-order-parameters.md` is the controlled fabrication/assembly option
sheet; compare it line by line with the final quotation.
`jlcpcb-support-request.md` is the ready-to-send engineering/source request for
the mixed SMT/PTH connector process, mandatory THT population, J60 wave
assembly, U5 custom lands, and exact constrained-part sourcing.

The current `generated/rev-a-audit/` snapshot is tracked for design review and
quick repository access, but it is **not a manufacturing release**. The
candidate JLC files must not be uploaded while `assembly/jlc-readiness.txt`
reports `NOT READY FOR PCBA UPLOAD`. C1 and the former J60/L1/L2 shortages now
have controlled replacements. Complete manual/wave assembly handling for
J1/J10/J20/J40/J60, live-stock reservation, and physical connector fit checks
remain open. J60 now uses four round plated holes and no longer needs the
former Kycon plated-slot DFM exception. Composite-video prototype validation is
explicitly deferred to assembled-board bring-up by owner direction; this is an
accepted Revision A prototype risk, not evidence that video has passed.

The first JLC BOM-matching workbook was reviewed in
`../docs/jlc-bom-review-2026-10-05.md`. It records the prohibited C1 match,
zero-stock exact parts, accepted tape-and-reel U40 code, conditional J1
difficult-processing fee, and D60 prototype substitution.

A released revision must be copied into a versioned, tracked release directory
and include reviewed Gerbers, drills, BOM, position files, assembly drawings,
ERC/DRC reports, approved stackup/order parameters, DFM evidence, and a checksum
manifest. Do not promote raw KiCad BOM/CPL exports: their DNP behavior is not the
Revision A population authority.
