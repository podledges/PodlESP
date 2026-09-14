# Phase 1 offline requirement traceability

This ledger maps the Phase 1 safety requirement IDs to the tests that exist in
[`tests/test_board_workflow.py`](../../tests/test_board_workflow.py). All listed
implemented coverage is **host/offline coverage only**: it does not access a
board and is not evidence of USB, flash, reset, firmware, or physical behavior.
The proposed column records follow-up acceptance coverage from the Phase 1 lab
plan; it is **not implemented in this PR**.

Test pointers use `BoardWorkflowTests.<method>` so they remain searchable even
when source line numbers move.

| Requirement | Existing implemented host/offline coverage | Proposed coverage — not implemented in this PR |
|---|---|---|
| `USB-01` — no hardware by default | [`BoardWorkflowTests.test_defaults_do_not_execute_hardware`](../../tests/test_board_workflow.py) checks both hardware-capable commands default to dry-run, rejects arbitrary flash arguments, and verifies dry preflight does not call approval, identity, or execution boundaries. | Trap hardware transports for every non-execute broker operation, malformed request, cancellation, and dry-run path. |
| `ID-01` — exact physical and endpoint binding | [`test_device_mismatch_and_changed_identity`](../../tests/test_board_workflow.py) and [`test_ambiguous_identity_is_rejected`](../../tests/test_board_workflow.py) reject mismatched, changed, missing, and duplicate synthetic endpoint identities. | Duplicate VID/PID devices, missing/duplicate serials, moved paths, post-reset swaps, and adapter-versus-DUT confusion. |
| `AUTH-01` — fresh, one-use, complete scope | [`test_authorization_absent_and_out_of_scope`](../../tests/test_board_workflow.py) rejects missing and manifest-mismatched approval. | Signed actor/broker/config/topology/limit scope, expiry and clock behavior, boot challenges, concurrent dispatch, durable replay prevention, and interrupted consumption. |
| `ART-01` — exact build and flash bytes | [`test_artifact_mismatch`](../../tests/test_board_workflow.py) rejects a synthetic artifact whose digest differs from its manifest. | Exact bundle allowlist/layout/settings, stale source or lock, traversal/symlink/truncation/extra-file cases, and replacement races. |
| `OWN-01` — one active lab operation | [`test_contention_snapshot_finds_known_owner`](../../tests/test_board_workflow.py) detects a synthetic known owner; [`test_lock_released_after_exception`](../../tests/test_board_workflow.py) checks cooperating-lock release. | Cross-process, cross-checkout, cross-slot, and resource-contention cases, while retaining the documented limits of process snapshots and cooperating locks. |
| `BOUND-01` — no indefinite or retried action | [`test_build_and_flash_command_failure`](../../tests/test_board_workflow.py) checks command failure and the one-open-attempt environment; [`test_capture_closes_fd_on_error`](../../tests/test_board_workflow.py) checks descriptor cleanup; the serial outcome test covers synthetic timeout/disconnect/cap outcomes. | Hung process trees, local deadlines, output caps, lease loss, cancellation, failed opens, kernel stalls, and proof that no automatic recovery path runs. |
| `TEST-01` — no false fixture PASS | [`test_serial_pass_fail_missing_marker_silence_timeout_disconnect_and_cap`](../../tests/test_board_workflow.py) requires matching BOOT/PASS nonces and covers FAIL, stale PASS, silence, malformed bytes, disconnect, and byte cap. | Split/boundary markers, mismatched nonces, stale streams, crash/noise cases, and explicit prevention of peripheral or performance claims. |
| `EVID-01` — durable record for every admitted attempt | **No existing test method.** The current [`write_result`](../../tools/podlesp_board.py) helper writes bounded JSON, but that is implementation, not tested durability coverage. | Fault injection around consume/spawn, partial journals, disk-full/restart/ACK-loss cases, terminal escaping, and non-replay of admitted unknown attempts. |
| `TOPO-01` — no port or power overclaim | **No existing test method.** Topology and power remain documentary prerequisites, not facts established by host tests. | Port accounting and refusal of unknown topology/power approval; later physical evidence remains separately authorized and separately labelled. |

CI runs the current 11 methods in the repository's pinned Nix development shell
before the bounded smoke build. A passing suite proves only these offline
contracts; the smoke build remains compilation evidence only.
