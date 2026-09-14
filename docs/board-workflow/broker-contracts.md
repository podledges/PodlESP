# Phase 1 broker data-plane contracts

[`tools/podlesp_broker_contracts.py`](../../tools/podlesp_broker_contracts.py)
is the source-only v1 schema, type, canonicalization, and validation module for a
future broker. It performs no USB, serial, subprocess, network, journal, or
broker-service work. Passing these validators is not authority to access a
board. A future runtime must still enforce durable one-use consumption and all
execution bounds; that work is not implemented here.

## Versioned records

All objects are closed: a missing field or an unrecognized field, version,
action, operation, effect, endpoint kind, artifact, or setting is rejected.
Required text rejects blank values and placeholders such as `UNKNOWN`, `TBD`,
`REPLACE`, and `UNCONFIRMED`.

| Record | Version / discriminator | Contract |
|---|---|---|
| Broker request | `protocol: podlesp-broker/1` | `capabilities`, `status`, `stage`, `plan`, `execute`, `lease`, `cancel`, `result`, and `ack` only. There is no shell/argument passthrough and no reset request. |
| Enrollment | `schema: podlesp-enrollment/1` | Either a `candidate` with `endpoint_binding: discover-only` and no endpoint, or an operator-`reviewed` `exact-native-usb` endpoint. Both are descriptive records whose `may_execute` property is always false. |
| Approval plan | `protocol: podlesp-broker/1`, `policy: podlesp-approval/1` | A complete, exact one-operation plan. Its canonical bytes are the signed payload. |
| Signed envelope | `plan` plus `signature` | SSHSIG policy, namespace `podlesp-operation-v1`, signer identity matching the operator record. Verification is supplied as a public-key-only hook. |

`canonical_json` uses UTF-8, sorted object keys, compact separators, and one
trailing newline. It rejects floating-point and non-finite values; `load_json`
also rejects duplicate fields. This is the only v1 signing representation.
The dispatcher contract contains a verification callback and admission facts,
not a signing API or approver private key.

## Enrollment is not authority

A `discover-only` record names an exact physical unit plus already reviewed
power/topology documents, but deliberately has no endpoint. It is only a
candidate for later human review. It cannot be supplied as an execute envelope,
open a device, grant inspection/capture/flash, or be upgraded by adding an
operation field. A reviewed enrollment adds the exact Pi-local by-path,
interface, VID/PID, USB strings, and hashed serial, but remains non-executable;
a separately signed, current approval envelope is still required.

Phase 1 first proof is **native ESP32-S3 USB Serial/JTAG only**. The v1 endpoint
validator therefore rejects USB-UART and generic tty bindings. This is a
software policy, not evidence that any physical unit has that connector or is
compatible. Physical identity and endpoint identity are separate required
facts; a VID/PID or slot label alone is insufficient.

## Approval plan shape

An approval plan binds all of the following in one signed canonical object:

- approval ID; operator identity, signer ID, and consent reference; issue and
  expiry timestamps (at most five minutes);
- lab, dispatcher identity, broker ID and SSH host-key fingerprint, current
  boot/session challenge, and runtime/config/topology/power SHA-256 digests;
- exact physical manufacturer/model/SKU/revision/local label and exact native
  USB by-path/interface/VID/PID/strings/serial hash;
- one of `inspect-once`, `capture-once`, `flash-once`, or
  `fixture-cycle-once`;
- exact effects and ceilings, recovery acknowledgement/reference, evidence
  destination/retention, and method/test IDs;
- for write operations, exact manifest, bundle, source, lock, five artifact
  digests, three fixed flash offsets, target/settings/baud values, and
  known-good image digest; non-write operations instead carry a closed,
  explicit `not-applicable` artifact/recovery variant.

Admission also compares the plan with trusted current wall-clock and local
broker, dispatcher, challenge, operation, physical-unit, and canonical endpoint
facts. It rejects clock distrust/rollback, premature or expired approvals,
more than five minutes of authority, insufficient remaining time for the
operation plus cleanup ceilings, signature failure, and every scope mismatch.
A future broker must atomically consume `approval_id` before device access and
retain replay state across restart; T2 defines the identifier and signed scope
but intentionally does not implement that T4 runtime behavior.

## Reset and physical-effect boundary

There is **no standalone reset operation or API**. `default_reset` and
`hard_reset` are accepted only as both explicitly named esptool constituents of
an approved `flash-once` or `fixture-cycle-once`. They are forbidden in inspect
and capture plans. Write effects must also disclose sector overwrite; full-chip
erase and security/eFuse changes are always false. No automatic reset,
recovery, retry, reconnect, power switch, or arbitrary esptool operation is in
this vocabulary.

These declarations do not authorize hardware. Attachment, enumeration, serial
opening, capture, flash, reset, host activation, deployment, and physical
claims remain outside this source-only ticket and require later separately
scoped approval and evidence.

## Host-only verification

Run:

```console
python3 -m unittest discover -s tests -v
```

[`tests/test_broker_contracts.py`](../../tests/test_broker_contracts.py) uses
synthetic mappings, a fixed clock, and a public verification test double. A
trap fails if validation tries to open a real path. CI runs this discovery step
before the bounded flake check. Green tests establish data-contract behavior
only, never USB, firmware, reset, power, or physical behavior.
