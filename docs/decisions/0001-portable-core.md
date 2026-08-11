# ADR 0001: Keep the canonical Skill core vendor-neutral

Status: accepted  
Date: 2026-08-11

## Context

Claude, Codex, Cursor, and WorkBuddy/CodeBuddy share the folder-based Agent Skills model, but expose different optional frontmatter fields, discovery locations, UI metadata, permissions, and invocation controls.

## Decision

Canonical skills use only the common contract: a self-contained directory, `SKILL.md`, `name`, `description`, and optional `scripts/`, `references/`, and `assets/`. Platform-only behavior stays in a separate file that other hosts ignore safely or in a separately generated host variant.

Skills live directly under the product repository root. This gives every skill an independent folder while avoiding reliance on recursive category discovery.

## Consequences

- A canonical skill can be copied between supported hosts without rewriting its core instructions.
- Some host conveniences require an adapter or variant rather than a single enriched frontmatter block.
- The repository validator is intentionally stricter than the full open specification: it rejects extra frontmatter in the canonical artifact.
- Compatibility claims require periodic re-verification against primary host documentation.

