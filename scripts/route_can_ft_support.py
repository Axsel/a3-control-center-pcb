#!/usr/bin/env python3
"""Route FT-CAN controller pull-up/pull-down support and MCP reset capacitor."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_CAN_FT_SUPPORT"

SIG = pcbnew.FromMM(0.20)
LOCAL_PWR = pcbnew.FromMM(0.50)
TRUNK = pcbnew.FromMM(0.60)
VIA_DIAMETER = pcbnew.FromMM(0.60)
VIA_DRILL = pcbnew.FromMM(0.30)
GND_VIA_DIAMETER = pcbnew.FromMM(0.45)
GND_VIA_DRILL = pcbnew.FromMM(0.20)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


board = pcbnew.LoadBoard(str(BOARD_PATH))
footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
nets = {str(name): net for name, net in board.GetNetsByName().items()}

for old_group in list(board.Groups()):
    if old_group.GetName() == GROUP_NAME:
        for old_item in list(old_group.GetItems()):
            board.Delete(old_item)
        board.Delete(old_group)

group = pcbnew.PCB_GROUP(board)
group.SetName(GROUP_NAME)
board.Add(group)


def pad(ref: str, number: str) -> pcbnew.VECTOR2I:
    found = footprints[ref].FindPadByNumber(number)
    if found is None:
        raise SystemExit(f"missing pad {ref}.{number}")
    return found.GetPosition()


def add(item) -> None:
    board.Add(item)
    group.AddItem(item)


def segment(net_name: str, start: pcbnew.VECTOR2I, end: pcbnew.VECTOR2I,
            width: int = SIG, layer: int = pcbnew.F_Cu) -> None:
    item = pcbnew.PCB_TRACK(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetLayer(layer)
    item.SetWidth(width)
    item.SetStart(start)
    item.SetEnd(end)
    add(item)


def path(net_name: str, points: list[pcbnew.VECTOR2I], width: int = SIG,
         layer: int = pcbnew.F_Cu) -> None:
    for start, end in zip(points, points[1:]):
        segment(net_name, start, end, width, layer)


def via(net_name: str, at: pcbnew.VECTOR2I, ground: bool = False) -> None:
    item = pcbnew.PCB_VIA(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetPosition(at)
    item.SetWidth(GND_VIA_DIAMETER if ground else VIA_DIAMETER)
    item.SetDrill(GND_VIA_DRILL if ground else VIA_DRILL)
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    add(item)


v3 = "/+3V3"

# Pull-up spine.  The horizontal L1 rail runs below the signal-side resistor
# pads.  A separate L3 feed supplies relocated CS pull-up R50, while the
# eastern support via joins the existing video-side +3V3 branch for R41.
spine_y = 53.50
pullups = ("R40", "R42", "R43")
for ref in pullups:
    p = pad(ref, "2")
    path(v3, [p, point(pcbnew.ToMM(p.x), spine_y)], LOCAL_PWR)
path(v3, [point(68.825, spine_y), point(80.825, spine_y)], TRUNK)
support_via = point(84.00, 56.00)
via(v3, support_via)
path(v3, [pad("R41", "2"), support_via], LOCAL_PWR)
path(v3, [support_via, point(84.00, 65.00),
          point(80.00, 70.50), point(78.00, 73.50)],
     TRUNK, pcbnew.In2_Cu)

# R50 sits beside the GPIO4 CS route.  Its supply enters L3 locally and joins
# the existing CAN-side +3V3 branch at the documented can-entry node.
r50_via = point(61.50, 44.50)
via(v3, r50_via)
path(v3, [pad("R50", "2"), r50_via], LOCAL_PWR)
path(v3, [r50_via, point(52.00, 48.00)], LOCAL_PWR, pcbnew.In2_Cu)

# MCP2515 reset-capacitor ground return.
path("/GND", [pad("C42", "1"), point(76.20, 36.00)], SIG)
via("/GND", point(76.20, 36.00), ground=True)

# Reset signal.  A short L3 dogleg bypasses VDD pin 18, then the R40 pull-up
# approaches from the west on L3 without crossing the SPI/control bundle.
reset = "/CAN_FT/MCP_RESET_N"
reset_cap = point(78.50, 37.50)
reset_pin = point(81.00, 39.69)
reset_pull = point(68.00, 51.00)
for at in (reset_cap, reset_pin, reset_pull):
    via(reset, at)
path(reset, [pad("C42", "2"), reset_cap])
path(reset, [reset_cap, point(79.00, 39.20), reset_pin], SIG,
     pcbnew.In2_Cu)
path(reset, [reset_pin, pad("U40", "17")])
path(reset, [pad("R40", "1"), reset_pull])
path(reset, [reset_pull, point(68.00, 45.00), point(70.00, 41.00),
             reset_pin], SIG, pcbnew.In2_Cu)

# Documented low/low standby defaults for the TJA1055 mode pins.
path("/GND", [pad("R44", "1"), point(80.20, 36.00)], SIG)
via("/GND", point(80.20, 36.00), ground=True)
path("/GND", [pad("R45", "1"), point(84.175, 34.50)], SIG)
via("/GND", point(84.175, 34.50), ground=True)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped FT-CAN support networks as {GROUP_NAME}")
