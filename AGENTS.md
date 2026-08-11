# Skill Factory product entry

This repository is the authoritative source for portable Agent Skills. Product facts in this repository override remembered conversation state and the sibling Agent Context repository.

## Start or resume work

1. Read `docs/INDEX.md` and select only the documents relevant to the request.
2. Read `docs/plans/active/` to establish current state, next work, and completion criteria.
3. Inspect the target Skill directory and current Git status before editing.
4. If resuming from a handoff, verify its referenced product revision and paths. Treat stale handoffs as hints, not authority.
5. Update the authoritative specification, plan, decision, implementation, or validation evidence when product state changes.

## Repository boundaries

- Read `docs/INDEX.md` before changing standards or layout.
- Store each real skill directly at `<repo>/<skill-name>/SKILL.md`; the folder name must equal the frontmatter `name`.
- Reserved infrastructure directories are `docs/`, `factory/`, `scripts/`, and `tests/`; they are not skills.
- Keep portable `SKILL.md` frontmatter to `name` and `description`. Put host-specific configuration in optional adapter files such as `agents/openai.yaml`.
- Keep `SKILL.md` concise and imperative. Put optional executable helpers in `scripts/`, on-demand documentation in `references/`, and output resources in `assets/`.
- Do not add `README.md`, changelogs, installation guides, quick references, or empty placeholder directories inside a skill.
- Product facts, accepted specifications, plans, decisions, and validation evidence belong in this repository, not in the sibling Agent Context repository.

## Validation and completion

Run from this repository root:

```powershell
python -B scripts/validate_skills.py .
python -B -m unittest discover -s tests
```

A Skill is not ready merely because its files parse. Apply the manual gates in `docs/quality/validation.md`, including trigger examples, safe failure behavior, script checks, and forward testing for every claimed host.

## Navigation

- Repository layout: `docs/architecture/repository-layout.md`
- Portable contract: `docs/specs/portable-skill-standard.md`
- Host compatibility: `docs/specs/platform-compatibility.md`
- Quality gates: `docs/quality/validation.md`
- Current plan: `docs/plans/active/bootstrap.md`
- New Skill scaffold: `scripts/new_skill.py`
- Canonical validator: `scripts/validate_skills.py`
