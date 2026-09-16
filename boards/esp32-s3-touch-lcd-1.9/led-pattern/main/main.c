/*
 * Lab demo: onboard LED pattern for ESP32-S3-Touch-LCD-1.9 class boards.
 *
 * Pin evidence (vendor demo, not physical unit confirmation):
 *   Waveshare ESP32-S3-LCD-1.9 ESP-IDF 04_WS2812_Test:
 *     LEDS_PIN = 15, LEDS_COUNT = 2, model WS2812 (GRB).
 *   Product docs also say WS2812 is "on the back, non-touch version only".
 *   Touch units may lack the strip; if nothing lights, stop and re-confirm pin/SKU.
 *
 * Pattern:
 *   - Default: 1 Hz blink (brief ON once per second).
 *   - Every 10 s: 2000 Hz on/off burst for 250 ms (period 0.5 ms), then resume 1 Hz.
 *
 * Console: USB Serial/JTAG (same as smoke fixture).
 */
#include <inttypes.h>
#include <stdio.h>
#include <string.h>

#include "driver/gpio.h"
#include "esp_cpu.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

/* Vendor demo pin; override at build only with evidence. */
#define WS2812_GPIO 15
#define WS2812_COUNT 2

#define BASE_HZ 1
#define BURST_HZ 2000
#define BURST_MS 250
#define BURST_EVERY_S 10

/* Brief ON window during 1 Hz cycle (ms). */
#define BASE_ON_MS 80

/* Brightness 0-255 for "on" (keep modest for eye safety). */
#define ON_R 0
#define ON_G 40
#define ON_B 0

static inline uint32_t cyc(void)
{
    return esp_cpu_get_cycle_count();
}

/* Rough cycle burn for WS2812 bit timing at CPU freq. */
static void delay_cycles(uint32_t n)
{
    uint32_t start = cyc();
    while ((cyc() - start) < n) {
    }
}

/*
 * Bit-bang one WS2812 bit. At 240 MHz, T0H~0.4us≈96c, T1H~0.8us≈192c,
 * slot ~1.25us≈300c. Numbers are approximate; strip still accepts them on S3.
 * ponytail: fixed cycle counts, retune if strip misbehaves on silicon/clock.
 */
static void ws_bit(int one)
{
    const uint32_t t1h = 192;
    const uint32_t t0h = 96;
    const uint32_t slot = 300;
    uint32_t high = one ? t1h : t0h;
    gpio_set_level(WS2812_GPIO, 1);
    delay_cycles(high);
    gpio_set_level(WS2812_GPIO, 0);
    delay_cycles(slot - high);
}

static void ws_byte(uint8_t b)
{
    for (int i = 7; i >= 0; i--) {
        ws_bit((b >> i) & 1);
    }
}

static void ws_pixel_grb(uint8_t g, uint8_t r, uint8_t b)
{
    ws_byte(g);
    ws_byte(r);
    ws_byte(b);
}

static void ws_show(uint8_t g, uint8_t r, uint8_t b)
{
    portDISABLE_INTERRUPTS();
    for (int i = 0; i < WS2812_COUNT; i++) {
        ws_pixel_grb(g, r, b);
    }
    portENABLE_INTERRUPTS();
    /* reset >50us */
    esp_rom_delay_us(80);
}

static void led_on(void)
{
    ws_show(ON_G, ON_R, ON_B);
}

static void led_off(void)
{
    ws_show(0, 0, 0);
}

static void run_burst_2khz(void)
{
    /* 2000 Hz toggle => 250 us half-period; full period 500 us. */
    const int half_us = 1000000 / (BURST_HZ * 2);
    const int cycles = (BURST_MS * 1000) / (half_us * 2);
    printf("PODLESP_LED_BURST start hz=%d ms=%d cycles=%d\n", BURST_HZ, BURST_MS, cycles);
    fflush(stdout);
    for (int i = 0; i < cycles; i++) {
        led_on();
        esp_rom_delay_us(half_us);
        led_off();
        esp_rom_delay_us(half_us);
    }
    printf("PODLESP_LED_BURST end\n");
    fflush(stdout);
}

void app_main(void)
{
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << WS2812_GPIO,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io);
    gpio_set_level(WS2812_GPIO, 0);

    vTaskDelay(pdMS_TO_TICKS(2000));
    printf("PODLESP_LED_PATTERN boot gpio=%d count=%d base_hz=%d burst=%dHz/%dms every %ds\n",
           WS2812_GPIO, WS2812_COUNT, BASE_HZ, BURST_HZ, BURST_MS, BURST_EVERY_S);
    printf("PODLESP_LED_PIN_SRC waveshare ESP32-S3-LCD-1.9 04_WS2812_Test LEDS_PIN=15 "
           "(touch variant may omit WS2812)\n");
    fflush(stdout);

    led_off();
    int sec = 0;
    for (;;) {
        if (sec > 0 && (sec % BURST_EVERY_S) == 0) {
            run_burst_2khz();
        } else {
            led_on();
            vTaskDelay(pdMS_TO_TICKS(BASE_ON_MS));
            led_off();
            vTaskDelay(pdMS_TO_TICKS(1000 - BASE_ON_MS));
            printf("PODLESP_LED_TICK sec=%d\n", sec);
            fflush(stdout);
        }
        sec++;
    }
}
