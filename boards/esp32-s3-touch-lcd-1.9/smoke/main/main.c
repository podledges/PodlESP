#include "esp_chip_info.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "podlesp-smoke";

void app_main(void)
{
    esp_chip_info_t chip_info;
    esp_chip_info(&chip_info);
    ESP_LOGI(TAG, "build smoke: %d CPU core(s)", chip_info.cores);

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
