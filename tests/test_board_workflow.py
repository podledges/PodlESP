import datetime as dt
import fcntl
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import podlesp_board as workflow


class BoardWorkflowTests(unittest.TestCase):
    def config(self):
        return {
            "target": "esp32s3",
            "manufacturer": "Maker",
            "model": "Model",
            "sku": "123",
            "revision": "A",
            "memory_configuration": "2 MiB flash, no PSRAM used by fixture",
            "wiring_source": "https://example.invalid/schematic-a",
            "forwarding_decision": "one WSL distribution, host monitor closed",
            "firmware_decision": "generic PodlESP smoke self-test approved",
            "partition_decision": "replace bootloader, table, and app sectors",
            "security_state_decision": "confirmed development unit, encryption and secure boot disabled",
            "recovery_plan": "restore locally archived known-good image with reviewed tool",
            "safety_guarantee": "cooperating-lock-and-snapshot-accepted",
            "device_by_path": "/dev/serial/by-path/pci-test",
            "usb_serial_sha256": "a" * 64,
            "usb_vid": "303a",
            "usb_pid": "1001",
            "usb_manufacturer": "Espressif",
            "usb_product": "USB JTAG/serial debug unit",
            "fixture_flash_size": "2MB",
            "baud": 115200,
            "flash_baud": 460800,
        }

    def identity(self, **changes):
        values = dict(
            node=Path("/dev/null"), rdev=os.stat("/dev/null").st_rdev,
            usb_path=Path("/sys/fake"), vid="303a", pid="1001",
            manufacturer="Espressif", product="USB JTAG/serial debug unit",
            serial_sha256="a" * 64,
        )
        values.update(changes)
        return workflow.DeviceIdentity(**values)

    def test_defaults_do_not_execute_hardware(self):
        parsed = workflow.parser().parse_args(["flash"])
        self.assertFalse(parsed.execute)
        parsed = workflow.parser().parse_args(["test-board"])
        self.assertFalse(parsed.execute)
        with self.assertRaises(SystemExit):
            workflow.parser().parse_args(["flash", "--execute", "erase-flash"])
        args = mock.Mock(board_config=Path("board"), manifest=Path("manifest"))
        with mock.patch.object(workflow, "validate_board_config", return_value=(self.config(), "c" * 64)), \
             mock.patch.object(workflow, "validate_manifest", return_value=({"artifact_dir": "/nix/store/fake"}, "m" * 64)), \
             mock.patch.object(workflow, "load_flash_plan", return_value=["esptool.py"]), \
             mock.patch.object(workflow, "validate_approval") as approval, \
             mock.patch.object(workflow, "inspect_identity") as identity, \
             mock.patch.object(workflow, "execute_flash_command") as execute:
            workflow.preflight(args, execute=False)
            approval.assert_not_called()
            identity.assert_not_called()
            execute.assert_not_called()

    def test_unknown_config_stops_hardware_preparation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "board.toml"
            path.write_text('target="esp32s3"\nmanufacturer="UNKNOWN"\n')
            with self.assertRaisesRegex(workflow.WorkflowError, "missing|unconfirmed"):
                workflow.validate_board_config(path)

    def test_authorization_absent_and_out_of_scope(self):
        cfg = self.config()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = root / "missing.toml"
            with self.assertRaisesRegex(workflow.WorkflowError, "cannot read"):
                workflow.validate_approval(missing, cfg, "c" * 64, "m" * 64)
            approval = root / "approval.toml"
            future = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5)).isoformat()
            approval.write_text(
                'approval_id="one"\napproved_by="captain"\n'
                f'approved_at="2026-01-01T00:00:00Z"\nexpires_at="{future}"\n'
                'operation="standard-flash-hard-reset"\n'
                f'artifact_manifest_sha256="{"0" * 64}"\n'
                f'board_config_sha256="{"c" * 64}"\n'
                f'device_identity_digest="{workflow.identity_config_digest(cfg)}"\n'
                'acknowledge_partition_overwrite=true\n'
            )
            with self.assertRaisesRegex(workflow.WorkflowError, "out of scope"):
                workflow.validate_approval(approval, cfg, "c" * 64, "m" * 64)

    def test_device_mismatch_and_changed_identity(self):
        expected = {
            "vid": "303a", "pid": "1001", "manufacturer": "Espressif",
            "product": "USB JTAG/serial debug unit", "serial_sha256": "a" * 64,
        }
        with self.assertRaisesRegex(workflow.WorkflowError, "mismatch"):
            workflow.verify_identity(self.identity(pid="9999"), expected)
        with self.assertRaisesRegex(workflow.WorkflowError, "changed"):
            workflow.require_unchanged_identity(self.identity(), self.identity(rdev=123))

    def test_ambiguous_identity_is_rejected(self):
        with self.assertRaisesRegex(workflow.WorkflowError, "ambiguous"):
            workflow.require_unique_identity(2)
        with self.assertRaisesRegex(workflow.WorkflowError, "ambiguous"):
            workflow.require_unique_identity(0)
        workflow.require_unique_identity(1)

    def test_contention_snapshot_finds_known_owner(self):
        identity = self.identity()
        with tempfile.TemporaryDirectory() as directory:
            proc = Path(directory)
            fd_dir = proc / "42" / "fd"
            fd_dir.mkdir(parents=True)
            (fd_dir / "3").symlink_to("/dev/null")
            owners, inaccessible = workflow.find_conflicts(identity, proc)
            self.assertEqual(owners, ["42"])
            self.assertEqual(inaccessible, 0)

    def test_artifact_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory)
            hashes = {}
            for name in workflow.ARTIFACT_FILES:
                (artifact / name).write_bytes(name.encode())
                hashes[name] = workflow.sha256_file(artifact / name)
            hashes["podlesp-smoke.bin"] = "0" * 64
            with self.assertRaisesRegex(workflow.WorkflowError, "artifact mismatch"):
                workflow.verify_artifact_hashes(artifact, hashes)

    def test_build_and_flash_command_failure(self):
        failed = subprocess.CompletedProcess([], 9, "", "offline failure")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(workflow.WorkflowError, "build failed"):
                workflow.run_build(Path(directory) / "manifest.json", runner=lambda *a, **k: failed)
        observed = {}
        def fake_flash(command, **kwargs):
            observed.update(kwargs)
            return failed
        self.assertEqual(workflow.execute_flash_command(["esptool.py"], fake_flash), 9)
        self.assertEqual(observed["env"]["ESPTOOL_OPEN_PORT_ATTEMPTS"], "1")
        self.assertEqual(observed["env"]["ESPTOOL_CFGFILE"], os.devnull)

    def test_serial_pass_fail_missing_marker_silence_timeout_disconnect_and_cap(self):
        nonce = b"0123456789abcdef"
        passed = workflow.evaluate_capture([b"PODLESP_BOOT " + nonce + b"\nPODLESP_SELF_TEST_PASS " + nonce + b"\n"])
        self.assertEqual(passed.outcome, "PASS")
        failed = workflow.evaluate_capture([b"PODLESP_SELF_TEST_FAIL " + nonce + b"\n"])
        self.assertEqual(failed.outcome, "FAIL")
        stale = workflow.evaluate_capture([b"PODLESP_SELF_TEST_PASS " + nonce + b"\n"])
        self.assertEqual(stale.outcome, "INCONCLUSIVE")
        self.assertIn("matching", stale.reason)
        silence = workflow.evaluate_capture([None])
        self.assertEqual((silence.outcome, silence.reason), ("INCONCLUSIVE", "silence"))
        disconnected = workflow.evaluate_capture([b""])
        self.assertEqual(disconnected.reason, "disconnect")
        garbage = workflow.evaluate_capture([b"\xffgarbage", None])
        self.assertIn("undecodable", garbage.reason)
        capped = workflow.evaluate_capture([b"x" * (workflow.MAX_BYTES + 1)])
        self.assertEqual(len(capped.data), workflow.MAX_BYTES)
        self.assertIn("byte cap", capped.reason)

    def test_lock_released_after_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "board.lock"
            handle = workflow.acquire_lock(lock_path)
            try:
                with self.assertRaisesRegex(workflow.WorkflowError, "held"):
                    workflow.acquire_lock(lock_path)
            finally:
                handle.close()
            replacement = workflow.acquire_lock(lock_path)
            replacement.close()

    def test_capture_closes_fd_on_error(self):
        identity = self.identity()
        with mock.patch.object(workflow.os, "open", return_value=77), \
             mock.patch.object(workflow.fcntl, "ioctl", side_effect=OSError("offline endpoint")), \
             mock.patch.object(workflow.os, "close") as close:
            with self.assertRaises(OSError):
                workflow.capture_serial(identity, 115200)
            close.assert_called_once_with(77)


if __name__ == "__main__":
    unittest.main()
