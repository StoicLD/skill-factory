from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_skills.py"
SPEC = importlib.util.spec_from_file_location("validate_skills", MODULE_PATH)
assert SPEC and SPEC.loader
validate_skills = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_skills
SPEC.loader.exec_module(validate_skills)


def write_skill(root: Path, folder: str, *, name: str | None = None, extra: str = "") -> Path:
    skill_dir = root / folder
    skill_dir.mkdir(parents=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(
        "---\n"
        f"name: {name or folder}\n"
        "description: Performs a test workflow. Use when validating a portable skill.\n"
        f"{extra}"
        "---\n\n"
        "# Test skill\n\n"
        "1. Validate the input.\n",
        encoding="utf-8",
    )
    return skill_path


class ValidateRepositoryTests(unittest.TestCase):
    def test_empty_factory_repository_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for reserved in validate_skills.RESERVED_ROOTS:
                (root / reserved).mkdir()
            skill_files, findings = validate_skills.validate_repository(root)
            self.assertEqual([], skill_files)
            self.assertEqual([], findings)

    def test_valid_direct_child_skill_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "example-skill")
            skill_files, findings = validate_skills.validate_repository(root)
            self.assertEqual(1, len(skill_files))
            self.assertEqual([], findings)

    def test_folder_and_name_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "example-skill", name="different-name")
            _, findings = validate_skills.validate_repository(root)
            self.assertTrue(any("must match parent folder" in finding.message for finding in findings))

    def test_extra_frontmatter_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "example-skill", extra="allowed-tools: Read\n")
            _, findings = validate_skills.validate_repository(root)
            self.assertTrue(any("permits only name and description" in finding.message for finding in findings))

    def test_nested_skill_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "category/example-skill", name="example-skill")
            _, findings = validate_skills.validate_repository(root)
            self.assertTrue(any("direct child directories" in finding.message for finding in findings))

    def test_auxiliary_readme_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill_path = write_skill(root, "example-skill")
            (skill_path.parent / "README.md").write_text("extra", encoding="utf-8")
            _, findings = validate_skills.validate_repository(root)
            self.assertTrue(any("auxiliary documentation" in finding.message for finding in findings))


if __name__ == "__main__":
    unittest.main()
