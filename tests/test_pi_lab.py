#!/usr/bin/env python3
"""Offline tests for Pi lab led-pattern flash helpers."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import podlesp_pi_lab as lab


class PiLabTests(unittest.TestCase):
    def artifact_dir(self, root: Path, app: str = "podlesp-led-pattern.bin") -> Path:
        d = root / "out"
        d.mkdir()
        (d / "bootloader.bin").write_bytes(b"BL")
        (d / "partition-table.bin").write_bytes(b"PT")
        (d / app).write_bytes(b"APP")
        (d / "flasher_args.json").write_text(
            json.dumps(
                {
                    "write_flash_args": ["--flash_mode", "dio", "--flash_size", "2MB", "--flash_freq", "80m"],
                    "flash_settings": {"flash_mode": "dio", "flash_size": "2MB", "flash_freq": "80m"},
                    "flash_files": {
                        "0x0": "bootloader/bootloader.bin",
                        "0x8000": "partition_table/partition-table.bin",
                        "0x10000": app,
                    },
                    "extra_esptool_args": {
                        "after": "hard_reset",
                        "before": "default_reset",
                        "stub": True,
                        "chip": "esp32s3",
                    },
                }
            )
        )
        return d

    def test_by_id_required_rejects_tty_and_glob(self):
        with self.assertRaisesRegex(lab.LabError, "by-id"):
            lab.require_by_id_path("/dev/ttyACM0")
        with self.assertRaisesRegex(lab.LabError, "glob"):
            lab.require_by_id_path("/dev/serial/by-id/usb-*")
        p = lab.require_by_id_path(lab.DEFAULT_BY_ID)
        self.assertTrue(str(p).startswith("/dev/serial/by-id/"))

    def test_esptool_version_gate(self):
        self.assertEqual(lab.require_esptool_version_ok("esptool v5.1.0\n5.1.0"), (5, 1, 0))
        with self.assertRaisesRegex(lab.LabError, "below required"):
            lab.require_esptool_version_ok("esptool 3.3.0", minimum=(4, 0, 0))
        with self.assertRaisesRegex(lab.LabError, "cannot parse"):
            lab.require_esptool_version_ok("not a version")

    def test_flash_argv_construction_and_missing_serial_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            art = self.artifact_dir(root)
            cmd = lab.load_led_flash_plan(art, port=lab.DEFAULT_BY_ID)
            self.assertIn("write-flash", cmd)
            self.assertIn(lab.DEFAULT_BY_ID, cmd)
            self.assertIn("0x0", cmd)
            self.assertIn("bootloader.bin", cmd)
            self.assertIn("podlesp-led-pattern.bin", cmd)
            # missing app
            (art / "podlesp-led-pattern.bin").unlink()
            with self.assertRaisesRegex(lab.LabError, "missing artifact"):
                lab.load_led_flash_plan(art, port=lab.DEFAULT_BY_ID)

    def test_flash_plan_refuses_wrong_app_name(self):
        with tempfile.TemporaryDirectory() as directory:
            art = self.artifact_dir(Path(directory), app="podlesp-smoke.bin")
            with self.assertRaisesRegex(lab.LabError, "missing app bin"):
                lab.load_led_flash_plan(art, port=lab.DEFAULT_BY_ID)

    def test_led_marker_parsing(self):
        sample = b"""
PODLESP_LED_PATTERN boot gpio=15 count=2 base_hz=1 burst=2000Hz/250ms every 10s
PODLESP_LED_TICK sec=0
PODLESP_LED_TICK sec=1
PODLESP_LED_TICK sec=2
PODLESP_LED_BURST start hz=2000 ms=250 cycles=500
PODLESP_LED_BURST end
"""
        outcome, reason = lab.evaluate_led_capture(sample)
        self.assertEqual(outcome, "PASS")
        self.assertIn("ticks=3", reason)
        bad = b"PODLESP_LED_BURST start hz=1000 ms=250 cycles=1\nPODLESP_LED_BURST end\n"
        outcome, _ = lab.evaluate_led_capture(bad, min_ticks=0, min_bursts=1)
        self.assertEqual(outcome, "FAIL")
        outcome, _ = lab.evaluate_led_capture(b"")
        self.assertEqual(outcome, "INCONCLUSIVE")

    def test_execution_gate(self):
        self.assertFalse(lab.execution_allowed(True))  # env unset
        self.assertFalse(lab.execution_allowed(False))

    def test_scp_plan_uses_by_id(self):
        with tempfile.TemporaryDirectory() as directory:
            art = self.artifact_dir(Path(directory))
            plan = lab.build_scp_and_ssh_plan(
                artifact_dir=art,
                ssh_host="192.168.0.14",
                ssh_identity="/tmp/key",
            )
            self.assertIn("192.168.0.14", plan["target"])
            self.assertTrue(any("bootloader.bin" in x for x in plan["scp"]))
            self.assertIn("/dev/serial/by-id/", plan["port"])
            self.assertIn("write-flash", plan["flash_argv"])


if __name__ == "__main__":
    unittest.main()
