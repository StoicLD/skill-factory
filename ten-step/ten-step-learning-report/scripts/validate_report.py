#!/usr/bin/env python3
"""Validate a generated ten-step learning HTML report."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_IDS = [
    "overview",
    *(f"step-{number}" for number in range(1, 11)),
    "sources",
    "continue-learning",
]
REQUIRED_SKILLS = [
    "$ten-step-06-learning-ladder",
    "$ten-step-07-core-sprint",
    "$ten-step-08-adaptive-exam",
    "$ten-step-09-feynman-loop",
]
PLACEHOLDER_PATTERN = re.compile(r"\{\{[^{}]+\}\}")


def validate_text(text: str) -> list[str]:
    findings: list[str] = []
    lowered = text.lower()
    if "<html" not in lowered or "</html>" not in lowered:
        findings.append("document must contain a complete html element")
    if "<nav" not in lowered:
        findings.append("document must contain navigation")
    for placeholder in sorted(set(PLACEHOLDER_PATTERN.findall(text))):
        findings.append(f"unresolved placeholder: {placeholder}")
    for identifier in REQUIRED_IDS:
        count = len(re.findall(rf'\bid=["\']{re.escape(identifier)}["\']', text))
        if count != 1:
            findings.append(f"id {identifier!r} must occur exactly once; found {count}")
    for skill in REQUIRED_SKILLS:
        if skill not in text:
            findings.append(f"missing continuation invocation: {skill}")
    if re.search(r"<script\b[^>]*\bsrc\s*=", text, re.IGNORECASE):
        findings.append("external script dependencies are not allowed")
    if re.search(r'''<link\b[^>]*\brel\s*=\s*["']stylesheet["']''', text, re.IGNORECASE):
        findings.append("external stylesheet dependencies are not allowed")
    return findings


def validate_path(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return [f"cannot read UTF-8 HTML: {error}"]
    return validate_text(text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="generated HTML report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = validate_path(args.report)
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}")
        return 1
    print(f"report validation passed: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
