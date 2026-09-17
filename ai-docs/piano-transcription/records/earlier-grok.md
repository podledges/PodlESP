---
title: "Retained source record: earlier Grok piano research"
report_date: "2026-09-17"
access_date: "2026-09-17"
status: "Sanitized curated record; corrections explicit"
---

# Earlier Grok source record

[Canonical synthesis](../README.md) | [Evidence](../evidence.md) | [Sources](../sources.md)

Original: **“Real-time piano-note transcription (ML + DSP) on microcontrollers”**,
independent scout `piano-research-grok`. Original report preserved separately;
this is a curated public research record, not verbatim operational history.

Original report SHA-256:
`e8cf21dde84bf86832306b599b0becb79344247a74beec0e5eb4d898985ce336`.

## Method and independence

First-wave web/literature search, primary PDF extraction, course/maker reports,
public repository READMEs and manufacturer specifications. The sibling's report
was not consulted before delivery. No model execution, firmware, hardware or
independent performance replication. Research recommendations were not authority
to build the proposed acquisition or transcription pipeline.

## Retained contributions

| Source / contribution | Reported evidence retained | Qualification |
|---|---|---|
| Jeong, ISMIR 2020 demo | Autoregressive note states, 32 ms hop, 320 ms context, <12 ms mean update on 2018 MacBook i5. [Primary PDF](https://program.ismir2020.net/static/lbd/ISMIR2020-LBD-444-abstract.pdf), [code](https://github.com/jdasam/online_amt) | PC microphone/MIDI/browser demo, not MCU; context and update compute are not E2E latency. PDF checked in earlier synthesis |
| Wei et al., 2025 | Streaming Seq2Seq, 16M parameters; MAESTRO onset 96.52%, with-duration 89.44%; 380 ms future context. [Paper](https://arxiv.org/pdf/2503.01362v1) | Computation explicitly excluded from latency calculation; research evaluation, not MCU. PDF checked in earlier synthesis |
| PAR / PARcompact | Online piano architecture and latency/size tradeoffs. [Paper](https://arxiv.org/pdf/2404.06818v1) | Exact paired rows replace broad approximate ranges in the original report |
| Onsets & Velocities | Strong onset/velocity scores and fast laptop throughput. [Paper](https://arxiv.org/pdf/2303.04485v2) | Seconds of context, no offsets/pedal, no MCU deployment |
| Mobile-AMT and causal adaptations | Phone/PC feasibility versus low-lookahead accuracy tradeoff. [Mobile-AMT](https://eurasip.org/Proceedings/Eusipco/Eusipco2024/pdfs/0000036.pdf), [Hu et al.](https://arxiv.org/abs/2509.07586) | 174 ms is formula, ten-second pooling critique unresolved for original deployment; hardware timing not measured by Hu |
| Basic Pitch | Tiny parameter count versus large measured desktop pipeline RAM. [Paper](https://arxiv.org/abs/2203.09893), [repository](https://github.com/spotify/basic-pitch) | Desktop process peak is not a lower bound for a rewrite; no measured MCU port |
| Onsets and Frames | Historical high-accuracy piano audio baseline. [ISMIR paper](https://ismir2018.ismir.net/doc/pdfs/19_Paper.pdf) | PC/research, not MCU |
| Cornell transcriber | Real RP2040 FFT note tracker. [Primary report](https://ece4760.github.io/Projects/Fall2022/jwl266_cds258_rat83/index.html) | Piano model not completed; no dense-piano event F1; not the separate triad project |
| Wrong-task checks | [Faust ESP32 synthesis/FX](https://www.nolanlem.com/pdfs/smc20_faust_esp32_.pdf), [Cybrid key sensing](https://github.com/ekumanov/cybrid) | Synthesis and mechanical MIDI sensing are not acoustic inference |

## Corrections preserved rather than silently copied

- The original “no measured S3 piano deployment found” is superseded by earlier
  Astra's **Huang isolated-note deployment**, not a polyphonic success.
- Default `mir_eval` pitch tolerance is **50 cents**, not one semitone.
  Timestamp tolerance is not user-visible response latency.
- Hu reduces lookahead of a **2048-sample window**, not the entire window to
  10 ms. Its strict-tolerance scores are not interchangeable with 50 ms scores.
- Contact piezo **may** reduce airborne noise; better transcription was not
  established. Soundboard audio remains a mixture; not every piezo is a key sensor.
- ESP32-S3 ADC2 DMA is unsupported in the cited continuous-driver documentation,
  a stronger target-specific issue than simply “avoid with Wi-Fi.” Board pins
  and memory must be independently identified. [Acquisition caveats](../piezo-and-adc.md)
- Device-family and mixed-SKU cost bands are not adopted as quotes. Use
  [priced objects, dates and exclusions](../evidence.md#hardware-costs) or unknown.
- Neither offsets, velocity, pedal nor a particular MAESTRO F1 is a mandatory
  definition of polyphonic pitch/onset transcription. These outputs are scored
  independently in the [broad comparison](../broad-evidence.md#output-coverage-without-moving-the-goalposts).

## Evidence limits and proposals

The original report did not find Huang, and its first-wave negative result
must be read with the narrower positive results added by the other records.
Agreement on desktop model limits is not independent experimental replication.
Commercial pickups/optical systems were illustrative rather than controlled
AMT benchmarks; no matched air/contact MCU piano study was found.

Retained future research sequence: define output/response criteria, evaluate
host-side models on matched recordings, audit causality, compare input modalities,
then test a constrained MCU baseline only under separate authorization. Source
metric, RAM, timing and sensing definitions must accompany every future claim.
