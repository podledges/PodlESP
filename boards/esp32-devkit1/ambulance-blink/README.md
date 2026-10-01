# ambulance-blink (ESP32-DEVKIT1 / DevKitC class)

Classic **ESP32** (not S3) lab fixture over **CP2102** USB-UART.

- Target: `esp32`
- Onboard LED: **GPIO2** (blue user LED on Espressif DevKitC)
- Pattern: double-flash groups (ambulance-like duty on one LED)
- Console: UART0 115200 via CP2102

```console
nix build .#ambulance-blink
```

Flash **only** on Pi CP2102 by-id path (never S3 JTAG). Hold **BOOT** if esptool reports boot mode 0x13.
