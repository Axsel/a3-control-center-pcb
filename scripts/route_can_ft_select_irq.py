#!/usr/bin/env python3
"""Route MCP2515 chip-select and interrupt, including their pull-ups."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_CAN_FT_SELECT_IRQ"

SIG = pcbnew.FromMM(0.20)
VIA_DIAMETER = pcbnew.FromMM(0.45)
VIA_DRILL = pcbnew.FromMM(0.20)


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
            layer: int = pcbnew.F_Cu) -> None:
    item = pcbnew.PCB_TRACK(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetLayer(layer)
    item.SetWidth(SIG)
    item.SetStart(start)
    item.SetEnd(end)
    add(item)


def path(net_name: str, points: list[pcbnew.VECTOR2I],
         layer: int = pcbnew.F_Cu) -> None:
    for start, end in zip(points, points[1:]):
        segment(net_name, start, end, layer)


def via(net_name: str, at: pcbnew.VECTOR2I) -> None:
    item = pcbnew.PCB_VIA(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetPosition(at)
    item.SetWidth(VIA_DIAMETER)
    item.SetDrill(VIA_DRILL)
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    add(item)


# Local active-low interrupt connection.  R41 is placed beside the existing
# +3V3 support via, allowing pin 12 to stay east of ERR/EN and avoid RXCAN.
irq = "/CAN_FT_INT"
irq_drop = point(83.50, 53.00)
irq_cross = point(81.00, 58.50)
irq_pull = point(80.50, 62.00)
for at in (irq_drop, irq_cross, irq_pull):
    via(irq, at)
path(irq, [pad("U40", "12"), point(81.00, 45.30), point(81.00, 48.50),
           point(83.50, 50.00), irq_drop])
path(irq, [irq_drop, point(81.00, 56.00), irq_cross], pcbnew.In2_Cu)
path(irq, [irq_cross, irq_pull], pcbnew.B_Cu)
path(irq, [irq_pull, point(80.50, 64.00), point(83.50, 64.00),
           point(83.50, 61.00), pad("R41", "1")])

# GPIO13 is on the module's lower edge.  The long, slow INT return therefore
# uses the open lower L4 corridor and only a short L3 bridge across ERR.
irq_source = point(40.555, 47.50)
irq_ctrl_a = point(70.00, 66.00)
irq_ctrl_b = point(81.00, 66.00)
irq_join = point(82.00, 64.00)
for at in (irq_source, irq_ctrl_a, irq_ctrl_b, irq_join):
    via(irq, at)
path(irq, [pad("U10", "16"), irq_source])
path(irq, [irq_source, point(42.00, 46.50), point(53.50, 46.50),
           point(53.50, 65.00), point(57.00, 66.00), irq_ctrl_a],
     pcbnew.B_Cu)
path(irq, [irq_ctrl_a, irq_ctrl_b], pcbnew.In2_Cu)
path(irq, [irq_ctrl_b, irq_join], pcbnew.B_Cu)

# GPIO4 is on the module's right edge.  CS stays on L1 and enters U40 through
# the open channel between left-side pins 3 and 4, then runs beneath the SOIC
# body to pin 16.  The pull-up branch is added after this main path is checked.
cs = "/CAN_FT_CS"
path(cs, [pad("U10", "26"), point(56.00, 42.78), point(58.00, 42.00),
          point(60.00, 40.00), point(63.00, 39.00), point(66.00, 39.00),
          point(68.50, 41.60), point(72.00, 41.60), point(76.00, 41.20),
          pad("U40", "16")])
path(cs, [pad("R50", "1"), point(58.50, 44.00), point(58.00, 42.00)])

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped FT-CAN select/interrupt as {GROUP_NAME}")
