#!/usr/bin/env python3
"""Route the TJA1055 fault-tolerant CAN physical bus and termination network.

This script intentionally does not route the MCP2515/SPI/control side.  It
connects the TJA1055 bus pins through the zero-ohm links, connector-side TVS,
J40, and the independently selectable ISO 11898-3 RTH/RTL branches.
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_CAN_FT_BUS"

SIG = pcbnew.FromMM(0.20)
BUS = pcbnew.FromMM(0.30)
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


def via(net_name: str, at: pcbnew.VECTOR2I) -> None:
    item = pcbnew.PCB_VIA(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetPosition(at)
    item.SetWidth(VIA_DIAMETER)
    item.SetDrill(VIA_DRILL)
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    add(item)


hphy = "/CAN_FT/CAN_FT_H_PHY"
lphy = "/CAN_FT/CAN_FT_L_PHY"
canh = "/CAN_FT/CAN_FT_H"
canl = "/CAN_FT/CAN_FT_L"
rth = "/CAN_FT/TJA_RTH"
rtl = "/CAN_FT/TJA_RTL"
term_h = "/CAN_FT/FT_TERM_H"
term_l = "/CAN_FT/FT_TERM_L"

# U41 bus pins have reversed vertical ordering relative to R46/R47.  Put only
# H_PHY on L4 for the short crossover and leave L_PHY on the component layer.
hphy_a = point(93.00, 43.50)
hphy_b = point(93.00, 38.00)
via(hphy, hphy_a)
via(hphy, hphy_b)
path(hphy, [pad("U41", "11"), hphy_a], BUS)
path(hphy, [hphy_a, point(94.00, 40.00), hphy_b],
     BUS, pcbnew.B_Cu)
path(hphy, [hphy_b, pad("R46", "1")], BUS)
path(lphy, [pad("U41", "12"), point(90.50, 42.20),
            point(92.00, 41.50), pad("R47", "1")], BUS)

# CANH uses a short L4 detour around CANL and re-enters beside D40.  CANH then
# approaches TVS pad 1 from below, avoiding TVS pad 2.  CANL stays above it and
# uses a short shunt to TVS pad 2.
h_a = point(94.00, 37.50)
h_b = point(94.00, 50.00)
via(canh, h_a)
via(canh, h_b)
path(canh, [pad("R46", "2"), h_a], BUS)
path(canh, [h_a, point(97.50, 37.50), point(97.50, 50.00), h_b],
     BUS, pcbnew.B_Cu)
path(canh, [h_b, point(95.00, 49.50), pad("D40", "1")], BUS)
path(canh, [pad("D40", "1"), point(95.00, 49.50),
            point(100.00, 49.50), pad("J40", "1")], BUS)

path(canl, [pad("R47", "2"), point(97.00, 43.00),
            point(101.00, 44.00), point(105.00, 44.00),
            pad("J40", "2")], BUS)
path(canl, [pad("D40", "2"), point(98.00, 47.90),
            point(99.00, 45.00), point(101.00, 44.00)], BUS)

# Direct TVS ground drop into L2.
gnd_via = point(96.00, 44.80)
path("/GND", [pad("D40", "3"), gnd_via], BUS)
via("/GND", gnd_via)

# Independent ISO 11898-3 line resistors and normally-open enable jumpers.
path(rth, [pad("U41", "8"), point(90.00, 47.30),
           point(90.00, 52.50), pad("R48", "1")], SIG)
path(rtl, [pad("U41", "9"), point(91.50, 46.00),
           point(92.00, 52.50), pad("R49", "1")], SIG)
path(term_h, [pad("R48", "2"), point(86.50, 57.00),
              point(86.50, 60.00), point(94.35, 60.00),
              pad("JP40", "1")], SIG)
term_l_a = point(92.50, 57.00)
term_l_b = point(97.50, 58.00)
via(term_l, term_l_a)
via(term_l, term_l_b)
path(term_l, [pad("R49", "2"), term_l_a], SIG)
path(term_l, [term_l_a, term_l_b], SIG, pcbnew.B_Cu)
path(term_l, [term_l_b, point(97.50, 56.00), pad("JP41", "1")], SIG)

# Enabled termination branches join their own bus line near D40/J40.  These
# are stubs by topology, acceptable for the intended <=125 kbit/s FT-CAN bus.
path(canh, [pad("JP40", "2"), point(96.50, 54.00),
            point(96.50, 50.00), pad("D40", "1")], BUS)
path(canl, [pad("JP41", "2"), point(102.00, 54.00),
            point(106.00, 52.00), pad("J40", "2")], BUS)

# TP40/TP41 are deferred to the final test-point cleanup rather than adding
# crossing stubs through the two termination branches.

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped FT-CAN physical bus as {GROUP_NAME}")
