#!/usr/bin/env python3
"""Route the USB-UART programming and ESP32 boot-control block."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "hardware" / "dual_can_esp32.kicad_pcb"
GROUP_NAME = "SCRIPT_PROGRAMMING"

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


# UART0 is deliberately routed away from the USB differential pair.  The two
# slow nets escape east from the module, use L3 to cross the existing HS-CAN
# diagonal, and descend on L4.  A second short L3 bridge crosses the FT-CAN
# interrupt trunk before the traces fan into the CP2102N top edge.
uart_tx = "/UART0_TX"
tx_esp = point(60.50, 31.35)
tx_cross_top = point(60.50, 35.00)
tx_cross_bottom = point(60.50, 37.30)
tx_irq_east = point(60.50, 47.10)
tx_drop = point(51.00, 58.50)
tx_usb = point(39.00, 65.40)
for at in (tx_esp, tx_cross_top, tx_cross_bottom, tx_irq_east,
           tx_drop, tx_usb):
    via(uart_tx, at)
path(uart_tx, [pad("U10", "35"), tx_esp])
path(uart_tx, [tx_esp, tx_cross_top], pcbnew.B_Cu)
path(uart_tx, [tx_cross_top, tx_cross_bottom], pcbnew.In2_Cu)
path(uart_tx, [tx_cross_bottom, tx_irq_east], pcbnew.B_Cu)
path(uart_tx, [tx_irq_east, point(51.00, 47.10), tx_drop])
path(uart_tx, [tx_drop, point(51.00, 64.00), point(43.00, 62.00),
               point(39.00, 62.00), tx_usb], pcbnew.B_Cu)
path(uart_tx, [tx_usb, pad("U2", "25")])
path(uart_tx, [tx_drop, pad("TP6", "1")])

uart_rx = "/UART0_RX"
rx_esp = point(59.50, 35.20)
rx_cross_top = point(59.50, 36.50)
rx_cross_bottom = point(56.50, 41.45)
rx_irq_east = point(59.50, 47.90)
rx_drop = point(53.00, 58.50)
rx_bottom_east = point(53.00, 61.00)
rx_bottom_west = point(50.20, 61.00)
rx_usb = point(38.50, 64.60)
for at in (rx_esp, rx_cross_top, rx_cross_bottom, rx_irq_east,
           rx_drop, rx_bottom_east, rx_bottom_west, rx_usb):
    via(uart_rx, at)
path(uart_rx, [pad("U10", "34"), point(55.00, 32.62),
               point(55.00, 33.30), point(59.50, 33.30), rx_esp])
path(uart_rx, [rx_esp, rx_cross_top], pcbnew.B_Cu)
path(uart_rx, [rx_cross_top, rx_cross_bottom], pcbnew.In2_Cu)
path(uart_rx, [rx_cross_bottom, rx_irq_east], pcbnew.B_Cu)
path(uart_rx, [rx_irq_east, point(53.00, 47.90), rx_drop])
path(uart_rx, [rx_drop, rx_bottom_east], pcbnew.B_Cu)
path(uart_rx, [rx_bottom_east, rx_bottom_west], pcbnew.In2_Cu)
path(uart_rx, [rx_bottom_west, point(37.00, 61.00),
               point(37.00, 63.80), rx_usb], pcbnew.B_Cu)
path(uart_rx, [rx_usb, pad("U2", "26")])
rx_test = point(43.50, 61.00)
via(uart_rx, rx_test)
path(uart_rx, [rx_test, pad("TP7", "1")])

# Espressif-style crossed DTR/RTS network.  The CP2102N top-edge fanout is
# staggered around UART0, then each modem signal reaches both the appropriate
# transistor emitter and the opposite transistor's base resistor.
dtr = "/USB_DTR"
dtr_usb = point(37.50, 65.50)
dtr_q_entry = point(42.50, 69.00)
dtr_branch = point(44.00, 72.70)
dtr_r22 = point(50.30, 71.50)
for at in (dtr_usb, dtr_q_entry, dtr_branch, dtr_r22):
    via(dtr, at)
path(dtr, [pad("U2", "28"), dtr_usb])
path(dtr, [dtr_usb, dtr_q_entry], pcbnew.B_Cu)
path(dtr, [dtr_q_entry, point(43.00, 72.95), pad("Q2", "2")])
path(dtr, [pad("Q2", "2"), dtr_branch])
path(dtr, [dtr_branch, point(46.00, 76.50), point(50.30, 76.50),
           dtr_r22], pcbnew.In2_Cu)
path(dtr, [dtr_r22, pad("R22", "1")])

rts = "/USB_RTS"
rts_usb = point(40.00, 64.60)
rts_branch = point(44.20, 68.50)
rts_r23 = point(40.50, 73.50)
for at in (rts_branch, rts_r23):
    via(rts, at)
path(rts, [pad("U2", "24"), point(39.50, 65.80), rts_usb])
path(rts, [rts_usb, point(42.00, 64.60), point(44.00, 67.95),
           pad("Q1", "2")])
path(rts, [pad("Q1", "2"), rts_branch])
path(rts, [rts_branch, point(40.50, 72.50), rts_r23], pcbnew.In2_Cu)
path(rts, [rts_r23, pad("R23", "1")])

base_q1 = "/ESP32 + UI/AUTO_Q1_BASE"
base_q1_r = point(53.50, 70.50)
base_q1_q = point(44.30, 66.60)
for at in (base_q1_r, base_q1_q):
    via(base_q1, at)
path(base_q1, [pad("R22", "2"), base_q1_r])
path(base_q1, [base_q1_r, point(48.50, 68.50), base_q1_q],
     pcbnew.In2_Cu)
path(base_q1, [base_q1_q, pad("Q1", "1")])

base_q2 = "/ESP32 + UI/AUTO_Q2_BASE"
base_q2_r = point(42.80, 73.50)
base_q2_q = point(44.20, 70.50)
for at in (base_q2_r, base_q2_q):
    via(base_q2, at)
path(base_q2, [pad("R23", "2"), base_q2_r])
path(base_q2, [base_q2_r, base_q2_q], pcbnew.In2_Cu)
path(base_q2, [base_q2_q, pad("Q2", "1")])

# ESP32 EN joins its local RC capacitor before using the open far-west L3
# corridor to reach Q1.  The transistor/pull-up branch stays between the
# existing FT-CAN INT and EN trunks on L4.
en = "/ESP32 + UI/ESP_EN"
en_west = point(28.50, 33.50)
en_lower = point(44.00, 63.00)
for at in (en_west, en_lower):
    via(en, at)
path(en, [pad("U10", "3"), point(35.40, 30.08),
          point(34.80, 30.80), point(34.20, 31.20), pad("C20", "2")])
path(en, [pad("C20", "2"), point(33.45, 33.20), en_west])
path(en, [en_west, point(28.50, 63.00), en_lower], pcbnew.In2_Cu)
path(en, [en_lower, point(46.00, 64.00), point(48.00, 65.00),
          point(48.00, 67.00), pad("Q1", "3")])

en_q = point(47.60, 69.50)
en_pull = point(55.20, 69.00)
for at in (en_q, en_pull):
    via(en, at)
path(en, [pad("Q1", "3"), en_q])
path(en, [en_q, en_pull], pcbnew.B_Cu)
path(en, [en_pull, pad("R20", "1")])

en_test = point(54.00, 80.50)
via(en, en_test)
path(en, [en_pull, point(55.20, 78.00), en_test], pcbnew.In2_Cu)
path(en, [en_test, pad("TP10", "1"), point(55.00, 81.20),
          pad("SW1", "1")])

# The pull-up lands directly beside the existing diagonal L3 +3V3 trunk.
en_3v3 = point(58.80, 67.00)
via("/+3V3", en_3v3)
path("/+3V3", [pad("R20", "2"), en_3v3])

# GPIO0 leaves the module on L1, follows the open right-side L3 corridor around
# the end of the +3V3 diagonal, and returns west on L4 just above CAN_FT_EN.
gpio0 = "/ESP32 + UI/ESP_GPIO0"
gpio0_top = point(62.50, 46.00)
gpio0_cross = point(69.50, 56.50)
gpio0_east = point(69.50, 72.00)
gpio0_q = point(48.00, 72.00)
gpio0_pull = point(57.00, 72.00)
for at in (gpio0_top, gpio0_cross, gpio0_east, gpio0_q, gpio0_pull):
    via(gpio0, at)
path(gpio0, [pad("U10", "25"), point(54.50, 44.80),
             point(55.00, 46.00), gpio0_top])
path(gpio0, [gpio0_top, point(62.50, 55.00), gpio0_cross],
     pcbnew.In2_Cu)
path(gpio0, [gpio0_cross, gpio0_east])
path(gpio0, [gpio0_east, gpio0_q], pcbnew.B_Cu)
path(gpio0, [gpio0_q, point(48.00, 72.00), pad("Q2", "3")])
path(gpio0, [gpio0_pull, pad("R21", "1")])

gpio0_test_top = point(60.00, 72.00)
gpio0_test = point(60.00, 80.50)
for at in (gpio0_test_top, gpio0_test):
    via(gpio0, at)
path(gpio0, [gpio0_test_top, gpio0_test], pcbnew.In2_Cu)
path(gpio0, [gpio0_test, pad("TP11", "1"), point(60.00, 81.20),
             pad("SW2", "1")])

gpio0_3v3 = point(59.50, 69.50)
via("/+3V3", gpio0_3v3)
path("/+3V3", [pad("R21", "2"), gpio0_3v3])
path("/+3V3", [gpio0_3v3, point(64.00, 68.50)], pcbnew.In2_Cu)

pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Routed and grouped programming block as {GROUP_NAME}")
