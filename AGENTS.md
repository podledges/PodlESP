# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Use the shared pinned shell in `flake.nix`; run the bounded `nix flake check` command in `README.md` after environment or firmware changes.
- The two lab board folders are `boards/esp32-s3-touch-lcd-1.9/` and `boards/esp32-cp2102-micro/`; each model's README is authoritative for its hardware notes and claim status. For board-facing work, open the matching README first, and never mix chip target, pin/ADC, USB, memory, peripheral, or revision facts across models.
- Treat builds as compilation evidence only. Hardware access and claims require explicit authorization and evidence from the exact board's primary sources.
- For flash/reset or board self-test work, follow `docs/board-workflow/README.md`; its commands are dry-run by default and each real cycle needs fresh scoped approval.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
