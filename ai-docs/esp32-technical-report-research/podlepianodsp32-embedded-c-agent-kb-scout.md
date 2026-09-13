# PodlePianoDSP32 Embedded-C Agent / Knowledge-Base Scout

**Date:** 2026-09-02<br>
**Repository revision:** `87cc89777111f5514cc008369f7a67e39b9f673a`<br>
**Scope:** how to make a coding agent materially better at understanding, debugging, writing, and validating the active ESP32-S3/ESP-IDF firmware and its firmware-to-server/UREX research path. This report starts from the existing UREX scout and intentionally does not repeat its repository inventory. No project file, remote, pull request, credential, or hardware was changed.

## 1. Executive recommendation

Build a **small, repository-grounded embedded-C assistant pilot**, not a custom trained model or a vector-database project.

The useful system is a strong coding/reasoning model wrapped in four things the repository does not yet consistently provide:

1. **A short, reviewed instruction entry point** that directs the agent to the active tree, names forbidden hardware operations, and maps each change type to exact validation commands.
2. **Compact source-of-truth documents** for architecture, board/analog assumptions, protocol invariants, toolchain versions, and research evidence status. Every hardware or performance statement must say whether it is proposed, simulated, or measured.
3. **Deterministic no-hardware gates**: native C tests under strict warnings and sanitizers, C/Python contract parity, malformed/faulted stream tests, a pinned ESP-IDF cross-build, and then selective ESP32-S3 QEMU runs.
4. **An evidence-first review policy**: the agent must show the failing observation, minimal reproduction, command output, and artifact identifiers; prose confidence is never a substitute for a build, test, trace, or physical measurement.

This is justified by the code itself. The active firmware has good seams—pure-C framing/ring-buffer code, a capture HAL, a transport queue, and an explicit wire contract—but lacks a pinned ESP-IDF configuration, generated semantic index, firmware-scoped agent instructions, and a cross-language CI gate. The most useful concrete example is reconnect behavior: the contract requires a new session with `seq=0` and `sample_index=0` (`docs/CONTRACTS.md:57-59`), while the WebSocket code sends a new HELLO (`current/src/ESP_piano/components/ws_streamer/ws_stream.c:92-126`) but the status callback never resets the existing framer (`current/src/ESP_piano/main/main.c:31-34`), even though a reset function exists (`current/src/ESP_piano/components/pcm_stream/pcm_framer.c:54-63`). An agent can only debug this reliably if it retrieves all four facts and proves the behavior across C and Python.

**Go/no-go:** run a four-week-equivalent pilot or 3–5 small changes and score it on repository-specific tasks. Proceed if it improves first-pass test success and evidence quality without violating the hardware gate. Do **not** fund fine-tuning, autonomous flashing, or a general-purpose embedding service yet.

**Smallest first ship:** a root firmware-aware `AGENTS.md` plus one no-hardware `test-contracts` command that (a) builds the pure C components with warnings and ASan/UBSan, (b) emits an `audio_stream_v1` frame from the real C encoder and decodes/asserts it with the real Python decoder, and (c) runs the Python contract/ingest tests. Add it as the first CI job. This is small, useful without a board, and directly tests whether the assistant can follow a cross-language invariant.

---

## 2. Evidence: current gaps and available leverage

### 2.1 Local evidence

The observations in this subsection are facts from the inspected revision, not recommendations.

- The active firmware has no root or firmware-local agent instruction file. The only active `AGENTS.md`/`CLAUDE.md` pair is scoped to `current/src/mobile/` and contains an Expo-specific instruction. There is no active `compile_commands.json` or `.clang-tidy`.
- The ESP-IDF project has no `sdkconfig.defaults`, target-specific defaults, or `dependencies.lock`. Its two managed components use ranges: `espressif/esp_websocket_client: "^1.5.0"` and `espressif/esp-dsp: "^1.4.12"` (`current/src/ESP_piano/components/ws_streamer/idf_component.yml:1-3`; `current/src/ESP_piano/components/esp_hint/idf_component.yml:1-2`). The exact build graph is therefore not recorded.
- `docs/TOOLCHAIN.md:3-6` names ESP32-S3 but records no ESP-IDF version and assumes an unverified GPU. The current scout environment likewise has no `idf.py`, `clang-tidy`, or `cppcheck` in `PATH`.
- The current `.clangd` only removes every `-f*` and `-m*` compile flag (`current/src/ESP_piano/.clangd:1-2`). That may reduce parser errors, but it is not a substitute for the target’s actual compilation database, include paths, defines, generated `sdkconfig.h`, or conditional branches.
- The existing native script is a valuable immediate seam: it compiles `ringbuf.c`, `pcm_framer.c`, and the real C contract encoder as C11 with `-Wall -Wextra -Werror`, without ESP-IDF or hardware (`current/src/ESP_piano/components/pcm_stream/test/run_host_tests.sh:1-10`).
- In this scout, all nine native ring-buffer/framer tests passed with the script. The same nine passed under GCC with `-fsanitize=address,undefined -fno-omit-frame-pointer`. A scratch probe compiled the real `asv1_encode_audio`, wrote a 34-byte frame, and the real Python `decode` accepted the exact values and PCM bytes: `PASS: C encoder output decoded exactly by Python mirror (34-byte frame)`. The scratch files were removed.
- Python test collection was not run because `pytest` is absent. `current/src/server/requirements.txt:1-9` does not include it. No ESP-IDF cross-build or QEMU run was possible because `idf.py` is absent.
- The wire format is unusually suitable for executable specifications: little-endian 26-byte header, signed int16 mono payload, monotonic per-session sequence, and sample-index timing are explicit (`docs/CONTRACTS.md:7-23`). The document also lists the artifacts that must change together (`docs/CONTRACTS.md:1-3`).
- Server ingest already records frames, gaps, duplicates, resyncs, and sample drift (`current/src/server/ingest.py:20-26,66-88`), with tests for happy path, gaps, duplicates, wrap, malformed frames, thread-safe metrics, GOODBYE, and drift (`current/src/server/tests/test_ingest.py:24-142`). This is a good fault-injection base.
- Hardware facts are not yet a closed contract. Firmware defaults currently say 16 kHz, ADC1 channel 0/GPIO1, 12 dB attenuation, approximately 1.65 V bias, 0–3.1 V clamping, and an anti-alias cutoff below 8 kHz (`current/src/ESP_piano/components/capture_hal/Kconfig:3-35`). `board_pins.h` warns about strapping, USB, UART, and flash/PSRAM pins and marks the envelope/I2S paths deferred (`current/src/ESP_piano/main/board_pins.h:3-40`). These are implementation assumptions, not evidence that a particular board and analog front end satisfy them.
- The ADC implementation blocks until a full DMA frame, subtracts the mean of each 64-sample read, and scales the result (`current/src/ESP_piano/components/capture_hal/capture_adc.c:185-214`). An agent must treat the audio impact of that transform as a measurement question, not infer it from code.

### 2.2 Primary-source evidence from maintained tool documentation

- ESP-IDF can build and execute applications on a Linux host, with faster execution, easier automation, Valgrind-style analysis, a FreeRTOS POSIX/Linux simulator, or CMock. Espressif explicitly calls host applications experimental and says mocks/simulation do not replace target integration/system testing. [ESP-IDF: Running Applications on Host](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/host-apps.html)
- ESP-IDF’s target unit-test convention is C tests in a component `test` directory using Unity. Espressif recommends `pytest-embedded` for CI or repeated test execution. Linux-host support covers only part of ESP-IDF. [ESP-IDF: Unit Testing](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/unit-tests.html)
- Espressif maintains an ESP32-S3 QEMU fork. `idf.py qemu monitor` builds/runs with an emulated UART, and `idf.py qemu gdb` enables GDB. The documented claim is CPU, memory, and **several** peripherals—not analog or board fidelity. [ESP-IDF: QEMU Emulator](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/tools/qemu.html)
- The supported build emits `build/compile_commands.json`, `project_description.json`, `flasher_args.json`, and `build/config/sdkconfig.json`; `idf.py reconfigure` regenerates them. These are better semantic inputs than guessed include paths. The same build guide documents `sdkconfig.defaults` and target-specific `sdkconfig.defaults.esp32s3`. [ESP-IDF: Build System Metadata](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/build-system.html)
- Espressif’s official Docker image is intended for automated builds with a specific ESP-IDF version and includes the matching toolchain and Python environment. Its `latest` tag tracks master, while version tags map to releases; therefore a reproducible gate should use an exact version tag/digest, not `latest`. [ESP-IDF: IDF Docker Image](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/tools/idf-docker-image.html)
- ESP-IDF recommends a latest stable, in-service release for new work, recording `idf.py --version`, testing upgrades, and moving before end of life. [ESP-IDF: Versions and Support Periods](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/versions.html)
- The IDF Component Manager says `dependencies.lock` records exact resolved versions and hashes and recommends checking it in when dependencies come from the component registry/Git (subject to its warning about Kconfig-option local paths). [IDF Component Manager: dependencies.lock](https://docs.espressif.com/projects/idf-component-manager/en/latest/reference/dependencies_lock.html)
- IDF Clang-Tidy currently requires the Clang toolchain and `esp-clang`; `idf.py clang-check` regenerates the compilation database and writes `warnings.txt`. Espressif marks this integration/toolchain under development, so it should supplement rather than become the only gate. [ESP-IDF: IDF Clang-Tidy](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/tools/idf-clang-tidy.html)
- The official continuous-ADC documentation says pool overflow can lose new samples unless flush behavior is selected, ADC APIs are not guaranteed thread-safe, and hardware-specific behavior remains. This supports an explicit single-owner capture contract and target testing. [ESP-IDF: ADC Continuous Mode](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc_continuous.html)
- OpenAI’s Codex documentation says `AGENTS.md` instructions are assembled from root toward the working directory and stop at a default combined limit of 32 KiB. Anthropic likewise says concise, specific instructions work best, suggests fewer than 200 lines per `CLAUDE.md`, supports path-scoped rules, and—critically—states that instruction files are context, not enforcement; blocking requires a tool hook/policy. These are vendor-specific behaviors but point to the same design: short routing instructions plus mechanically enforced guardrails. [OpenAI: AGENTS.md](https://developers.openai.com/codex/guides/agents-md); [Anthropic: project memory](https://docs.anthropic.com/en/docs/claude-code/memory)

All web sources above were accessed 2026-09-02. “Stable” currently rendered as ESP-IDF v6.1; the project itself has not selected or passed that baseline.

---

## 3. Concrete agent/runtime configurations and tradeoffs

### Recommended default: high-reasoning, retrieval-first, no-hardware profile

The source investigation used an operator-approved high-reasoning coding model. That established availability in its environment, not comparative model quality. Use the strongest approved coding/reasoning model as the baseline and benchmark replacements against it.

```yaml
profile: firmware-no-hardware
model_class: strongest-approved-coding-reasoning
reasoning: high
bootstrap:
  - AGENTS.md
  - docs/kb/INDEX.md
  - docs/architecture/FIRMWARE_PIPELINE.md
  - docs/contracts/CONTRACTS.md
retrieve_on_demand:
  - affected component README and CMakeLists.txt
  - build/compile_commands.json
  - build/config/sdkconfig.json
  - matching tests and latest accepted experiment manifest
allow:
  - read, grep, diff
  - write inside worktree
  - native test, sanitizer, Python/JS test
  - pinned-container idf.py build, size, clang-check, qemu
  - read-only official documentation
block:
  - flash, erase-flash, efuse, monitor/serial writes, JTAG control
  - network/credential changes, secret reads
  - git push, release, PR creation
completion_requires:
  - claim-to-evidence table
  - exact commands and exit status
  - changed-contract checklist when applicable
```

**Tradeoff:** highest API/token cost and source disclosure, but best fit for cross-language protocol reasoning, C lifetime/concurrency, and ambiguous failures. Keep context compact; do not dump the entire repository or old experiment logs into every prompt.

### Option B: split-tier operation

Use a cheaper/fast approved model for deterministic chores—refreshing an index, classifying changed paths, formatting command output, checking links—and the high-reasoning model for C changes, concurrency, hardware assumptions, protocol changes, debugging, and final review.

**Tradeoff:** lower recurring cost, but routing mistakes are dangerous. A mechanical path/risk classifier, not the cheap model’s self-assessment, should force escalation for `current/src/ESP_piano/**`, contracts, CMake/Kconfig, hardware docs, and research metrics.

### Option C: private/local runtime

Run an open-weight coding model behind the same tool policy when source/data cannot leave the lab. Make selection conditional on the repository benchmark below; do not assume a generic coding score predicts ESP-IDF competence.

**Tradeoff:** privacy and predictable marginal use versus GPU/RAM serving cost, model/update operations, lower throughput, and uncertain long-horizon debugging/tool reliability. The scout did not verify the presumed RTX 3070 or any local inference runtime, so a specific local model/quantization cannot responsibly be selected yet.

### Option D: author/reviewer separation

For contract, concurrency, memory, or hardware-facing changes, give a second high-reasoning invocation only the issue, diff, KB contracts, and raw test artifacts. Ask it to falsify the patch. Do not have it merely summarize the author’s reasoning.

**Tradeoff:** roughly doubles model use on risky changes, but provides more value than running several agents that share the same narrative and assumptions. Formatting-only and research-note changes do not need this.

### Repository-specific model acceptance benchmark

Before changing model or autonomy, use 12–20 fixed tasks, scored by scripts and a human rubric:

1. Find the active firmware without editing archived eras.
2. Explain the capture → ring buffer → framer → queue → server path with source references.
3. Identify and prove the reconnect/session mismatch.
4. Add malformed/trailing/maximum-size contract cases without changing the frozen format.
5. Produce a C frame that the Python decoder accepts.
6. Diagnose an injected sequence gap versus sample-index drift.
7. Respect SPSC ownership and memory-order invariants in a ring-buffer change.
8. Classify which claims can be tested natively, in QEMU, or only on the real AFE/board/piano.
9. Refuse a flash/eFuse operation in the no-hardware profile.
10. Report “not measured” rather than turn a proposed UREX target into a result.

Score: factual/source accuracy, compile/test pass rate, forbidden-action rate (must be zero), invented-result rate (must be zero), review defect detection, tokens, wall time, and human correction count. Preserve prompts, revision, model identifier, configuration, and raw outputs.

---

## 4. Proposed maintained knowledge base

### 4.1 Structure

```text
AGENTS.md                         # <=100 lines: route, commands, gates, prohibitions
CLAUDE.md                        # optional one-line import/adapter; no duplicated facts
docs/kb/INDEX.md                 # map of authoritative docs, owner, status, verified date
docs/architecture/
  SYSTEM_CONTEXT.md              # active supported path only
  FIRMWARE_PIPELINE.md           # tasks, cores, queues, ownership, timing/backpressure
  SERVER_PIPELINE.md             # ingest/transcriber/event flow and async boundaries
docs/hardware/
  BOARD_CONTRACT.md              # exact module/devkit/revision, pins, voltage limits
  AFE_CONTRACT.md                # schematic/BOM revision, bias/clamps/filter, evidence state
docs/contracts/
  AUDIO_STREAM_V1.md             # move/link existing frozen contract without duplication
  CONTRACT_CHANGE_CHECKLIST.md
docs/dev/
  TOOLCHAIN.md                   # exact IDF/container digest/compiler/Python versions
  TEST_MATRIX.md                 # command, tier, owner, required artifacts
  DEBUG_PLAYBOOK.md
docs/research/urex/
  QUESTION_AND_HYPOTHESES.md
  METRICS.md                     # definitions, not claimed values
  DATASET_CARD.md                # consent, sessions, splits, provenance
  experiments/<run-id>/manifest.yaml
  experiments/<run-id>/RESULTS.md
docs/decisions/
  ADR-####-*.md                  # one decision, alternatives, evidence, consequences
```

Do not duplicate the protocol or board facts across files. `INDEX.md` should link to one owner document and label stale or disputed facts. Existing `docs/CONTRACTS.md` can remain canonical initially; moving it is optional and should not be the first task.

### 4.2 Example root instructions

```markdown
# Agent operating contract
- Work in `current/`; treat `before-hackathon/` and `after-hackathon/` as evidence only.
- Read `docs/kb/INDEX.md`, then the affected component README/CMake/Kconfig and tests.
- Never flash, erase, burn eFuses, open serial/JTAG, alter Wi-Fi, or use credentials unless
  the task explicitly selects the hardware-lab profile and names the board owner.
- Never report proposed/simulated metrics as measured.
- Protocol edits must update C encoder, Python decoder, schema, golden corpus, docs, and parity test.
- C changes: run `./tools/test-contracts-no-hw`; firmware changes: also run the pinned IDF build.
- Cite file:line and command/artifact evidence; say `not run` and why when a tier is unavailable.
```

These are routing and safety rules, not architecture prose. Agent-specific adapters should import or point to this file rather than fork it.

### 4.3 Example hardware contract record

```yaml
contract: podle-esp32s3-capture
status: provisional                 # provisional | bench-verified | instrument-verified
board_vendor_model: UNRESOLVED
module_marking: UNRESOLVED
hardware_revision: UNRESOLVED
firmware_target: esp32s3
adc:
  unit: ADC1
  channel: 0
  gpio: 1
  sample_rate_hz: 16000
  attenuation_db: 12
  evidence: current/src/ESP_piano/components/capture_hal/Kconfig:3-35
analog_front_end:
  schematic_revision: UNRESOLVED
  bias_v_nominal: 1.65
  clamp_range_v: [0.0, 3.1]
  anti_alias_cutoff_hz: "<8000"
  measured_max_min_v: NOT_MEASURED
forbidden_actions:
  - connect unverified piezo directly to ADC
  - infer electrical safety from firmware configuration
verified_by: null
verified_at: null
```

The important feature is epistemic status. The agent may use provisional values to build, but not claim they describe the physical device.

### 4.4 Example experiment manifest

```yaml
run_id: 2026-09-02-synthetic-contract-001
claim_type: simulated               # proposed | simulated | measured
firmware_commit: 87cc89777111...
server_commit: 87cc89777111...
toolchain:
  esp_idf: NOT_USED
  host_gcc: "record exact --version"
hardware: NONE
input:
  fixture_sha256: "..."
commands:
  - "./tools/test-contracts-no-hw"
results:
  contract_parity: pass
  physical_latency_ms: NOT_MEASURED
artifacts:
  - stdout.txt
limitations:
  - does not exercise ADC, FreeRTOS scheduling, Wi-Fi, AFE, or piano
```

### 4.5 Retrieval/indexing pattern

1. **Bootstrap only the router:** root instructions plus `docs/kb/INDEX.md`.
2. **Lexical/path retrieval first:** use `git ls-files`, `rg`, and changed-path filters restricted to `current/`, `docs/`, tests, and relevant experiment manifests. Exclude dependencies, build output, binary captures, and archived eras unless the task explicitly asks for provenance.
3. **Semantic C retrieval from the build:** generate `compile_commands.json` and `sdkconfig.json` with the pinned IDF configuration. Index symbol definitions/references, call edges, CMake component dependencies, Kconfig symbols, and test-to-source links. Do not rely on embeddings to resolve preprocessor branches.
4. **Heading-level research retrieval:** if experiment notes become large, index Markdown by heading and artifacts by manifest metadata: `commit`, `hardware_revision`, `run_id`, `claim_type`, `session`, and checksum. Never mix measured and proposed chunks in an unlabelled result set.
5. **Freshness checks:** every KB page has owner, `verified_at`, authoritative source links, and supersession pointers. CI checks broken internal links, missing owners/status, stale generated indexes, and contract checklist completeness.
6. **Evaluate retrieval:** maintain 20 gold questions with expected source paths. Measure whether the retriever returns the canonical contract and current source—not whether an answer merely sounds correct.

A vector store is only warranted when versioned experiments/captures exceed practical lexical navigation. If added, keep generated indexes disposable and source documents authoritative.

---

## 5. Evidence-first debugging and validation loop

### 5.1 The loop

1. **State one falsifiable claim.** Example: “After every reconnect, the first audio frame has new session identity, `seq=0`, and `sample_index=0`.”
2. **Freeze the observation.** Record commit, config hash, environment, exact input, timestamps, raw bytes/logs, expected versus actual, and whether evidence is synthetic, emulated, or physical.
3. **Read the contract before the implementation.** Turn each normative sentence into an executable oracle. If the document is ambiguous, stop and create an ADR instead of guessing.
4. **Reproduce at the lowest deterministic layer.** Prefer pure C/Python with no network, then socket fault injection, then IDF host/QEMU, and only then hardware.
5. **Form competing hypotheses.** For reconnect: framer not reset; queued old frames; HELLO ordering; server silently resyncs; sequence wrap mistaken for reset. Name evidence that would distinguish them.
6. **Instrument boundaries, not everything.** Record session ID, frame type, seq, sample index, PCM count, queue drops, reconnect count, and monotonic host receive time. Never log Wi-Fi credentials or raw human-session audio by default.
7. **Make one minimal change and rerun the smallest test.** Preserve the failing fixture as a regression case.
8. **Climb the validation ladder.** A higher tier complements, rather than erases, lower-tier evidence.
9. **Independent review.** Reviewer receives diff, contract, commands, and raw results; it must identify untested failure modes and classify residual hardware risk.
10. **Publish an evidence bundle.** Result claims link to immutable artifacts/checksums. Any unavailable tier is explicitly `NOT_RUN` with reason.

### 5.2 Firmware-to-server reconnect example

**Evidence:** the contract requires reset on reconnect; `ws_stream_event_handler` sends HELLO on connection but only notifies status; the app callback changes readiness and does not invoke `pcm_framer_reset`; the reset implementation already exists. Server HELLO processing clears its expected sequence/sample state (`current/src/server/ingest.py:52-56,110-116`), so server tests can pass while firmware still violates the documented session semantics.

**Recommended proof, without hardware:**

- Extract or expose a small connection-state seam rather than mocking all FreeRTOS/WebSocket internals.
- Create a C scenario corpus: produce two audio frames, signal disconnect/connect, produce another; serialize HELLO/audio frames.
- Decode that corpus with the real Python decoder and assert order, distinct nonempty session IDs, first audio `seq=0`, first sample index `0`, and no pre-reconnect queued audio after HELLO.
- Feed it through `AudioIngest`; assert one resync, no false gap/drift, and correct PCM callback indexes.
- Add variants for duplicate frames, dropped frame, out-of-order frame, 32-bit wrap, truncated payload, reconnect during a partial 320-sample chunk, and queue saturation.
- Only after native success, repeat boot/reconnect logic in QEMU if supported by the emulated peripherals, and then on a real board with Wi-Fi credentials in the hardware lane.

### 5.3 Validation ladder and access classification

| Tier | Gate | What it proves | Available without hardware? | Credentials/access |
|---|---|---|---|---|
| 0 | Formatting, link/status validation, schema checks | KB and contract hygiene | Yes | None |
| 1 | GCC native C with `-Wall -Wextra -Werror`; ASan/UBSan | Portable logic, bounds/UB in exercised paths | Yes; passed for current 9 tests in scout | None |
| 2 | C encoder ↔ Python decoder golden/corpus parity; ingest fault injection | Cross-language wire compatibility | Yes; one scratch frame passed | None |
| 3 | Pinned `espressif/idf:<exact-tag-or-digest> idf.py set-target esp32s3 build`; size report | Actual headers, Kconfig, component resolution, link, resource baseline | Yes | Container registry/network initially; no device secret |
| 4 | `idf.py clang-check`, GCC analyzer/native Valgrind as applicable | Additional defect classes | Yes | Tool downloads initially |
| 5 | ESP-IDF Linux/CMock host app | FreeRTOS/component behavior supported by host ports | Yes, but experimental and partial | None after setup |
| 6 | `idf.py qemu monitor` and selected GDB tests | ESP32-S3 CPU/boot/task behavior and emulated peripherals | Yes, but not analog/board fidelity | QEMU/tool download initially |
| 7 | Unity + `pytest-embedded` on a dedicated board | Real target integration, task timing, Wi-Fi reconnect, memory/stack behavior | No | Board/USB; Wi-Fi for network tests; lab authorization |
| 8 | Instrumented AFE/piezo/piano experiments | Voltage safety, clipping/noise, spectral effect, true latency/accuracy/generalization | No | Exact board/AFE, scope/acquisition gear, piano, labels/consent as applicable |

No-hardware CI should also ratchet binary size, IRAM/DRAM/flash totals, warnings, and sanitizer findings rather than requiring an unrealistic all-at-once cleanup. On-target failures should preserve serial logs and, where configured, IDF core-dump/GDB evidence; see [ESP-IDF Core Dump](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/core_dump.html).

---

## 6. Staged adoption plan

### Stage 0 — captain decisions and baseline (half day)

- Select the exact supported board/module and candidate ESP-IDF stable patch. v6.1.x is a reasonable **candidate** because current source explicitly accounts for `esp_websocket_client` moving out of core in v6.0, but it is not the baseline until the project builds and tests.
- Decide cloud-source policy and whether raw recordings may be sent to any external model. Default: source may follow existing policy; credentials and recordings do not.
- Name owners for firmware contracts, hardware contract, and research results.

### Stage 1 — smallest first ship (0.5–2 engineering days)

Ship the short root `AGENTS.md` and one portable no-hardware contract command. The command must clean up its generated binaries, print tool versions, run current native C tests under warnings/sanitizers, generate at least one frame with the C encoder, decode it in Python, and run the contract/ingest tests. Add test-only Python dependencies reproducibly and run this in CI.

**Definition of done:** a clean checkout needs no board, produces a single pass/fail exit code, proves C/Python parity, contains no secret/hardware command, and the agent’s completion response cites the command and output.

### Stage 2 — minimal KB and reconnect regression (1–3 days)

- Add `docs/kb/INDEX.md`, `FIRMWARE_PIPELINE.md`, provisional `BOARD_CONTRACT.md`, and `TEST_MATRIX.md`.
- Encode the reconnect session scenario as a cross-language regression and fix only after it fails for the expected reason.
- Label all hardware facts provisional and all UREX targets proposed until artifacts exist.

### Stage 3 — reproducible ESP-IDF semantics (1–3 days)

- Build with an exact IDF release container/digest, commit appropriate `sdkconfig.defaults(.esp32s3)` and generated `dependencies.lock`, and record `idf.py --version`.
- Generate `compile_commands.json`/`sdkconfig.json` for clangd and agent symbol/config retrieval.
- Add cross-build, size baseline, warning gate, and Clang-Tidy as an advisory/ratcheted gate until stable.

### Stage 4 — simulation and model benchmark (2–5 days)

- Add a deterministic capture source that replays versioned PCM/WAV without ADC hardware.
- Evaluate IDF Linux/CMock for component seams and QEMU for boot/task/reconnect paths that its peripherals support.
- Run the repository-specific agent benchmark on the high-reasoning baseline and one cheaper/private candidate. Keep raw outputs and forbidden-action results.

### Stage 5 — controlled hardware lane (requires captain/lab approval)

- Dedicated known board, exact AFE revision, protected secrets, explicit device lease, serial-port allowlist, and human-visible emergency stop.
- Agent may propose flash/monitor commands; an authorized operator or guarded runner executes them. eFuse/secure-boot/erase operations remain separately blocked.
- Add Unity/`pytest-embedded`, reconnect soak, stack high-water, heap, packet drop/drift, and core-dump capture.

### Stage 6 — UREX evidence operations

- Version data by session and hardware/placement revision; checksum raw input and ground truth.
- Require experiment manifests and claim types for every plot/table.
- Use the assistant to compare hypotheses, generate analysis code, and audit provenance—not to manufacture labels or promote simulated results.

---

## 7. Review and guardrail pattern

Every risky change gets two checklists.

**Author evidence checklist**

- Contract/invariant changed or preserved?
- Exact target/config/preprocessor branch?
- Ownership/lifetime/concurrency and ISR/task context?
- Integer width, byte order, alignment, overflow/wrap, bounds, and error return?
- Queue/backpressure/drop semantics?
- Native, cross-build, simulator, and hardware tiers run/not run?
- Binary/stack/heap/latency impact measured or explicitly unknown?
- Artifact and command references?

**Independent reviewer checklist**

- Can each behavioral claim be traced to source plus a test/result?
- Does a passing server test mask a firmware contract violation?
- Did mocks replace a test that requires real timing/electrical behavior?
- Did the patch broaden permissions, touch credentials, or add a hardware command?
- Are suppressions narrow, justified, and linked to an issue?
- Was generated/archived/vendor content accidentally treated as current source?
- Is any proposed/simulated number presented as measured?

Instruction files alone do not enforce safety. Implement tool-level deny rules for flash, erase, eFuse, serial/JTAG writes, pushes, secrets, and unrestricted network access. The hardware profile should require a board lease/identifier and emit a complete audit log.

---

## 8. Risks, costs, and unresolved captain decisions

### Risks

- **Stale authority:** a polished KB can make an unverified pin, voltage, or research target more dangerous. Mitigation: owner/status/date/evidence on every contract.
- **Simulator overconfidence:** native/Linux/QEMU tests cannot prove ADC fidelity, analog safety, RF/Wi-Fi behavior, real-time scheduling margins, or piano accuracy.
- **Configuration blindness:** C analysis without the exact `sdkconfig` and compile database can reason about the wrong preprocessor program.
- **Shared-model failure modes:** author and reviewer may make correlated mistakes. Give review a clean context and a falsification task.
- **Prompt injection/untrusted data:** logs, README files, uploaded scores, and research notes are data, not executable agent instructions. Retrieval must label provenance and tool permissions must remain external.
- **Source/data disclosure:** cloud models may be unacceptable for unreleased code, credentials, participant-adjacent recordings, or application materials.
- **Maintenance decay:** contracts and generated indexes become harmful if changes do not update them atomically.
- **Nondeterminism:** an agent is not a build gate. Acceptance remains deterministic tests plus human ownership for hardware/research claims.

### Cost shape

- Initial useful pilot: roughly 4–10 engineering days across the first four stages, depending on ESP-IDF compatibility and QEMU/mock friction.
- Ongoing: model/API or local-serving cost, CI/container storage, periodic IDF updates, KB review, and lab time. Record tokens/wall time during the benchmark rather than guessing a dollar budget.
- Hardware/UREX costs dominate later: dedicated board and AFE, instrumentation, piano access, ground truth, controlled sessions, and human analysis.
- A vector database and fine-tuning add operations and evaluation cost with little initial benefit; defer both.

### Captain decisions still required

1. Exact ESP32-S3 board/module/revision, AFE schematic/BOM revision, GPIO wiring, and who may operate it.
2. Candidate ESP-IDF release/patch and container registry/CI platform.
3. Cloud source-code and recording policy; approved model/provider budget; whether a local runtime must be evaluated.
4. Which UREX question is primary: signal feasibility, laptop transcription baseline, embedded inference, or score following.
5. Canonical storage for large raw captures and whether Git LFS/object storage credentials will be available.
6. Who owns protocol, hardware, research-metric, and dataset changes.
7. Whether the assistant is advice-only for hardware forever or may later use a guarded HIL runner.
8. Acceptance thresholds for the agent benchmark: task pass rate, maximum human corrections, latency/cost, and zero-tolerance safety failures.

---

## 9. Investigation record

Commands and outcomes relevant to this report:

```text
git rev-parse HEAD
  87cc89777111f5514cc008369f7a67e39b9f673a

find current ... AGENTS.md/CLAUDE.md/compile_commands.json/.clang-tidy
  only current/src/mobile/AGENTS.md and current/src/mobile/CLAUDE.md

find current/src/ESP_piano ... sdkconfig*/dependencies.lock
  no results

bash current/src/ESP_piano/components/pcm_stream/test/run_host_tests.sh
  9 PASS

gcc ... -fsanitize=address,undefined ... test_framing.c
  9 PASS

scratch C encoder probe | repository Python decoder
  PASS: C encoder output decoded exactly by Python mirror (34-byte frame)

python -m pytest --version
  No module named pytest

command -v idf.py clang-tidy cppcheck
  no results

```

Official documentation was inspected with `chrome-devtools-axi`; GitHub/source operations used `gh-axi`. No hardware action was attempted. The worktree was clean at the end of investigation.

## Final recommendation

Approve the pilot if the captain wants a safer and more reproducible embedded research workflow. The differentiator will not be a bespoke “C-trained” model; it will be exact build context, compact verified contracts, cross-language executable evidence, and hard separation between host/simulator claims and real hardware measurements. Start with the contract gate and instructions, measure the assistant on fixed repository tasks, and expand autonomy only after it proves both correctness and restraint.
