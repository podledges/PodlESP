---
title: "Retained source record: broad Grok piano research"
report_date: "2026-09-17"
access_date: "2026-09-17"
status: "Sanitized curated record; patent, definition and cost corrections applied"
---

# Broad Grok source record

[Canonical synthesis](../README.md) | [Broad evidence](../broad-evidence.md) | [Sources](../sources.md)

Original: **“MCU / embedded acoustic piano transcription (second pass)”**,
independent scout `piano-broad-grok`. Original preserved separately; this public
record curates evidence and explicitly corrects overstatements rather than
publishing them as facts. No private paths or operational logs are reproduced.

Original report SHA-256:
`12fe29e975b6ee59f8b5f9eb3915fc9358feb194139be086eef8762bfcfcfb33`.

## Method and independence

Earlier reports were read to avoid a bibliography rerun, without sibling broad
report consultation or contact before delivery. General web, multilingual,
Chinese technical articles/contests, patents, sibling Cornell projects,
commercial products, FPGA abstracts, theses and Bela/NIME were explored.
Primary PDFs/HTML and Semantic Scholar abstracts supplied evidence; no downloaded
implementation was executed and no hardware was accessed.

Query families included STM32/ESP32/RP2040/Teensy transcription, 嵌入式 钢琴
音符识别, DSP portable analyzer, ピアノ 自動採譜 マイコン, multilingual
embedded-piano terms, Zynq AMT, patents and audio-to-MIDI hardware. Search hits
for synthesis, visualizers or touch keyboards were not accepted as transcription.

## New evidence retained

| Family / primary link | Positive finding | Limit |
|---|---|---|
| [Cornell Chord Identifier](https://ece4760.github.io/Projects/Fall2022/ah677_jjn48_tlc234/index.html), [author article](https://circuitcellar.com/research-design-hub/projects/identifying-musical-chords/) | RP2040 @48 MHz, air mic/LPF, 2048-point FFT at 5 kHz, top-three peak triad labeling; qualitative sine-chord success around 100 BPM | ~0.6 s hold, not E2E; struck piano/guitar timbres difficult; no event stream, F1, memory high-water or complete priced system |
| [Zhai/Wang/Du AET 2009](http://www.chinaaet.com/article/13611) | TMS320VC5502 DSP + ARM S3C44B0X, CS53L21 mic input, pitch/duration to MIDI/staff; 57/60 notes, duration errors 13.5 ms mean / 25.6 ms max | Count ratio not full matched-event recall; synth A440 example, 60-note instrument unclear; no dense acoustic-piano polyphony or E2E |
| [Casio US5202528A](https://patents.google.com/patent/US5202528A/en) | 1993 patent discloses DSP filter-bank simultaneous-note architecture | **Not proof of built hardware or productization.** Runtime performance, memory and cost unknown |
| [Zynq ISVLSI 2019](https://doi.org/10.1109/ISVLSI.2019.00075), [ISMCR 2019](https://doi.org/10.1109/ISMCR47492.2019.8955662) | Abstracts: FPGA PL capture, ARM PS DFT/PCP/matching, smartphone chord display; ISMCR says 90% open chords and ~250 ms sampling latency | Full text not recovered; not MCU or piano event F1; separate papers' metrics must not be silently merged |
| [Wu/Fong/Yang/Zeng AIIoT 2025](https://doi.org/10.1109/AIIoT65859.2025.11105340) | Abstract: FPGA cloud chord service, 680 ms versus Python 2.5 s | Workload/timing boundaries incomplete; not MCU; open-code claim not artifact-verified |
| [Zammit/Cutajar 2025](https://doi.org/10.5604/01.3001.0055.2099) | Abstract retrieved via Semantic Scholar, STM32F407/CMSIS FFT/electret, generated pitches and piano, note/beat/duration given time signature | Full paper unavailable; no numeric accuracy, latency, memory or verified polyphony status |
| [NIME Bela pipeline 2023](https://nime.org/proceedings/2023/nime2023_22.pdf) | Piezo-capable capture and embedded neural tooling | Linux SBC/PRU, not MCU piano AMT |
| [Scorpiano 2021](https://arxiv.org/abs/2108.10689) | Monophonic piano-file DSP to score | Desktop/file workflow, not embedded polyphony |

Wrong-task screens retained: STM32 cp33 is audio processing/display, not
transcription; ESP32 “piano” examples often synthesize or sense touch. Monophonic
pedals, PC/phone/cloud transcription apps and key/hammer MIDI systems do not
establish general acoustic-piano inference on MCU. A “Melody Walker” contest
hardware page without released code was insufficient evidence.

## Explicit editorial corrections

1. Original Casio wording called the patent proof of productization. **Superseded:**
   a patent documents disclosure/claims, not manufacture or sale. Separate product
   evidence would be needed; none is supplied here.
2. Original device-family cost bands lacked exact priced objects/dates/links.
   They are omitted as quotes. Full system costs are unknown unless a specific
   documented estimate is identified, with exclusions. See [cost boundaries](../broad-evidence.md#commercial-and-contact-sensing-exclusions).
3. The original report varied whether “full” AMT required offsets/velocity and
   mir_eval-class testing. Canonical scoring separates pitch, onset, offset,
   velocity and pedal. No particular dataset or expressive output is required
   merely to acknowledge a genuine polyphonic pitch/onset result.
4. Cornell's tests include **simulated instrument sounds**. Its piano-timbre
   failure is useful, not a controlled acoustic-piano benchmark. Synthesis
   independently re-read the course report and article; no code/demo execution.
5. Zhai's 57/60 is a reported detected-note count, not a verified precision/recall
   protocol; missing false-positive matching remains explicit. Synthesis re-read
   the Chinese article, retaining its segmentation-before-pitch boundary.

## Access limits and proposals

Full texts for Zammit and the IEEE FPGA papers were not recovered; Semantic
Scholar abstracts are not full implementation audits. Fong's thesis and some
maker/thesis sites returned 403; another thesis timed out. No paywall bypass,
video-derived measurement, paid browser session or downloaded-code execution.
No controlled MCU piano contact-versus-air benchmark was located.

Future proposals: compare sine and piano triads as a calibrated narrow baseline,
retain monophonic held-out tests, use a host-side piano reference, separately
score key sensing, and require electrical review before paired piezo recordings.
The additional M7 result comes from the sibling's later accepted record, not
from this independent discovery pass.
