#!/usr/bin/env python3
"""Route the reviewed high-speed CAN interface end to end.

The ESP32 TWAI logic signals reach the TCAN332 independently.  CANH/CANL use
0.30 mm top-layer routes through the reserved zero-ohm links and connector-side
TVS device.  The optional 120 ohm termination remains behind JP20.
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_CAN_HS_ROUTING"

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


tx = "/CAN_HS_TX"
rx = "/CAN_HS_RX"
hphy = "/CAN_HS/CAN_HS_H_PHY"
lphy = "/CAN_HS/CAN_HS_L_PHY"
canh = "/CAN_HS/CAN_HS_H"
canl = "/CAN_HS/CAN_HS_L"
term = "/CAN_HS/CAN_HS_TERM"

# TX crosses to L4 so the reversed source/destination ordering cannot force a
# logic-signal crossover. RX remains on L1 with continuous L2 reference.
tx_a = point(55.20, 41.50)
tx_b = point(70.80, 25.00)
via(tx, tx_a)
via(tx, tx_b)
path(tx, [pad("U10", "27"), tx_a])
path(tx, [tx_a, point(60.00, 37.00), point(66.00, 33.00),
          point(70.80, 27.00), tx_b],
     SIG, pcbnew.B_Cu)
path(tx, [tx_b, point(72.20, 25.00), pad("U20", "1")])

rx_a = point(67.50, 32.50)
rx_b = point(74.00, 32.50)
via(rx, rx_a)
via(rx, rx_b)
path(rx, [pad("U10", "28"), point(55.50, 40.24), point(55.50, 38.50),
          point(60.00, 37.00), point(65.50, 34.00), rx_a])
path(rx, [rx_a, rx_b], SIG, pcbnew.B_Cu)
path(rx, [rx_b, pad("U20", "4")])

# TCAN332 bus-side pins to the reserved zero-ohm CMC-bypass links.
path(hphy, [pad("U20", "7"), point(80.00, 27.35),
            point(81.00, 25.50), pad("R30", "1")], BUS)
path(lphy, [pad("U20", "6"), point(80.00, 28.65),
            point(81.00, 29.50), pad("R31", "1")], BUS)

# Protected connector paths.  D20's two bus pads face each other in this
# orientation, so the main pair passes immediately above/below it and uses
# short shunt stubs rather than routing one bus through the other bus's pad.
path(canh, [pad("R30", "2"), point(84.00, 24.50),
            point(92.00, 24.50), pad("J20", "1")], BUS)
path(canh, [point(84.80, 24.50), point(84.80, 27.80), pad("D20", "1")], BUS)
path(canl, [pad("R31", "2"), point(84.00, 31.00),
            point(97.50, 31.00), pad("J20", "2")], BUS)
path(canl, [point(88.20, 31.00), point(88.20, 29.10), pad("D20", "2")], BUS)

# Short diagnostic stubs, kept on the protected side of R30/R31.
path(canh, [pad("R30", "2"), point(81.50, 23.50), pad("TP20", "1")], SIG)
# TP21 is placed beside the protected CANL run and completed by the final
# cleanup pass, avoiding the former long stub from the board edge.

# Selectable 120 ohm termination.  J20 is through-hole but JP20 is SMD, so the
# CANH crossing leg uses one explicit L4-to-L1 transition beside the jumper.
hterm_b = point(102.50, 34.50)
via(canh, hterm_b)
path(canh, [pad("J20", "1"), hterm_b], BUS, pcbnew.B_Cu)
path(canh, [hterm_b, point(103.20, 36.20), pad("JP20", "1")], BUS)
path(canl, [pad("J20", "2"), point(100.58, 34.50), pad("R32", "2")], BUS)
path(term, [pad("R32", "1"), point(97.00, 37.00), point(97.00, 39.00),
            point(105.65, 39.00), pad("JP20", "2")], BUS)

# Connector-side TVS ground has a direct L2 drop.
gnd_via = point(86.50, 25.50)
path("/GND", [pad("D20", "3"), gnd_via], BUS)
via("/GND", gnd_via)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped high-speed CAN as {GROUP_NAME}")
