# Agent-operated build, approved flash, and board self-test

This is a deliberately narrow internal workflow for the generic ESP32-S3
fixture. It does not identify or certify the currently unknown physical board,
its memory, display, touch controller, pins, wiring, or product firmware. It
never validates a sensor or actuator. The normal commands are:

```console
./tools/podlesp-board build
./tools/podlesp-board flash
./tools/podlesp-board test-board
```

`build` invokes the repository's pinned, bounded Nix build. `flash` and
`test-board` are read-only plan validation by default: without `--execute` they
do not inspect, open, reset, or transmit to a device and do not invoke esptool.
There is no arbitrary argument passthrough. `test-board --execute` is the
preferred first bounded cycle because one process keeps the cooperating lock
across flash, standard reset, and capture. `flash --execute` is available for a
separately approved upload, but does not claim a firmware test.

## Software-only preparation

No hardware approval is needed for these steps:

```console
python3 -m unittest discover -s tests -v
nix flake check --print-build-logs --max-jobs 2 --cores 2
./tools/podlesp-board build
```

The last command writes `.podlesp/artifact.json` with the immutable Nix output,
source revision, lock-file digest, flash settings, and hashes of every artifact.
It requires a clean tracked source tree so an artifact cannot silently drift
from its revision. A successful build is compilation evidence for a generic
`esp32s3` fixture only. The [Phase 1 traceability ledger](phase-1-traceability.md)
maps the current host/offline tests to their safety requirement IDs and labels
proposed follow-up coverage separately. The source-only [broker data-plane
contract](broker-contracts.md) defines future request, enrollment, plan, and
approval records without adding a service or hardware path.

The fixture waits two seconds, emits `PODLESP_BOOT <random-run-nonce>`, then
emits exactly one `PODLESP_SELF_TEST_PASS <same-nonce>` or
`PODLESP_SELF_TEST_FAIL <same-nonce>`. It checks only that ESP-IDF reports an
ESP32-S3 with at least one core. USB Serial/JTAG console, a 2 MB flash image,
and the single-factory-app partition table are explicit fixture settings, not
claims about the assigned board.

## One-time facts and decisions

Copy `board.toml.example` to ignored `.podlesp/board.toml`. Every `UNKNOWN` must
be resolved from the exact unit and primary documentation before execution:

1. physical manufacturer, model, SKU, marking, and hardware revision;
2. flash and PSRAM parts, sizes, modes, and whether the fixture's 2 MB/DIO/80
   MHz image is supported;
3. schematic/revision proving the connector reaches ESP32-S3 USB Serial/JTAG,
   with no unsafe attached circuitry or GPIO/peripheral assumption;
4. current Windows/WSL USB forwarding and ownership arrangement;
5. confirmed current flash-encryption/secure-boot state, permission to replace
   the bootloader, partition table, and app sectors with this exact fixture,
   and the intended baud choices (the workflow never changes security state);
6. a preserved known-good image, its hash, a reviewed restoration method, and
   the fact that recovery may be impossible if no restorable image exists; and
7. acceptance that the project lock plus local process snapshot is only a
   cooperating safety measure, not complete OS/host exclusivity.

Use one exact `/dev/serial/by-path/...` endpoint. Record SHA-256 of its exact
sysfs USB serial string locally rather than recording the raw identifier. The
configured path, VID, PID, USB strings, and serial hash must all match and the
serial hash must identify exactly one current ACM endpoint. `303a:1001` only
identifies an Espressif USB Serial/JTAG interface used by multiple chips; it is
not board manufacturer/SKU/revision evidence.

Generate the scoped values without hardware access by running the default dry
run after the board file and build manifest exist:

```console
./tools/podlesp-board test-board
```

The output includes the fixed esptool plan and digests to place in a one-time
approval copied from `approval.toml.example`.

## Future approval and execution

**Do not run this section until the captain/operator gives fresh external
approval for this exact first cycle.** Creating an approval file or supplying
`--execute` does not prove permission. The approval must name the approving
person and short expiry and cover all of:

- exact board configuration hash and selected device identity digest;
- exact artifact-manifest hash;
- one standard esptool `write_flash` operation with `default_reset` before and
  `hard_reset` afterward;
- overwrite/sector erase of the bootloader at `0x0`, partition table at
  `0x8000`, and application at `0x10000`; and
- the immediate, read-only, bounded serial capture at the configured baud.

No blanket or continuing authority follows. Approval is marked consumed before
esptool starts, including when upload fails. Full-chip/region erase, eFuse,
security, secure-boot, JTAG/OpenOCD, arbitrary esptool commands, retries,
automatic reconnect, and permission/forwarding changes are not supported.

For the first approved cycle, one project agent/session enters the already
validated pinned shell and runs only:

```console
nix develop
./tools/podlesp-board test-board --execute
```

Immediately before esptool, the command takes `.podlesp/locks/board.lock`,
rechecks identity twice, and scans visible `/proc/*/fd` entries for a known
owner of that character device. A known owner stops the run. Inaccessible
unrelated processes are counted and reported, not treated as proof of
contention and not used to demand privileged inspection. Conversely, an empty
snapshot does not prove no race, no host monitor, or no competing WSL
distribution. `flock` only coordinates cooperating PodlESP sessions. If the
captain requires stronger availability evidence than these documented limits,
do not execute. Never kill owners, use broad sudo, chmod a node, change udev or
forwarding, or restart a service.

The fixed esptool invocation makes one open attempt, uses the artifact's three
files and settings, uses DTR/RTS `default_reset` to enter the bootloader, writes
and verifies the selected flash regions, then uses RTS `hard_reset` for a normal
boot. These control-line effects and flash-sector erasure mean flashing is
**destructive**, not nondestructive. The tool then verifies identity again and
opens the endpoint read-only (`O_RDONLY`) without idf-monitor or esptool. It
never deliberately changes DTR/RTS during capture or transmits bytes. Opening or
closing a particular USB/driver stack can still have platform-specific
control-line effects; wiring and behavior must be accepted before the run.
Plain observation is intentionally not a command here and never secretly
invokes auto-reset.

Capture flushes old input after open and requires a matching random boot/PASS
nonce, making stale buffered PASS output insufficient. It ends at 20 seconds or
65,536 bytes, whichever comes first, and stops immediately on disconnect or
error. There are no retries, reconnects, reset loops, or reflashes; the file
descriptor and lock close on every exit. PASS requires both markers. Explicit
FAIL is failure. Silence, garbage, missing/mismatched markers, crash output,
disconnect, byte cap, and timeout are inconclusive/failure, never success.
Configured 115200 baud in the example is a decision to confirm, not a conclusion
from the earlier unperformed serial scout.

## Evidence and first-run checklist

Each attempted run writes a bounded JSON record under ignored `.podlesp/runs/`
with artifact/config/device digests, upload status, firmware result, duration,
byte count, escaped serial text, and `physical_measurements: NOT_PERFORMED`.
Raw USB serials are omitted and MAC-like hex strings are redacted. Preserve the
run record outside this disposable worktree if it is needed as evidence.

Before the future first run, verify:

- [ ] repository tests, `nix flake check`, and `build` passed at the approved commit;
- [ ] every board/configuration/wiring/forwarding fact above is confirmed;
- [ ] exact by-path endpoint, hashed serial, and security state were confirmed now;
- [ ] no known host, WSL, IDE, terminal, monitor, or agent owns the board;
- [ ] cooperating-lock/snapshot limitations are acceptable for this run;
- [ ] known-good image and realistic recovery steps are available;
- [ ] fresh one-time approval covers artifact, config, device, erasure, reset, and capture;
- [ ] configured console and flash/test baud rates are approved;
- [ ] agent will run one command once and stop on any mismatch/error;
- [ ] result is reported separately as software tests, upload, firmware self-test,
      and physical measurements.

Still requiring physical access: board identity inspection, memory/wiring
confirmation, forwarding and ownership checks, first upload/reset, serial
self-test, recovery proof, and every display/touch/sensor/actuator measurement.
Neither build nor upload alone proves firmware self-test, and firmware PASS does
not prove physical peripheral behavior.

## Mechanism references

- ESP-IDF v5.5.2 USB Serial/JTAG console guide:
  <https://docs.espressif.com/projects/esp-idf/en/v5.5.2/esp32s3/api-guides/usb-serial-jtag-console.html>
- esptool reset modes and single-attempt default:
  <https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/advanced-options.html>
- Linux `TIOCEXCL` (used only after capture opens):
  <https://man7.org/linux/man-pages/man2/TIOCEXCL.2const.html>
- Microsoft WSL USB attachment limitations are linked from the root README.

`TIOCEXCL` blocks later non-privileged opens while the capture descriptor is
held; it cannot protect the interval before esptool opens, privileged opens, a
host-side claimant, or a different interface. The cooperating lock and process
scan retain those limitations rather than claiming impossible exclusivity.
