/*
 * Lab demo: slow LEDC "breathe" on ESP32-DevKitC class boards.
 *
 * Hardware honesty (Espressif DevKitC):
 *   - One user LED on GPIO2 (often blue).
 *   - Board power LED (often red) is NOT GPIO-controllable.
 *   - No second documented user LED pin without external wiring.
 *
 * Captain asked blue OFF + red PWM. With only GPIO2 available, this fixture
 * runs slow PWM glow on GPIO2 (the single user LED) and logs that limitation.
 * If a future clone documents a separate red GPIO, set GLOW_GPIO and leave
 * GPIO2 driven low as BLUE_HOLD_OFF_GPIO.
 */
#include <math.h>
#include <stdio.h>
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* Single documented user LED on stock DevKitC. */
#define GLOW_GPIO 2
/* No separate blue to force off when glow shares GPIO2 (-1 = unused). */
#define BLUE_HOLD_OFF_GPIO (-1)

#define LEDC_MODE LEDC_LOW_SPEED_MODE
#define LEDC_TIMER LEDC_TIMER_0
#define LEDC_CHANNEL LEDC_CHANNEL_0
#define LEDC_DUTY_RES LEDC_TIMER_13_BIT
#define LEDC_FREQ_HZ 5000
#define DUTY_MAX ((1 << 13) - 1)

/* Full breathe cycle ~3 s. */
#define CYCLE_MS 3000
#define STEP_MS 20

static void glow_set_duty(uint32_t duty)
{
    ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, duty);
    ledc_update_duty(LEDC_MODE, LEDC_CHANNEL);
}

void app_main(void)
{
#if BLUE_HOLD_OFF_GPIO >= 0
    gpio_config_t off = {
        .pin_bit_mask = 1ULL << BLUE_HOLD_OFF_GPIO,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&off);
    gpio_set_level(BLUE_HOLD_OFF_GPIO, 0);
#endif

    ledc_timer_config_t timer = {
        .speed_mode = LEDC_MODE,
        .duty_resolution = LEDC_DUTY_RES,
        .timer_num = LEDC_TIMER,
        .freq_hz = LEDC_FREQ_HZ,
        .clk_cfg = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&timer));

    ledc_channel_config_t ch = {
        .speed_mode = LEDC_MODE,
        .channel = LEDC_CHANNEL,
        .timer_sel = LEDC_TIMER,
        .intr_type = LEDC_INTR_DISABLE,
        .gpio_num = GLOW_GPIO,
        .duty = 0,
        .hpoint = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ch));

    vTaskDelay(pdMS_TO_TICKS(300));
    printf("PODLESP_GLOW boot glow_gpio=%d blue_hold_off=%d cycle_ms=%d "
           "note=stock_DevKitC_single_user_LED_GPIO2_power_red_not_GPIO\n",
           GLOW_GPIO, BLUE_HOLD_OFF_GPIO, CYCLE_MS);
    fflush(stdout);

    unsigned tick = 0;
    const int steps = CYCLE_MS / STEP_MS;
    for (;;) {
        for (int i = 0; i < steps; i++) {
            /* Triangle-ish via half-sine for smooth ends. */
            float phase = (float)i / (float)steps; /* 0..1 */
            float s = sinf(phase * 3.14159265f);   /* 0..1..0 */
            if (s < 0) {
                s = 0;
            }
            uint32_t duty = (uint32_t)(s * s * (float)DUTY_MAX); /* gamma-ish */
            glow_set_duty(duty);
            vTaskDelay(pdMS_TO_TICKS(STEP_MS));
        }
        printf("PODLESP_GLOW_TICK n=%u\n", tick);
        fflush(stdout);
        tick++;
    }
}
