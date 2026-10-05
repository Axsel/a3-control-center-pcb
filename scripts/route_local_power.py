#!/usr/bin/env python3
"""Route reviewed local converter loops and their L2 ground drops.

All generated tracks and vias are stored in a named KiCad group.  Rerunning the
script replaces only that group, including the pieces on shared power/GND nets,
without disturbing later manual routing.
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_LOCAL_POWER_GND"

SIG = pcbnew.FromMM(0.20)
JOIN = pcbnew.FromMM(0.25)
GND = pcbnew.FromMM(0.40)
PWR = pcbnew.FromMM(0.50)
PWR_WIDE = pcbnew.FromMM(0.60)
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
            width: int = SIG, layer: int = pcbnew.F_Cu) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetNetCode(nets[net_name].GetNetCode())
    track.SetLayer(layer)
    track.SetWidth(width)
    track.SetStart(start)
    track.SetEnd(end)
    add(track)


def path(net_name: str, points: list[pcbnew.VECTOR2I], width: int = SIG,
         layer: int = pcbnew.F_Cu) -> None:
    for start, end in zip(points, points[1:]):
        segment(net_name, start, end, width, layer)


def via(net_name: str, at: pcbnew.VECTOR2I) -> None:
    item = pcbnew.PCB_VIA(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetPosition(at)
    item.SetWidth(VIA_DIAMETER)
    item.SetDrill(VIA_DRILL)
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    add(item)


def ground_drop(start: pcbnew.VECTOR2I, at: pcbnew.VECTOR2I,
                width: int = GND) -> None:
    segment("/GND", start, at, width)
    via("/GND", at)


# TPS62132 3V3 buck: local input, output, soft-start, and ground returns.
usb5 = "/USB + Power/+5V_USB"
v3 = "/+3V3"
ss3 = "/USB + Power/SS_3V3"

segment(usb5, pad("U4", "10"), pad("U4", "12"), JOIN)
path(usb5, [pad("U4", "11"), point(36.00, 57.25),
            point(35.20, 56.50), pad("C7", "2")], PWR)
segment(usb5, pad("U4", "13"), point(36.80, 58.462), SIG)
path(usb5, [point(36.80, 58.462), point(35.50, 59.50),
            pad("C8", "2")], PWR)

path(v3, [pad("L1", "2"), point(46.00, 57.00)], PWR_WIDE)
path(v3, [point(46.00, 57.00), point(46.30, 55.50), pad("C9", "2")], PWR)
path(v3, [point(46.00, 57.00), point(46.00, 58.70), pad("C10", "2")], PWR)
path(ss3, [pad("U4", "9"), point(35.80, 56.25),
           point(35.80, 51.225), pad("C11", "2")])

segment("/GND", pad("U4", "5"), pad("U4", "8"), JOIN)
ground_drop(point(38.00, 55.538), point(38.00, 54.70))
ground_drop(point(39.00, 55.538), point(39.00, 54.70))
segment("/GND", pad("U4", "15"), pad("U4", "16"), JOIN)
segment("/GND", point(38.50, 57.00), pad("U4", "15"), JOIN)
ground_drop(pad("U4", "16"), point(39.80, 59.20))
ground_drop(pad("C7", "1"), point(31.80, 56.50))
ground_drop(pad("C8", "1"), point(31.90, 59.50))
ground_drop(pad("C9", "1"), point(49.80, 55.50))
ground_drop(pad("C10", "1"), point(49.10, 59.50))
ground_drop(pad("C11", "1"), point(37.80, 52.775))

# TPS63070 5V buck-boost: keep the two switch nodes separate and compact.
l1ft = "/USB + Power/L1_5VFT"
l2ft = "/USB + Power/L2_5VFT"
v5ft = "/+5V_FT"
fb = "/USB + Power/FB_5VFT"
vaux = "/USB + Power/VAUX_5VFT"

segment(l1ft, pad("U5", "11"), point(63.80, 57.00), SIG)
path(l1ft, [point(63.80, 57.00), point(64.30, 56.315),
            pad("L2", "1")], PWR_WIDE)
segment(l2ft, pad("U5", "9"), point(63.80, 58.00), SIG)
path(l2ft, [point(63.80, 58.00), point(64.30, 58.685),
            pad("L2", "2")], PWR_WIDE)

path(usb5, [pad("C17", "2"), point(58.45, 52.50), point(59.00, 53.00),
            point(61.775, 53.00), pad("C19", "2")], PWR)
path(usb5, [pad("C18", "2"), point(63.45, 53.00),
            point(61.775, 53.00)], PWR)
path(usb5, [pad("C19", "2"), point(61.775, 55.50)], PWR)
segment(usb5, point(61.775, 55.50), pad("U5", "12"), SIG)

path(v5ft, [pad("U5", "8"), point(62.00, 59.40), pad("C16", "2")], PWR)
path(v5ft, [pad("C16", "2"), point(62.00, 60.225)], PWR_WIDE)
for power_via in (point(62.00, 60.225), point(57.45, 62.80),
                  point(60.95, 62.80), point(64.95, 62.80)):
    via(v5ft, power_via)
path(v5ft, [point(62.00, 60.225), point(62.00, 62.80),
            point(57.45, 62.80)], PWR_WIDE, pcbnew.In2_Cu)
path(v5ft, [point(62.00, 62.80), point(64.95, 62.80)], PWR_WIDE,
     pcbnew.In2_Cu)
path(v5ft, [point(57.45, 62.80), pad("C13", "2")], PWR)
path(v5ft, [point(60.95, 62.80), pad("C14", "2")], PWR)
path(v5ft, [point(64.95, 62.80), pad("C15", "2")], PWR)

path(fb, [pad("U5", "5"), point(60.275, 59.50), pad("R12", "1")])
path(fb, [pad("R12", "1"), pad("R13", "2")])
path(v5ft, [pad("R12", "2"), point(53.80, 59.50),
            point(53.80, 62.00), point(57.45, 62.80)])
path(vaux, [pad("U5", "3"), point(58.80, 57.75),
            point(57.80, 57.00), point(57.80, 55.00), pad("C12", "2")])

ground_drop(pad("U5", "1"), point(58.60, 56.00), SIG)
ground_drop(pad("U5", "4"), point(58.80, 58.25), SIG)
ground_drop(pad("U5", "15"), point(59.50, 55.50), SIG)
ground_drop(pad("U5", "10"), point(63.20, 57.50), pcbnew.FromMM(0.15))
ground_drop(pad("C12", "1"), point(56.00, 55.00))
ground_drop(pad("C17", "1"), point(55.80, 51.50))
ground_drop(pad("C18", "1"), point(60.80, 51.50))
ground_drop(pad("C19", "1"), point(59.40, 54.00))
ground_drop(pad("C16", "1"), point(60.20, 61.775))
ground_drop(pad("C13", "1"), point(55.55, 65.00))
ground_drop(pad("C14", "1"), point(59.05, 65.00))
ground_drop(pad("C15", "1"), point(63.05, 65.00))
ground_drop(pad("R13", "1"), point(54.80, 61.50), SIG)

# Crystal/load-capacitor and MCP2515 local ground returns.
ground_drop(pad("Y40", "2"), point(67.80, 43.20), SIG)
ground_drop(pad("Y40", "4"), point(64.20, 47.80), SIG)
ground_drop(pad("C43", "1"), point(65.20, 50.10), SIG)
ground_drop(pad("C44", "1"), point(62.50, 40.50), SIG)
ground_drop(pad("U40", "9"), point(69.20, 49.40), SIG)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped local converter/clock grounds as {GROUP_NAME}")
