"""Regression tests for portable navigation contracts (standard library only)."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import project_probe as probe


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.write("CLAUDE.md", "[Shared entry](AGENTS.md)")
        self.write("AGENTS.md", "[Docs](docs/INDEX.md)")
        self.write("docs/INDEX.md", "[Design](design/INDEX.md)")
        self.write("docs/design/INDEX.md", "[Model](<My Model.md>)\n[Back](../INDEX.md)")
        self.write("docs/design/My Model.md", "Accepted model.")
        self.contract = {
            "version": 1,
            "docs_root": "docs",
            "map_target": "docs/INDEX.md",
            "required_files": ["CLAUDE.md", "AGENTS.md", "docs/INDEX.md", "docs/design/INDEX.md", "docs/design/My Model.md"],
            "authoritative_docs": ["docs/design/My Model.md"],
            "entrypoints": [
                {"path": "CLAUDE.md", "ordered_links": ["AGENTS.md"]},
                {"path": "AGENTS.md", "ordered_links": ["docs/INDEX.md"]},
            ],
            "index": {"path": "docs/INDEX.md", "ordered_links": ["docs/design/INDEX.md"]},
            "navigation_maps": [{"path": "docs/design/INDEX.md", "ordered_links": ["docs/design/My Model.md"]}],
            "ignored_directories": [],
            "forbid_nested_git": True,
        }

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def failures(self):
        failures = {}
        probe.validate_contract(self.contract, self.root, lambda n, p, d: failures.update({n: d}) if not p else None)
        return failures

    def test_compatibility_entry_and_subindex_with_backlink(self):
        self.assertEqual(self.failures(), {})

    def test_empty_facts_need_no_placeholder(self):
        self.contract["required_files"] = ["CLAUDE.md", "AGENTS.md", "docs/INDEX.md"]
        self.contract["authoritative_docs"] = []
        self.contract["index"]["ordered_links"] = []
        del self.contract["navigation_maps"]
        self.write("docs/INDEX.md", "No accepted fact documents yet.")
        self.assertEqual(self.failures(), {})

    def test_direct_legacy_contract_and_unbounded_maps(self):
        self.contract.pop("navigation_maps")
        self.contract["index"]["ordered_links"] = ["docs/design/My Model.md"]
        self.write("CLAUDE.md", "[Docs](docs/INDEX.md)")
        self.contract["entrypoints"][0]["ordered_links"] = ["docs/INDEX.md"]
        self.write("docs/INDEX.md", "[Model](<design/My Model.md>)\n" + "Navigation note\n" * 250)
        self.write("AGENTS.md", "[Docs](docs/INDEX.md)\n" + "Navigation note\n" * 250)
        self.contract["entrypoints"][1]["max_lines"] = 100
        self.contract["index"]["max_lines"] = 200
        self.assertEqual(self.failures(), {})

    def test_declared_cycle_rejected_even_with_exit(self):
        self.contract["navigation_maps"][0]["ordered_links"].append("docs/INDEX.md")
        self.assertIn("navigation_has_no_loading_cycles", self.failures())

    def test_missing_intermediate_link_rejected(self):
        self.write("docs/INDEX.md", "Design link removed.")
        self.assertIn("document_index_ordered_links_exist", self.failures())

    def test_disconnected_facts_rejected(self):
        self.contract["index"]["ordered_links"] = []
        self.assertIn("navigation_targets_are_reachable", self.failures())

    def test_entry_cannot_skip_common_index(self):
        self.contract["entrypoints"][0]["ordered_links"] = ["docs/design/My Model.md"]
        self.write("CLAUDE.md", "[Fact](<docs/design/My Model.md>)")
        self.assertIn("navigation_targets_are_reachable", self.failures())

    def test_missing_fact_file_rejected(self):
        (self.root / "docs/design/My Model.md").unlink()
        self.assertIn("required_files_exist", self.failures())

    def test_single_document_root_preserved(self):
        self.write("outside.md", "A fact outside the document root.")
        self.contract["required_files"].append("outside.md")
        self.contract["authoritative_docs"].append("outside.md")
        self.assertIn("authoritative_docs_are_scoped", self.failures())

    def test_unknown_fields_and_duplicate_roles_rejected(self):
        self.contract["navigation_maps"][0]["typo"] = True
        self.assertIn("navigation_maps_are_valid", self.failures())
        self.contract["navigation_maps"] = [self.contract["index"]]
        self.assertIn("navigation_maps_are_valid", self.failures())

    def test_cli_success_and_failure_exit_codes(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True, capture_output=True)
        # Contract stays outside the target repository, as the skill requires.
        with tempfile.TemporaryDirectory() as directory:
            contract_path = Path(directory) / "contract.json"
            contract_path.write_text(json.dumps(self.contract), encoding="utf-8")
            command = [sys.executable, "-B", str(Path(probe.__file__)), "validate", "--root", str(self.root), "--contract", str(contract_path)]
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)["ok"])
            self.write("AGENTS.md", "No navigation link.")
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertFalse(json.loads(result.stdout)["ok"])


class MarkdownTests(unittest.TestCase):
    def test_inline_spaces_titles_parentheses_and_encoding(self):
        text = '''[A](<My File.md> "Title") [B](chapter(v2).md)
[C](My%20File.md#section) [D](a\\(b\\).md 'Title')'''
        self.assertEqual(probe.markdown_destinations(text), ["My File.md", "chapter(v2).md", "My%20File.md#section", "a(b).md"])

    def test_full_collapsed_shortcut_references_in_use_order(self):
        text = '''[z]: z.md
[a]: <A File.md> "Title"
[A][a] [z][] [a] [unknown]
[unused]: unused.md
'''
        self.assertEqual(probe.markdown_destinations(text), ["A File.md", "z.md", "A File.md"])

    def test_examples_images_comments_and_escaped_links_are_not_navigation(self):
        text = '''`[code](bad.md)` ![image](bad.png) <!-- [comment](bad.md) -->
```markdown
[fence](bad.md)
```
    [indented](bad.md)
\\[escaped](bad.md)
[real](good.md)
'''
        self.assertEqual(probe.markdown_destinations(text), ["good.md"])

    def test_link_resolution_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "AGENTS.md"
            source.write_text('[a](<My File.md>) [b](My%20File.md) [web](https://example.com) [anchor](#x) [bad](../escape.md) [abs](C:/secret.md)', encoding="utf-8")
            targets, errors = probe.markdown_targets(source, root)
            self.assertEqual(targets, ["My File.md", "My File.md"])
            self.assertEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
