# Portable Skill standard

Status: accepted  
Last verified: 2026-08-11

This repository targets the common Agent Skills contract supported by Claude, Codex/ChatGPT, Cursor, and WorkBuddy/CodeBuddy. The open specification is the baseline; host-specific features are optional adapters, never portable-core requirements.

## Required artifact

Every skill is one directory named with lowercase ASCII letters, digits, and single hyphens. It contains a `SKILL.md` file whose YAML frontmatter has exactly two fields:

```markdown
---
name: example-skill
description: Explain what the skill does and the concrete tasks or phrases that should trigger it.
---

# Example skill

Write concise, imperative instructions here.
```

Requirements:

- `name` is 1–64 characters, matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`, and exactly matches the parent directory.
- `description` is 1–1024 characters, states both capability and triggering context, front-loads the key use case, and contains no XML tags.
- The Markdown body is non-empty, imperative, and under 500 lines.
- Keep the frontmatter to `name` and `description` for portable skills. The wider open standard permits optional fields, but host support and semantics vary.

## Optional resources

Create only resources that the workflow actually needs:

- `scripts/`: deterministic, repeatable code. Make dependencies explicit, handle errors, and test the scripts.
- `references/`: detailed documentation loaded only when needed. Link each relevant reference directly from `SKILL.md`; avoid deep reference chains.
- `assets/`: templates, icons, fonts, examples, or boilerplate used in outputs rather than loaded as instructions.
- `agents/openai.yaml`: optional Codex/ChatGPT UI, dependency, and invocation metadata. It must not be required by the portable workflow.

Do not add auxiliary documentation such as `README.md`, `CHANGELOG.md`, `INSTALLATION_GUIDE.md`, or `QUICK_REFERENCE.md` inside a skill. Put authoring and release guidance in the repository's `docs/` tree.

## Progressive disclosure

Design for three levels of loading:

1. Every host sees `name` and `description` to decide whether the skill applies.
2. The host loads the full `SKILL.md` only after activation.
3. The host reads references or runs scripts only when the active workflow requires them.

Keep essential procedure in `SKILL.md`; move detailed schemas, variants, and long examples into directly linked references. Do not duplicate the same fact across both.

## Authoring workflow

1. Define concrete user prompts that should and should not trigger the skill.
2. Identify reusable scripts, references, and assets; omit directories without a real use.
3. Create `<source-root>/<skill-name>/SKILL.md` with the portable frontmatter.
4. Write instructions for another capable agent, using imperative language and explicit inputs, outputs, failure states, and validation.
5. Add host adapters only when they improve that host without changing portable behavior.
6. Run structural validation, script tests, realistic trigger checks, and at least one forward task before release.

## Primary references

- [Agent Skills open specification](https://agentskills.io/specification)
- [Claude Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Cursor: Agent Skills](https://cursor.com/docs/skills.md)
- [WorkBuddy/CodeBuddy: Skills](https://www.workbuddy.ai/docs/ide/Features/Skills)
