#include <stdio.h>
#include <stdint.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

#include "esp_adc/adc_oneshot.h"
#include "esp_rom_sys.h"

#define USE_GPIO36_VP     1   

#define PERIOD_MS         10

#define SAMPLES_AVG       16

#define BASELINE_CONST    1530

#define ADC_ATTEN         ADC_ATTEN_DB_12
#define ADC_WIDTH         ADC_BITWIDTH_12

#if USE_GPIO36_VP
  #define ADC_CH ADC_CHANNEL_0
#else
  #define ADC_CH ADC_CHANNEL_3
#endif

static adc_oneshot_unit_handle_t adc1_handle;

static int32_t read_adc_avg_raw(int n)
{
    int64_t sum = 0;
    for (int i = 0; i < n; i++) {
        int raw = 0;
        adc_oneshot_read(adc1_handle, ADC_CH, &raw);
        sum += raw;
        esp_rom_delay_us(80);
    }
    return (int32_t)(sum / n);
}

void app_main(void)
{
    esp_log_level_set("*", ESP_LOG_NONE);
    setvbuf(stdout, NULL, _IONBF, 0);

    adc_oneshot_unit_init_cfg_t unit_cfg = {
        .unit_id = ADC_UNIT_1,
        .ulp_mode = ADC_ULP_MODE_DISABLE,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit_cfg, &adc1_handle));

    adc_oneshot_chan_cfg_t chan_cfg = {
        .atten = ADC_ATTEN,
        .bitwidth = ADC_WIDTH,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, ADC_CH, &chan_cfg));

    TickType_t last_wake = xTaskGetTickCount();

    while (1) {
        int64_t t_us = esp_timer_get_time();

        int32_t raw = read_adc_avg_raw(SAMPLES_AVG);

        int32_t level = raw - BASELINE_CONST;
        if (level < 0) level = 0;

        printf("%lld,%ld,%ld\n",
               (long long)t_us,
               (long)raw,
               (long)level);

        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(PERIOD_MS));
    }
}
