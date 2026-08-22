from __future__ import annotations

import importlib.util
import json
import re
import struct
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUITE = {
    "ten-step-learning-report": ("十步学习方法 · 01–10 完整学习报告", True),
    "ten-step-06-learning-ladder": ("十步学习方法 · 06 水平诊断与学习阶梯", False),
    "ten-step-07-core-sprint": ("十步学习方法 · 07 核心 20% 微课冲刺", False),
    "ten-step-08-adaptive-exam": ("十步学习方法 · 08 自适应逐题考试", False),
    "ten-step-09-feynman-loop": ("十步学习方法 · 09 费曼解释纠错", False),
}
PLUGIN_SOURCE = ROOT / "factory" / "plugins" / "ten-step-learning-suite"
PLUGIN_TEMPLATE = PLUGIN_SOURCE / "plugin.json.template"
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
            self.assertIn('icon_small: "./assets/step-icon.svg"', metadata)
            self.assertIn('icon_large: "./assets/step-icon.svg"', metadata)
            self.assertIn('brand_color: "#7567F8"', metadata)
            self.assertTrue((skill_dir / "assets" / "step-icon.svg").is_file())
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
            self.assertIn("仅当用户通过 /skills 选择或显式调用", frontmatter)
            self.assertIn(f"Run only after explicit selection or mention of `${name}`", text)
            self.assertIn("Never auto", text)

    def test_display_names_sort_in_learning_order(self) -> None:
        names = [display_name for display_name, _ in SUITE.values()]
        self.assertEqual(names, sorted(names))
        self.assertRegex(names[0], r"01–10")
        self.assertRegex(names[1], r"06")
        self.assertRegex(names[2], r"07")
        self.assertRegex(names[3], r"08")
        self.assertRegex(names[4], r"09")

    def test_plugin_brand_metadata_and_assets(self) -> None:
        manifest = json.loads(PLUGIN_TEMPLATE.read_text(encoding="utf-8"))
        interface = manifest["interface"]
        self.assertEqual("ten-step-learning-suite", manifest["name"])
        self.assertEqual("1.1.0", manifest["version"])
        self.assertEqual("Ten-step-learning", interface["displayName"])
        self.assertIn("十步学习方法", interface["shortDescription"])
        self.assertIn("01 多视角调研", interface["longDescription"])
        self.assertIn("10 速查表", interface["longDescription"])
        retired_brand = "十步" + "智学"
        self.assertNotIn(retired_brand, PLUGIN_TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual("#7567F8", interface["brandColor"])
        self.assertEqual(3, len(interface["defaultPrompt"]))
        self.assertEqual(
            {
                "$ten-step-learning-report",
                "$ten-step-06-learning-ladder",
                "$ten-step-09-feynman-loop",
            },
            {
                prompt.split(maxsplit=1)[0]
                for prompt in interface["defaultPrompt"]
            },
        )
        for key, expected_name in {
            "composerIcon": "icon.png",
            "logo": "logo.png",
            "logoDark": "logo-dark.png",
        }.items():
            asset_path = interface[key]
            self.assertTrue(asset_path.startswith("./assets/"))
            self.assertEqual(expected_name, Path(asset_path).name)
            self.assertTrue((PLUGIN_SOURCE / asset_path.removeprefix("./")).is_file())

    def test_plugin_png_dimensions(self) -> None:
        def png_dimensions(path: Path) -> tuple[int, int]:
            data = path.read_bytes()[:24]
            self.assertEqual(b"\x89PNG\r\n\x1a\n", data[:8])
            self.assertEqual(b"IHDR", data[12:16])
            return struct.unpack(">II", data[16:24])

        self.assertEqual((512, 512), png_dimensions(PLUGIN_SOURCE / "assets" / "logo.png"))
        self.assertEqual(
            (512, 512), png_dimensions(PLUGIN_SOURCE / "assets" / "logo-dark.png")
        )
        self.assertEqual((128, 128), png_dimensions(PLUGIN_SOURCE / "assets" / "icon.png"))

    def test_authoritative_build_script_is_clean_and_versioned(self) -> None:
        script = (ROOT / "scripts" / "build_ten_step_learning_plugin.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("[string]$Version = '1.1.0'", script)
        self.assertIn("Remove-Item -LiteralPath $outputRoot -Recurse -Force", script)
        self.assertIn("Unsafe output path", script)
        self.assertIn("plugin.json.template", script)
        self.assertIn("$requiredBrandAssets", script)

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
        self.assertIn("先让学习者解释，再开始教学", text)
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
