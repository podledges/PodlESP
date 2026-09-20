---
title: "Beyond neural piano papers: MCU multipitch and near-misses"
report_date: "2026-09-17"
access_date: "2026-09-17"
status: "Four-report synthesis; author claims, not local replication"
---

# MCU multipitch exists; general acoustic-piano transcription remains unverified

[Overview](README.md) | [Earlier evidence](evidence.md) |
[Sensors](piezo-and-adc.md) | [Experiments](experiments.md) | [Sources](sources.md)

The broader independent searches add **two positive MCU multipitch cases**:
a Cortex-M7 two-note violin demonstration and an RP2040 triad identifier.
Neither establishes general polyphonic acoustic-piano pitch/onset transcription.
That narrower gap is not an impossibility result, nor does it require velocity,
pedal, a particular F1 threshold or a particular dataset to count as transcription.

All measurements below belong to the source authors. **Unknown** means not
established in the inspected evidence, not zero. A proposed architecture, source
implementation, author demonstration and independent replication are distinct.
None of these systems was executed or independently replicated for this vault.

## What is genuinely new?

| Contribution | New source family | What changes |
|---|---|---|
| Broad Astra | ITESO M7, NIME Pi3, 2010 NMF, Pianolizer code | Positive restricted MCU multipitch; non-neural alternatives; stronger latency and export-boundary distinctions |
| Broad Grok | Cornell Chord Identifier, Chinese C55x analyzer, Casio, additional FPGA abstracts | Another MCU multipitch case; older DSP note/duration work; historical proposals, not proof of shipment |
| Both broad passes | FPGA, commercial and contact-sensor near-misses | Broader coverage, not two independent hardware validations |
| Earlier Astra / Grok | Huang, Cornell transcriber, modern neural models, ADC/sensor caveats | Retained in [earlier evidence](evidence.md), not replaced by this pass |

The [four sanitized source records](README.md#research-provenance-and-reconciled-findings)
retain each scout's contribution and access limits. This is synthesis, not a
third search campaign. Selected primary documents were cross-checked during synthesis.

## Devices, tasks and sensing

| System / date | Runtime hardware / class | Method and instrument | Input / contact evidence | Observed or disclosed output |
|---|---|---|---|---|
| Navarro Hernández, Mercado Fong, Pardiñas Mir, ITESO, Aug 2022 [S22](sources.md#s22) | MIMXRT1010-EVK, MIMXRT1011 Cortex-M7, 500 MHz; **MCU** | CMSIS floating-point FFT, peak/pitch lookup, E4-D6; **violin** | Onboard air mic, WM8960, SAI/I2S/DMA; no piezo experiment | Author example: simultaneous A4/F5; beat-aggregated console notes/durations; three slots designed, not three-note piano validation |
| Haghighi, Nan, Chou, Cornell, Fall 2022 / article 2024 [S23](sources.md#s23) | Pico RP2040 at 48 MHz; **MCU** | Top-three FFT peaks, neighbor suppression, interval/root table; major/minor/augmented/diminished triads | Electret air mic, approximately 1.2 kHz Sallen-Key LPF, ADC/DMA; synth/simulated instrument sounds, no contact test | Chord name on VGA; three frequencies/note names on serial. Good on sine triads; struck piano/guitar timbres difficult |
| Dessein, Cont, Lemaitre, ISMIR 2010 [S24](sources.md#s24) | MATLAB, 2.40 GHz laptop; **PC** | Fixed 88-note templates, beta-divergence NMF, threshold/pruning; MAPS piano and sampled-piano examples | Recorded audio; no established contact condition | Polyphonic piano note events, separately scored onsets and offsets |
| Schramm, Visi, Brasil, Johann, NIME 2018 [S25](sources.md#s25) | Pi3 Model B, BCM2837, Raspbian, GPU FFT, USB audio; **Linux SBC** | Instrument-specific CQT/PLCA, median/hysteresis, resynthesis; guitars/glasses, failed Arco-Barco | Contact pickups within intended class; condenser mic for glasses; no piano piezo/air A/B | Polyphonic instrument augmentation; explicitly not optimized for accurate audio-to-MIDI |
| Pusep, Pianolizer, repository from 2021 / demo 2022 [S26](sources.md#s26) | Browser/WASM, desktop C++, Raspberry Pi Linux, model unspecified | Sliding DFT note-energy visualization; distinct Perl MIDI export | ReSpeaker Pi HAT example; no controlled contact-piano benchmark | Live analysis/display; **whole-file MIDI exporter**; Arduino only drives LEDs |
| Zhai / Wang / Du, AET 2009 [S27](sources.md#s27) | TMS320VC5502 + S3C44B0X; **DSP + ARM** | Energy-based segmentation, 4096-point FFT pitch pick; synth A440 piano tone and rhythmic 60-note signal | CS53L21 mic input; no piezo test; 60-note instrument not fully specified | One pitch per segmented note, duration, stored MIDI, synth playback/staff LCD |
| Zammit / Cutajar, 2025 [S11](sources.md#s11) | STM32F407; **MCU**, abstract only | CMSIS FFT/peak picking; generated pitches and actual piano | Electret air mic; contact unknown | Note/beat, duration given time signature; polyphony unknown, not verified as monophonic or polyphonic |

## Latency, accuracy, memory and cost must stay paired

| System | Accuracy / test evidence | Timing boundary | Memory / storage | Complete system cost |
|---|---|---|---|---|
| ITESO M7 | Figure 8 two violin notes; no trial count, corpus, precision/recall/F1 | 492,675 cycles / 500 MHz = **0.98535 ms task compute**; **512 / 8000 = 64 ms blocks**, then beat aggregation; E2E unknown | 128 KB chip RAM capacity, **used RAM unknown**; board guide: 128 **Mbit** = 16 MB flash, not thesis's 128 MB | Unknown |
| Cornell Chord ID | Qualitative sine-triad success up to 100 BPM; piano/guitar timbre failures; no note-event F1 | **2048 / 5000 = 409.6 ms** audio block; approximately **0.6 s chord hold** test, not measured response percentile; serial thread every second, distinct from VGA | Peak RAM, firmware storage unknown | Unknown; historical Pico board price is not its full BOM |
| NMF 2010 | 25 MAPS excerpts × 30 s: frame F 65.5%, onset F 71.1%, onset+offset F 28.2% | 50 ms window, 10 ms hop; subjective-example simulation about 3x real-time; E2E unknown | 4 GB **installed laptop RAM**, not measured use; peak memory unknown | Unknown |
| NIME Pi3 | Three guitarists/two guitars; glasses success; Arco-Barco failure; no F1 by design | Approx. **45/70 ms audio-input to resynthesized-output** at 512/1024 hops; 256-hop case required laptop; no percentile distribution | 1 GB board RAM capacity; peak application RAM unknown | Unknown |
| Pianolizer | Source and examples, no piano event benchmark | 256-sample output cadence ~5.8 ms at 44.1 kHz, not MIDI latency; default 40 ms smoothing; exporter waits for complete analysis | Header documents 64 KB default ring buffer, not total RAM; C2 history 11,462 samples (~260 ms spectral support), not fixed delay | Unknown |
| Zhai DSP+ARM | **57/60 detected**, authors call 95%; all 57 pitch labels claimed correct; duration mean absolute error **13.5 ms**, max **25.6 ms** | 128/12000 = 10.67 ms energy frame, 64-sample overlap; five-frame threshold persistence; pitch follows detected note boundaries; E2E unknown | Article: DSP 32K × 16-bit on-chip RAM, 8 KB FFT allocation, no external DSP RAM needed; full-system high-water use unknown | Unknown |
| Zammit STM32 | Abstract says “good results”; no numeric score/protocol recovered | “Real-time” claim; window, compute and E2E unknown | Unknown | Unknown |

The Zhai 57/60 ratio is a **note-count result**, not independently matched
precision/recall: no complete false-positive or timing-matching protocol is given.
Its A440 example is synthesized, not evidence of a live acoustic piano deployment.

## Output coverage, without moving the goalposts

**A note-transcription result can report pitch and onset without offset,
velocity or pedal.** Score these outputs independently. A missing velocity
head must not erase a genuine polyphonic onset result. Conversely, a chord
label or instantaneous pitch list does not establish separate note attacks.

| System | Concurrent pitches | Onset / re-onset | Offset / duration | Velocity | Pedal |
|---|---|---|---|---|---|
| ITESO M7 | Two violin notes demonstrated | Beat aggregation; event errors unknown | Beat-count duration, not scored release timing | Not demonstrated | Not demonstrated |
| Cornell Chord ID | Three peak-derived notes / triad name | Not implemented as event stream | Timing/length left as future work | Not implemented | Not implemented |
| NMF 2010 | Piano polyphony scored | Onset F 71.1%; restrike-specific score unknown | Joint onset+offset F 28.2% | Not scored | Not scored |
| NIME Pi3 | Instrument-specific polyphony demonstrated | Activity drives resynthesis; no event F1 | Activity-driven, no offset benchmark | Not scored | Not scored |
| Pianolizer exporter | Multiple per-note activity tracks | Zero/nonzero transitions; no distinct restrike without a zero | Offline thresholded start/end events | Whole-note amplitude + global normalization, not calibrated key velocity | No decoder established |
| Huang S3, retained [S1](sources.md#s1) | Isolated clips only | Segmentation, not scored onset timing | Not scored | Not scored | Not scored |
| Mobile-AMT, retained [S6](sources.md#s6) | Piano polyphony scored | Onset F 96.30% | Joint +offset F 76.80% | Joint +offset+velocity F 75.53% | Not established by these scores |

## Why sub-millisecond computation is not sub-millisecond transcription

```text
M7 microphone -> 64 ms blocks -> 0.985 ms measured task -> beat aggregation
                                                       -> serial console
                 <--------- full response not measured ---------------->

Pianolizer audio -> sliding spectral state -> frequent analysis output
                                            |
                                  collect whole-file output
                                            |
                           note averages + global velocity scaling -> MIDI file

Neither a task timer nor frequent analysis output measures live MIDI response.
```

M7 timing was measured with debugger breakpoints around a recognition task.
Do not add 64 + 0.98 and label it universal total latency: block alignment,
beat aggregation and output waiting remain unknown. Three output slots and a
major-triad MATLAB prototype do not establish three-note acoustic-piano success.

Pianolizer's exporter buffers complete analysis at lines 280-284; note averages
at 128-175 and global scaling at 235-247 introduce future dependence. A causal
sliding filter may react before its complete history is replaced, so its C2
history length is also not a fixed response-time claim. [S26](sources.md#s26)

The NMF and PLCA sources make **non-neural instrument-specific templates** worth
including in future baselines, not automatically portable to an MCU. Keep the
original ISMIR NMF paper separate from its differently tuned MIREX abstract.

## Patents, FPGA and proposals: retain the ideas, not invented deployments

| Source / date | What the evidence actually supports | Missing / disallowed inference |
|---|---|---|
| Casio US5202528A, filed 1991, granted 1993 [S28](sources.md#s28) | Disclosed DSP+CPU mic/line bandpass-bank multipitch architecture; envelope detection and channel allocation; example four voices | **Patent is not proof of build, productization or shipment.** Piano benchmark, runtime memory, latency and cost unknown |
| Jung / Amusetec US6856923B2, granted 2005 [S29](sources.md#s29) | Piano template/subtraction and score-informed proposals; Young Chang grand recordings analyzed on Sony Windows notebook; dynamics/pedal ideas | Not MCU deployment. 5 ms hop and ~2 ms timestamp-localization example are not E2E delay; productization, complete RAM/cost and scored outputs unknown |
| Vaca et al., ISVLSI + ISMCR 2019 [S30](sources.md#s30) | Abstracts: Zynq-7000 FPGA PL microphone capture, ARM PS DFT/PCP/pattern matching, chord display on phone; ISMCR reports **90% open-chord accuracy**, **~250 ms sampling latency** | Full papers unavailable to scouts. Not bare MCU or piano note F1; instrument, full protocol, memory, cost and full response unknown. Do not attribute ISMCR's numbers to ISVLSI alone |
| Wu / Fong / Yang / Zeng, AIIoT 2025 [S31](sources.md#s31) | Abstract: FPGA web service for chord sequences, **680 ms vs 2.5 s Python**; open-source claim | Cloud service, not on-device MCU; request/workload boundaries, device memory/cost and accuracy unknown; code claim not artifact-verified |
| GUT-9, 2023 competition [S32](sources.md#s32) | Two ESP32 design, exact variant unknown; released first-board dominant-frequency FFT, 2048 samples at requested 10 kHz (204.8 ms nominal capture); **struck water cups** | Main-control-board source absent; no independently scored classifier or piano polyphony; used RAM, total cost and measured E2E unknown |
| Park / Singhal / Suresh, Illinois, 2026-02-27 [S33](sources.md#s33) | STM32F446RET6 **design**, one audio note at a time; microphone FFT plus separate MIDI-input path; ≥90%/≤200 ms high-level targets | Not final measurements; inconsistent 50 ms section targets and FFT-only estimates cannot validate full path; memory unknown |

## Commercial and contact-sensing exclusions

| Source | Sensing / runtime / task | Evidence and cost boundary |
|---|---|---|
| Sonuus G2M V3, introduced 2016 [S34](sources.md#s34) | Analog guitar/bass/voice to MIDI, physical **monophonic** box; chip undisclosed; no controlled piano/contact test | Manufacturer price **USD 99.99**, observed 2026-09-17, box only; numeric E2E, RAM and piano accuracy unknown |
| Algoriffix Transkr V4 [S34](sources.md#s34) | Advertised polyphonic piano/audio transcription, **Windows/macOS** app/plugin; audio interface, not MCU | Regular **USD 129** software license, observed 2026-09-17; host/interface/mic excluded; accuracy, RAM and numeric E2E unknown |
| Cycfi eight-input converter proposal [S35](sources.md#s35) | Divided/piezo pickup audio pitch tracking, not key sensing; target processor unspecified | Inspected repository contains README/license/image, no converter firmware. Built system, performance, memory and cost unknown |
| Jones dulcimer, 2017/2018 [S35](sources.md#s35) | Fixed-note string piezo triggers and Livid Brain V2 integration; not mixed-piano audio inference | Maker reports stalled integration; no successful device accuracy, latency, RAM or complete cost |
| Bela NIME pipeline, 2023 [S36](sources.md#s36) | Linux/PRU embedded neural tooling, piezo-capable dataset capture | Not piano transcription benchmark; complete piano-system cost/accuracy/memory/latency unknown |
| Scorpiano 2021; Union capstone 2019/2020 [S36](sources.md#s36) | Desktop monophonic piano files; respectively Linux Pi4 electric-guitar analysis | Wrong runtime/task for MCU piano. Union has conflicting dates/aggregates; not used as comparative accuracy or cost anchor |

**Illinois's USD 95.70** is a proposed raw-parts total dated 2026-02-27,
not a validated transcriber price; its document separately budgets labor.
Unlinked device-family price bands in the broad Grok report are **not adopted**.
Other system costs remain unknown. Earlier [item-specific cost anchors](evidence.md#hardware-costs)
remain dated observations, never interchangeable system prices.
All quotes exclude whatever is not explicitly included: host, instrument,
power, cabling, installation, enclosure, analog conditioning, tax/shipping,
calibration, labeled recordings and engineering/evaluation work.

```text
Shared soundboard piezo -> mixed vibration -> pitch/event inference
Divided string pickup  -> per-string audio -> pitch tracking
Known-pitch piezo zone -> activity trigger -> assigned note
Optical/key sensor    -> mechanism motion -> MIDI

A piano roll alone cannot tell which problem was solved.
```

No controlled MCU acoustic-piano contact-versus-air transcription comparison
was found across the four reports. Preserve sensor transfer and electrical
sign-off as open evidence needs, not assumptions or hardware authorization.
