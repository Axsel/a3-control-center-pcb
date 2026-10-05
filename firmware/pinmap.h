#pragma once

/* ESP32-WROOM-32E-N4 hardware contract; keep synchronized with docs/pinout.md. */

#define PIN_UART0_TX          1
#define PIN_UART0_RX          3
#define PIN_BOOT              0

#define PIN_CAN_HS_TX        16
#define PIN_CAN_HS_RX        17

#define PIN_CAN_FT_SCK       18
#define PIN_CAN_FT_MISO      19
#define PIN_CAN_FT_MOSI      23
#define PIN_CAN_FT_CS         4
#define PIN_CAN_FT_INT       13
#define PIN_CAN_FT_STB       32
#define PIN_CAN_FT_EN        33
#define PIN_CAN_FT_ERR       35

#define PIN_OLED_SDA         21
#define PIN_OLED_SCL         22

#define PIN_VIDEO_DAC        25
#define PIN_DAC2_RESERVED    26

#define PIN_STATUS_LED       27
#define PIN_USER_BUTTON      36
#define PIN_EXP_GPIO34       34
#define PIN_EXP_GPIO14       14

#define MCP2515_OSC_HZ 16000000UL
#define CAN_FT_MAX_BITRATE 125000UL
