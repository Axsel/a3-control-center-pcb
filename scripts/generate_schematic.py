#!/usr/bin/env python3
"""Generate the reviewed KiCad 10 schematic hierarchy.

Connectivity in this file is the source used for repeatable capture.  It does
not replace datasheet review: every value and package used here is recorded in
the project design notes and must pass KiCad ERC plus visual review.
"""

from pathlib import Path
import subprocess

import kicad_sch_api as ksa


ROOT = Path(__file__).resolve().parents[1]
HW = ROOT / "hardware"
PROJECT = "dual_can_esp32"
KICAD_CLI = ROOT / "scripts" / "kicad-cli"

R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"
TP = "TestPoint:TestPoint_Pad_D1.0mm"
BUTTON = "Button_Switch_SMD:SW_Push_1P1T_NO_E-Switch_TL3301NxxxxxG"

# Nets that leave a child sheet.  They use hierarchical labels; all other
# names use local labels and therefore cannot leak accidentally between sheets.
HIERARCHICAL_NETS = {
    "+3V3",
    "+5V_FT",
    "GND",
    "UART0_TX",
    "UART0_RX",
    "USB_RTS",
    "USB_DTR",
    "CAN_HS_TX",
    "CAN_HS_RX",
    "CAN_FT_MOSI",
    "CAN_FT_MISO",
    "CAN_FT_SCK",
    "CAN_FT_CS",
    "CAN_FT_INT",
    "CAN_FT_STB",
    "CAN_FT_EN",
    "CAN_FT_ERR",
    "VIDEO_DAC",
}


def component(sch, lib_id, ref, value, pos, footprint=None, rotation=0, **props):
    return sch.components.add(
        lib_id,
        reference=ref,
        value=value,
        position=pos,
        footprint=footprint,
        rotation=rotation,
        **props,
    )


def net(sch, name, ref, pin, shape="passive"):
    # Component.get_pin_position() in kicad-sch-api 0.5.6 reverses two-pin
    # passives.  The schematic-level method is correct and is deliberately
    # used for every connection and no-connect marker.
    pos = sch.get_component_pin_position(ref, str(pin))
    if pos is None:
        raise ValueError(f"Missing pin {ref}.{pin} for net {name}")
    if name in HIERARCHICAL_NETS:
        sch.add_hierarchical_label(name, pos, shape=shape)
    else:
        sch.add_label(name, position=pos)


def nc(sch, ref, *pins):
    for pin in pins:
        pos = sch.get_component_pin_position(ref, str(pin))
        if pos is None:
            raise ValueError(f"Missing no-connect pin {ref}.{pin}")
        sch.no_connects.add(pos)


def two_pin(sch, lib_id, ref, value, pos, net1, net2, footprint, rotation=90, **props):
    component(sch, lib_id, ref, value, pos, footprint, rotation, **props)
    net(sch, net1, ref, "1")
    net(sch, net2, ref, "2")


def testpoint(sch, ref, signal, pos):
    component(sch, "Connector:TestPoint", ref, signal, pos, TP)
    net(sch, signal, ref, "1")


def power_flag(sch, ref, signal, pos):
    component(sch, "power:PWR_FLAG", ref, "PWR_FLAG", pos)
    net(sch, signal, ref, "1")


def new_child(parent, sheet_uuid):
    del parent, sheet_uuid
    sch = ksa.create_schematic(PROJECT)
    # References are globally unique across this project.  Avoid the current
    # kicad-sch-api hierarchy-context helper because it serializes its private
    # UUID path as a visible custom symbol field in KiCad 10.
    return sch


def build_power_usb(parent, sheet_uuid):
    s = new_child(parent, sheet_uuid)
    s.add_text("USB-C POWER, USB-UART, +3V3 AND +5V_FT", (90, 18), size=2.0, bold=True)
    s.add_text(
        "5 V / 1 A source required. No USB-PD. TPS2553 limit: 28.7 kΩ, about 0.90 A nominal.",
        (25, 23),
        size=1.1,
    )

    component(
        s,
        "Connector:USB_C_Receptacle_USB2.0_16P",
        "J1",
        "USB4105-GF-A",
        (35, 55),
        "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
        Manufacturer="GCT",
        MPN="USB4105-GF-A",
    )
    for pin in ("A4", "A9", "B4", "B9"):
        net(s, "VBUS_RAW", "J1", pin)
    for pin in ("A1", "A12", "B1", "B12"):
        net(s, "GND", "J1", pin)
    for pin in ("A6", "B6"):
        net(s, "USB_CONN_DP", "J1", pin)
    for pin in ("A7", "B7"):
        net(s, "USB_CONN_DM", "J1", pin)
    net(s, "USB_CC1", "J1", "A5")
    net(s, "USB_CC2", "J1", "B5")
    net(s, "USB_SHIELD", "J1", "SH")
    nc(s, "J1", "A8", "B8")

    two_pin(s, "Device:R", "R1", "5.1k 1%", (25, 82), "USB_CC1", "GND", R0603)
    two_pin(s, "Device:R", "R2", "5.1k 1%", (35, 82), "USB_CC2", "GND", R0603)
    two_pin(s, "Device:R", "R3", "1M", (45, 82), "USB_SHIELD", "GND", R0603)
    two_pin(s, "Device:C", "C1", "4.7nF 1kV C0G | FV32N472J102EFG", (55, 82), "USB_SHIELD", "GND", C1210)
    two_pin(s, "Device:R", "R4", "0R DNP", (65, 82), "USB_SHIELD", "GND", R0603)

    component(s, "Power_Protection:USBLC6-2SC6", "U1", "USBLC6-2SC6", (72, 55), "Package_TO_SOT_SMD:SOT-23-6")
    net(s, "USB_CONN_DP", "U1", "1")
    net(s, "USB_DP", "U1", "6")
    net(s, "USB_CONN_DM", "U1", "3")
    net(s, "USB_DM", "U1", "4")
    net(s, "GND", "U1", "2")
    net(s, "VBUS_RAW", "U1", "5")

    component(
        s,
        "Interface_USB:CP2102N-Axx-xQFN28",
        "U2",
        "CP2102N-A02-GQFN28R",
        (112, 55),
        "Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm",
        Manufacturer="Silicon Labs",
        MPN="CP2102N-A02-GQFN28R",
    )
    net(s, "GND", "U2", "3")
    net(s, "GND", "U2", "29")
    net(s, "USB_DP", "U2", "4")
    net(s, "USB_DM", "U2", "5")
    net(s, "+3V3", "U2", "6")
    net(s, "+3V3", "U2", "7")
    net(s, "USB_VBUS_SENSE", "U2", "8")
    net(s, "CP2102_RST", "U2", "9")
    net(s, "UART0_TX", "U2", "25")
    net(s, "UART0_RX", "U2", "26")
    net(s, "USB_RTS", "U2", "24")
    net(s, "USB_DTR", "U2", "28")
    nc(s, "U2", "1", "2", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "27")

    two_pin(s, "Device:R", "R5", "22.1k 1%", (90, 82), "VBUS_RAW", "USB_VBUS_SENSE", R0603)
    two_pin(s, "Device:R", "R6", "47.5k 1%", (100, 82), "USB_VBUS_SENSE", "GND", R0603)
    two_pin(s, "Device:R", "R7", "1k", (110, 82), "+3V3", "CP2102_RST", R0603)
    two_pin(s, "Device:C", "C2", "4.7uF", (120, 82), "+3V3", "GND", C0805)
    two_pin(s, "Device:C", "C3", "100nF", (130, 82), "+3V3", "GND", C0603)

    component(s, "a3-control-center:TPS2553DBV", "U3", "TPS2553DBVR", (47, 112), "Package_TO_SOT_SMD:SOT-23-6")
    net(s, "VBUS_RAW", "U3", "1")
    net(s, "GND", "U3", "2")
    net(s, "VBUS_RAW", "U3", "3")
    net(s, "USB_PWR_FAULT", "U3", "4")
    net(s, "USB_ILIM", "U3", "5")
    net(s, "+5V_USB", "U3", "6")
    two_pin(s, "Device:R", "R8", "28.7k 1%", (30, 132), "USB_ILIM", "GND", R0603)
    two_pin(s, "Device:R", "R9", "10k", (40, 132), "+3V3", "USB_PWR_FAULT", R0603)
    two_pin(s, "Device:C", "C4", "1uF", (50, 132), "VBUS_RAW", "GND", C0805)
    two_pin(s, "Device:C", "C5", "47uF", (60, 132), "+5V_USB", "GND", C1210)
    two_pin(s, "Device:C", "C6", "100nF", (70, 132), "+5V_USB", "GND", C0603)

    component(
        s,
        "Regulator_Switching:TPS62132",
        "U4",
        "TPS62132RGTR",
        (105, 112),
        "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias",
    )
    for pin in ("1", "2", "3"):
        net(s, "SW_3V3", "U4", pin)
    net(s, "PG_3V3", "U4", "4")
    net(s, "GND", "U4", "5")
    net(s, "GND", "U4", "6")
    net(s, "GND", "U4", "7")
    net(s, "GND", "U4", "8")
    net(s, "SS_3V3", "U4", "9")
    for pin in ("10", "11", "12", "13"):
        net(s, "+5V_USB", "U4", pin)
    net(s, "+3V3", "U4", "14")
    for pin in ("15", "16", "17"):
        net(s, "GND", "U4", pin)
    two_pin(s, "Device:L", "L1", "2.2uH WPN4020H2R2MT", (130, 107), "SW_3V3", "+3V3", "A3_Control_Center:WPN4020H", rotation=0, Datasheet="https://www.alfatec.de/fileadmin/productfiles/datasheets/sunlord_wpn4020h_series.pdf")
    two_pin(s, "Device:C", "C7", "10uF", (85, 132), "+5V_USB", "GND", C0805)
    two_pin(s, "Device:C", "C8", "100nF", (95, 132), "+5V_USB", "GND", C0603)
    two_pin(s, "Device:C", "C9", "22uF", (105, 132), "+3V3", "GND", C0805)
    two_pin(s, "Device:C", "C10", "100nF", (115, 132), "+3V3", "GND", C0603)
    two_pin(s, "Device:C", "C11", "3.3nF", (125, 132), "SS_3V3", "GND", C0603)
    two_pin(s, "Device:R", "R10", "100k", (135, 132), "+3V3", "PG_3V3", R0603)

    component(s, "a3-control-center:TPS63070", "U5", "TPS63070RNMR", (172, 110), "A3_Control_Center:TI_RNM0015A_VQFN-HR-15")
    net(s, "GND", "U5", "1")
    net(s, "PG_5VFT", "U5", "2")
    net(s, "VAUX_5VFT", "U5", "3")
    net(s, "GND", "U5", "4")
    net(s, "FB_5VFT", "U5", "5")
    nc(s, "U5", "6")
    for pin in ("7", "8"):
        net(s, "+5V_FT", "U5", pin)
    net(s, "L2_5VFT", "U5", "9")
    net(s, "GND", "U5", "10")
    net(s, "L1_5VFT", "U5", "11")
    for pin in ("12", "13"):
        net(s, "+5V_USB", "U5", pin)
    net(s, "EN_5VFT", "U5", "14")
    net(s, "GND", "U5", "15")
    two_pin(s, "Device:L", "L2", "1.5uH XGL4020-152MEC", (172, 142), "L1_5VFT", "L2_5VFT", "Inductor_SMD:L_Coilcraft_XxL4020", rotation=0)
    two_pin(s, "Device:R", "R11", "10k", (145, 132), "+5V_USB", "EN_5VFT", R0603)
    two_pin(s, "Device:R", "R12", "680k 1%", (155, 132), "+5V_FT", "FB_5VFT", R0603)
    two_pin(s, "Device:R", "R13", "130k 1%", (165, 132), "FB_5VFT", "GND", R0603)
    two_pin(s, "Device:R", "R14", "100k", (175, 132), "+3V3", "PG_5VFT", R0603)
    two_pin(s, "Device:C", "C12", "100nF", (185, 132), "VAUX_5VFT", "GND", C0603)
    for i, x in enumerate((195, 205, 215), 13):
        two_pin(s, "Device:C", f"C{i}", "22uF 16V", (x, 132), "+5V_FT", "GND", C0805)
    two_pin(s, "Device:C", "C16", "10uF", (225, 132), "+5V_FT", "GND", C0603)
    two_pin(s, "Device:C", "C17", "10uF", (195, 110), "+5V_USB", "GND", C0805)
    two_pin(s, "Device:C", "C18", "10uF", (205, 110), "+5V_USB", "GND", C0805)
    two_pin(s, "Device:C", "C19", "10uF", (215, 110), "+5V_USB", "GND", C0603)

    power_flag(s, "#FLG01", "VBUS_RAW", (25, 98))
    power_flag(s, "#FLG03", "+3V3", (135, 98))
    power_flag(s, "#FLG05", "GND", (232, 98))
    testpoint(s, "TP1", "VBUS_RAW", (25, 150))
    testpoint(s, "TP2", "+5V_USB", (40, 150))
    testpoint(s, "TP3", "+3V3", (55, 150))
    testpoint(s, "TP4", "+5V_FT", (70, 150))
    testpoint(s, "TP5", "GND", (85, 150))
    testpoint(s, "TP6", "UART0_TX", (100, 150))
    testpoint(s, "TP7", "UART0_RX", (115, 150))
    testpoint(s, "TP8", "USB_PWR_FAULT", (130, 150))

    s.save(HW / "dual_can_esp32_power_usb.kicad_sch")


def build_mcu_ui(parent, sheet_uuid):
    s = new_child(parent, sheet_uuid)
    s.add_text("ESP32-WROOM-32E, PROGRAMMING, DISPLAY AND USER I/O", (105, 18), size=2.0, bold=True)
    component(s, "RF_Module:ESP32-WROOM-32E", "U10", "ESP32-WROOM-32E-N4", (105, 72), "RF_Module:ESP32-WROOM-32E")
    net(s, "+3V3", "U10", "2")
    net(s, "ESP_EN", "U10", "3")
    net(s, "USER_BUTTON", "U10", "4")
    nc(s, "U10", "5")
    net(s, "EXP_GPIO34", "U10", "6")
    net(s, "CAN_FT_ERR", "U10", "7")
    net(s, "CAN_FT_STB", "U10", "8")
    net(s, "CAN_FT_EN", "U10", "9")
    net(s, "VIDEO_DAC", "U10", "10")
    net(s, "DAC2_RESERVED", "U10", "11")
    net(s, "STATUS_LED", "U10", "12")
    net(s, "EXP_GPIO14", "U10", "13")
    nc(s, "U10", "14")
    net(s, "CAN_FT_INT", "U10", "16")
    nc(s, "U10", "17", "18", "19", "20", "21", "22", "23", "24")
    net(s, "ESP_GPIO0", "U10", "25")
    net(s, "CAN_FT_CS", "U10", "26")
    net(s, "CAN_HS_TX", "U10", "27")
    net(s, "CAN_HS_RX", "U10", "28")
    nc(s, "U10", "29")
    net(s, "CAN_FT_SCK", "U10", "30")
    net(s, "CAN_FT_MISO", "U10", "31")
    nc(s, "U10", "32")
    net(s, "OLED_SDA", "U10", "33")
    net(s, "UART0_RX", "U10", "34")
    net(s, "UART0_TX", "U10", "35")
    net(s, "OLED_SCL", "U10", "36")
    net(s, "CAN_FT_MOSI", "U10", "37")
    net(s, "GND", "U10", "[1,15,38,39]")

    two_pin(s, "Device:R", "R20", "10k", (35, 45), "+3V3", "ESP_EN", R0603)
    two_pin(s, "Device:C", "C20", "1uF", (45, 45), "ESP_EN", "GND", C0805)
    component(s, "Switch:SW_Push", "SW1", "RESET / EN", (55, 45), BUTTON)
    net(s, "ESP_EN", "SW1", "1")
    net(s, "GND", "SW1", "2")
    two_pin(s, "Device:R", "R21", "10k", (35, 62), "+3V3", "ESP_GPIO0", R0603)
    component(s, "Switch:SW_Push", "SW2", "BOOT", (55, 62), BUTTON)
    net(s, "ESP_GPIO0", "SW2", "1")
    net(s, "GND", "SW2", "2")

    # The generator does not retain KiCad's inherited-symbol hash for SS8050.
    # Use the equivalent B-E-C base graphic and keep the audited value/package.
    component(s, "Transistor_BJT:Q_NPN_BEC", "Q1", "SS8050", (35, 92), "Package_TO_SOT_SMD:SOT-23", Manufacturer="onsemi", MPN="SS8050")
    component(s, "Transistor_BJT:Q_NPN_BEC", "Q2", "SS8050", (60, 92), "Package_TO_SOT_SMD:SOT-23", Manufacturer="onsemi", MPN="SS8050")
    two_pin(s, "Device:R", "R22", "10k", (25, 108), "USB_DTR", "AUTO_Q1_BASE", R0603, rotation=0)
    two_pin(s, "Device:R", "R23", "10k", (50, 108), "USB_RTS", "AUTO_Q2_BASE", R0603, rotation=0)
    net(s, "AUTO_Q1_BASE", "Q1", "1")
    net(s, "USB_RTS", "Q1", "2")
    net(s, "ESP_EN", "Q1", "3")
    net(s, "AUTO_Q2_BASE", "Q2", "1")
    net(s, "USB_DTR", "Q2", "2")
    net(s, "ESP_GPIO0", "Q2", "3")
    s.add_text("Espressif crossed two-NPN auto-program circuit: simultaneous DTR/RTS assertion leaves EN and GPIO0 high.", (25, 118), size=1.0)

    two_pin(s, "Device:C", "C21", "10uF", (132, 43), "+3V3", "GND", C0805)
    two_pin(s, "Device:C", "C22", "100nF", (142, 43), "+3V3", "GND", C0603)
    two_pin(s, "Device:C", "C23", "100uF low-ESR", (152, 43), "+3V3", "GND", C1210)

    component(s, "Connector_Generic:Conn_01x04", "J10", "B4B-PH-K-S(LF)(SN)", (175, 62), "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical")
    net(s, "+3V3", "J10", "1")
    net(s, "GND", "J10", "2")
    net(s, "OLED_SCL", "J10", "3")
    net(s, "OLED_SDA", "J10", "4")
    two_pin(s, "Device:R", "R24", "4.7k DNP", (175, 85), "+3V3", "OLED_SCL", R0603)
    two_pin(s, "Device:R", "R25", "4.7k DNP", (185, 85), "+3V3", "OLED_SDA", R0603)
    s.add_text("J10 Gravity/PH2.0: 1 +3V3, 2 GND, 3 SCL, 4 SDA. DFR0486 has onboard 10k pull-ups; R24/R25 stay DNP.", (150, 95), size=1.0)

    two_pin(s, "Device:R", "R26", "1k", (175, 112), "STATUS_LED", "STATUS_LED_A", R0603, rotation=0)
    component(s, "Device:LED", "D10", "STATUS GREEN", (200, 112), "LED_SMD:LED_0603_1608Metric", rotation=90)
    net(s, "STATUS_LED_A", "D10", "1")
    net(s, "GND", "D10", "2")
    two_pin(s, "Device:R", "R27", "10k", (175, 128), "+3V3", "USER_BUTTON", R0603)
    component(s, "Switch:SW_Push", "SW3", "USER", (200, 128), BUTTON)
    net(s, "USER_BUTTON", "SW3", "1")
    net(s, "GND", "SW3", "2")

    testpoint(s, "TP10", "ESP_EN", (25, 140))
    testpoint(s, "TP11", "ESP_GPIO0", (40, 140))
    testpoint(s, "TP12", "DAC2_RESERVED", (55, 140))
    testpoint(s, "TP13", "VIDEO_DAC", (70, 140))
    testpoint(s, "TP14", "EXP_GPIO34", (85, 140))
    testpoint(s, "TP15", "EXP_GPIO14", (100, 140))

    s.save(HW / "dual_can_esp32_mcu_ui.kicad_sch")


def build_can_hs(parent, sheet_uuid):
    s = new_child(parent, sheet_uuid)
    s.add_text("CAN_HS — ESP32 TWAI + TCAN332", (95, 18), size=2.0, bold=True)
    s.add_text("ISO 11898-2, up to 1 Mbit/s. Termination is open by default.", (85, 24), size=1.1)
    component(s, "Interface_CAN_LIN:TCAN332", "U20", "TCAN332DR", (85, 65), "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
    net(s, "CAN_HS_TX", "U20", "1")
    net(s, "GND", "U20", "2")
    net(s, "+3V3", "U20", "3")
    net(s, "CAN_HS_RX", "U20", "4")
    nc(s, "U20", "5", "8")
    net(s, "CAN_HS_L_PHY", "U20", "6")
    net(s, "CAN_HS_H_PHY", "U20", "7")
    two_pin(s, "Device:C", "C30", "100nF", (85, 92), "+3V3", "GND", C0603)
    two_pin(s, "Device:C", "C31", "1uF", (97, 92), "+3V3", "GND", C0805)

    # Default-fit bypasses. Their four pads reserve the series position where
    # a validated two-line common-mode choke may replace both links later.
    two_pin(s, "Device:R", "R30", "0R (CMC bypass)", (125, 58), "CAN_HS_H_PHY", "CAN_HS_H", R0603, rotation=0)
    two_pin(s, "Device:R", "R31", "0R (CMC bypass)", (125, 72), "CAN_HS_L_PHY", "CAN_HS_L", R0603, rotation=0)

    component(s, "a3-control-center:PESD2CAN24T_Q", "D20", "PESD2CAN24T-Q", (160, 65), "Package_TO_SOT_SMD:SOT-23")
    net(s, "CAN_HS_H", "D20", "1")
    net(s, "CAN_HS_L", "D20", "2")
    net(s, "GND", "D20", "3")

    component(s, "Jumper:SolderJumper_2_Open", "JP20", "CAN_HS TERM ENABLE", (155, 100), "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm")
    net(s, "CAN_HS_H", "JP20", "1")
    net(s, "CAN_HS_TERM", "JP20", "2")
    two_pin(s, "Device:R", "R32", "120R 1%", (180, 100), "CAN_HS_TERM", "CAN_HS_L", R0603, rotation=0)
    s.add_text("JP20: bridge only when this board is at a physical bus end.", (160, 112), size=1.0)

    component(s, "Connector_Generic:Conn_01x03", "J20", "1715734", (205, 65), "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal")
    net(s, "CAN_HS_H", "J20", "1")
    net(s, "CAN_HS_L", "J20", "2")
    net(s, "GND", "J20", "3")
    s.add_text("J20: 1 CANH, 2 CANL, 3 GND", (205, 82), size=1.0)
    testpoint(s, "TP20", "CAN_HS_H", (120, 130))
    testpoint(s, "TP21", "CAN_HS_L", (145, 130))
    s.save(HW / "dual_can_esp32_can_hs.kicad_sch")


def build_can_ft(parent, sheet_uuid):
    s = new_child(parent, sheet_uuid)
    s.add_text("CAN_FT — MCP2515 + TJA1055T/3", (100, 18), size=2.0, bold=True)
    s.add_text(
        "ISO 11898-3, up to 125 kbit/s. JP40/JP41 are open by default; fit both together only after network termination review.",
        (72, 24),
        size=1.0,
    )

    component(
        s,
        "Interface_CAN_LIN:MCP2515-xSO",
        "U40",
        "MCP2515T-I/SO",
        (62, 72),
        "Package_SO:SOIC-18W_7.5x11.6mm_P1.27mm",
        Manufacturer="Microchip",
        MPN="MCP2515T-I/SO",
    )
    net(s, "MCP_TXCAN", "U40", "1")
    net(s, "MCP_RXCAN", "U40", "2")
    nc(s, "U40", "3", "4", "5", "6", "10", "11")
    net(s, "MCP_OSC2", "U40", "7")
    net(s, "MCP_OSC1", "U40", "8")
    net(s, "GND", "U40", "9")
    net(s, "CAN_FT_INT", "U40", "12")
    net(s, "CAN_FT_SCK", "U40", "13")
    net(s, "CAN_FT_MOSI", "U40", "14")
    net(s, "CAN_FT_MISO", "U40", "15")
    net(s, "CAN_FT_CS", "U40", "16")
    net(s, "MCP_RESET_N", "U40", "17")
    net(s, "+3V3", "U40", "18")
    two_pin(s, "Device:C", "C40", "100nF", (35, 105), "+3V3", "GND", C0603)
    two_pin(s, "Device:C", "C41", "1uF", (45, 105), "+3V3", "GND", C0805)
    two_pin(s, "Device:R", "R40", "10k", (55, 105), "+3V3", "MCP_RESET_N", R0603)
    two_pin(s, "Device:C", "C42", "100nF", (65, 105), "MCP_RESET_N", "GND", C0603)
    two_pin(s, "Device:R", "R41", "10k", (75, 105), "+3V3", "CAN_FT_INT", R0603)
    two_pin(s, "Device:R", "R50", "10k", (85, 105), "+3V3", "CAN_FT_CS", R0603)

    component(
        s,
        "a3-control-center:Crystal_4Pad_13_GND24",
        "Y40",
        "ABM3BAIG-16.000MHZ-12-2-T",
        (62, 130),
        "Crystal:Crystal_SMD_5032-4Pin_5.0x3.2mm",
        Manufacturer="Abracon",
        MPN="ABM3BAIG-16.000MHZ-12-2-T",
    )
    net(s, "MCP_OSC1", "Y40", "1")
    net(s, "GND", "Y40", "2")
    net(s, "MCP_OSC2", "Y40", "3")
    net(s, "GND", "Y40", "4")
    two_pin(s, "Device:C", "C43", "18pF C0G", (45, 148), "MCP_OSC1", "GND", C0603)
    two_pin(s, "Device:C", "C44", "18pF C0G", (75, 148), "MCP_OSC2", "GND", C0603)
    s.add_text("Y40 CL=12 pF; 18 pF loads assume about 3 pF total stray. Validate frequency/startup on assembled PCB.", (35, 158), size=0.9)

    component(
        s,
        "a3-control-center:TJA1055T_3",
        "U41",
        "TJA1055T/3/2Z",
        (132, 72),
        "Package_SO:SO-14_3.9x8.65mm_P1.27mm",
        Manufacturer="NXP",
        MPN="TJA1055T/3/2Z",
    )
    nc(s, "U41", "1")
    net(s, "MCP_TXCAN", "U41", "2")
    net(s, "MCP_RXCAN", "U41", "3")
    net(s, "CAN_FT_ERR", "U41", "4")
    net(s, "CAN_FT_STB", "U41", "5")
    net(s, "CAN_FT_EN", "U41", "6")
    net(s, "+5V_FT", "U41", "7")
    net(s, "TJA_RTH", "U41", "8")
    net(s, "TJA_RTL", "U41", "9")
    net(s, "+5V_FT", "U41", "10")
    net(s, "CAN_FT_H_PHY", "U41", "11")
    net(s, "CAN_FT_L_PHY", "U41", "12")
    net(s, "GND", "U41", "13")
    net(s, "+5V_FT", "U41", "14")
    two_pin(s, "Device:R", "R42", "10k", (103, 108), "+3V3", "MCP_RXCAN", R0603)
    two_pin(s, "Device:R", "R43", "10k", (113, 108), "+3V3", "CAN_FT_ERR", R0603)
    two_pin(s, "Device:R", "R44", "10k", (123, 108), "CAN_FT_STB", "GND", R0603)
    two_pin(s, "Device:R", "R45", "10k", (133, 108), "CAN_FT_EN", "GND", R0603)
    two_pin(s, "Device:C", "C45", "100nF", (143, 108), "+5V_FT", "GND", C0603)
    two_pin(s, "Device:C", "C46", "1uF", (153, 108), "+5V_FT", "GND", C0805)
    s.add_text("R44/R45 force STB=0, EN=0 (non-driving standby) during ESP32 reset; firmware sets both high for normal mode.", (96, 120), size=0.9)

    # Default-fit series links preserve optional common-mode choke positions.
    two_pin(s, "Device:R", "R46", "0R (CMC bypass)", (172, 60), "CAN_FT_H_PHY", "CAN_FT_H", R0603, rotation=0)
    two_pin(s, "Device:R", "R47", "0R (CMC bypass)", (172, 74), "CAN_FT_L_PHY", "CAN_FT_L", R0603, rotation=0)

    # ISO 11898-3 distributed termination: separate matched resistor from each
    # bus wire to its transceiver bias pin. This is never a 120 ohm line-to-line
    # termination. Jumpers are both open by default pending vehicle topology.
    two_pin(s, "Device:R", "R48", "1.2k 1% CONFIG", (155, 133), "TJA_RTH", "FT_TERM_H", R0603, rotation=0)
    component(s, "Jumper:SolderJumper_2_Open", "JP40", "CAN_FT RTH ENABLE", (190, 133), "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm")
    net(s, "FT_TERM_H", "JP40", "1")
    net(s, "CAN_FT_H", "JP40", "2")
    two_pin(s, "Device:R", "R49", "1.2k 1% CONFIG", (155, 147), "TJA_RTL", "FT_TERM_L", R0603, rotation=0)
    component(s, "Jumper:SolderJumper_2_Open", "JP41", "CAN_FT RTL ENABLE", (190, 147), "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm")
    net(s, "FT_TERM_L", "JP41", "1")
    net(s, "CAN_FT_L", "JP41", "2")

    component(s, "a3-control-center:PESD2CAN24T_Q", "D40", "PESD2CAN24T-Q", (205, 67), "Package_TO_SOT_SMD:SOT-23")
    net(s, "CAN_FT_H", "D40", "1")
    net(s, "CAN_FT_L", "D40", "2")
    net(s, "GND", "D40", "3")
    component(s, "Connector_Generic:Conn_01x03", "J40", "1715734", (235, 67), "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal")
    net(s, "CAN_FT_H", "J40", "1")
    net(s, "CAN_FT_L", "J40", "2")
    net(s, "GND", "J40", "3")
    s.add_text("J40: 1 CANH, 2 CANL, 3 GND", (224, 87), size=1.0)
    testpoint(s, "TP40", "CAN_FT_H", (205, 105))
    testpoint(s, "TP41", "CAN_FT_L", (225, 105))
    s.save(HW / "dual_can_esp32_can_ft.kicad_sch")


def build_video(parent, sheet_uuid):
    s = new_child(parent, sheet_uuid)
    s.add_text("COMPOSITE VIDEO — GPIO25 DAC + THS7314", (100, 18), size=2.0, bold=True)
    s.add_text(
        "Default: 0.1 uF AC input clamp, THS7314 CH1, 75 ohm source, DC output. Bench-calibrate DAC levels before freeze.",
        (65, 24),
        size=1.0,
    )

    two_pin(s, "Device:R", "R60", "33R", (45, 62), "VIDEO_DAC", "VIDEO_DAC_SER", R0603, rotation=0)
    two_pin(s, "Device:C", "C60", "100nF X7R FIT", (70, 62), "VIDEO_DAC_SER", "VIDEO_IN", C0805, rotation=0)
    two_pin(s, "Device:R", "R61", "0R DNP (DC INPUT)", (70, 78), "VIDEO_DAC_SER", "VIDEO_IN", R0603, rotation=0)

    component(
        s,
        "a3-control-center:THS7314",
        "U60",
        "THS7314DR",
        (112, 67),
        "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        Manufacturer="Texas Instruments",
        MPN="THS7314DR",
    )
    net(s, "VIDEO_IN", "U60", "1")
    net(s, "GND", "U60", "2")
    net(s, "GND", "U60", "3")
    net(s, "+3V3", "U60", "4")
    net(s, "GND", "U60", "5")
    nc(s, "U60", "6", "7")
    net(s, "VIDEO_BUF_OUT", "U60", "8")
    two_pin(s, "Device:C", "C61", "100nF", (102, 98), "+3V3", "GND", C0603)
    two_pin(s, "Device:C", "C62", "1uF", (115, 98), "+3V3", "GND", C0805)
    s.add_text("Unused CH2/CH3 inputs tied to GND; outputs left NC.", (92, 108), size=0.9)

    two_pin(s, "Device:R", "R62", "75R 1%", (150, 62), "VIDEO_BUF_OUT", "VIDEO_SRC", R0603, rotation=0)
    component(s, "Jumper:SolderJumper_2_Bridged", "JP60", "BUFFERED DC FIT", (178, 62), "Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm")
    net(s, "VIDEO_SRC", "JP60", "1")
    net(s, "VIDEO_RCA", "JP60", "2")

    two_pin(s, "Device:C_Polarized", "C63", "470uF 6.3V EEEFK0J471GP DNP", (160, 83), "VIDEO_SRC", "VIDEO_AC_OPTION", "Capacitor_SMD:CP_Elec_8x10", rotation=0)
    component(s, "Jumper:SolderJumper_2_Open", "JP61", "OUTPUT AC DNP", (195, 83), "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm")
    net(s, "VIDEO_AC_OPTION", "JP61", "1")
    net(s, "VIDEO_RCA", "JP61", "2")

    two_pin(s, "Device:R", "R63", "TBD DNP (PASSIVE)", (115, 130), "VIDEO_DAC", "VIDEO_PASSIVE", R0603, rotation=0)
    component(s, "Jumper:SolderJumper_2_Open", "JP62", "PASSIVE DNP", (150, 130), "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm")
    net(s, "VIDEO_PASSIVE", "JP62", "1")
    net(s, "VIDEO_RCA", "JP62", "2")
    s.add_text("Interlock: only one of JP60, JP61, or JP62 may be closed. JP60 is the assembly default.", (105, 143), size=1.0)

    component(
        s,
        "Device:D_TVS",
        "D60",
        "HPESD5V0U1BA-Q",
        (215, 105),
        "Diode_SMD:D_SOD-323",
        Manufacturer="Nexperia",
        MPN="HPESD5V0U1BA-Q",
    )
    net(s, "VIDEO_RCA", "D60", "1")
    net(s, "GND", "D60", "2")
    component(s, "Connector_Generic:Conn_01x02", "J60", "RCJ-014", (235, 67), "A3_Control_Center:RCJ-014", Datasheet="https://www.sameskydevices.com/product/resource/rcj-01.pdf")
    net(s, "GND", "J60", "1")
    net(s, "VIDEO_RCA", "J60", "2")
    s.add_text("J60 RCJ-014: manufacturer pin 1 = shell/VIDEO_GND; pin 2 = center/VIDEO_OUT.", (190, 32), size=0.9)
    testpoint(s, "TP60", "VIDEO_DAC", (45, 155))
    testpoint(s, "TP61", "VIDEO_BUF_OUT", (75, 155))
    testpoint(s, "TP62", "VIDEO_RCA", (105, 155))
    s.save(HW / "dual_can_esp32_video.kicad_sch")


def build_placeholder(parent, sheet_uuid, filename, title, note):
    s = new_child(parent, sheet_uuid)
    s.add_text(title, (25, 20), size=2.0, bold=True)
    s.add_text(note, (25, 28), size=1.2)
    s.add_text("Capture gate: populate only after the relevant primary-datasheet circuit and package audit is recorded.", (25, 36), size=1.0)
    s.save(HW / filename)


def main():
    root = ksa.create_schematic(PROJECT)
    root.add_text("A3 CONTROL CENTER — ESP32 DUAL-CAN / OLED / COMPOSITE VIDEO", (115, 18), size=2.2, bold=True)
    root.add_text("Revision A schematic capture — reviewed hierarchical nets connect the functional sheets.", (110, 24), size=1.1)

    sheets = [
        ("USB + Power", "dual_can_esp32_power_usb.kicad_sch", (25, 38), (75, 35), "2"),
        ("ESP32 + UI", "dual_can_esp32_mcu_ui.kicad_sch", (115, 38), (75, 35), "3"),
        ("CAN_HS", "dual_can_esp32_can_hs.kicad_sch", (25, 90), (75, 35), "4"),
        ("CAN_FT", "dual_can_esp32_can_ft.kicad_sch", (115, 90), (75, 35), "5"),
        ("Composite Video", "dual_can_esp32_video.kicad_sch", (205, 90), (75, 35), "6"),
    ]
    ids = {}
    for name, filename, pos, size, page in sheets:
        ids[name] = root.add_sheet(name, filename, pos, size, project_name=PROJECT, page_number=page)

    sheet_nets = {
        "USB + Power": ["+3V3", "+5V_FT", "GND", "UART0_TX", "UART0_RX", "USB_RTS", "USB_DTR"],
        "ESP32 + UI": [
            "+3V3", "GND", "UART0_TX", "UART0_RX", "USB_RTS", "USB_DTR",
            "CAN_HS_TX", "CAN_HS_RX", "CAN_FT_MOSI", "CAN_FT_MISO",
            "CAN_FT_SCK", "CAN_FT_CS", "CAN_FT_INT", "CAN_FT_STB",
            "CAN_FT_EN", "CAN_FT_ERR", "VIDEO_DAC",
        ],
        "CAN_HS": ["+3V3", "GND", "CAN_HS_TX", "CAN_HS_RX"],
        "CAN_FT": [
            "+3V3", "+5V_FT", "GND", "CAN_FT_MOSI", "CAN_FT_MISO",
            "CAN_FT_SCK", "CAN_FT_CS", "CAN_FT_INT", "CAN_FT_STB",
            "CAN_FT_EN", "CAN_FT_ERR",
        ],
        "Composite Video": ["+3V3", "GND", "VIDEO_DAC"],
    }
    sheet_lookup = {name: (pos, size) for name, _filename, pos, size, _page in sheets}
    for sheet_name, names in sheet_nets.items():
        (sx, sy), (sw, _sh) = sheet_lookup[sheet_name]
        for index, signal in enumerate(names):
            along = 5.0 + index * min(4.0, (sw - 10.0) / max(1, len(names) - 1))
            root.add_sheet_pin(ids[sheet_name], signal, "passive", "top", along)
            root.add_label(signal, position=(sx + along, sy))

    build_power_usb(root, ids["USB + Power"])
    build_mcu_ui(root, ids["ESP32 + UI"])
    build_can_hs(root, ids["CAN_HS"])
    build_can_ft(root, ids["CAN_FT"])
    build_video(root, ids["Composite Video"])
    root.save(HW / "dual_can_esp32.kicad_sch")

    # kicad-sch-api currently serializes the KiCad 9 schematic grammar. KiCad
    # 10 can read it, but repairs and rewrites embedded symbol data on opening.
    # Normalize every generated sheet immediately so the checked-in hierarchy
    # opens without the "automatically fixed" warning on the project version.
    for schematic in sorted(HW.glob(f"{PROJECT}*.kicad_sch")):
        subprocess.run(
            [str(KICAD_CLI), "sch", "upgrade", "--force", str(schematic)],
            check=True,
        )


if __name__ == "__main__":
    main()
