# Repository layout

The Ten-step-learning source unit is both a catalog of portable skills and the source of the factory rules that govern them. It is stored under the parent `project/` Git repository.

```text
ten-step/
├── AGENTS.md
├── docs/                  # Product specifications, decisions, plans, quality gates
├── factory/
│   ├── templates/         # Non-discoverable Skill templates; no file named SKILL.md
│   └── plugins/           # Authoritative Plugin manifests and brand assets
├── scripts/               # Factory commands
├── tests/                 # Factory command tests
└── <skill-name>/          # One independently distributable skill
    ├── SKILL.md           # Required
    ├── scripts/           # Optional deterministic helpers
    ├── references/        # Optional on-demand context
    ├── assets/            # Optional output resources
    └── agents/
        └── openai.yaml    # Optional Codex/ChatGPT adapter
```

## Boundaries

- A real skill lives directly under this source root. Nested category folders are not used because not every host discovers nested skills consistently.
- A skill must remain independently copyable: copying its directory must copy everything it needs.
- A skill must not depend on this repository's `docs/`, `factory/`, `scripts/`, or sibling skills at runtime.
- Shared facts may be used while authoring, but release artifacts must carry their own required references or scripts.
- Factory templates use names such as `SKILL.md.template` so hosts do not accidentally discover them as runnable skills.
- Plugin distribution sources live under `factory/plugins/`; generated marketplaces and installable Plugin trees live outside the parent Git repository under `../../codex-plugin/` and may be deleted before every build.

Reserved root directories are `docs`, `factory`, `scripts`, and `tests`. Any other visible root directory is treated as a skill candidate by the local validator.
