#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"
#include "video.h"

#include "pinmap.h"

#define FRAME_WIDTH  320U
#define FRAME_HEIGHT 200U

_Static_assert(PIN_VIDEO_DAC == 25,
               "The audited video library always drives DAC1/GPIO25");

static const char *TAG = "a3_video_bench";

static void fill_pattern(uint8_t *frame)
{
#if CONFIG_A3_VIDEO_PATTERN_BLACK
    memset(frame, 0x00, FRAME_WIDTH * FRAME_HEIGHT);
    ESP_LOGI(TAG, "pattern=black");
#elif CONFIG_A3_VIDEO_PATTERN_WHITE
    memset(frame, 0xff, FRAME_WIDTH * FRAME_HEIGHT);
    ESP_LOGI(TAG, "pattern=white");
#elif CONFIG_A3_VIDEO_PATTERN_CHECKER
    for (unsigned y = 0; y < FRAME_HEIGHT; ++y) {
        for (unsigned x = 0; x < FRAME_WIDTH; ++x) {
            frame[y * FRAME_WIDTH + x] = (((x / 20U) ^ (y / 20U)) & 1U)
                                               ? 0xff
                                               : 0x00;
        }
    }
    ESP_LOGI(TAG, "pattern=checkerboard 20px");
#else
    for (unsigned y = 0; y < FRAME_HEIGHT; ++y) {
        for (unsigned x = 0; x < FRAME_WIDTH; ++x) {
            frame[y * FRAME_WIDTH + x] = (uint8_t)((x / 40U) * 255U / 7U);
        }
    }
    ESP_LOGI(TAG, "pattern=eight-step grayscale bars");
#endif
}

void app_main(void)
{
    ESP_LOGI(TAG, "A3 composite-video bench build");
    ESP_LOGI(TAG, "fixed output=DAC1/GPIO%d, I2S0 DMA, 8bpp framebuffer",
             PIN_VIDEO_DAC);

#if CONFIG_A3_VIDEO_STANDARD_NTSC
    ESP_LOGI(TAG, "standard=NTSC, mode=320x200, nominal line=63.55us");
    video_graphics(NTSC_320x200, FB_FORMAT_GREY_8BPP);
#else
    ESP_LOGI(TAG, "standard=PAL, mode=320x200, nominal line=64us");
    video_graphics(PAL_320x200, FB_FORMAT_GREY_8BPP);
#endif

    uint8_t *frame = video_get_frame_buffer_address();
    if (frame == NULL) {
        ESP_LOGE(TAG, "video framebuffer allocation failed");
        abort();
    }
    fill_pattern(frame);

    ESP_LOGI(TAG, "output running; leave firmware idle while measuring");
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
