#!/usr/bin/env python3
"""Create a portable Agent Skill as a direct child of a source catalog root."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESOURCE_DIRS = ("scripts", "references", "assets")


def title_from_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def validate_name(name: str) -> None:
    if len(name) > 64 or not NAME_PATTERN.fullmatch(name):
        raise ValueError(
            "name must be 1-64 lowercase ASCII letters/digits separated by single hyphens"
        )


def create_skill(root: Path, name: str, description: str, resources: list[str]) -> Path:
    validate_name(name)
    description = description.strip()
    if not description or len(description) > 1024:
        raise ValueError("description must be 1-1024 characters")
    if re.search(r"<[^>]+>", description):
        raise ValueError("description must not contain XML tags")

    target = root.resolve() / name
    if target.exists():
        raise FileExistsError(f"target already exists: {target}")

    target.mkdir(parents=False)
    for resource in resources:
        (target / resource).mkdir()

    rendered_description = json.dumps(description, ensure_ascii=False)
    body = f"""---
name: {name}
description: {rendered_description}
---

# {title_from_name(name)}

## Workflow

1. Replace this line with the first task-specific imperative step.
2. State required inputs, safe failure behavior, and validation.
3. Reference bundled resources only where the workflow needs them.

## Output

Describe the expected result and concise validation evidence.
"""
    (target / "SKILL.md").write_text(body, encoding="utf-8", newline="\n")
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="portable kebab-case skill name")
    parser.add_argument("--description", required=True, help="what the skill does and when to use it")
    parser.add_argument(
        "--resources",
        nargs="*",
        choices=RESOURCE_DIRS,
        default=[],
        help="optional resource directories to create",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="source catalog root; defaults to the current directory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        target = create_skill(args.root, args.name, args.description, args.resources)
    except (ValueError, FileExistsError, OSError) as error:
        print(f"error: {error}")
        return 1
    print(f"created draft skill: {target}")
    print("customize SKILL.md, add only needed resources, then run scripts/validate_skills.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
