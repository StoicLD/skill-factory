from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUITE = {
    "ten-step-learning-report": ("十步学习 · 完整报告", True),
    "ten-step-06-learning-ladder": ("十步学习 · 06 学习阶梯", False),
    "ten-step-07-core-sprint": ("十步学习 · 07 核心冲刺", False),
    "ten-step-08-adaptive-exam": ("十步学习 · 08 自适应考试", False),
    "ten-step-09-feynman-loop": ("十步学习 · 09 费曼循环", False),
}
CHECKPOINT_FIELDS = [
    "Topic",
    "Goal and target depth",
    "Learner profile",
    "Source materials used",
    "Current explicit Skill",
    "Current step and status",
    "Demonstrated capabilities",
    "Unresolved misconceptions or gaps",
    "Next deliberate action",
    "Recommended explicit invocation",
]


VALIDATOR_PATH = ROOT / "ten-step-learning-report" / "scripts" / "validate_report.py"
SPEC = importlib.util.spec_from_file_location("ten_step_report_validator", VALIDATOR_PATH)
assert SPEC and SPEC.loader
report_validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = report_validator
SPEC.loader.exec_module(report_validator)


class TenStepSuiteTests(unittest.TestCase):
    def test_five_skill_entries_have_unique_openai_metadata(self) -> None:
        display_names: set[str] = set()
        for name, (display_name, implicit) in SUITE.items():
            skill_dir = ROOT / name
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            metadata = (skill_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")
            self.assertIn(f"name: {name}", skill_text)
            self.assertIn(f'display_name: "{display_name}"', metadata)
            self.assertIn(f"${name}", metadata)
            self.assertIn(
                f"allow_implicit_invocation: {str(implicit).lower()}", metadata
            )
            short_match = re.search(r'^  short_description: "([^"]+)"$', metadata, re.MULTILINE)
            self.assertIsNotNone(short_match)
            assert short_match
            self.assertGreaterEqual(len(short_match.group(1)), 25)
            self.assertLessEqual(len(short_match.group(1)), 64)
            self.assertEqual(1, len(re.findall(r"^  default_prompt:", metadata, re.MULTILINE)))
            display_names.add(display_name)
        self.assertEqual(len(SUITE), len(display_names))

    def test_interactive_skills_require_explicit_invocation(self) -> None:
        for name in SUITE:
            if name == "ten-step-learning-report":
                continue
            text = (ROOT / name / "SKILL.md").read_text(encoding="utf-8")
            frontmatter = text.split("---", 2)[1]
            self.assertRegex(frontmatter, r"Use only when the user explicitly")
            self.assertIn(f"Run only after explicit selection or mention of `${name}`", text)
            self.assertIn("Never auto", text)

    def test_checkpoint_schema_is_consistent(self) -> None:
        for name in SUITE:
            if name == "ten-step-learning-report":
                continue
            text = (ROOT / name / "references" / "checkpoint.md").read_text(
                encoding="utf-8"
            )
            for field in CHECKPOINT_FIELDS:
                self.assertEqual(1, len(re.findall(rf"^- {re.escape(field)}:", text, re.MULTILINE)))

    def test_adaptive_exam_protects_answers(self) -> None:
        text = (
            ROOT / "ten-step-08-adaptive-exam" / "SKILL.md"
        ).read_text(encoding="utf-8")
        ask_position = text.index("Ask exactly one question")
        wait_position = text.index("then wait", ask_position)
        reveal_position = text.index("do not reveal", wait_position)
        score_position = text.index("After each answer", reveal_position)
        self.assertLess(ask_position, wait_position)
        self.assertLess(wait_position, reveal_position)
        self.assertLess(reveal_position, score_position)

    def test_feynman_loop_requires_learner_first(self) -> None:
        text = (
            ROOT / "ten-step-09-feynman-loop" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Require an explanation before teaching", text)
        self.assertIn("Then wait", text)
        self.assertIn("Do not provide a standard explanation", text)

    def test_report_template_exposes_only_expected_placeholders(self) -> None:
        template = (
            ROOT / "ten-step-learning-report" / "assets" / "report-template.html"
        ).read_text(encoding="utf-8")
        placeholders = set(re.findall(r"\{\{[^{}]+\}\}", template))
        self.assertEqual(
            {
                "{{LANG}}",
                "{{TOPIC}}",
                "{{PROFILE}}",
                "{{GENERATED_AT}}",
                "{{METHOD_SUMMARY}}",
                "{{NAV_ITEMS}}",
                "{{STEP_SECTIONS}}",
                "{{SOURCES}}",
                "{{NEXT_ACTIONS}}",
            },
            placeholders,
        )

    def test_report_validator_accepts_complete_self_contained_html(self) -> None:
        identifiers = [
            "overview",
            *(f"step-{number}" for number in range(1, 11)),
            "sources",
            "continue-learning",
        ]
        body = "".join(f'<section id="{identifier}"></section>' for identifier in identifiers)
        skills = " ".join(f"${name}" for name in SUITE if name != "ten-step-learning-report")
        html = f"<html><body><nav></nav>{body}{skills}</body></html>"
        self.assertEqual([], report_validator.validate_text(html))

    def test_report_validator_rejects_unresolved_or_external_content(self) -> None:
        findings = report_validator.validate_text(
            '<html><body><nav></nav>{{TOPIC}}<script src="x.js"></script></body></html>'
        )
        self.assertTrue(any("unresolved placeholder" in finding for finding in findings))
        self.assertTrue(any("external script" in finding for finding in findings))
        self.assertTrue(any("step-1" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
