#!/usr/bin/env python3
"""Route local MCP2515-to-TJA1055 data and default-mode connections."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_CAN_FT_CONTROLLER"

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


txcan = "/CAN_FT/MCP_TXCAN"
rxcan = "/CAN_FT/MCP_RXCAN"

# The two controller/transceiver data nets run in parallel on L4 underneath
# U40.  Their short L1 escapes stay outside both SOIC/TSSOP courtyards.
tx_a = point(68.80, 38.42)
tx_b = point(82.50, 40.96)
rx_a = point(68.80, 39.69)
rx_b = point(82.50, 42.23)
for net_name, at in ((txcan, tx_a), (txcan, tx_b),
                     (rxcan, rx_a), (rxcan, rx_b)):
    via(net_name, at)

path(txcan, [pad("U40", "1"), tx_a])
path(txcan, [tx_a, point(74.00, 39.00), tx_b], SIG, pcbnew.B_Cu)
path(txcan, [tx_b, pad("U41", "2")])
path(rxcan, [pad("U40", "2"), rx_a])
path(rxcan, [rx_a, point(74.00, 40.30), rx_b], SIG, pcbnew.B_Cu)
path(rxcan, [rx_b, pad("U41", "3")])

# TJA1055 RXD is open drain; branch the existing L4 RXCAN route to its 3.3 V
# pull-up without loading the short U40-U41 component-layer escapes.
rx_pull = point(74.00, 50.50)
via(rxcan, rx_pull)
path(rxcan, [point(74.00, 40.30), rx_pull], SIG, pcbnew.B_Cu)
path(rxcan, [rx_pull, pad("R42", "1")])

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped local FT-CAN controller links as {GROUP_NAME}")
