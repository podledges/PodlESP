#!/usr/bin/env python3
"""Pure data-plane contracts for a future PodlESP broker.

This module validates records only.  It deliberately contains no device,
serial, USB, subprocess, network, or persistence implementation.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import hashlib
import json
import re
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

PROTOCOL_VERSION = "podlesp-broker/1"
POLICY_VERSION = "podlesp-approval/1"
ENROLLMENT_VERSION = "podlesp-enrollment/1"
SIGNATURE_NAMESPACE = "podlesp-operation-v1"
LAB_ID = "PodlESP"

OPERATIONS = frozenset(("inspect-once", "capture-once", "flash-once", "fixture-cycle-once"))
REQUEST_ACTIONS = frozenset(("capabilities", "status", "stage", "plan", "execute", "lease", "cancel", "result", "ack"))
WRITE_OPERATIONS = frozenset(("flash-once", "fixture-cycle-once"))
RESET_CONSTITUENTS = ("default_reset", "hard_reset")
ARTIFACT_FILES = frozenset((
    "bootloader.bin",
    "partition-table.bin",
    "podlesp-smoke.bin",
    "podlesp-smoke.elf",
    "flasher_args.json",
))
FLASH_OFFSETS = {
    "bootloader.bin": "0x0",
    "partition-table.bin": "0x8000",
    "podlesp-smoke.bin": "0x10000",
}
SUPPORTED_BAUDS = frozenset((9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600))
UNKNOWN = re.compile(r"(?:UNKNOWN|REPLACE|UNCONFIRMED|TBD|<[^>]+>)", re.I)
HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
HOST_FINGERPRINT = re.compile(r"SHA256:[A-Za-z0-9+/]{20,}={0,2}")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:@/-]{0,127}")
USB_HEX = re.compile(r"[0-9a-f]{4}")
GIT_REVISION = re.compile(r"[0-9a-f]{40,64}")

MAX_CEILINGS = {
    "request_bytes": 65_536,
    "identity_seconds": 5,
    "capture_seconds": 20,
    "capture_bytes": 65_536,
    "flash_seconds": 120,
    "flash_output_bytes": 1_048_576,
    "operation_seconds": 150,
    "cleanup_seconds": 5,
    "lease_seconds": 10,
}


class ContractError(ValueError):
    """A record is unsupported, incomplete, unresolved, or out of scope."""


@dataclasses.dataclass(frozen=True)
class EnrollmentRecord:
    enrollment_id: str
    endpoint_binding: str
    physical_unit: Mapping[str, str]
    endpoint: Mapping[str, str] | None

    @property
    def may_execute(self) -> bool:
        """Enrollment is descriptive evidence and never execution authority."""
        return False


@dataclasses.dataclass(frozen=True)
class ApprovalPlan:
    approval_id: str
    operation: str
    expires_at: dt.datetime
    signer_id: str
    canonical_bytes: bytes


@dataclasses.dataclass(frozen=True)
class BrokerRequest:
    request_id: str
    action: str
    body: Mapping[str, Any]


@dataclasses.dataclass(frozen=True)
class AdmissionContext:
    now: dt.datetime
    clock_trusted: bool
    broker_id: str
    host_key_fingerprint: str
    runtime_sha256: str
    config_sha256: str
    topology_sha256: str
    power_sha256: str
    boot_challenge: str
    dispatcher_id: str
    endpoint_identity_sha256: str
    operation: str | None = None
    physical_unit_label: str | None = None


# A dispatcher receives only this verification capability.  No signing API or
# private-key field exists in the contract.
SignatureVerifier = Callable[[str, bytes, str, str, str], bool]


def hashlib_sha256(value: bytes) -> str:
    """Hash canonical endpoint bindings without exposing raw USB serials."""
    return hashlib.sha256(value).hexdigest()


def _pairs_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate field: {key}")
        result[key] = value
    return result


def load_json(data: bytes | str) -> Any:
    """Load strict JSON, rejecting duplicate keys and non-finite numbers."""
    try:
        return json.loads(
            data,
            object_pairs_hook=_pairs_without_duplicates,
            parse_constant=lambda value: (_ for _ in ()).throw(ContractError(f"unsupported number: {value}")),
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ContractError(f"invalid JSON: {exc}") from exc


def _canonical_value(value: Any, path: str = "$.") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise ContractError(f"floating-point value is not canonical at {path}")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _canonical_value(item, f"{path}[{index}]")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ContractError(f"non-string object key at {path}")
            _canonical_value(item, f"{path}{key}.")
        return
    raise ContractError(f"unsupported canonical JSON type at {path}")


def canonical_json(value: Any) -> bytes:
    """Return the sole v1 signing representation: sorted compact UTF-8 JSON."""
    _canonical_value(value)
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _object(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{path} must be an object")
    return value


def _strict(value: Any, required: set[str], path: str) -> Mapping[str, Any]:
    obj = _object(value, path)
    missing = required - set(obj)
    extra = set(obj) - required
    if missing:
        raise ContractError(f"{path} missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise ContractError(f"{path} unsupported fields: {', '.join(sorted(extra))}")
    return obj


def _text(value: Any, path: str, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value.strip() or UNKNOWN.search(value):
        raise ContractError(f"{path} must be concrete")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise ContractError(f"{path} has unsupported format")
    return value


def _digest(value: Any, path: str) -> str:
    return _text(value, path, HEX_SHA256)


def _timestamp(value: Any, path: str) -> dt.datetime:
    text = _text(value, path)
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{path} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ContractError(f"{path} must include a timezone")
    return parsed.astimezone(dt.timezone.utc)


def _physical_unit(value: Any, path: str = "physical_unit") -> Mapping[str, str]:
    fields = {"manufacturer", "model", "sku", "revision", "local_label"}
    obj = _strict(value, fields, path)
    for key in fields:
        _text(obj[key], f"{path}.{key}")
    return obj  # type: ignore[return-value]


def _endpoint(value: Any, path: str = "endpoint") -> Mapping[str, str]:
    fields = {"binding", "by_path", "interface", "vid", "pid", "usb_manufacturer", "usb_product", "usb_serial_sha256"}
    obj = _strict(value, fields, path)
    if obj["binding"] != "exact-native-usb":
        raise ContractError(f"{path}.binding must be exact-native-usb")
    by_path = _text(obj["by_path"], f"{path}.by_path")
    if not by_path.startswith("/dev/serial/by-path/") or any(char in by_path for char in "*?["):
        raise ContractError(f"{path}.by_path must name one exact by-path endpoint")
    if obj["interface"] != "usb-serial-jtag":
        raise ContractError(f"{path}.interface must be usb-serial-jtag for native-USB first proof")
    _text(obj["vid"], f"{path}.vid", USB_HEX)
    _text(obj["pid"], f"{path}.pid", USB_HEX)
    _text(obj["usb_manufacturer"], f"{path}.usb_manufacturer")
    _text(obj["usb_product"], f"{path}.usb_product")
    _digest(obj["usb_serial_sha256"], f"{path}.usb_serial_sha256")
    return obj  # type: ignore[return-value]


def validate_enrollment(value: Any) -> EnrollmentRecord:
    """Validate a candidate or reviewed identity record; never grant execution."""
    fields = {"schema", "enrollment_id", "state", "endpoint_binding", "physical_unit", "endpoint", "topology_sha256", "power_sha256", "review_ref"}
    obj = _strict(value, fields, "enrollment")
    if obj["schema"] != ENROLLMENT_VERSION:
        raise ContractError("unsupported enrollment schema")
    enrollment_id = _text(obj["enrollment_id"], "enrollment.enrollment_id", ID)
    physical = _physical_unit(obj["physical_unit"], "enrollment.physical_unit")
    _digest(obj["topology_sha256"], "enrollment.topology_sha256")
    _digest(obj["power_sha256"], "enrollment.power_sha256")
    _text(obj["review_ref"], "enrollment.review_ref")
    binding = obj["endpoint_binding"]
    if binding == "discover-only":
        if obj["state"] != "candidate" or obj["endpoint"] is not None:
            raise ContractError("discover-only enrollment must be a candidate with no endpoint")
        endpoint = None
    elif binding == "exact-native-usb":
        if obj["state"] != "reviewed":
            raise ContractError("exact-native-usb enrollment must be operator-reviewed")
        endpoint = _endpoint(obj["endpoint"], "enrollment.endpoint")
    else:
        raise ContractError("unsupported endpoint_binding")
    frozen_physical = MappingProxyType(dict(physical))
    frozen_endpoint = MappingProxyType(dict(endpoint)) if endpoint is not None else None
    return EnrollmentRecord(enrollment_id, binding, frozen_physical, frozen_endpoint)


def _validate_artifact(value: Any, operation: str) -> None:
    obj = _object(value, "plan.artifact")
    if operation not in WRITE_OPERATIONS:
        expected = {"applicability", "reason"}
        obj = _strict(obj, expected, "plan.artifact")
        if obj != {"applicability": "not-applicable", "reason": "non-write operation"}:
            raise ContractError("non-write artifact fields must be explicitly not-applicable")
        return
    fields = {"applicability", "manifest_sha256", "bundle_sha256", "source_revision", "flake_lock_sha256", "file_digests", "flash_offsets", "settings"}
    obj = _strict(obj, fields, "plan.artifact")
    if obj["applicability"] != "exact":
        raise ContractError("write operation requires exact artifacts")
    for key in ("manifest_sha256", "bundle_sha256", "flake_lock_sha256"):
        _digest(obj[key], f"plan.artifact.{key}")
    _text(obj["source_revision"], "plan.artifact.source_revision", GIT_REVISION)
    digests = _strict(obj["file_digests"], set(ARTIFACT_FILES), "plan.artifact.file_digests")
    for name in ARTIFACT_FILES:
        _digest(digests[name], f"plan.artifact.file_digests.{name}")
    offsets = _strict(obj["flash_offsets"], set(FLASH_OFFSETS), "plan.artifact.flash_offsets")
    if dict(offsets) != FLASH_OFFSETS:
        raise ContractError("unsupported flash file layout")
    settings = _strict(obj["settings"], {"chip", "flash_size", "flash_baud", "capture_baud"}, "plan.artifact.settings")
    if settings["chip"] != "esp32s3" or settings["flash_size"] != "2MB":
        raise ContractError("unsupported flash target or size")
    for key in ("flash_baud", "capture_baud"):
        if type(settings[key]) is not int or settings[key] not in SUPPORTED_BAUDS:
            raise ContractError(f"unsupported {key}")


def _validate_effects(value: Any, operation: str) -> None:
    fields = {"identity_snapshot", "serial_open", "capture", "flash_write", "sector_overwrite", "security_change", "full_chip_erase", "esptool_reset_constituents"}
    obj = _strict(value, fields, "plan.effects")
    expected = {
        "identity_snapshot": True,
        "serial_open": operation != "inspect-once",
        "capture": operation in ("capture-once", "fixture-cycle-once"),
        "flash_write": operation in WRITE_OPERATIONS,
        "sector_overwrite": operation in WRITE_OPERATIONS,
        "security_change": False,
        "full_chip_erase": False,
        "esptool_reset_constituents": list(RESET_CONSTITUENTS) if operation in WRITE_OPERATIONS else [],
    }
    if dict(obj) != expected:
        raise ContractError("effect disclosure does not exactly match operation")


def _validate_ceilings(value: Any) -> int:
    obj = _strict(value, set(MAX_CEILINGS), "plan.ceilings")
    for key, maximum in MAX_CEILINGS.items():
        amount = obj[key]
        if type(amount) is not int or amount <= 0 or amount > maximum:
            raise ContractError(f"plan.ceilings.{key} exceeds supported policy")
    return int(obj["operation_seconds"]) + int(obj["cleanup_seconds"])


def validate_approval_plan(value: Any, context: AdmissionContext) -> ApprovalPlan:
    fields = {"protocol", "policy", "approval_id", "operator", "issued_at", "expires_at", "lab", "broker", "dispatcher_id", "physical_unit", "endpoint", "operation", "artifact", "effects", "ceilings", "recovery", "evidence"}
    plan = _strict(value, fields, "plan")
    if plan["protocol"] != PROTOCOL_VERSION or plan["policy"] != POLICY_VERSION:
        raise ContractError("unsupported protocol or policy version")
    approval_id = _text(plan["approval_id"], "plan.approval_id", ID)
    if plan["lab"] != LAB_ID:
        raise ContractError("approval scope mismatch: lab")
    operator = _strict(plan["operator"], {"identity", "signer_id", "consent_ref"}, "plan.operator")
    for key in operator:
        _text(operator[key], f"plan.operator.{key}", ID if key == "signer_id" else None)
    issued = _timestamp(plan["issued_at"], "plan.issued_at")
    expires = _timestamp(plan["expires_at"], "plan.expires_at")
    if not context.clock_trusted:
        raise ContractError("broker clock is not trusted")
    now = context.now.astimezone(dt.timezone.utc) if context.now.tzinfo is not None else None
    if now is None:
        raise ContractError("admission clock must include a timezone")
    if expires <= issued or expires - issued > dt.timedelta(minutes=5):
        raise ContractError("approval lifetime is invalid")
    if now < issued:
        raise ContractError("approval clock rollback or issue-time mismatch")
    if now >= expires:
        raise ContractError("approval has expired")
    broker = _strict(plan["broker"], {"id", "host_key_fingerprint", "runtime_sha256", "config_sha256", "topology_sha256", "power_sha256", "boot_challenge"}, "plan.broker")
    _text(broker["id"], "plan.broker.id", ID)
    _text(broker["host_key_fingerprint"], "plan.broker.host_key_fingerprint", HOST_FINGERPRINT)
    for key in ("runtime_sha256", "config_sha256", "topology_sha256", "power_sha256"):
        _digest(broker[key], f"plan.broker.{key}")
    _text(broker["boot_challenge"], "plan.broker.boot_challenge", ID)
    expected_broker = {
        "id": context.broker_id,
        "host_key_fingerprint": context.host_key_fingerprint,
        "runtime_sha256": context.runtime_sha256,
        "config_sha256": context.config_sha256,
        "topology_sha256": context.topology_sha256,
        "power_sha256": context.power_sha256,
        "boot_challenge": context.boot_challenge,
    }
    mismatched = [key for key, expected in expected_broker.items() if broker[key] != expected]
    if mismatched:
        raise ContractError("approval scope mismatch: broker " + ", ".join(mismatched))
    dispatcher_id = _text(plan["dispatcher_id"], "plan.dispatcher_id", ID)
    if dispatcher_id != context.dispatcher_id:
        raise ContractError("approval scope mismatch: dispatcher")
    physical = _physical_unit(plan["physical_unit"], "plan.physical_unit")
    if context.physical_unit_label is not None and physical["local_label"] != context.physical_unit_label:
        raise ContractError("approval scope mismatch: physical unit")
    endpoint = _endpoint(plan["endpoint"], "plan.endpoint")
    _digest(context.endpoint_identity_sha256, "admission.endpoint_identity_sha256")
    if hashlib_sha256(canonical_json(endpoint)) != context.endpoint_identity_sha256:
        raise ContractError("approval scope mismatch: endpoint identity")
    operation = plan["operation"]
    if operation not in OPERATIONS:
        raise ContractError("unsupported operation")
    if context.operation is not None and operation != context.operation:
        raise ContractError("approval scope mismatch: operation")
    _validate_artifact(plan["artifact"], operation)
    _validate_effects(plan["effects"], operation)
    required_remaining = _validate_ceilings(plan["ceilings"])
    if expires - now < dt.timedelta(seconds=required_remaining):
        raise ContractError("approval expires before operation and cleanup ceilings")
    recovery = _strict(plan["recovery"], {"known_good_image_sha256", "method_ref", "partial_write_acknowledged"}, "plan.recovery")
    if operation in WRITE_OPERATIONS:
        _digest(recovery["known_good_image_sha256"], "plan.recovery.known_good_image_sha256")
        _text(recovery["method_ref"], "plan.recovery.method_ref")
        if recovery["partial_write_acknowledged"] is not True:
            raise ContractError("write operation lacks partial-write acknowledgement")
    elif dict(recovery) != {"known_good_image_sha256": "not-applicable", "method_ref": "not-applicable", "partial_write_acknowledged": False}:
        raise ContractError("non-write recovery fields must be explicitly not-applicable")
    evidence = _strict(plan["evidence"], {"destination_ref", "retention_ref", "method_ids", "test_ids"}, "plan.evidence")
    _text(evidence["destination_ref"], "plan.evidence.destination_ref")
    _text(evidence["retention_ref"], "plan.evidence.retention_ref")
    for key in ("method_ids", "test_ids"):
        values = evidence[key]
        if not isinstance(values, list) or not values:
            raise ContractError(f"plan.evidence.{key} must be a non-empty list")
        for index, item in enumerate(values):
            _text(item, f"plan.evidence.{key}[{index}]", ID)
    return ApprovalPlan(
        approval_id,
        operation,
        expires,
        str(operator["signer_id"]),
        canonical_json(plan),
    )


def validate_signed_approval(value: Any, context: AdmissionContext, verifier: SignatureVerifier) -> ApprovalPlan:
    envelope = _strict(value, {"plan", "signature"}, "envelope")
    plan = validate_approval_plan(envelope["plan"], context)
    signature = _strict(envelope["signature"], {"algorithm", "namespace", "signer_id", "value"}, "envelope.signature")
    if signature["algorithm"] != "sshsig" or signature["namespace"] != SIGNATURE_NAMESPACE:
        raise ContractError("unsupported approval signature policy")
    signer_id = _text(signature["signer_id"], "envelope.signature.signer_id", ID)
    if signer_id != plan.signer_id:
        raise ContractError("approval signer identity mismatch")
    encoded = _text(signature["value"], "envelope.signature.value")
    if not verifier(signer_id, plan.canonical_bytes, encoded, str(signature["algorithm"]), str(signature["namespace"])):
        raise ContractError("approval signature verification failed")
    return plan


def validate_request(value: Any) -> BrokerRequest:
    request = _strict(value, {"protocol", "request_id", "action", "body"}, "request")
    if request["protocol"] != PROTOCOL_VERSION:
        raise ContractError("unsupported request protocol")
    request_id = _text(request["request_id"], "request.request_id", ID)
    action = request["action"]
    if action not in REQUEST_ACTIONS:
        raise ContractError("unsupported request action")
    body_fields = {
        "capabilities": set(),
        "status": {"run_id"},
        "stage": {"bundle_sha256", "manifest_sha256", "total_bytes"},
        "plan": {"plan"},
        "execute": {"envelope"},
        "lease": {"run_id", "sequence"},
        "cancel": {"run_id"},
        "result": {"run_id"},
        "ack": {"run_id", "result_sha256"},
    }[action]
    body = _strict(request["body"], body_fields, "request.body")
    for key, item in body.items():
        if key.endswith("_sha256"):
            _digest(item, f"request.body.{key}")
        elif key in ("run_id",):
            _text(item, f"request.body.{key}", ID)
        elif key in ("total_bytes", "sequence") and (type(item) is not int or item < 0):
            raise ContractError(f"request.body.{key} must be a non-negative integer")
    if action == "stage" and body["total_bytes"] > 32 * 1024 * 1024:
        raise ContractError("staged bundle exceeds v1 ceiling")
    # Nested plan/envelope admission is intentionally a separate call requiring
    # a trusted clock, exact local scope, and signature verifier.
    return BrokerRequest(request_id, action, MappingProxyType(dict(body)))


def validate_execute_request(value: Any, context: AdmissionContext, verifier: SignatureVerifier) -> tuple[BrokerRequest, ApprovalPlan]:
    """Validate the complete execute admission surface without performing I/O."""
    request = validate_request(value)
    if request.action != "execute":
        raise ContractError("request is not an execute request")
    plan = validate_signed_approval(request.body["envelope"], context, verifier)
    return request, plan
