#include <inttypes.h>
#include <stdio.h>

#include "esp_chip_info.h"
#include "esp_random.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void app_main(void)
{
    esp_chip_info_t chip_info;
    esp_chip_info(&chip_info);

    /* Let the USB Serial/JTAG endpoint return after esptool's hard reset. */
    vTaskDelay(pdMS_TO_TICKS(2000));

    const uint64_t nonce = ((uint64_t)esp_random() << 32) | esp_random();
    printf("PODLESP_BOOT %016" PRIx64 "\n", nonce);

    if (chip_info.model != CHIP_ESP32S3 || chip_info.cores < 1) {
        printf("PODLESP_SELF_TEST_FAIL %016" PRIx64 "\n", nonce);
    } else {
        printf("PODLESP_SELF_TEST_PASS %016" PRIx64 "\n", nonce);
    }
    fflush(stdout);

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
