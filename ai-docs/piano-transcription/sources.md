---
title: "Primary sources and evidence boundaries"
report_date: "2026-09-17"
access_date: "2026-09-17"
status: "Source register for the two-scout synthesis"
---

# Primary sources and evidence boundaries

[Overview and provenance](README.md) | [Comparisons](evidence.md) |
[Piezo and ADC](piezo-and-adc.md) | [Experiments](experiments.md)

Sources were consulted on **2026-09-17**. Publications have their own dates
below. Core numbers come from full primary papers or code, not popularity,
search-result counts or agreement between scouts. These remain author-reported
results unless explicitly identified otherwise; neither scout independently
replicated the systems. DOI and author-linked repository URLs may serve as
identifiers without implying every linked artifact was inspected.

## S1

**Huang Jixiang, 2025: 基于知识蒸馏的轻量级钢琴单音识别方案**
(“Lightweight piano single-note recognition based on knowledge distillation”).
*Information Technology and Informatization*, issue 10, pp. 27-31;
DOI 10.3969/j.issn.1672-9528.2025.10.006. Revised 2025-10-10;
publisher listing dated 2025-11-28.

- Full primary PDF: <https://www.sdie.org.cn/staticjt/upload/file/20251128/1764296896339521.pdf>
- Publisher listing: <https://www.sdie.org.cn/list_79/>
- DOI: <https://doi.org/10.3969/j.issn.1672-9528.2025.10.006>
- Support: sections 1-3, Tables 1-3, Figures 3-6. Figure 6 on printed p. 30
  was visually checked: the 512 ms capture precedes recognition. Table 3
  reports 99.6%, 217.8 ms, 104.1 kB RAM and 494.72 kB read-only storage.
- Boundary: isolated labels, no open deployment artifacts or independent
  replication located. Dataset splitting by piano and total latency unverified.
- Retrieved PDF SHA-256: `5ffcecb6936a2d2dbac373d3fb195df1ba3b663f4257ce97ac2817c0983d9f2e`.

## S2

**Christopher Schiff, Jacob Lashin and Romano Tio: Cornell RP2040 transcriber.**
Fall 2022 course report; Circuit Cellar issue 398, September 2023, web article
dated 2024-03-08.

- Primary report: <https://ece4760.github.io/Projects/Fall2022/jwl266_cds258_rat83/index.html>
- Author article: <https://circuitcellar.com/research-design-hub/real-time-automatic-music-transcriber/>
- Report repository: <https://github.com/JacobLashin/jwl266_cds258_rat83_ECE4760_FinalProject/tree/536d9f292ebfbcb2f14378401af08eb73e1d3d0a>
- TFLite framework port, not a piano model: <https://github.com/cds258/pico-tflu-4760/tree/c37b87c634b7a39842768e31c1b74495fcfc5fd2>
- Author-linked video, not independently viewed during synthesis:
  <https://www.youtube.com/watch?v=c4soAzSzYtE>
- Support: Conclusions and Machine Learning sections distinguish completed
  FFT/MIDI work, the fire-alarm tutorial and unfinished piano ML. Magazine
  article provides FFT settings and explicit complex-instrument limitations;
  its indexed text was cross-checked against the accessible course report.
- Boundary: qualitative demonstration, no formal piano event F1 or total
  response measurement. Inspected report repository contains website assets,
  not a complete piano-inference firmware release.

## S3

**Rachel M. Bittner, Juan José Bosch, David Rubinstein, Gabriel Meseguer-Brocal
and Sebastian Ewert, ICASSP 2022: Notes and Multipitch / Basic Pitch.**

- Paper: <https://arxiv.org/pdf/2203.09893>
- Repository: <https://github.com/spotify/basic-pitch/tree/fa5997af0a8210982619003269994a1be25eddf3>
- Window settings: <https://github.com/spotify/basic-pitch/blob/fa5997af0a8210982619003269994a1be25eddf3/basic_pitch/constants.py#L25-L47>
- File inference: <https://github.com/spotify/basic-pitch/blob/fa5997af0a8210982619003269994a1be25eddf3/basic_pitch/inference.py#L194-L244>
- Note decoder: <https://github.com/spotify/basic-pitch/blob/fa5997af0a8210982619003269994a1be25eddf3/basic_pitch/note_creation.py#L403-L501>
- Support: paper sections 3, 4.3, 4.5 and Table 3 give architecture, piano scores
  and desktop process memory/timing. Source confirms reverse-time onset order,
  bidirectional energy tracing and mean-frame-activation amplitude.
- Boundary: current releases differ from the original paper. The inspected
  TFLite artifact is 204,448 bytes, not a measured MCU arena or runtime.
  Desktop process RAM is not a lower bound on a rewritten embedded pipeline.

## S4

**Andrés Fernández, EUSIPCO 2023: Onsets and Velocities.**
Inspected arXiv v2, 2023-06-01.

- Paper: <https://arxiv.org/pdf/2303.04485v2>
- Desktop demo: <https://github.com/andres-fr/iamusica_demo/tree/6f2067ef734a8fba0cdf4db2c106248d1e66ffe3>
- Author-linked training repository: <https://github.com/andres-fr/iamusica_training>
- Support: Table I, sections II-A/C and III(c,e): 96.78% onset, 94.50%
  onset+velocity F1, 24 ms hop, CPU throughput and seconds-scale context.
  Demo README describes approximately 5.5 s configuration and laptop-mic use.
- Boundary: no offsets/pedal; 4 s workshop context truncation has no rigorous
  paired accuracy study. Not an MCU deployment.

## S5

**Taegyun Kwon, Dasaem Jeong and Juhan Nam, 2024: PAR / PARcompact.**
Inspected arXiv v1 dated 2024-04-10, marked under review. Later bibliographies
cite the journal publication; this synthesis uses the inspected preprint.

- Paper: <https://arxiv.org/pdf/2404.06818v1>
- Repository, metadata/README inspected:
  <https://github.com/TaegyunKwon/PARpiano/tree/4b4659c0a7d848968b5b4336502c2a9d57c620eb>
- Support: sections IV-B/C and V-C/D/E; Table III size ablation, Table IV
  **paired** latency/accuracy, Table V cross-dataset performance.
- Boundary: context latency is not measured MCU end-to-end timing. Whole-piece
  research evaluation and compact-model results must not be conflated with
  a verified streaming device or the larger PAR model's accuracy.

## S6

**Yuta Kusaka and Akira Maezawa, Yamaha, EUSIPCO 2024: Mobile-AMT**, pp. 36-40.

- Primary proceedings: <https://eurasip.org/Proceedings/Eusipco/Eusipco2024/pdfs/0000036.pdf>
- Support: section III-A, equations 1-2 describe frame-wise inference and
  latency; sections IV/V and Tables IV/V give evaluation conditions,
  MAESTRO/IDMT scores, single-core device RTF and 129 MB MacBook peak RAM.
- Boundary: 174 ms is a formula. Original deployed ONNX graph was not verified;
  S7's global-pooling criticism remains unresolved, not a settled replacement
  latency. No MCU or piezo deployment benchmark.

## S7

**Patricia Hu, Silvan David Peter, Jan Schlüter and Gerhard Widmer, 2025:
Exploring System Adaptations for Minimum Latency Real-Time Piano Transcription.**
arXiv posted 2025-09-09.

- Paper: <https://arxiv.org/pdf/2509.07586>
- HTML: <https://arxiv.org/html/2509.07586>
- Support: section 3.1 pooling critique; section 4.2 shifted/asymmetric windows;
  final Table 4 strict-tolerance scores; section 5 computation estimate and
  hardware timing explicitly left to future work.
- Boundary: the causal baseline's poor scores do not prove impossibility of
  future methods. This is not an independent measurement of S6's original
  phone binary. Do not call its 10 ms lookahead a 10 ms-long window.

## S8

**mir_eval metric implementation**, inspected revision
`fe73b3533737814f83dbd9739f06e90f5f82f758`.

- <https://github.com/craffel/mir_eval/blob/fe73b3533737814f83dbd9739f06e90f5f82f758/mir_eval/transcription.py>
- <https://github.com/craffel/mir_eval/blob/fe73b3533737814f83dbd9739f06e90f5f82f758/mir_eval/transcription_velocity.py>
- Support: default onset/pitch/offset tolerances and velocity normalization plus
  fitted scale/intercept. Code inspected, not executed for a transcription test.
- Boundary: historical papers may use different versions/options; record those
  in any reproduction. Default pitch tolerance is 50 cents, not 100 cents.

## S9

**Google/Magenta, MAESTRO dataset**, page originally dated 2018-10-29,
including v3.0.0 documentation.

- <https://magenta.tensorflow.org/datasets/maestro>
- Support: acoustic Disklavier performances, MIDI labels, about 3 ms alignment,
  composition-separated splits, versions and CC BY-NC-SA 4.0 license.
- Boundary: classical concert piano data does not certify arbitrary rooms,
  contact pickups or unobserved pianos. Licensing needs review for downstream use.

## S10

**Domenico Stefani and Luca Turchet, DAFx 2022: On the Challenges of Embedded
Real-time Music Information Retrieval.**

- Author PDF: <https://www.lucaturchet.it/PUBLIC_DOWNLOADS/publications/conferences/On_the_Challenges_of_Embedded_Real-Time_Music_Information_Retrieval.pdf>
- Author-linked implementation, not source-audited here:
  <https://github.com/domenicostefani/cpp-timbreID/>
- Support: sections 4.1-4.4.1, Tables 1-3: guitar techniques, Raspberry Pi 4
  Linux SBC, five guitars/players, random split and component-summed 30.7 ms.
- Boundary: paper explicitly excludes MCU scope; technique classification is
  not pitch transcription, and approximate summed delay is not exact total delay.

## S11

**Joseph A. Zammit and Joseph Cutajar, MCAST Journal of Applied Research &
Practice 9(2), 2025: An Embedded Real-time Musical Note and Beat Transcription
System.** DOI metadata dated 2025-07-15.

- <https://doi.org/10.5604/01.3001.0055.2099>
- Author publication list: <https://electronics-lab.info/?page_id=94>
- Support: author list confirms publication; indexed abstract describes
  STM32F407, CMSIS FFT, electret input and piano/generated-tone tests.
- Boundary: full text not retrieved; no numeric accuracy, timing, polyphony or
  ML claim verified. A lead only, not evidence for the main positive conclusion.

## S12

**Espressif, ESP32-S3 datasheet v2.2, continuous ADC documentation and ADC-183.**

- <https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf>
- <https://docs.espressif.com/projects/esp-idf/en/release-v5.3/esp32s3/api-reference/peripherals/adc_continuous.html>
- <https://docs.espressif.com/projects/esp-chip-errata/en/latest/esp32s3/03-errata-description/shared/sar-adc-adc2-not-work.html>
- Support: CPU/memory/ADC capabilities; continuous-driver buffer loss and
  unsupported ADC2 DMA. Erratum says no fix scheduled.
- Boundary: chip/SDK facts, not identified-board pin availability, configured
  SDK version, measured effective resolution or ML execution performance.

## S13

**James Karki, Texas Instruments, SLOA033A, September 2000:
Signal Conditioning Piezoelectric Sensors.**

- <https://www.ti.com/lit/an/sloa033a/sloa033a.pdf>
- Support: sections 2, 3.1, 3.2 explain charge/capacitance/leakage, impedance,
  bias, cable effects and voltage/charge-mode amplification.
- Boundary: illustrative circuits, not PodlESP sign-off, selected values or a
  certified protection design.

## S14

**Yamaha ENSPIRE PRO features**, undated manufacturer page.

- <https://usa.yamaha.com/products/musical_instruments/pianos/disklavier/enspire_pro/features.html>
- Support: optical key/hammer/pedal sensing, distinct from audio inference.
- Boundary: performance precision is manufacturer marketing, not independently
  validated audio-transcription accuracy.

## S15

**Adafruit ESP32-S3 Feather 5477**, price observed 2026-09-17: **USD 17.50**.

- <https://www.adafruit.com/product/5477>
- 4 MB flash / 2 MB PSRAM board only. Not the identified experimental board;
  excludes sensor/frontend and all system costs listed in [costs](evidence.md#hardware-costs).

## S16

**Adafruit MAX4466 electret microphone amplifier 1063**, price observed
2026-09-17: **USD 6.95**.

- <https://www.adafruit.com/product/1063>
- Mic/amplifier only, not a complete acquisition or transcription system.

## S17

**Adafruit enclosed piezo element 1739**, price observed 2026-09-17:
**USD 0.95**.

- <https://www.adafruit.com/product/1739>
- Raw resonant element, not a calibrated piano pickup or protected frontend.

## S18

**Raspberry Pi Pico launch announcement**, 2021-01-21: **USD 4 board price**.

- <https://www.raspberrypi.com/news/raspberry-pi-silicon-pico-now-on-sale/>
- Publication metadata was checked. Historical launch price, not a current quote
  or a complete Cornell-system BOM.

## S19

**Dasaem Jeong, ISMIR 2020 late-breaking demo:
Real-time Automatic Piano Music Transcription System.**

- Primary PDF: <https://program.ismir2020.net/static/lbd/ISMIR2020-LBD-444-abstract.pdf>
- Author-linked code: <https://github.com/jdasam/online_amt>
- Support: sections 2-4: MAESTRO v2-trained autoregressive states, 32 ms hop,
  5,120-sample / 320 ms buffer, <12 ms average update on 2018 quad-core i5
  MacBook, PyAudio/PyTorch, browser and MIDI visualization.
- Boundary: compute per update is not measured total latency; no full accuracy
  table in the demo abstract. Synthesis checked the PDF, not execution of code.

## S20

**Weixing Wei, Jiahao Zhao, Yulun Wu and Kazuyoshi Yoshii, 2025:
Streaming Piano Transcription Based on Consistent Onset and Offset Decoding
with Sustain Pedal Detection.** Inspected arXiv v1 dated 2025-03-03.

- Primary PDF: <https://arxiv.org/pdf/2503.01362v1>
- Support: Tables 2-4, sections 4.1.5 and 4.2.3: MAESTRO v3 test, 16M
  parameters, 96.52% onset / 89.44% with-duration F1, 50 ms onset tolerance,
  max(50 ms, 20% duration) offset tolerance, 19 future frames × 20 ms.
- Boundary: its 380 ms calculation **explicitly puts computational speed
  aside**. Not a device runtime, MCU result or proof of external MIDI latency.

## S21

**PodlESP current project context**, repository revision
`53ada7be017220a06a9c7e7547fd9a0d83b6d13b` at synthesis base.
Public repository links keep these context references usable when `ai-docs`
is opened as a standalone vault.

- Board identity and claim status:
  <https://github.com/podledges/PodlESP/blob/53ada7be017220a06a9c7e7547fd9a0d83b6d13b/boards/esp32-s3-touch-lcd-1.9/README.md>
- Chip ADC map and caveats:
  <https://github.com/podledges/PodlESP/blob/53ada7be017220a06a9c7e7547fd9a0d83b6d13b/docs/esp32-s3-adc-gpios.md>
- Hardware authorization boundary:
  <https://github.com/podledges/PodlESP/blob/53ada7be017220a06a9c7e7547fd9a0d83b6d13b/docs/board-workflow/README.md>
- Boundary: advertised board memory/revision is unconfirmed. Research brief
  records piezo/parallel-frontend intent and absent electrical sign-off;
  synthesis did not inspect or approve the schematic. Existing firmware is
  not a binding future design.
