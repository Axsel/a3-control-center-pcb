#!/usr/bin/env python3
"""Route only reviewed Revision A critical nets.

Current scope is the USB 2.0 full-speed data path.  The Type-C receptacle's
duplicated orientation contacts require two short layer changes; the primary
pair stays on F.Cu over the future continuous L2 ground plane.  This script is
idempotent for the four USB data nets, but intentionally removes and recreates
all tracks/vias on those nets.  Do not run it after hand-editing those routes.
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
TRACK_WIDTH = pcbnew.FromMM(0.20)
VIA_DIAMETER = pcbnew.FromMM(0.45)
VIA_DRILL = pcbnew.FromMM(0.20)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


board = pcbnew.LoadBoard(str(BOARD_PATH))
footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
nets = {str(name): net for name, net in board.GetNetsByName().items()}

print(
    "USB routing source:",
    BOARD_PATH,
    "J1.A6=",
    pcbnew.ToMM(footprints["J1"].FindPadByNumber("A6").GetPosition().x),
    pcbnew.ToMM(footprints["J1"].FindPadByNumber("A6").GetPosition().y),
)

USB_NETS = {
    "/USB + Power/USB_CONN_DP",
    "/USB + Power/USB_CONN_DM",
    "/USB + Power/USB_DP",
    "/USB + Power/USB_DM",
}

# Preserve every unrelated/manual route while making this reviewed section
# repeatable.
for item in list(board.GetTracks()):
    if str(item.GetNetname()) in USB_NETS:
        # Delete(), rather than Remove(), is required by the KiCad 10 SWIG
        # bindings here.  Remove() detaches the item but leaves ownership in
        # an unsafe state and can segfault before SaveBoard().
        board.Delete(item)


def pad_point(ref: str, number: str) -> pcbnew.VECTOR2I:
    pad = footprints[ref].FindPadByNumber(number)
    if pad is None:
        raise SystemExit(f"missing pad {ref}.{number}")
    return pad.GetPosition()


def add_segment(net_name: str, start: pcbnew.VECTOR2I,
                end: pcbnew.VECTOR2I, layer: int = pcbnew.F_Cu) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetNetCode(nets[net_name].GetNetCode())
    track.SetLayer(layer)
    track.SetWidth(TRACK_WIDTH)
    track.SetStart(start)
    track.SetEnd(end)
    board.Add(track)


def add_path(net_name: str, points: list[pcbnew.VECTOR2I],
             layer: int = pcbnew.F_Cu) -> None:
    for start, end in zip(points, points[1:]):
        add_segment(net_name, start, end, layer)


def add_via(net_name: str, at: pcbnew.VECTOR2I) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetNetCode(nets[net_name].GetNetCode())
    via.SetPosition(at)
    via.SetWidth(VIA_DIAMETER)
    via.SetDrill(VIA_DRILL)
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(via)


conn_dp = "/USB + Power/USB_CONN_DP"
conn_dm = "/USB + Power/USB_CONN_DM"
usb_dp = "/USB + Power/USB_DP"
usb_dm = "/USB + Power/USB_DM"

# Primary Type-C orientation pair (A6/A7) on F.Cu.
dp_main = [pad_point("J1", "A6"), point(27.50, 68.75),
           point(28.00, 68.05), pad_point("U1", "1")]
dm_main = [pad_point("J1", "A7"), point(27.50, 69.25),
           point(28.00, 69.95), pad_point("U1", "3")]
add_path(conn_dp, dp_main)
add_path(conn_dm, dm_main)

# Alternate Type-C orientation contacts.  Their swapped order is resolved with
# one route above and one below the primary pair.  The through-vias are kept
# well clear of the opposite F.Cu trace; the two crossover routes then occupy
# different signal layers.
dp_via_in, dp_via_out = point(27.50, 70.50), point(28.00, 68.05)
dm_via_in, dm_via_out = point(27.50, 67.00), point(29.00, 69.95)
add_path(conn_dp, [pad_point("J1", "B6"), point(27.00, 69.75), dp_via_in])
add_path(conn_dm, [pad_point("J1", "B7"), point(27.00, 68.25), dm_via_in])
for name, at in ((conn_dp, dp_via_in), (conn_dp, dp_via_out),
                 (conn_dm, dm_via_in), (conn_dm, dm_via_out)):
    add_via(name, at)
add_path(conn_dp, [dp_via_in, point(28.00, 71.00),
                   dp_via_out], pcbnew.In2_Cu)
add_path(conn_dm, [dm_via_in, point(29.00, 67.00),
                   dm_via_out], pcbnew.B_Cu)

# ESD array to CP2102N.  These paired routes remain on F.Cu and converge only
# as required by the QFN's 0.5 mm D+/D- pin pitch.
add_path(usb_dp, [pad_point("U1", "6"), point(34.00, 68.05),
                  point(35.20, 69.00), pad_point("U2", "4")])
add_path(usb_dm, [pad_point("U1", "4"), point(34.00, 69.95),
                  point(35.20, 69.50), pad_point("U2", "5")])

pcbnew.SaveBoard(str(BOARD_PATH), board)
print(
    "Routed reviewed USB-C/ESD/CP2102N data nets;",
    "J1.A6 to first waypoint=",
    tuple(pcbnew.ToMM(v) for v in (dp_main[0].x, dp_main[0].y,
                                  dp_main[1].x, dp_main[1].y)),
)
