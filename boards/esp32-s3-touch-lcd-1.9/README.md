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

## Captain-reported vendor marketing claims

The following text records captain-provided marketing/specification claims for
this **ESP32-S3 1.9-inch touch-LCD model only**. It is not a confirmed inventory
of the assigned unit. Treat every item as unverified until physical markings
identify the product and revision and the matching primary manual or schematic
confirms it; the authority order below still applies.

| Area | Captain-reported / vendor marketing claim | Qualification |
| --- | --- | --- |
| Processor | ESP32-S3R8; dual-core Xtensa LX7, up to 240 MHz | Claimed for this model; exact fitted package is not yet physically confirmed. |
| On-chip memory | 512 KB SRAM and 384 KB ROM | Chip-level claim, not a measurement of the assigned board. |
| Additional memory | Internal 8 MB PSRAM and external 16 MB flash | Claimed capacities and placement; neither is proven by the smoke fixture or a build. |
| Wireless | 2.4 GHz Wi-Fi (802.11 b/g/n), Bluetooth 5 LE, and an onboard antenna | The supplied blurb also says “WiFi 6.” Do not interpret that as 802.11ax: it conflicts with the commonly documented ESP32-S3 802.11 b/g/n capability and must not be asserted unless a primary Waveshare/Espressif source for this exact product establishes it. Antenna implementation remains unconfirmed. |
| Display | 1.9-inch IPS LCD; 170×320; 262K color; approximately 500 cd/m² brightness and 900:1 contrast; SPI; ST7789V2 driver | Marketing values and controller identity are claimed, not observed. |
| Touch | CST816 touch controller on touch-enabled variants | Variant-dependent claim; do not assume the assigned unit includes it. |
| IMU | Six-axis `QM18658`, as written by the captain | `QM18658` is likely a vendor typo for the commonly used `QMI8658`; retain both names pending a marking/photo and matching primary documentation. |
| Connections | USB Type-C power/debug, 3.7 V MX1.25 Li-ion charging port, and microSD slot | Presence and functions are claimed; connector wiring, card interface, and electrical limits remain unconfirmed. |
| Enclosure | Metal body | Claimed material, not physically verified. |

The phrase “rich compatible interface” appears in the supplied marketing text,
but is too vague to establish any connector, header, signal, bus, or pin map.
No such interface details should be inferred from it. The linked
[Waveshare documentation](https://docs.waveshare.com/ESP32-S3-LCD-1.9) is useful
model-name evidence, but its product facts become board facts here only after
the assigned hardware identity and revision are confirmed.

### ESP32-S3 ADC (chip-level, not board pinout)

This product class uses ESP32-S3, whose silicon ADC map is **ADC1 on GPIO1–10**
and **ADC2 on GPIO11–20**. See the repository's explicit
[ESP32-S3 ADC-capable GPIO map](../../docs/esp32-s3-adc-gpios.md) and its linked
Espressif sources.

That map describes silicon capability only. It does **not** identify which
header or pad, if any, is available for analog use on this 1.9-inch LCD board.
The LCD, touch controller, IMU, USB, flash, or other board circuitry may consume
or constrain those pins; a free ADC net requires the matching schematic and
hardware revision before use. Prefer ADC1 when Wi-Fi may run. In particular, do
not treat ADC2-capable GPIO19 or GPIO20 as free analog inputs without checking
USB routing on the actual PCB.

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
image, and the single-factory-app partition table. The 2 MB selection is a
fixture compile choice, not a contradiction of or proof for the claimed 16 MB
board flash. Those compile-time choices are not evidence that the assigned
physical board has compatible wiring or memory;
[`docs/board-workflow/`](../../docs/board-workflow/README.md) requires
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
