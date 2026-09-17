---
title: "Experiments that could confirm or disprove MCU piano feasibility"
report_date: "2026-09-17"
status: "Proposed research only; not implementation or hardware authorization"
---

# Experiments that could confirm or disprove MCU piano feasibility

[Overview](README.md) | [Evidence](evidence.md) |
[Piezo and ADC](piezo-and-adc.md) | [Sources](sources.md)

No experiments below have been performed by this synthesis. They are research
recommendations, not permission to implement, acquire audio, connect hardware,
flash or reset a board. The schematic lacks electrical sign-off. Hardware
experiments require that review, exact-board evidence and fresh authorization.

## 1. Separate the acceptance criteria

Define isolated pitch, chord pitch sets, onset/re-onset, offset and velocity
as different tasks. Declare maximum intended polyphony and playing rate.
Specify physical key release versus pedal-adjusted acoustic note end.
Choose response deadlines from the application, not a paper's “real-time” label.

Report onset F1 at 10, 20, 30 and 50 ms tolerance, offset-inclusive F1 with an
explicit offset rule, and per-key/register results. Add false notes per minute
in silence/noise, missed attacks, duplicate events and chord-set exact match.
For velocity, report absolute errors as well as any rescaled metric. Defaults
and their limits are in [the metric definitions](evidence.md#read-the-metrics-before-the-rankings).

**Disconfirming result:** a high clip-classification percentage hides false
notes, merged restrikes or missing soft notes. Do not rename it transcription
accuracy.

## 2. Establish an offline baseline before porting

Start with permitted public recordings and reliable aligned labels. Compare
harmonic-aware classical DSP with a small isolated-note classifier and a
published polyphonic desktop model. Include the SNet1D-style experiment as a
narrow reproduction target, not as a ready open-source implementation: its
weights and firmware were not found. Pin versions and record dataset licenses.
MAESTRO's license is CC BY-NC-SA 4.0. [S1](sources.md#s1), [S9](sources.md#s9)

Split by piano, session and mounting condition **before** slicing or
augmentation. Near-duplicate clips from one recording should not appear on
both sides of the test. A digital keyboard's MIDI is a valid oracle only for
the performance that produced the recorded audio, with clocks aligned; it is
not ground truth for a separate acoustic-piano performance.

**Disconfirming result:** ML does not beat the classical baseline under the same
window/latency budget, or excellent in-domain scores disappear on held-out
pianos. Neither a smaller MCU nor quantization repairs missing evidence.

Add fixed-template NMF/PLCA as **non-neural** baselines rather than comparing
only peak picking and deep models. The 2010 piano NMF and 2018 Pi3 augmentation
results justify the comparison, not an MCU feasibility promise.
[S24](sources.md#s24), [S25](sources.md#s25)

## 3. Compare sensors and analog branches fairly

After the safety prerequisites and authorization, use paired performances
recorded through an air mic and contact channels, preserving raw samples,
bias, clipping, timestamps and overflow metadata. Treat digital-piano line
output as a separate instrument/input condition. Test one conditioned piezo
channel before assuming multiple branches are beneficial.

Include quiet/loud attacks, bass/treble, detuning, speech, room changes,
pedal thumps, handling noise and changed mounts/gain. Measure transfer response
and channel correlation alongside transcription. Do not infer benefit from
SNR alone. [Sensor caveats](piezo-and-adc.md)

**Disconfirming result:** piezo remounting changes features more than note
identity, branches add no useful information, low-frequency loading removes
bass, or clipping creates harmonic false notes.

## 4. Make polyphony and articulation adversarial

Test every single key, octave and semitone pairs, fifths, triads, dense chords,
widely separated registers and soft notes under louder ones. Add arpeggios,
fast repeated notes, tremolos and pedal-held restrikes. Record exact stimulus
combinations and inter-onset times; no finite demo certifies every possible
chord. Keep missed/extra predictions in the denominator.

**Disconfirming result:** the system mistakes harmonics for additional keys,
merges repeated attacks, or uses room decay as a substitute for release timing.
Cornell and the compact-model ablations explain why these are essential
stress tests. [S2](sources.md#s2), [S5](sources.md#s5)

Compare the M7 violin-pair and Cornell triad tasks on their stated instrument,
register and hold-time conditions before testing transfer to acoustic piano.
For Cornell, include sine versus struck-piano timbres; for M7, keep beat-based
reporting separate from event timing. A four-note chord or wide-register pair
must not be scored by only whether its three loudest peaks form a known triad.
[S22](sources.md#s22), [S23](sources.md#s23)

Score-informed candidate restriction is a separate condition from unconstrained
transcription; disclose any expected score rather than silently narrowing the
recognition task. [S29](sources.md#s29), [S33](sources.md#s33)

## 5. Test causality, not just throughput

Replay identical audio prefixes with different future continuations. Outputs
already emitted before future audio arrives must not change. For bounded
lookahead, score results at the time they actually become available. Declare
any provisional events and revisions separately from final events.

Inspect transform centering, temporal pooling, normalization, backward
recurrent layers, future peak picking and whole-note averaging. Compare
bounded-streaming and offline outputs on the same data. This directly addresses
the [Mobile-AMT dispute](evidence.md#mobile-amt-174-ms-remains-a-qualified-claim)
and [Pianolizer's live-analysis versus file-export boundary](broad-evidence.md#why-sub-millisecond-computation-is-not-sub-millisecond-transcription).

**Disconfirming result:** RTF is below one but the queue grows, the model waits
seconds for context, or accurate event timestamps arrive after the usable
response deadline. Backdating is not low latency.

## 6. Measure an MCU candidate only when justified and authorized

Inventory operators, precision, model storage, peak internal RAM, PSRAM if any,
DSP buffers, recurrent state and DMA requirements. Profile feature extraction,
inference, decoding and the complete workload, not just a convolution kernel.
Compare accuracy before/after quantization on identical held-out data.

Use an independently recorded acoustic onset or precisely defined electrical
stimulus and an externally observed output event on a common clock. Report
median, p95, p99, maximum, misses, deadline failures and queue growth. Separate
mechanical-action-to-sound delay when assessing key-action responsiveness.
Record model/firmware hashes, board identity, clock, core allocation, numeric
format, concurrent display/radio load and long-run loss counters.

**Disconfirming result:** average inference fits but tails miss the deadline,
PSRAM contention loses samples, memory grows over time, or compression destroys
offsets/polyphony. Retain these failures rather than citing only a successful
allocation or one phrase played cleanly.

## What would change the conclusion?

A reproducible on-MCU result with **joint** task accuracy, defined end-to-end
latency, complete memory/compute measurements and held-out acoustic-piano
conditions would upgrade the current evidence. A piezo result additionally
needs mounting and frontend conditions. Open artifacts and independent
replication would increase confidence further.

Until then, compare three architectures honestly: constrained MCU note assist,
PC/phone audio transcription, and direct key sensing. They solve different
problems. This research does not choose between them or authorize deployment.
