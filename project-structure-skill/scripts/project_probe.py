#!/usr/bin/env python3
"""Inspect or validate a single-repository, docs-mapped Agent project."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Sequence
from urllib.parse import unquote, urlsplit


CONTRACT_KEYS = {
    "version",
    "docs_root",
    "map_target",
    "required_files",
    "authoritative_docs",
    "entrypoints",
    "index",
    "ignored_directories",
    "forbid_nested_git",
}
ENTRY_KEYS = {"path", "ordered_links"}
OPTIONAL_CONTRACT_KEYS = {"navigation_maps"}
# Accepted only for compatibility with previously generated temporary contracts.
LEGACY_ENTRY_KEYS = {"max_lines"}
WINDOWS_ABSOLUTE_PATTERN = re.compile(r"^[A-Za-z]:[/\\]")


def markdown_destinations(text: str) -> list[str]:
    """Read inline/reference links, excluding code, comments and images.

    This lightweight reader covers the Markdown navigation forms documented in
    validation.md; it is not a full Markdown renderer.
    """
    lines: list[str] = []
    fence = ""
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = ""
            lines.append("\n")
        elif marker:
            fence = marker[1]
            lines.append("\n")
        elif line.startswith(("    ", "\t")):
            lines.append("\n")
        else:
            lines.append(line)
    text = re.sub(r"<!--.*?-->", "", "".join(lines), flags=re.S)

    def destination(start: int) -> tuple[str | None, int]:
        while start < len(text) and text[start].isspace():
            start += 1
        angled = start < len(text) and text[start] == "<"
        if angled:
            start += 1
        result: list[str] = []
        depth = 0
        pos = start
        while pos < len(text):
            char = text[pos]
            if char == "\\" and pos + 1 < len(text) and text[pos + 1] in r"\`*_{}[]()#+-.!<>":
                result.append(text[pos + 1])
                pos += 2
                continue
            if angled:
                if char == ">":
                    return html.unescape("".join(result)), pos + 1
                if char in "\r\n<":
                    return None, pos
            else:
                if char.isspace() or (char == ")" and depth == 0):
                    break
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
            result.append(char)
            pos += 1
        if angled or depth:
            return None, pos
        return html.unescape("".join(result)), pos

    def label_key(value: str) -> str:
        return " ".join(value.split()).casefold()

    references: dict[str, str] = {}
    definition_spans: dict[int, int] = {}
    for match in re.finditer(r"(?m)^ {0,3}\[([^\]\n]+)\]:[ \t]*", text):
        target, end = destination(match.end())
        if target is not None:
            references.setdefault(label_key(match[1]), target)
            line_end = text.find("\n", end)
            definition_spans[match.start()] = len(text) if line_end < 0 else line_end + 1

    targets: list[str] = []
    pos = 0
    while pos < len(text):
        if pos in definition_spans:
            pos = definition_spans[pos]
            continue
        if text[pos] == "\\":
            pos += 2
            continue
        if text[pos] == "`":
            run = re.match(r"`+", text[pos:])[0]
            closing = re.search(r"(?<!`)" + re.escape(run) + r"(?!`)", text[pos + len(run):])
            pos = pos + len(run) + closing.end() if closing else pos + len(run)
            continue
        image = text.startswith("![", pos)
        opening = pos + 1 if image else pos
        if text[opening] != "[":
            pos += 1
            continue
        end = opening + 1
        depth = 1
        while end < len(text) and depth:
            if text[end] == "\\":
                end += 2
                continue
            if text[end] == "[":
                depth += 1
            elif text[end] == "]":
                depth -= 1
            end += 1
        if depth:
            pos += 1
            continue
        label = text[opening + 1:end - 1]
        target = None
        if text[end:end + 1] == "(":
            target, tail = destination(end + 1)
            closing = re.match(r'''\s*(?:"[^"\n]*"|'[^'\n]*'|\([^\n]*?\))?\s*\)''', text[tail:])
            if closing:
                end = tail + closing.end()
            else:
                target = None
        elif text[end:end + 1] == "[":
            closing = text.find("]", end + 1)
            if closing >= 0:
                target = references.get(label_key(text[end + 1:closing] or label))
                end = closing + 1
        else:
            target = references.get(label_key(label))
        if target is not None and not image:
            targets.append(target)
        pos = end
    return targets


@dataclass(frozen=True)
class GitInfo:
    available: bool
    top_level: str | None
    branch: str | None
    has_commits: bool | None
    remote_count: int | None


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None


def git_info(root: Path) -> GitInfo:
    top = run_git(root, "rev-parse", "--show-toplevel")
    if top is None:
        return GitInfo(False, None, None, None, None)
    if top.returncode != 0:
        return GitInfo(True, None, None, None, None)

    branch_result = run_git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    branch = (
        branch_result.stdout.strip()
        if branch_result is not None and branch_result.returncode == 0
        else None
    )
    commits_result = run_git(root, "rev-parse", "--verify", "HEAD")
    has_commits = commits_result is not None and commits_result.returncode == 0
    remotes_result = run_git(root, "remote")
    remote_count = (
        len([line for line in remotes_result.stdout.splitlines() if line.strip()])
        if remotes_result is not None and remotes_result.returncode == 0
        else None
    )
    return GitInfo(
        True,
        top.stdout.strip(),
        branch,
        has_commits,
        remote_count,
    )


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def normalize_relative_path(raw: Any) -> str | None:
    if not isinstance(raw, str):
        return None
    value = raw.strip().replace("\\", "/")
    if not value or value.startswith("/") or WINDOWS_ABSOLUTE_PATTERN.match(value):
        return None
    raw_parts = value.split("/")
    if not raw_parts or any(part in {"", ".", ".."} for part in raw_parts):
        return None
    parts = PurePosixPath(value).parts
    return PurePosixPath(*parts).as_posix()


def unique_paths(raw: Any, label: str) -> tuple[list[str], list[str]]:
    if not isinstance(raw, list):
        return [], [f"{label} must be a list"]
    values: list[str] = []
    errors: list[str] = []
    for item in raw:
        normalized = normalize_relative_path(item)
        if normalized is None:
            errors.append(f"{label} contains unsafe path {item!r}")
        else:
            values.append(normalized)
    folded = [value.casefold() for value in values]
    if len(folded) != len(set(folded)):
        errors.append(f"{label} contains duplicate or case-colliding paths")
    return values, errors


def resolve_inside(root: Path, relative: str) -> Path | None:
    candidate = (root / Path(relative)).resolve()
    return candidate if is_relative_to(candidate, root) else None


def markdown_targets(source_path: Path, repository_root: Path) -> tuple[list[str], list[str]]:
    try:
        text = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return [], [str(error)]

    targets: list[str] = []
    errors: list[str] = []
    for raw in markdown_destinations(text):
        if WINDOWS_ABSOLUTE_PATTERN.match(raw) or raw.startswith("\\"):
            errors.append(f"absolute local link is not portable: {raw!r}")
            continue
        try:
            parsed = urlsplit(raw)
        except ValueError as error:
            errors.append(f"invalid link {raw!r}: {error}")
            continue
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        decoded = unquote(parsed.path).replace("\\", "/")
        if decoded.startswith("/") or WINDOWS_ABSOLUTE_PATTERN.match(decoded):
            errors.append(f"absolute local link is not portable: {raw!r}")
            continue
        candidate = (source_path.parent / Path(decoded)).resolve()
        if not is_relative_to(candidate, repository_root):
            errors.append(f"link escapes repository: {raw!r}")
            continue
        targets.append(candidate.relative_to(repository_root).as_posix())
    return targets, errors


def contains_subsequence(actual: list[str], expected: list[str]) -> bool:
    if not expected:
        return True
    index = 0
    for value in actual:
        if value.casefold() == expected[index].casefold():
            index += 1
            if index == len(expected):
                return True
    return False


def find_nested_git_markers(root: Path, max_depth: int | None = None) -> tuple[list[str], list[str]]:
    markers: list[str] = []
    errors: list[str] = []
    root = root.resolve()
    def record_walk_error(error: OSError) -> None:
        errors.append(str(error))

    for current, directories, files in os.walk(
        root,
        followlinks=False,
        onerror=record_walk_error,
    ):
        current_path = Path(current)
        try:
            depth = len(current_path.relative_to(root).parts)
        except ValueError:
            continue
        if max_depth is not None and depth >= max_depth:
            directories[:] = []
        if current_path == root:
            directories[:] = [name for name in directories if name != ".git"]
            continue
        if ".git" in directories:
            marker = current_path / ".git"
            markers.append(marker.relative_to(root).as_posix() + "/")
            directories.remove(".git")
        if ".git" in files:
            marker = current_path / ".git"
            markers.append(marker.relative_to(root).as_posix())
        inaccessible: list[str] = []
        for name in list(directories):
            path = current_path / name
            try:
                if path.is_symlink():
                    directories.remove(name)
            except OSError as error:
                inaccessible.append(f"{path}: {error}")
                directories.remove(name)
        errors.extend(inaccessible)
    return sorted(markers), errors


def visible_paths(root: Path, max_depth: int) -> list[str]:
    results: list[str] = []
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        depth = len(current_path.relative_to(root).parts)
        directories[:] = [name for name in directories if name != ".git"]
        if depth >= max_depth:
            directories[:] = []
        for name in sorted(directories):
            results.append((current_path / name).relative_to(root).as_posix() + "/")
        for name in sorted(files):
            if current_path == root and name == ".git":
                continue
            results.append((current_path / name).relative_to(root).as_posix())
    return sorted(results)


def load_contract(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return None, str(error)
    if not isinstance(data, dict):
        return None, "contract root must be an object"
    return data, ""


def parse_map(
    raw: Any,
    label: str,
    required_set: set[str],
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if (
        not isinstance(raw, dict)
        or not ENTRY_KEYS.issubset(raw)
        or set(raw) - ENTRY_KEYS - LEGACY_ENTRY_KEYS
    ):
        return None, [f"{label} must contain {sorted(ENTRY_KEYS)}; only legacy max_lines is additionally accepted"]
    path = normalize_relative_path(raw.get("path"))
    if path is None:
        errors.append(f"{label}.path is unsafe")
    elif path.casefold() not in required_set:
        errors.append(f"{label}.path is not in required_files")
    links, link_errors = unique_paths(raw.get("ordered_links"), f"{label}.ordered_links")
    errors.extend(link_errors)
    for link in links:
        if link.casefold() not in required_set:
            errors.append(f"{label}.ordered_links path is not in required_files: {link}")
    if errors:
        return None, errors
    return {"path": path, "ordered_links": links}, []


def validate_map(
    spec: dict[str, Any],
    root: Path,
    add: Callable[[str, bool, str], None],
    check_prefix: str,
) -> None:
    source = resolve_inside(root, spec["path"])
    if source is None or not source.is_file():
        add(f"{check_prefix}_exists", False, spec["path"])
        return
    add(f"{check_prefix}_exists", True, spec["path"])
    actual, link_errors = markdown_targets(source, root)
    add(f"{check_prefix}_links_are_portable", not link_errors, json.dumps(link_errors))
    add(
        f"{check_prefix}_ordered_links_exist",
        contains_subsequence(actual, spec["ordered_links"]),
        json.dumps({"expected": spec["ordered_links"], "actual": actual}),
    )


def validate_contract(
    contract: dict[str, Any],
    root: Path,
    add: Callable[[str, bool, str], None],
) -> None:
    unknown = sorted(set(contract) - CONTRACT_KEYS - OPTIONAL_CONTRACT_KEYS)
    missing = sorted(CONTRACT_KEYS - set(contract))
    add("contract_keys_are_exact", not unknown and not missing, json.dumps({"unknown": unknown, "missing": missing}))
    add("contract_version_is_supported", contract.get("version") == 1, repr(contract.get("version")))

    required, required_errors = unique_paths(contract.get("required_files"), "required_files")
    authoritative, authoritative_errors = unique_paths(contract.get("authoritative_docs"), "authoritative_docs")
    ignored, ignored_errors = unique_paths(contract.get("ignored_directories"), "ignored_directories")
    path_errors = required_errors + authoritative_errors + ignored_errors
    add("contract_paths_are_safe_and_unique", not path_errors, json.dumps(path_errors))
    required_set = {value.casefold() for value in required}

    docs_root = normalize_relative_path(contract.get("docs_root"))
    map_target = normalize_relative_path(contract.get("map_target"))
    add("contract_docs_root_is_safe", docs_root is not None, repr(contract.get("docs_root")))
    add("contract_map_target_is_safe", map_target is not None, repr(contract.get("map_target")))

    missing_files: list[str] = []
    escaped_files: list[str] = []
    for relative in required:
        candidate = resolve_inside(root, relative)
        if candidate is None:
            escaped_files.append(relative)
        elif not candidate.is_file():
            missing_files.append(relative)
    add("required_files_stay_in_repository", not escaped_files, json.dumps(escaped_files))
    add("required_files_exist", not missing_files, json.dumps(missing_files))

    authority_errors: list[str] = []
    for relative in authoritative:
        if relative.casefold() not in required_set:
            authority_errors.append(f"not required: {relative}")
        if docs_root is not None:
            relative_path = PurePosixPath(relative)
            docs_path = PurePosixPath(docs_root)
            if relative_path == docs_path or docs_path not in relative_path.parents:
                authority_errors.append(f"outside docs_root: {relative}")
        if map_target is not None and relative.casefold() == map_target.casefold():
            authority_errors.append(f"map_target cannot be an authoritative fact document: {relative}")
    add("authoritative_docs_are_scoped", not authority_errors, json.dumps(authority_errors))

    raw_entries = contract.get("entrypoints")
    entry_specs: list[dict[str, Any]] = []
    entry_errors: list[str] = []
    if not isinstance(raw_entries, list) or not raw_entries:
        entry_errors.append("entrypoints must be a non-empty list")
    else:
        for index, raw_entry in enumerate(raw_entries):
            parsed, errors = parse_map(raw_entry, f"entrypoints[{index}]", required_set)
            entry_errors.extend(errors)
            if parsed is not None:
                entry_specs.append(parsed)
    folded_entries = [entry["path"].casefold() for entry in entry_specs]
    if len(folded_entries) != len(set(folded_entries)):
        entry_errors.append("entrypoint paths duplicate or case-collide")
    add("contract_entrypoints_are_valid", not entry_errors, json.dumps(entry_errors))

    index_spec, index_errors = parse_map(contract.get("index"), "index", required_set)
    add("contract_index_is_valid", not index_errors, json.dumps(index_errors))

    common_map_errors: list[str] = []
    if map_target is not None:
        if map_target.casefold() not in required_set:
            common_map_errors.append("map_target is not in required_files")
        if docs_root is not None:
            target_path = PurePosixPath(map_target)
            docs_path = PurePosixPath(docs_root)
            if target_path == docs_path or docs_path not in target_path.parents:
                common_map_errors.append("map_target is outside docs_root")
        if index_spec is not None and index_spec["path"].casefold() != map_target.casefold():
            common_map_errors.append("index.path does not equal map_target")
    add("common_document_map_is_valid", not common_map_errors, json.dumps(common_map_errors))

    for index, entry in enumerate(entry_specs):
        validate_map(entry, root, add, f"entrypoint_{index}")
    if index_spec is not None:
        validate_map(index_spec, root, add, "document_index")

    navigation_specs: list[dict[str, Any]] = []
    navigation_errors: list[str] = []
    raw_navigation = contract.get("navigation_maps", [])
    if not isinstance(raw_navigation, list):
        navigation_errors.append("navigation_maps must be a list")
    else:
        for index, raw_map in enumerate(raw_navigation):
            parsed, errors = parse_map(raw_map, f"navigation_maps[{index}]", required_set)
            navigation_errors.extend(errors)
            if parsed is not None:
                navigation_specs.append(parsed)
                validate_map(parsed, root, add, f"navigation_map_{index}")
    maps = entry_specs + ([index_spec] if index_spec else []) + navigation_specs
    map_paths = [spec["path"].casefold() for spec in maps]
    if len(map_paths) != len(set(map_paths)):
        navigation_errors.append("map paths duplicate or case-collide across roles")
    if set(map_paths) & {path.casefold() for path in authoritative}:
        navigation_errors.append("a navigation map cannot also be an authoritative fact document")
    add("navigation_maps_are_valid", not navigation_errors, json.dumps(navigation_errors))
    # Only declared forward reading links form the graph. Ordinary backlinks
    # and cross-references are not mandatory loading dependencies.
    graph = {spec["path"].casefold(): [p.casefold() for p in spec["ordered_links"]] for spec in maps}

    def reachable(start: str) -> set[str]:
        visited: set[str] = set()
        pending = [start]
        while pending:
            current = pending.pop()
            if current not in visited:
                visited.add(current)
                pending.extend(graph.get(current, []))
        return visited

    unreachable: list[str] = []
    if map_target is not None:
        for entry in entry_specs:
            if map_target.casefold() not in reachable(entry["path"].casefold()):
                unreachable.append(f"entrypoint cannot reach map_target: {entry['path']}")
        index_reachable = reachable(map_target.casefold())
        unreachable.extend(f"fact unreachable from map_target: {path}" for path in authoritative if path.casefold() not in index_reachable)
    add("navigation_targets_are_reachable", not unreachable, json.dumps(unreachable))

    indegrees = dict.fromkeys(graph, 0)
    for targets in graph.values():
        for target in targets:
            if target in indegrees:
                indegrees[target] += 1
    pending = [path for path, degree in indegrees.items() if degree == 0]
    while pending:
        current = pending.pop()
        for target in graph[current]:
            if target in indegrees:
                indegrees[target] -= 1
                if indegrees[target] == 0:
                    pending.append(target)
    cyclic = [path for path, degree in indegrees.items() if degree > 0]
    add("navigation_has_no_loading_cycles", not cyclic, json.dumps({"cycle_or_blocked_maps": cyclic}))

    ignore_failures: list[str] = []
    for relative in ignored:
        probe = f"{relative.rstrip('/')}/.project-probe"
        result = run_git(root, "check-ignore", "--quiet", "--no-index", "--", probe)
        if result is None or result.returncode != 0:
            ignore_failures.append(relative)
    add("ignored_directories_are_mechanically_ignored", not ignore_failures, json.dumps(ignore_failures))

    forbid_nested = contract.get("forbid_nested_git")
    add("contract_nested_git_flag_is_boolean", isinstance(forbid_nested, bool), repr(forbid_nested))
    if forbid_nested is True:
        markers, scan_errors = find_nested_git_markers(root)
        add("nested_git_scan_completed", not scan_errors, json.dumps(scan_errors))
        add("no_nested_git_markers", not markers, json.dumps(markers))


def inspect_repository(root: Path, max_depth: int) -> dict[str, Any]:
    resolved = root.resolve()
    markers, scan_errors = find_nested_git_markers(resolved, max_depth=None)
    return {
        "root": str(resolved),
        "exists": resolved.is_dir(),
        "git": asdict(git_info(resolved)),
        "nested_git_markers": markers,
        "scan_errors": scan_errors,
        "visible_paths": visible_paths(resolved, max_depth) if resolved.is_dir() else [],
    }


def validate_repository(
    root: Path,
    contract_path: Path | None,
    expect_branch: str | None,
    expect_no_commits: bool,
    expect_no_remotes: bool,
) -> dict[str, Any]:
    resolved = root.resolve()
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    info = git_info(resolved)
    add("root_exists", resolved.is_dir(), str(resolved))
    add("git_available", info.available, "git executable must be available")
    detected_top = Path(info.top_level).resolve() if info.top_level else None
    add("root_is_git_top_level", detected_top == resolved, f"detected={detected_top}")

    if expect_branch is not None:
        add("branch_matches", info.branch == expect_branch, f"expected={expect_branch}; detected={info.branch}")
    if expect_no_commits:
        add("repository_has_no_commits", info.has_commits is False, repr(info.has_commits))
    if expect_no_remotes:
        add("repository_has_no_remotes", info.remote_count == 0, repr(info.remote_count))

    if contract_path is not None:
        contract, error = load_contract(contract_path.resolve())
        add("contract_loaded", contract is not None, error or str(contract_path.resolve()))
        if contract is not None:
            validate_contract(contract, resolved, add)

    return {
        "ok": all(check["passed"] for check in checks),
        "root": str(resolved),
        "git": asdict(info),
        "checks": checks,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="inspect a repository without modifying it")
    inspect_parser.add_argument("--root", required=True, type=Path)
    inspect_parser.add_argument("--max-depth", type=int, default=3)

    validate_parser = subparsers.add_parser("validate", help="validate repository structure")
    validate_parser.add_argument("--root", required=True, type=Path)
    validate_parser.add_argument("--contract", type=Path)
    validate_parser.add_argument("--expect-branch")
    validate_parser.add_argument("--expect-no-commits", action="store_true")
    validate_parser.add_argument("--expect-no-remotes", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "inspect":
        result = inspect_repository(args.root, args.max_depth)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    result = validate_repository(
        root=args.root,
        contract_path=args.contract,
        expect_branch=args.expect_branch,
        expect_no_commits=args.expect_no_commits,
        expect_no_remotes=args.expect_no_remotes,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        raise SystemExit(130)
