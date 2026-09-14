# ESP32-S3 ADC-capable GPIOs

This page records the **ESP32-S3 chip's ADC channel map**. The chip has two SAR
ADC units and 20 analog-enabled GPIOs. It is not a board wiring or connector
map.

## Channel map

### ADC1

| Channel | GPIO |
| --- | --- |
| ADC1_CH0 | GPIO1 |
| ADC1_CH1 | GPIO2 |
| ADC1_CH2 | GPIO3 |
| ADC1_CH3 | GPIO4 |
| ADC1_CH4 | GPIO5 |
| ADC1_CH5 | GPIO6 |
| ADC1_CH6 | GPIO7 |
| ADC1_CH7 | GPIO8 |
| ADC1_CH8 | GPIO9 |
| ADC1_CH9 | GPIO10 |

### ADC2

| Channel | GPIO |
| --- | --- |
| ADC2_CH0 | GPIO11 |
| ADC2_CH1 | GPIO12 |
| ADC2_CH2 | GPIO13 |
| ADC2_CH3 | GPIO14 |
| ADC2_CH4 | GPIO15 |
| ADC2_CH5 | GPIO16 |
| ADC2_CH6 | GPIO17 |
| ADC2_CH7 | GPIO18 |
| ADC2_CH8 | GPIO19 |
| ADC2_CH9 | GPIO20 |

The authoritative mapping is in Espressif's [ESP32-S3 ADC API
reference](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc/index.html),
which lists the `ADC1_GPIO1_CHANNEL` through `ADC1_GPIO10_CHANNEL` and
`ADC2_GPIO11_CHANNEL` through `ADC2_GPIO20_CHANNEL` definitions. Thus only
GPIO1 through GPIO20 are in the ESP32-S3 ADC-capable set; other GPIO numbers do
not become analog inputs merely because they are GPIOs.

## Selection and integration caveats

- Prefer **ADC1** when Wi-Fi may run. Current ESP-IDF documentation says ADC2 is
  shared with Wi-Fi in [oneshot mode](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc/adc_oneshot.html#hardware-limitations),
  with driver protection, and documents an ESP32-S3 ADC2 DMA limitation in
  [continuous mode](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc/adc_continuous.html#hardware-limitations).
  ADC2 behavior and RF coexistence have varied across Espressif chips and IDF
  drivers, so consult the current target-specific IDF documentation rather than
  assuming a broader rule.
- Maximum measurable input voltage depends on the configured attenuation and
  the chip's ADC characteristics. Use Espressif's [ADC attenuation
  guidance](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc/index.html#adc-attenuation)
  and the ESP32-S3 datasheet; this page intentionally does not assign a voltage
  limit.
- This map does not replace checks for strapping, USB, flash, or other pin
  functions. Those constraints are separate and depend on the package, module,
  board routing, and design.
- A package or module variant may omit a chip pad, and a development board may
  not break every listed GPIO out. The table therefore does **not** guarantee
  GPIO1 through GPIO20 are all accessible on a given DevKit.
- This is not a PodlESP pin assignment for the touch-LCD product. A board model
  needs its own primary-source schematic and revision evidence before making
  connector or peripheral pin claims.

An analog source such as a contact piezo or analog-output MEMS sensor could use
one of these channels through a suitable analog front end. PDM or I2S digital
microphones use digital peripherals instead of these ADC channels.
