# Skill Factory repository map

This Git repository contains independently maintained Skill source units. Keep this file as a map; product facts, implementation, tests, plans, and validation evidence belong in the selected source unit.

## Start or resume work

1. Read the [repository source map](docs/INDEX.md).
2. Identify the source unit that owns the task.
3. Read that unit's native entry and documentation index before editing.
4. Check Git status from this repository root, then run validation from the source unit named by its entry.

## Current source units

- Ten-step-learning: read [ten-step/AGENTS.md](ten-step/AGENTS.md), then [ten-step/docs/INDEX.md](ten-step/docs/INDEX.md).

## Boundaries

- `project/` is the only Git root for the source units stored here; do not create nested repositories.
- Generated Codex Plugin and Marketplace output lives outside this repository under `../codex-plugin/` and is not source.
- Do not store product facts in this root map. Add a source unit to `docs/INDEX.md`, then keep its facts under that unit.
- Do not move files between source units or change Git history, remotes, worktrees, or generated-output boundaries without explicit owner approval.
