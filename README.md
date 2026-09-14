# PodlESP

Project-local, reproducible ESP-IDF tooling for ESP32 development. One shared
tool environment supports board-specific firmware under [`boards/`](boards/).
The default scope is deliberately hardware-safe. Builds never access hardware;
the documented board workflow is dry-run by default and requires a fully
confirmed board configuration plus fresh, externally granted, one-time approval
before it can flash/reset or run its bounded serial self-test.

## Pinned toolchain

[`flake.lock`](flake.lock) pins both Nixpkgs and
[`mirrexagon/nixpkgs-esp-dev`](https://github.com/mirrexagon/nixpkgs-esp-dev),
the maintained packaging recommended by the [NixOS ESP-IDF
wiki](https://wiki.nixos.org/wiki/ESP-IDF). One shared `esp-idf-full`
environment supplies toolchains for ESP-IDF's supported chip families; board
folders select their own target. For the initial ESP32-S3 project it provides:

- ESP-IDF **v5.5.2** and `idf.py`;
- `xtensa-esp-elf` GCC **14.2.0 (esp-14.2.0_20251107)** for ESP32-S3;
- Espressif GDB **16.3_20250913**; and
- Espressif OpenOCD **0.12.0-esp32-20250707** (invoked as `openocd`).

The upstream flake permits Python `ecdsa` 0.19.1, which Nixpkgs marks insecure,
because esptool depends on it; follow the linked packaging project's security
notice when updating the lock.

Nix 2.4 or newer with flakes enabled is required. No global installation or
system activation is needed.

## Enter the environment

From the repository root:

```console
nix develop
```

There is intentionally no automatically trusted `.envrc`. Run `nix develop`
explicitly. The measured x86_64-linux store closure is **7.2 GiB**; compressed
download size varies with cache state. Allow disk, network, and time for the
pinned ESP-IDF source and all supported binary toolchains. Build the shell
derivation and remeasure its closure with:

```console
shell_path="$(nix build --no-link --print-out-paths .#devShells.x86_64-linux.default)"
nix path-info --closure-size --human-readable "$shell_path"
```

Confirm the tools without touching a device:

```console
idf.py --version
xtensa-esp32s3-elf-gcc --version
xtensa-esp32s3-elf-gdb --version
openocd --version
```

## Build-only smoke test

[`boards/esp32-s3-touch-lcd-1.9/smoke`](boards/esp32-s3-touch-lcd-1.9/smoke)
is a minimal ESP-IDF application. Its board-local CMake project fixes
`IDF_TARGET` to `esp32s3`; the shared development shell does not select a chip.
The example contains no display, touch, or board-pin configuration. It does
explicitly select the ESP32-S3 USB Serial/JTAG console, a 2 MB flash image, and
a single-factory-app partition table for the generic fixture; these build
settings are not proof that an assigned physical board supports them.

The fully sandboxed reproducibility check is:

```console
nix flake check --print-build-logs --max-jobs 2 --cores 2
```

Equivalently, build the named output:

```console
nix build .#smoke --print-build-logs --max-jobs 2 --cores 2
```

To prove the actual development-shell entry and ordinary cross-build path:

```console
nix develop --command bash -euc '
  idf.py --version
  xtensa-esp32s3-elf-gcc --version | head -n 1
  xtensa-esp32s3-elf-gdb --version | head -n 1
  openocd --version
  cd boards/esp32-s3-touch-lcd-1.9/smoke
  export CMAKE_BUILD_PARALLEL_LEVEL=2 NINJAFLAGS=-j2
  idf.py set-target esp32s3
  idf.py build
  grep -F "CONFIG_IDF_TARGET=\"esp32s3\"" sdkconfig
  xtensa-esp32s3-elf-readelf -h build/podlesp-smoke.elf
'
```

This only creates ignored local build files. Do **not** append `flash`,
`monitor`, OpenOCD startup, or an esptool command to these validation commands.
CI first discovers all pure-Python host/offline board-workflow and broker
contract safety tests with the runner's Python 3, then uses the pinned Nix
tooling for the sandboxed check with two jobs/cores and a 45-minute job limit.
These are separate offline-contract and compilation results, not board
validation.

## Guarded board workflow

The project commands and future first-run checklist are in
[`docs/board-workflow/`](docs/board-workflow/README.md):

```console
./tools/podlesp-board build
./tools/podlesp-board flash
./tools/podlesp-board test-board
```

The latter two are validation-only dry runs unless `--execute` is explicitly
supplied together with a complete local board configuration and scoped,
unexpired, one-time approval. The flag is not captain/operator permission. No
hardware command is authorized by this documentation or by a successful build.
Run the offline guard and capture tests with:

```console
python3 -m unittest discover -s tests -v
```

The [Phase 1 traceability ledger](docs/board-workflow/phase-1-traceability.md)
maps safety requirement IDs to implemented tests and clearly separates
proposed follow-up coverage. The source-only [broker contract](docs/board-workflow/broker-contracts.md)
defines versioned plans, enrollment records, and approval envelopes; it is not
a running service or hardware authority.

## Board layout and compatibility

For the chip-level analog channel map, see [ESP32-S3 ADC-capable
GPIOs](docs/esp32-s3-adc-gpios.md); it is not a board or product pin assignment.

Each model gets `boards/<model-slug>/`, containing a hardware note and its own
firmware/configuration folders. The first model is
[`esp32-s3-touch-lcd-1.9`](boards/esp32-s3-touch-lcd-1.9/README.md). Its board
note separates the confirmed `esp32s3` chip-family build target from unconfirmed
physical model/revision and peripheral assumptions.

To add a board, verify its exact identity against public manufacturer and chip
primary sources, create one normalized model slug, document the ESP-IDF chip
target and evidence, and add a board-local project/config. Parameterize another
`mkEspIdfFirmware` output in [`flake.nix`](flake.nix) only when that project
exists. Reuse the shared pinned environment; do not duplicate flakes, invent
prospective board folders, or assume pin/memory compatibility from the chip
family. Build within the board folder so generated configuration does not leak
between models.

## NixOS-WSL USB notes (future manual use only)

These notes are for a later, explicitly authorized hardware session. None of
them are part of setup or CI validation.

### Forwarding from Windows

Microsoft's [WSL USB
instructions](https://learn.microsoft.com/windows/wsl/connect-usb) require
`usbipd-win` 5 or newer. Keep a WSL terminal open, then in PowerShell:

```powershell
usbipd list
# Administrator PowerShell, once per device sharing setup:
usbipd bind --busid <BUSID>
# A normal PowerShell is sufficient after binding:
usbipd attach --wsl --busid <BUSID>
```

Use the bus ID shown by `usbipd list`; do not record hardware serial numbers in
this repository. While attached, Windows cannot use the device, and all WSL2
distributions share access to it. Attachment is not durable across physical
disconnects and may be lost across WSL/Windows shutdown or USB re-enumeration;
run `usbipd list` and attach the current bus ID again rather than scripting a
reconnect loop. When a later session is finished, disconnect physically or use:

```powershell
usbipd detach --busid <BUSID>
```

### Linux permissions are two separate paths

A CDC ACM serial node such as `/dev/ttyACM*` is commonly `root:dialout` mode
`0660`. Membership changes only take effect in a new login/session (often after
restarting WSL); verify with `id -nG` and `stat /dev/ttyACM*`. Do not use `sudo`
or loosen the node to world-writable as a workaround.

OpenOCD's USB JTAG access is separate from serial-node access. It uses libusb
and requires Espressif OpenOCD udev rules; `dialout` membership alone is not a
JTAG permission grant. On NixOS those rules must be enabled through the
captain-owned system configuration and activated separately. Espressif's
[ESP32-S3 built-in JTAG
documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/jtag-debugging/configure-builtin-jtag.html)
requires Linux udev rules and warns that the USB D+/D- wiring must be suitable.
Do not infer this from the presence of a serial node.

### Safe next steps

After the physical SKU/revision, effective `dialout` membership, and separate
udev rules are confirmed, a future bounded hardware plan should be reviewed and
explicitly authorized. Split it into one operation at a time: first passive USB
and permission inspection, then (if approved) a serial-only observation, and
only later a temporary debug build and flash/monitor or JTAG test. Define a
stop condition and factory-firmware recovery plan before any write or reset.
Never automate reconnect, reset, flash, erase, or probe loops.
