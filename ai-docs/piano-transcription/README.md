---
title: "Piano transcription on a microcontroller"
report_date: "2026-09-17"
status: "Research synthesis; no hardware validation"
---

# Piano transcription on a microcontroller

[Research index](../README.md) | [Evidence](evidence.md) |
[Piezo and ADC](piezo-and-adc.md) | [Experiments](experiments.md) |
[Sources](sources.md)

## The answer in brief

**Piano ML plus DSP has been reported on ESP32-S3, but for isolated notes,
not robust polyphonic transcription.** Huang Jixiang's 2025 paper reports
**99.6% classification accuracy on 1,000 live single notes**, 104.1 kB RAM
and 494.72 kB read-only storage. Its **217.8 ms average processing follows
512 ms of audio collection**. Neither figure is measured total
sound-to-MIDI latency. A straightforward collect-then-classify budget is
about 730 ms, an inference from the design rather than an end-to-end
measurement. [S1](sources.md#s1)

**The two searches found no adequately evidenced accurate, low-latency,
full-polyphonic piano transcription deployment running entirely on an MCU.**
That is a bounded literature-search result, not proof of impossibility.
The strongest polyphonic examples inspected use PCs, phones or tablets,
or report algorithmic lookahead without a measured deployment deadline.

Three different tasks must remain separate:

| Task | Evidence found | What it does not establish |
|---|---|---|
| MCU isolated-note classification | Huang's S3 author-reported deployment | Chords, re-onsets, offsets, velocity, all-key robustness or interactive latency |
| Polyphonic audio-to-note inference | Strong PC/mobile papers and source repositories | The same accuracy, memory footprint or timing on an S3 |
| Key/hammer sensing to MIDI | Optical sensing in instruments such as Disklavier | Audio inference: this observes the mechanism, not the mixed sound |

No hardware was accessed and no model was benchmarked for this synthesis.
No external inference service or cloud is required by the documented local
PC/mobile deployments; training on a GPU is separate from where inference
runs. Conversely, an MCU sending audio to a host would not be MCU-only AMT.

## Read by question

- **Who did it, and how well?** [Evidence and matched comparisons](evidence.md).
- **Does a piezo simplify the problem?** [Sensor and circuit caveats](piezo-and-adc.md).
- **What should be tested next?** [Falsifiable experiments](experiments.md).
- **Where did each claim come from?** [Primary-source register](sources.md).

```text
Air microphone / soundboard piezo / electrical AUDIO output
                          |
             conditioning + ADC or codec
                          |
               DSP features + ML model
                          |
        pitch + onset + offset + velocity decoder
                          |
                externally available event

Key / hammer optical sensor -> key events -> MIDI
                 is a different measurement path.

Observe the whole audio path's delay, not just its feature hop.
```

## Research provenance and reconciled findings

This is the synthesis of **two completed independent reports**, both dated
2026-09-17: **Astra**, “MCU piano audio transcription: what has actually been
demonstrated?”, and **Grok**, “Real-time piano-note transcription (ML + DSP)
on microcontrollers.” Neither scout consulted the other before delivery.
Original reports and scratch evidence are preserved separately, not copied
into this vault. This follow-on cross-checks their primary evidence; it is
not a third scout or an independent replication of the papers.

Astra contributed the S3 single-note study, detailed circuit/source audit and
latency caveats. Grok contributed additional online-system leads, notably
Jeong's 2020 demo and Wei et al.'s 2025 streaming paper; their primary PDFs
were checked during synthesis. Shared conclusions are not counted as two
independent experimental validations.

| Difference or tempting interpretation | Resolution from primary evidence |
|---|---|
| Grok found no measured S3 piano ML deployment | Huang supplies a narrower positive result: isolated-note classification, not polyphonic event transcription. [S1](sources.md#s1) |
| Mobile-AMT has 174 ms latency, or definitely ten seconds | Keep the original 174 ms formula and the later pooling critique distinct. The original deployed graph's buffering/causality remains unresolved. [S6](sources.md#s6), [S7](sources.md#s7) |
| Basic Pitch's desktop RAM rules out every MCU rewrite | Desktop process peaks are not an embedded lower bound; no measured embedded replacement was established. [S3](sources.md#s3) |
| A matching pitch may differ by one semitone | Default `mir_eval` pitch tolerance is **50 cents**, half a semitone, not one semitone. [S8](sources.md#s8) |
| Compact PAR accuracy and shortest delay can be combined | Use the exact paired rows in [the latency table](evidence.md#parcompact); 128 ms has substantially lower scores than 320 ms. [S5](sources.md#s5) |
| Cornell demonstrated piano ML on Pico | It did not finish that model. The deployed neural tutorial was a fire-alarm classifier. [S2](sources.md#s2) |
| Hu's negative result used only a 10 ms audio window | The experiment shifts a **2,048-sample window** to reduce lookahead, rather than shrinking the entire window to 10 ms. Accuracy still falls. [S7](sources.md#s7) |
| Jeong's 320 ms buffer or Wei's 380 ms figure is measured end-to-end latency | Jeong reports context length and per-update compute separately. Wei explicitly sets computational speed aside in its latency calculation. [S19](sources.md#s19), [S20](sources.md#s20) |

## Project boundary

PodlESP's research interest is piezo sensing with parallel analog frontends
intended for ESP32-S3 ADC acquisition. Existing firmware is not a binding
signal-processing design. **The current schematic has not received electrical
sign-off.** Board identity, available pins, gain, bias, protection, filtering
and sample integrity require evidence before any future hardware work.

These notes recommend experiments, not implementation, procurement or
hardware operations. They do not select a product architecture or authorize
a connection, reset, flash, acquisition run or self-test.
