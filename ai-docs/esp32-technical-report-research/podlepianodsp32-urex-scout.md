# PodlePianoDSP32 / UREX Scout Report

Date: 2026-08-24<br>
Repository: `https://github.com/podledges/PodlePianoDSP32`<br>
Inspected revision: `87cc89777111f5514cc008369f7a67e39b9f673a` (`main`, merged 2026-08-18)<br>
Scope: read-only repository and local-evidence investigation. No hardware was flashed or driven, no remote was changed, and no Windows or global configuration was modified.

## Executive answer for the captain

PodlePianoDSP32 is best presented as a recovered research platform for contact-sensor piano understanding, not as a finished piano-learning product. Its strongest implemented work is an ESP32-S3 signal acquisition and streaming pipeline, explicit cross-language data contracts, a laptop ingest/transcription skeleton, reusable measurement harnesses, and a score-following prototype. Its strongest research direction exists in a separate local design vault: detect all currently sounding piano notes, including chords, from a piezo-captured vibration signal using a small quantized neural network running on the ESP32.

The central UREX gap is evidence. The repository contains plans, fixtures, simulators, and a detailed physical test protocol, but no real piezo recordings, labeled piano dataset, latency report, accuracy report, field logs, or completed experiment record. Some demo surfaces are also incompatible or intentionally fabricated. The captain should make the proposal about measuring feasibility and tradeoffs, then produce a small, auditable pilot dataset before claiming accuracy, latency, automatic page turning, Gemini OMR, or on-device polyphonic inference.

The first shippable task should be a truthful `current/README.md` plus a one-command, fake-transcriber smoke path that identifies the one supported architecture, fixes paths broken by the repository restructure, records what is and is not real, and provides a results table whose unmeasured fields are visibly marked `TBD`. This is narrow, useful for a proposal immediately, and creates the runbook needed for the first physical experiment.

## 1. What the project currently is

### Repository eras and provenance

The root is an archive-plus-active-tree repository:

- `before-hackathon/` is the frozen pre-hackathon snapshot.
- `after-hackathon/` is the frozen post-hackathon snapshot.
- `current/` is the active codebase.
- `docs/` is described as living documentation and `data/` as the home for captures and datasets.

This is explicit in `README.md:5-15` and the pinned commits and tags are recorded in `docs/ERA_SNAPSHOTS.md:5-15`. Git history contains 41 commits from 2026-06-03 through 2026-08-18. Much of the integrated system landed in a concentrated hackathon burst on 2026-06-27, followed by a salvage audit and firmware modularization on 2026-08-02, and the era-folder restructure on 2026-08-17/18. The repository has multiple contributors. That history is useful evidence of iteration, but contribution ownership should be documented before a research application.

### Implemented system pieces

#### A. ESP32-S3 acquisition and streaming firmware

The live firmware is not merely a sketch. `current/src/ESP_piano/main/main.c:20-24,36-61,63-114` wires a real pipeline:

1. ADC capture is pinned to core 1.
2. Samples feed an atomic single-producer/single-consumer ring buffer.
3. A framer emits network frames from core 0.
4. A bounded WebSocket transmitter sends those frames to the laptop.
5. An optional ESP-DSP FFT hint path receives the same samples.
6. Ten-second network metrics report sent, reconnected, and dropped counts.

Six reusable ESP-IDF components and their seams are documented in `current/src/ESP_piano/components/README.md:1-46`: `asv1_contracts`, `pcm_stream`, `capture_hal`, `ws_streamer`, `wifi_sta`, and `esp_hint`.

Continuous ADC/DMA capture is implemented in `current/src/ESP_piano/components/capture_hal/capture_adc.c:34-42,82-140,155-216`. It keeps a persistent raw buffer, reads at the configured sample rate, removes the mean of each sample block, scales to signed 16-bit PCM, and uses ADC1. Wi-Fi credentials now have their own Kconfig entries at `current/src/ESP_piano/components/wifi_sta/Kconfig:1-16`. The reference configuration is 16 kHz on ESP32-S3 ADC1 channel 0, which maps to GPIO1 (`current/src/ESP_piano/components/capture_hal/Kconfig:3-19`).

The ring buffer now enforces power-of-two capacity and uses C11 atomics (`current/src/ESP_piano/components/pcm_stream/ringbuf.c:3-17,20-59`). This addresses defects identified during salvage. The WebSocket component isolates the capture path behind an eight-frame queue and maintains drop/reconnect metrics (`current/src/ESP_piano/components/ws_streamer/ws_stream.c:16-35,61-80`).

#### B. Explicit firmware-to-server contracts

`audio_stream_v1` is a documented 26-byte binary header carrying sequence number, absolute sample index, timestamp, sample rate, channel count, and PCM length (`docs/CONTRACTS.md:1-33`). The sample index is intended to be the timing source of truth. A C encoder and Python decoder exist, as does `note_events_v1` with a JSON schema (`docs/CONTRACTS.md:35-59`).

The Python ingest layer tracks duplicates, gaps, session resync, and sample-index drift. The repository's salvage audit identifies this as one of the strongest reusable modules (`docs/SALVAGE.md:165-185`).

#### C. Laptop server and transcription adapters

The FastAPI server serves `/`, `/health`, raw audio WebSocket `/stream`, and note WebSocket `/notes` (`current/src/server/app.py:165-232`). It supports a deterministic fake transcriber and a Basic Pitch adapter (`current/src/server/app.py:259-281,288-307`).

The Basic Pitch adapter buffers two seconds of audio with one-second overlap and produces note events (`current/src/server/transcriber/basic_pitch.py:47-138`). That makes a laptop-side polyphonic baseline possible, although it is not yet a low-latency or production-quality implementation.

#### D. Score following and page-turn prototype

The JavaScript score follower normalizes several score shapes, groups chords, compares observed notes, and tracks progress. `current/src/final_bar_matching/full_score_progress_tracker.js:292-370` tries the next event, current-bar restart, current-page restart, and limited backward recovery, then emits progress and boundary events.

The separate Node server accepts PDFs, simulates note inputs, feeds the score tracker, and broadcasts page-turn events. Its `/transcribe` endpoint deliberately fabricates OMR data (`current/src/server/index.js:159-198,238-305`). This proves interaction flow only, not sheet-music recognition.

#### E. Test and measurement scaffolding

The repository already contains unusually useful experiment infrastructure:

- A C-major WAV/MIDI fixture pair under `current/src/fixtures/`.
- A synthetic real-time stream replay tool.
- A golden accuracy checker using precision, recall, and F1 with a minimum F1 gate of 0.50.
- A latency harness that calculates p50 and p95 and writes JSON results.
- A detailed physical test guide with placement guidance, tests T1-T9, pass/fail criteria, troubleshooting, and an artifact checklist (`docs/PHYSICAL_TEST_GUIDE.md:206-240,244-384,579-635`).
- A frozen protocol specification and fixture tests.
- JavaScript simulator suites for score following and browser integration.

In this scout environment, the milestone 4 score simulator and browser integration simulator passed under Node 24.19.0. The parallel repository inventory ran all six score simulators, and all six passed. The C host tests could not start because `cc`/`gcc` is absent. The Python tests could not start because `pytest` is absent. The Vite build could not start because dependencies are not installed. The ESP-IDF build could not be attempted because `idf.py` is absent. These are environment limitations, not passing results.

## 2. What is missing, broken, stale, or risky

### Research evidence is missing

This is the most important deficiency for UREX.

- `data/README.md:1-5` is only a placeholder.
- No real piezo WAV captures, labeled MIDI sessions, placement photos, ESP serial logs, server logs, latency JSON, accuracy JSON/CSV, T19 result document, or experiment notebook was found in the repository.
- The local vault explicitly says `nothing run yet` and expects the first experiment at Milestone M1 (`[private local evidence archive]/PodleNote/obby/implementation_plans.md:24-29`).
- Success targets such as frame F1 at least 0.85 and latency at most 150 ms are proposals, not measurements (`.../obby/Project Overview.md:41-45`).

The proposal may state these as hypotheses or acceptance targets. It should not state that the system achieves them.

### The repository contains two different project centers

The recovered hackathon code centers on ESP32 audio streaming to a laptop, laptop transcription, UI visualization, score following, and automatic page turning. The later local design vault centers on fully on-device polyphonic note detection using log-frequency features and a small int8 CNN (`.../obby/Project Overview.md:9-27`).

Those can form a staged research program, but they are not yet one implementation. The captain must decide whether UREX is primarily:

1. contact-piezo piano transcription with laptop inference,
2. embedded polyphonic classification on ESP32,
3. robust automatic score following/page turning, or
4. an intentionally staged comparison of laptop and embedded inference.

Trying to claim all four as a single near-term deliverable will make the scope look unfocused.

### End-to-end integration is fragmented

- The FastAPI server broadcasts contract-style lowercase events such as `note_on`, while `current/src/mobile/App.tsx:138-164` reacts to hackathon-style uppercase `NOTE_PLAYED`, `PAGE_TURN`, and `SCORE_COMPLETED`. Live FastAPI notes will not drive that mobile UI.
- The mobile client has no reconnection loop (`current/src/mobile/App.tsx:95-136`).
- `current/src/web_app/app.js:1008-1048` still expects the obsolete direct ESP WebSocket path `/ws`.
- The FastAPI PCM server operates on port 8000. The Node score/OMR server is a separate port-8080 system. A bridge exists, but this is not a single clear application path.
- The current Vite page includes hardcoded presentation claims and fake logs. It should be treated as marketing UI, not proof.

### Transcription is not ready for the stated live target

- FastAPI defaults to the fake transcriber (`current/src/server/app.py:288-307`).
- Basic Pitch uses a two-second inference window with one-second overlap (`current/src/server/transcriber/basic_pitch.py:75-138`). It can duplicate events in overlapping windows, writes a temporary WAV for every inference, and inference is invoked synchronously from the WebSocket ingest path (`current/src/server/app.py:119-136,200-215`). This can block the asyncio event loop.
- `docs/ONSETS_FRAMES_EVAL.md:84-99` tells the user to select `onsets_frames`, but the CLI accepts only `fake` and `basic_pitch` and rejects other values (`current/src/server/app.py:259-281,288-297`). No Onsets and Frames adapter or result file exists.
- The on-device `esp_hint` is a fixed-threshold, monophonic FFT peak picker and is logged to serial, not delivered as authoritative polyphonic output. It cannot support the local vault's 88-note research claim.

### Score following is promising but fragile under real sensor noise

The tracker is tested against simulators, but its defaults and search strategy are risky for piezo transcription:

- A gap over five seconds since the last accepted event resets all progress.
- Two consecutive unrelated observations reset all progress because `DEFAULT_MAX_CONSECUTIVE_UNRELATED` is 1 (`current/src/final_bar_matching/full_score_progress_tracker.js:5-7,266-280`).
- Candidate search has no forward skip, so a missed note can stall the tracker (`current/src/final_bar_matching/full_score_progress_tracker.js:292-339`).
- The Jaccard chord score penalizes extra harmonic or pedal-derived notes as strongly as missing notes.
- The salvage audit records additional null-guard and caller-mutation defects (`docs/SALVAGE.md:144-159`).

These behaviors must be tested with realistic false positives, false negatives, repeated passages, tempo changes, pauses, and pedal resonance before claiming reliable page turns.

### Hardware is a draft, not a validated instrument

- The tracked KiCad PCB is effectively empty. The schematic is a draft analog front end, not fabrication-ready.
- The schematic uses old ESP32 GPIO34 labeling while the active firmware targets ESP32-S3 GPIO1.
- Component metadata and displayed values conflict in places: TL072 library metadata versus MCP6002 value, and 1N4007 metadata versus 1N5817 value.
- The I2S capture implementation is explicitly deferred (`current/src/ESP_piano/components/capture_hal/capture_i2s.c:1-33`).
- The analog preconditions are documented, but no oscilloscope capture, noise-floor measurement, clipping test, frequency-response plot, or bill of materials was found.
- Mean removal is performed independently on every 64-sample block (`current/src/ESP_piano/components/capture_hal/capture_adc.c:203-214`). At 16 kHz that is a 4 ms block. Its effect on bass fundamentals and low-frequency response needs measurement.
- The physical guide cites RMS log lines and thresholds, but current firmware only logs network metrics every ten seconds (`current/src/ESP_piano/main/main.c:106-113`). Several physical checks therefore cannot be executed as written.

### Documentation is stale after the era restructure

The active code moved under `current/src/`, but the living physical guide still uses commands such as `cd ESP_piano`, `python server/app.py`, and `python tools/...`, and tells the field team to use an old feature branch (`docs/PHYSICAL_TEST_GUIDE.md:24-55,77-84,94-103`). The root README tells readers where the active tree is but provides no current quick start, supported architecture, equipment list, results, or limitations.

`docs/TOOLCHAIN.md:1-11` is also a dated environment snapshot. In this scout, `nvidia-smi` exists in PATH but cannot load NVIDIA's management library, Python is 3.13.14 rather than the recorded 3.13.13, and ESP-IDF remains unavailable.

### Reproducibility and repository hygiene are weak

- There is no CI workflow.
- `pytest` is not included in `current/src/server/requirements.txt:1-9`, so the documented Python test suite is not reproducible from that file alone.
- Python dependencies use broad lower bounds and no lockfile.
- There is no project-wide license, only a mobile license and vendored licenses. This matters if UREX work, public datasets, models, or code will be redistributed.
- About 1,610 `node_modules` files are tracked across duplicated era trees. The repository has 1,996 tracked files total.
- `current/.gitignore:1` begins with malformed text, and its blanket `*.bin` rule at line 4 excluded the golden audio fixture referenced by `docs/CONTRACTS.md:33` and `current/src/contracts/tests/test_audio_stream.py:61-67`.
- There is no issue backlog despite known defects.
- A broken KiCad history gitlink has no `.gitmodules` mapping.

### Contract/session edge cases remain

The frozen contract says a reconnect begins a new session and resets both sequence and sample index (`docs/CONTRACTS.md:57-59`). Firmware sends a new HELLO after WebSocket reconnect, but the app-level framer is not reset by the connection-status callback (`current/src/ESP_piano/main/main.c:31-34,85-100`). `TYPE_GOODBYE` exists in the contract, but no firmware send path was found. Packet-loss, restart, and reconnection behavior therefore need an end-to-end test before the protocol can be called frozen in practice.

## 3. What the captain likely needs to do next

### Immediate application / proposal work

1. **Choose one research question.** Recommended framing: "Can a low-cost contact piezo and ESP32-S3 capture chain support reliable, low-latency polyphonic piano note detection, and what accuracy/latency tradeoffs arise between laptop and embedded inference?" If UREX is shorter, narrow further to signal feasibility and laptop baseline only.
2. **Name the current maturity honestly.** Say "working modular acquisition/streaming prototype plus simulated score-following software; physical and ML validation pending."
3. **Define hypotheses and metrics before implementation.** Use note-on F1, frame-level micro-F1, per-register F1, false notes per silent minute, p50/p95 end-to-end latency, packet gaps/drop rate, clipping rate, and 30-minute stability. The local evaluation note already proposes the right families of metrics (`.../obby/Evaluation And Metrics.md:9-43`).
4. **Write a staged scope.** Phase 1 is signal-chain characterization. Phase 2 is a reproducible laptop baseline. Phase 3 is embedded model feasibility. Score following/page turning should be an application demonstration or later research question, not mixed into the core hypothesis prematurely.
5. **Identify mentor, facilities, and required access.** The plan needs a specific piano, permission to mount a sensor, the exact ESP32 board, safe analog-front-end parts, optional MIDI ground truth, a GPU-capable machine if used, and a faculty mentor capable of supervising signal processing/embedded ML.
6. **Prepare ethics and data language.** Piano vibration/audio data is normally low-risk, but recordings may capture nearby speech through the soundboard or microphone. State storage, consent, anonymization, and retention plans if human sessions are recorded.
7. **Resolve contribution/provenance.** Create a contribution map separating pre-existing code, hackathon code, collaborator work, AI-assisted work, and the captain's proposed UREX work. Confirm code, model, dataset, and sheet-music licenses.
8. **Use targets as proposed thresholds, not achieved results.** Do not claim less than 150 ms, F1 of 0.85, Onsets and Frames support, real Gemini OMR, or robust page turning until result artifacts exist.

### Technical cleanup

1. Create a current top-level runbook and select one supported path: ESP32-S3 -> FastAPI `/stream` -> one transcriber -> contract-compatible browser/debug client.
2. Repair all live documentation paths after the move to `current/src/` and clearly label archive-era docs and hackathon simulators.
3. Add a repeatable development environment, test dependencies, pinned or locked Python dependencies, and CI for C host tests, Python contracts/server tests, JavaScript score simulations, and the Vite build.
4. Restore the missing golden contract fixture under a permitted extension or add a targeted ignore exception. Add an actual C-to-Python parity test.
5. Remove tracked dependency trees from the active development tree in a later cleanup change. Preserve snapshots/tags for archaeology instead of treating vendored `node_modules` as source.
6. Fix the FastAPI event-loop blocking path and Basic Pitch overlap deduplication before performance claims.
7. Align the note-event protocol across FastAPI, Node, mobile, and browser, then add one end-to-end contract test.
8. Test and fix reconnect semantics, including framer/sample-index reset and explicit session boundaries.
9. Decide whether the Node score server remains part of the supported path or whether score tracking moves behind the Python server. Do not maintain two overlapping server shells without a documented boundary.

### Experiment / design validation

1. **Freeze M0 choices:** exact sensor, mounting method, piano type, ESP32 variant, analog circuit, target note range, output, and latency requirement. The local open-question list explains why each changes the design (`.../obby/Open Questions And Assumptions.md:11-59`).
2. **Validate electrical safety first:** measure piezo spikes, DC bias, clamping, noise floor, and clipping with an oscilloscope or suitable acquisition instrument. Correct the KiCad schematic and produce a BOM before attaching it to the research piano.
3. **Run a tabletop capture, then a piano placement sweep.** Record silence, soft/loud single notes, chromatic scales, low/high register notes, intervals, chords, pedal noise, and mechanical thumps. Preserve raw PCM/WAV and exact configuration.
4. **Acquire ground truth.** Prefer simultaneous MIDI from a digital or MIDI-equipped piano. For acoustic piano, use scripted performances and optionally simultaneous microphone teacher labels. Split evaluation by recording session, not by frame (`.../obby/Dataset And Labeling Strategy.md:21-47`).
5. **Establish baselines in order:** simple FFT hint, laptop Basic Pitch or another supported model, then the proposed small CNN. Compare accuracy, latency, compute, and failure modes rather than assuming the CNN wins.
6. **Measure the acquisition transform.** Specifically test whether 64-sample mean removal suppresses useful bass content, whether a single-pole anti-alias filter is sufficient, and whether all target keys rise above the ADC noise floor.
7. **Run the measurement harness against real captures.** Store commit hash, hardware revision, configuration, raw inputs, ground truth, p50/p95 latency, F1, per-register results, and failure notes for every run.
8. **Validate score following separately** using injected realistic transcription errors, tempo variation, pauses, repeats, missed events, added harmonics, and pedal noise.

### Demo / showcase preparation

1. Produce one reproducible demo script with a known-good configuration and fallback mode.
2. Record a short evidence video that shows the physical sensor and circuit, serial/network health, live note output, and the measured latency method in one continuous take where possible.
3. Create a poster diagram that distinguishes implemented, simulated, and proposed components visually.
4. Prepare a results table and plots: sensor placement, signal/noise examples, spectra, accuracy by register/polyphony, latency distribution, and common failure cases.
5. Keep a synthetic/fake-transcriber fallback for UI demonstration, but label it prominently as simulated.
6. Package a field kit: board, verified AFE, spare piezo, data USB cable, mounting material, exact firmware binary/config, laptop environment, local Wi-Fi fallback, and printed troubleshooting steps.
7. Rehearse failure handling. The showcase should still teach something if Wi-Fi, the model, or the piano setup fails: replay a captured raw session through the same server and show the measurement record.

### Longer-term research work

1. Build a versioned, on-distribution piezo dataset with known sensor position and analog-chain revision.
2. Implement matching Python and C feature extractors and require parity before deployment, following `.../obby/Project Roadmap.md:19-21` and `.../obby/Training Pipeline.md:34-40`.
3. Train and compare a small 88-output classifier, quantify int8 degradation, and verify PC-to-device output parity.
4. Evaluate generalization across sensor placements, instruments, dynamics, registers, polyphony levels, ambient conditions, and hardware revisions.
5. Investigate onset-aware outputs and uncertainty calibration only after the baseline and dataset are stable.
6. Compare laptop inference against ESP32-S3 inference on accuracy, latency, energy, memory, and privacy/offline operation.
7. Treat score following as a second research layer: robust alignment under noisy observations, repeats, skips, pauses, and expressive timing.
8. Publish negative results and ablations. The local vault already requires failed ideas to remain part of the experiment record, which is excellent research practice.

## 4. Existing evidence and artifacts that support the UREX story

### In the repository

- **Era snapshots and Git history:** proof of the project's recovery from an earlier prototype and hackathon integration (`README.md:5-15`; `docs/ERA_SNAPSHOTS.md:5-15`).
- **Modular firmware:** real acquisition, framing, network isolation, protocol encoding, and metrics code under `current/src/ESP_piano/`.
- **Draft analog hardware:** KiCad schematic sources under `current/KiCad/firstTime/`. Useful as design-history evidence, not yet as a fabrication artifact.
- **Frozen contracts:** binary audio and note-event specifications in `docs/CONTRACTS.md` with C, Python, JSON schema, and tests.
- **Physical test protocol:** `docs/PHYSICAL_TEST_GUIDE.md`, including sensor placement, T1-T9, recovery steps, and an artifact checklist.
- **Salvage audit:** `docs/SALVAGE.md` is a candid module-by-module quality assessment and records known defects, reusable seams, and prior measured software-test state.
- **Synthetic fixtures and measurement tools:** `current/src/fixtures/`, `current/src/tools/check_golden.py`, `latency_harness.py`, `stream_synthetic.py`, and fixture generation.
- **Passing score simulations:** six JavaScript simulators passed in this scout environment.
- **Hackathon product narrative:** `after-hackathon/README.md:1-47,141-181` documents the intended piano-learning assistant and automatic-page-turn demonstration while explicitly identifying mocked OMR.

### Local, non-git evidence

The following read-only folder exists at `[private local evidence archive]`:

- A personal application PDF was present but was not inspected. Its filename, filesystem metadata, and contents are omitted from this public copy, and no claim in this report relies on it.
- `KiCad-Schematic-Screenshot.png`, 60,178 bytes, modified 2026-08-14. Visual inspection shows a piezo, MCP6002-labeled op-amp stages, 1 MΩ resistors, capacitors, Schottky-clamp labels, and ESP32 GPIO34/GPIO35 nets. It supports the hardware-design story but also exposes the old-board and component-metadata cleanup needed.
- `single-note-detection.mp4`, 19,089,041 bytes, modified 2026-08-14. Chromium reports 37.57 seconds, 3840x2160. The filename suggests a single-note demonstration, but the report does not infer performance from the filename alone. The captain should catalog what input, sensor, code revision, and output the video actually shows.
- `IMG_2432.mov`, 119,255,358 bytes, modified 2026-08-14. The installed browser could not open the MOV, so its contents were not verified.
- A complete Obsidian-style design vault under `PodleNote/obby/`, modified 2026-08-02. It includes project overview, open assumptions, signal acquisition, feature extraction, CNN architecture, dataset plan, training/quantization, ESP32 deployment, evaluation metrics, roadmap, modularity, and history.
- A zipped/local working copy and USB driver archive. These may help reconstruct the original development setup but should not be treated as research results.

The local vault is valuable proposal material because it provides a coherent hypothesis, milestone order, data strategy, and metrics. It is also explicit that the work was still at design stage. Preserve that honesty.

## 5. Hard questions to ask the captain

1. What does "UREX" refer to here, and what are the exact application deadline, page limit, required sections, eligibility rules, budget rules, mentor requirements, and project period?
2. What is the single research question the captain wants judged: sensing feasibility, polyphonic transcription, on-device ML, score following, or an explicit comparison?
3. What has physically worked on a real piano, with which commit, board, circuit, sensor, mounting position, and software mode?
4. What exactly do the two local videos show, and can their setup and results be reproduced?
5. Is the target piano acoustic or digital, and can it provide MIDI ground truth?
6. Which exact ESP32 board and revision is available? Is it S3, does it have PSRAM, and which GPIO is actually wired?
7. What is the verified analog front-end schematic and BOM? Have piezo spike voltage, bias, clipping, and noise floor been measured safely?
8. Must inference run on the ESP32 for the research contribution, or is laptop inference acceptable for the first phase?
9. Is the required outcome live feedback below 100-150 ms, offline practice analysis, automatic page turning, or a dataset/feasibility result?
10. Does the study need all 88 keys and dense polyphony, or can it begin with a defined register and limited chord size?
11. What piano access, lab instruments, GPU, recording time, and faculty supervision are guaranteed?
12. Who wrote which parts of the repository, including hackathon collaborators and AI-assisted work, and what portion will be the captain's new research contribution?
13. What licenses govern the repository, uploaded sheet music, public datasets, pretrained models, and any demo assets?
14. Will any human sessions or ambient microphone recordings be collected, and what consent/data-retention requirements apply?
15. Which current UI is intended to survive: FastAPI debug browser, React Native app, old web app, or a new minimal research dashboard?
16. What result would falsify the hypothesis or cause the team to change sensor, AFE, model, or scope?

## 6. Recommended first task narrow enough to ship

### Ship: a truthful current runbook and reproducible smoke test

Create `current/README.md` and a small scripted smoke test for the one supported no-hardware path.

The README should contain:

1. A five-line statement of the research goal and current maturity.
2. One architecture diagram: ESP32-S3 ADC/DMA -> `audio_stream_v1` -> FastAPI -> fake or Basic Pitch -> contract client.
3. Exact commands using current paths.
4. A dependency/toolchain table.
5. A supported-mode table that marks fake as simulation, Basic Pitch as laptop baseline, Onsets and Frames as not implemented, and embedded polyphonic CNN as proposed.
6. A hardware table naming the board, pin, draft AFE, and unresolved BOM/schematic items.
7. A test matrix with commands and current status.
8. A results table with every physical metric marked `not measured` until an artifact is attached.
9. Links to contracts, physical test guide, salvage audit, and local-experiment artifact conventions.

The smoke test should start or instantiate the FastAPI app with the fake transcriber, feed a known `audio_stream_v1` HELLO and PCM sequence, observe a contract-valid note event, and exercise `/health`. It should run without hardware or an ML model and become the first CI job. Then align one browser/debug client to that same note-event contract.

Definition of done:

- A fresh environment can follow the README without guessing paths.
- The smoke test passes from one documented command.
- The diagram and tables distinguish implemented, simulated, and proposed work.
- No unmeasured performance claim appears as fact.
- The next physical task is explicit: verify the AFE and capture the first versioned real-piano WAV plus configuration, photo, and log.

This task is preferable to immediately implementing the CNN or redesigning the app. It creates a defensible proposal baseline, exposes integration drift quickly, and gives every later experiment a stable provenance and execution record.

## Investigation record

Key commands run:

```text
git status --short --branch
rg --files
find current -path '*/node_modules' -prune -o -type f -print
git log --oneline --decorate --all
git rev-list --count HEAD
git ls-files | wc -l
git ls-files '*node_modules*' | wc -l
rg -n '(TODO|FIXME|stub|fake|mock|hardcod|onsets_frames|BasicPitch)' current/src docs
gh-axi repo view -R podledges/PodlePianoDSP32
gh-axi issue list -R podledges/PodlePianoDSP32 --state all
gh-axi pr list -R podledges/PodlePianoDSP32 --state all
bash current/src/ESP_piano/components/pcm_stream/test/run_host_tests.sh
python -m pytest -q current/src/contracts/tests current/src/server/tests
node current/src/final_bar_matching/simulator_milestone4.js
node current/src/final_bar_matching/simulator_browser_integration.js
npm --prefix current/src/web run build --if-present
# Private local evidence archive inventory command omitted from public copy.
```

Observed command outcomes:

- Git worktree was clean and detached at `87cc897` before investigation.
- GitHub reports a public JavaScript-classified repository with 2 stars, 1 fork, no issues, and 4 merged pull requests.
- JavaScript milestone 4 and browser integration simulations passed in the primary scout; the parallel inventory confirmed all six simulator scripts pass.
- C host tests did not run: `cc: command not found`.
- Python tests did not run: `No module named pytest`.
- Web build did not run: `vite: command not found` because dependencies were not installed.
- ESP-IDF build and hardware flash were not attempted: `idf.py` is unavailable and hardware-driving commands were outside scout scope.
- `nvidia-smi` is present but failed to load `libnvidia-ml.so`, so GPU availability was not verified.
- No project files were modified. Scratch browser/PDF inspection state was disposable. Only the source report and task-runner status records were written outside the inspected repository.

## Final recommendation

Proceed with UREX if the captain can secure a mentor, a specific instrument, a verified ESP32-S3 plus safe AFE, and time to collect a small ground-truth dataset. Pitch it as a measured embedded-sensing research question with a staged laptop baseline, not as a completed smart-piano product. The immediate deliverable is documentation and a contract-level smoke path; the first scientific milestone is one versioned, reproducible physical capture session with honest signal, accuracy, and latency measurements.
