# Pi USB lab bootstrap (thin host)

The Raspberry Pi is a **flash/serial lab host only**. Full ESP-IDF / `idf.py` / Nix
ESP toolchains stay on the main machine via PodlESP flake packages.

## Current lab facts (update if inventory changes)

| Item | Value |
|---|---|
| SSH | `ssh -i ~/.ssh/podlesp_pi_ed25519 podledges@192.168.0.14` |
| Board | Raspberry Pi Zero 2 W Rev 1.0 |
| Management Wi-Fi | **5 GHz only** — `wlan1` Realtek `0bda:c811` / `rtw88_8821cu` on AVE_5G. Do not restore 2.4 GHz as primary. |
| ESP USB | `303a:1001` Espressif USB JTAG/serial |
| Serial by-id | `/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_1C:DB:D4:7A:5F:D0-if00` |
| esptool venv | `~/.local/share/podlesp/venvs/esptool-5.1.0` (`esptool==5.1.0`) |
| User groups | `dialout`, `plugdev` (serial access without root) |

RAM on Zero 2 W is ~424 MiB — **do not** install full ESP-IDF or a Nix ESP build farm on the Pi.

## After reboot — re-verify (read-only)

```bash
ssh -i ~/.ssh/podlesp_pi_ed25519 podledges@192.168.0.14
tr -d '\0' < /proc/device-tree/model; hostname; hostname -I
lsusb
ls -l /dev/serial/by-id/
~/.local/share/podlesp/venvs/esptool-5.1.0/bin/python -m esptool version
ip -br addr   # expect wlan1 UP; leave wlan0 alone
```

If the by-id symlink name changes (new ESP unit), update docs and flash plans; never flash `/dev/ttyACM0` by bare name in automation.

## Repair esptool venv (Pi only)

```bash
VENV=~/.local/share/podlesp/venvs/esptool-5.1.0
python3 -m venv "$VENV"   # only if missing
"$VENV/bin/pip" install 'esptool==5.1.0'
"$VENV/bin/python" -m esptool version
```

## Repeatable led-pattern path

On the **main machine** (PodlESP checkout):

```bash
nix build .#led-pattern --print-build-logs --max-jobs 2 --cores 2
python tools/podlesp_pi_lab.py plan-flash --artifact-dir result
# Review printed scp/ssh/esptool plan (dry-run).
```

Operator-approved flash (destructive): transfer `result/*.bin` to Pi `~/podlesp-led-flash`, then run esptool from the plan against the **by-id** port. Capture serial and check markers:

```text
PODLESP_LED_TICK sec=N
PODLESP_LED_BURST start hz=2000 ms=250 cycles=...
PODLESP_LED_BURST end
```

```bash
python tools/podlesp_pi_lab.py parse-capture /path/to/capture.log
```

Guarded local (non-Pi) smoke workflow remains `tools/podlesp_board.py` and is separate.

## Non-goals

- Full IDF on the Pi
- Automatic Wi-Fi cutover or 2.4 GHz restore
- Standing flash authority — each physical flash needs a fresh captain/operator decision
