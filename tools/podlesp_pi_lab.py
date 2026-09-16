#!/usr/bin/env python3
"""Repeatable Pi USB lab flash helpers for PodlESP led-pattern (thin host).

Builds stay on the main machine (nix). The Pi only runs esptool + serial capture.
Dry-run is the default. Real flash requires --execute AND env PODLESP_PI_LAB_EXECUTE=1.

Does not install ESP-IDF on the Pi. Does not touch Wi-Fi.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_BY_ID = (
    "/dev/serial/by-id/"
    "usb-Espressif_USB_JTAG_serial_debug_unit_1C:DB:D4:7A:5F:D0-if00"
)
DEFAULT_APP_BIN = "podlesp-led-pattern.bin"
DEFAULT_ESPTOOL = "python -m esptool"
DEFAULT_CHIP = "esp32s3"
DEFAULT_FLASH_BAUD = 460800
DEFAULT_SERIAL_BAUD = 115200

# Accept hyphen or underscore esptool CLI spellings in plans.
LED_TICK_RE = re.compile(rb"PODLESP_LED_TICK sec=(\d+)")
LED_BURST_START_RE = re.compile(
    rb"PODLESP_LED_BURST start hz=(\d+) ms=(\d+) cycles=(\d+)"
)
LED_BURST_END_RE = re.compile(rb"PODLESP_LED_BURST end")
LED_BOOT_RE = re.compile(rb"PODLESP_LED_PATTERN boot ")


class LabError(RuntimeError):
    pass


def require_by_id_path(path: str | Path) -> Path:
    """Refuse globs and non by-id serial paths."""
    text = str(path)
    if any(c in text for c in "*?["):
        raise LabError("serial path must not contain globs")
    p = Path(text)
    if not str(p).startswith("/dev/serial/by-id/"):
        raise LabError("serial path must be under /dev/serial/by-id/")
    if p.name in ("", ".", ".."):
        raise LabError("serial by-id path incomplete")
    return p


def require_esptool_version_ok(version_text: str, minimum: tuple[int, int, int] = (4, 0, 0)) -> tuple[int, int, int]:
    """Parse esptool version string; gate below minimum."""
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", version_text)
    if not m:
        raise LabError(f"cannot parse esptool version from: {version_text!r}")
    ver = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    if ver < minimum:
        raise LabError(f"esptool {ver} below required {minimum}")
    return ver


def translate_flash_files(flash_files: dict) -> dict[str, str]:
    """Map flasher_args.json names to flat nix result layout names."""
    out: dict[str, str] = {}
    for offset, name in flash_files.items():
        base = Path(str(name)).name
        out[str(offset)] = base
    return out


def load_led_flash_plan(
    artifact_dir: Path,
    *,
    port: str | Path,
    esptool_prefix: str = DEFAULT_ESPTOOL,
    chip: str = DEFAULT_CHIP,
    flash_baud: int = DEFAULT_FLASH_BAUD,
    app_bin: str = DEFAULT_APP_BIN,
) -> list[str]:
    """Build esptool argv for led-pattern artifacts (local or remote cwd)."""
    port_path = require_by_id_path(port)
    artifact_dir = Path(artifact_dir)
    args_path = artifact_dir / "flasher_args.json"
    try:
        args = json.loads(args_path.read_text())
    except OSError as exc:
        raise LabError(f"cannot read flasher_args.json: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise LabError(f"invalid flasher_args.json: {exc}") from exc

    extra = args.get("extra_esptool_args") or {}
    if extra.get("chip") not in (None, chip, "esp32s3"):
        raise LabError(f"unexpected chip in flasher_args: {extra.get('chip')}")
    files = args.get("flash_files") or {}
    names = {Path(str(v)).name for v in files.values()}
    if app_bin not in names:
        raise LabError(f"flasher_args missing app bin {app_bin}; got {sorted(names)}")
    for need in ("bootloader.bin", "partition-table.bin", app_bin):
        # partition may be nested name
        pass
    flat = translate_flash_files(files)
    # ensure local files exist when checking on builder
    for offset, fname in flat.items():
        if not (artifact_dir / fname).is_file():
            # allow nested only if translated
            raise LabError(f"missing artifact file {fname} for offset {offset}")

    prefix = shlex.split(esptool_prefix)
    # Prefer modern hyphen flags; esptool 5 accepts both.
    cmd = prefix + [
        "--chip",
        chip,
        "-p",
        str(port_path),
        "-b",
        str(flash_baud),
        "--before",
        "default-reset",
        "--after",
        "hard-reset",
        "write-flash",
        "--flash-mode",
        "dio",
        "--flash-size",
        "2MB",
        "--flash-freq",
        "80m",
    ]
    for offset, fname in sorted(flat.items(), key=lambda kv: int(str(kv[0]), 16)):
        cmd += [str(offset), fname]
    return cmd


def evaluate_led_capture(
    data: bytes,
    *,
    min_ticks: int = 3,
    min_bursts: int = 1,
    expect_burst_hz: int = 2000,
    expect_burst_ms: int = 250,
) -> tuple[str, str]:
    """Return (PASS|FAIL|INCONCLUSIVE, reason) for LED serial markers."""
    if not data:
        return "INCONCLUSIVE", "no serial data"
    ticks = LED_TICK_RE.findall(data)
    bursts = LED_BURST_START_RE.findall(data)
    ends = LED_BURST_END_RE.findall(data)
    if LED_BOOT_RE.search(data) is None and not ticks and not bursts:
        return "INCONCLUSIVE", "missing LED boot/tick/burst markers"
    if bursts:
        for hz, ms, _cyc in bursts:
            if int(hz) != expect_burst_hz or int(ms) != expect_burst_ms:
                return "FAIL", f"burst params hz={hz.decode()} ms={ms.decode()}"
    if len(ticks) >= min_ticks and len(bursts) >= min_bursts and len(ends) >= min_bursts:
        return "PASS", f"ticks={len(ticks)} bursts={len(bursts)}"
    return (
        "INCONCLUSIVE",
        f"ticks={len(ticks)} bursts={len(bursts)} ends={len(ends)} "
        f"(need ticks>={min_ticks} bursts>={min_bursts})",
    )


def build_remote_flash_script(
    *,
    remote_dir: str,
    port: str,
    esptool_cmd: str,
    flash_argv: list[str],
    capture_seconds: float = 22.0,
) -> str:
    """Shell script body run on the Pi after bins are present in remote_dir."""
    # flash_argv already includes esptool prefix; re-join safely
    flash_line = " ".join(shlex.quote(a) for a in flash_argv)
    port_q = shlex.quote(port)
    dir_q = shlex.quote(remote_dir)
    return f"""set -euo pipefail
cd {dir_q}
test -e {port_q} || {{ echo "STOP: serial missing: {port}"; exit 3; }}
{flash_line}
python3 - <<'PY'
import serial, time, sys
port = {port!r}
ser = serial.Serial(port, {DEFAULT_SERIAL_BAUD}, timeout=0.5)
t0 = time.time()
buf = b""
while time.time() - t0 < {capture_seconds}:
    chunk = ser.read(4096)
    if chunk:
        buf += chunk
        sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()
ser.close()
open("/tmp/podlesp-led-capture.bin", "wb").write(buf)
print("\\nPODLESP_CAPTURE_BYTES", len(buf), flush=True)
PY
"""


def build_scp_and_ssh_plan(
    *,
    artifact_dir: Path,
    ssh_host: str,
    ssh_user: str = "podledges",
    ssh_identity: str | None = None,
    remote_dir: str = "~/podlesp-led-flash",
    port: str = DEFAULT_BY_ID,
    esptool_prefix: str = (
        "$HOME/.local/share/podlesp/venvs/esptool-5.1.0/bin/python -m esptool"
    ),
) -> dict:
    """Describe main-machine transfer + remote flash (no execution)."""
    port_path = require_by_id_path(port)
    artifact_dir = Path(artifact_dir)
    # Remote flash cwd is remote_dir; argv uses bare filenames.
    flash_cmd = load_led_flash_plan(
        artifact_dir,
        port=port_path,
        esptool_prefix=esptool_prefix,
    )
    bins = ["bootloader.bin", "partition-table.bin", DEFAULT_APP_BIN, "flasher_args.json"]
    for name in bins:
        if not (artifact_dir / name).is_file() and name != "flasher_args.json":
            raise LabError(f"missing {name} in {artifact_dir}")
    scp_files = [str(artifact_dir / n) for n in bins if (artifact_dir / n).is_file()]
    ssh = ["ssh"]
    scp = ["scp"]
    if ssh_identity:
        ssh += ["-i", ssh_identity]
        scp += ["-i", ssh_identity]
    target = f"{ssh_user}@{ssh_host}"
    return {
        "scp": scp + scp_files + [f"{target}:{remote_dir}/"],
        "ssh_mkdir": ssh + [target, f"mkdir -p {remote_dir}"],
        "flash_argv": flash_cmd,
        "remote_script": build_remote_flash_script(
            remote_dir=remote_dir if not remote_dir.startswith("~") else remote_dir,
            port=str(port_path),
            esptool_cmd=esptool_prefix,
            flash_argv=flash_cmd,
        ),
        "port": str(port_path),
        "target": target,
    }


def execution_allowed(execute_flag: bool) -> bool:
    return bool(execute_flag) and os.environ.get("PODLESP_PI_LAB_EXECUTE") == "1"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan-flash", help="print scp/ssh/esptool plan (dry-run)")
    plan.add_argument("--artifact-dir", type=Path, required=True)
    plan.add_argument("--host", default="192.168.0.14")
    plan.add_argument("--user", default="podledges")
    plan.add_argument("--identity", default=str(Path.home() / ".ssh" / "podlesp_pi_ed25519"))
    plan.add_argument("--port", default=DEFAULT_BY_ID)
    plan.add_argument(
        "--esptool-prefix",
        default="$HOME/.local/share/podlesp/venvs/esptool-5.1.0/bin/python -m esptool",
    )

    parse = sub.add_parser("parse-capture", help="evaluate a captured serial log file")
    parse.add_argument("path", type=Path)
    parse.add_argument("--min-ticks", type=int, default=3)
    parse.add_argument("--min-bursts", type=int, default=1)

    ver = sub.add_parser("check-esptool-version", help="gate esptool version text")
    ver.add_argument("text")

    miss = sub.add_parser("require-port", help="validate by-id path string (no open)")
    miss.add_argument("path")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "plan-flash":
            plan = build_scp_and_ssh_plan(
                artifact_dir=args.artifact_dir,
                ssh_host=args.host,
                ssh_user=args.user,
                ssh_identity=args.identity or None,
                port=args.port,
                esptool_prefix=args.esptool_prefix,
            )
            print("DRY RUN plan (no transfer/flash):")
            print("mkdir:", " ".join(plan["ssh_mkdir"]))
            print("scp:", " ".join(plan["scp"]))
            print("flash_argv:", " ".join(plan["flash_argv"]))
            print("port:", plan["port"])
            if execution_allowed(False):
                pass
            print("Real flash requires separate operator steps with PODLESP_PI_LAB_EXECUTE=1")
            return 0
        if args.command == "parse-capture":
            data = args.path.read_bytes()
            outcome, reason = evaluate_led_capture(
                data, min_ticks=args.min_ticks, min_bursts=args.min_bursts
            )
            print(f"{outcome}: {reason}")
            return 0 if outcome == "PASS" else 2
        if args.command == "check-esptool-version":
            ver = require_esptool_version_ok(args.text)
            print("ok", ".".join(map(str, ver)))
            return 0
        if args.command == "require-port":
            print(require_by_id_path(args.path))
            return 0
        raise LabError(f"unknown command {args.command}")
    except LabError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
