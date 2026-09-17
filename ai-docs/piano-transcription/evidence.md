---
title: "Piano transcription evidence and comparisons"
report_date: "2026-09-17"
status: "Author-reported results, not locally reproduced"
---

# Piano transcription evidence and comparisons

[Overview](README.md) | [Sensors](piezo-and-adc.md) |
[Experiments](experiments.md) | [Sources](sources.md)

## Read the metrics before the rankings

- **Classification accuracy** is correct labels divided by isolated examples.
  It is not a polyphonic note-event score or a false-trigger rate in silence.
- **Frame/multipitch detection** identifies active pitches. **Note events**
  additionally need separate attacks and releases; repeated notes can occur
  without an intervening silent frame. Velocity and pedal are separate tasks.
- **Note F1** is the harmonic mean of precision (matched predictions / all
  predictions) and recall (matched references / all references). Standard
  `mir_eval` defaults use **50 cents pitch tolerance and 50 ms onset tolerance**.
  Including offsets adds the larger of 50 ms or 20% of reference duration.
  Velocity matching normally normalizes reference values and fits a global
  linear rescaling of estimates before a 0.1 tolerance. This does not guarantee
  absolute MIDI-velocity calibration. [S8](sources.md#s8)
- **Hop** is the spacing of feature frames, **lookahead** is future audio needed,
  **compute time** is execution time, and **RTF** is compute time / audio duration.
  RTF below one means throughput can keep up, not that a user gets a quick answer.
  Measured end-to-end latency includes acquisition, buffering, processing,
  decoding and output. Correct backdated timestamps can arrive very late.
- **MAESTRO** contains acoustic Disklavier grand-piano audio with captured MIDI
  labels aligned to about 3 ms. It is not simply synthetic piano audio. Pedal
  means key release, damper action and audible note end differ. Versions and
  evaluation splits matter. [S9](sources.md#s9)

## What runs where

Numbers are primary authors' reported results, not independent replications by
this project. Each row's task and timing definition limit the comparison.

| System / method | Execution, sensor and instrument | Outputs and mode | Accuracy and timing evidence |
|---|---|---|---|
| Huang, SNet1D, 2025: onset segmentation, MFCC, distilled small CNN | **ESP32-S3**; onboard microphone, piano single notes; PC training | One of 88 pitch classes; live 512 ms segments; **monophonic** | 99.6% on 1,000 live notes; 217.8 ms mean preprocessing + classification **after collection**; no event F1 or measured total latency. [S1](sources.md#s1) |
| Schiff, Lashin, Tio, Cornell, 2022: fixed-point FFT peaks, thresholds, nearest-note lookup, debounce | **RP2040 Pico**, MAX4466 electret air mic; recorder/flute/pure tones | Internal on/off events during capture; `.MID` file transferred to PC after STOP; polyphony unvalidated | Qualitative success, no numeric accuracy or total-latency table. Piano ML unfinished; piano spectra problematic. [S2](sources.md#s2) |
| Jeong, 2020: autoregressive multi-state CNN/LSTM | **2018 MacBook Pro**, 2.3 GHz quad-core i5; microphone piano input | Polyphonic states including re-onset; online MIDI and browser display | Mean update compute <12 ms per 32 ms hop; 320 ms audio context. Demo paper does not give its own full accuracy table or measured sound-to-output latency. [S19](sources.md#s19) |
| Kwon, Jeong, Nam, PARcompact, 2024: CNN-FiLM and shared pitchwise LSTMs | PyTorch research evaluation; recorded piano, **no measured MCU deployment** | Polyphonic note states; bounded lookahead supports online design | At 160 ms context latency: onset F1 94.33%, with-offset 78.25%; roughly 2.7M parameters. See paired rows below. [S5](sources.md#s5) |
| Fernández, Onsets & Velocities, 2023: log-mel plus time derivative, CNN | **Desktop PyTorch**; recordings or laptop air mic about 2 m from piano | Polyphonic onset + velocity; **no offset/pedal**; live blocks | MAESTRO v3 onset F1 96.78%, onset+velocity 94.50%; <2 s compute for 120 s audio on eight-core i7-11800H. Paper discusses >9 s context latency and a 4 s workshop configuration. [S4](sources.md#s4) |
| Kusaka and Maezawa, Mobile-AMT, 2024: MobileNet-style CNNs, unidirectional GRUs | **MacBook, iPad, Pixel 6**; acoustic/digital piano recordings, air-mic domain | Polyphonic onset/offset/velocity; authors describe frame-by-frame inference | MAESTRO v3 F1: onset 96.30%, +offset 76.80%, +offset+velocity 75.53%; 174 ms formula, **not measured total delay**; RTF 0.25 / 0.35 / 0.6. [S6](sources.md#s6) |
| Wei, Zhao, Wu, Yoshii, streaming Seq2Seq, 2025: CQT, CNN encoder, separate transformer decoders with pedal | Research evaluation, **no MCU deployment timing**; piano recordings | Polyphonic onset/offset and sustain-aware decoding; streaming architecture | MAESTRO v3 test onset F1 96.52%, with-duration 89.44%; 16M parameters; **380 ms future context excluding computation**. [S20](sources.md#s20) |
| Hu, Peter, Schlüter, Widmer, Causal-AMT, 2025: causal CNNs, shifted asymmetric windows, binary targets | Research evaluation, **hardware timing left to future work**; piano recordings | Polyphonic onset/offset research model; causal processing | Final table at 30 ms onset tolerance: onset F1 37.38 ± 7.85%, with-offset 10.37 ± 4.42%; not directly comparable to 50 ms scores. [S7](sources.md#s7) |
| Bittner et al., NMP / Basic Pitch, 2022: harmonic CQT, small CNN, note postprocessing | **Desktop benchmark**, multi-instrument recorded audio; later TFLite/ONNX/CoreML artifacts | Polyphonic notes/multipitch; file workflow, not proven causal MCU stream | Original MAESTRO onset F1 70.9%, with-offset 10.5%; 465 s Slakh file processed in 24 s, 951 MB peak process RAM. [S3](sources.md#s3) |

No demo or aggregate dataset score proves all 88 keys, all chord combinations,
all pianos or all sensor placements. Acoustic piano, digital piano line output,
contact pickup, voice and percussion are not interchangeable test conditions.

## Huang: the positive MCU result, with its limits

[S1](sources.md#s1), Tables 1-3 and Figure 6, is the closest match to the MCU
question. Short-time energy and zero-crossing rate locate candidate attacks.
Each 8,192-sample frame at 16 kHz lasts **512 ms**. MFCCs use a 2,048-sample
window and 512-sample hop to produce 128 × 13 features. The distilled student
has one 1D convolution and two fully connected layers, about 127,000 parameters.
Deployment folds batch normalization into convolution, reuses activation
buffers and uses DSP/vector instructions.

| Test | Conditions | Reported classification accuracy |
|---|---|---:|
| NSynth keyboard subset | Piano/electronic-keyboard sounds; 48,297 train / 2,072 validation / 658 test | 98.48% distilled student |
| Author microphone dataset | 48 pianos, all 88 isolated notes; 30,380 / 10,126 / 10,128 examples | 99.66% distilled versus 96.93% undistilled, PC comparison |
| Live ESP32-S3 | 1,000 isolated piano notes; microphone details and per-key distribution insufficiently documented | 99.6% |

The S3 experiment reports **104.1 kB RAM**, **494.72 kB “ROM”**, and **217.8 ms
mean processing per frame including preprocessing**. Figure 6 places that
processing after frame collection. **512 + 217.8 = 729.8 ms** is a derived
sequential budget, not a measured total latency or a guaranteed bound; pre-roll,
overlap and external output timing are insufficiently specified.

Missing: chord tests, onset/offset timing scores, velocity/pedal metrics,
fast-restrike behavior, noise false-trigger rate, worst-case runtime, firmware,
weights, public author dataset and independent replication. The 60/20/20 split
does not establish held-out pianos/sessions. The microphone result is not a
piezo/SAR-ADC result. No complete hardware cost is disclosed.

The paper's “2 MB ROM” / “DSP chip” terminology should not become a chip fact:
Espressif specifies **384 KB mask ROM**, 512 KB SRAM and CPU instruction
extensions. Preserve the paper's storage figure as reported read-only storage,
not proof of writable mask ROM or a separate accelerator. [S12](sources.md#s12)

## PARcompact

Use **Table IV's exact paired latency/accuracy rows**, not the best accuracy
from another experiment combined with the shortest delay. These are model
context latencies, not measured MCU input/output delays. The 16 kHz,
4,096-sample centered STFT alone needs 128 ms of future context; hop is 32 ms.
[S5](sources.md#s5)

| CNN time-filter widths | Context latency | Onset F1 | With-offset F1 |
|---|---:|---:|---:|
| (1,1,1,1,1,1) | 128 ms | 84.25% | 45.18% |
| (3,1,1,1,1,1) | 160 ms | 94.33% | 78.25% |
| (3,1,3,1,1,1) | 192 ms | 95.77% | 81.63% |
| (3,1,3,1,3,1) | 224 ms | 95.58% | 78.64% |
| (3,3,3,3,3,3) | 320 ms | 96.03% | 84.65% |

Parameters vary from 2.54M to 2.68M across these variants. The paper uses
standard note matching (50 ms onset tolerance; offsets within 50 ms or 20%
of duration). These are not five measured device latency percentiles.

The separate size ablation also matters: 653K parameters gives 90.83% onset /
69.08% with-offset F1; 299K gives 81.31% / 16.47%; 50K gives 66.99% / 15.98%.
Small-width training becomes unstable. Compression needs an accuracy test,
not an assumption. Cross-domain scores also fall: full PAR gets 97.0% note F1
on MAESTRO v3 versus 79.9% on MAPS, with annotation and piano mismatch discussed.

## Mobile-AMT: 174 ms remains a qualified claim

The original formula is:

**L = [N/2 + H(r + 2)/2] / sample rate**.

For N = 2,048 samples, H = 320, r = 9 and 16 kHz, it gives **174 ms**. It
accounts for window centering, CNN context and postprocessing. The authors
describe an `r`-frame input buffer and frame-by-frame inference. Actual
single-core ONNX tests measure RTF, not physical end-to-end latency; MacBook
peak RAM is 129 MB, mobile peak RAM is not reported. [S6](sources.md#s6)

Hu et al. argue that squeeze/excitation pooling over time introduces
noncausal dependence on ten-second blocks. That is a substantive **later
architectural critique**, not independent measurement of the original
phone deployment. Its description and the original bounded-buffer description
are unresolved without the deployed graph, pooling axes, state/buffering and
paired online/offline tests. Do not replace “174 ms formula” with “definitely
ten seconds” or silently endorse either as measured total delay. [S7](sources.md#s7)

Real-recording evidence is stronger than a demo: Mobile-AMT tests
IDMT-PIANO-MM, with 432 recordings across nine pieces, eight rooms,
upright/grand/digital pianos and microphone/phone/tablet recordings. Note F1
drops from 96.30% on MAESTRO to 78.84% on IDMT without augmentation. Mixed
training plus timbre, room, noise, microphone and clipping augmentation yields
93.15% (std 4.97) on IDMT. Offset labels there are insufficiently precise, so
only onset-note scores are evaluated. **No contact-piezo condition is established.**

## Low lookahead is not yet high accuracy

Causal-AMT changes targets, decoding, CNN causality and window weighting.
At 16 kHz it retains a **2,048-sample window** but shifts/tapers it to reduce
lookahead to 10 ms; that is not a 10 ms-long audio window. Most ablations use
MAESTRO v3 validation data and reduced training; the final 2,000-epoch comparison
is the paper's exception to validation-only evaluation. [S7](sources.md#s7)

Final onset F1 is 31.55% at 10 ms tolerance and 37.38% at 30 ms; with-offset
F1 is 5.03% and 10.37%. These strict-tolerance results expose a difficult
accuracy/response tradeoff, **not a proof that every future causal method must
fail**. The reported 160 GFLOPs per three seconds after sharing CNN work is an
operation count, not measured MCU timing. Hardware-time analysis is future work.

Wei et al.'s different system uses 19 future frames at a 20 ms hop, giving
380 ms **with computational speed explicitly set aside**. Jeong's earlier
demo reports 320 ms total audio context and <12 ms average compute per update;
context length alone does not identify the physical event's output delay.
Both illustrate why “streaming” and “low-latency” need separate measurements.
[S19](sources.md#s19), [S20](sources.md#s20)

## Basic Pitch and Cornell: two common misreadings

**Basic Pitch:** 16,782 parameters in the original paper do not specify working
memory. A 2017 MacBook Pro with 3.1 GHz quad-core i7 and 16 GB RAM uses 490 MB
peak for 0.35 s white noise, 951 MB for 465 s audio; resampling is outside timing.
These **desktop process** measurements are not a lower bound for an embedded
rewrite. Conversely, a small TFLite file does not prove supported Micro
operators, small activation arena, bounded CQT buffers or causal decoding.
[S3](sources.md#s3)

Inspected source revision uses roughly two-second windows and reverse-time
onset processing plus forward/backward energy tracing. Velocity derives from
mean note-frame activation, not a separately validated key-velocity predictor.
The original paper's scores are not scores for every later Basic Pitch version.

**Cornell:** the MCU really performs FFT/threshold DSP, but the authors say
piano spectra were impractical with the completed approach. They did not finish
the proposed piano ML; the deployed neural tutorial detects fire alarms.
A 1,024-point FFT at 10 kHz spans 102.4 ms and has about 9.77 Hz bin spacing;
these are settings-derived numbers, not measured response latency. Listing
A0-C8 in a lookup does not prove discrimination across that range. MIDI bytes
are stored and sent to a PC after STOP, not a demonstrated live external MIDI
receiver. [S2](sources.md#s2)

## Related results that do not answer the piano question

- **Stefani/Turchet guitar techniques:** Raspberry Pi 4 with 4 GB RAM, Elk
  Audio OS and internal guitar pickups, **not an MCU**. Five guitars/players,
  75/25 stratified random split; 99.1% classification for four percussion
  classes plus one pitched class, but 56.5% for twelve techniques. Approximate
  30.7 ms sums separately measured components; no exact end-to-end benchmark.
  Neither task is piano pitch transcription. [S10](sources.md#s10)
- **Zammit/Cutajar STM32F407:** an abstract describes electret input, CMSIS FFT,
  piano/generated-pitch tests and note/beat detection. Full text was not
  retrieved; quantitative accuracy, latency and polyphony remain unverified.
  Treat as a follow-up lead, not successful piano ML evidence. [S11](sources.md#s11)

## What an S3 feasibility claim still needs

Espressif specifies dual cores up to 240 MHz and 512 KB internal SRAM;
optional flash/PSRAM depends on the package and board. These are not model
throughput or audio-quality measurements. [S12](sources.md#s12)

Huang gives a concrete narrow deployment report. None of the polyphonic
studies supplies the matching S3 **RAM + storage + full DSP/inference timing +
accuracy + end-to-end latency** evidence. Quantizing 2.7M weights to int8 would
still take roughly 2.7 MB before activations/state, but that arithmetic alone
neither proves nor disproves a suitable flash/PSRAM-based port. Record all
memory classes, operator support, contention and sustained backlog on the
identified board. The lab board's advertised memory is not yet physically
confirmed. [S21](sources.md#s21)

## Hardware costs

USD observed **2026-09-17**, except the explicitly historical launch price.
These are parts, not validated system BOMs. [S15-S18](sources.md#s15)

| Item | Price and source | Exclusions / limits |
|---|---:|---|
| ESP32-S3 Feather 5477, 4 MB flash / 2 MB PSRAM | $17.50, Adafruit | Not identified as Huang's board or the PodlESP LCD board |
| MAX4466 electret microphone board 1063 | $6.95, Adafruit | No MCU, wiring or validated acquisition design |
| Enclosed piezo element 1739 | $0.95, Adafruit | Resonant raw element, not a calibrated piano pickup or protected high-impedance frontend |
| Raspberry Pi Pico | $4, manufacturer launch 2021-01-21 | Historical board-only price, not a current complete Cornell BOM |
| Huang deployment; PC/mobile hosts | Not disclosed in cited papers | Host hardware cannot be priced as an MCU board |
| Complete PodlESP piezo/parallel-frontend system | Not established | Requires identified hardware and approved circuit/BOM |

Feather + air-mic board is a **$24.45 subtotal**; Feather + bare piezo is
**$18.45 before the necessary frontend**. Neither buys a working transcriber.
All exclude tax, shipping, duties, power/cables, enclosure, assembly,
calibration, instruments, piano, labeled data, training and engineering labor.
Ambiguous multi-SKU price bands and stock-dependent used-equipment prices from
the scout leads are not used as equivalent complete-system quotes.
