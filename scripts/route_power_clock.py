#!/usr/bin/env python3
"""Route reviewed, self-contained power and clock nets.

Only unique local nets are replaced, so this script remains safe while the
rest of the board is routed manually.  Shared rails and GND are deliberately
left untouched.
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
SIGNAL_WIDTH = pcbnew.FromMM(0.20)
SW_WIDTH = pcbnew.FromMM(0.60)
SW_JOIN_WIDTH = pcbnew.FromMM(0.25)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


board = pcbnew.LoadBoard(str(BOARD_PATH))
footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
nets = {str(name): net for name, net in board.GetNetsByName().items()}

OWNED_NETS = {
    "/USB + Power/SW_3V3",
    "/CAN_FT/MCP_OSC1",
    "/CAN_FT/MCP_OSC2",
}

for item in list(board.GetTracks()):
    if str(item.GetNetname()) in OWNED_NETS:
        board.Delete(item)


def pad(ref: str, number: str) -> pcbnew.VECTOR2I:
    found = footprints[ref].FindPadByNumber(number)
    if found is None:
        raise SystemExit(f"missing pad {ref}.{number}")
    return found.GetPosition()


def segment(net_name: str, start: pcbnew.VECTOR2I, end: pcbnew.VECTOR2I,
            width: int = SIGNAL_WIDTH) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetNetCode(nets[net_name].GetNetCode())
    track.SetLayer(pcbnew.F_Cu)
    track.SetWidth(width)
    track.SetStart(start)
    track.SetEnd(end)
    board.Add(track)


def path(net_name: str, points: list[pcbnew.VECTOR2I],
         width: int = SIGNAL_WIDTH) -> None:
    for start, end in zip(points, points[1:]):
        segment(net_name, start, end, width)


# TPS62132: join its three SW pins locally, then use a short, broad connection
# into L1.  No other copper is allowed to enlarge this high-dV/dt node.
sw = "/USB + Power/SW_3V3"
segment(sw, pad("U4", "1"), pad("U4", "3"), SW_JOIN_WIDTH)
path(sw, [pad("U4", "2"), point(40.70, 57.25), point(41.10, 57.00),
          pad("L1", "1")], SW_WIDTH)

# MCP2515 crystal loop.  OSC1 has the shortest direct leg.  OSC2 approaches
# crystal pad 3 from above/left to avoid grounded crystal pad 2.
osc1 = "/CAN_FT/MCP_OSC1"
path(osc1, [pad("U40", "8"), pad("Y40", "1")])
path(osc1, [pad("Y40", "1"), point(67.275, 48.20), pad("C43", "2")])

osc2 = "/CAN_FT/MCP_OSC2"
path(osc2, [pad("U40", "7"), point(69.00, 46.04), point(68.50, 42.50),
            point(65.00, 42.50), pad("Y40", "3")])
path(osc2, [pad("Y40", "3"), pad("C44", "2")])

pcbnew.SaveBoard(str(BOARD_PATH), board)
print("Routed TPS62132 switch node and MCP2515 crystal nets")
