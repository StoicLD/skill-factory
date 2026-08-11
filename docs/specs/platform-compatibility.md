# Platform compatibility

Last verified: 2026-08-11

The canonical skill directory remains host-neutral. Installation is a deployment concern: copy or link the same skill directory into the host's discovery location.

| Host | Project-level discovery target | Portable core | Optional extension |
|---|---|---|---|
| Claude Code | `.claude/skills/<skill-name>/` | `SKILL.md`, `scripts/`, `references/`, `assets/` | Avoid Claude-only frontmatter in a portable artifact |
| Codex | `.agents/skills/<skill-name>/` | Open Agent Skills structure | `agents/openai.yaml` for UI, dependencies, and invocation policy |
| Cursor | `.cursor/skills/<skill-name>/` | Open Agent Skills structure | Cursor-only frontmatter such as `paths` must be maintained as a separate variant, not added to the portable core |
| WorkBuddy/CodeBuddy | `.codebuddy/skills/<skill-name>/` | `SKILL.md`, `scripts/`, `references/`, `assets/` | WorkBuddy-only invocation, context, model, or hook fields require a separate variant |

## Portability policy

- The canonical artifact uses only `name` and `description` in `SKILL.md` frontmatter.
- Platform-specific metadata may be added only when other hosts safely ignore the file. `agents/openai.yaml` meets this rule because it is separate from `SKILL.md`.
- Platform-specific frontmatter changes require a generated or maintained host variant outside the canonical skill directory; they are not committed into the portable core.
- Scripts must not assume a host-specific environment variable or tool name unless the requirement is stated in `SKILL.md` and an equivalent path exists for every supported host.
- “Compatible” means the host can discover, activate, and execute the core workflow. It does not promise identical UI, implicit-trigger ranking, permissions, or tool availability.

Before publishing, re-check the host documentation because discovery paths and extension fields can evolve:

- [Claude Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Cursor Agent Skills](https://cursor.com/docs/skills.md)
- [WorkBuddy/CodeBuddy Skills](https://www.workbuddy.ai/docs/ide/Features/Skills)

