# PodleRex ESP32 board compatibility and Singapore purchasing scout

**Date observed:** 2026-09-06<br>
**Task:** `podlerex-esp32-buying-scout`<br>
**Scope:** knowledge only. No implementation, purchases, accounts, hardware operations, installs, flashes, or repository changes.<br>
**Shopee:** blocked (login/traffic wall). Shopee prices, stock, and shipping are **unverified**. Verified Singapore alternatives are Amazon.sg and Lazada.sg.

This report is self-contained. It starts from the current PodleRex worktree, the local ESP32 TRM PDF, Espressif primary docs dated 2025–2026, and live Singapore storefronts.

---

## Executive recommendations (one per use case)

| Use case | Practical buy | Why | Do not |
|---|---|---|---|
| **Match current PodleRex firmware** (`ESP_piano` on original ESP32) | **Espressif ESP32-DevKitC-32E**, Amazon.sg, **S$23.20**, in stock, ships to Singapore | Official original-ESP32 board with ESP32-WROOM-32E, GPIO34/ADC1_CH6 broken out, ESP-IDF/PlatformIO first-class. Same chip family as the firmware. | Do not buy S3/C5/S31 as a drop-in. Do not wire a piezo disc to any ADC pin. |
| **Hobbyist “DevKit V1” 30-pin clone** (GPIO2 LED, breadboard-narrow) | Lazada **30Pin-Type-C** clone at **S$4.88 + S$1.99** shipping, Get by 9–14 Sep 2026; or Amazon.sg Teyleten 30P 3-pack **S$29.74** | 30-pin DOIT-style layout is what “ESP32 DevKit V1” usually means. GPIO34 is present. GPIO2 LED is typical on this clone class, not on official DevKitC. | Do not assume 30-pin and 36/38-pin are interchangeable. Do not use the extra flash pins on 36/38-pin boards. |
| **Newest announced chip** | **Do not buy yet** for this project | ESP32-S31 announced 2026-03-26, mass production 2026-07-27. IDF support is **preview on master**. No Amazon.sg listing found. Not pin-compatible. | Do not treat S31 as “newest therefore best” or as a DevKit V1 replacement. |
| **Newest official board purchasable in Singapore today** | **ESP32-C5-DevKitC-1-N8R8**, Amazon.sg, **S$29.55**, in stock | Dual-band Wi-Fi 6 + BLE + 802.15.4. Official Espressif. USB-C. Not suitable as a firmware drop-in. | Do not assume ADC channel numbers or GPIO2 LED. RISC-V single-core, different pinout. |
| **Newest *suitable* board if leaving original ESP32** (piezo/FFT/ESP-NOW research) | **ESP32-S3-DevKitC-1** (official N32R16V **S$27.55**, 1 left; or a verified N8R8) | Dual-core, better analog story than original ESP32, vector/SIMD, native USB. Matches the older PodlePianoDSP32 S3 path. Requires a firmware port. | Do not treat S3 as pin-compatible with DevKit V1. ADC1_CH6 is **not** GPIO34 on S3. |

**Analog front-end (all boards):** never connect a piezo contact disc or microphone capsule directly to an ESP32 ADC pin. The local KiCad sheet already intends an op-amp path to `ESP32_GPIO_34`; that path is unfinished and electrically inconsistent (TL072 symbol, MCP6002 value).

---

## What the repository actually targets

`Brief.md` is empty (0 bytes). `Research/`, `docs/`, and `AI-docs/` contain only `.gitkeep`. The local hardware/firmware evidence is:

| Artifact | What it implies |
|---|---|
| `ESP32/ESP_piano/main/adc_sampler.c:13-27` | Continuous ADC, `ADC_CONV_SINGLE_UNIT_1`, **`ADC_DIGI_OUTPUT_FORMAT_TYPE1`**, `ADC_CHANNEL_6`, `ADC_UNIT_1`, 12-bit, `ADC_ATTEN_DB_12`, `SAMPLE_RATE` 20480 Hz |
| `ESP32/ESP_piano/main/adc_sampler.h:7-8` | `SAMPLE_RATE 20480`, `READ_LENGTH 1024` |
| `ESP32/ESP_piano/main/audio_dsp.h:9-11` | `FFT_SIZE 2048`, piano-range threshold 150 mV |
| `ESP32/ESP_piano/main/audio_dsp.c:88` | Valid frequencies 27.5–4186 Hz (A0–C8) |
| `ESP32/ESP_piano/main/main.cpp:13` | Onboard LED **GPIO 2** |
| `ESP32/ESP_piano/CMakeLists.txt` | Native ESP-IDF CMake (`$ENV{IDF_PATH}`) |
| `ESP32/ESP_piano/main/idf_component.yml` | `espressif/esp-dsp: ^1.4.12` |
| `ESP32/ESP_piano/main/network.h` | ESP-NOW, hardcoded peer MAC |
| `KiCad/firstTime/firstTime.kicad_sch:1675,1986,1904` | Net `ESP32_GPIO_34`; op-amp instance **value MCP6002** on **TL072** symbol; piezo/microphone symbol |
| `Schematic & Datasheets/esp32_technical_reference_manual_en.pdf` | ESP32 TRM **v5.7**, 783 pages, created 2026-03-13 |

`ADC_DIGI_OUTPUT_FORMAT_TYPE1` is the original ESP32 DMA format. ESP32-S2/S3/C3/C5/S31 use TYPE2. Combined with GPIO2 LED and ADC1 channel 6 → GPIO34, the in-tree firmware is written for **original ESP32**, not S3.

Related predecessor reports:

- [`podlepianodsp32-urex-scout.md`](podlepianodsp32-urex-scout.md) (2026-08-24): recovered research platform used **ESP32-S3**, 16 kHz, ADC1 CH0/GPIO1, and a KiCad sheet labelled GPIO34. That GPIO mismatch is the same class of error this repo still has if someone flashes S3 firmware thinking “ESP32”.
- [`podlepianodsp32-embedded-c-agent-kb-scout.md`](podlepianodsp32-embedded-c-agent-kb-scout.md) (2026-09-02): no-hardware ESP-IDF ladder; do not connect an unverified piezo to ADC.

---

## Chip vs module vs development board

These three words are not interchangeable.

| Layer | What it is | Original-ESP32 examples | Notes |
|---|---|---|---|
| **Chip (SoC)** | Bare silicon. No flash, no antenna, no USB. | ESP32-D0WD-V3 (current). Several older SKUs are NRND/EOL in datasheet v5.3 (2026-07-29). | Two Xtensa LX6 cores, 2.4 GHz Wi-Fi + BT/BLE. No native USB. |
| **Module** | SoC + flash (+ optional PSRAM) + crystal + RF matching + antenna or U.FL, shielded. | ESP32-WROOM-32 (legacy), **ESP32-WROOM-32E / 32UE** (current), ESP32-WROVER-E (PSRAM). | This is what is soldered onto a DevKit. Antenna type (PCB vs U.FL) is a module suffix, not a chip change. |
| **Development board** | Module on a PCB with USB-UART, 3.3 V regulator, EN/BOOT buttons, pin headers. | **Espressif ESP32-DevKitC V4** (official). **DOIT ESP32 DEVKIT V1** (clone family). | “DevKit V1” in hobby listings almost always means the DOIT clone, **not** Espressif DevKitC. |

Espressif’s own current original-ESP32 entry board is **ESP32-DevKitC V4**, with module options WROOM-32E/32UE, WROVER-E/IE, WROOM-32D/32U (older), SOLO-1. User guide: <https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html> (docs timestamped 2026-07). USB is **Micro-B**. USB-UART is a discrete bridge (CP2102-class). Power LED only; **no GPIO2 user LED**.

DOIT ESP32 DEVKIT V1 is a third-party board that typically uses ESP32-WROOM-32 / 32D / 32E, Micro-USB or USB-C depending on year, CP2102 or CH340, and a blue LED on **GPIO2**. PlatformIO board id `esp32doit-devkit-v1` (<https://docs.platformio.org/en/latest/boards/espressif32/esp32doit-devkit-v1.html>). Vendor page historically `http://www.doit.am/`. It is **not** an Espressif-manufactured board.

### 30-pin vs 36/38-pin “DevKit V1”

| | **30-pin DOIT V1** | **36/38-pin DOIT / “DevKitC-32” clone** | **Official ESP32-DevKitC V4** |
|---|---|---|---|
| Headers | 15 + 15 | 18+18 or 19+19 | 19 + 19 (J2/J3) |
| GPIO34 / ADC1_CH6 | Present | Present | Present (`IO34`) |
| GPIO 6–11 (flash) | Usually **not** broken out | Often broken out as CLK/SD0/SD1/CMD/SD2/SD3 | Broken out as D0–D3/CMD/CLK; **do not use** |
| Breadboard | Narrow, usually fits | Often too wide; hangs off both rails | Official width; flash-pin row near USB |
| GPIO2 LED | Typical | Common | **No** user LED in Espressif user guide |
| USB | Micro-B or Type-C clone | Micro-B or Type-C clone | Micro-B |
| UART bridge | CP2102 or CH340 | CP2102 / CH340 / “CP2012” | CP2102-class, auto-program on GPIO0 |
| Firmware LED (`GPIO 2`) | Visible heartbeat | Usually visible | Toggles a pin with no LED |

GPIO34 is present on all three. The 30- vs 36-pin choice does **not** change the ADC pin for this firmware. The extra pins on 36/38-pin boards are mostly SPI-flash lines; Espressif: “Avoid using these pins, as it may disrupt access to the SPI flash memory.”

---

## ADC, sampling, analog front-end, USB/debug, toolchain

### ADC mapping (original ESP32)

From ESP-IDF `soc/adc_channel.h` and TRM Table 31.3-1 / datasheet Table 4-6:

| ADC | Channel | GPIO / pad | Usable with Wi-Fi? |
|---|---|---|---|
| ADC1 | CH0–CH3 | 36, 37, 38, 39 | Yes |
| ADC1 | CH4–CH5 | 32, 33 | Yes |
| **ADC1** | **CH6** | **34 (VDET_1)** | **Yes — this is the firmware pin** |
| ADC1 | CH7 | 35 | Yes |
| ADC2 | CH0–CH9 | 4, 0, 2, 15, 13, 12, 14, 27, 25, 26 | **No** while Wi-Fi is on |

GPIO 34–39 are **input-only** (no output driver, no internal pull-up/down). Firmware `ADC_CHANNEL_6` + `ADC_UNIT_1` is GPIO34. The KiCad net `ESP32_GPIO_34` matches that, not S3 GPIO1.

IDF continuous-mode hardware limits for original ESP32 (v6.1):

- ADC2 is shared with Wi-Fi; `adc_continuous_start()` serialises against the Wi-Fi driver.
- Continuous DMA uses **I2S0 as the hardware FIFO**. If I2S0 is already taken, `adc_continuous_new_handle()` returns `ESP_ERR_NOT_FOUND`.
- ESP32 DevKitC: GPIO0 is occupied by auto-program circuitry.
- RNG quality drops while ADC continuous is running.
- Sample-frequency window in `soc_caps.h` for ESP32: **20 kHz – 2 MHz**. Firmware `SAMPLE_RATE 20480` sits on the **low bound**.

Datasheet v5.3 Table 4-3 (2026-07-29): 12-bit SAR, DIG controller up to **2 Msps**, DNL ±7 LSB, INL ±12 LSB, **Wi-Fi and Bluetooth off** for that characterisation. Table 4-4 calibrated total error at atten=3 (the old 11 dB / current 12 dB setting): **±60 mV** over 150–2450 mV. Firmware uses `ADC_ATTEN_DB_12` and then converts peak-to-peak as if full-scale were 3300 mV (`adc_sampler.c:49`). That millivolt scale is **not** datasheet-accurate; IDF says use `adc_cali_raw_to_voltage()`.

Effective ADC ranges after eFuse Vref calibration (datasheet Table 4-4):

| Atten | Effective range |
|---|---|
| 0 dB | 100–950 mV |
| 2.5 dB | 100–1250 mV |
| 6 dB | 150–1750 mV |
| 12 dB (atten=3) | 150–2450 mV; worse above ~2450 mV / code 3000 |

Absolute maximum on power/IO rails: **3.6 V** (Table 5-1). DC `VIH` max is `VDD + 0.3 V` (Table 5-3). A piezo disc can exceed that on a hard hammer strike.

Nyquist at 20.48 kHz is 10.24 kHz. C8 is 4186 Hz, so the fundamental fits, but piano harmonics and contact-mic transients do not, unless an analog anti-alias filter is present. Bin width is 10 Hz (`20480/2048`).

**Original ESP32 on-chip ADC is not an audio codec.** It is adequate for a first contact-mic feasibility test after a proper AFE, not for claiming transcription accuracy. Wi-Fi (ESP-NOW uses the Wi-Fi radio) couples noise into ADC1. That is a measurement problem, not something a newer pin-incompatible chip silently fixes in this firmware.

### Do not wire piezo to ADC

A piezo contact disc is a high-impedance capacitive generator. Open-circuit spikes of tens of volts are normal. The ESP32 pin will see:

1. Overvoltage beyond 3.6 V (permanent damage / latch-up).
2. Negative excursions (ADC is unipolar, 0–Vref).
3. Almost no current into the SAR sample capacitor, so a raw disc looks like a high-pass “click” rather than a piano signal.
4. No anti-aliasing, so 20.48 kHz sampling folds ultrasonic/transient energy into the 27.5–4186 Hz band the DSP trusts.

Required analog functions (design intent, not a schematic to build from this scout):

- **Clamp** to ~0 / 3.3 V (Schottky pair or dedicated clamp), with a series resistor.
- **Bias** near mid-rail (~1.65 V) so the unipolar ADC sees the waveform.
- **Buffer** with a 3.3 V rail-to-rail op-amp (MCP6002-class). TL072 is **not** a 3.3 V single-supply part.
- **Anti-alias** low-pass below ~8–10 kHz before the ADC.
- **Measure** spike voltage, bias, clipping, and noise with a scope **before** the ESP32 is attached.

The local KiCad sheet already points at that architecture (piezo → MCP6002-labelled stage → `ESP32_GPIO_34`) but the symbol is still TL072, the datasheet property still points at TI TL071, and there is no reviewed BOM. Treat it as intent, not a buildable AFE. Previous UREX scout made the same “do not attach until measured” call.

An I2S/PDM microphone or an external audio ADC is a different, cleaner acquisition path. It is **not** what `adc_sampler.c` implements.

### USB and debug

Original ESP32 has **no USB controller**. Programming is UART0 (GPIO1 TX / GPIO3 RX) through an on-board USB-UART bridge.

| Item | Official DevKitC V4 | DOIT DevKit V1 class |
|---|---|---|
| Connector | Micro-USB B | Micro-USB or USB-C clone |
| Bridge | CP2102-class, up to 3 Mbps | CP2102 or CH340 (“CP2012” in some listings) |
| Auto-reset | Yes (GPIO0 programming circuit) | Usually yes; quality varies |
| Download | Hold BOOT, tap EN | Same |
| Native USB / USB-Serial-JTAG | No | No |
| On-board JTAG | No | No |
| External JTAG | GPIO12/13/14/15 (MTDI/MTCK/MTMS/MTDO) | Same; 30-pin boards still expose 12/13/14/15 |
| Cable | Data-capable USB cable required | Same |

PlatformIO: default upload `esptool`. Board is **not ready** for 1-click debug; needs ESP-Prog / J-Link / CMSIS-DAP. ESP-IDF: `idf.py flash/monitor` over the same UART. Official `idf.py mcp-server` can flash — keep that out of the default agent profile (already in the source investigation context).

ESP32-S3 and ESP32-C5 DevKits add a **USB-Serial/JTAG Type-C port on the chip** plus a separate USB-UART Type-C. That is a board/chip change, not a DevKit V1 feature.

### ESP-IDF and PlatformIO

Current in-tree project is **ESP-IDF native**, not Arduino.

| Tool | Original ESP32 DevKitC / DOIT V1 | C5 / S3 / S31 |
|---|---|---|
| ESP-IDF v6.1 (stable, docs 2026-09-05) | Full (`idf.py set-target esp32`) | C5/S3 full; **S31 preview on master only** |
| PlatformIO `espressif32` | `board = esp32doit-devkit-v1` or `esp32dev`; `framework = espidf` | Different board ids; not a recompile |
| Arduino-ESP32 | Works, but this repo is not Arduino | Different cores |
| QEMU | CPU/memory, not ADC/AFE | Same limit |

There is no `sdkconfig` in the repo, so the IDF target is not pinned. `ADC_DIGI_OUTPUT_FORMAT_TYPE1` will not mean the same hardware on S3/C5.

---

## Newest chip vs newest purchasable board vs newest suitable board

Do not collapse these three.

### Newest announced / newest SoC: ESP32-S31

Espressif primary sources:

- Announcement: 2026-03-26, “Espressif Unveils ESP32-S31…” <https://www.espressif.com/ja-jp/node/10413>
- Mass production: **2026-07-27** <https://www.espressif.com/en/news/ESP32_S31_Mass_Production>
- Product page: <https://www.espressif.com/en/products/socs/esp32-s31>
- Dual-core 32-bit RISC-V up to 320 MHz, 512 KB SRAM, up to 60 GPIOs, Wi-Fi 6 **2.4 GHz only**, Bluetooth 5.4 (LE Audio + Classic), IEEE 802.15.4, Gigabit Ethernet MAC, dual I2S.
- Official boards on <https://www.espressif.com/en/products/devkits> (fetched 2026-09-06): **ESP-Mosaico**, **ESP32-S31-Function-CoreBoard-1**, **ESP32-S31-Korvo-1**. User guide for the Function-CoreBoard: <https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s31/esp32-s31-function-coreboard-1/user_guide.html>
- Buy links on that page are **AliExpress** (Function-CoreBoard `1005012329349286`, Korvo-1 `1005012333744553`, Korvo sample ~US$59). Not Amazon.sg.
- ESP-IDF: v6.1 release notes (2026-08-27) “Added **preview** support for ESP32-S31”. Developer portal: “Until a full support version is released, please update to the HEAD of master.” <https://developer.espressif.com/hardware/esp32s31/>
- Chip datasheet still **PRELIMINARY** (v0.5, 2026-07-13). WROOM-3 module datasheet v0.7, 2026-09-03, still PRELIMINARY.

Amazon.sg search for `ESP32-S31` on 2026-09-06 returned S3/C3 boards, **no S31 DevKit**.

Pinout is unrelated to DevKit V1 (Function-CoreBoard J2 uses GPIO58/59 UART, GPIO61 BOOT, GPIO60 RGB LED, etc.).

### Newest *purchasable official* board in Singapore (verified): ESP32-C5-DevKitC-1

- ESP32-C5 mass production announced **2025-05-23**: <https://developer.espressif.com/blog/2025/05/news-esp32c5-mp/>
- Chip datasheet **v1.5, 2026-09-03** (official release, not preview).
- Board user guide v1.2: <https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c5/esp32-c5-devkitc-1/user_guide.html>
- Dual-band Wi-Fi 6 (2.4 + 5 GHz), BLE 5, Zigbee/Thread. RISC-V **single-core 240 MHz**. USB-C (chip USB-Serial/JTAG + USB-UART). ADC channels are GPIO1/2/3/4/5/6, **not GPIO34**.
- Amazon.sg official listing verified 2026-09-06: see purchasing section.

ESP32-P4 is high-performance (no on-chip Wi-Fi; uses C5/C6 as a radio companion). Datasheet v1.2 2026-06-10. Wrong class for a DevKit V1 replacement.

ESP32-C61 DevKit exists (Mouser “New Product”) but is not the headline newest radio chip; C5 is the dual-band Wi-Fi 6 SoC, S31 is the newest high-end Wi-Fi 6 + BT Classic + 802.15.4 + Ethernet SoC.

### Newest *suitable* board for this piezo/FFT work (if changing chips)

**ESP32-S3-DevKitC-1**. Not the newest SoC. Dual-core Xtensa LX7, better documented ADC continuous path, vector extensions, native USB, PSRAM options, already used in PodlePianoDSP32. Requires a firmware port: TYPE2 ADC format, different GPIO map (S3 ADC1_CH0 is GPIO1), no GPIO2-as-DevKit-LED assumption.

---

## Singapore purchasing

### Shopee — blocked (unverified)

`chrome-devtools-axi` session `esp32scout`:

- Search `https://shopee.sg/search?keyword=ESP32%20DevKit%20V1` redirected to<br>
  `https://shopee.sg/verify/traffic/error?...&is_logged_in=false`<br>
  copy: “Page Unavailable … Please log in and try again.” The transient tracking identifier is omitted from this public copy.
- Direct product URL also redirected to the same wall (a transient tracking identifier omitted from this public copy).

No login or checkout was performed.

Indexed Shopee URLs that **existed in search snippets** but could **not** be verified for price, stock, variant, or Singapore delivery:

- <https://shopee.sg/ESP32-DevKitC-WIFI-Bluetooth-Development-Board-Equipped-with-WROOM-32D-32U-WROVER-Module-38Pin-TYPE-C-Interface-i.1090513196.24217753393> — 38-pin Type-C clone, ships-from snippet “Mainland China”.
- <https://shopee.sg/ESP32-DevKitC-core-board-ESP32-development-board-ESP32-WROOM-32D-ESP32-WROOM-32U-for-Arduino-i.161750523.7359003532> — seller `luckcute.sg`, 96% rating in snippet, ships-from “Mainland China”, copies Espressif DevKitC V4 getting-started text.

Treat those as **unverified**. Do not use snippet text as stock or SGD price.

### Verified alternative 1 — Amazon.sg (official Espressif, ships to Singapore)

Observed 2026-09-06 in headed Chrome, **no login/checkout**. Buy box: delivery to Singapore, shipper **Amazon US**, “US imports may differ from local products.”

| Board | URL | Price | Stock | Delivery evidence | Notes |
|---|---|---|---|---|---|
| **ESP32-DevKitC-32E** (official, WROOM-32E, 4 MB flash, PCB antenna) | <https://www.amazon.sg/Espressif-ESP32-DevKitC-32E-Development-Board/dp/B09MQJWQN2> | **S$23.20** | **In stock** | Free delivery Mon 14 Sep 2026 on international items over S$60; fastest Sat 12 Sep | **Recommended original-ESP32 board.** Variants on the same page: 32UE S$24.71, VE S$24.47, VIE S$24.71. Links Espressif getting-started. |
| **ESP32-C5-DevKitC-1-N8R8** (official) | <https://www.amazon.sg/Espressif-ESP32-C5-DevKitC-1-N8R8-Development-Board/dp/B0G4CY619B> | **S$29.55** | **In stock** | Free delivery Sat 12 Sep 2026 over S$60 | **Recommended newest official purchasable board.** Not firmware-compatible. |
| **ESP32-S3-DevKitC-1-N32R16V** (official) | <https://www.amazon.sg/Espressif-ESP32-S3-DevKitC-1-N32R16V-Development-Board/dp/B0FDG3WJDX> | **S$27.55** | **Only 1 left** | Free delivery 14–18 Sep 2026 over S$60 | Suitable *if porting*. Listing bullet “256 MB Flash” is wrong; SKU is 32 MB flash + 16 MB PSRAM. |
| Teyleten 30-pin 3-pack (clone, CP2102) | <https://www.amazon.sg/Teyleten-Robot-ESP-WROOM-32-Development-Microcontroller/dp/B08246MCL5> | **S$29.74** | **In stock** | Free delivery Tue 15 Sep 2026 over S$60; fastest Sat 12 Sep | Explicitly 30P vs 38P “sizes and circuit layouts are different.” Clone, not Espressif. |

A 2026-09-06 Amazon.sg search for `ESP32-S31` did **not** return an S31 DevKit.

### Verified alternative 2 — Lazada.sg (clone DevKit V1 class)

Observed 2026-09-06, no login.

| Board | URL | Price | Delivery | Seller | Variant control |
|---|---|---|---|---|---|
| ESP32 30Pin/38Pin CP2102 Type-C clone | <https://www.lazada.sg/products/pdp-i3495650411.html> | **S$4.88** (was S$8.80) + **S$1.99** shipping | **Get by 9–14 Sep 2026** | Radiant Promenade, 96% seller rating, “100% Shipped in 48 hrs”, **no product reviews**, international seller, 15-day returns | Select **30Pin-Type-C** (also 30Pin-Micro, 38Pin-Micro, 38Pin-Type-C) |
| Waveshare ESP32-C5 (not Espressif DevKitC-1) | <https://www.lazada.sg/products/pdp-i13888605732.html> | **S$19.85** + S$1.99 | Get by 14–21 Sep 2026 | JY TECH HUB | N16R8 / N32R8 soldered/unsoldered. Dual-band C5 module. **Not** pin-compatible with DevKit V1. |

The S$4.88 Lazada board is the closest **verified** “DevKit V1 30-pin” Singapore listing. Specs on that page are marketplace-noisy (unrelated “battery/circuit breaker” fields). Prefer the Amazon official 32E if module authenticity and documentation matter more than S$18.

### Other SG-reachable distributors (partial)

Indexed, **not fully loaded in this environment** (DigiKey HTML was Cloudflare “Just a moment…” via curl; Mouser chrome tab failed with socket hang-up):

- DigiKey.sg ESP32-DEVKITC-32E: <https://www.digikey.sg/en/products/detail/espressif-systems/ESP32-DEVKITC-32E/12091810> — snippet **S$13.72**, 1,400 in stock, 8-week factory lead time. Prefer re-check in a browser before ordering.
- Mouser.sg ESP32-DevKitC-VE: <https://www.mouser.sg/ProductDetail/Espressif-Systems/ESP32-DevKitC-VE> — snippet **S$12.18**, 767 in stock (this SKU is **WROVER-E / PSRAM**, not the 32E WROOM).
- SGBotic search for ESP32 DevKit did not surface a current original-ESP32 DevKit in the pages fetched.

Espressif sample portal: <https://www.espressif.com/en/company/contact/buy-a-sample>. AliExpress official store is cited for S31 boards; not verified for Singapore GST/delivery here.

---

## Comparison matrix

| | DOIT DevKit V1 30-pin | DOIT / clone 36/38-pin | **Espressif DevKitC-32E** | ESP32-S3-DevKitC-1 | ESP32-C5-DevKitC-1 | ESP32-S31 Function-CoreBoard-1 |
|---|---|---|---|---|---|---|
| SoC | ESP32 (Xtensa dual) | ESP32 | **ESP32-D0WD-V3 in WROOM-32E** | ESP32-S3 | ESP32-C5 RISC-V 240 MHz | ESP32-S31 RISC-V 320 MHz dual |
| Module | WROOM-32 / 32E mixed | Mixed | WROOM-32E 4 MB | WROOM-1/2 variants | WROOM-1 N8R8 | WROOM-3 16+16 MB |
| Firmware drop-in for `ESP_piano` | **Yes** (TYPE1, GPIO34, GPIO2 LED) | Yes electrically; LED/USB vary | **Yes electrically; no GPIO2 LED** | **No** (TYPE2, GPIO map) | **No** | **No** + IDF preview |
| ADC1_CH6 | GPIO34 | GPIO34 | GPIO34 | **Not GPIO34** | **Not GPIO34** | Different |
| Wi-Fi vs ADC2 | ADC2 unusable | Same | Same | Different ADC | Different ADC | Different |
| On-chip ADC for piezo | Poor, needs AFE | Same | Same | Better, still needs AFE | Different, still needs AFE | Different; board has **codec + mic** |
| USB | UART bridge | UART bridge | Micro-USB UART | Dual Type-C, native USB | Dual Type-C, native USB | USB-C UART + USB-Serial/JTAG + USB-A host |
| Debug | External probe | External | External | On-chip USB-JTAG | On-chip USB-JTAG | On-chip USB-JTAG |
| ESP-IDF v6.1 | Yes | Yes | Yes | Yes | Yes | **Preview / master** |
| PlatformIO | `esp32doit-devkit-v1` | often `esp32dev` | `esp32dev` | `esp32-s3-devkitc-1` | C5 board id | Unlikely in stable PIO |
| Pin-compatible with DevKit V1 | Reference | Close, extra flash pins | Close, extra flash pins labelled | **No** | **No** | **No** |
| SG verified buy (2026-09-06) | Lazada 30Pin-Type-C S$4.88; Amazon Teyleten 3× S$29.74 | Lazada 38-pin variant of same listing | **Amazon.sg S$23.20 in stock** | Amazon.sg N32R16V S$27.55 (1 left) | **Amazon.sg S$29.55 in stock** | AliExpress only; **not on Amazon.sg** |
| Role | Cheap V1-shaped clone | Extra pins, more foot-gun | **Buy this for current firmware** | Best *suitable* upgrade | Newest official SG board | Newest announced platform |

---

## Portability notes for related tooling work

Do not expand these into implementation. Record only:

1. In-tree firmware is **ESP-IDF CMake**, target **original ESP32**, continuous ADC DMA, `esp-dsp`, ESP-NOW. Not Arduino. Not PlatformIO-first (PIO can wrap IDF via `framework = espidf`, `board = esp32doit-devkit-v1` or `esp32dev`).
2. `SAMPLE_RATE 20480` is the ESP32 digital-ADC **minimum** (`SOC_ADC_SAMPLE_FREQ_THRES_LOW` = 20 kHz). Treat sample-rate experiments as a hardware+driver question, not a free software knob.
3. Continuous ADC **owns I2S0** on original ESP32. Host tests and QEMU will not prove ADC fidelity; that remains a hardware evidence boundary.
4. GPIO2 LED is a **DOIT V1 convention**. Official DevKitC will compile and toggle GPIO2 with no visible LED.
5. Analog safety is a **hardware gate**, not a clang-tidy gate. Agent must not invent a “direct GPIO34 piezo” wiring from the KiCad net name.
6. PDF: local TRM is ESP32 v5.7 (2026-03-13). Datasheet used here is v5.3 (2026-07-29) from espressif.com. `pdftotext` first, for document inspection.
7. Windows is only justified for USB-UART driver install (CP210x / CH340) and physical flash/monitor. Linux/NixOS can do IDF builds.
8. If the planner assumes ESP32-S3 docs (GPIO1, TYPE2, USB-JTAG), it will mis-advise this repo. Keep original-ESP32 TRM/datasheet as the ADC source of truth until a port is explicitly planned.
9. Newest chips (C5, S31) are IDF-supported to different degrees; S31 is preview. A “set-target” change is a project port, not a board swap.

---

## What should ship from this scout

Nothing in the PodleRex repository. No bug was reproduced that has a code fix. Maintainers may later:

- fill `Brief.md` / `Research/` with a pointer to this report,
- pin `idf.py set-target esp32` / a `sdkconfig.defaults`,
- replace the TL072/MCP6002 KiCad inconsistency,

those are follow-up tasks, not this scout.

---

## Method, commands, limits

Inspected PodleRex revisions: `54e90f7` and `9636eeb`, from a disposable detached worktree. `Brief.md` was empty.

Commands / tools:

- Read `ESP32/ESP_piano/main/{adc_sampler.c,adc_sampler.h,audio_dsp.c,audio_dsp.h,main.cpp,network.h,packet.h,CMakeLists.txt,idf_component.yml}` and `KiCad/firstTime/firstTime.kicad_sch`.
- `pdfinfo` / `pdftotext` on local TRM and downloaded `esp32_datasheet_en.pdf` (v5.3, 2026-07-29, 78 pages).
- `web_search` / `web_fetch` / `open_page` against docs.espressif.com, espressif.com news/devkits, developer.espressif.com, GitHub esp-idf v6.1, PlatformIO.
- `chrome-devtools-axi` session `esp32scout`: Shopee traffic wall (twice); Amazon.sg product pages; Lazada.sg search + PDP.
- No Shopee login. No checkout. No flash. No repo writes.

Primary citations:

- ESP32-DevKitC V4 user guide: <https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html>
- ESP-IDF v6.1 ADC continuous (ESP32): <https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc/adc_continuous.html>
- ESP-IDF v6.1 ADC overview: <https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc/index.html>
- ESP32 datasheet v5.3: <https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf>
- Local TRM v5.7: `Schematic & Datasheets/esp32_technical_reference_manual_en.pdf` (created 2026-03-13)
- ADC channel header: <https://github.com/espressif/esp-idf/blob/v6.1/components/soc/esp32/include/soc/adc_channel.h>
- PlatformIO DOIT V1: <https://docs.platformio.org/en/latest/boards/espressif32/esp32doit-devkit-v1.html>
- ESP32-S31 MP 2026-07-27: <https://www.espressif.com/en/news/ESP32_S31_Mass_Production>
- ESP32-S31 boards: <https://www.espressif.com/en/products/devkits>
- ESP32-S31 Function-CoreBoard-1: <https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s31/esp32-s31-function-coreboard-1/user_guide.html>
- ESP32-S31 IDF status: <https://developer.espressif.com/hardware/esp32s31/>
- ESP-IDF v6.1 notes (S31 preview): <https://github.com/espressif/esp-idf/releases/tag/v6.1>
- ESP32-C5 MP 2025-05-23: <https://developer.espressif.com/blog/2025/05/news-esp32c5-mp/>
- ESP32-C5-DevKitC-1 v1.2: <https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c5/esp32-c5-devkitc-1/user_guide.html>
- ESP DevKits index: <https://docs.espressif.com/projects/esp-dev-kits/en/latest/>

Limits:

- Shopee could not be verified. Facts from Shopee search snippets are labelled unverified.
- DigiKey/Mouser SG pages were not fully rendered here.
- Piezo spike voltages were **not** measured (knowledge-only; no hardware).
- Amazon/Lazada prices and stock are **2026-09-06 snapshots**.
- “In stock” on Amazon US import listings can change; delivery dates assume the observed Singapore destination.
