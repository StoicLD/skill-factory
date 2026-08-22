# Bootstrap plan

Status: first portable Skill suite branded, packaged, and validated
Started: 2026-08-11

## Source-tree migration

- The complete maintainable Ten-step-learning source tree now lives under `project/ten-step/` inside the parent Git repository.
- The parent `project/AGENTS.md` and `project/docs/INDEX.md` are thin maps; Ten-step-learning facts remain in this source unit.
- Generated Codex Plugin output remains outside the repository under `../../codex-plugin/` and was not moved into the source tree.

## Completed in initialization

- Created an isolated product repository, Agent Context repository, and non-Git temporary directory.
- Established the portable core and host-adapter boundary.
- Defined the direct-child folder contract for independently distributable skills.
- Added a non-discoverable template, a zero-dependency scaffold command, a validator, and validator tests.
- Added quality gates and a current compatibility matrix.

## First product suite

- Added `ten-step-learning-report` for a complete sourced ten-step HTML artifact.
- Added explicit-only steps 6-9 as four independently installable interactive Skills.
- Added Codex/ChatGPT interface metadata, a self-contained report template, a zero-dependency report validator, consistent checkpoint contracts, and suite behavior tests.
- Recorded trigger, automated, and forward-test evidence in `docs/quality/ten-step-suite-validation.md`.
- Branded the suite as `Ten-step-learning` with the Chinese name `十步学习方法`, five ordered Chinese Skill entries, a wisdom-familiar Plugin logo, and five distinct step icons.
- Added an authoritative clean-build command at `scripts/build_ten_step_learning_plugin.ps1`; it generates the disposable local Marketplace under `../../codex-plugin/ten-step-learning-suite/` and validates the complete Plugin.

## Next product work

1. Reinstall the generated `1.1.0` Plugin from `ten-step-learning-local` in an unrestricted Codex session and confirm the new logo, descriptions, icons, and five named entries in a new task.
2. Forward-test Claude, Cursor, and WorkBuddy/CodeBuddy before claiming behavioral parity.
