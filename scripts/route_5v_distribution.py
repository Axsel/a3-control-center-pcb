#!/usr/bin/env python3
"""Route the reviewed shared 5 V trunks on L3 (In2.Cu).

The protected USB rail feeds both converters.  The regulated 5V_FT rail feeds
the TJA1055's separate supply pins and local capacitors.  Generated objects are
kept in a named group for safe replacement.
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_5V_DISTRIBUTION"

SIG = pcbnew.FromMM(0.20)
LOCAL_PWR = pcbnew.FromMM(0.50)
TRUNK = pcbnew.FromMM(0.80)
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
            width: int, layer: int = pcbnew.F_Cu) -> None:
    item = pcbnew.PCB_TRACK(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetLayer(layer)
    item.SetWidth(width)
    item.SetStart(start)
    item.SetEnd(end)
    add(item)


def path(net_name: str, points: list[pcbnew.VECTOR2I], width: int,
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


def ground_drop(start: pcbnew.VECTOR2I, at: pcbnew.VECTOR2I) -> None:
    segment("/GND", start, at, SIG)
    via("/GND", at, ground=True)


usb5 = "/USB + Power/+5V_USB"
v5ft = "/+5V_FT"

# TPS2553 output enters L3 immediately so it does not cross C7's grounded pad.
usb5_source = point(31.50, 55.55)
segment(usb5, pad("U3", "6"), point(30.80, 55.55), SIG)
segment(usb5, point(30.80, 55.55), usb5_source, LOCAL_PWR)
via(usb5, usb5_source)

# Join the TPS62132 local input island from above, then take the long feed to
# the TPS63070 input on L3.
usb5_west = point(35.20, 55.50)
usb5_east = point(61.775, 53.00)
path(usb5, [pad("C7", "2"), usb5_west], LOCAL_PWR)
via(usb5, usb5_west)
via(usb5, usb5_east)
path(usb5, [usb5_source, usb5_west, point(35.20, 61.50),
            point(42.00, 61.50), point(45.00, 53.50), point(53.00, 52.50),
            point(60.50, 52.50), usb5_east], TRUNK, pcbnew.In2_Cu)

# Extend regulated 5V_FT from the local output network to TJA1055.  TP4 is a
# plated test point on this L3 trunk.
ft_local = point(64.95, 62.80)  # existing local-output via
ft_pin7 = point(82.50, 47.31)
ft_pin10 = point(91.20, 44.77)
ft_pin14 = point(90.50, 39.69)
ft_c46 = point(87.80, 51.00)
ft_c45 = point(90.00, 34.00)
for transition in (ft_pin7, ft_pin10, ft_pin14, ft_c46, ft_c45):
    via(v5ft, transition)

path(v5ft, [ft_local, point(71.00, 57.50), point(76.00, 54.50),
            point(80.00, 50.00), ft_pin7], TRUNK, pcbnew.In2_Cu)
path(v5ft, [ft_pin7, ft_c46, ft_pin10, ft_pin14, ft_c45], TRUNK,
     pcbnew.In2_Cu)

# Short top-layer escapes at each supply pin/capacitor.
path(v5ft, [pad("U41", "7"), ft_pin7], LOCAL_PWR)
segment(v5ft, pad("U41", "10"), point(90.20, 44.77), SIG)
segment(v5ft, point(90.20, 44.77), ft_pin10, LOCAL_PWR)
path(v5ft, [pad("U41", "14"), ft_pin14], LOCAL_PWR)
path(v5ft, [pad("C46", "2"), ft_c46], LOCAL_PWR)
path(v5ft, [pad("C45", "2"), ft_c45], LOCAL_PWR)

ground_drop(pad("C46", "1"), point(84.20, 51.00))
ground_drop(pad("C45", "1"), point(86.30, 34.00))

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped shared 5 V rails as {GROUP_NAME}")
