---
title: "Retained source record: earlier Astra piano research"
report_date: "2026-09-17"
access_date: "2026-09-17"
status: "Sanitized curated record; not a new experiment or verbatim report"
---

# Earlier Astra source record

[Canonical synthesis](../README.md) | [Evidence](../evidence.md) | [Sources](../sources.md)

Original: **“MCU piano audio transcription: what has actually been demonstrated?”**,
independent scout `piano-research-astra`. The original report and scratch evidence
are preserved separately. This publication retains its research contribution,
public source trail and limitations, not private operational logs or host paths.

Original report SHA-256:
`614f98a625ca2a36433403e3cc3dd90247a1a3483d51675cb234e8c52da3fe0f`.

## Method and independence

Independent first-wave search of primary papers, author reports, official
datasets, manufacturer documentation and source repositories. The sibling report
was not consulted before delivery. PDFs and public source were read, not executed;
no model, firmware or hardware benchmark was run. Synthesis is not replication.

## Retained findings and primary evidence

| Contribution | Evidence retained | Boundary |
|---|---|---|
| Huang SNet1D, ESP32-S3 | 99.6% on 1000 live isolated notes; 104.1 kB RAM, 494.72 kB read-only storage; 217.8 ms processing follows 512 ms acquisition. [Primary PDF](https://www.sdie.org.cn/staticjt/upload/file/20251128/1764296896339521.pdf) | Not chords or scored note events; ~730 ms sequential budget is derived, not measured E2E. No open model/firmware or held-out-piano split established |
| Cornell RP2040 transcriber | Actual FFT/threshold/debounce path; internal on/off states, PC MIDI file after STOP. [Author report](https://ece4760.github.io/Projects/Fall2022/jwl266_cds258_rat83/index.html) | Piano ML unfinished; deployed neural tutorial was fire-alarm classification. Piano spectra impractical in completed DSP method |
| Basic Pitch | Original 16,782 parameters; 70.9% onset / 10.5% with-offset piano F1, 951 MB long-file desktop peak. [Paper](https://arxiv.org/abs/2203.09893) | Tiny weights are not total RAM; desktop overhead is not an embedded lower bound; original paper is not every later version |
| Basic Pitch source audit | Reverse-time onset processing, forward/backward tracing and whole-note means. [Pinned decoder](https://github.com/spotify/basic-pitch/blob/fa5997af0a8210982619003269994a1be25eddf3/basic_pitch/note_creation.py#L403-L501) | Not a proven causal MCU emitter; 204,448-byte TFLite file does not specify Micro compatibility or arena size |
| Onsets & Velocities | 96.78% onset / 94.50% onset+velocity F1; laptop throughput <2 s per 120 s audio. [Paper](https://arxiv.org/abs/2303.04485v2) | No offset/pedal; 24 ms hop with seconds of context, including 4 s workshop configuration |
| PARcompact | At 160 ms modeled context: 94.33% onset / 78.25% with-offset F1. [Paper](https://arxiv.org/abs/2404.06818v1) | Match size/latency/accuracy by row; no MCU measured runtime; aggressive size reduction hurts offsets |
| Mobile-AMT | 96.30% onset / 76.80% +offset / 75.53% +offset+velocity; 174 ms formula, phone/tablet/PC RTF, 129 MB MacBook peak. [Paper](https://eurasip.org/Proceedings/Eusipco/Eusipco2024/pdfs/0000036.pdf) | Deployed pooling/buffering remains unresolved against later criticism; neither 174 ms nor ten seconds is independently measured E2E |
| Causal-AMT | Final 30 ms-tolerance onset F1 37.38%, with-offset 10.37%. [Paper](https://arxiv.org/abs/2509.07586) | Shifted 2048-sample window, not 10 ms-long window; operation counts, not hardware timing; not proof future causal methods must fail |
| Metrics and sensors | [mir_eval](https://github.com/craffel/mir_eval/blob/fe73b3533737814f83dbd9739f06e90f5f82f758/mir_eval/transcription.py), [MAESTRO](https://magenta.tensorflow.org/datasets/maestro), [TI SLOA033A](https://www.ti.com/lit/an/sloa033a/sloa033a.pdf) | 50-cent pitch tolerance; acoustic audio with MIDI labels; no proven piezo transcription advantage or electrical sign-off |

The complete retained [earlier comparison](../evidence.md), [sensor analysis](../piezo-and-adc.md)
and [source register S1-S21](../sources.md#s1) include further conditions:
Huang's datasets/ROM terminology, matched PAR ablations, IDMT domain shift,
Stefani's guitar-technique wrong-task example, Zammit's abstract, ADC2 DMA caveat
and exact priced components. No full-system price was established.

## Search limits and editorial reconciliation

Some extraction endpoints failed; accessible publisher PDFs and author sources
supplied core evidence. Huang Figure 6 was rendered and inspected. MCAST full
text was not recovered. A linked Cornell video was not viewed; unavailable
YouTube tooling did not become video evidence. No independent device replication
was located. Source revisions/fingerprints are retained in the register.

The original negative conclusion was bounded to general piano transcription,
not every musical-pitch task. The broadened synthesis adds genuine
[M7 violin and RP2040 triad evidence](../broad-evidence.md). Missing offsets,
velocity or pedal must not erase genuine pitch/onset transcription. This record
is historical research evidence, not authority to implement its recommendations.

Future proposals retained: held-out-piano/session splits, matched air/contact
recordings after electrical review, adversarial chords/restrikes, prefix-based
causality tests, and full-path latency/memory profiling on a separately authorized
identified MCU. None was performed by this report.
