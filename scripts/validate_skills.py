#!/usr/bin/env python3
"""Validate canonical portable Agent Skills in this repository."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIELD_PATTERN = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
XML_TAG_PATTERN = re.compile(r"<[^>]+>")
RESERVED_ROOTS = {"docs", "factory", "scripts", "tests"}
FORBIDDEN_SKILL_FILES = {
    "README.md",
    "CHANGELOG.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
}


@dataclass(frozen=True)
class Finding:
    path: Path
    message: str


def scalar_value(raw: str) -> str:
    value = raw.strip()
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid double-quoted YAML scalar: {error.msg}") from error
        if not isinstance(parsed, str):
            raise ValueError("frontmatter values must be strings")
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise ValueError("unterminated single-quoted YAML scalar")
        return value[1:-1].replace("''", "'")
    return value


def parse_skill(path: Path) -> tuple[dict[str, str], list[str], list[Finding]]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as error:
        return {}, [], [Finding(path, f"cannot read UTF-8 text: {error}")]

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines, [Finding(path, "SKILL.md must start with YAML frontmatter delimiter ---")]
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}, lines, [Finding(path, "frontmatter closing delimiter --- is missing")]

    metadata: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:end], start=2):
        if not line.strip():
            continue
        match = FIELD_PATTERN.fullmatch(line)
        if not match:
            findings.append(Finding(path, f"frontmatter line {line_number} must be a one-line scalar"))
            continue
        key, raw_value = match.groups()
        if key in metadata:
            findings.append(Finding(path, f"duplicate frontmatter field: {key}"))
            continue
        try:
            metadata[key] = scalar_value(raw_value)
        except ValueError as error:
            findings.append(Finding(path, f"frontmatter field {key}: {error}"))

    return metadata, lines[end + 1 :], findings


def validate_skill(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_dir = path.parent
    if skill_dir.parent != root:
        findings.append(Finding(path, "skills must be direct child directories of the repository root"))

    metadata, body_lines, parse_findings = parse_skill(path)
    findings.extend(parse_findings)

    unexpected = sorted(set(metadata) - {"name", "description"})
    if unexpected:
        findings.append(
            Finding(path, f"portable frontmatter permits only name and description; found: {', '.join(unexpected)}")
        )

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not name:
        findings.append(Finding(path, "required frontmatter field name is missing or empty"))
    else:
        if len(name) > 64 or not NAME_PATTERN.fullmatch(name):
            findings.append(Finding(path, "name must be 1-64 lowercase letters/digits separated by single hyphens"))
        if name != skill_dir.name:
            findings.append(Finding(path, f"name {name!r} must match parent folder {skill_dir.name!r}"))
        if XML_TAG_PATTERN.search(name):
            findings.append(Finding(path, "name must not contain XML tags"))

    if not description:
        findings.append(Finding(path, "required frontmatter field description is missing or empty"))
    else:
        if len(description) > 1024:
            findings.append(Finding(path, "description exceeds 1024 characters"))
        if XML_TAG_PATTERN.search(description):
            findings.append(Finding(path, "description must not contain XML tags"))

    if not any(line.strip() for line in body_lines):
        findings.append(Finding(path, "Markdown instruction body is empty"))
    if len(body_lines) > 500:
        findings.append(Finding(path, "Markdown instruction body exceeds 500 lines"))

    for forbidden in sorted(FORBIDDEN_SKILL_FILES):
        candidate = skill_dir / forbidden
        if candidate.exists():
            findings.append(Finding(candidate, "auxiliary documentation is forbidden inside a skill"))
    return findings


def validate_repository(root: Path) -> tuple[list[Path], list[Finding]]:
    root = root.resolve()
    findings: list[Finding] = []
    if not root.is_dir():
        return [], [Finding(root, "repository root does not exist or is not a directory")]

    skill_files = sorted(path for path in root.rglob("SKILL.md") if ".git" not in path.parts)
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name in RESERVED_ROOTS:
            continue
        if not (child / "SKILL.md").is_file():
            findings.append(Finding(child, "visible non-reserved root directory must be a skill with SKILL.md"))

    for skill_file in skill_files:
        findings.extend(validate_skill(skill_file, root))
    return skill_files, findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_files, findings = validate_repository(args.root)
    if findings:
        for finding in findings:
            print(f"ERROR {finding.path}: {finding.message}")
        print(f"validation failed: {len(findings)} finding(s), {len(skill_files)} skill(s) inspected")
        return 1
    print(f"validation passed: {len(skill_files)} skill(s) inspected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

