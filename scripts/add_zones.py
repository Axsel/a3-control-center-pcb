#!/usr/bin/env python3
"""Create the reviewed Revision A copper zones and refill the board.

The first zone is the continuous L2 (In1.Cu) ground reference plane.  Its
outline is inset from the board edge; footprint keepouts, including the
ESP32-WROOM antenna keepout, remain authoritative during refill.
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
ZONE_NAME = "GND_L2_PLANE"


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


board = pcbnew.LoadBoard(str(BOARD_PATH))
nets = {str(name): net for name, net in board.GetNetsByName().items()}

# Idempotently replace only the zone owned by this script.
for zone in list(board.Zones()):
    if zone.GetZoneName() == ZONE_NAME:
        board.Delete(zone)

zone = pcbnew.ZONE(board)
zone.SetZoneName(ZONE_NAME)
zone.SetLayer(pcbnew.In1_Cu)
zone.SetNet(nets["/GND"])
zone.SetLocalClearance(pcbnew.FromMM(0.20))
zone.SetMinThickness(pcbnew.FromMM(0.20))

# The provisional 100 x 70 mm outline spans (20,20) to (120,90).  A 0.55 mm
# inset clears the 0.50 mm copper-to-edge rule with a small numerical margin.
outline_index = zone.Outline().NewOutline()
for corner in (
    point(20.55, 20.55),
    point(119.45, 20.55),
    point(119.45, 89.45),
    point(20.55, 89.45),
):
    zone.Outline().Append(corner, outline_index)

board.Add(zone)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Created and filled {ZONE_NAME} on In1.Cu")
