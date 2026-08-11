# Validation and release gates

Run from the product repository root:

```powershell
python scripts/validate_skills.py .
python -m unittest discover -s tests
```

## Automated structural gate

The local validator checks:

- every discovered `SKILL.md` belongs to a direct child skill directory;
- every visible, non-reserved root directory contains `SKILL.md`;
- folder and `name` match and use portable kebab-case naming;
- frontmatter contains exactly `name` and `description`;
- descriptions are non-empty, within 1024 characters, and free of XML tags;
- the body is non-empty and no longer than 500 lines;
- common auxiliary files forbidden by the factory contract are absent.

## Manual semantic gate

Before release, also verify:

- at least three positive trigger prompts and two negative trigger prompts;
- instructions identify inputs, outputs, success conditions, and safe failure behavior;
- no secrets, machine-specific absolute paths, or unstated external dependencies;
- scripts have representative executable tests and useful error messages;
- references are loaded conditionally and are linked directly from `SKILL.md`;
- a realistic forward task succeeds in each claimed host, or the untested host is clearly marked unverified;
- platform extensions do not alter portable-core behavior.

Structural validation is necessary but not sufficient for a release claim.

