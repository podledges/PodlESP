# red-glow (ESP32-DEVKIT1)

Slow LEDC breathe on the **single DevKitC user LED (GPIO2)**.

Stock Espressif DevKitC has **no GPIO-controllable red power LED**. This demo
cannot turn a separate “blue” off while glowing another pin without external LEDs.

```console
nix build .#red-glow
```

Flash only on CP2102 by-id → ttyUSB0. Never S3/ACM0.
