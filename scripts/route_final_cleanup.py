#!/usr/bin/env python3
"""Finish Revision A auxiliary nets and local ground returns.

This script intentionally runs after every functional-block router.  Its
objects live in one named group so connectivity cleanup remains deterministic
and can be regenerated without touching reviewed critical routing.
"""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_FINAL_CLEANUP"

SIG = pcbnew.FromMM(0.20)
PWR = pcbnew.FromMM(0.50)
VIA_DIAMETER = pcbnew.FromMM(0.45)
VIA_DRILL = pcbnew.FromMM(0.20)
PWR_VIA_DIAMETER = pcbnew.FromMM(0.60)
PWR_VIA_DRILL = pcbnew.FromMM(0.30)


def point(x, y):
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


def pad(ref, number):
    found = footprints[ref].FindPadByNumber(number)
    if found is None:
        raise SystemExit(f"missing pad {ref}.{number}")
    return found.GetPosition()


def add(item):
    board.Add(item)
    group.AddItem(item)


def segment(net_name, start, end, layer=pcbnew.F_Cu, width=SIG):
    item = pcbnew.PCB_TRACK(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetLayer(layer)
    item.SetWidth(width)
    item.SetStart(start)
    item.SetEnd(end)
    add(item)


def path(net_name, points, layer=pcbnew.F_Cu, width=SIG):
    for start, end in zip(points, points[1:]):
        segment(net_name, start, end, layer, width)


def via(net_name, at, power=False):
    item = pcbnew.PCB_VIA(board)
    item.SetNetCode(nets[net_name].GetNetCode())
    item.SetPosition(at)
    item.SetWidth(PWR_VIA_DIAMETER if power else VIA_DIAMETER)
    item.SetDrill(PWR_VIA_DRILL if power else VIA_DRILL)
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    add(item)


def ground_drop(start, at):
    segment("/GND", start, at)
    via("/GND", at)


# Local ground islands.  Each via contacts the uninterrupted L2 GND plane.
ground_drop(pad("C20", "1"), point(31.55, 30.80))
ground_drop(pad("U10", "39"), point(45.50, 34.80))
ground_drop(pad("U10", "15"), point(38.00, 47.00))
ground_drop(pad("U10", "38"), point(52.50, 27.54))
ground_drop(pad("TP5", "1"), point(73.50, 65.00))
ground_drop(pad("U41", "13"), point(86.50, 42.00))

# USB/power-section ground islands.
ground_drop(pad("C1", "1"), point(28.50, 79.00))
ground_drop(pad("U3", "2"), point(27.00, 56.50))
ground_drop(pad("U1", "2"), point(30.75, 69.00))
ground_drop(pad("R1", "1"), point(27.00, 84.50))
ground_drop(pad("R2", "1"), point(29.00, 85.25))
ground_drop(pad("R3", "1"), point(20.80, 58.00))
ground_drop(pad("R4", "1"), point(24.00, 60.00))
ground_drop(pad("R6", "1"), point(34.50, 53.00))
ground_drop(pad("U2", "3"), point(35.50, 68.50))
ground_drop(pad("U2", "29"), point(39.00, 70.00))
ground_drop(pad("C4", "1"), point(26.50, 51.00))
ground_drop(pad("C5", "1"), point(42.525, 78.00))
ground_drop(pad("C6", "1"), point(35.00, 64.00))
ground_drop(pad("R8", "1"), point(27.50, 61.00))

# USB-C receptacle ground tabs escape outward from the dense high-speed pin
# field before dropping into L2.  This avoids both orientation-pair crossovers.
path("/GND", [pad("J1", "A1"), point(27.00, 65.80),
              point(28.50, 64.50)])
via("/GND", point(28.50, 64.50))
ground_drop(pad("J1", "A12"), point(27.50, 73.50))

# Join the four through-hole shell stakes on B.Cu.  The shell remains a
# distinct net and reaches board ground only through the documented RC link.
shield = "/USB + Power/USB_SHIELD"
path(shield, [point(25.605, 64.68), point(21.425, 64.68),
              point(21.425, 73.32), point(25.605, 73.32)], pcbnew.B_Cu)
path(shield, [pad("R4", "2"), point(25.605, 64.68)])
path(shield, [pad("R3", "2"), point(25.00, 59.00), pad("R4", "2")])
shield_c1 = point(25.60, 75.50)
via(shield, shield_c1)
path(shield, [point(25.605, 73.32), shield_c1], pcbnew.B_Cu)
path(shield, [shield_c1, pad("C1", "2")])

# Join both Type-C VBUS contact pairs and the connector-side USB ESD supply on
# L3.  The transition points sit outside the D+/D- crossover vias.
vbus = "/USB + Power/VBUS_RAW"
vbus_top = point(31.00, 65.50)
vbus_bottom = point(31.00, 72.50)
vbus_u1 = point(31.50, 69.00)
for at in (vbus_top, vbus_bottom, vbus_u1):
    via(vbus, at, power=True)
path(vbus, [pad("J1", "A4"), point(27.00, 66.60),
            point(27.00, 66.20), point(29.50, 65.50), vbus_top])
path(vbus, [pad("J1", "A9"), point(29.50, 71.40), vbus_bottom], width=PWR)
path(vbus, [pad("U1", "5"), vbus_u1], width=PWR)
vbus_mid = point(32.00, 69.00)
path(vbus, [vbus_top, vbus_mid, vbus_bottom],
     pcbnew.In2_Cu, PWR)
path(vbus, [vbus_mid, vbus_u1], pcbnew.In2_Cu, PWR)

# Raw-VBUS bulk capacitor C4 is local to the input test point and TPS2553
# feed, minimizing the connector-to-switch input loop.
path(vbus, [pad("C4", "2"), point(23.50, 52.95),
            point(22.50, 50.50), pad("TP1", "1")],
     width=PWR)

# USB-C default-current advertisements.  Keep the 5.1-k CC pulldowns close to
# the receptacle, below its dense D+/D-/VBUS pin field.  Short front escapes
# transition to the otherwise quiet back-layer pocket, then return to the
# component side immediately beside each resistor.
cc1 = "/USB + Power/USB_CC1"
cc1_j = point(24.00, 67.75)
cc1_l3 = point(24.00, 72.00)
cc1_r = point(27.00, 80.60)
for at in (cc1_j, cc1_l3, cc1_r):
    via(cc1, at)
path(cc1, [pad("J1", "A5"), cc1_j])
path(cc1, [cc1_j, cc1_l3], pcbnew.B_Cu)
path(cc1, [cc1_l3, point(24.00, 76.50), cc1_r], pcbnew.In2_Cu)
path(cc1, [cc1_r, pad("R1", "2")])

cc2 = "/USB + Power/USB_CC2"
cc2_j = point(22.70, 70.75)
cc2_l3 = point(22.70, 72.00)
cc2_b = point(22.70, 74.50)
cc2_l3b = point(22.70, 76.50)
cc2_r = point(29.00, 83.10)
for at in (cc2_j, cc2_l3, cc2_b, cc2_l3b, cc2_r):
    via(cc2, at)
path(cc2, [pad("J1", "B5"), cc2_j])
path(cc2, [cc2_j, cc2_l3], pcbnew.B_Cu)
path(cc2, [cc2_l3, cc2_b], pcbnew.In2_Cu)
path(cc2, [cc2_b, cc2_l3b], pcbnew.B_Cu)
path(cc2, [cc2_l3b, point(22.70, 80.50), point(26.00, 82.50), cc2_r],
     pcbnew.In2_Cu)
path(cc2, [cc2_r, pad("R2", "2")])

# TPS2553 input pins surround its ground pin, so join them around the package
# edge rather than running copper through the center pad.  The divider source
# and raw-input test point fan out into the open upper-left corridor.
path(vbus, [pad("U3", "1"), point(26.00, 55.55),
            point(26.00, 57.45), pad("U3", "3")], width=PWR)
path(vbus, [pad("U3", "1"), point(27.00, 53.50),
            point(29.00, 51.50), pad("R5", "2")], width=PWR)
path(vbus, [pad("R5", "2"), point(29.00, 49.50),
            point(24.00, 48.50), pad("TP1", "1")], width=PWR)

path("/USB + Power/USB_VBUS_SENSE",
     [pad("R5", "1"), point(31.50, 51.50), pad("R6", "2")])
vbus_sense = "/USB + Power/USB_VBUS_SENSE"
sense_src = point(31.50, 51.50)
sense_back = point(35.20, 50.50)
sense_u2 = point(37.50, 72.50)
for at in (sense_src, sense_back, sense_u2):
    via(vbus_sense, at)
path(vbus_sense, [sense_src, sense_back], pcbnew.In2_Cu)
path(vbus_sense,
     [sense_back, point(35.40, 52.00), point(35.40, 54.00),
      point(34.40, 54.80), point(34.40, 70.50),
      point(35.00, 71.20), point(35.00, 72.50), sense_u2],
     pcbnew.B_Cu)
path(vbus_sense, [sense_u2, pad("U2", "8")])
ilim = "/USB + Power/USB_ILIM"
ilim_u3 = point(30.80, 56.50)
ilim_r8 = point(29.40, 60.20)
for at in (ilim_u3, ilim_r8):
    via(ilim, at)
path(ilim, [pad("U3", "5"), ilim_u3])
path(ilim, [ilim_u3, point(29.60, 57.50), point(29.60, 59.50), ilim_r8],
     pcbnew.In2_Cu)
path(ilim, [ilim_r8, pad("R8", "2")])
path("/USB + Power/CP2102_RST",
     [pad("U2", "9"), point(38.00, 73.00), pad("R7", "1")])

# Carry the TPS2553 active-low fault indication under the protected-5-V
# backbone on L3.  The y=62.2 corridor remains above ESP_EN and below the
# power spine endpoint, with short component-layer escapes at both ends.
fault_src = point(31.00, 58.50)
fault_dst = point(46.00, 62.20)
for at in (fault_src, fault_dst):
    via("/USB + Power/USB_PWR_FAULT", at)
path("/USB + Power/USB_PWR_FAULT", [pad("U3", "4"), fault_src])
path("/USB + Power/USB_PWR_FAULT",
     [fault_src, point(30.50, 59.50), point(30.50, 61.50),
      point(33.00, 62.20), fault_dst],
     pcbnew.In2_Cu)
path("/USB + Power/USB_PWR_FAULT", [fault_dst, pad("R9", "1")])
path("/USB + Power/USB_PWR_FAULT",
     [fault_dst, point(47.00, 63.20), pad("TP8", "1")])

vbus_switch = point(25.00, 54.00)
via(vbus, vbus_switch, power=True)
path(vbus, [point(26.00, 55.55), vbus_switch], width=PWR)
vbus_en_w = point(27.00, 63.50)
vbus_en_e = point(29.40, 64.00)
for at in (vbus_en_w, vbus_en_e):
    via(vbus, at, power=True)
path(vbus, [vbus_switch, point(25.00, 62.00), vbus_en_w],
     pcbnew.In2_Cu, PWR)
path(vbus, [vbus_en_w, vbus_en_e], pcbnew.B_Cu, PWR)
path(vbus, [vbus_en_e, vbus_top], pcbnew.In2_Cu, PWR)


# Tactile switches have two physical pins per logical contact.  Join both
# halves and drop each ground contact to L2 locally.
path("/GND", [point(48.95, 87.25), point(58.05, 87.25)])
ground_drop(point(48.95, 87.25), point(48.00, 86.00))
path("/GND", [point(72.95, 87.25), point(82.05, 87.25)])
ground_drop(point(72.95, 87.25), point(72.00, 86.00))
ground_drop(point(60.95, 87.25), point(60.95, 86.00))
ground_drop(point(70.05, 87.25), point(70.05, 86.00))

# Protected 5 V completion and test point.  L3 is used for the long branches.
usb5 = "/USB + Power/+5V_USB"
# Protected-5-V bulk capacitor C5 is local to the L3 distribution backbone.
# Keep the protected-5-V layer-transition clear of the wider WPN4020H L1 pad.
usb5_c5_a = point(41.00, 59.60)
usb5_c5_b = point(52.00, 57.50)
usb5_c5_c = point(52.00, 62.50)
usb5_c5_d = point(51.20, 65.50)
usb5_c5_f = point(50.00, 67.50)
for at in (usb5_c5_a, usb5_c5_f):
    via(usb5, at, power=True)
path(usb5, [point(42.00, 61.50), usb5_c5_a], pcbnew.In2_Cu, PWR)
path(usb5, [usb5_c5_a, point(49.50, 57.50), usb5_c5_b,
            usb5_c5_c, usb5_c5_d, usb5_c5_f], pcbnew.B_Cu, PWR)
path(usb5, [usb5_c5_f, point(49.00, 70.20), point(49.00, 76.00),
            point(47.50, 78.00), pad("C5", "2")], width=PWR)
# Join the TPS62132 bottom input pad to its three left-side VIN pins around the
# package corner; the exposed center and adjacent bottom pads are ground/3V3.
path(usb5, [point(36.80, 58.4625), point(36.20, 57.75),
            pad("U4", "12")])
path(usb5, [point(31.50, 55.55), pad("TP2", "1")], width=PWR)

# C6 is the local protected-5-V bypass for the USB-UART block.  Its rotated
# placement gives the supply pad a direct escape to the existing L3 backbone
# while its other pad drops locally to the uninterrupted ground plane.
usb5_c6 = point(35.00, 60.50)
via(usb5, usb5_c6, power=True)
path(usb5, [pad("C6", "2"), usb5_c6], width=PWR)
path(usb5, [usb5_c6, point(35.20, 61.50)], pcbnew.In2_Cu, PWR)

# Keep the 5V_FT enable pull-up next to U5.  Its supply end drops directly
# onto the protected-5-V L3 spine; EN approaches U5 pad 14 from above between
# the input bypass capacitors.
usb5_r11 = point(55.00, 52.50)
via(usb5, usb5_r11, power=True)
path(usb5, [pad("R11", "2"), usb5_r11])
path(usb5, [usb5_r11, point(53.00, 52.50)], pcbnew.In2_Cu, PWR)
en5_src = point(55.325, 54.50)
en5_dst = point(60.775, 55.40)
for at in (en5_src, en5_dst):
    via("/USB + Power/EN_5VFT", at)
path("/USB + Power/EN_5VFT", [pad("R11", "1"), en5_src])
path("/USB + Power/EN_5VFT",
     [en5_src, point(56.00, 52.50), point(60.50, 52.50),
      point(61.00, 54.25), en5_dst], pcbnew.B_Cu)
path("/USB + Power/EN_5VFT", [en5_dst, pad("U5", "14")])

# Complete the nearby 3V3 pull-up/test branches against the existing L3 tree.
v3 = "/+3V3"
path(v3, [pad("R7", "2"), point(36.55, 75.50)])

v3_r9 = point(46.00, 59.175)
v3_tp3 = point(52.50, 65.00)
for at in (v3_r9, v3_tp3):
    via(v3, at, power=True)
path(v3, [pad("R9", "2"), v3_r9])
path(v3, [v3_r9, point(46.791, 59.175)], pcbnew.In2_Cu, PWR)

path(v3, [pad("TP3", "1"), v3_tp3])
path(v3, [v3_tp3, point(50.00, 64.50)], pcbnew.In2_Cu, PWR)

v3_r10 = point(44.00, 51.50)
via(v3, v3_r10, power=True)
path(v3, [pad("R10", "2"), v3_r10])
path(v3, [v3_r10, point(43.50, 53.50)], pcbnew.B_Cu, PWR)

# U4's remaining 3V3 output pad escapes away from the adjacent ground pads,
# then joins the existing bottom-layer 3V3 converter bridge from the west.
v3_u4_14 = point(38.00, 60.00)
via(v3, v3_u4_14, power=True)
path(v3, [pad("U4", "14"), point(38.25, 59.30), v3_u4_14])
path(v3, [v3_u4_14, point(36.50, 58.50), point(36.50, 53.50),
          point(43.50, 53.50)], pcbnew.B_Cu, PWR)

# U5 power-good pull-up is likewise local.  The logic trace reaches pad 2
# directly; the 3V3 end joins the nearby bottom-layer converter bridge.
v3_r14 = point(54.50, 57.25)
via(v3, v3_r14, power=True)
path(v3, [pad("R14", "2"), v3_r14])
path(v3, [v3_r14, point(54.50, 59.50), point(54.00, 60.30),
          point(54.00, 62.70), point(54.50, 65.786)],
     pcbnew.In2_Cu, PWR)
pg5_src = point(56.00, 56.50)
pg5_dst = point(59.00, 57.25)
for at in (pg5_src, pg5_dst):
    via("/USB + Power/PG_5VFT", at)
path("/USB + Power/PG_5VFT", [pad("R14", "1"), pg5_src])
path("/USB + Power/PG_5VFT", [pg5_src, pg5_dst], pcbnew.B_Cu)
path("/USB + Power/PG_5VFT", [pg5_dst, pad("U5", "2")])

path(v3, [point(80.825, 53.50), point(82.00, 54.50),
          point(84.00, 56.00)], width=PWR)

# R10 is deliberately local to U4: power-good is a short component-layer
# route and its pull-up reaches the nearby 3V3 backbone through one via.
path("/USB + Power/PG_3V3",
     [pad("U4", "4"), point(40.50, 54.50), point(41.675, 53.00),
      pad("R10", "1")])

# Complete the switch signal contacts to their already-routed test-point legs.
path("/ESP32 + UI/ESP_EN", [point(48.95, 82.75), point(58.05, 82.75)])
path("/ESP32 + UI/ESP_EN", [pad("SW1", "1"), point(55.00, 81.20)])
path("/ESP32 + UI/ESP_GPIO0", [point(60.95, 82.75), point(70.05, 82.75)])
path("/ESP32 + UI/ESP_GPIO0", [pad("SW2", "1"), point(60.00, 81.20)])

# The 5V_FT test pad is top copper; stitch it to the L3 rail that already
# passes immediately beneath it.
v5ft_tp = point(71.00, 58.50)
via("/+5V_FT", v5ft_tp, power=True)
path("/+5V_FT", [pad("TP4", "1"), v5ft_tp], width=PWR)
path("/+5V_FT", [v5ft_tp, point(71.00, 57.50)], pcbnew.In2_Cu, PWR)

# Exposed bus test points.
gpio34 = "/ESP32 + UI/EXP_GPIO34"
gpio34_esp = point(35.80, 33.89)
gpio34_tp = point(30.00, 34.00)
for at in (gpio34_esp, gpio34_tp):
    via(gpio34, at)
path(gpio34, [pad("U10", "6"), gpio34_esp])
path(gpio34, [gpio34_esp, gpio34_tp], pcbnew.B_Cu)
path(gpio34, [gpio34_tp, pad("TP14", "1")])

path("/ESP32 + UI/DAC2_RESERVED",
     [pad("U10", "11"), point(30.00, 40.24), pad("TP12", "1")])

gpio14 = "/ESP32 + UI/EXP_GPIO14"
gpio14_esp = point(35.50, 42.78)
gpio14_low = point(35.50, 46.00)
for at in (gpio14_esp, gpio14_low):
    via(gpio14, at)
path(gpio14, [pad("U10", "13"), gpio14_esp])
path(gpio14, [gpio14_esp, gpio14_low], pcbnew.B_Cu)
path(gpio14, [gpio14_low, point(34.00, 47.00), pad("TP15", "1")])

path("/CAN_HS/CAN_HS_L", [pad("TP21", "1"), point(91.00, 31.00)])

ft_h_tp = point(106.00, 60.00)
ft_h_bus = point(96.50, 52.00)
for at in (ft_h_tp, ft_h_bus):
    via("/CAN_FT/CAN_FT_H", at)
path("/CAN_FT/CAN_FT_H", [pad("TP40", "1"), ft_h_tp])
path("/CAN_FT/CAN_FT_H", [ft_h_tp, point(108.00, 56.00), ft_h_bus],
     pcbnew.B_Cu)
path("/CAN_FT/CAN_FT_H", [ft_h_bus, point(96.50, 54.00)])

ft_l_tp = point(110.00, 60.00)
ft_l_bus = point(106.00, 50.00)
for at in (ft_l_tp, ft_l_bus):
    via("/CAN_FT/CAN_FT_L", at)
path("/CAN_FT/CAN_FT_L", [pad("TP41", "1"), ft_l_tp])
path("/CAN_FT/CAN_FT_L", [ft_l_tp, point(114.00, 56.00), ft_l_bus],
     pcbnew.B_Cu)
path("/CAN_FT/CAN_FT_L", [ft_l_bus, point(106.00, 52.00)])

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed final auxiliary cleanup as {GROUP_NAME}")
