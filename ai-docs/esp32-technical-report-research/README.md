# ESP32 technical-report research

Curated public copies of a completed report-writing investigation and the three scout reports it directly cites. These are historical research records, not PodlESP implementation or hardware-validation results. Dates below are the reports' own research/observation dates.

| Report | Originating project | Date | Scope |
|---|---|---:|---|
| [Technical implementation report guidance](technical-implementation-report-guidance.md) | **PodlePianoDSP32** (UREX piano/piezo research), revision `28a68dba91b650da836af7b215bdd03c77ec0c7a` | 2026-09-09 | Source-backed guidance and evidence audit. Proposed experiments and illustrative targets are explicitly not measured results. |
| [PodlePianoDSP32 / UREX scout](podlepianodsp32-urex-scout.md) | **PodlePianoDSP32**, revision `87cc89777111f5514cc008369f7a67e39b9f673a` | 2026-08-24 | Repository and private-local-evidence inventory for the UREX research direction. |
| [PodlePianoDSP32 embedded-C agent / knowledge-base scout](podlepianodsp32-embedded-c-agent-kb-scout.md) | **PodlePianoDSP32**, revision `87cc89777111f5514cc008369f7a67e39b9f673a` | 2026-09-02 | Proposed agent, knowledge-base, and no-hardware validation workflow; includes attributed software-test observations from that scout only. |
| [PodleRex ESP32 board and buying scout](podlerex-esp32-board-buying-scout.md) | **PodleRex**, revisions `54e90f7` and `9636eeb` | 2026-09-06 | Original-ESP32 compatibility and time-sensitive Singapore storefront observations. It concerns a different repository and hardware target. |

## Evidence boundary

PodlePianoDSP32 and PodleRex are separate projects from PodlESP. Their pins, boards, firmware paths, build observations, purchasing recommendations, proposed experiments, and performance targets must not be treated as PodlESP facts. The main report itself identifies conflicts between the predecessor reports and later source inspection; later, target-matched primary evidence takes precedence. For current PodlESP board facts and validation rules, use this repository's root [`README.md`](../../README.md) and board-specific documentation.

## Publication edits

Technical content and evidence-status language were retained. The public copies make only portability/privacy edits:

- private fleet report paths were replaced with relative links to the four files in this directory;
- disposable worktree and private Windows archive paths were generalized;
- a personal application filename and filesystem metadata were omitted (its contents were never inspected or used as evidence);
- fleet task-runner completion commands, internal runtime/provider details, transient browser tracking identifiers, and an exact delivery postcode were removed or generalized; and
- one reference to an unrelated, unpublished fleet report was removed rather than publishing or implying inclusion of that report.

No credentials or secrets were found. Storefront price, stock, shipping, software-version, and “stable/latest” statements remain dated observations and may now be stale.
