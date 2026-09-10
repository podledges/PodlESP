#!/usr/bin/env python3
"""Guarded build/flash/self-test workflow for PodlESP.

Only build opens no hardware. Flash and test-board are dry-run unless --execute is
present, and execution additionally requires a scoped, unexpired approval file.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import select
import stat
import subprocess
import sys
import termios
import time
import tomllib
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_FILES = (
    "bootloader.bin",
    "partition-table.bin",
    "podlesp-smoke.bin",
    "podlesp-smoke.elf",
    "flasher_args.json",
)
MAX_SECONDS = 20.0
MAX_BYTES = 65_536
SUPPORTED_BAUDS = {9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600}
REQUIRED_BOARD_FIELDS = (
    "manufacturer",
    "model",
    "sku",
    "revision",
    "memory_configuration",
    "wiring_source",
    "forwarding_decision",
    "firmware_decision",
    "partition_decision",
    "security_state_decision",
    "recovery_plan",
    "device_by_path",
    "usb_serial_sha256",
    "usb_vid",
    "usb_pid",
    "usb_manufacturer",
    "usb_product",
    "fixture_flash_size",
    "baud",
    "flash_baud",
)
UNKNOWN = re.compile(r"(?:UNKNOWN|REPLACE|UNCONFIRMED|TBD|<[^>]+>)", re.I)


class WorkflowError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class DeviceIdentity:
    node: Path
    rdev: int
    usb_path: Path
    vid: str
    pid: str
    manufacturer: str
    product: str
    serial_sha256: str

    @property
    def public_digest(self) -> str:
        material = "\0".join(
            (self.vid, self.pid, self.manufacturer, self.product, self.serial_sha256)
        )
        return hashlib.sha256(material.encode()).hexdigest()


@dataclasses.dataclass(frozen=True)
class CaptureResult:
    outcome: str
    reason: str
    data: bytes
    elapsed_seconds: float
    boot_nonce: str | None = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load_toml(path: Path) -> dict:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise WorkflowError(f"cannot read {path}: {exc}") from exc


def validate_board_config(path: Path) -> tuple[dict, str]:
    cfg = load_toml(path)
    missing = [key for key in REQUIRED_BOARD_FIELDS if key not in cfg]
    if missing:
        raise WorkflowError("board config missing: " + ", ".join(missing))
    unknown = [key for key in REQUIRED_BOARD_FIELDS if UNKNOWN.search(str(cfg[key]))]
    if unknown:
        raise WorkflowError("unconfirmed board config values: " + ", ".join(unknown))
    if str(cfg.get("target")) != "esp32s3":
        raise WorkflowError("board target must be esp32s3")
    if str(cfg.get("safety_guarantee")) != "cooperating-lock-and-snapshot-accepted":
        raise WorkflowError("safety_guarantee decision is absent or unsupported")
    device = Path(str(cfg["device_by_path"]))
    if not str(device).startswith("/dev/serial/by-path/") or any(c in str(device) for c in "*?["):
        raise WorkflowError("device_by_path must be one exact /dev/serial/by-path entry")
    serial_hash = str(cfg["usb_serial_sha256"]).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", serial_hash):
        raise WorkflowError("usb_serial_sha256 must be a 64-character SHA-256")
    baud = int(cfg["baud"])
    flash_baud = int(cfg["flash_baud"])
    if baud not in SUPPORTED_BAUDS:
        raise WorkflowError(f"unsupported configured baud: {baud}")
    if flash_baud not in SUPPORTED_BAUDS:
        raise WorkflowError(f"unsupported configured flash_baud: {flash_baud}")
    raw = path.read_bytes()
    return cfg, hashlib.sha256(raw).hexdigest()


def run_build(manifest_path: Path, runner: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> dict:
    command = [
        "nix", "build", ".#smoke", "--no-link", "--print-out-paths",
        "--print-build-logs", "--max-jobs", "2", "--cores", "2",
    ]
    result = runner(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise WorkflowError(f"pinned Nix build failed ({result.returncode})")
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise WorkflowError("Nix build did not return exactly one output path")
    artifact_dir = Path(lines[0]).resolve()
    if not str(artifact_dir).startswith("/nix/store/"):
        raise WorkflowError("build output is not an immutable Nix store path")
    hashes = {}
    for name in ARTIFACT_FILES:
        path = artifact_dir / name
        if not path.is_file():
            raise WorkflowError(f"build output missing {name}")
        hashes[name] = sha256_file(path)
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    if dirty:
        raise WorkflowError("refusing manifest for a dirty tracked source tree")
    flasher = json.loads((artifact_dir / "flasher_args.json").read_text())
    manifest = {
        "schema": 1,
        "kind": "generic-esp32s3-self-test-fixture",
        "source_revision": revision,
        "flake_lock_sha256": sha256_file(ROOT / "flake.lock"),
        "artifact_dir": str(artifact_dir),
        "files": hashes,
        "flash_settings": flasher.get("flash_settings"),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(canonical_json(manifest))
    print(f"built generic ESP32-S3 fixture: {artifact_dir}")
    print(f"artifact manifest: {manifest_path} sha256={sha256_file(manifest_path)}")
    print("Compilation is not certification of the configured physical board.")
    return manifest


def verify_artifact_hashes(artifact_dir: Path, hashes: dict[str, str]) -> None:
    if set(hashes) != set(ARTIFACT_FILES):
        raise WorkflowError("artifact file set is incomplete or unexpected")
    for name, expected in hashes.items():
        file_path = artifact_dir / name
        if not file_path.is_file() or sha256_file(file_path) != expected:
            raise WorkflowError(f"artifact mismatch: {name}")


def validate_manifest(path: Path) -> tuple[dict, str]:
    try:
        manifest = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowError(f"cannot read artifact manifest: {exc}") from exc
    if manifest.get("schema") != 1 or manifest.get("kind") != "generic-esp32s3-self-test-fixture":
        raise WorkflowError("unsupported artifact manifest")
    if manifest.get("flake_lock_sha256") != sha256_file(ROOT / "flake.lock"):
        raise WorkflowError("artifact was built with a different flake.lock")
    current_revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.strip()
    if manifest.get("source_revision") != current_revision:
        raise WorkflowError("artifact source revision is stale or mismatched")
    artifact_dir = Path(str(manifest.get("artifact_dir", ""))).resolve()
    if not str(artifact_dir).startswith("/nix/store/"):
        raise WorkflowError("artifact directory is not in the Nix store")
    verify_artifact_hashes(artifact_dir, manifest.get("files", {}))
    return manifest, sha256_file(path)


def _read_attr(path: Path, name: str) -> str:
    try:
        return (path / name).read_text().strip()
    except OSError as exc:
        raise WorkflowError(f"cannot read USB identity {path / name}: {exc}") from exc


def inspect_identity(cfg: dict, sys_tty_root: Path = Path("/sys/class/tty")) -> DeviceIdentity:
    configured = Path(str(cfg["device_by_path"]))
    try:
        node = configured.resolve(strict=True)
        node_stat = node.stat()
    except OSError as exc:
        raise WorkflowError(f"configured device is unavailable: {configured}: {exc}") from exc
    if not stat.S_ISCHR(node_stat.st_mode):
        raise WorkflowError("configured device does not resolve to a character device")
    tty_link = sys_tty_root / node.name
    try:
        resolved_tty = tty_link.resolve(strict=True)
    except OSError as exc:
        raise WorkflowError(f"no sysfs identity for {node.name}: {exc}") from exc
    usb_path = next((p for p in (resolved_tty, *resolved_tty.parents) if (p / "idVendor").is_file()), None)
    if usb_path is None:
        raise WorkflowError("serial node has no USB identity parent")
    serial = _read_attr(usb_path, "serial")
    identity = DeviceIdentity(
        node=node,
        rdev=node_stat.st_rdev,
        usb_path=usb_path,
        vid=_read_attr(usb_path, "idVendor").lower(),
        pid=_read_attr(usb_path, "idProduct").lower(),
        manufacturer=_read_attr(usb_path, "manufacturer"),
        product=_read_attr(usb_path, "product"),
        serial_sha256=hashlib.sha256(serial.encode()).hexdigest(),
    )
    expected = {
        "vid": str(cfg["usb_vid"]).lower().removeprefix("0x"),
        "pid": str(cfg["usb_pid"]).lower().removeprefix("0x"),
        "manufacturer": str(cfg["usb_manufacturer"]),
        "product": str(cfg["usb_product"]),
        "serial_sha256": str(cfg["usb_serial_sha256"]).lower(),
    }
    verify_identity(identity, expected)
    matches = 0
    for tty in sys_tty_root.glob("ttyACM*"):
        try:
            resolved = tty.resolve(strict=True)
            parent = next((p for p in (resolved, *resolved.parents) if (p / "idVendor").is_file()), None)
            if parent and hashlib.sha256(_read_attr(parent, "serial").encode()).hexdigest() == expected["serial_sha256"]:
                matches += 1
        except (OSError, WorkflowError):
            continue
    require_unique_identity(matches)
    return identity


def require_unique_identity(matches: int) -> None:
    if matches != 1:
        raise WorkflowError(f"device identity is ambiguous ({matches} matching serial endpoints)")


def verify_identity(identity: DeviceIdentity, expected: dict[str, str]) -> None:
    changed = [key for key, value in expected.items() if getattr(identity, key) != value]
    if changed:
        raise WorkflowError("device identity mismatch: " + ", ".join(changed))


def require_unchanged_identity(before: DeviceIdentity, after: DeviceIdentity) -> None:
    if before != after:
        raise WorkflowError("device identity changed during operation")


def find_conflicts(identity: DeviceIdentity, proc_root: Path = Path("/proc")) -> tuple[list[str], int]:
    owners: set[str] = set()
    inaccessible = 0
    for proc in proc_root.glob("[0-9]*"):
        try:
            fds = list((proc / "fd").iterdir())
        except FileNotFoundError:
            continue
        except PermissionError:
            inaccessible += 1
            continue
        for fd in fds:
            try:
                info = fd.stat()
                if stat.S_ISCHR(info.st_mode) and info.st_rdev == identity.rdev:
                    owners.add(proc.name)
            except FileNotFoundError:
                continue
            except PermissionError:
                inaccessible += 1
                break
    return sorted(owners), inaccessible


def identity_config_digest(cfg: dict) -> str:
    fields = {
        key: cfg[key]
        for key in (
            "manufacturer", "model", "sku", "revision", "device_by_path",
            "usb_serial_sha256", "usb_vid", "usb_pid", "usb_manufacturer", "usb_product",
        )
    }
    return hashlib.sha256(canonical_json(fields)).hexdigest()


def validate_approval(path: Path, cfg: dict, cfg_hash: str, manifest_hash: str) -> dict:
    approval = load_toml(path)
    required = {
        "operation": "standard-flash-hard-reset",
        "artifact_manifest_sha256": manifest_hash,
        "board_config_sha256": cfg_hash,
        "device_identity_digest": identity_config_digest(cfg),
        "acknowledge_partition_overwrite": True,
    }
    wrong = [key for key, value in required.items() if approval.get(key) != value]
    if wrong:
        raise WorkflowError("approval is absent or out of scope: " + ", ".join(wrong))
    for key in ("approval_id", "approved_by", "approved_at", "expires_at"):
        if not approval.get(key) or UNKNOWN.search(str(approval[key])):
            raise WorkflowError(f"approval missing concrete {key}")
    try:
        expires = dt.datetime.fromisoformat(str(approval["expires_at"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise WorkflowError("approval expires_at is not ISO-8601") from exc
    if expires.tzinfo is None or expires <= dt.datetime.now(dt.timezone.utc):
        raise WorkflowError("approval has expired")
    consumed = ROOT / ".podlesp" / "consumed-approvals" / hashlib.sha256(str(approval["approval_id"]).encode()).hexdigest()
    if consumed.exists():
        raise WorkflowError("approval was already consumed")
    approval["_consumed_path"] = consumed
    return approval


def load_flash_plan(manifest: dict, cfg: dict) -> list[str]:
    artifact_dir = Path(manifest["artifact_dir"])
    args = json.loads((artifact_dir / "flasher_args.json").read_text())
    extra = args.get("extra_esptool_args", {})
    if extra != {"after": "hard_reset", "before": "default_reset", "stub": True, "chip": "esp32s3"}:
        raise WorkflowError("artifact requests unexpected esptool behavior")
    settings = args.get("flash_settings")
    if settings != manifest.get("flash_settings") or settings.get("flash_size") != str(cfg["fixture_flash_size"]):
        raise WorkflowError("artifact flash settings do not match board decision")
    expected_names = {"bootloader/bootloader.bin", "podlesp-smoke.bin", "partition_table/partition-table.bin"}
    if set(args.get("flash_files", {}).values()) != expected_names:
        raise WorkflowError("unexpected flash file layout")
    translated = {
        "bootloader/bootloader.bin": "bootloader.bin",
        "partition_table/partition-table.bin": "partition-table.bin",
        "podlesp-smoke.bin": "podlesp-smoke.bin",
    }
    command = [
        "esptool.py", "--chip", "esp32s3", "--port", str(cfg["device_by_path"]),
        "--baud", str(int(cfg["flash_baud"])), "--before", "default_reset",
        "--after", "hard_reset", "write_flash",
    ] + list(args["write_flash_args"])
    for offset, name in sorted(args["flash_files"].items(), key=lambda pair: int(pair[0], 16)):
        command += [offset, str(artifact_dir / translated[name])]
    return command


def execute_flash_command(command: list[str], runner: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> int:
    env = os.environ.copy()
    env["ESPTOOL_OPEN_PORT_ATTEMPTS"] = "1"
    env["ESPTOOL_CFGFILE"] = os.devnull
    return runner(command, cwd=ROOT, env=env, check=False).returncode


def acquire_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        handle.close()
        if exc.errno in (errno.EACCES, errno.EAGAIN):
            raise WorkflowError("cooperating board lock is held") from exc
        raise
    return handle


def evaluate_capture(chunks: Iterable[bytes], elapsed: float = 0.0) -> CaptureResult:
    data = bytearray()
    reason = "stream ended/disconnected"
    for chunk in chunks:
        if chunk is None:  # type: ignore[comparison-overlap]
            reason = "timeout"
            break
        if chunk == b"":
            reason = "disconnect"
            break
        remaining = MAX_BYTES - len(data)
        data.extend(chunk[:remaining])
        text = data.decode("utf-8", "replace")
        fail = re.search(r"PODLESP_SELF_TEST_FAIL ([0-9a-f]{16})\b", text)
        passed = re.search(r"PODLESP_SELF_TEST_PASS ([0-9a-f]{16})\b", text)
        boot = re.search(r"PODLESP_BOOT ([0-9a-f]{16})\b", text)
        if fail:
            return CaptureResult("FAIL", "firmware reported FAIL", bytes(data), elapsed, fail.group(1))
        if passed:
            if not boot or boot.group(1) != passed.group(1):
                return CaptureResult("INCONCLUSIVE", "PASS lacks matching current-run boot marker", bytes(data), elapsed)
            return CaptureResult("PASS", "matching boot and self-test PASS markers", bytes(data), elapsed, passed.group(1))
        if len(data) >= MAX_BYTES:
            reason = "byte cap reached"
            break
    if not data:
        detail = "silence" if reason in ("timeout", "stream ended/disconnected") else reason
    elif b"PODLESP_BOOT " not in data:
        detail = f"{reason}; missing boot marker or undecodable output"
    else:
        detail = f"{reason}; missing PASS/FAIL marker"
    return CaptureResult("INCONCLUSIVE", detail, bytes(data), elapsed)


def capture_serial(identity: DeviceIdentity, baud: int, now: Callable[[], float] = time.monotonic) -> CaptureResult:
    baud_constant = getattr(termios, f"B{baud}", None)
    if baud_constant is None:
        raise WorkflowError(f"termios does not support configured baud {baud}")
    fd = os.open(identity.node, os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
    started = now()
    data = bytearray()
    reason = "timeout"
    try:
        fcntl.ioctl(fd, termios.TIOCEXCL)
        attrs = termios.tcgetattr(fd)
        attrs[0] = 0
        attrs[1] = 0
        attrs[2] = termios.CS8 | termios.CLOCAL | termios.CREAD
        attrs[3] = 0
        attrs[4] = baud_constant
        attrs[5] = baud_constant
        attrs[6][termios.VMIN] = 0
        attrs[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        termios.tcflush(fd, termios.TCIFLUSH)
        while len(data) < MAX_BYTES:
            elapsed = now() - started
            if elapsed >= MAX_SECONDS:
                reason = "timeout"
                break
            ready, _, _ = select.select([fd], [], [], min(0.25, MAX_SECONDS - elapsed))
            if not ready:
                continue
            try:
                chunk = os.read(fd, min(4096, MAX_BYTES - len(data)))
            except OSError as exc:
                reason = f"serial error: {exc}"
                break
            if not chunk:
                reason = "disconnect"
                break
            data.extend(chunk)
            result = evaluate_capture([bytes(data)], now() - started)
            if result.outcome in ("PASS", "FAIL"):
                return result
        if len(data) >= MAX_BYTES:
            reason = "byte cap reached"
        sentinel: list[bytes | None] = [bytes(data)] if data else []
        sentinel.append(b"" if reason == "disconnect" else None)
        result = evaluate_capture(sentinel, now() - started)
        if reason.startswith("serial error"):
            return dataclasses.replace(result, reason=reason)
        if reason == "byte cap reached":
            return dataclasses.replace(result, reason="byte cap reached; missing conclusive markers")
        return result
    finally:
        os.close(fd)


def escaped_serial(data: bytes) -> str:
    text = data.decode("utf-8", "backslashreplace")
    text = re.sub(r"\b[0-9A-Fa-f]{12}\b", "<redacted-hex-id>", text)
    return text.encode("unicode_escape").decode("ascii")


def write_result(result: CaptureResult, manifest_hash: str, cfg_hash: str, identity: DeviceIdentity, upload_ok: bool) -> Path:
    run_dir = ROOT / ".podlesp" / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = run_dir / f"{stamp}-{manifest_hash[:12]}.json"
    record = {
        "schema": 1,
        "artifact_manifest_sha256": manifest_hash,
        "board_config_sha256": cfg_hash,
        "device_identity_digest": identity.public_digest,
        "upload": "SUCCESS" if upload_ok else "NOT_RUN_OR_FAILED",
        "firmware_self_test": result.outcome,
        "reason": result.reason,
        "elapsed_seconds": round(result.elapsed_seconds, 3),
        "captured_bytes": len(result.data),
        "boot_nonce": result.boot_nonce,
        "serial_escaped": escaped_serial(result.data),
        "physical_measurements": "NOT_PERFORMED",
    }
    path.write_bytes(canonical_json(record))
    return path


def preflight(args, execute: bool = False):
    cfg, cfg_hash = validate_board_config(args.board_config)
    manifest, manifest_hash = validate_manifest(args.manifest)
    command = load_flash_plan(manifest, cfg)
    print("validated artifact/config; planned fixed command:")
    print(f"artifact_manifest_sha256={manifest_hash}")
    print(f"board_config_sha256={cfg_hash}")
    print(f"device_identity_digest={identity_config_digest(cfg)}")
    print(" ".join(command))
    print("Normal write_flash overwrites/erases sectors containing bootloader, partition table, and app; it is destructive.")
    if not execute:
        print("DRY RUN: no device opened, reset, transmission, or flash performed.")
        return None
    approval = validate_approval(args.approval, cfg, cfg_hash, manifest_hash)
    lock = acquire_lock(ROOT / ".podlesp" / "locks" / "board.lock")
    try:
        identity = inspect_identity(cfg)
        owners, inaccessible = find_conflicts(identity)
        if owners:
            raise WorkflowError("known serial conflict from PID(s): " + ", ".join(owners))
        print(f"conflict snapshot: no visible owners; {inaccessible} process(es) inaccessible (not proof of exclusivity)")
        if inspect_identity(cfg) != identity:
            raise WorkflowError("device identity changed during preflight")
        approval["_consumed_path"].parent.mkdir(parents=True, exist_ok=True)
        approval["_consumed_path"].write_text(dt.datetime.now(dt.timezone.utc).isoformat() + "\n")
        returncode = execute_flash_command(command)
        if returncode:
            log = write_result(
                CaptureResult("NOT_RUN", f"upload command failed ({returncode})", b"", 0.0),
                manifest_hash, cfg_hash, identity, False,
            )
            raise WorkflowError(f"esptool upload failed ({returncode}); log={log}")
        if inspect_identity(cfg).public_digest != identity.public_digest:
            raise WorkflowError("device identity changed after upload/reset")
        log = write_result(
            CaptureResult("NOT_RUN", "standalone flash has no firmware self-test", b"", 0.0),
            manifest_hash, cfg_hash, identity, True,
        )
        print(f"upload: SUCCESS; firmware self-test: NOT_RUN; log={log}")
        return cfg, cfg_hash, manifest_hash, identity
    finally:
        lock.close()


def execute_test_board(args) -> None:
    cfg, cfg_hash = validate_board_config(args.board_config)
    manifest, manifest_hash = validate_manifest(args.manifest)
    command = load_flash_plan(manifest, cfg)
    print("validated artifact/config; planned fixed flash followed by bounded read-only capture:")
    print(f"artifact_manifest_sha256={manifest_hash}")
    print(f"board_config_sha256={cfg_hash}")
    print(f"device_identity_digest={identity_config_digest(cfg)}")
    print(" ".join(command))
    if not args.execute:
        print("DRY RUN: no device opened, reset, transmission, or flash performed.")
        return
    approval = validate_approval(args.approval, cfg, cfg_hash, manifest_hash)
    lock = acquire_lock(ROOT / ".podlesp" / "locks" / "board.lock")
    upload_ok = False
    identity = None
    try:
        identity = inspect_identity(cfg)
        owners, inaccessible = find_conflicts(identity)
        if owners:
            raise WorkflowError("known serial conflict from PID(s): " + ", ".join(owners))
        print(f"conflict snapshot: no visible owners; {inaccessible} process(es) inaccessible (not proof of exclusivity)")
        if inspect_identity(cfg) != identity:
            raise WorkflowError("device identity changed during preflight")
        approval["_consumed_path"].parent.mkdir(parents=True, exist_ok=True)
        approval["_consumed_path"].write_text(dt.datetime.now(dt.timezone.utc).isoformat() + "\n")
        returncode = execute_flash_command(command)
        if returncode:
            log = write_result(
                CaptureResult("NOT_RUN", f"upload command failed ({returncode})", b"", 0.0),
                manifest_hash, cfg_hash, identity, False,
            )
            raise WorkflowError(f"esptool upload failed ({returncode}); log={log}")
        upload_ok = True
        current = inspect_identity(cfg)
        if current.public_digest != identity.public_digest:
            raise WorkflowError("device identity changed after upload/reset")
        result = capture_serial(current, int(cfg["baud"]))
        log = write_result(result, manifest_hash, cfg_hash, current, upload_ok)
        print(f"result: {result.outcome}: {result.reason}; log={log}")
        if result.outcome != "PASS":
            raise WorkflowError("board self-test did not pass")
    finally:
        lock.close()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="run the pinned build without hardware access")
    build.add_argument("--manifest", type=Path, default=ROOT / ".podlesp" / "artifact.json")
    for name in ("flash", "test-board"):
        cmd = sub.add_parser(name, help=f"dry-run {name}; --execute requires external approval")
        cmd.add_argument("--board-config", type=Path, default=ROOT / ".podlesp" / "board.toml")
        cmd.add_argument("--manifest", type=Path, default=ROOT / ".podlesp" / "artifact.json")
        cmd.add_argument("--approval", type=Path, default=ROOT / ".podlesp" / "approval.toml")
        cmd.add_argument("--execute", action="store_true", help="perform approved hardware operation; never implies permission")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "build":
            run_build(args.manifest)
        elif args.command == "flash":
            preflight(args, args.execute)
        else:
            execute_test_board(args)
        return 0
    except (WorkflowError, subprocess.SubprocessError) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
