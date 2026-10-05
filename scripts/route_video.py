#!/usr/bin/env python3
"""Route the Revision A composite-video analog block."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_VIDEO"

SIG = pcbnew.FromMM(0.20)
VIDEO = pcbnew.FromMM(0.30)
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
            layer: int = pcbnew.F_Cu, width: int = SIG) -> None:
    item = pcbnew.PCB_TRACK(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetLayer(layer)
    item.SetWidth(width)
    item.SetStart(start)
    item.SetEnd(end)
    add(item)


def path(net_name: str, points: list[pcbnew.VECTOR2I],
         layer: int = pcbnew.F_Cu, width: int = SIG) -> None:
    for start, end in zip(points, points[1:]):
        segment(net_name, start, end, layer, width)


def via(net_name: str, at: pcbnew.VECTOR2I) -> None:
    item = pcbnew.PCB_VIA(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetPosition(at)
    item.SetWidth(VIA_DIAMETER)
    item.SetDrill(VIA_DRILL)
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    add(item)


video_dac = "/VIDEO_DAC"
video_dac_ser = "/Composite Video/VIDEO_DAC_SER"
video_in = "/Composite Video/VIDEO_IN"
video_buf = "/Composite Video/VIDEO_BUF_OUT"
video_src = "/Composite Video/VIDEO_SRC"
video_ac = "/Composite Video/VIDEO_AC_OPTION"
video_passive = "/Composite Video/VIDEO_PASSIVE"
video_rca = "/Composite Video/VIDEO_RCA"

# DAC input options: R60 is the normal source resistor into C60. R61 is the
# DNP DC-link experiment and R63/JP62 are the DNP passive-output experiment.
path(video_dac_ser, [pad("R60", "2"), point(82.00, 70.50),
                     pad("C60", "1")])
path(video_dac_ser, [point(82.00, 70.50), point(82.00, 75.00),
                     pad("R61", "1")])
path(video_in, [pad("C60", "2"), point(86.00, 69.00),
                pad("U60", "1")])
path(video_in, [pad("R61", "2"), point(86.00, 75.00),
                point(86.00, 69.00)])

# THS7314 local 3.3 V and ground. Existing distribution vias at (90,77) and
# (95.5,79) are reused; added ground drops are local to the analog block.
path("/+3V3", [pad("U60", "4"), point(88.50, 76.00),
                pad("C61", "2"), point(90.00, 77.00)])
path("/+3V3", [pad("C62", "2"), point(95.50, 79.00)])

gnd_u60 = point(87.00, 72.00)
via("/GND", gnd_u60)
path("/GND", [pad("U60", "2"), gnd_u60])
path("/GND", [pad("U60", "3"), point(87.50, 72.64), gnd_u60])
path("/GND", [pad("U60", "5"), point(94.30, 74.20)])
path("/GND", [pad("C61", "1"), point(86.30, 77.00)])
path("/GND", [pad("C62", "1"), point(92.00, 75.20)])

# Buffered output and test point.
path(video_buf, [pad("U60", "8"), point(95.00, 70.10),
                 pad("R62", "1")])
buf_tp_via_a = point(96.00, 70.50)
buf_tp_via_b = point(99.00, 65.00)
for at in (buf_tp_via_a, buf_tp_via_b):
    via(video_buf, at)
path(video_buf, [point(95.00, 70.10), buf_tp_via_a])
path(video_buf, [buf_tp_via_a, point(94.00, 64.00), buf_tp_via_b],
     pcbnew.In2_Cu)
path(video_buf, [buf_tp_via_b, pad("TP61", "1")])

# Default DC output. The optional C63/JP61 AC branch is routed separately after
# the default path is clean so it cannot become an unterminated analog stub.
src_via_a = point(100.50, 72.00)
src_via_b = point(94.00, 67.00)
for at in (src_via_a, src_via_b):
    via(video_src, at)
path(video_src, [pad("R62", "2"), src_via_a], width=VIDEO)
path(video_src, [src_via_a, point(100.50, 66.50),
                 point(94.00, 66.50), src_via_b], pcbnew.B_Cu, VIDEO)
path(video_src, [src_via_b, pad("JP60", "1")], width=VIDEO)

src_c63_via = point(88.00, 83.00)
via(video_src, src_c63_via)
path(video_src, [pad("C63", "1"), src_c63_via])
path(video_src, [src_c63_via, point(88.00, 86.00),
                 point(104.00, 86.00),
                 point(106.00, 78.00), point(106.00, 74.00),
                 src_via_a], pcbnew.In2_Cu)

# Optional output AC coupling. C63 and JP61 are both DNP/open by default; this
# branch has no electrical effect unless the documented alternative is fitted.
ac_via_a = point(97.00, 83.00)
ac_via_b = point(97.00, 68.00)
for at in (ac_via_a, ac_via_b):
    via(video_ac, at)
path(video_ac, [pad("C63", "2"), point(97.00, 84.00), ac_via_a])
path(video_ac, [ac_via_a, point(98.00, 80.00), point(98.00, 74.00),
                point(94.00, 70.00), ac_via_b], pcbnew.B_Cu)
path(video_ac, [ac_via_b, pad("JP61", "1")])

# RCA output spine. JP60 is closed by default; JP61 and JP62 are open.
passive_rca_via_a = point(83.50, 78.00)
passive_rca_mid_via = point(102.00, 81.00)
passive_rca_via_b = point(108.00, 76.00)
for at in (passive_rca_via_a, passive_rca_mid_via, passive_rca_via_b):
    via(video_rca, at)
path(video_rca, [pad("JP60", "2"), point(96.50, 66.00),
                 point(99.65, 66.00), pad("JP61", "2"),
                 point(101.50, 68.00), pad("D60", "1"),
                 point(106.00, 73.00), passive_rca_via_b,
                 pad("J60", "1")], width=VIDEO)
path(video_rca, [point(101.50, 68.00), point(104.00, 64.00),
                 pad("TP62", "1")], width=VIDEO)
path(video_rca, [pad("JP62", "2"), passive_rca_via_a], width=VIDEO)
path(video_rca, [passive_rca_via_a, point(84.00, 81.00),
                 passive_rca_mid_via], pcbnew.In2_Cu, VIDEO)
path(video_rca, [passive_rca_mid_via, point(109.00, 81.00),
                 passive_rca_via_b], pcbnew.B_Cu, VIDEO)

# Passive-output option and local DAC fanout. The long GPIO25 route is added
# after the local analog block is electrically clean.
path(video_passive, [pad("R63", "2"), pad("JP62", "1")])
path(video_dac, [pad("TP60", "1"), point(78.00, 68.00),
                 pad("R60", "1")])
path(video_dac, [point(78.00, 68.00), point(77.00, 73.00),
                 pad("R63", "1")])

# GPIO25 analog feed.  It descends between the existing STB/EN trunks, uses a
# short L3 bridge only to cross the FT-CAN ERR barrier, then follows the quiet
# lower perimeter.  A final L3 approach reaches the local video star without
# crossing the OLED pair or the bottom-row controls.  L2 remains pure ground.
dac_esp_via = point(34.00, 38.97)
dac_stb_right_via = point(34.00, 72.20)
dac_stb_left_via = point(32.00, 75.00)
dac_err_bottom_via = point(31.00, 81.00)
dac_bottom_via = point(65.00, 87.50)
dac_tp_via = point(67.00, 81.00)
dac_turn_via = point(70.00, 78.00)
dac_local_via = point(78.00, 72.00)
for at in (dac_esp_via, dac_stb_right_via, dac_stb_left_via,
           dac_err_bottom_via, dac_bottom_via, dac_tp_via,
           dac_turn_via, dac_local_via):
    via(video_dac, at)

path(video_dac, [pad("U10", "10"), dac_esp_via])
path(video_dac, [dac_esp_via,
                 dac_stb_right_via], pcbnew.B_Cu)
path(video_dac, [dac_stb_right_via, dac_stb_left_via])
path(video_dac, [dac_stb_left_via, dac_err_bottom_via], pcbnew.In2_Cu)
path(video_dac, [dac_err_bottom_via, point(31.00, 87.50),
                 dac_bottom_via], pcbnew.B_Cu)
path(video_dac, [dac_bottom_via, dac_tp_via,
                 dac_turn_via], pcbnew.In2_Cu)
path(video_dac, [dac_turn_via, point(77.00, 78.00),
                 point(77.00, 74.00), dac_local_via], pcbnew.B_Cu)
path(video_dac, [dac_tp_via, pad("TP13", "1")])
path(video_dac, [dac_local_via, point(77.00, 73.00)])

# Connector-side ESD and shield returns.
path("/GND", [pad("D60", "2"), point(105.50, 68.95)])
video_gnd = point(106.00, 69.00)
via("/GND", video_gnd)
path("/GND", [point(105.50, 68.95), video_gnd])
# RCJ-014 has three large pin-1 shell stakes tied directly to GND.  They make
# the former KLPX pad-to-via stub unnecessary and avoid a hole-to-hole conflict.

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped composite-video block as {GROUP_NAME}")
