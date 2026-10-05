#!/usr/bin/env python3
"""Apply the Revision A first-pass functional placement.

Run with the KiCad 10 Python environment via scripts/kicad-python.  This is a
repeatable coarse placement only: it intentionally creates no tracks, zones,
or final silkscreen.  Coordinates are millimetres in the existing 100 x 70 mm
outline (20,20) to (120,90).
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
MOUNTING_HOLE_LIBRARY = Path(
    "/var/lib/flatpak/runtime/org.kicad.KiCad.Library.Footprints/aarch64/"
    "stable/active/files/footprints/MountingHole.pretty"
)


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def set_footprint(fp, x: float, y: float, angle: float = 0.0) -> None:
    fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    fp.SetOrientationDegrees(angle)
    fp.Value().SetVisible(False)
    fp.Reference().SetVisible(True)
    fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
    fp.Reference().SetTextThickness(mm(0.12))


board = pcbnew.LoadBoard(str(BOARD_PATH))

# Mechanical footprints are intentionally board-only and therefore do not come
# from the schematic transfer.  Add them once and then treat them like every
# other deterministic placement item.
existing_refs = {fp.GetReference() for fp in board.GetFootprints()}
for ref in ("H1", "H2", "H3", "H4"):
    if ref not in existing_refs:
        hole = pcbnew.FootprintLoad(str(MOUNTING_HOLE_LIBRARY), "MountingHole_3.2mm_M3")
        if hole is None:
            raise SystemExit("could not load official MountingHole_3.2mm_M3 footprint")
        hole.SetReference(ref)
        board.Add(hole)

footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}

# Layout-driven GPIO reassignment: MCP2515 INT uses safe, non-strapping GPIO13
# on the module's lower edge; input-only GPIO34 becomes the spare test point.
# Rename the existing expansion net so the deterministic board rebuild stays
# synchronized with generate_schematic.py without a GUI netlist-transfer step.
nets = {str(name): net for name, net in board.GetNetsByName().items()}
spare = nets.get("/ESP32 + UI/EXP_GPIO13") or nets.get("/ESP32 + UI/EXP_GPIO34")
irq = nets["/CAN_FT_INT"]
cs = nets["/CAN_FT_CS"]
status = nets["/ESP32 + UI/STATUS_LED"]
if spare is None:
    raise SystemExit("missing ESP32 expansion net for GPIO reassignment")
spare.SetNetname("/ESP32 + UI/EXP_GPIO34")
footprints["U10"].FindPadByNumber("6").SetNet(spare)
footprints["U10"].FindPadByNumber("16").SetNet(irq)
footprints["U10"].FindPadByNumber("12").SetNet(status)
footprints["U10"].FindPadByNumber("26").SetNet(cs)

# Primary mechanical / edge placement.  The ESP32 antenna end faces the top
# edge; the official footprint's all-layer antenna keepout remains authoritative.
primary = {
    "U10": (45.0, 32.8, 0),
    "J1": (22.5, 69.0, 270),
    "J20": (95.5, 27.5, 0),
    "J40": (103.0, 47.0, 0),
    "J60": (110.0, 80.5, 0),
    "J10": (34.0, 86.0, 0),
    "SW1": (53.5, 85.0, 0),
    "SW2": (65.5, 85.0, 0),
    "SW3": (77.5, 85.0, 0),
    # Provisional enclosure posts.  The asymmetric lower-right support avoids
    # the board-edge RCA while still bracing the connector side of the board.
    "H1": (24.0, 32.0, 0),
    "H2": (116.0, 24.0, 0),
    "H3": (24.0, 86.0, 0),
    "H4": (116.0, 59.0, 0),
}

# USB-C, protection, USB-UART, and automatic-programming cluster.
usb = {
    "U1": (31.0, 69.0, 0), "U2": (39.0, 69.0, 0),
    "Q1": (46.0, 67.0, 0), "Q2": (46.0, 72.0, 0),
    "R1": (27.0, 81.5, 90), "R2": (29.0, 84.0, 90),
    "R3": (23.0, 58.0, 0), "R4": (25.5, 61.5, 0),
    "C1": (27.5, 77.5, 90), "C2": (32.5, 77.0, 0),
    "C3": (36.0, 77.0, 0), "C4": (25.0, 52.0, 270),
    "C5": (44.0, 77.0, 0), "C6": (36.0, 63.0, 90),
    "R9": (45.0, 61.5, 90), "R10": (42.5, 51.5, 0),
    "R11": (54.5, 53.5, 180), "R14": (56.0, 57.25, 180),
}

# Protected input and the two switching converters.  Inductors and bulk/input
# capacitors are deliberately kept in compact, separable power islands.
power = {
    "U3": (29.0, 56.5, 0), "C7": (33.5, 56.5, 0),
    "C8": (33.5, 59.5, 0), "R5": (30.5, 51.5, 90),
    "R6": (33.5, 51.5, 90), "TP1": (22.5, 48.5, 0),
    "TP2": (33.0, 54.0, 0), "TP8": (48.0, 64.0, 0),

    # U4 is rotated so VIN faces the protected USB source and SW faces L1.
    # This shortens both high-di/dt loops and leaves the quiet 3V3 output on
    # the inductor's far side.
    "U4": (38.5, 57.0, 180), "L1": (43.3, 57.0, 0),
    "C9": (48.0, 55.5, 180), "C10": (47.5, 59.5, 180),
    "C11": (37.0, 52.0, 90), "C12": (57.5, 55.0, 0),
    "C13": (56.5, 64.0, 0), "C14": (60.0, 64.0, 0),
    "C15": (64.0, 64.0, 0), "R7": (37.0, 74.0, 180),
    "R8": (29.0, 61.0, 0), "TP3": (52.5, 64.0, 0),

    "U5": (61.0, 57.5, 0), "L2": (65.5, 57.5, 270),
    "C16": (61.0, 61.0, 90), "C17": (57.5, 51.5, 0),
    "C18": (62.5, 51.5, 0), "C19": (61.0, 54.0, 0),
    # Keep the high-impedance U5 feedback node close to FB; both FB resistor
    # ends face right toward the IC while the rail ends face the quiet left.
    "R12": (56.5, 59.5, 180), "R13": (56.5, 61.5, 0),
    "TP4": (71.0, 57.5, 0), "TP5": (72.0, 66.0, 0),
}

# ESP32 support, accessible UI, OLED connector, and debug points.
esp_ui = {
    "C20": (32.5, 32.0, 0), "C21": (32.5, 27.5, 0),
    "C22": (32.5, 29.8, 0), "C23": (48.0, 48.5, 0),
    "D10": (28.5, 43.0, 0), "R20": (57.0, 67.0, 0),
    "R21": (57.0, 70.0, 0), "R22": (52.0, 71.0, 0),
    "R23": (42.0, 74.5, 0), "R24": (44.0, 82.0, 0),
    "R25": (48.0, 79.5, 0), "R26": (32.0, 43.0, 180),
    "R27": (60.5, 49.5, 0),
    "TP6": (50.5, 57.5, 0), "TP7": (40.5, 60.5, 0),
    "TP10": (55.0, 80.0, 0), "TP11": (59.0, 80.0, 0),
    "TP12": (30.0, 39.0, 0), "TP13": (67.0, 80.0, 0),
    "TP14": (30.0, 35.0, 0), "TP15": (31.0, 47.0, 0),
}

# High-speed CAN: connector -> protection -> transceiver.  Bypass resistors
# reserve a future CMC without forcing an unverified choke into Revision A.
can_hs = {
    "D20": (86.5, 27.5, 90), "R30": (82.5, 25.5, 0),
    "R31": (82.5, 29.5, 0), "JP20": (105.0, 37.0, 0),
    "R32": (99.0, 37.0, 0), "U20": (76.5, 28.0, 0),
    "C30": (70.8, 28.6, 0), "C31": (70.5, 34.0, 0),
    "TP20": (78.0, 21.5, 0), "TP21": (91.0, 33.0, 0),
}

# Fault-tolerant CAN: MCP2515 and crystal remain left of the 5 V transceiver;
# bus termination/bias options stay immediately behind the connector.
can_ft = {
    "U40": (75.0, 43.5, 0), "Y40": (66.0, 45.5, 90),
    "C40": (80.0, 34.0, 180), "C41": (74.0, 36.0, 0),
    "C42": (78.0, 36.0, 0), "C43": (66.5, 49.5, 0),
    "C44": (64.0, 41.0, 0), "R40": (68.0, 52.0, 0),
    "R41": (84.0, 59.0, 0), "R42": (76.0, 52.0, 0),
    "R43": (80.0, 52.0, 0), "R44": (82.0, 36.0, 0),
    "R45": (85.0, 36.0, 0),
    "U41": (86.5, 43.5, 0), "C45": (88.0, 34.0, 0),
    "C46": (86.0, 51.0, 0), "R46": (93.0, 39.0, 0),
    "R47": (95.0, 41.5, 0), "R48": (88.0, 55.0, 270),
    "R49": (91.0, 55.0, 270), "R50": (60.0, 45.0, 0),
    "JP40": (95.0, 56.0, 0), "JP41": (100.0, 56.0, 0),
    "D40": (96.0, 47.0, 90), "TP40": (106.0, 58.0, 0),
    "TP41": (110.0, 58.0, 0),
}

# Composite-video quiet island.  The DNP 470 uF capacitor is left enough room
# for its 8 x 10 mm can, while the active DC-coupled path is the default.
video = {
    "U60": (91.0, 72.0, 0), "C60": (84.0, 69.0, 0),
    "C61": (88.0, 77.0, 0), "C62": (94.0, 77.0, 0),
    "C63": (91.0, 84.0, 0), "D60": (104.0, 70.0, 90),
    "R60": (80.0, 70.5, 0), "R61": (84.0, 75.0, 0),
    "R62": (99.0, 72.0, 0), "R63": (79.0, 75.0, 0),
    "JP60": (95.0, 68.0, 0), "JP61": (99.0, 68.0, 0),
    "JP62": (82.0, 78.0, 0), "TP60": (77.0, 67.0, 0),
    "TP61": (99.0, 64.0, 0), "TP62": (104.0, 64.0, 0),
}

placement = {}
for group in (primary, usb, power, esp_ui, can_hs, can_ft, video):
    placement.update(group)

missing = sorted(set(footprints) - set(placement))
extra = sorted(set(placement) - set(footprints))
if missing or extra:
    raise SystemExit(f"placement mismatch: missing={missing}, extra={extra}")

for ref, (x, y, angle) in placement.items():
    set_footprint(footprints[ref], x, y, angle)

pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Placed {len(placement)} footprints in {BOARD_PATH}")
