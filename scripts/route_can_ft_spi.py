#!/usr/bin/env python3
"""Route the ESP32-to-MCP2515 SPI interface and related pull-ups."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_CAN_FT_SPI"

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


# MOSI takes the open upper L3 corridor below the antenna keepout, then changes
# to L4 east of the controller to cross the existing L3 mode-control bundle.
# Short L1 escapes connect the two device pads.
mosi = "/CAN_FT_MOSI"
mosi_source = point(55.50, 28.81)
mosi_turn = point(87.00, 30.00)
mosi_dest = point(81.50, 42.80)
via(mosi, mosi_source)
via(mosi, mosi_turn)
via(mosi, mosi_dest)
path(mosi, [pad("U10", "37"), mosi_source])
path(mosi, [mosi_source, point(58.00, 30.00), mosi_turn], pcbnew.In2_Cu)
path(mosi, [mosi_turn, point(87.00, 42.80), mosi_dest], pcbnew.B_Cu)
path(mosi, [mosi_dest, pad("U40", "14")])

# SCK uses the open lower L4 corridor.  This keeps the clock clear of the L3
# power tree and avoids a long parallel run beside the CAN_HS logic routes.
sck = "/CAN_FT_SCK"
sck_source = point(55.50, 37.70)
sck_cross_a = point(56.00, 34.00)
sck_cross_b = point(66.50, 35.00)
sck_south_a = point(70.00, 60.00)
sck_south_b = point(82.00, 60.00)
sck_dest = point(81.00, 44.00)
for at in (sck_source, sck_cross_a, sck_cross_b, sck_south_a,
           sck_south_b, sck_dest):
    via(sck, at)
path(sck, [pad("U10", "30"), sck_source])
path(sck, [sck_source, sck_cross_a], pcbnew.B_Cu)
path(sck, [sck_cross_a, sck_cross_b], pcbnew.In2_Cu)
path(sck, [sck_cross_b, point(66.50, 56.00), sck_south_a], pcbnew.B_Cu)
path(sck, [sck_south_a, sck_south_b], pcbnew.In2_Cu)
path(sck, [sck_south_b, point(89.50, 58.00), point(89.50, 48.00),
           point(81.00, 48.00), sck_dest], pcbnew.B_Cu)
path(sck, [sck_dest, pad("U40", "13")])

# MISO parallels SCK without reversing their ordering.  It crosses CAN_HS on
# an upper L3 lane, drops south on L4, crosses the slow-control trunks on its
# own L3 lane, and returns to U40 above the SCK approach.
miso = "/CAN_FT_MISO"
miso_source = point(55.00, 36.43)
miso_cross_a = point(56.00, 32.50)
miso_cross_b = point(67.50, 34.00)
miso_south_a = point(70.00, 54.50)
miso_south_b = point(73.00, 51.00)
miso_dest = point(72.00, 42.23)
for at in (miso_source, miso_cross_a, miso_cross_b, miso_south_a,
           miso_dest):
    via(miso, at)
path(miso, [pad("U10", "31"), miso_source])
path(miso, [miso_source, point(54.50, 35.00), point(54.50, 32.50),
            miso_cross_a], pcbnew.B_Cu)
path(miso, [miso_cross_a, miso_cross_b], pcbnew.In2_Cu)
path(miso, [miso_cross_b, point(67.00, 36.00), point(67.00, 52.00),
            miso_south_a],
     pcbnew.B_Cu)
path(miso, [miso_south_a, miso_south_b], pcbnew.In2_Cu)
# The final leg stays on L3 beneath the SOIC body, clear of the L1 RXCAN pull-up
# and the L4 EN crossover.  Only the short pin escape returns to L1.
path(miso, [miso_south_b, point(72.40, 49.00), point(72.40, 47.00),
            point(72.00, 45.00), miso_dest], pcbnew.In2_Cu)
path(miso, [miso_dest, pad("U40", "15")])

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped FT-CAN SPI as {GROUP_NAME}")
