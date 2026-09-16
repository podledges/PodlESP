# led-pattern (lab demo)

ESP32-S3 firmware: WS2812 onboard LED pattern for lab bring-up.

- **1 Hz** brief blink
- every **10 s**: **2000 Hz** on/off burst for **250 ms**

GPIO **15**, 2× WS2812 GRB from Waveshare `04_WS2812_Test` (non-touch may be the only variant with the strip).

Build:

```console
nix build .#led-pattern --print-build-logs --max-jobs 2 --cores 2
```

Not UREX product code. Physical flash only via authorized Pi USB path.

## Flash via Pi lab

See [pi-lab-bootstrap.md](../../../docs/board-workflow/pi-lab-bootstrap.md) and:

```console
nix build .#led-pattern
python tools/podlesp_pi_lab.py plan-flash --artifact-dir result
```

Dry-run by default. Physical flash is operator-approved and uses esptool on the Pi over `/dev/serial/by-id/...`.
