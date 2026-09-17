---
title: "Piezo sensing and ESP32-S3 acquisition caveats"
report_date: "2026-09-17"
status: "Concepts and prerequisites; schematic not electrically signed off"
---

# Piezo sensing and ESP32-S3 acquisition caveats

[Overview](README.md) | [Evidence](evidence.md) |
[Experiments](experiments.md) | [Sources](sources.md)

**The current schematic has not received electrical sign-off.** These notes
explain what must be understood, not an approved circuit, pin assignment or
permission to connect hardware. Existing firmware is not a binding design.

## Four inputs, different evidence

| Input | What is measured | Main confounders | What existing results transfer? |
|---|---|---|---|
| Air microphone | Radiated instrument sound plus room | Reverberation, speech, distance, clipping, microphone response | Closest to MAESTRO/IDMT piano studies, still subject to domain shift |
| Soundboard piezo / contact pickup | Structure-borne vibration | Mounting, resonances, pedal/handling noise, cable/loading | No controlled MCU piano-AMT piezo-versus-air benchmark found in the two searches |
| Electrical pickup / digital-piano line output | Analog audio, often already mixed across notes | Pickup/timbre/gain differences; model and instrument settings | Less room involvement is not proof of acoustic-piano or piezo accuracy |
| Key/hammer optical or electrical sensing | Mechanism position/motion | Sensor calibration, mechanical installation, release definition | Direct MIDI sensing is not audio inference, even when the screen looks identical |

MAESTRO uses acoustic Disklavier piano recordings with captured MIDI labels.
Yamaha's optical key/hammer/pedal system is the labeling mechanism, not the
transcription model. Its manufacturer precision claims should not be relabeled
as ML accuracy. [S9](sources.md#s9), [S14](sources.md#s14)

A contact pickup **may** reduce direct airborne interference, but transcription
can worsen because the model has learned air-mic spectra. There is no universal
piezo improvement supported by the reviewed experiments. Mobile-AMT's IDMT
results demonstrate recording-domain sensitivity, not piezo robustness.
[S6](sources.md#s6)

## Parallel analog paths are not source separation

```text
One piezo -> shared mechanical mixture -> branch A: gain/filter -> ADC channel
                                     -> branch B: gain/filter -> ADC channel

Two branches provide conditioned views, not two independently isolated notes.
Multiple physical piezos might add spatial information; measure correlation.
```

Splitting one high-impedance source may also change loading. Different gains
can help dynamic range, but clipping, phase response and channel sampling skew
must be characterized before combining features. Many sensors near keys do
not automatically become perfect key sensors: cross-coupling must be measured.

## Understand each component's job

Texas Instruments models a piezo as a charge source with capacitance/leakage.
Its output depends on excitation and can range from microvolts to hundreds of
volts across applications. That range is a protection warning, not a prediction
for this sensor. Static charge decays, so an isolated strike detector cannot
simply infer a continuously held key. [S13](sources.md#s13)

| Function | Why it matters | Required future evidence |
|---|---|---|
| Sensor, mounting, cable | Sets mechanical/electrical transfer function | Sensor specification, repeatable attachment, cable capacitance and frequency response |
| Input resistance / buffer | Loading can remove bass; bias current causes offsets | Input impedance, leakage and low-frequency corner, including A0 |
| Protection | Strikes, unplugging and faults may exceed component limits | Reviewed clamp currents, leakage/capacitance, absolute limits and fault behavior |
| Bias / reference | Bipolar audio must fit the ADC's unipolar range | Actual usable range, reference noise, startup and saturation recovery |
| Gain / branch isolation | Soft attacks need SNR; loud attacks clip | Headroom, cross-loading, inter-branch amplitude and phase |
| High/low-pass filtering | Bass loss and aliasing can create irrecoverable feature errors | Analog response at actual per-channel sample rate; digital filtering cannot undo aliasing |
| Supply, grounding, decoupling | Display/radio/digital noise can enter weak audio | Noise under intended concurrent workloads, not only an idle board |
| ADC / buffers / clocks | Gaps or skew corrupt spectra and event times | Measured rates, channel ordering/skew, overflow counts and timebase alignment |

TI's voltage-mode example depends on sensor/cable capacitance and favors a
nearby high-input-impedance amplifier. Its charge-mode example uses feedback
capacitance to convert charge to voltage and a feedback resistor to bleed
charge and set the low-frequency corner. Neither is a certified PodlESP circuit;
component values and protection require exact-board review. [S13](sources.md#s13)

## ESP32-S3 ADC is a chip capability, not a board pin map

- Silicon ADC1 channels map to GPIO1-10; ADC2 to GPIO11-20. A package, USB,
  display or other routing may consume or hide those pins. Do not borrow
  assignments from a different ESP32 model. [S21](sources.md#s21)
- ESP-IDF release-v5.3 says **ADC2 DMA retrieval is no longer supported because
  unstable results were observed**. ADC-183 describes the digital controller
  becoming inoperative and says no fix is scheduled. Do not force unsupported
  ADC2 DMA merely because two ADC units exist. [S12](sources.md#s12)
- Multiple channel patterns do not prove simultaneous acquisition. Verify
  aggregate and per-channel rates, skew, settling and loss. Nominal 12-bit
  samples do not certify effective resolution or audio quality.
- The continuous driver can lose results when its buffer fills. Preserve loss
  counters and raw bias/clipping evidence; a timestamp after dropped samples
  cannot reconstruct the missing audio.
- The cited SDK documentation is a target-specific reference, not a claim
  about the firmware's configured version. Likewise, the board's advertised
  PSRAM/flash is not confirmed by a smoke build. [S21](sources.md#s21)

One 8,192-sample int16 audio buffer takes 16,384 bytes; four channels take
65,536 bytes before DMA, features, model state or duplicated buffering. That
arithmetic is a planning input, not a feasibility measurement.

## Before any later hardware experiment

Obtain exact board/revision and sensor information, electrical review,
confirmed available pins and fresh scoped authorization. Then measure the
acquisition chain separately from inference. Do not infer analog safety,
calibration or lossless streaming from a successful firmware build or a
published neural-network score. The [experiment plan](experiments.md) describes
what useful evidence would look like without authorizing its execution.
