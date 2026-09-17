---
title: "Primary sources and evidence boundaries"
report_date: "2026-09-17"
access_date: "2026-09-17"
status: "Source register for the four-report synthesis"
---

# Primary sources and evidence boundaries

[Overview and provenance](README.md) | [Comparisons](evidence.md) |
[Piezo and ADC](piezo-and-adc.md) | [Experiments](experiments.md)

Sources were consulted on **2026-09-17**. Publications have their own dates
below. Core numbers come from full primary papers or code, not popularity,
search-result counts or agreement between scouts. These remain author-reported
results unless explicitly identified otherwise; none of the four reports
independently replicated the systems. DOI and author-linked repository URLs may serve as
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
  STM32F407, CMSIS FFT, electret input and piano/generated-tone tests. Broad
  Grok also retrieved the abstract through Semantic Scholar: duration assumes
  a supplied time signature; “good results” remains unquantified.
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

## S22

**José Luis Navarro Hernández, Ixchel Dayanara Mercado Fong and Jorge Arturo
Pardiñas Mir, ITESO, August 2022: Detection of musical notes using a polyphonic
pitch tracking embedded system.** Embedded-systems specialization graduation
report, not a peer-reviewed conference paper.

- Institutional identifier: <https://hdl.handle.net/11117/8208>
- Primary PDF: <https://rei.iteso.mx/bitstreams/90fcf30b-caea-4dcf-be12-31c66ac10260/download>
- NXP MIMXRT1010EVKHUG, Rev. 0, 2019-07-30: <https://www.farnell.com/datasheets/2860193.pdf>
- Support: primary report fully read by Broad Astra; PDF p. 5 rendered to
  confirm violin A4/F5, with hardware/dataflow on pp. 3-5. NXP guide Table 1,
  sections 2.4/2.6, through indexed text, supports 128 Mbit flash, MIMXRT1011,
  WM8960 and microphone; direct guide download timed out.
- Boundary: 492,675 cycles is task compute after 64 ms blocks, with beat-based
  reporting. Two violin notes, not a scored general-piano event stream. Used
  RAM, complete cost and external response unknown. No open implementation found.
- Report PDF SHA-256: `cf13f734be4c2301b65ca51c7c2f2255167c2e43d2676d08929073cddb557ec2`.

## S23

**Ariana Haghighi, Jeff Nan, Tiffany Chou, Cornell Chord Identifier, Fall 2022.**
Chou and Nan, “Identifying Musical Chords,” Circuit Cellar issue 402, January
2024, web dated 2024-08-05. Distinct from S2's transcriber.

- Primary course report: <https://ece4760.github.io/Projects/Fall2022/ah677_jjn48_tlc234/index.html>
- Author article: <https://circuitcellar.com/research-design-hub/projects/identifying-musical-chords/>
- Support: hardware/software/results sections and article, both also read in
  synthesis. Article confirms 2048 samples at 5 kHz. Course report confirms
  48 MHz, triad types, 100 BPM test, one-second serial thread and timbre limits.
- Boundary: three peak-derived pitches/chord name, not note-event transcription.
  Tested synth and simulated instrument sounds are not a controlled live
  acoustic-piano corpus. Approximately 0.6 s chord hold is not E2E measurement.
  No memory high-water or complete BOM price established.

## S24

**Arnaud Dessein, Arshia Cont, Guillaume Lemaitre, ISMIR 2010, pp. 489-494:
Real-time Polyphonic Music Transcription with Non-negative Matrix Factorization
and Beta-divergence.**

- Original paper: <https://archives.ismir.net/ismir2010/paper/000083.pdf>
- DOI: <https://doi.org/10.5281/zenodo.1414823>
- Different MIREX extended abstract: <http://articles.ircam.fr/textes/Dessein10b/index.pdf>
- Support: original full text, sections 5.1/5.2, Tables 1/2: 25 MAPS excerpts,
  65.5% frame / 71.1% onset / 28.2% onset+offset F, MATLAB laptop simulation.
- Boundary: not MCU; 4 GB installed RAM, not usage. No measured E2E latency.
  Historical MIREX evaluator cited, not replaced here with current defaults.
  Extended abstract has different tuning; its settings are not mixed with scores.
- Original PDF SHA-256: `8b3c1c3f52bff87d6ae4fe167428bf4fce96f75af2c390a6b40f654d8d6f648f`.

## S25

**Rodrigo Schramm, Federico Visi, André Brasil, Marcelo Johann, NIME 2018,
pp. 120-125: A polyphonic pitch tracking embedded system for rapid instrument
augmentation.**

- Proceedings: <https://www.nime.org/proceedings/2018/nime2018_paper0027.pdf>
- Support: full paper, section 2.3 Pi3/Raspbian; sections 3.1-3.4 instruments,
  approximate 45/70 ms input-to-resynthesized-output traces and failure cases.
- Boundary: Linux SBC, not MCU. 256-hop case required laptop. Errors accepted
  for augmentation, no F1; no piano piezo/air comparison or peak RAM/total cost.
- PDF SHA-256: `ec28a02b935a49e9b88c6842366ac00bd1bf47689bf7e008b153715e4dc10f2f`.

## S26

**Stanislaw Pusep, Pianolizer**, source revision
`735a7f2036a7e72d16b193acf1281f354bbdda24`; repository from 2021, demo 2022.

- Repository: <https://github.com/creaktive/pianolizer/tree/735a7f2036a7e72d16b193acf1281f354bbdda24>
- Spectral history: <https://github.com/creaktive/pianolizer/blob/735a7f2036a7e72d16b193acf1281f354bbdda24/cpp/pianolizer.hpp#L430-L455>
- Note averaging: <https://github.com/creaktive/pianolizer/blob/735a7f2036a7e72d16b193acf1281f354bbdda24/misc/transcribe2midi.pl#L128-L175>
- Global scaling/full buffering: <https://github.com/creaktive/pianolizer/blob/735a7f2036a7e72d16b193acf1281f354bbdda24/misc/transcribe2midi.pl#L235-L284>
- Support: README, analysis header, exporter and tree inspected as source only.
- Boundary: live analysis distinct from whole-file MIDI export. Arduino drives
  LEDs, not inference. No event F1 or MCU deployment; spectral cents error is
  not transcription accuracy. Video metadata only, no watched-demo claims.

## S27

**翟景瞳 (Zhai Jingtong), 王玲 (Wang Ling), 杜秀伟 (Du Xiuwei), AET,
2009-04-14: 基于DSP的便携式音乐分析仪的设计与实现.**

- Full article: <http://www.chinaaet.com/article/13611>
- Support: also read during synthesis. Sections 2/3 identify TMS320VC5502,
  ARM S3C44B0X, CS53L21, DSP memory and algorithms; section 4 reports
  synthesized A440, 57 of 60 notes, duration errors 13.5 ms mean / 25.6 ms max.
- Boundary: DSP+ARM, not MCU-only; pitch follows segmented notes. 95% is the
  authors' count ratio, not a full false-positive-aware event metric. Actual
  clock, full-system memory, complete cost, E2E and acoustic-piano polyphony unknown.

## S28

**Casio Computer Co., Ltd., US5202528A: Electronic musical instrument with a
note detector capable of detecting a plurality of notes sounded simultaneously.**
Filed 1991-04-10, granted 1993-04-13.

- Patent: <https://patents.google.com/patent/US5202528A/en>
- Broad Grok's text source: <https://www.freepatentsonline.com/5202528.html>
- Support: DSP/CPU filter-bank disclosure, per-note envelopes and voice
  allocation; Broad Grok read primary patent text. Synthesis retrieved Google
  Patents after the other text extractor returned 404.
- Boundary: **disclosure, not proof of productization, build or shipment**.
  No independently validated piano corpus, latency, used RAM or system cost.
  The broad report's stronger productization wording is explicitly superseded.

## S29

**Doill Jung / Amusetec, US6856923B2: Method for analyzing music using sounds
instruments.** Priority 2000-12-05, international filing 2001-12-03, US grant
2005-02-15.

- <https://patents.google.com/patent/US6856923B2/en>
- Support: Figures 9-18 and pseudocode 1/2 describe piano templates,
  subtraction, score-informed mode and dynamics/pedal ideas; illustrative
  Young Chang grand recordings analyzed on Sony Windows notebook.
- Boundary: not an MCU deployment or scored product. “Monophonic pitches” here
  can mean individual pitches extracted from a mixture, not necessarily a
  monophonic task. Hop/localization error is not output latency. No legal opinion.

## S30

**Kevin Vaca, Archit Gajjar, Xiaokun Yang, ISVLSI 2019, pp. 378-384:
Real-Time Automatic Music Transcription (AMT) with Zync FPGA.** Related paper:
Vaca, Mitchell M. Jefferies, Yang, ISMCR 2019, “An Open Audio Processing Platform
with Zync FPGA.” Title spelling retained; platform family is Zynq.

- ISVLSI: <https://doi.org/10.1109/ISVLSI.2019.00075>
- ISMCR: <https://doi.org/10.1109/ISMCR47492.2019.8955662>
- Support: abstracts/index/author listing only; Broad Grok obtained Semantic
  Scholar abstracts. ISMCR reports 90% open-chord accuracy and ~250 ms sampling
  latency. ISVLSI describes PL capture and ARM PS feature/pattern processing.
- Boundary: full PDFs not recovered, instruments/protocol/memory/cost unknown;
  FPGA SoC and phone display, not MCU or piano note-event F1.

## S31

**Nansong Wu, Brandon Fong, Xiao-Kun Yang, Kaiman Zeng, IEEE AIIoT 2025:
Hardware-Accelerated Music Transcription on the Cloud via FPGA Implementation.**

- <https://doi.org/10.1109/AIIoT65859.2025.11105340>
- Support: abstract via Semantic Scholar in Broad Grok: FPGA web service,
  chord sequences 680 ms versus Python 2.5 s, authors' open-source claim.
- Boundary: abstract only, code not retrieved; request/workload timing boundary,
  accuracy, full memory/cost unknown. Not on-device MCU transcription. Related
  2021 Fong thesis PDF returned 403, not silently promoted to inspected evidence.

## S32

**GUT-9, 2023 Chinese competition K project**, source revision
`7b4f83a183e2241dcc81d512d2c4d955e08cc87a`.

- <https://github.com/GUT-9/2023TI-K-_ESP32_Arduino/tree/7b4f83a183e2241dcc81d512d2c4d955e08cc87a>
- <https://github.com/GUT-9/2023TI-K-_ESP32_Arduino/blob/7b4f83a183e2241dcc81d512d2c4d955e08cc87a/FFT_Board/shiyin/shiyin.ino>
- Competition task reproduction: <https://www.eetree.cn/task/31>
- Support: five struck water cups, two ESP32 design; source releases only FFT
  board with 2048 samples, requested 10 kHz, MajorPeak and serial frequency.
- Boundary: source inspected, never executed. Award is author claim, not
  independently checked. Main-board code absent; no piano polyphony benchmark.

## S33

**Jay Park, Nuwan Singhal, Sarayu Suresh, Illinois ECE445 Project 98,
Piano Visualizer Design Document, 2026-02-27.**

- <https://courses.grainger.illinois.edu/ece445/getfile.asp?id=25484>
- Support: high-level requirements, microphone/tolerance/cost sections,
  proposed STM32F446RET6, explicitly one audio note at a time, separate MIDI
  input. USD 95.70 proposed parts, separate labor estimate.
- Boundary: design, not final performance or validated BOM. Conflicting 200/50 ms
  targets; FFT-only estimates are not measured input/output response.
- PDF SHA-256: `91874c8fdcba1a238a0359743a834a44b9509d1e6c3797a7d3a7b27c628671ba`.

## S34

**Manufacturer products**, live pages observed 2026-09-17.

- Sonuus G2M FAQ: <https://sonuus.com/products_g2m_faq.html>
- Algoriffix Transkr V4: <https://www.algoriffix.com/>
- Vochlea Dubler: <https://vochlea.com/products/dubler-studio-kit-2>
- Support: G2M V3 (introduced 2016) explicitly monophonic, USD 99.99 box;
  Transkr advertises polyphonic piano, Windows/macOS standalone/plugin,
  regular USD 129 license only. Dubler voice-to-MIDI/chord generation is a
  wrong-task screen, not piano multipitch recognition.
- Boundary: vendor claims, no controlled piano benchmark, peak RAM or numeric
  full-path latency established; software “standalone” is not embedded hardware.

## S35

**Cycfi multichannel pitch-to-MIDI proposal and James Jones dulcimer account.**

- Cycfi snapshot: <https://github.com/cycfi/hz_audio_to_midi/tree/0b37fa87dc607136a2a3585601cf25b41a51bce0>
- Jones, 2017-04-12, updated 2018-04-07: <https://www.jamesjonesinstruments.com/post/a-midi-hammered-dulcimer-1>
- Support: Cycfi README/tree only contains license, README and image; eight
  input audio proposal, no converter firmware. Jones describes stalled
  fixed-pitch string-trigger integration using Livid Brain V2.
- Boundary: divided-pickup pitch inference, assigned-note piezo triggers and
  key sensing are distinct. Neither demonstrates mixed-audio piano AMT or a
  completed priced system. Personal correspondence is not reproduced.

## S36

**Additional screened families**, retained without promoting wrong-task results.

- Pelinski, Diaz, Benito Temprano, McPherson, NIME 2023, Bela neural pipeline:
  <https://nime.org/proceedings/2023/nime2023_22.pdf>
- Sofronievski / Gerazov, Scorpiano, arXiv 2021-08-24:
  <https://arxiv.org/abs/2108.10689>
- Krause / Sebastian, Union College capstone, cover 2019-03-21, hosted 2020:
  <https://bpb-us-w2.wpmucdn.com/muse.union.edu/dist/0/590/files/2020/03/499-Final-Design-Paper-Ian-Krause-Raphael-Sebastian-II.pdf>
- Support: Broad Grok retrieved Bela and Scorpiano papers; respectively Linux
  piezo-capable NN tooling and desktop monophonic piano-file transcription.
  Broad Astra inspected Union architecture/results/BOM/conclusion: Pi4 Linux,
  monophonic electric guitar, conflicting dates and aggregate scores.
- Boundary: none is MCU piano polyphony; no new piano-system cost, memory or
  latency inferred from these adjacent tasks. Union's questionable totals are
  excluded from comparative accuracy/cost anchors.

## Source access and retained records

Public links identify evidence; structural URL validation is not a claim that
every endpoint remains reachable. Some publisher/DOI extractors returned 404,
IEEE full papers were unavailable, Fong thesis returned 403, and no video was
watched for either broad report. Exact-title multilingual discovery is not an
exhaustive live Scholar citation sweep. No paywall or TLS bypass was used.

Each [source record](README.md#research-provenance-and-reconciled-findings)
identifies scope, report date, original fingerprint, contributions, corrections
and access limits. Curated records exclude private host paths and operational
logs; they are not verbatim reports or new independent measurements.
