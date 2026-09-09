# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Use the shared pinned shell in `flake.nix`; run the bounded `nix flake check` command in `README.md` after environment or firmware changes.
- For board-facing work, read that model's `boards/<model-slug>/README.md` first. Keep chip targets separate from board pin, memory, peripheral, and revision claims.
- Treat builds as compilation evidence only. Hardware access and claims require explicit authorization and evidence from the exact board's primary sources.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
