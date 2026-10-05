#!/usr/bin/env python3
"""Apply deterministic Revision A silkscreen DFM cleanup.

Dense power/clock reference designators remain available on F.Fab and in the
assembly drawing.  Their F.SilkS copies are hidden where they overlap exposed
copper or another footprint.  Functional connector/polarity legends are not
removed.
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"

board = pcbnew.LoadBoard(str(BOARD_PATH))
footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}

HIDE_REFS = {
    "TP20", "TP21", "H2", "TP7", "C13", "C10", "R8", "R12",
    "R13", "SW2", "C16", "C14", "C21", "C22", "C20", "C43",
    "U40", "R14", "R10", "C19", "C18", "TP6", "C23", "C40",
    "C42", "R44", "TP2", "C7", "R6", "R7", "R9",
}

for ref in HIDE_REFS:
    footprints[ref].Reference().SetVisible(False)

# The KiCad RCA footprint duplicates the body rectangle on F.Fab and F.SilkS;
# its 10 x 10 mm silk rectangle necessarily crosses the two shield pads.  Keep
# the accurate Fab outline and remove only that redundant silk rectangle.
j60 = footprints["J60"]
for item in list(j60.GraphicalItems()):
    if item.GetLayer() != pcbnew.F_SilkS or not isinstance(item, pcbnew.PCB_SHAPE):
        continue
    # KiCad 10's Python binding exposes SHAPE_T_RECT as integer value 1.
    if item.GetShape() != 1:
        continue
    start = item.GetStart()
    end = item.GetEnd()
    if (abs(pcbnew.ToMM(start.x) - 106.0) < 0.01 and
            abs(pcbnew.ToMM(start.y) - 75.5) < 0.01 and
            abs(pcbnew.ToMM(end.x) - 116.0) < 0.01 and
            abs(pcbnew.ToMM(end.y) - 85.5) < 0.01):
        j60.Remove(item)

if not any(
        isinstance(item, pcbnew.PCB_SHAPE) and
        item.GetLayer() == pcbnew.F_SilkS and item.GetShape() == 0 and
        abs(pcbnew.ToMM(item.GetStart().x) - 106.0) < 0.01 and
        abs(pcbnew.ToMM(item.GetStart().y) - 75.5) < 0.01 and
        abs(pcbnew.ToMM(item.GetEnd().x) - 106.0) < 0.01 and
        abs(pcbnew.ToMM(item.GetEnd().y) - 85.5) < 0.01
        for item in j60.GraphicalItems()):
    edge = pcbnew.PCB_SHAPE(j60)
    edge.SetShape(0)
    edge.SetLayer(pcbnew.F_SilkS)
    edge.SetWidth(pcbnew.FromMM(0.20))
    edge.SetStart(point := pcbnew.VECTOR2I(pcbnew.FromMM(106.0),
                                           pcbnew.FromMM(75.5)))
    edge.SetEnd(pcbnew.VECTOR2I(point.x, pcbnew.FromMM(85.5)))
    j60.Add(edge)

pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Cleaned F.SilkS; hidden reference count: {len(HIDE_REFS)}")
