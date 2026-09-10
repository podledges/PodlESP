# ESP32-S3-TOUCH-LCD-1.9

## Identity and support status

- Repository slug: `esp32-s3-touch-lcd-1.9`
- ESP-IDF chip target: `esp32s3`
- Captain-provided model string: `ESP32-S3-TOUCH-LCD-1.9`
- Physical manufacturer, SKU, and hardware revision: **not yet confirmed**

Waveshare publishes a product named
[`ESP32-S3-Touch-LCD-1.9`](https://docs.waveshare.com/ESP32-S3-LCD-1.9), SKU
30939, built around ESP32-S3R8 and documented as supporting ESP-IDF. This is
strong model-name compatibility evidence, but it is not proof that the physical
unit assigned to this repository is that exact product or revision.

## Authority for future hardware work

Before adding board-facing configuration or code, identify the physical unit
and cite the fact's owner. Use this order:

1. the exact product/revision marking and the manufacturer's product manual;
2. the matching manufacturer's schematic and pinout;
3. Espressif's ESP32-S3 datasheet, technical reference manual, and ESP-IDF
   documentation for chip-level behavior; and
4. checked-in project configuration and component documentation.

Do not transfer pin assignments, flash/PSRAM settings, buses, electrical limits,
or peripheral instances from a similarly named board. If a schematic net or
revision is unclear, leave the assumption unimplemented and request
confirmation. A clean build proves compilation only, never hardware behavior.

## Firmware

[`smoke`](smoke) is a generic build/self-test fixture. Its only board-family
constraint is ESP-IDF target `esp32s3`; it deliberately does not configure the
display, touch controller, external memory, GPIO, or JTAG. For a future approved
self-test it explicitly selects the chip's USB Serial/JTAG console, a 2 MB flash
image, and the single-factory-app partition table. Those compile-time choices
are not evidence that the assigned physical board has compatible wiring or
memory; [`docs/board-workflow/`](../../docs/board-workflow/README.md) requires
those facts to be confirmed before any hardware operation.

Build it from the repository root with:

```console
nix build .#smoke --print-build-logs --max-jobs 2 --cores 2
```

Generated `build/`, `sdkconfig`, and component-manager files stay inside this
board's firmware folder and are ignored by Git. The guarded project-local build
command additionally records immutable artifact hashes without hardware access:

```console
./tools/podlesp-board build
```

## Future verification record

For a hardware-facing change, record in its change description:

- exact board model, SKU, and revision observed;
- source links (and document page/section where available) for every changed
  pin, bus, clock, memory, or electrical assumption;
- ESP-IDF version, chip target, and relevant sdkconfig defaults;
- the exact build command and all warnings; and
- whether hardware behavior was actually observed, with untested claims clearly
  labeled.

Keep interrupt handlers short, acknowledge interrupt sources, treat ISR-shared
data as concurrent, use fixed-width types for hardware values, and keep
application logic separate from board/peripheral initialization.
