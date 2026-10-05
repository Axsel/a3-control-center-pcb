#!/usr/bin/env python3
"""Route the OLED and local user-interface circuitry."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_UI"

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


# Active-high status LED.  The LED cathode receives a short dedicated L2
# ground drop; no boot-strapping pin is involved (STATUS_LED is GPIO27).
status = "/ESP32 + UI/STATUS_LED"
path(status, [pad("U10", "12"), point(34.50, 41.51),
              point(33.50, 42.50), pad("R26", "1")])

status_a = "/ESP32 + UI/STATUS_LED_A"
path(status_a, [pad("R26", "2"), pad("D10", "2")])

led_gnd = point(26.50, 43.00)
via("/GND", led_gnd)
path("/GND", [pad("D10", "1"), led_gnd])

# OLED connector local fanout.  R24/R25 remain DNP by default because the
# selected DFR0486 module already includes I2C pull-ups, but their pads are
# fully wired for controlled population during bring-up.
scl = "/ESP32 + UI/OLED_SCL"
path(scl, [pad("J10", "3"), point(38.00, 84.50),
           point(41.50, 82.00), pad("R24", "1")])

sda = "/ESP32 + UI/OLED_SDA"
path(sda, [pad("J10", "4"), point(43.00, 86.00),
           point(46.50, 83.50), point(46.50, 80.20), pad("R25", "1")])

# The ESP32-to-OLED I2C pair gets beyond the module antenna keepout and the
# already-routed CAN barrier, then follows adjacent B.Cu perimeter lanes. SCL
# uses a short L3 escape while SDA weaves around the CAN traces on B.Cu. L2 is
# deliberately left as an uninterrupted ground plane.
scl_esp_via = point(55.50, 30.08)
sda_esp_via = point(58.00, 34.80)
scl_outer_via = point(76.00, 29.00)
sda_bridge = point(66.50, 30.50)
sda_outer = point(77.00, 34.00)
scl_oled_via = point(43.20, 84.00)
sda_oled_via = point(46.50, 84.00)
for net_name, at in (
        (scl, scl_esp_via), (sda, sda_esp_via),
        (scl, scl_outer_via),
        (scl, scl_oled_via), (sda, sda_oled_via)):
    via(net_name, at)

path(scl, [pad("U10", "36"), scl_esp_via])
path(sda, [pad("U10", "33"), point(54.80, 33.89),
           point(55.10, 34.80), sda_esp_via])
path(scl, [scl_esp_via, point(54.00, 30.08), point(54.00, 27.50),
           point(67.50, 27.50), point(67.50, 26.80),
           point(71.50, 26.80), point(73.00, 29.00), scl_outer_via],
     pcbnew.In2_Cu)
path(sda, [sda_esp_via, point(58.00, 30.50),
           point(66.00, 30.50), sda_bridge], pcbnew.B_Cu)
path(sda, [sda_bridge, point(69.50, 26.50),
           point(69.50, 24.50), point(75.00, 24.50),
           point(75.00, 34.00), sda_outer],
     pcbnew.B_Cu)
path(scl, [scl_outer_via, point(76.00, 23.50),
           point(91.50, 23.50), point(91.50, 43.80),
           point(92.00, 44.20), point(92.00, 45.40),
           point(91.50, 45.80), point(91.50, 84.80),
           point(44.00, 84.80), scl_oled_via], pcbnew.B_Cu)
path(sda, [sda_outer,
           point(77.00, 25.00), point(90.50, 25.00),
           point(90.50, 33.20), point(89.20, 33.20),
           point(89.20, 40.50), point(90.50, 40.50),
           point(90.50, 76.00),
           point(89.20, 76.00), point(89.20, 78.00),
           point(90.50, 78.00), point(90.50, 82.00),
           point(48.50, 82.00), sda_oled_via],
     pcbnew.B_Cu)
path(scl, [scl_oled_via, pad("R24", "1")])
path(sda, [sda_oled_via, pad("R25", "1")])

oled_3v3_r24 = point(44.80, 83.00)
oled_3v3_r25 = point(48.80, 80.50)
for at in (oled_3v3_r24, oled_3v3_r25):
    via("/+3V3", at)
path("/+3V3", [pad("J10", "1"), point(34.00, 83.50),
                oled_3v3_r24, oled_3v3_r25], pcbnew.In2_Cu)
path("/+3V3", [oled_3v3_r24, pad("R24", "2")])
path("/+3V3", [oled_3v3_r25, pad("R25", "2")])

# Optional active-low user button.  The GPIO-to-pullup branch uses the clear
# upper B.Cu channel beneath the module keepout.  The switch branch takes the
# otherwise unused lower perimeter so it does not cut through the OLED pair or
# the programming/CAN fanout.
user = "/ESP32 + UI/USER_BUTTON"
user_u_via = point(38.00, 31.35)
user_r_via = point(58.50, 49.50)
user_sw_via = point(84.00, 88.50)
user_usb_top_via = point(21.50, 60.00)
user_usb_bottom_via = point(21.50, 75.50)
user_gnd_via = point(71.00, 87.25)
user_pullup_via = point(64.50, 49.50)
for net_name, at in (
        (user, user_u_via), (user, user_r_via), (user, user_sw_via),
        (user, user_usb_top_via), (user, user_usb_bottom_via),
        ("/GND", user_gnd_via), ("/+3V3", user_pullup_via)):
    via(net_name, at)

path(user, [pad("U10", "4"), user_u_via])
path(user, [user_u_via, point(40.00, 28.00),
            point(50.00, 28.00), point(50.00, 45.50),
            point(54.50, 45.50), point(54.50, 49.50), user_r_via],
     pcbnew.B_Cu)
path(user, [user_r_via, pad("R27", "1")])

path(user, [user_u_via, point(27.00, 31.35), point(27.00, 28.50),
            point(21.50, 28.50), user_usb_top_via],
     pcbnew.B_Cu)
path(user, [user_usb_top_via, point(23.50, 61.00),
            point(23.50, 75.00), user_usb_bottom_via], pcbnew.In2_Cu)
path(user, [user_usb_bottom_via, point(21.50, 88.50), user_sw_via],
     pcbnew.B_Cu)
path(user, [user_sw_via, point(84.00, 82.75), pad("SW3", "1")])

path("/GND", [pad("SW3", "2"), point(71.50, 87.25), user_gnd_via])
path("/+3V3", [pad("R27", "2"), user_pullup_via])
path("/+3V3", [user_pullup_via, point(65.00, 47.00),
                point(64.00, 45.00), point(61.50, 44.50)], pcbnew.In2_Cu)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped UI block as {GROUP_NAME}")
