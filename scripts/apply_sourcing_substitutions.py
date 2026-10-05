#!/usr/bin/env python3
"""Apply the current JLC sourcing substitutions to the placed PCB.

J60 preserves the former signal and ground pad centers. L1 uses its current
manufacturer land pattern; rerun the power routing passes after replacement.
"""

from pathlib import Path
import os
import sys
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
LIB_PATH = ROOT / "hardware" / "lib" / "a3-control-center.pretty"


def footprint_map(board):
    return {fp.GetReference(): fp for fp in board.GetFootprints()}


def replace_footprint(board, ref, lib_name, value, position_mm, angle_deg, pad_nets):
    print(f"Loading {ref}/{lib_name}", flush=True)
    old = footprint_map(board)[ref]
    new = pcbnew.FootprintLoad(str(LIB_PATH), lib_name)
    if new is None:
        raise RuntimeError(f"Unable to load {lib_name}")
    new.SetReference(ref)
    new.SetValue(value)
    new.SetPath(old.GetPath())
    new.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(position_mm[0]), pcbnew.FromMM(position_mm[1])))
    new.SetOrientationDegrees(angle_deg)
    new.SetFPID(pcbnew.LIB_ID("A3_Control_Center", lib_name))
    for pad in new.Pads():
        net_name = pad_nets[pad.GetNumber()]
        pad.SetNet(board.FindNet(net_name))
    print(f"Configured {ref} pads", flush=True)
    board.Remove(old)
    print(f"Removed old {ref}", flush=True)
    board.Add(new)
    new.thisown = False
    print(f"Replaced {ref} with {lib_name}", flush=True)


target = sys.argv[1] if len(sys.argv) > 1 else ""
if target not in {"L1", "J60"}:
    raise SystemExit("usage: apply_sourcing_substitutions.py L1|J60")

board = pcbnew.LoadBoard(str(BOARD_PATH))
print("Loaded board", flush=True)

if target == "L1":
    footprint_map(board)["L2"].SetValue("1.5uH XGL4020-152MEC")
    replace_footprint(
        board, "L1", "WPN4020H", "2.2uH WPN4020H2R2MT",
        (43.3, 57.0), 0.0,
        {"1": "/USB + Power/SW_3V3", "2": "/+3V3"},
    )
else:
    replace_footprint(
        board, "J60", "RCJ-014", "RCJ-014",
        (110.0, 80.5), 0.0,
        {"1": "/GND", "2": "/Composite Video/VIDEO_RCA"},
    )

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Applied D079 footprint update for {target}")
sys.stdout.flush()
# KiCad 10 Flatpak's SWIG bindings can double-destroy transferred footprint
# objects during interpreter shutdown.  The board has already been saved; use
# a clean process exit after flushing output to avoid that binding-only crash.
os._exit(0)
