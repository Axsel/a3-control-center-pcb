#!/usr/bin/env python3
"""Route the reviewed +3V3 distribution tree and primary bypass returns.

The TPS62132 output enters L3 at the output-capacitor junction.  Wide L3
branches feed the ESP32, USB/UART + OLED, CAN, and video islands; only short
escapes to fine-pitch IC pins remain on F.Cu.  Generated objects live in a
named group so this script can be rerun without touching hand routing.
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_3V3_DISTRIBUTION"

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


def ground_drop(start: pcbnew.VECTOR2I, at: pcbnew.VECTOR2I,
                width: int = SIG) -> None:
    segment("/GND", start, at, width)
    via("/GND", at, ground=True)


v3 = "/+3V3"

# Enter L3 at the TPS62132 output junction.  This point is already part of the
# short L1/C9/C10 top-layer output network created by route_local_power.py.
source = point(46.00, 57.00)
via(v3, source)

# L3 tree.  Branches are intentionally separated by function and avoid the
# existing protected-5V and 5V_FT L3 corridors.
esp_node = point(34.30, 29.80)
uart_node = point(34.00, 74.80)
hs_node = point(72.30, 31.50)
mcp_node = point(79.00, 32.30)
c41_node = point(73.80, 33.20)
video_node = point(90.00, 77.00)
video_bulk = point(95.50, 79.00)
esp_entry = point(40.50, 49.50)
can_entry = point(52.00, 48.00)

for transition in (esp_node, uart_node, hs_node, mcp_node, c41_node,
                   video_node, video_bulk, esp_entry, can_entry):
    via(v3, transition)

# Short B.Cu bridges cross the protected-5V corridor near the regulator; the
# long branches then return to L3.  This avoids cutting through either 5 V
# trunk and leaves L2 as an uninterrupted ground plane.
path(v3, [source, point(43.50, 53.50), esp_entry], TRUNK, pcbnew.B_Cu)
path(v3, [esp_entry, point(36.00, 41.00), esp_node], TRUNK, pcbnew.In2_Cu)
path(v3, [source, point(48.50, 54.50), can_entry], TRUNK, pcbnew.B_Cu)
path(v3, [source, point(48.00, 62.50), point(42.00, 65.50),
          point(35.50, 71.50), uart_node],
     TRUNK, pcbnew.In2_Cu)
path(v3, [uart_node, point(33.00, 82.00), pad("J10", "1")],
     LOCAL_PWR, pcbnew.In2_Cu)
path(v3, [can_entry, point(60.00, 38.50),
          point(70.00, 35.00), hs_node], TRUNK, pcbnew.In2_Cu)
path(v3, [point(70.00, 35.00), mcp_node], TRUNK, pcbnew.In2_Cu)
path(v3, [source, point(50.00, 64.50), point(64.00, 68.50),
          point(78.00, 73.50), video_node], TRUNK, pcbnew.In2_Cu)
path(v3, [video_node, point(93.00, 79.00), video_bulk],
     LOCAL_PWR, pcbnew.In2_Cu)

# ESP32 local bulk/high-frequency bypass and module VDD.
path(v3, [esp_node, pad("C22", "2")], LOCAL_PWR)
path(v3, [pad("C22", "2"), point(35.00, 29.55), pad("U10", "2")],
     SIG)
path(v3, [pad("C21", "2"), point(34.10, 27.50),
          point(35.05, 28.45), pad("U10", "2")], LOCAL_PWR)
ground_drop(pad("C21", "1"), point(30.80, 27.50), LOCAL_PWR)
ground_drop(pad("C22", "1"), point(30.80, 29.80), SIG)
ground_drop(pad("U10", "1"), point(35.20, 26.90), SIG)

# The additional 100 uF reservoir is below the module and joins the same L3
# tree without forcing its charging current through a fine-pitch module pad.
esp_bulk = point(49.50, 48.50)
via(v3, esp_bulk)
path(v3, [can_entry, esp_bulk], LOCAL_PWR, pcbnew.In2_Cu)
path(v3, [esp_bulk, pad("C23", "2")], LOCAL_PWR)
ground_drop(pad("C23", "1"), point(46.20, 48.50), LOCAL_PWR)

# CP2102N supply pins and its 4.7 uF / 100 nF bypass pair.
path(v3, [uart_node, point(33.45, 75.40), pad("C2", "2")], LOCAL_PWR)
path(v3, [pad("C2", "2"), point(33.45, 75.70),
          point(36.775, 75.70), pad("C3", "2")], LOCAL_PWR)
path(v3, [pad("C3", "2"), point(36.55, 75.50),
          pad("U2", "7"), pad("U2", "6")], SIG)
ground_drop(pad("C2", "1"), point(30.60, 77.00), LOCAL_PWR)
ground_drop(pad("C3", "1"), point(35.20, 78.20), SIG)

# High-speed CAN transceiver bypass.  C31 is the nearby bulk capacitor.
path(v3, [hs_node, pad("C31", "2")], LOCAL_PWR)
path(v3, [hs_node, pad("C30", "2")], LOCAL_PWR)
path(v3, [pad("C30", "2"), point(72.80, 28.60),
          pad("U20", "3")], SIG)
ground_drop(pad("C30", "1"), point(68.90, 28.60), SIG)
ground_drop(pad("C31", "1"), point(68.60, 34.00), LOCAL_PWR)
ground_drop(pad("U20", "2"), point(72.90, 27.35), SIG)

# MCP2515 bypass and VDD.  Its 100 nF capacitor is above the package; the
# 1 uF capacitor is retained as a nearby local reservoir.
path(v3, [mcp_node, pad("C40", "2")], LOCAL_PWR)
path(v3, [pad("C40", "2"), point(79.65, 35.50),
          pad("U40", "18")], SIG)
path(v3, [point(70.00, 35.00), c41_node], LOCAL_PWR, pcbnew.In2_Cu)
path(v3, [c41_node, pad("C41", "2")], LOCAL_PWR)
ground_drop(pad("C40", "1"), point(81.80, 34.00), SIG)
ground_drop(pad("C41", "1"), point(71.50, 37.50), LOCAL_PWR)

# THS7314 video buffer bypass.  C61 is the local 100 nF part; C62 is bulk.
path(v3, [video_node, pad("C61", "2")], LOCAL_PWR)
path(v3, [pad("C61", "2"), point(88.70, 75.20),
          pad("U60", "4")], SIG)
path(v3, [video_bulk, pad("C62", "2")], LOCAL_PWR)
ground_drop(pad("C61", "1"), point(86.30, 77.00), SIG)
ground_drop(pad("C62", "1"), point(92.00, 75.20), LOCAL_PWR)
ground_drop(pad("U60", "5"), point(94.30, 74.20), SIG)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped +3V3 distribution as {GROUP_NAME}")
