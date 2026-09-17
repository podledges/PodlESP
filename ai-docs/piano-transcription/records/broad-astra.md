---
title: "Retained source record: broad Astra piano research"
report_date: "2026-09-17"
access_date: "2026-09-17"
status: "Sanitized curated record; source inspection, not execution"
---

# Broad Astra source record

[Canonical synthesis](../README.md) | [Broad evidence](../broad-evidence.md) | [Sources](../sources.md)

Original: **“Beyond the first pass: MCU piano transcription and its strongest
near-misses”**, independent scout `piano-broad-astra`. Original report and scratch
files are preserved separately. Private paths, lifecycle commands and tool logs
are excluded; public evidence, access limits and provenance remain.

Original report SHA-256:
`243290d0eacd9242b9c893f832fd4af0848d7cadc7bf515b0f4a9d0bb8522dea`.

## Method and independence

Read earlier reports only to identify covered families. Did not read/contact
the sibling broad scout before delivery or launch another scout. Searched general
web, exact scholarly titles, institutional repositories, citation chains, maker
source trees, patents and commercial pages. English, Chinese, Japanese, Spanish,
German and French query families broadened the discovery surface.

Examples: “polyphonic transcription microcontroller,” “Cortex-M7 pitch,”
“piano audio to MIDI hardware standalone,” “辨音识键奏乐系统,”
“ピアノ 採譜 マイコン,” and contact/piezo/patent combinations. ITESO led to
NIME, whose references led to the older NMF family. This was not an exhaustive
live Google Scholar citation-index sweep; citation counts were not quality evidence.

## New evidence retained

| Family / primary link | Finding | Limit |
|---|---|---|
| [ITESO 2022 report](https://rei.iteso.mx/bitstreams/90fcf30b-caea-4dcf-be12-31c66ac10260/download) | MIMXRT1010-EVK/MIMXRT1011 M7, 500 MHz, mic/WM8960; two violin notes A4/F5; 492,675 cycles task compute after 512/8 kHz = 64 ms blocks | E4-D6, beat aggregation, no piano corpus or scored note events; used RAM/total cost/E2E unknown |
| [NXP board guide](https://www.farnell.com/datasheets/2860193.pdf) | 128 Mbit = 16 MB flash, not thesis's 128 MB; onboard mic/codec | Manufacturer guide via indexed text; direct download timed out, no claimed local PDF hash |
| [NIME 2018](https://www.nime.org/proceedings/2018/nime2018_paper0027.pdf) | Pi3 **Linux** CQT/PLCA/resynthesis; approximate 45/70 ms input-output delay; guitars/glasses | 256-hop case required laptop; Arco-Barco failed; errors accepted, no F1 or piano contact/air test |
| [ISMIR 2010 NMF](https://archives.ismir.net/ismir2010/paper/000083.pdf) | 25 MAPS excerpts, frame/onset/onset+offset F 65.5/71.1/28.2%; non-neural piano baseline | MATLAB laptop, 4 GB installed not used RAM; no E2E. Different MIREX abstract tuning not mixed in |
| [Pianolizer revision](https://github.com/creaktive/pianolizer/tree/735a7f2036a7e72d16b193acf1281f354bbdda24) | Actual live analysis and actual MIDI exporter exist | Exporter buffers whole file, averages whole notes and globally normalizes velocities; Arduino drives LEDs only |
| [2023 ESP32 competition source](https://github.com/GUT-9/2023TI-K-_ESP32_Arduino/tree/7b4f83a183e2241dcc81d512d2c4d955e08cc87a) | Dominant-frequency FFT board, 2048 readings at requested 10 kHz | Struck water cups, not piano; only one of two boards' code released |
| [Illinois 2026 design](https://courses.grainger.illinois.edu/ece445/getfile.asp?id=25484) | Proposed STM32F446RET6 microphone/LED system, one audio note at a time | Targets, not results; conflicting 200/50 ms targets; USD 95.70 proposed parts, not working transcriber |
| [Sonuus G2M](https://sonuus.com/products_g2m_faq.html), [Transkr](https://www.algoriffix.com/) | Physical monophonic box versus marketed polyphonic Windows/macOS software | Chips/performance unknown; observed USD 99.99 box and USD 129 regular software price are different priced objects |
| [Cycfi proposal](https://github.com/cycfi/hz_audio_to_midi/tree/0b37fa87dc607136a2a3585601cf25b41a51bce0), [Jones dulcimer](https://www.jamesjonesinstruments.com/post/a-midi-hammered-dulcimer-1) | Divided-pickup pitch tracking proposal; stalled fixed-note piezo trigger integration | Not built general piano transcribers; audio-per-string and known-note triggering are distinct |
| [Jung patent](https://patents.google.com/patent/US6856923B2/en) | Piano templates/subtraction, score-informed mode, dynamics/pedal ideas; Sony notebook examples | Patent is not measured MCU deployment; hop/localization accuracy is not response time |
| [Vaca FPGA](https://doi.org/10.1109/ISVLSI.2019.00075) | Zynq PL/ARM chord-recognition abstract | Full text unavailable; not MCU, no verified piano event benchmark |

Additional exclusions: Dubler voice-to-MIDI/chord generation is not simultaneous
piano inference. Union College Pi4 capstone uses electric guitar and has conflicting
dates/aggregates; its summary accuracy was not promoted into a benchmark.
Full primary links and inspected sections are retained in [S22-S36](../sources.md#s22).

## Access and reproducibility boundaries

Primary ITESO, NIME, ISMIR, Illinois and Union PDFs were downloaded and inspected;
ITESO p. 5 was rendered to confirm violin notes and cycle display. PDF hashes and
source commit/line links remain in the register. Downloaded code was never run.
No independent hardware replication was found.

YouTube tooling was unavailable; no video was watched or transcribed. Several
extraction endpoints returned 404; institutional bitstreams resolved core PDFs.
NXP guide/IRCAM abstract direct downloads timed out, indexed text was labeled.
Author-site TLS mismatch was not bypassed. IEEE full text and a live Scholar
citation sweep remained unavailable. Browser automation and paid research were
not used. Unreviewed thesis/maker leads were not counted as positive evidence.

## Reconciliation for this synthesis

Keep the genuine MCU two-note result. The original basic-event wording included
offset handling, but the canonical synthesis now explicitly treats **pitch/onset
transcription as a result in its own right**, with offset, velocity and pedal
scored separately. No negative conclusion is made by moving that definition.

Retained future suggestions: template baselines, score-informed versus unconstrained
conditions, adversarial polyphony/restrikes, causal emission audits, common-clock
latency measurements and matched air/contact recordings after electrical review
and fresh authorization. These are proposals, not performed experiments.
