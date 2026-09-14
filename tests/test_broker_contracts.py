import copy
import datetime as dt
import hashlib
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import podlesp_broker_contracts as contracts


class PublicSignatureVerifier:
    """Test verification capability containing no signing/private key."""

    def __init__(self, expected_signer, expected_payload, expected_signature):
        self.expected_signer = expected_signer
        self.expected_payload = expected_payload
        self.expected_signature = expected_signature
        self.calls = 0

    def __call__(self, signer, payload, signature, algorithm, namespace):
        self.calls += 1
        return (
            signer == self.expected_signer
            and payload == self.expected_payload
            and signature == self.expected_signature
            and algorithm == "sshsig"
            and namespace == contracts.SIGNATURE_NAMESPACE
        )


class BrokerContractTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.now = dt.datetime(2026, 9, 14, 12, 0, tzinfo=dt.timezone.utc)
        self.context = contracts.AdmissionContext(
            now=self.now,
            clock_trusted=True,
            broker_id="broker-zero-1",
            host_key_fingerprint="SHA256:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi1234567890=",
            runtime_sha256="1" * 64,
            config_sha256="2" * 64,
            topology_sha256="3" * 64,
            power_sha256="4" * 64,
            boot_challenge="boot-7-session-9",
            dispatcher_id="dispatcher-vm-1",
            endpoint_identity_sha256=hashlib.sha256(contracts.canonical_json(self.endpoint())).hexdigest(),
            operation="fixture-cycle-once",
            physical_unit_label="B1",
        )

    def physical_unit(self):
        return {
            "manufacturer": "Example Maker",
            "model": "Example ESP32-S3",
            "sku": "EX-S3-1",
            "revision": "A",
            "local_label": "B1",
        }

    def endpoint(self):
        return {
            "binding": "exact-native-usb",
            "by_path": "/dev/serial/by-path/platform-test-usb-0:1.0",
            "interface": "usb-serial-jtag",
            "vid": "303a",
            "pid": "1001",
            "usb_manufacturer": "Espressif",
            "usb_product": "USB JTAG/serial debug unit",
            "usb_serial_sha256": "5" * 64,
        }

    def artifact(self):
        return {
            "applicability": "exact",
            "manifest_sha256": "6" * 64,
            "bundle_sha256": "7" * 64,
            "source_revision": "8" * 40,
            "flake_lock_sha256": "9" * 64,
            "file_digests": {name: hashlib.sha256(name.encode()).hexdigest() for name in contracts.ARTIFACT_FILES},
            "flash_offsets": dict(contracts.FLASH_OFFSETS),
            "settings": {
                "chip": "esp32s3",
                "flash_size": "2MB",
                "flash_baud": 460800,
                "capture_baud": 115200,
            },
        }

    def effects(self, operation="fixture-cycle-once"):
        return {
            "identity_snapshot": True,
            "serial_open": operation != "inspect-once",
            "capture": operation in ("capture-once", "fixture-cycle-once"),
            "flash_write": operation in contracts.WRITE_OPERATIONS,
            "sector_overwrite": operation in contracts.WRITE_OPERATIONS,
            "security_change": False,
            "full_chip_erase": False,
            "esptool_reset_constituents": list(contracts.RESET_CONSTITUENTS) if operation in contracts.WRITE_OPERATIONS else [],
        }

    def plan(self, operation="fixture-cycle-once"):
        write = operation in contracts.WRITE_OPERATIONS
        return {
            "protocol": contracts.PROTOCOL_VERSION,
            "policy": contracts.POLICY_VERSION,
            "approval_id": "approval-123",
            "operator": {
                "identity": "operator:captain",
                "signer_id": "operator-key-1",
                "consent_ref": "consent:ticket-123",
            },
            "issued_at": (self.now - dt.timedelta(minutes=1)).isoformat(),
            "expires_at": (self.now + dt.timedelta(minutes=4)).isoformat(),
            "lab": contracts.LAB_ID,
            "broker": {
                "id": self.context.broker_id,
                "host_key_fingerprint": self.context.host_key_fingerprint,
                "runtime_sha256": self.context.runtime_sha256,
                "config_sha256": self.context.config_sha256,
                "topology_sha256": self.context.topology_sha256,
                "power_sha256": self.context.power_sha256,
                "boot_challenge": self.context.boot_challenge,
            },
            "dispatcher_id": self.context.dispatcher_id,
            "physical_unit": self.physical_unit(),
            "endpoint": self.endpoint(),
            "operation": operation,
            "artifact": self.artifact() if write else {
                "applicability": "not-applicable",
                "reason": "non-write operation",
            },
            "effects": self.effects(operation),
            "ceilings": dict(contracts.MAX_CEILINGS),
            "recovery": {
                "known_good_image_sha256": "a" * 64 if write else "not-applicable",
                "method_ref": "recovery:reviewed-B1" if write else "not-applicable",
                "partial_write_acknowledged": write,
            },
            "evidence": {
                "destination_ref": "archive:private/podlesp",
                "retention_ref": "policy:no-auto-delete-v1",
                "method_ids": ["METHOD-USB-FIXTURE-01"],
                "test_ids": ["AUTH-01", "ID-01"],
            },
        }

    def envelope(self, plan=None):
        plan = self.plan() if plan is None else plan
        return {
            "plan": plan,
            "signature": {
                "algorithm": "sshsig",
                "namespace": contracts.SIGNATURE_NAMESPACE,
                "signer_id": "operator-key-1",
                "value": "external-signature-fixture",
            },
        }

    def verifier(self, plan):
        return PublicSignatureVerifier(
            "operator-key-1",
            contracts.canonical_json(plan),
            "external-signature-fixture",
        )

    def test_canonicalization_is_stable_strict_and_duplicate_safe(self):
        left = {"z": ["é", 2], "a": {"y": True, "x": None}}
        right = {"a": {"x": None, "y": True}, "z": ["é", 2]}
        expected = b'{"a":{"x":null,"y":true},"z":["\xc3\xa9",2]}\n'
        self.assertEqual(contracts.canonical_json(left), expected)
        self.assertEqual(contracts.canonical_json(right), expected)
        with self.assertRaisesRegex(contracts.ContractError, "floating-point"):
            contracts.canonical_json({"seconds": 1.5})
        with self.assertRaisesRegex(contracts.ContractError, "duplicate"):
            contracts.load_json('{"action":"status","action":"execute"}')

    def test_signature_hook_receives_canonical_plan_and_dispatcher_has_no_signing_key(self):
        plan = self.plan()
        verifier = self.verifier(plan)
        result = contracts.validate_signed_approval(self.envelope(plan), self.context, verifier)
        self.assertEqual(result.operation, "fixture-cycle-once")
        self.assertEqual(verifier.calls, 1)
        self.assertNotIn("private", vars(verifier))
        self.assertNotIn("key", {field.name for field in contracts.dataclasses.fields(self.context)})
        bad = self.envelope(plan)
        bad["signature"]["value"] = "forged-by-dispatcher"
        with self.assertRaisesRegex(contracts.ContractError, "verification failed"):
            contracts.validate_signed_approval(bad, self.context, verifier)

    def test_complete_execute_request_validates_without_io(self):
        plan = self.plan()
        request = {
            "protocol": contracts.PROTOCOL_VERSION,
            "request_id": "request-1",
            "action": "execute",
            "body": {"envelope": self.envelope(plan)},
        }
        verifier = self.verifier(plan)
        with mock.patch("builtins.open", side_effect=AssertionError("real I/O attempted")):
            parsed, approved = contracts.validate_execute_request(request, self.context, verifier)
        self.assertEqual((parsed.action, approved.approval_id), ("execute", "approval-123"))

    def test_metadata_only_enrollment_is_candidate_only_and_cannot_execute(self):
        enrollment = {
            "schema": contracts.ENROLLMENT_VERSION,
            "enrollment_id": "enrollment-B1-candidate",
            "state": "candidate",
            "endpoint_binding": "discover-only",
            "physical_unit": self.physical_unit(),
            "endpoint": None,
            "topology_sha256": "3" * 64,
            "power_sha256": "4" * 64,
            "review_ref": "operator-review:pending-B1",
        }
        record = contracts.validate_enrollment(enrollment)
        self.assertFalse(record.may_execute)
        self.assertIsNone(record.endpoint)
        request = {
            "protocol": contracts.PROTOCOL_VERSION,
            "request_id": "request-enrollment",
            "action": "execute",
            "body": {"envelope": enrollment},
        }
        with self.assertRaises(contracts.ContractError):
            contracts.validate_execute_request(request, self.context, lambda *args: True)
        escalated = copy.deepcopy(enrollment)
        escalated["operation"] = "flash-once"
        with self.assertRaisesRegex(contracts.ContractError, "unsupported fields"):
            contracts.validate_enrollment(escalated)

    def test_reviewed_enrollment_requires_exact_native_usb_identity(self):
        enrollment = {
            "schema": contracts.ENROLLMENT_VERSION,
            "enrollment_id": "enrollment-B1-reviewed",
            "state": "reviewed",
            "endpoint_binding": "exact-native-usb",
            "physical_unit": self.physical_unit(),
            "endpoint": self.endpoint(),
            "topology_sha256": "3" * 64,
            "power_sha256": "4" * 64,
            "review_ref": "operator-review:approved-B1",
        }
        self.assertFalse(contracts.validate_enrollment(enrollment).may_execute)
        for key, value in (("interface", "usb-uart"), ("usb_serial_sha256", "UNKNOWN"), ("by_path", "/dev/ttyACM0")):
            changed = copy.deepcopy(enrollment)
            changed["endpoint"][key] = value
            with self.subTest(key=key), self.assertRaises(contracts.ContractError):
                contracts.validate_enrollment(changed)

    def test_scope_challenge_operation_and_identity_mismatches_fail_closed(self):
        mutations = (
            ("broker id", lambda plan: plan["broker"].update(id="other-broker")),
            ("host key", lambda plan: plan["broker"].update(host_key_fingerprint="SHA256:abcdefghijklmnopqrstuvwxyzABCDEFGHI1234567890=")),
            ("runtime", lambda plan: plan["broker"].update(runtime_sha256="b" * 64)),
            ("config", lambda plan: plan["broker"].update(config_sha256="b" * 64)),
            ("topology", lambda plan: plan["broker"].update(topology_sha256="b" * 64)),
            ("power", lambda plan: plan["broker"].update(power_sha256="b" * 64)),
            ("challenge", lambda plan: plan["broker"].update(boot_challenge="old-boot")),
            ("dispatcher", lambda plan: plan.update(dispatcher_id="other-dispatcher")),
            ("operation", lambda plan: plan.update(operation="flash-once")),
            ("physical", lambda plan: plan["physical_unit"].update(local_label="B2")),
            ("identity", lambda plan: plan["endpoint"].update(usb_serial_sha256="b" * 64)),
        )
        for name, mutate in mutations:
            plan = self.plan()
            mutate(plan)
            with self.subTest(name=name), self.assertRaises(contracts.ContractError):
                contracts.validate_approval_plan(plan, self.context)

    def test_expiry_lifetime_clock_and_remaining_window_rejections(self):
        cases = []
        expired = self.plan()
        expired["expires_at"] = self.now.isoformat()
        cases.append(expired)
        future = self.plan()
        future["issued_at"] = (self.now + dt.timedelta(seconds=1)).isoformat()
        cases.append(future)
        long_lived = self.plan()
        long_lived["expires_at"] = (self.now + dt.timedelta(minutes=5)).isoformat()
        cases.append(long_lived)
        too_short = self.plan()
        too_short["expires_at"] = (self.now + dt.timedelta(seconds=154)).isoformat()
        cases.append(too_short)
        for index, plan in enumerate(cases):
            with self.subTest(index=index), self.assertRaises(contracts.ContractError):
                contracts.validate_approval_plan(plan, self.context)
        untrusted = dataclasses_replace(self.context, clock_trusted=False)
        with self.assertRaisesRegex(contracts.ContractError, "not trusted"):
            contracts.validate_approval_plan(self.plan(), untrusted)

    def test_effects_resets_artifacts_and_unknown_fields_are_operation_exact(self):
        for operation in contracts.OPERATIONS:
            context = dataclasses_replace(self.context, operation=operation)
            plan = self.plan(operation)
            contracts.validate_approval_plan(plan, context)
            reset_names = plan["effects"]["esptool_reset_constituents"]
            self.assertEqual(bool(reset_names), operation in contracts.WRITE_OPERATIONS)
        standalone = self.plan()
        standalone["operation"] = "reset-once"
        with self.assertRaisesRegex(contracts.ContractError, "unsupported operation"):
            contracts.validate_approval_plan(standalone, dataclasses_replace(self.context, operation=None))
        hidden_reset = self.plan("capture-once")
        hidden_reset["effects"]["esptool_reset_constituents"] = ["hard_reset"]
        with self.assertRaisesRegex(contracts.ContractError, "effect disclosure"):
            contracts.validate_approval_plan(hidden_reset, dataclasses_replace(self.context, operation="capture-once"))
        extra = self.plan()
        extra["shell_command"] = "esptool.py erase_flash"
        with self.assertRaisesRegex(contracts.ContractError, "unsupported fields"):
            contracts.validate_approval_plan(extra, self.context)

    def test_required_identity_and_approval_facts_reject_unknown_or_missing(self):
        plan = self.plan()
        plan["physical_unit"]["revision"] = "UNKNOWN"
        with self.assertRaisesRegex(contracts.ContractError, "concrete"):
            contracts.validate_approval_plan(plan, self.context)
        plan = self.plan()
        del plan["endpoint"]["vid"]
        with self.assertRaisesRegex(contracts.ContractError, "missing fields"):
            contracts.validate_approval_plan(plan, self.context)
        plan = self.plan()
        plan["operator"]["consent_ref"] = "TBD"
        with self.assertRaisesRegex(contracts.ContractError, "concrete"):
            contracts.validate_approval_plan(plan, self.context)

    def test_request_vocabulary_rejects_unknown_actions_fields_and_versions(self):
        valid = {
            "protocol": contracts.PROTOCOL_VERSION,
            "request_id": "request-status-1",
            "action": "status",
            "body": {"run_id": "run-1"},
        }
        self.assertEqual(contracts.validate_request(valid).action, "status")
        for mutate in (
            lambda request: request.update(action="reset"),
            lambda request: request.update(protocol="podlesp-broker/2"),
            lambda request: request["body"].update(command="uname -a"),
        ):
            changed = copy.deepcopy(valid)
            mutate(changed)
            with self.assertRaises(contracts.ContractError):
                contracts.validate_request(changed)


def dataclasses_replace(instance, **changes):
    return contracts.dataclasses.replace(instance, **changes)


if __name__ == "__main__":
    unittest.main()
