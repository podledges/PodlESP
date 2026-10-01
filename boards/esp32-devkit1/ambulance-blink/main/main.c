/*
 * Lab demo: ambulance-style blink for ESP32-DevKitC class boards.
 *
 * Onboard LED: GPIO2 is the common Espressif DevKitC *blue* user LED
 * (active-high on most modules). This board class typically has ONE user LED.
 * Red/blue dual colors need external LEDs — optional second pin via
 * CONFIG or compile-time PODLESP_LED_B if defined; default unused.
 *
 * Pattern (one LED): emergency double-flash groups ~4 Hz burst feel:
 *   ON 80ms, OFF 80ms, ON 80ms, OFF 280ms  (repeat)
 * If LED_B_GPIO >= 0: alternate A vs B every half-cycle (~300 ms each).
 *
 * Console: UART0 @ 115200 (CP2102 bridge).
 */
#include <stdio.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* Espressif ESP32-DevKitC user LED (blue). Do not invent other pins. */
#define LED_A_GPIO 2
/* No second onboard LED documented for stock DevKitC — keep disabled. */
#define LED_B_GPIO (-1)

#define ON_MS 80
#define GAP_MS 80
#define GROUP_OFF_MS 280

static void led_set(int gpio, int on)
{
    if (gpio < 0) {
        return;
    }
    gpio_set_level((gpio_num_t)gpio, on ? 1 : 0);
}

static void pulse_a(void)
{
    led_set(LED_A_GPIO, 1);
    vTaskDelay(pdMS_TO_TICKS(ON_MS));
    led_set(LED_A_GPIO, 0);
    vTaskDelay(pdMS_TO_TICKS(GAP_MS));
    led_set(LED_A_GPIO, 1);
    vTaskDelay(pdMS_TO_TICKS(ON_MS));
    led_set(LED_A_GPIO, 0);
    vTaskDelay(pdMS_TO_TICKS(GROUP_OFF_MS));
}

static void pulse_b(void)
{
    led_set(LED_B_GPIO, 1);
    vTaskDelay(pdMS_TO_TICKS(ON_MS));
    led_set(LED_B_GPIO, 0);
    vTaskDelay(pdMS_TO_TICKS(GAP_MS));
    led_set(LED_B_GPIO, 1);
    vTaskDelay(pdMS_TO_TICKS(ON_MS));
    led_set(LED_B_GPIO, 0);
    vTaskDelay(pdMS_TO_TICKS(GROUP_OFF_MS));
}

void app_main(void)
{
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << LED_A_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
#if LED_B_GPIO >= 0
    io.pin_bit_mask |= (1ULL << LED_B_GPIO);
#endif
    gpio_config(&io);
    led_set(LED_A_GPIO, 0);
    led_set(LED_B_GPIO, 0);

    vTaskDelay(pdMS_TO_TICKS(500));
    printf("PODLESP_AMBULANCE boot led_a=%d led_b=%d pattern=double-flash "
           "on=%d gap=%d group_off=%d (DevKitC single blue LED; dual needs external)\n",
           LED_A_GPIO, LED_B_GPIO, ON_MS, GAP_MS, GROUP_OFF_MS);
    fflush(stdout);

    unsigned tick = 0;
    for (;;) {
        if (LED_B_GPIO >= 0) {
            if ((tick % 2) == 0) {
                pulse_a();
            } else {
                pulse_b();
            }
        } else {
            pulse_a();
        }
        printf("PODLESP_AMBULANCE_TICK n=%u\n", tick);
        fflush(stdout);
        tick++;
    }
}
