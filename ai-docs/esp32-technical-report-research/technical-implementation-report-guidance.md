# What an embedded-system technical implementation report should contain
## Source-backed guidance for the UREX ESP32 piano/piezo project

**Research date:** 2026-09-09<br>
**Repository:** PodlePianoDSP32, revision `28a68dba91b650da836af7b215bdd03c77ec0c7a`<br>
**Deliverable type:** research and report-writing guidance, not an implementation, hardware validation, or completed experimental report.<br>
**Evidence boundary:** repository/source inspection and primary-document research only. No firmware build, flash, purchase, live hardware experiment, publication, push, or PR was performed. All suggested experiments below are **future protocols**, not completed work. All numerical acceptance targets in examples are **illustrative**, not captain-approved requirements or measured results.

## Executive answer

A good technical implementation report lets an independent engineer answer five questions: **What was required? Why was this design chosen? What exactly was built? How was it verified? What do the results actually justify?** It needs a reproducible account of the physical signal chain, target-specific acquisition, algorithms, real-time software, interfaces, resource limits, and failure behavior—not a diary, an ESP32 tutorial, or a source-code dump. University guidance explicitly calls for specifications, justified alternatives, technical definition/BOM, repeatable experiments, and separation of measured results from interpretation. [R1, Appendices A–C; R2, slides 4–8]

For this project, organize the technical core around:

> Piano vibration → piezo and mounting → protection/bias/buffer/gain/anti-aliasing → **identified SoC/ADC/driver configuration** → timestamped sample transport → selected DSP/transcriber → a precisely named output endpoint → evidence against requirements.

The defensible current claim is **“modular acquisition/streaming and transcription-adapter source exists; the as-built hardware and end-to-end physical performance remain unverified.”** Do not simply repeat the earlier scouts' characterization of a working ESP32-S3 pipeline: the current board documentation says **ESP32-S3**, but `capture_adc.c` selects **TYPE1** and reads `sample->type1.data`. The inspected ESP-IDF v5.4.2 header's S3 branch provides **TYPE2**, not `type1`. This is a concrete source-level target mismatch, not a reproduced build failure. The exact project's IDF version and actual board are still unknown. [L2–L3; R10]

The report should also explicitly reject four misleading shortcuts:

- “12-bit ADC converted to int16” does **not** mean 16-bit measurement resolution, calibrated volts, or measured SNR.
- A nominal sample rate or DMA configuration does **not** establish actual timing, losslessness, or end-to-end latency.
- A repeated FFT peak event does **not** establish musical onset, polyphonic transcription, or velocity estimation.
- Synthetic replay, fake transcription, UI animation, and a test plan are **not** real-piano results.

**Minimum persuasive evidence:** exact board/sensor/AFE provenance; one annotated schematic and mounting photograph; source/configuration map; a timing/ownership diagram; safe-input and acquired-waveform evidence; paired input/ground-truth data; latency distribution plus detection error counts; CPU/heap/stack and loss counters; requirement–design–test traceability; and a reproducible build/analysis manifest. If those artifacts do not yet exist, publish the document internally as a **design and implementation-status report with a verification plan**, leaving physical results “not measured.”

---

## 1. Scope, evidence status, and reconciliation of previous scouts

### 1.1 Working assumptions—not hidden decisions

- The target is the **UREX contact-piezo piano project**, specifically the active `current/` tree of PodlePianoDSP32. `before-hackathon/`, `after-hackathon/`, and active `legacy/` code are historical evidence, not interchangeable configurations.
- Audience: an engineering assessor or research mentor who understands basic circuits/programming but did not build this system. No UREX-specific rubric, page limit, or approved requirement set was supplied. The outline is adaptable, not a claimed institutional template.
- Main report boundary: sensor/acquisition plus **one explicitly selected transcription/output path per experiment**. Laptop inference, optional embedded hints, fully embedded ML, and score following must be distinguished.
- Exact board, module, silicon revision, sensor part/capacitance, mounting, circuit/BOM, and actual firmware build are unknown. S3 is documented intent, **not confirmed bench identity**.
- Polyphonic note identification is relevant to the broader research direction. Per-key trigger hardware, pitch-continuous output, velocity estimation, MIDI transport, audio synthesis, and page turning are conditional sections—not presumed requirements.
- No further captain decision is needed to deliver this guidance. Future engineering choices below are scope-dependent recommendations, not newly opened decision gates.

### 1.2 Use a claim-status vocabulary throughout the eventual report

| Label | Meaning | Sufficient evidence |
|---|---|---|
| **Required / proposed target** | Intended acceptance criterion | Requirement ID, rationale, owner, revision; not a result |
| **Designed / planned** | Proposed architecture, circuit, or algorithm | Versioned drawing/decision with assumptions |
| **Implemented in source** | Code or design artifact exists | Exact revision, configuration branch, file/function references |
| **Built / host-tested / simulated** | A specified nonphysical validation actually ran | Command, environment, output, input fixture and timestamp |
| **Bench-measured** | Electronics/target tested in a recorded setup | Instrument data, calibration/settings, raw logs and configuration |
| **Piano/session-validated** | Whole claimed boundary tested on the instrument | Setup/placement identity, raw capture, labels, analysis and uncertainty |
| **Unknown / not measured / not applicable** | Missing evidence or deliberately outside scope | Explicit reason and effect on conclusions |

“Implemented” alone is too ambiguous: a schematic may be drawn but not assembled, and C source may exist without compiling for the intended target. Keep these statuses in captions, architecture legends, result tables, and the abstract.

### 1.3 What the required prior evidence establishes

Three predecessor scout reports were read completely:

1. [`podlepianodsp32-urex-scout.md`](podlepianodsp32-urex-scout.md) (2026-08-24; revision `87cc897…`): recovered streaming/transcription platform, draft AFE, absent physical dataset/results, proposed on-device polyphonic work in a separate local vault.
2. [`podlepianodsp32-embedded-c-agent-kb-scout.md`](podlepianodsp32-embedded-c-agent-kb-scout.md) (2026-09-02; same revision): native-test/build-context opportunities, missing pinned IDF/configuration, reconnect and data-contract risks. Its past nine-test pass is **that scout's software evidence**, not a test rerun here.
3. [`podlerex-esp32-board-buying-scout.md`](podlerex-esp32-board-buying-scout.md) (2026-09-06): a **different repository**, PodleRex, with original-ESP32/ADC1_CH6/GPIO34, 20.48 ksample/s and ESP-NOW code. Its purchasing, chip-launch, and availability findings are irrelevant to this writing task and were not revalidated.

**Reconciliation:** do not transplant PodleRex's 20.48 ksample/s, I2S0 ADC-DMA usage, GPIO34, ESP-NOW, or board recommendations into the active S3-intended project. Conversely, do not assume the S3 intent makes the current TYPE1 capture implementation valid. Earlier scout summaries are leads; the inspected revision and matching primary documentation take precedence.

The old scouts' local vault/video claims remain **attributed prior observations**. This investigation did not reopen those external files, extract the application PDF, or establish that a video demonstrates the current revision.

### 1.4 Current repository evidence ledger

`L#` references below identify exact local evidence at the inspected revision. Root README lines 5–17 identify `current/` as active.

| ID | Current evidence | What the eventual report may say—and may not say |
|---|---|---|
| **L1** | `README.md:5–17`; `data/README.md:1–5`; `current/src/fixtures/` contains `cmaj_chord.wav`, `cmaj_chord.mid`, `project_tree.txt` | Active/archive layout and synthetic fixture artifacts exist. No real-piano experiment bundle was found in the inspected data/fixture locations; that does not prove no one has private bench data. |
| **L2** | `current/src/ESP_piano/main/board_pins.h:3–40`; `components/capture_hal/Kconfig:3–35` | Documented S3 board map, default 16 ksample/s, ADC1 channel 0/GPIO1, 12 dB attenuation and provisional analog preconditions. These do not identify the actual assembled board or prove a safe voltage range. |
| **L3** | `current/src/ESP_piano/components/capture_hal/capture_adc.c:29–31,101–125,185–214` | ADC1, 12-bit, continuous-driver source, four-frame pool, TYPE1 selection/parsing, per-read mean subtraction and int16 scaling. **S3 compatibility is unresolved/contradicted by the pinned header inspection**; no ADC calibration call is present in this capture file. The comment “radio-immune” is not a noise measurement or a defensible analog guarantee. |
| **L4** | `current/src/ESP_piano/main/main.c:20–24,31–61,98–114` | Capture on core 1 at priority 5, stream on core 0 at priority 4, 4096-byte stack requests, 4096-sample ring, 64-sample reads; optional hint computation executes synchronously in capture. Only network metrics are logged by the main ten-second loop. |
| **L5** | `components/pcm_stream/ringbuf.c:20–59`; `pcm_framer.c:15–63`; `include/pcm_framer.h:9` | Atomic SPSC source; ring-full drops new samples; frame size 320 samples; framer counts emitted samples and has a reset function. This is not proof that every physical ADC sample reaches the server. |
| **L6** | `components/ws_streamer/ws_stream.c:16–24,92–126,143–174,204–246`; `main/main.c:31–34` | Eight-entry copied-frame queue, transmit task, drops, HELLO on connection. Status callback does not reset framer. Document/retest session reset, queue flushing, ordering, send success interpretation, and reconnect counting; initial connect also increments its “reconnects” metric. |
| **L7** | `docs/CONTRACTS.md:7–33,35–59` | 26-byte little-endian audio header, sample-index timing, note-event schema, non-authoritative hints, new session/reset requirement. Note “active snapshot” prose versus event enums needs an unambiguous consumer contract. Paths in this document predate the move under `current/`. |
| **L8** | `components/esp_hint/esp_hint.c:16–26,44–95,99–114` | Optional nonoverlapping 1024-sample Hann FFT, largest-bin pitch hint, threshold 200, fixed velocity 100 and confidence 0.5, `note_on` output logged by main. Not validated onset timing, true velocity, calibrated confidence, note-off state, or polyphonic inference. |
| **L9** | `current/src/server/app.py:119–136,165–166,259–281,288–305`; `server/transcriber/basic_pitch.py:35–39,75–138,150–178` | Default fake transcriber, optional Basic Pitch, fallback to fake, two-second window/one-second overlap, synchronous feed/inference call path, ONNX/TFLite/model backend resolution. Actual backend and fallback must be captured per run. Only fake/basic_pitch are accepted; Onsets & Frames is not an available CLI mode. |
| **L10** | `current/src/server/index.js:168–172,238ff`; `docs/ONSETS_FRAMES_EVAL.md:9–16,84–99` | OMR is explicitly fabricated; O&F document describes an unimplemented evaluation intention. Neither is evidence of real OMR or streaming O&F performance. |
| **L11** | `current/KiCad/firstTime/firstTime.kicad_sch:1675,1964–1986,2063–2086,2492–2515` | GPIO34 net, TL072 symbol/MCP6002 value and 1N4007 library/1N5817 value inconsistencies. Draft circuit is not a reviewed as-built schematic/BOM. Do not infer physical components or safety from displayed labels. |
| **L12** | `current/src/tools/latency_harness.py:79–107,121–130,161–187`; `docs/PHYSICAL_TEST_GUIDE.md:303–325,362–397` | Replay harness times **after sending the frame containing the onset** to received matching note event, on one host clock. It does not time piezo, ADC, firmware acquisition or visible UI. Its pitch-first matching and measured-only quantiles need auditing for repeated notes, misses and false matches. |
| **L13** | `docs/PHYSICAL_TEST_GUIDE.md:206–240,362–397,597–612`; `current/src/tools/check_golden.py:79–84,150–159` | Placement/RMS advice and capture/evaluation procedures are proposed, not measurements. A system-audio/line-in WAV is not automatically ESP ADC PCM. Free playing must **not** be scored against the unrelated C-major fixture MIDI. The checker fabricates two-second note durations and ignores offsets for evaluation; it does not validate real note-off timing. |
| **L14** | `components/ws_streamer/idf_component.yml:1–3`; `components/esp_hint/idf_component.yml:1–2`; no `sdkconfig*` or `dependencies.lock` found under active firmware | Dependency ranges exist, but no closed target/configuration/build graph was found. The string `FIRMWARE_VERSION "v2.1.0"` is not a unique build identifier. |

Here and below, firmware paths abbreviated as `components/...` are beneath `current/src/ESP_piano/`; server/tool paths are beneath `current/src/`.

### 1.5 Corrections that matter most to the report

1. **S3 versus TYPE1:** ESP-IDF v5.4.2 `hal/adc_types.h:198–217` exposes only `type2` in its S3 branch. Current source references `type1` twice. This is a high-priority compatibility evidence gap and likely follow-up correction, but a build has not been run and no particular current installation is assumed. [L2–L3; R10]
2. **0–3.1 V is not automatically a calibrated range:** Kconfig's provisional clamp wording cannot override the inspected S3 datasheet v2.2 §5.5, whose ATTEN3 calibrated effective range is 0–2900 mV under specified **DC, 100 nF, 25 °C, Wi-Fi-disabled** conditions. Neither a calibrated range nor a power-pin absolute-maximum table is a complete ADC input-protection specification. [L2; R6]
3. **Record-before-processing matters:** per-64-sample mean subtraction discards bias information and changes the waveform. Postprocessed PCM alone cannot establish input bias, raw-code clipping, or ADC voltage calibration. [L3]
4. **A sample counter can hide loss:** ring drops occur before the framer's sample-index advance. A downstream contiguous sample index need not mean contiguous physical time. Account for ADC pool losses, ring losses and transport-frame losses separately. [L4–L7]
5. **Existing latency/accuracy guides need methodological repair before being quoted:** replay is a subsystem test; labels must match the actual performance; fake fallback cannot count as transcription success; fixed-threshold advice without implemented instrumentation is not a field result. [L9, L12–L13]

---

## 2. Detailed annotated table of contents for the eventual project report

The percentages below are a suggested allocation of **main-text space**, not a UREX rule. Combine headings for a short report, but preserve the five logical layers: requirements → rationale → as-built implementation → verification/results → discussion. The technical sections should have explanatory prose, not only checklists. [R1, §§3.10–3.14 and Appendices A–B]

| Proposed section | Question answered; exact content | Depth and appropriate artifacts | Evidence required |
|---|---|---|---|
| **Front matter: title, authors/contributions, revision, abstract** | What was investigated, built and established? Identify maturity and one primary system boundary. | Standalone 150–250-word abstract as an adaptable suggestion; no unsupported headline numbers. TOC/list of figures for a long document. | Revision, scope, result IDs; acknowledge inherited/hackathon/AI-assisted work according to institution rules. |
| **1. Problem, research question and scope** (~8%) | Why piezo piano sensing? Who needs the output? Is this sensing feasibility, transcription, embedded inference, or score following? Define non-goals. | One context diagram; define “onset,” “active note,” “latency,” “real time,” “velocity,” and “polyphony.” | Stakeholder/use-case evidence; cited background; scope status. |
| **2. Requirements and success criteria** (~8%) | What must work, under which conditions and with what tolerances? | Numbered requirement table; functional, electrical, timing, accuracy, resource, recovery and reproducibility requirements. | Source/rationale for every target; version and approval status; test IDs. |
| **3. Background and design rationale** (~12%) | Why this sensor/AFE/ADC/algorithm/partition, rather than alternatives? | Compare two or three credible alternatives per consequential decision; weighted decision matrix only if weights are justified. Essential equations and tradeoffs, not a full DSP textbook. | Datasheet/TRM/IDF version citations; literature; calculations; rejected alternatives and constraints. |
| **4. As-built hardware implementation** (~15%) | What physical device produced the input? | Exact board/module/silicon/sensor/BOM; annotated AFE schematic; actual net-to-pin table; mounting dimensions/photo; power and grounding diagram. | Revision-controlled design plus assembly photos and deviations; component markings; inspection/calibration records. If absent, label “planned hardware.” |
| **5. As-built firmware and acquisition** (~17%) | How do samples move and who owns each state? | Target/config table; task/ISR/queue ownership table; timing diagram; startup/recovery state machine; protocol summary; loss policy; selected short code excerpts. | Exact source/functions, generated config, build log, resource report, task/driver configuration and traces. |
| **6. DSP/transcription and output integration** (~12%) | What transformations turn samples into the claimed output, and where do they execute? | Full parameter table and algorithm/state description; causal window/hop diagram; event examples; host backend/model provenance; interface sequence diagram. | Executable version, coefficients/weights hashes, parity tests, true backend, labels; optional ML subsection only if used. |
| **7. Verification method and experimental design** (~10%) | How were claims tested independently of the implementation? | Test matrix; apparatus and synchronization diagram; ground-truth protocol; metrics; sample counts; split/randomization rules; uncertainty model. | Preregistered/frozen protocol, instrument settings, calibration, fixture/label hashes, scripts. |
| **8. Results against requirements** (~10%) | What passed, failed or remains unknown? | Requirement verdict table; waveform/spectral examples; latency ECDF; error counts; resource/soak plots; compare baseline and intervention under matched conditions. | Raw artifacts and analysis commands for every point/number; denominators, uncertainty, exclusions and failed runs. No measured plot until data exists. |
| **9. Discussion, limitations and threats to validity** (~6%) | Why did it work/fail, and where do conclusions stop? | Explain errors and tradeoffs; internal/external validity; measured versus predicted limits; alternatives suggested by evidence. | Link interpretations to results and literature; distinguish hypothesis from demonstrated mechanism. |
| **10. Conclusions and prioritized next work** (~2%) | To what extent were original objectives met? What is the next evidence-producing action? | Short verdict by research question/requirement; no new results. | Traceable results or explicit “not evaluated.” |
| **References and appendices** | Can another engineer reconstruct and audit the work? | Full citations; detailed schematic/BOM; configs/locks; selected full listings; test procedures; raw-data index; analysis manifest and contribution map. | Stable URLs/DOIs/revisions/checksums, artifact locations, access limits and licenses. |

**Depth rule:** include a detail in the main text if changing it could change safety, a result, a timing claim, a reproducibility outcome, or a design decision. Put exhaustive instances in an appendix. Example: explain the anti-alias filter topology and measured response in the body; put tolerance calculations and complete BOM in Appendix A. Show a short critical ownership/transform excerpt; link the full firmware rather than printing it.

---

## 3. Exact technical details and project-specific checklist

This section doubles as a writing checklist. Unchecked items are evidence to obtain, not implied missing implementation work to perform in this scout.

### 3.1 Requirements: specify the phenomenon, not just the feature name

- [ ] Define instrument type and supported note/register range. “Piano” is not enough: upright/grand/digital, tuning, pedal behavior, mounting access and accepted dynamic range affect scope.
- [ ] Separate **global onset detection** (“an attack happened”), **pitch classification** (“A4”), **multipitch/active-note state**, **note events with offsets**, and **score position/page turn**. These are distinct tasks with different oracles. [R17–R20]
- [ ] Specify whether a note is active when the key is down, the damper is lifted, the string is audibly vibrating, or a classifier state is active. Sustain pedal makes those non-equivalent. [R19, §2]
- [ ] Name the output endpoint and timing reference. A note timestamp estimated retrospectively is not the time at which a user receives a result.
- [ ] State allowed missed, false and double triggers, matching tolerances, release behavior and repeated-note separation. Add polyphony and relative loudness conditions only if claimed.
- [ ] Describe continuous operation duration, allowed degraded modes, recovery deadlines, memory limits, deployment constraints and operating environment.
- [ ] Mark all values as sourced requirement, provisional engineering target, derived bound, or measured quantity.

**Main-text artifact:** requirement table with ID, condition, measurable quantity, unit, target, justification, verification method and status. A phrase such as “accurate and low latency” is not testable.

### 3.2 Piezo mechanics, mounting and crosstalk

**Why this belongs in implementation:** the sensor responds to deformation, and its mechanics/resonance and electrical loading affect the signal. Mounting is part of the measurement system, not a setup footnote. TI describes the deformation/charge model and resonance; TE's DT documentation supplies a concrete manufacturer example of model-dependent dimensions, capacitance, loading and attachment. TE DT is **polymer film, not proof of this project's unidentified ceramic disc specifications**. [R3, §2; R4, “Piezoelectric sensors”; R5]

- [ ] Identify sensor manufacturer/part, ceramic disc versus film versus internally buffered sensor, lot/sample ID, diameter/thickness/material, nominal and measured capacitance, resonant behavior, electrode orientation and lead attachment.
- [ ] Include a placement coordinate system relative to a permanent piano landmark; dimensioned photo/sketch; contact area, attachment material/thickness, preload/application method, orientation and cable strain relief.
- [ ] Record piano make/model or anonymized identifier, soundboard location, tuning, lid/pedal state, room/support conditions, nearby disturbance sources and instrument-owner permission for non-damaging attachment.
- [ ] Distinguish within-mount repeatability from remove/remount reproducibility. Hold electrical configuration fixed for placement comparisons; randomize order to reduce player/time confounding.
- [ ] Separate electrical channel coupling, structural vibration propagation, sympathetic string resonance, and algorithmic harmonic/octave errors.
- [ ] For **one soundboard sensor**, vibration from multiple strings is intended input; “zero crosstalk” is the wrong requirement. Report sensitivity across register and spurious-note behavior. For **several key/pad sensors**, report cross-channel response ratios and trigger-confusion matrices, including simultaneous hits.

**Figures/tables:** overall mounting photo, close-up with scale, placement-response map by note/register, mounting log and sensor specification table. Do not claim the guide's “best near bass bridge” position is universally optimal; it is a candidate to compare. [L13]

### 3.3 Sensor impedance and analog front end: safe, bounded, explainable

A high-input-impedance **voltage amplifier** and a **charge amplifier with a virtual-ground input** are different solutions. Do not assert that every piezo conditioning circuit must present a large signal-input resistance: charge-mode conditioning deliberately collects charge at low closed-loop input impedance. Both need low leakage/bias-current reasoning. [R3, §§3.1–3.2; R4, “Input impedance”]

Document the **actual topology**, not a generic list of parts:

- [ ] Sensor equivalent circuit, capacitance and leakage assumptions; cable length/capacitance/shield and connector polarity; input/bias resistance and its low-frequency effect.
- [ ] Protection on both polarities, series impedance and transient current/energy path; clamp part, leakage/capacitance and tolerance; op-amp input limits; ADC input limits; powered-off behavior and possible back-powering of rails.
- [ ] Distinguish recommended operating envelope, calibrated measurement range, and absolute-maximum stress rating. A diode to a supply rail does not clamp exactly at the rail, and a regulator may not absorb injected charge. Verify the actual design before connecting the MCU.
- [ ] Bias/reference source, nominal level, measured level, impedance/decoupling, startup settling, drift and available positive/negative headroom.
- [ ] Amplifier supply, common-mode range, output swing under actual load, input bias/leakage and voltage/current noise, gain-bandwidth, slew rate, stability with ADC/cable capacitance, and overload recovery. “Rail-to-rail” is not an unlimited swing/drive guarantee.
- [ ] Stage-by-stage gain and tolerances, soft-note sensitivity versus loud-note/chord headroom; saturation at every stage, not only at the ADC rails.
- [ ] Analog high-/low-pass poles, passband ripple, stopband rejection, phase/group delay and tolerances. Anti-aliasing must happen **before sampling**; digital filtering cannot remove an already aliased component. [R4; R22]
- [ ] As-built schematic, net labels/test points, matching BOM/package/pinout, board-versus-breadboard construction, assembly deviations and photographs. Resolve TL072/MCP6002 and diode metadata before describing physical components. [L11]

**Useful equations, with stated idealizations:** for a simple capacitive sensor and resistive voltage-mode load, let `C_T` be total parallel sensor/cable/input capacitance and `R_eq` its effective leakage/bias resistance:

\[
|Z_C(f)|=\frac{1}{2\pi f C_T},\qquad f_L\approx\frac{1}{2\pi R_{eq}C_T}. \tag{1}
\]

This is a simplified lumped model, excluding mechanical resonance and complicated protection networks. Derive the actual circuit response rather than copying a low-frequency formula blindly; parallel physical capacitances **add**. In ideal charge-mode midband operation:

\[
V_{out}-V_{bias}\approx-\frac{Q}{C_f},\qquad f_L\approx\frac{1}{2\pi R_f C_f}. \tag{2}
\]

For a noninverting resistive-gain stage `G=1+R_f/R_g`, and a single RC low-pass `f_c=1/(2πRC)`. Define which stage those components belong to; neither formula describes the entire AFE automatically. [R3–R4]

**Safety statement for the report:** no direct piezo-to-ADC connection is justified by the inspected evidence. Piezo voltages vary widely with type and excitation; manufacturer literature establishes the hazard, **not this disc's actual peak voltage**. Input protection must be designed and measured against the chosen parts under a supervised, current-limited lab protocol. Do not treat this report as a build-ready schematic. [R3, §3; R5]

**Main text:** one readable circuit with labeled functions/test nodes and nominal limits, transfer-function rationale, waveform showing bias/headroom, measured gain/filter response. **Appendix:** full schematic/BOM, protection calculations, tolerance/noise analysis and scope exports.

### 3.4 Target-specific ADC, calibration, resolution and aliasing

Start this section with a hardware/software identity table: SoC, silicon revision, module SKU, development-board model/revision, flash/PSRAM, GPIO, ADC unit/channel, reference/attenuation, configured bit width, driver mode, DMA format, requested sample rate, measured sample rate, pattern/channel count, IDF/toolchain version and calibration scheme.

| Concern | S3-intended active project | Original-ESP32 comparison—**not a drop-in configuration** |
|---|---|---|
| Pin mapping | Documented ADC1_CH0 → GPIO1; primary S3 pin table agrees. [L2; R6, Table 2-8] | Sibling scout says ADC1_CH6/GPIO34; do not rewire by channel number alone. |
| DMA resources | S3 continuous driver allocates GDMA; exhaustion can return `ESP_ERR_NOT_FOUND`. [R8, Resource Allocation] | Original-ESP32 continuous ADC uses I2S0 as DMA FIFO. [R9, Hardware Limitations] |
| ADC output structure | S3 IDF v5.4.2 branch is TYPE2/32-bit result record. [R10] | Original-ESP32 branch documents TYPE1; its packing is different. [R10] |
| ADC2 | S3 IDF v5.4.2 warns ADC2 DMA retrieval is unsupported due to unstable results; do not force it casually. [R8] | Original driver has its own ADC2/Wi-Fi restrictions and mode limitations. [R9] |
| Calibration | S3 curve-fitting scheme documented for this IDF reference. [R11] | Do not assume S3 calibration tables, eFuses or scheme apply to original ESP32. |
| Sampling limits | Verify selected release's `soc_caps`, driver checks, clock tree, electrical conditions and actual output. | Do not inherit a legal sample-rate range from a different target. |

Checklist:

- [ ] Record requested and **measured** conversion/sample rates, sample-clock source/divisors/power-management settings, legal range and channel scan pattern. For multiple channels, distinguish aggregate conversion rate from per-channel rate and quantify inter-channel skew. [R7–R9]
- [ ] Explain ADC result record size separately from quantizer width and wire PCM width. For S3, 32-bit DMA records do not imply 32-bit resolution; the sensor conversion is 12-bit. [R6–R8, R10]
- [ ] Explain code-to-voltage calibration: factory/eFuse scheme, attenuation/bitwidth, calibration conditions and residual error. Use `adc_cali_raw_to_voltage()` only with the correct scheme/configuration; archive checks against known voltages. [R11]
- [ ] If raw ADC counts are centered/scaled into int16, show the exact integer rounding and saturation rules. Do **not** use `code × 3.3/4095` as a claim of calibrated ADC voltage.
- [ ] Specify intended electrical/audio passband and justify `f_s` from both fundamental and relevant harmonics/transients. Having C8's fundamental below Nyquist does not establish alias suppression.
- [ ] Define anti-alias passband edge, stopband edge and rejection requirement, not only “cutoff <8 kHz.” A one-pole response below Nyquist may still pass substantial out-of-band energy. [R4, R22]
- [ ] Measure raw-code noise, clipping, transfer residuals, frequency response and Wi-Fi-on versus appropriate controlled-off behavior. ADC1 avoids certain peripheral conflicts; it is not “radio-immune.” [R6 §5.5; R11 “Minimize Noise”]
- [ ] Treat the manufacturer's 100 nF/multisampling noise advice as circuit-dependent. A large capacitor driven through high impedance can attenuate useful audio; averaging changes bandwidth and timing. Do not copy a DC characterization setup as a complete audio design. [R6, R11]

**Present no nominal-bits-as-ENOB claim.** If effective number of bits is reported, specify the sine-wave SINAD test method, frequency, amplitude, bandwidth/window and operating configuration. Musical capture SNR alone is not a conventional ADC ENOB test.

### 3.5 Acquisition, DMA, buffering and data integrity

- [ ] Identify the owner and lifetime of the ADC handle, driver pool, application raw buffer, sample block, ring, framer and queued network frame. Indicate copies versus borrowed pointers and when storage may be reused.
- [ ] List DMA conversion-frame size in **bytes and conversion records**, pool depth, partial-read behavior, read timeouts, overflow/error responses and buffer placement/alignment constraints. The driver's pool is not the same thing as the application read buffer. [R8]
- [ ] State whether application callbacks run in ISR context or a task. Current source performs blocking driver reads in a capture task; it does not implement an application ADC callback. An ISR-callback recommendation must not be described as current code. [L3–L4]
- [ ] Define acquisition start, frame timestamp reference, stream/session start, reset semantics, clock domains, sequence wraps and how gaps enter both timestamps and samples.
- [ ] Account for three distinct loss sites: ADC pool overflow, ring-full drops, and network queue/send drops. Record denominators and units (conversion records, int16 samples, frames), and decide how downstream analysis rejects or marks discontinuous windows.
- [ ] Document backpressure/drop-oldest/drop-newest policy and maximum stale-data age. A bigger buffer can hide overload while worsening interactive latency.
- [ ] If calibration or logging is moved into the capture path, include its cost in the same budget. If flash/cache-disabled periods are possible, document IRAM configuration and test the chosen policy. [R8, R13]

**Derived configuration arithmetic—not measured performance:** assuming the documented 16 ksample/s single-channel path and 320-sample frames:

| Item | Derivation | What it means, and does not mean |
|---|---|---|
| Read block | `64/16000 = 4 ms` | Nominal block span, not measured task period or ADC fidelity. |
| S3-format raw frame/pool | `64×4 = 256 B`; four frames `=1024 B`, covering `16 ms` | Derived for S3 result size; current TYPE1 mismatch must first be resolved. Driver overhead/descriptors are extra. |
| Ring | `4096×2 =8192 B =8 KiB`; `4096/16000 =256 ms` | Storage/backlog capacity, not inevitable latency or proof of 256 ms scheduling tolerance at all layers. |
| Wire frame | `26 + 320×2 =666 B`; `50 frames/s` | Audio protocol rate `33,300 B/s =266.4 kbit/s`, excluding WebSocket/TCP/IP/Wi-Fi overhead, retransmissions and control traffic. |
| TX queue | Eight 320-sample audio frames span `160 ms` | Queue payload storage is eight **2048-byte slots**, not eight 666-byte allocations; length fields and queue overhead are additional. |
| Optional FFT hint | `1024/16000 =64 ms`; `Δf=16000/1024 =15.625 Hz` | Window span/bin spacing, not measured onset latency or 88-key pitch resolution. |

Show these calculations once in the body with L3–L8 references; put exhaustive memory layout in an appendix. Do not add all buffer capacities and call the sum “latency”: queues can be empty, full, nested or dropping, and actual delay depends on occupancy and execution.

### 3.6 DSP, onset, pitch and velocity—only what is actually used

**Mandatory parameter disclosure for every used processing stage:** input units/range; DC removal; filters and coefficients; window type/length; FFT size and normalization; hop/overlap; feature scaling; thresholds/hysteresis; adaptive-statistic time constants; peak selection; refractory/rearm rules; note-off logic; tuning reference; state resets; output timestamp convention and lookahead. Specify numeric type, rounding/saturation and library/version/implementation selection.

**Current source deserves an exact description, not a stronger algorithm name:**

- Per-block transform approximates `y[n]=sat16((x[n]−floor(block_mean))×32767/2048)` with C integer arithmetic. Mean is recomputed for every 64-sample read. This is **block-dependent processing**, not simply a conventional time-invariant high-pass filter with a known cutoff. Test low-frequency amplitude and block-boundary artifacts across signal phases. [L3]
- Optional hint uses a Hann window, a 1024-point FFT, largest positive-frequency bin, fixed magnitude threshold and nearest equal-tempered MIDI mapping. It can repeatedly emit `note_on` while a steady note remains strong. It does not independently localize an attack or maintain note release. Its velocity/confidence are constants. [L8]
- Basic Pitch is a **host model adapter**, resampling 16 ksample/s PCM to 22.05 ksample/s, using two-second input windows with one-second overlap; document buffering, backend, model hash, file I/O and overlap deduplication behavior. Its amplitude-to-velocity/confidence mapping is not a validated physical calibration. [L9; R20]

Equations worth including when applicable:

\[
X_m[k]=\sum_{n=0}^{N-1}x[mH+n]w[n]e^{-j2\pi kn/N},\quad
\Delta f=f_s/N,\quad T_H=H/f_s. \tag{3}
\]

Here `N` is window length and `H` hop length. State whether this forward-indexed window is timestamped at start, center or end, and when its last required sample becomes available. Zero-padding can interpolate the spectrum but does not create information equivalent to a longer observation.

For an **optional comparison baseline**, positive spectral flux can be written:

\[
D[m]=\sum_k\max(0,|X_m[k]|-|X_{m-1}[k]|). \tag{4}
\]

This is not currently implemented in the hint. A detector also needs thresholding/peak selection and rearming; naming “spectral flux” without those details is insufficient. Bello separates preprocessing, detection function and peak picking; Dixon demonstrates that small implementation/threshold differences materially affect results. [R17, §§III–V; R18, §§2–3]

Pitch mapping, if used:

\[
m=69+12\log_2\!\left(\frac{f}{440\,\mathrm{Hz}}\right),\qquad
 e_{cents}=1200\log_2(\hat f/f_{ref}). \tag{5}
\]

State rounding, tuning reference, accepted range and octave/harmonic rejection. A largest spectral peak need not be the fundamental. The hint's 15.625 Hz bin spacing is much wider than the approximately 1.64 Hz A0–A♯0 fundamental separation; code range checks alone cannot substantiate full-keyboard discrimination. This is a **derived limitation of the simple bin mapping**, not a measured accuracy result or proof that all alternative estimators require that bin spacing.

Conditional subsections:

- **Trigger-only:** envelope/energy or flux; threshold adaptation, attack confirmation, rearm and minimum repeat interval; evaluate false/missed/double triggers. Do not add pitch/ML claims.
- **Monophonic pitch:** describe estimator, confidence/voicing, low-frequency observation length, tuning and octave errors; stress sustained notes and transients separately.
- **Polyphonic transcription:** describe outputs per pitch, overlapping notes, harmonic confusion, repeated-note handling and sustain/offset semantics. Global onset counts cannot prove chord-note recall. [R18–R20]
- **Velocity/intensity:** distinguish hammer/key velocity, MIDI velocity, loudness, peak voltage and arbitrary normalized amplitude. A single soundboard amplitude also depends on note, placement and other sounding notes. Claim only a calibrated proxy unless independent velocity reference exists. [R19, §3.1]
- **Embedded ML, only if deployed:** training data/splits, architecture/tensor dimensions, frontend parity, model/weight hash, quantization scales/calibration set, supported operators, arena/activation memory, inference time distribution, flash/PSRAM placement, PC/device output parity and accuracy change. A small parameter count is not a full peak-memory budget. [R20, §3]
- **Score following/page turns:** separate downstream evaluation under controlled transcription errors, pauses/repeats/skips and accidental page turns. Simulated OMR or synthetic note injection must be labeled.

**Literature-to-project boundary:** Onsets & Frames' published architecture includes bidirectional recurrent processing and full-sequence inference. Published faster-than-real-time throughput is **not evidence of causal low-latency streaming**, a supported repo adapter, ESP32 feasibility, or this piezo domain's accuracy. [R19, §§3–5; L9–L10]

**Figures:** raw/processed waveform with independently labeled onset; spectrogram; detection function/threshold/refractory state on a common time axis; pitch/active-note piano roll against labels; window/causal-lookahead diagram. Show genuine successes **and failures** when data exists.

### 3.7 Real-time tasks, ISRs, shared state and timing budgets

| Current owner/context | Inputs → outputs | State/implementation fact | Required report/test detail |
|---|---|---|---|
| Driver ISR/internal DMA machinery | ADC → driver pool | Driver-owned buffering; optional callbacks would be ISR context. [R8] | Interrupt configuration, pool overflow count, IRAM behavior and no blocking application callbacks if later used. |
| Capture task, core 1, priority 5 | Blocking 64-sample read → hint → ring pushes | Owns capture lifecycle in normal operation; synchronous FFT/log callback can delay the next read. [L3–L4] | Worst observed service time and inter-read gap, error-loop behavior, high-water stack, effects with hints on/off. |
| Stream task, core 0, priority 4 | Ring → framer → nonblocking queue send | Owns framer/sample index; polls with `vTaskDelay(pdMS_TO_TICKS(1))`. [L4–L5] | Actual tick rate/rounding, wakeup jitter, frame pointer lifetime, ignored return values, pre-framer loss accounting. |
| TX task, core 0, priority 4 | Queue copies → WebSocket client | Queue depth 8; connect/send timeouts and drops. [L6] | Queue occupancy, network stalls, per-frame age, driver/internal network task priorities. |
| WebSocket event callback | Connected/disconnected → HELLO/status | Changes readiness; does not reset framer. [L6] | Actual callback context, ordering with queued audio, reset ownership across cores. |
| Main metrics task | Metrics snapshot → log | Ten-second sent/reconnect/drop log. [L4] | Logging perturbation and missing ADC/ring diagnostics. |
| Host runtime | Ingest → transcriber → notes | Feed/inference reached synchronously; separate host clock. [L9] | Event-loop blocking, host threads/backend, input backlog, output freshness and session ownership. |

Describe SPSC assumptions, C11 acquire/release edges and whether atomics are lock-free on the selected toolchain; do not claim lock freedom from the word `atomic` alone. Shared metrics use a spinlock in the current source. In ESP-IDF SMP, disabling local interrupts or suspending one core's scheduler does not protect shared state from another core. Task creation stack sizes are **bytes**, unlike vanilla FreeRTOS word-based conventions. [R12, Tasks / Scheduler Suspension / Critical Sections]

A useful timing decomposition is:

\[
L=t_{output}-t_{reference}
=L_{mechanical/AFE}+L_{observation}+L_{scheduling/queues}+L_{compute}+L_{transport}+L_{presentation}. \tag{6}
\]

Define boundaries so terms do not double-count overlapping work. The whole-chain trace is authoritative; a sum of average or percentile stage times is not generally the whole-chain percentile.

For periodic stage `i`, state release interval `T_i`, deadline `D_i`, observed execution `C_i`, blocking/interference and jitter. `Σ C_i/T_i` per core is useful **screening arithmetic**, not a proof of schedulability for a Wi-Fi/SMP system. Report **maximum observed time under stated stress**, not “WCET” unless a genuine worst-case argument exists. [R13]

**Proposed report excerpt format—not new firmware:**

```text
Stage: capture-read + preprocessing + optional hint
Context: core 1 task, priority 5; IDF tick rate = RECORD
Input block: 64 conversion results; nominal span = 4 ms
Output ownership: ring producer only
Loss/error policy: DESCRIBE ACTUAL SOURCE; deviations = RECORD
Observed service time p50/p95/max: NOT MEASURED
Longest inter-read gap / ADC pool overflows: NOT MEASURED
Evidence: firmware/config hash + trace file + analysis command
```

### 3.8 Output interfaces, state semantics and failure handling

- [ ] For the current path, document Wi-Fi STA → WebSocket `/stream` → server → `/notes`, addressing/configuration, transport security/trust boundary and reconnect behavior. Do not describe original-ESP32 sibling ESP-NOW as this project's output.
- [ ] Include byte layout, endianness, types/ranges, PCM units, payload limits, control frames, version negotiation/validation, sequence wrap, session reset and malformed-input handling. Cite canonical contract, then describe deviations. [L7]
- [ ] Specify timestamp clock/domain/epoch. Current framer's `timestamp_ms` is derived from sample count, while hint timestamps come from boot-time timer reads; explain alignment before comparing them. [L5, L8]
- [ ] Resolve note snapshot versus transition semantics, source authority, stale-note clearing, duplicate events, missing note-offs, stuck-note prevention, maximum state age and reconnect reset.
- [ ] If actual output is MIDI, specify DIN/UART versus USB/BLE/network transport, serialization/packetization, MIDI channel/note-on/off/velocity semantics and measured endpoint. If actual output is audio, add DAC/I2S sample format, clocking, codec/amp/filter, underflow and output latency. **Neither is established by the present source inventory.**
- [ ] If UI/page turning is claimed, include software version, frame/render scheduling, browser/mobile event compatibility and visual-output measurement—not merely server event time.
- [ ] Error table: sensor unplugged/shorted or stuck, rail/bias out of bounds, clipping, ADC invalid/timeout/pool overflow, ring/TX overrun, allocation/task creation failure, Wi-Fi loss, malformed frame, model load/inference failure, host backlog, restart and power interruption.
- [ ] For each fault, state detection, owner, bounded response, degraded-output indication, recovery/reset, diagnostic counter and corresponding test. “Print an error” is not a full recovery policy.
- [ ] Distinguish fail-fast initialization (`ESP_ERROR_CHECK`) from recoverable runtime handling. Main capture/stream task creation return values and read/push/send failure paths merit documentation and future review. [L3–L6]
- [ ] Treat automatic fake-transcriber fallback as an explicitly signaled simulation/degraded mode; for physical accuracy evaluation, reject that run rather than silently score it. [L9]

**Artifacts:** interface table, annotated sample real frame/event, startup/reconnect sequence diagram, error-state machine, fault matrix and a failure trace. Omit credentials and participant-identifying data.

### 3.9 Power, grounding, noise, CPU and memory

**Electrical:** identify supply/regulator/cable, measured rail/bias ripple and voltage droop during radio activity, decoupling placement, analog return path, sensor cable shielding/ground termination, USB-ground loops, digital switching aggressors, brownout behavior and thermal conditions. Avoid generic advice to split ground planes without explaining return-current paths. S3 hardware guidelines explicitly discuss decoupling and transmit-current surges; module-board implementation must be checked rather than copying bare-chip recommendations wholesale. [R16, Power Supply / Analog Power Supply]

**Resources:** provide static link-map flash/IRAM/DRAM usage; runtime heap by capability; minimum-ever free heap; largest free block (fragmentation); task stack high-water marks; CPU occupancy per core/task; queue high-water marks; allocation failure counts; and network bandwidth. Peak memory includes dependencies, driver pools/descriptors, Wi-Fi/TCP/WebSocket stacks, FFT scratch/tables and host model activations—not only user arrays. [R14]

Derived source examples, **not a complete measured budget**: ring storage 8 KiB; three explicit application task-stack requests total 12 KiB (capture, stream, TX); optional hint's three main arrays total 14 KiB (`1024 floats + 2048 floats + 1024 int16`), excluding FFT library tables and call-stack use. TX queue reserves at least 16 KiB for its eight payload slots, plus metadata/queue overhead. [L4, L6, L8]

Capture resource trends before/after reconnect storms and long runs. Compare instrumentation-enabled and representative release configurations: verbose UART output, heap poisoning and tracing can materially alter timings. CPU cycle counts are per-core; do not subtract readings from different cores. [R13–R14]

### 3.10 Build and analysis reproducibility

- [ ] Record repository commit and dirty patch; exact target, IDF commit/release, compiler and flags, CMake/Ninja/Python, environment/container digest and OS/architecture.
- [ ] Archive complete generated `sdkconfig` (with secrets redacted separately), defaults, component manifest/resolution lock, partition table, flash/PSRAM settings, link map and build log. `sdkconfig.defaults` is not the complete resolved configuration. [R15]
- [ ] Record managed ESP-DSP/WebSocket versions, protocol/schema revision, firmware binary/ELF hashes and hardware revision; exact host dependency environment, model backend/weights and UI version. Dependency ranges are not a reproducible lock. [L14; R15]
- [ ] Give commands from a clean checkout **using `current/src/...` paths**. Separate host/synthetic gates, cross-build and authorized future hardware validation; record tests not run and why.
- [ ] Capture experiment/analysis manifests with input and label hashes, scripts, random seeds, matching policy, exclusions, environment, units and figure regeneration commands. Keep immutable raw data and loss maps.
- [ ] Establish contribution/provenance/licensing for inherited code, model weights, recordings, sheet music and borrowed figures. Consider consent/privacy for sessions and incidental speech; consult institutional rules rather than asserting an exemption.

An appendix may list build commands such as `idf.py --version`, `idf.py build`, `idf.py size` and dependency inspection **as a future reproducibility recipe**; none was run in this investigation. Do not print unverified old quick-start commands as proven instructions.

---

## 4. Concrete verification matrix

**All rows below are proposed and NOT RUN here.** Replace illustrative sample counts with a justified protocol before collection. Freeze acceptance targets before looking at held-out results. Run safety/identity checks first; do not connect unverified piezo outputs to an MCU or overdrive a pin to “test its limit.” [R1 Appendix A; R3; R6]

| Test ID | Claim / future test and conditions | Measures and verdict basis | Required artifacts |
|---|---|---|---|
| **T00 Identity/build** | Reconcile actual board/module/pins, schematic/BOM, target/ADC format; clean cross-build and host contract tests | Correct target/format; exact config and build success; source/test status | Board markings/photo, schematic revision, config/lock, build log, ELF/map/hash |
| **T01 AFE safety and bias** | Qualified bench review; staged, current-limited tests of both signal polarities, expected transients, startup and powered-off conditions; MCU disconnected until safe | Bias/headroom, clamp/current path, overshoot, recovery, rail injection versus selected-part limits | Annotated scope captures/CSV at sensor-input and protected/ADC nodes, equipment/probe setup, reviewed calculations |
| **T02 AFE gain/filter** | Small-signal sweep in intended band and above Nyquist, multiple input levels; known source impedance or piezo-equivalent network | Gain/phase, passband/stopband rejection, low-frequency rolloff, saturation/recovery; compare prediction | Input/output traces, gain/phase plot, source impedance and component values |
| **T03 ADC transfer/calibration** | Known safe DC levels and AC tones at relevant amplitudes; exact attenuation/config; repeat radio/load states | Raw codes versus calibrated voltage, residual error, resolution/noise, clipping; requested versus actual scale | Raw codes before block mean removal, calibrated output, DMM/reference readings, residual plot |
| **T04 Sampling/timing/loss** | Known waveform plus timestamp/sequence instrumentation; sustained acquisition, CPU/radio stress, intentional consumer delays in a controlled future test build | Effective `f_s`, drift, block service interval/jitter, all loss counters, channel validity/skew if multichannel | Raw records, logic/GPIO markers, config, stage counters, occupancy/time plot |
| **T05 Noise/clipping/dynamic range** | Terminated/equivalent source, connected quiet sensor, soft-to-loud notes/chords, radio idle/busy, representative supplies | Band-limited noise RMS/PSD, tone SNR or signal-to-background ratio, headroom, clipping fraction, minimum detectable level at stated error rate | Raw and processed waveform/PSD, gain settings, stimuli/labels, rail traces |
| **T06 Mount/remount response** | Suggested pilot: three safe candidate locations × three independent remounts; fixed note/dynamic script and electronics | Per-register amplitude/SNR/detection; within-mount and between-remount variation | Dimensioned placement photos/log, raw sessions and paired comparisons |
| **T07 Single-note/onset correctness** | Suggested pilot: ≥12 notes spanning declared register × three dynamics × ten repetitions, randomized; plus quiet and mechanical disturbances | TP/FP/FN; precision/recall/F1; false events/minute; double triggers per true event; pitch/octave error; onset error | Matched real reference labels, event stream, waveform overlay, error list |
| **T08 Repeat/rearm** | Repeated same note, trills, releases and sustained notes; inter-onset intervals swept around claimed limit; soft-after-loud | Missed repeats, doubles from ringing, note-off/rearm behavior, recovery after clipping | Ground-truth event times, detector state/detection function, event timeline |
| **T09 Polyphony/crosstalk** | If claimed: 2/3/4-note chords, close/octave-separated pitches, staggered onsets, pedal on/off, loud/soft masking. If multisensor: one channel excited with others observed | Per-note/chord recall, extra notes, octave confusions; cross-channel amplitude and false-trigger matrices | Piano rolls/confusion matrices, matched raw recordings/labels; explicit chord grouping policy |
| **T10 Velocity/calibration repeatability** | Only if claimed: independently referenced dynamics/velocity, per-key or register calibration; repeat sessions/remounts and held-out levels | Mapping/residuals, monotonicity, MAE or rank correlation, saturation, between-session shift | Calibration/test split, reference semantics, fitted curve and held-out errors |
| **T11 End-to-end latency** | Physical reference → actual claimed output; cold/warm, idle/loaded network/CPU and representative notes/dynamics; suggested ≥300 stimuli per principal condition spread over sessions | p50/p95/p99 if supported by sample size, maximum, IQR/SD, deadline-miss rate; misses reported separately | Same-clock traces or validated clock mapping; per-event table incl. unmatched inputs; ECDF/histogram |
| **T12 Protocol/fault/recovery** | Host malformed/duplicate/gap/wrap corpus; future controlled disconnect/reconnect, queue pressure, host/model failure, startup order | No stale session contamination; loss visibility; bounded recovery; no unlabelled fake results/stuck notes | Corpus, C/Python results, session/event logs, fault injection times and recovery trace |
| **T13 Resource budget** | Worst representative processing, hints on/off, actual transcriber/backend, radio traffic and output consumers | Task/core occupancy, service deadlines, min heap/largest block, stack margins, queue occupancy, binary size | Map/size, runtime stats, heap/stack trends, instrumentation settings |
| **T14 Soak/stability** | Suggested exploratory stages: 30 minutes then multi-hour run; quiet/active alternation and controlled reconnects; duration adapted to intended use | Resets/watchdogs, unbounded backlog, dropped samples/frames, stale notes, memory growth, time drift, recovery counts | Complete logs and counters, memory/latency trends, reset causes, failures and exclusions |
| **T15 Application behavior** | Only if UI/score following is claimed: independent labeled score/performance; pauses, repeats, skipped/extra/missed notes, error-injected note streams | Correct progress/page boundaries, wrong page turns, recovery and visible-output latency | Score/version, input source labels (real/replay/simulated), synchronized UI recording |

A 45-minute demonstration or three correctly highlighted keys is useful feasibility evidence, not a statistical validation of 88-key performance. Repeating the same waveform 300 times estimates system timing under that workload; it does not supply 300 independent pianos or performances.

---

## 5. Measurement protocols and analysis definitions

### 5.1 Common protocol for every physical measurement

1. **Freeze the question and boundary.** Name requirement/test, actual versus illustrative target, independent/dependent variables and expected operating conditions.
2. **Identify apparatus.** Board/sensor/AFE/piano/run IDs; probe/instrument model and calibration status; gain, bandwidth, attenuation, sample rate, record length, coupling, trigger level and all relevant settings. Include wiring/test-point and ground-reference diagram. [R1 A.3–A.5]
3. **Review safety.** Use appropriate voltage-rated/high-impedance or differential probing and current-limited excitation. Do not attach an earth-referenced scope ground to an unknown node or defeat protective earth. Probe loading becomes part of the sensor load and must be quantified.
4. **Warm up and establish baseline.** Record quiet/zero/reference readings before and after; document changes in temperature, supply and placement.
5. **Collect raw and processed evidence.** Preserve ADC codes before mean removal when measuring the acquisition chain; archive processing state, packet/loss counters, timing markers and labels. A screenshot alone is insufficient for distributions or reproducible spectral analysis.
6. **Control/order/repeat.** Randomize note/level or condition order when possible, use independent sessions/remounts, record operator and deviations; do not tune on held-out test observations.
7. **Analyze from immutable input.** Scripts emit per-trial records plus aggregate tables/plots; disclose invalid/unmatched samples rather than deleting awkward runs.
8. **Verdict.** Pass/fail/not evaluated against the frozen requirement, with uncertainty and limitations. Preserve negative results.

### 5.2 Oscilloscope and logic-analyzer trace plan

Recommended future traces:

- **Analog overview:** sensor or source node, conditioned/bias node, ADC input and supply rail on common timebase; capture quiet, soft note, loud transient and recovery. Where instrument channel count is insufficient, document repeated-run comparability and do not claim simultaneity.
- **Timing view:** independently detected physical/electrical onset plus GPIO markers for block availability, processing begin/end and event enqueue. Marker assignment/pulse semantics and firmware revision must be recorded. These markers do **not** exist as a completed measurement feature in the inspected source.
- **Communication:** relevant physical digital output or a loopback observer with independently characterized delay. Decode the actual interface only (e.g. UART if selected); a logic analyzer does not directly observe when a Wi-Fi packet is delivered or a browser paints.
- **User-visible endpoint:** photodiode/scope for a display indicator, captured electrical MIDI endpoint, or audio loopback if audio output is the claimed output. A GPIO toggled before the browser updates measures an earlier boundary.

State scope/logic resolution and timing uncertainty, probe delay/skew, trigger definition, acquisition dead time, missed-trigger risk and measurement overhead. Do not equate callback pulse jitter with individual ADC aperture jitter: DMA block/service timing is a different observable. [R13, Measuring Performance]

### 5.3 End-to-end latency and jitter protocol

**Define three separate quantities:**

1. **Output availability latency:** `L_i = t_output_available,i − t_reference,i`.
2. **Estimated onset timing error:** `e_i = t_estimated_onset,i − t_reference,i` after valid clock alignment.
3. **Variation/jitter:** the spread of `L_i` (state whether SD, IQR, p95−p50, or range), not onset-estimation error and not clock drift.

Choose reference honestly: hammer/string excitation, first detectable piezo vibration, externally generated protected electrical onset, or MIDI key event. A MIDI event is not automatically the hammer-contact/audio onset; characterize its offset/jitter or label the metric “MIDI-to-output.” Electrical replay at the AFE excludes mechanics; replay over WebSocket excludes the complete embedded acquisition path. [R17 §I.B; R18 §3.1]

**Acquisition:** prefer a common instrument clock capturing reference and real output. If separate MCU/laptop clocks are necessary, estimate offset and drift using repeated synchronization events and an affine mapping `t_host = a·t_device+b`; retain fit residuals and synchronization uncertainty. NTP or a single start timestamp is not automatically adequate. Do not subtract ESP boot-time and host monotonic timestamps directly.

**Sampling plan:** vary input timing relative to block/window boundaries; run cold-start and warmed-up model sessions; quiet and loaded host/network; soft/loud and repeated notes; log actual backend/fallback. Suggested pilot ≥300 inputs per major condition is an engineering starting point, not a universal power calculation. p99 from 300 events describes only a few tail observations; obtain a larger sample or report wide uncertainty instead of precision theatre.

**Matching:** match reference and output one-to-one using note identity if applicable, session, order and an explicit allowed window. Keep every true stimulus row, including no output, double output, and wrong output. Never compute the headline latency only from convenient fast successes without reporting unmatched inputs and deadline failures. A latency timeout is censored/no-response evidence, not a zero latency.

**Report:** sample/session counts, detected fraction, p50/p95/p99 where supported, max observed, SD/IQR, deadline exceedances and response misses, ECDF and temporal trend. Use confidence intervals reflecting dependence (e.g. session-level resampling for performance estimates); do not present adjacent frames as independent experiments. Keep within-session jitter separate from between-session differences.

**Existing harness caveat:** it starts timing after `await ws.send(frame)` for the whole onset-containing frame, then selects an unmatched expected note of the same pitch. It omits the wait to acquire that frame and can misassociate repeated notes; it also records only matched events. It remains useful after audit as a **host replay-to-event subsystem benchmark**, never as a physical whole-chain latency result. [L12]

### 5.4 Clipping, noise, SNR and dynamic range protocol

Record both **analog clipping** (flat tops, slew limits, overload recovery at each stage) and **digital clipping** (raw ADC limits or chosen calibrated envelope, plus int16 saturation after processing). Define threshold and denominator, for example:

\[
r_{clip}=N_{samples\ outside\ declared\ valid\ envelope}/N_{samples}. \tag{7}
\]

Thresholds must correspond to the actual chain, not automatically `0`/`4095` or `±32767`. Analog op-amp saturation may occur well before those codes.

For noise, use a stated band and configuration: sensor-equivalent termination for electronic noise; connected sensor with no playing for operational background; quiet pre/post windows; Wi-Fi and supply comparisons. Report RMS and PSD, spectral window/length/overlap, equivalent-noise bandwidth where relevant, and averaging method.

\[
 x_{RMS}=\sqrt{\frac1N\sum_n(x[n]-\bar x)^2},\qquad
 SNR=20\log_{10}(V_{signal,RMS}/V_{noise,RMS}). \tag{8}
\]

Define how `V_signal,RMS` is isolated. For a controlled sine, separate fitted fundamental, harmonic distortion and noise. If comparing a music-window RMS with a separate silent-window RMS, call it **signal-to-background ratio** unless a justified signal/noise separation is performed. Use the same gain, units and band; broadband versus band-limited numbers are not interchangeable. ADC counts require calibration before voltage units; dBFS requires an explicit full-scale RMS convention.

Characterize dynamic range using a level sweep: loudest **undistorted** condition down to quietest signal meeting the declared detection-error criterion. ADC electrical dynamic range, acoustic dynamic range and usable trigger dynamic range are different. If `20 log10(V_max_clean/V_noise)` is reported, name it as the electrical ratio and document band/level. A soft/loud MIDI label is not a calibrated dB SPL measurement.

### 5.5 Missed, false, double triggers and note metrics

Freeze a matching policy before evaluation:

- For global attacks, decide how closely spaced notes in a chord are grouped into one onset; for transcription, preserve separate note identities. Dixon intentionally did not penalize merged chord onsets because he was not recognizing notes; that policy is inappropriate if copied directly into per-note chord evaluation. [R18, §3.1]
- Use one-to-one matching within a declared tolerance; report extra same-note detections as false positives and separately as double-trigger rate. Misses are unmatched reference events.
- `Precision=TP/(TP+FP)`, `Recall=TP/(TP+FN)`, `F1=2TP/(2TP+FP+FN)`; specify zero-denominator behavior. Also report raw counts, false positives per silent minute and doubles per reference event. [R18]
- Report **note-onset F1**, frame-level active-note F1 and note-with-offset F1 separately where applicable. Frame-heavy sustained notes can hide missed attacks or repeated spuriously short notes. [R19, §2]
- For comparability, an optional literature-style note match can use onset ±50 ms and a declared pitch tolerance; if offsets are included, state the exact tolerance (O&F used max(50 ms, 20% of reference duration)). These evaluation tolerances are **not a latency acceptance target**. [R19]
- Break down by register, dynamics, polyphony, pedal, session, placement and disturbance. Show examples of octave/harmonic errors, soft notes masked by loud ringing, repeated notes merged, and pedal/key noise mistaken for notes.
- Verify evaluation tool semantics/version. Current `check_golden.py` is onset-oriented and does not measure actual offsets. Do not simply label its scalar output “transcription accuracy.” [L13]

### 5.6 Dynamic calibration and repeatability protocol

For an intensity/velocity proxy, collect multiple independent levels/repetitions per note or register using an independently documented reference. Separate calibration and evaluation sessions, including remounts. Plot proxy versus reference with residuals, state monotonicity/saturation, use a fitted mapping only from calibration data, and report held-out error and drift. No independent velocity reference → describe repeatability/relative response, **not absolute key or hammer velocity accuracy**. [R19, §3.1]

For multiple sensors, measure excitation `i` and response `j` over fixed attack/band windows; a possible crosstalk quantity is `20 log10(A_j/A_i)` with noise-floor/zero-response handling. Add the **trigger confusion matrix**, since a low amplitude ratio can still trigger a low-threshold neighboring channel. For a single mixed soundboard signal, prefer false-note matrices and masking tests rather than pretending each note has a separate electrical channel.

### 5.7 CPU/memory and long-run protocol

Build a release-like instrumented profile and state logging/tracing overhead. Capture per-core/task execution over representative workloads, not only idle averages; measure processing and inter-service gaps around FFT/model calls. Archive stack margins, heap minimum/largest block, driver/ring/network losses and queue occupancy over time. [R12–R14]

For soak tests, define duration and workload schedule, checkpoint counters and reset reasons; include quiet intervals, sustained playing, host stalls and controlled reconnects. Look for monotonic heap decline, fragmentation, stale notes, sequence drift and growing queue age. Report longest observed stable run and all observed failures, not “100% reliable.” Even zero observed failures does not establish zero failure probability; any statistical upper bound requires stated independence/stationarity assumptions.

---

## 6. Requirement → design → implementation → test traceability

### 6.1 Blank template

| Requirement ID / revision | Need and rationale/source | Operating condition / measurable target / units | Design decision and alternative rejected | Implemented artifact + configuration | Verification/test ID and oracle | Raw artifact + analysis/version | Result / uncertainty | Verdict / limitation |
|---|---|---|---|---|---|---|---|---|
| REQ-___ | Who needs what and why? | Define numerator/denominator, endpoint and condition; mark provisional targets | Decision ID, equation, datasheet section | Commit, file/function, schematic/BOM/config hash | Inspection / calculation / host / simulated / bench / full system | Immutable run ID, hashes, command | NOT MEASURED until evidenced | Pass / fail / partial / not evaluated |

This is a many-to-many map: one test can verify several requirements, and one requirement may need electrical, software and physical tests. A code unit test cannot close an AFE safety requirement. [R1, Appendix B.5]

### 6.2 Worked examples—**illustrative targets; no measurements**

| ID | Illustrative requirement | Proposed design link / actual source status | Planned test and evidence | Current result |
|---|---|---|---|---|
| **ILL-LAT-01** | Under specified warm-model, single-note C3–C6, three-dynamic, normal-network conditions, **p95 physical-reference-to-client-event latency ≤150 ms**; response-miss rate reported separately. This is not a promise of 150 ms UI display or all-key/polyphonic performance. | Small causal observation/queue/compute budgets would be required. Existing 320-sample frames span 20 ms; current Basic Pitch two-second windows do **not** justify feasibility of this target. | T11 common-clock/reference mapping, ≥300 inputs/condition pilot, every stimulus retained; ECDF and p95 CI; exact client-event boundary. | **NOT MEASURED; design feasibility unresolved.** |
| **ILL-DET-01** | On a held-out, declared single-piano/register dataset, per-note onset F1 ≥0.90 at ±50 ms matching tolerance; false notes during silence ≤1/min. | L8 hint is a baseline only; chosen detector must define onset/rearm/pitch semantics. Thresholds frozen using calibration/validation sessions. | T07/T08, paired raw/label/event files; one-to-one matching, counts and per-register results. | **NOT MEASURED.** |
| **ILL-DATA-01** | At configured 16 ksample/s, zero **unreported** sample discontinuities during a 30-minute defined workload; every loss site accounted for. | ADC/ring/TX counters and discontinuity propagation needed; framer-only sample index is insufficient. [L3–L7] | T04/T12/T14, known input, delayed consumers, counter reconciliation and timestamp discontinuity checks. | **NOT EVALUATED; source-level observability gap.** |
| **ILL-SAFE-01** | Under explicitly bounded sensor transients and powered/unpowered states, ADC/op-amp pins and injected currents remain within selected-component limits with stated margin. **No generic numeric voltage limit is assumed.** | Reviewed AFE protection/bias/gain and current paths; existing schematic labels conflict. | T00/T01, manufacturer limits plus instrumented protected-node/current evidence before attachment. | **NOT VERIFIED; board/BOM unresolved.** |

**How to write a future result honestly:**

> “REQ-… was evaluated in run … using firmware … and AFE … . Of … stimuli, … produced valid outputs and … missed the deadline. The measured p95 was … ms (interval …, method …). This satisfies/does not satisfy the requirement under … conditions; remounted/different-piano operation was not tested.”

Leave placeholders visibly empty until real artifacts supply them. Do not populate them with plausible numbers for visual completeness.

---

## 7. Priorities and main-text versus appendix split

### 7.1 Minimum essential: do these first

1. **Truthful scope/status and exact identity:** one supported architecture per result, actual board/sensor/circuit, source/target mismatch resolution, fake/planned/physical legend.
2. **Testable requirements and reference definitions:** what constitutes a note/onset, which output endpoint and clock, how errors are counted.
3. **Safe and characterized signal chain:** schematic/BOM, mounting, bias/protection/headroom/filtering, real raw waveform and noise/clipping evidence.
4. **Reconstructable acquisition/algorithm:** driver/ADC/format/config, data ownership and loss semantics, full processing parameters, causal window/latency explanation.
5. **Small valid evidence bundle:** matched capture and labels, detection counts, latency distribution plus misses, error examples, loss/resource/short-soak observations with run provenance.
6. **Reproduction recipe and limitations:** versions/configs/hashes, analysis script and explicit unavailable tests/results.

A short report may concentrate on these and honestly omit polyphony/velocity/ML/page turning if not part of its claim. Safety, known contradictions and adverse results are never “appendix-only to save space.”

### 7.2 Strong research-grade additions

- Independent sessions/remounts and held-out instruments; larger balanced dataset and power/sample-size justification.
- Compare simple onset/pitch baselines and selected model under identical conditions; parameter sweeps on validation only; ablations for placement, AFE, block mean removal, window/hop and backend.
- Full AFE magnitude/phase/noise/alias rejection and calibration residuals; tolerances, overload recovery and environmental sensitivity.
- Hardware/host timing decomposition validated against whole-chain measurements, clock drift and measurement uncertainty, tail distributions under stress.
- Multisensor electrical/mechanical crosstalk or single-sensor masking/polyphony analysis, as applicable.
- Embedded ML feature/quantization parity and peak activation/arena budgets if embedded inference is actually pursued.
- Multiple-board repeatability, multi-hour soak/fault testing, failure-mode analysis, reproducible containers/locked dependencies and regenerated figures from raw data.

### 7.3 Placement by artifact

| Keep in main text | Put full detail in appendices / evidence archive |
|---|---|
| System boundary/status diagram and requirement summary | Full traceability register and historical requirements/decisions |
| Actual AFE schematic readable at report scale and key limits | Full sheets/netlist/BOM, footprints, assembly deviations, calculations |
| Mounting photo with dimensions; test-point/clock diagram | All placements, session photos, instrument certificates/settings |
| Ownership/task/queue table and timing budget | Full configuration, driver/RTOS settings, memory map and detailed traces |
| Exact critical DSP parameters, selected equation and short annotated source excerpt | Full source at immutable revision; coefficients, model metadata and parity fixtures |
| Requirement verdicts, latency ECDF, error counts and representative failure traces | Per-event CSV/JSON, complete logs, raw waveforms, scripts, all subgroup tables |
| Limitations, unanswered evidence gaps and next steps | Environment manifests, checksums, dataset cards, consent/access information |

**Adaptable compression:** for a ~6-page main body, prioritize one architecture figure, one AFE/mounting panel, requirement/implementation tables, method diagram and honest results/limitations. For ~12–20 pages, separate hardware/acquisition/DSP and devote real space to characterization and errors. These are suggested layouts, **not known UREX limits**. If there are no results, do not pad the “results” pages: use a status/verification-readiness table and call the document an interim report.

---

## 8. Proposal versus as-built report; limitations, units and uncertainty

### 8.1 Different documents make different claims

| Topic | Design proposal | As-built technical implementation report |
|---|---|---|
| Circuit | Candidate topology and calculations, component selection rationale | Actual schematic/BOM/revision and assembly deviations; measured electrical behavior |
| Firmware | Planned drivers/tasks/protocol and feasibility budget | Exact compiled target/config, implemented state ownership/error behavior and provenance |
| DSP/model | Hypothesis, alternatives, planned window/features/model | Actual numerical pipeline/parameters/backend and validated data contracts |
| Performance | Target/prediction with assumptions | Measurement with method, conditions, raw evidence, uncertainty and failures |
| Verification | Proposed apparatus/tests/sample size | What ran, what did not, deviations, data/analysis and requirement verdicts |
| Conclusions | Feasibility/risk and next experiments | Supported findings and bounded generalization; remaining unknowns |

Appropriate current wording: “The source implements a 320-sample framing component; physical end-to-end timing has not been established.” Inappropriate: “The system samples reliably at 16 kHz with low latency,” based only on Kconfig and a replay harness. Proposal language (“will,” “intended,” “hypothesized”) must not become past-tense achievement by editing style alone.

### 8.2 Threats to validity that matter here

- **Construct validity:** onset label versus keypress versus audible transient; active string versus key state; MIDI velocity versus amplitude; event time versus availability time; one global onset versus all chord notes. [R17–R20]
- **Internal validity:** ground-truth clock mismatch; ADC format/config errors; silent fake fallback; matching errors; filtered/centered recordings hiding bias/clipping; inconsistent preprocessing across PC/device; different acquisition paths used for input and calibration; probe loading; logging-induced timing changes.
- **Selection/analysis bias:** tuning thresholds on test data; choosing only best placements/notes/runs; omitting no-response events from latency; averaging away tails; considering correlated frames independent; using unrelated MIDI as labels. Dixon explicitly cautions that same-instrument conditions and ground-truth-tuned parameters make results optimistic. [R18, §4]
- **External validity:** one piano, sensor, performer, room, board, power source, network and mounting; microphone-trained models on contact-piezo input; insufficient bass/treble/soft-note/polyphony/pedal coverage. Published acoustic/synthesized datasets are not a substitute for piezo-domain validation. [R19–R20]
- **Reliability/reproducibility:** missing toolchain/config/weights, moving `stable/latest` sources, unknown hardware revisions, overwritten results, undocumented calibration or script version.
- **Interpretation:** observed radio-correlated noise is evidence of association, not proof of a particular coupling path; a gain/filter change improving F1 does not prove every mechanism unless controlled ablations isolate them. Worst observed latency is not a guaranteed upper bound.

### 8.3 Units and uncertainty: exact reporting requirements

Use `V`, `mV`, `Hz`, `ksample/s`, `ms`, `µs`, `B`, `KiB`, `dB`, `dBFS`, and **ADC counts** explicitly. Distinguish bits/sample, conversion-record bytes, samples/frame, frames/s and aggregate/per-channel rate. Define Hz versus MIDI versus cents and amplitude versus power spectra. Label both axes and table units; use appropriate significant figures. Cite the provenance of externally sourced figures and equations. [R1 §§3.13, 6.2; R21]

Maintain an uncertainty budget for timing and voltage:

| Component | Example future evaluation | What not to conflate |
|---|---|---|
| Repeatability | Repeated measurements/sessions; Type A statistical estimate | Trial-to-trial variation is not the uncertainty of an average or percentile. |
| Instrument calibration/resolution | Manufacturer/calibration data, quantization, probe ratio/skew; Type B model | Display digits do not establish accuracy. |
| Synchronization/reference | Clock fit residual, drift, trigger threshold, MIDI/audio alignment | Timestamp units of µs do not imply µs true accuracy. |
| Circuit/loading | Gain/component tolerances, source/probe impedance, bias drift | Nominal component value is not the measured transfer function. |
| Label/matching | Annotation disagreement, onset ambiguity and tolerance | A ±50 ms matching window is not measurement uncertainty or allowable system latency. |

For a scalar result depending on inputs, combine standard uncertainties using sensitivities and covariance; simple RSS is valid only under appropriate independence assumptions. Report expanded uncertainty `U=k·u_c` with the coverage factor/method, not an unexplained “±.” NIST distinguishes Type A/B evaluation methods and explicitly cautions against confusing error with uncertainty. A 95% confidence interval on p95 latency and a systematic clock-calibration uncertainty are distinct statements. [R21, §§3–7, Appendix A]

Do not import obsolete unit conventions from an old course handout as standards; the UKZN guide is used here for report structure and experimental completeness, not as the authoritative SI definition.

---

## 9. Evidence gaps and practical next collection steps

### 9.1 Prioritized gap inventory

| Priority | Missing/conflicting evidence | Why it gates a defensible report | Next evidence-producing action—not implementation in this scout |
|---|---|---|---|
| **P0** | Actual board/module/silicon and wiring unknown; S3 docs versus TYPE1 source; old GPIO34 schematic | Cannot truthfully identify ADC/DMA/peripheral behavior or reproduce firmware | Photograph markings and wiring; preserve existing build/config if available; compare pin map/format to target-specific header/TRM; authorized engineer performs clean target build before any flash. |
| **P0** | Reviewed as-built AFE/sensor BOM and input safety absent | Physical capture claim could hide unsafe/uncharacterized input | Inventory real parts and sensor capacitance; annotate as-built schematic and test points; qualified review then disconnected-MCU/current-limited T01/T02 evidence. |
| **P0** | No current raw preprocessed/raw-code physical bundle or paired real ground truth found | Cannot claim electrical performance, musical accuracy or true latency | Define raw capture boundary and paired-label protocol; retain raw codes/bias/loss map as well as processed PCM and matched labels. |
| **P0** | Fake fallback and unsupported O&F instructions | “Successful” demo/evaluation could exercise a simulator | Record true backend/model at runtime and fail an accuracy run if fake; classify O&F as proposed until an actual adapter/build/test exists. |
| **P1** | ADC/ring/transport loss accounting and session semantics not end-to-end proven | Sample time can silently compress; reconnect may mix old/new state | Preserve source/config and add future diagnostic/test evidence at each loss site; host cross-language and fault corpus; then target traces under load. |
| **P1** | Analog/filter/calibration/noise/clipping response unmeasured | Cannot justify sample rate, resolution or usable dynamic range | Execute approved T02/T03/T05 under documented electrical conditions; compare actual radio/supply states. |
| **P1** | Replay latency mistaken for whole-chain timing | No physical or visible-output latency claim is supported | Define endpoint/reference; capture same-clock trace or characterize clock mapping; report replay separately. |
| **P1** | No mounting/remount/register/pedal evidence | Generalization from one note/place would be weak | Small randomized placement and note/dynamic pilot; independent remounts; save photographs and failures. |
| **P1** | Exact IDF/toolchain/config/components and model environment absent | Cannot reconstruct source behavior or budgets | Archive available actual build artifacts; generate a reproducibility manifest and clean-build evidence in a future authorized work item. |
| **P1** | CPU/heap/stack/queue and stability measurements absent | Real-time/resource claims unsupported | T13 and staged T14; collect maximum observed service gaps, min heap/largest block, stack margins and loss counters. |
| **P2 conditional** | Full polyphony, velocity, embedded CNN, robust page turning not established | These claims require distinct algorithms/labels/tests | Expand scope only after baseline acquisition/evidence works; use T09/T10/T15 and embedded parity/resource tests as applicable. |
| **P2** | Rubric/page limit, authorship/licensing and data-governance specifics not supplied | Final presentation/provenance may need adaptation | Apply the real course rubric when available; include contribution map and data-access policy. This does not block the present guidance. |

### 9.2 Practical sequence for the project team

1. **Evidence freeze, before prose polishing:** create a manifest of what currently exists; ask the hardware owner to supply board/sensor/AFE photos and the actual flashed revision/config, without inferring them from filenames or old videos.
2. **Resolve identity and safety first:** reconcile S3/TYPE1/GPIO and component labels through source/datasheets and a no-hardware build; obtain the reviewed circuit and safe protected-node measurements before attaching the MCU.
3. **Fix the measurement specification before collecting data:** decide the operational onset/output definition for each run; pair real input with matching ground truth; disallow fake fallback in accuracy runs; distinguish direct ADC capture from laptop line-in/replay.
4. **Collect a small auditable pilot:** silence/electronic baseline, low/mid/high notes at several dynamics, repeats and loud transients; include timing/loss and rail/bias evidence. If polyphony is in scope, add a few defined chords/pedal cases without claiming comprehensive coverage.
5. **Analyze and write the implementation/status chapter from actual artifacts:** source/config/state ownership, schematic, measured transforms, raw-event errors, latency distribution and resource status. Preserve contradictory and failed observations.
6. **Expand only along the research question:** remounts/held-out sessions, alternative AFE or DSP ablations, polyphony and then embedded-model feasibility where warranted.
7. **Generate final figures and requirement verdicts from the archived data:** write the abstract/conclusion last; a negative or limited feasibility result is scientifically useful if reproducible.

**Potential follow-up work that may deserve a separate shipping task:** S3 ADC-format compatibility/build regression; sample-loss/session observability; and corrections to the physical guide's capture/label/latency/fake-mode instructions. They are source/method findings here, **not implemented fixes or reproduced hardware failures**. No PR is part of this scout.

---

## 10. Verified primary-source register and claim-level reading guide

All items below were **retrieved as document content and inspected**, not cited from search snippets. Access date: **2026-09-09**. Source-specific versions matter: ESP-IDF **v5.4.2** is a pinned documentation/source reference used for this investigation, **not a claim that the project uses it, that it is the latest release, or that the project passes on it**. Online datasheets/TRMs and hardware guidelines can change at their URLs; observed versions and selected hashes are provided below.

### University engineering-report guidance

**[R1] University of KwaZulu-Natal, Discipline of Mechanical Engineering, _Guide for Writing Technical Reports_, May 2015.** Adapted from Stellenbosch engineering guidance.<br>
Full URL: https://engineering.ukzn.ac.za/wp-content/uploads/2022/05/2015-Mech-Eng-UKZN-Guide-for-Technical-Reports.pdf<br>
**Inspected/useful sections:** §§2–3 (reader, structure, substantiated conclusions), §3.13 (figures/tables), §6.2 (equations); Appendix A.1–A.5, printed pp.15–16 (repeatability, apparatus/settings/calibration, procedures/raw data, set versus measured values); Appendix B.3–B.6, pp.17–18 (requirements, alternatives, testing, complete product description/BOM); Appendix C.3/C.6, pp.19–20 (sample calculations and traceability). **Supports:** the overall outline and evidence requirements. Its course formatting prescriptions are not the captain's rubric, and its old SI appendix is not used as a current standards source.

**[R2] Brandon Lucia, Carnegie Mellon University 18-545, _Design Reviews_, Fall 2016.**<br>
Full URL: https://course.ece.cmu.edu/~ece545/F16/slides/L05_DesignReviews.pdf<br>
**Inspected/useful sections:** slides 4–8: promise versus delivery, full design specification, hardware/software partition, interface definitions, block diagram, architecture/clocking/circuits, weak points and unanswered questions. **Supports:** design-review versus final-proof distinction and specific embedded-design content. A course lecture, not a UREX rubric or universal page requirement.

### Piezo and analog front-end manufacturers

**[R3] James Karki, Texas Instruments, _Signal Conditioning Piezoelectric Sensors_, SLOA033A, September 2000.**<br>
Full URL: https://www.ti.com/lit/an/sloa033a/sloa033a.pdf<br>
**Inspected/useful sections:** §2 and Fig.1, p.2 (charge/voltage equivalent models and dynamic rather than static sensing); §3, p.2 (wide output voltage range, impedance); §§3.1–3.2/Figs.2–3, pp.3–4 (voltage/charge modes, cable capacitance, bias, feedback and filter roles). **Supports:** why source impedance, cable, bias and protection/gain belong in the report; not a validated circuit or voltage bound for this sensor. Mathematical typography/parallel-capacitance notation should be checked against the actual circuit, not copied mechanically.

**[R4] Eduardo Bartolome, Texas Instruments, _Signal conditioning for piezoelectric sensors_, Analog Applications Journal, 1Q 2010, pp.24–31, SLYT369.**<br>
Full URL: https://www.ti.com/lit/an/slyt369/slyt369.pdf<br>
**Inspected/useful sections:** “Piezoelectric sensors,” p.24; “Analysis of the charge amplifier: Input impedance / Gain / Bandwidth,” p.25; low-pass and “Noise,” p.26; “Other practical considerations” and differential interference examples later in the article. **Supports:** deformation/resonance, virtual-ground charge mode, bandwidth/noise/bias-current tradeoffs, need to limit aliased noise. Component/example results are TI's, not this project's measurements.

**[R5] TE Connectivity, _DT Sensors_, Rev A2, 04/2025, pp.1–2.**<br>
Full URL: https://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FDT_Series_without_Leads%7FA1%7Fpdf%7FEnglish%7FENG_DS_DT_Series_without_Leads_A1.pdf%7F11026274-00<br>
**Inspected/useful sections:** Features/Specifications p.1; Dimensions and Part Numbers p.2. PDF identifies Rev A2 even though URL contains A1. **Supports:** real sensor datasheets specify loading, geometry, capacitance and attachment; DT example recommends 10 MΩ loading and warns of large output voltage range. **Applicability limit:** polymer film, not a measurement/specification of the repository's unknown piezo disc; no DT electrical values or attachment recommendations are assumed to transfer.

### Espressif silicon, peripherals, runtime and build

**[R6] Espressif, _ESP32-S3 Series Datasheet_, observed v2.2.**<br>
Full URL: https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf<br>
Resolved URL: https://documentation.espressif.com/esp32-s3_datasheet_en.pdf<br>
**Inspected/useful sections:** Table 2-8/analog pin assignment (GPIO1/ADC1_CH0); §4.2.2.1 p.59 (SAR ADC); §5.1 p.64 (stress versus operating ratings); §5.4 p.65 (DC characteristics); §5.5 p.66 Tables 5-5/5-6 (ADC characterization conditions, nonlinearity, calibrated ranges). **Supports:** target identity, 12-bit conversion, electrical/calibration conditions and the distinction between numerical word width and accuracy. Do not turn its power-pin maximum into a universal ADC clamp specification.

**[R7] Espressif, _ESP32-S3 Technical Reference Manual_, observed Version 1.8.**<br>
Full URL: https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf<br>
Resolved URL: https://documentation.espressif.com/esp32-s3_technical_reference_manual_en.pdf<br>
**Inspected/useful sections:** Chapter 39 “On-Chip Sensors and Analog Signal Processing,” especially §39.3; §39.3.7.5 pp.1472–1473 (scan pattern example); §39.3.7.6 p.1473 (32-bit DMA record and 12-bit data); §39.3.7.7 (digital filters); §39.3.8 (ADC2 arbiter). **Supports:** documenting scan/format/clock/controller decisions rather than generically saying “DMA.” Bitfield interpretation for firmware should also use the matching IDF header [R10]; do not generalize from this TRM to original ESP32.

**[R8] Espressif, ESP-IDF v5.4.2, ESP32-S3 _ADC Continuous Mode Driver_.**<br>
Full URL: https://docs.espressif.com/projects/esp-idf/en/v5.4.2/esp32s3/api-reference/peripherals/adc_continuous.html<br>
**Inspected/useful sections:** Driver Concepts, Resource Allocation, ADC Configurations, Register Event Callbacks, Read Conversion Result, Hardware Limitations, Power Management, IRAM Safe, Thread Safety. **Supports:** bytes versus records, GDMA allocation, partial reads/timeouts, overflow losses, driver buffer ownership, ISR callback constraints, ADC2 DMA restriction, power locks and lack of general API thread safety.

**[R9] Espressif, ESP-IDF v5.4.2, original ESP32 _ADC Continuous Mode Driver_.**<br>
Full URL: https://docs.espressif.com/projects/esp-idf/en/v5.4.2/esp32/api-reference/peripherals/adc_continuous.html<br>
**Inspected/useful sections:** Resource Allocation, Hardware Limitations, Power Management. **Supports:** original-ESP32 I2S0 DMA FIFO and target-specific resource/Wi-Fi behavior. Included specifically to prevent false cross-variant transfer, not as the active S3 configuration guide.

**[R10] Espressif, ESP-IDF v5.4.2 source, `components/hal/include/hal/adc_types.h`.**<br>
Full URL: https://github.com/espressif/esp-idf/blob/v5.4.2/components/hal/include/hal/adc_types.h<br>
API retrieved with `gh-axi`: https://api.github.com/repos/espressif/esp-idf/contents/components/hal/include/hal/adc_types.h?ref=v5.4.2<br>
**Inspected/useful sections:** output-format enum; target-conditional `adc_digi_output_data_t`; lines 150–177 original ESP32/S2 branch and 198–217 S3/P4 branch. **Supports:** S3 exposes `type2`, whereas current capture source dereferences `type1`. This is direct source inspection, not a flashed or compiled reproduction. S2's structure is another reason not to say every non-original variant behaves identically.

**[R11] Espressif, ESP-IDF v5.4.2, ESP32-S3 _ADC Calibration Driver_.**<br>
Full URL: https://docs.espressif.com/projects/esp-idf/en/v5.4.2/esp32s3/api-reference/peripherals/adc_calibration.html<br>
**Inspected/useful sections:** Introduction, ADC Calibration Curve Fitting Scheme, Result Conversion, Thread Safety, Minimize Noise. **Supports:** device-dependent reference, curve-fitting/eFuse requirements, `adc_cali_raw_to_voltage()` in mV, matching attenuation/bit width and noise caveats. Calibration is not equivalent to arbitrary 3.3 V scaling.

**[R12] Espressif, ESP-IDF v5.4.2, ESP32-S3 _FreeRTOS (IDF)_ documentation.**<br>
Full URL: https://docs.espressif.com/projects/esp-idf/en/v5.4.2/esp32s3/api-reference/system/freertos_idf.html<br>
**Inspected/useful sections:** SMP concepts, Tasks/Creation, Scheduler Suspension, Critical Sections, Floating Point Usage. **Supports:** core affinity, byte-count stack sizes, spinlock-based mutual exclusion and scheduler limitations. Only documented aspects are used; no schedulability claim follows from using two cores.

**[R13] Espressif, ESP-IDF v5.4.2, ESP32-S3 _Minimizing Execution Time_.**<br>
Full URL: https://docs.espressif.com/projects/esp-idf/en/v5.4.2/esp32s3/api-guides/performance/speed.html<br>
**Inspected/useful sections:** Measuring Performance; Improving Overall Speed/Reduce logging overhead; Targeted Optimizations. **Supports:** scope/logic measurements, timer/cycle-counter overhead, per-core cycle counters, cache variability, runtime task stats and instrumentation effects.

**[R14] Espressif, ESP-IDF v5.4.2, ESP32-S3 _Heap Memory Debugging_.**<br>
Full URL: https://docs.espressif.com/projects/esp-idf/en/v5.4.2/esp32s3/api-reference/system/heap_debug.html<br>
**Inspected/useful sections:** Heap Information, Allocation Failure, Heap Corruption Detection, Heap Tracing. **Supports:** minimum free heap, largest block/fragmentation, allocation failures, memory-integrity diagnostics and tracing overhead. Static array totals alone are insufficient.

**[R15] Espressif, ESP-IDF v5.4.2, ESP32-S3 _Build System_.**<br>
Full URL: https://docs.espressif.com/projects/esp-idf/en/v5.4.2/esp32s3/api-guides/build-system.html<br>
**Inspected/useful sections:** project structure and managed components; preset component/build variables (`IDF_VER`, `IDF_TARGET`); Custom sdkconfig defaults; target-dependent defaults. **Supports:** exact target/version/config and dependency-resolution evidence; distinction between defaults and resolved configuration.

**[R16] Espressif, _ESP32-S3 Hardware Design Guidelines: Schematic Checklist_, retrieved latest-page snapshot.**<br>
Full URL: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html<br>
**Inspected/useful sections:** Power Supply, Digital/Analog Power Supply, Power-up and Reset Timing, ADC pin mapping. **Supports:** decoupling/current-surge/reset and pin-assignment documentation. Bare-chip recommendations require interpretation for an actual module/devkit and AFE.

### Peer-reviewed music/DSP literature

**[R17] Juan Pablo Bello, Laurent Daudet, Samer Abdallah, Chris Duxbury, Mike Davies and Mark B. Sandler, “A Tutorial on Onset Detection in Music Signals,” _IEEE Transactions on Speech and Audio Processing_, 13(5), 1035–1047, 2005.**<br>
DOI: https://doi.org/10.1109/TSA.2005.851998<br>
Full text inspected (university-hosted paper copy): https://hajim.rochester.edu/ece/sites/zduan/teaching/ece472/reading/Bello_2005.pdf<br>
**Relevant sections:** I.B–C (onset/attack/transient and pipeline), III (detection functions), IV (postprocessing/threshold/peak selection), V (dataset/evaluation), VI (application-dependent choice). **Supports:** terminology, algorithm disclosure and threshold/label dependence. No published performance number is treated as a piezo-project result.

**[R18] Simon Dixon, “Onset Detection Revisited,” _Proceedings of DAFx-06_, pp.133–137, 2006.**<br>
Full proceedings PDF: https://dafx.de/paper-archive/2006/papers/p_133.pdf<br>
**Relevant sections:** §2.1 (positive spectral flux), §2.6 (onset selection/lookahead), §§3.1–3.3 (matching, merged/double events, representative data, implementation sensitivity), §4 (optimistic tuning/same-instrument limitations). **Supports:** why precise algorithm/evaluation details and held-out conditions are indispensable. Its noncausal peak-selection example cannot be silently copied as zero-lookahead embedded processing.

**[R19] Curtis Hawthorne, Erich Elsen, Jialin Song, Adam Roberts, Ian Simon, Colin Raffel, Jesse Engel, Sageev Oore and Douglas Eck, “Onsets and Frames: Dual-Objective Piano Transcription,” _ISMIR 2018_.**<br>
Author manuscript inspected: https://arxiv.org/pdf/1710.11153<br>
Version page: https://arxiv.org/abs/1710.11153 (inspected PDF identifies v2, 5 June 2018).<br>
**Relevant sections:** §2 (dataset/sustain and frame/note/offset metrics), §3 (frontend, bidirectional architecture/full-sequence inference), §3.1 (relative velocity), §5 (ablations). **Supports:** separating onset/frame/offset/velocity claims and causality from throughput. Does not establish repository O&F support, piezo-domain accuracy or S3 deployment.

**[R20] Rachel M. Bittner, Juan José Bosch, David Rubinstein, Gabriel Meseguer-Brocal and Sebastian Ewert, “A Lightweight Instrument-Agnostic Model for Polyphonic Note Transcription and Multipitch Estimation,” _ICASSP 2022_.**<br>
Author manuscript inspected: https://arxiv.org/pdf/2203.09893<br>
Version page: https://arxiv.org/abs/2203.09893 (PDF identifies v2, 12 May 2022).<br>
**Relevant sections:** §2 (note versus multipitch task), §3 (CQT/harmonic stacking, outputs, feature-map memory and postprocessing), §4 (metrics/datasets/validation), §4.5 (efficiency). **Supports:** Basic Pitch baseline provenance, model/frontend/postprocessing disclosure, memory and applicability limits. “Lightweight” is not proof of fitting this MCU or meeting its live latency target.

### Measurement and sampling methodology

**[R21] Barry N. Taylor and Chris E. Kuyatt, NIST Technical Note 1297, _Guidelines for Evaluating and Expressing the Uncertainty of NIST Measurement Results_, 1994 edition.**<br>
Full PDF inspected: https://nvlpubs.nist.gov/nistpubs/Legacy/TN/nbstechnicalnote1297.pdf<br>
NIST landing page inspected: https://www.nist.gov/pml/nist-technical-note-1297<br>
**Relevant sections:** §§3–4 (Type A/B), §5 (combination, covariance and corrections), §6 (expanded uncertainty), §7 (reporting), Appendix A (propagation). **Supports:** uncertainty budget and appropriate reporting, not an assertion that a particular instrument is calibrated.

**[R22] Meinard Müller and collaborators, International Audio Laboratories Erlangen, _Fundamentals of Music Processing notebooks: Digital Signals—Sampling_.**<br>
Full URL: https://www.audiolabs-erlangen.de/resources/MIR/FMP/C2/C2S2_DigitalSignalSampling.html<br>
**Inspected/useful sections:** Aliasing and Sampling Theorem, with executable demonstrations. **Supports:** band-limiting/Nyquist rationale and why digital postprocessing cannot recover arbitrary aliased input. Primary teaching material, not one of the peer-reviewed experimental papers above.

### Inaccessible or unsuitable evidence—not counted as verified support

- Melbourne technical/design-report pages were discovered, but direct HTTP retrieval returned **403**; their search text is not used as verified citation evidence. URLs: https://students.unimelb.edu.au/academic-skills/resources/reading,-writing-and-referencing/reports/technical-reports and https://students.unimelb.edu.au/academic-skills/resources/reading,-writing-and-referencing/reports/design-reports . UKZN and CMU originals supply accessible university guidance instead.
- Microchip MCP6001/2/4 datasheet attempt, https://ww1.microchip.com/downloads/en/DeviceDoc/21733J.pdf , returned **403**. No specific MCP6002 electrical limits are claimed from that inaccessible document. Exact op-amp part/datasheet verification remains an AFE evidence requirement.
- PCB Piezotronics mounting URL, https://www.pcb.com/resources/technical-information/tech-educational-papers/mounting , redirected to a general technical-information page without the required article content. Not used to substantiate a mounting method or frequency response.
- Prior scouts' private local vault, application PDF and video contents were not reverified here. No prior-storefront/pricing/new-chip assertions were needed.

---

## 11. Investigation record, reproducibility of this research, and completion

### What was done

1. Read the research skill and all three prescribed scout reports; inspected root README, living contracts/physical/O&F guidance, actual acquisition/streaming/hint/server/test source and KiCad evidence at the current revision.
2. Used search only to discover source locations. Retrieved primary HTML/PDF content, extracted PDF text with `pdftotext -layout`, and read relevant sections. For the decisive target mismatch, retrieved the **actual pinned Espressif header** using `gh-axi`.
3. Synthesized a scope-adaptable report outline, parameter/evidence checklist, measurement protocols/matrix, traceability templates and prioritized gaps. No numeric experimental outcomes were generated.
4. Reviewed the complete report against source claims and current code, especially variant distinctions, calibration conditions, measurement boundaries and simulation labeling. Checked all selected source fingerprints against retrieved bytes, source-register completeness, Markdown fence balance and the absence of tracked project changes; these are document checks, not firmware or physical tests.

### Commands and observed outcomes

```text
pwd
  [disposable PodlePianoDSP32 worktree]

git status --short                         # initially clean

git rev-parse HEAD
  28a68dba91b650da836af7b215bdd03c77ec0c7a

git log -1 --format='%h %s'
  28a68db Merge pull request #5 from podledges/fm/pianodsp32-register-explainer-skill

find docs -maxdepth 2 -type f
find current/src/ESP_piano -maxdepth 3 -type f
find data current/src/fixtures -type f
  data/README.md
  current/src/fixtures/cmaj_chord.wav
  current/src/fixtures/cmaj_chord.mid
  current/src/fixtures/project_tree.txt

find current/src/ESP_piano -name '*sdkconfig*' -o -name 'dependencies.lock'
  no results

rg -n 'TARGET|TYPE1|type1|frame_samples|mean|sample_freq' \
  current/src/ESP_piano/components/capture_hal/capture_adc.c
  114: .format = ADC_DIGI_OUTPUT_FORMAT_TYPE1,
  206: sum += sample->type1.data;
  209: const int32_t mean = (int32_t)(sum / (int64_t)n_samples);
  212: const int32_t centered = (int32_t)sample->type1.data - mean;

rg -n 'TL072|MCP6002|GPIO_34|1N4007|1N5817' \
  current/KiCad/firstTime/firstTime.kicad_sch
  confirmed source/value/net inconsistencies summarized in L11

rg -n 'transcriber|basic_pitch|fake|onsets' current/src/server/app.py
  CLI choices=('fake', 'basic_pitch'), default='fake'; fallback present

python .research/fetch_sources.py
  direct urllib HTTP retrieval to worktree scratch; HTMLParser text extraction;
  PDF extraction via pdftotext -layout; per-source URL/redirect/size/SHA-256 log
  403 / redirect-only sources excluded as documented above

gh-axi api '/repos/espressif/esp-idf/contents/components/hal/include/hal/adc_types.h?ref=v5.4.2' \
  --header 'Accept: application/vnd.github.raw+json' --full
  full response body retrieved; S3 branch has type2, no type1
```

An initial attempt to pipe `gh-axi --jq .content` directly through `base64 -d` failed because its response was wrapped/truncated for display. The full raw-body request above succeeded; the body was decoded from the response wrapper in scratch. This is a retrieval-format issue, not a GitHub source/content failure. No browser operation was needed; HTTP retrieval was not automated GUI browsing. No firmware/test/hardware commands embedded in historical docs were executed.

### Selected immutable source fingerprints

These identify bytes actually retrieved; they are not checksums of project measurement data. The citations, findings and fingerprints are preserved here; retrieved source copies used during the investigation were temporary.

| Source | Retrieved bytes | SHA-256 |
|---|---:|---|
| R1 UKZN PDF | 512692 | `8e328e583f684fdd9d225f197e804547fe679c7f37c21537dd3249bc7a1ea2cf` |
| R6 S3 datasheet PDF v2.2 | 1098115 | `2d5a7cb7fd559d8d972bd88db32669c0196d23f22d7afaafb0f63d099b589a3f` |
| R7 S3 TRM PDF v1.8 | 15215232 | `4484bf8a69035ec42a731c58c64ada6fbd1f1618c5559409f134d9ea083f444f` |
| R8 S3 ADC HTML v5.4.2 | 105596 | `0ead5632cedeb6eefcaa68d85b9c57bb62fcca8ed4590d92ed53d7d8156c72aa` |
| R10 ADC header v5.4.2 | 10828 | `aac350a80a9c5c8bc9e7fe5b42d701865b2ad259a7fdc0f5622159f59769aa40` |
| R3 TI SLOA033A PDF | 60284 | `b07c5dd9fd68f17210d83fd72b2b00526ef96feed56fbeeb4fdaea7b907ffffc` |
| R5 TE DT PDF Rev A2 | 123075 | `5376219be08272fd08e50689530be001ce52efff719a66aa3b591e3a921a9c8c` |
| R18 Dixon PDF | 156118 | `307a8c18d34baa290498019d2a013803371472e6153e3419d1fe4c5ab07c8eac` |
| R19 O&F PDF | 357053 | `d8a512b1f0f64da8735f3c9c727f43fa91f9af39b88a7ea38d9c19f8822cd0ad` |
| R20 Basic Pitch PDF | 534859 | `63040c77ce170c4c353f287ee5b777a57615098d799e998ec618a4f5de7d5b36` |
| R21 NIST PDF | 435960 | `f2c8e6026d5589a63d492f192b72cd905f554b477a6049532256170aec477e92` |

### Original investigation completion

The source investigation reported no unresolved project-owner decision. Its recommendations for future engineering work were not approvals of experiments or engineering targets. Task-runner lifecycle commands and private fleet paths have been omitted from this public copy.

## Final recommendation

Write the UREX document as an **evidence-linked implementation/status report**, centered on the actual piezo-to-output chain. First resolve hardware/ADC identity and electrical safety, then obtain a small matched raw-data/ground-truth/timing bundle. A clear description of source, limitations, failed tests and unmeasured hypotheses is substantially stronger than a polished claim of low-latency, high-accuracy piano transcription without reproducible evidence.
