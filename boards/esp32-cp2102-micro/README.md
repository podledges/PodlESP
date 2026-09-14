# ESP32S-CP2102-MICRO

## Identity and support status

- Repository slug: `esp32-cp2102-micro`
- Captain-provided marketplace/label string: `ESP32S-CP2102-MICRO`
- Alternate transcription seen in notes: `ESOP32S-CP2102-MICRO`
- ESP-IDF chip target: **not yet confirmed**
- Physical manufacturer, exact module marking, SKU, and hardware revision: **not yet confirmed**

This is the second lab board. It is **not the ESP32-S3 1.9-inch touch-LCD
model** documented in
[`boards/esp32-s3-touch-lcd-1.9/`](../esp32-s3-touch-lcd-1.9/README.md).
Keep evidence and configuration for the two physical boards separate.

## What the label probably means

Until the physical markings are recorded, the label supports only a working
interpretation:

- `ESP32S` likely refers to an ESP32-class module, possibly a classic ESP32 or
  ESP32-WROOM variant. It does **not** prove an ESP32-S3 chip.
- `CP2102` likely identifies a Silicon Labs CP2102 USB-to-UART bridge.
- `MICRO` likely describes a Micro-USB connector.

These interpretations are not confirmed manufacturer specifications. They do
not establish a module variant, pinout, flash size, memory configuration, or
board revision. No display, touch controller, IMU, or other onboard peripheral
has been reported for this model, so none is assumed here.

## Authority for future hardware work

Before adding board-facing configuration or code, identify the physical unit
and cite the fact's owner. Use this order:

1. markings observed on the exact board and module;
2. the matching manufacturer's product manual, schematic, and pinout;
3. Espressif's datasheet, technical reference manual, and ESP-IDF documentation
   for the chip established by those markings; and
4. checked-in project configuration and component documentation.

Do not transfer pin assignments, memory settings, buses, electrical limits, or
peripheral instances from a similarly named board. If the chip, schematic net,
or revision remains unclear, leave the assumption unimplemented and request
confirmation. A clean build proves compilation only, never hardware behavior.

### ADC separation from ESP32-S3

Do **not** apply [`docs/esp32-s3-adc-gpios.md`](../../docs/esp32-s3-adc-gpios.md)
to this board unless its module silk or other exact-board marking proves that
the chip is ESP32-S3. A classic ESP32 has a different ADC-capable GPIO and
channel map. If markings confirm a classic ESP32, use Espressif's
[ESP32 (non-S3) ADC documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc_oneshot.html)
and the matching chip datasheet as the chip-level authorities.

**ADC pins are TBD after chip ID.** Chip-level ADC capability still would not
prove that a GPIO is exposed or electrically usable on this particular board.

## Programming path expectation

The expected programming path is USB serial through the CP2102 bridge to the
chip's UART bootloader, using the Micro-USB connector. This remains an
interpretation of the label until the board is inspected. Do not assume the
built-in USB Serial/JTAG path selected by the ESP32-S3 smoke fixture, and do not
reuse that fixture's USB, target, reset, or boot assumptions for this model.

## Firmware

No board-local firmware or smoke application exists for this model yet. Do not
invent one until the exact chip target and the board facts needed by its
configuration are confirmed. The existing ESP32-S3 smoke application belongs
only to `esp32-s3-touch-lcd-1.9`.

Any future build remains compilation evidence only. Hardware operations must
follow [`docs/board-workflow/`](../../docs/board-workflow/README.md), whose
commands are dry-run by default and require exact-board evidence plus fresh,
scoped authorization for each real cycle.

## Future verification record

For a hardware-facing change, record in its change description:

- photographs or transcriptions of the exact board and module markings;
- confirmed manufacturer, product/SKU, module, chip, and hardware revision;
- source links (and document page/section where available) for every changed
  pin, bus, clock, memory, USB/UART, or electrical assumption;
- the ESP-IDF version, confirmed chip target, and relevant sdkconfig defaults;
- the exact build command and all warnings; and
- whether hardware behavior was actually observed, with untested claims clearly
  labeled.

For any authorized device interaction, also record the observed USB identity
and serial-device behavior without committing unique device serial numbers.
Keep application logic separate from board/peripheral initialization, and do
not add peripheral claims that are not supported by exact-board evidence.
