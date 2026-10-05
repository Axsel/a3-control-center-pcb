#!/usr/bin/env python3
"""Route ESP32-to-TJA1055 ERR/STB/EN slow-control bundle."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_CAN_FT_CONTROL"

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


routes = (
    ("/CAN_FT_ERR", "7", "4", point(32.50, 35.16), point(82.50, 43.50),
     [point(30.00, 35.16), point(30.00, 79.00), point(80.00, 79.00),
      point(80.00, 43.50)]),
)

for net_name, esp_pin, tja_pin, source_via, dest_via, waypoints in routes:
    via(net_name, source_via)
    via(net_name, dest_via)
    path(net_name, [pad("U10", esp_pin), source_via])
    path(net_name, [source_via, *waypoints, dest_via], pcbnew.B_Cu)
    path(net_name, [dest_via, pad("U41", tja_pin)])

# STB shares the open lower L4 corridor, then changes to L3 only for its final
# approach so it can cross the existing ERR trunk.  R44 joins on that L3 leg.
stb = "/CAN_FT_STB"
stb_source = point(32.50, 36.43)
stb_bridge = point(76.00, 49.00)
stb_dest = point(82.50, 44.77)
stb_pull = point(82.50, 38.00)
for at in (stb_source, stb_bridge, stb_dest, stb_pull):
    via(stb, at)
path(stb, [pad("U10", "8"), stb_source])
path(stb, [stb_source, point(33.00, 36.43), point(33.00, 74.00),
           point(76.00, 74.00), stb_bridge], pcbnew.B_Cu)
path(stb, [stb_bridge, point(74.00, 46.00), point(76.00, 44.77), stb_dest],
     pcbnew.In2_Cu)
path(stb, [stb_dest, pad("U41", "5")])
path(stb, [pad("R44", "2"), stb_pull])
path(stb, [stb_pull, point(85.00, 38.00), point(85.00, 44.77), stb_dest],
     pcbnew.In2_Cu)

# EN uses the next lower L4 lane and a separate L3 approach.  Its pull-down
# enters from the right, clear of both STB and the U41 +5 V supply escape.
en = "/CAN_FT_EN"
en_source = point(34.50, 37.70)
en_bridge = point(72.00, 50.00)
en_cross_a = point(73.00, 46.04)
en_cross_b = point(75.00, 46.04)
en_mid = point(78.00, 46.04)
en_dest = point(82.50, 46.04)
en_pull = point(88.00, 36.00)
for at in (en_source, en_cross_a, en_cross_b, en_mid, en_dest, en_pull):
    via(en, at)
path(en, [pad("U10", "9"), en_source])
path(en, [en_source, point(36.00, 37.70), point(36.00, 71.00),
          point(72.00, 71.00), en_bridge], pcbnew.B_Cu)
path(en, [en_bridge, point(72.00, 46.04), en_cross_a], pcbnew.B_Cu)
path(en, [en_cross_a, en_cross_b])
path(en, [en_cross_b, en_mid], pcbnew.B_Cu)
path(en, [en_mid, en_dest], pcbnew.In2_Cu)
path(en, [en_dest, pad("U41", "6")])
path(en, [pad("R45", "2"), en_pull])
path(en, [en_pull, point(88.00, 46.04), en_dest], pcbnew.In2_Cu)

# R43's open-drain ERR pull-up lands directly on the vertical L4 ERR trunk.
err_pull = point(80.00, 52.00)
via("/CAN_FT_ERR", err_pull)
path("/CAN_FT_ERR", [pad("R43", "1"), err_pull])

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped FT-CAN mode/error controls as {GROUP_NAME}")
