---
title: "Piano transcription on a microcontroller"
report_date: "2026-09-17"
status: "Research synthesis; no hardware validation"
---

# Piano transcription on a microcontroller

[Research index](../README.md) | [Earlier evidence](evidence.md) |
[Broad-search evidence](broad-evidence.md) | [Piezo and ADC](piezo-and-adc.md) |
[Experiments](experiments.md) | [Sources](sources.md)

## The answer in brief

**Piano ML plus DSP has been reported on ESP32-S3, but for isolated notes,
not robust polyphonic transcription.** Huang Jixiang's 2025 paper reports
**99.6% classification accuracy on 1,000 live single notes**, 104.1 kB RAM
and 494.72 kB read-only storage. Its **217.8 ms average processing follows
512 ms of audio collection**. Neither figure is measured total
sound-to-MIDI latency. A straightforward collect-then-classify budget is
about 730 ms, an inference from the design rather than an end-to-end
measurement. [S1](sources.md#s1)

**MCU multipitch exists:** an August 2022 Cortex-M7 report demonstrates **two
violin notes**, with 0.98 ms task computation after 64 ms audio blocks and
beat aggregation. A separate Cornell RP2040 project identifies **triads**,
working well on sine tones but struggling with struck piano/guitar timbres.
Neither supplies general acoustic-piano pitch/onset transcription evidence.
[S22](sources.md#s22), [S23](sources.md#s23)

**Across four reports, no verified general polyphonic acoustic-piano note
transcriber running entirely on an MCU was found.** This is a bounded search
result, not impossibility. Pitch, onset/re-onset, offset, velocity and pedal
are separate outputs: missing offset/velocity/pedal does not invalidate a
real polyphonic pitch/onset result. Do not require MAESTRO or a new accuracy
threshold merely to exclude a positive demonstration.

These tasks must remain separate:

| Task | Evidence found | What it does not establish |
|---|---|---|
| MCU isolated-note classification | Huang's S3 author-reported deployment | Chords, re-onsets, offsets, velocity, all-key robustness or interactive latency |
| Restricted MCU multipitch / chord labeling | M7 violin pair; RP2040 triads | General acoustic-piano note events, scored expressivity or measured full response |
| Polyphonic audio-to-note inference | Strong PC/mobile papers and source repositories | The same accuracy, memory footprint or timing on an S3 |
| Key/hammer sensing to MIDI | Optical sensing in instruments such as Disklavier | Audio inference: this observes the mechanism, not the mixed sound |

No hardware was accessed and no model was benchmarked for this synthesis.
No external inference service or cloud is required by the documented local
PC/mobile deployments; training on a GPU is separate from where inference
runs. Conversely, an MCU sending audio to a host would not be MCU-only AMT.

## Read by question

- **What did the wider search add?** [MCU multipitch, older DSP, patents and near-misses](broad-evidence.md).
- **Who did it, and how well?** [Earlier evidence and matched comparisons](evidence.md).
- **Does a piezo simplify the problem?** [Sensor and circuit caveats](piezo-and-adc.md).
- **What should be tested next?** [Falsifiable experiments](experiments.md).
- **Where did each claim come from?** [Primary-source register](sources.md).

```text
Air microphone / soundboard piezo / electrical AUDIO output
                          |
             conditioning + ADC or codec
                          |
           classical DSP / templates / ML
                          |
          pitch + onset; optional other outputs
                          |
                externally available event

Key / hammer optical sensor -> key events -> MIDI
                 is a different measurement path.

Observe the whole audio path's delay, not just its feature hop.
```

## Research provenance and reconciled findings

All **four reports** are dated/accessed **2026-09-17**. Each pair was independent
of its sibling before delivery. The broader pair read the earlier reports to
avoid repeating covered sources. Agreement is not independent experimental
replication. Original reports and scratch evidence remain preserved separately;
the vault now also retains these **sanitized, curated source records**, with
original fingerprints, public citations and explicit editorial corrections:

| Wave / record | Distinct contribution |
|---|---|
| [Earlier Astra](records/earlier-astra.md) | Huang S3 isolated notes, source/latency audit, circuitry and metric detail |
| [Earlier Grok](records/earlier-grok.md) | Jeong/Wei online leads, architectural comparisons and disconfirming causal evidence |
| [Broad Astra](records/broad-astra.md) | M7 violin, NIME Pi3, older NMF, Pianolizer and maker/product distinctions |
| [Broad Grok](records/broad-grok.md) | RP2040 triads, Chinese DSP, Casio disclosure and additional FPGA abstracts |

This extends the same canonical vault introduced in
[PR #12](https://github.com/podledges/PodlESP/pull/12), not a competing copy.
It is synthesis with selected primary-source checks, not a third scout or
new runtime benchmark. Search/access limitations remain attached to the records.

| Difference or tempting interpretation | Resolution from primary evidence |
|---|---|
| No MCU multipitch exists | M7 two-note violin and RP2040 triads are genuine narrower positives. [Broad evidence](broad-evidence.md) |
| Casio patent proves commercial productization | Patent proves disclosure, not a built or shipped product. [S28](sources.md#s28) |
| Tiny task compute or frequent spectral updates prove fast MIDI | M7 beat aggregation and Pianolizer whole-file export must be included. [Timing boundaries](broad-evidence.md#why-sub-millisecond-computation-is-not-sub-millisecond-transcription) |
| Generic hardware cost bands price a working transcriber | Keep item/date/source-specific quotes or unknown; exclude unsupported ballparks. [Cost boundaries](broad-evidence.md#commercial-and-contact-sensing-exclusions) |
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
