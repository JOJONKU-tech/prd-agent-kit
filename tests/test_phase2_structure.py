from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Phase2StructureTests(unittest.TestCase):
    def test_required_phase2_files_exist(self):
        required = [
            "protocols/onboarding.md",
            "protocols/source-priority.md",
            "protocols/confirmation-gates.md",
            "skills/prd-knowledge-engineering/SKILL.md",
            "skills/prd-knowledge-engineering/references/onboarding.md",
            "skills/prd-knowledge-engineering/references/source-priority.md",
            "skills/prd-knowledge-engineering/references/confirmation-gates.md",
            "templates/knowledge-base/_meta/SCHEMA.md",
            "templates/knowledge-base/_meta/config.yaml",
            "templates/knowledge-base/_meta/router.yaml",
            "templates/knowledge-base/_meta/index.md",
            "templates/knowledge-base/_meta/log.md",
            "templates/knowledge-base/_shared/index.md",
            "templates/knowledge-base/domains/_template/domain.yaml",
            "templates/knowledge-base/domains/_template/index.md",
            "templates/knowledge-base/domains/_template/sources/manifest.yaml",
            "templates/knowledge-base/domains/_template/business/overview.md",
            "templates/knowledge-base/domains/_template/sop/router.yaml",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual([], missing)

    def test_onboarding_first_message_only_requests_sources(self):
        text = (ROOT / "protocols/onboarding.md").read_text(encoding="utf-8")
        match = re.search(
            r"<!-- FIRST_MESSAGE_START -->(.*?)<!-- FIRST_MESSAGE_END -->",
            text,
            re.S,
        )
        if match is None:
            self.fail("onboarding protocol needs a testable first-message block")
        first_message = match.group(1)
        self.assertIn("文件、目录或在线文档链接", first_message)
        for forbidden in ["知识库路径", "复制", "MCP", "Claude", "Codex", "Hermes", "模板"]:
            self.assertNotIn(forbidden, first_message)

    def test_onboarding_enforces_three_question_limit_and_gate1(self):
        text = (ROOT / "protocols/onboarding.md").read_text(encoding="utf-8")
        self.assertIn("每轮最多3个问题", text)
        self.assertIn("Gate 1前不得写入知识库", text)
        self.assertIn("无资料模式", text)
        self.assertIn("unknown", text)

    def test_source_priority_separates_business_and_format_sources(self):
        text = (ROOT / "protocols/source-priority.md").read_text(encoding="utf-8")
        self.assertIn("业务事实优先级", text)
        self.assertIn("格式规范优先级", text)
        self.assertIn("不得混用", text)
        self.assertIn("冲突", text)

    def test_confirmation_protocol_defines_two_content_gates(self):
        text = (ROOT / "protocols/confirmation-gates.md").read_text(encoding="utf-8")
        self.assertIn("Gate 1", text)
        self.assertIn("Gate 2", text)
        self.assertIn("plan_sha256", text)
        self.assertIn("确认失效", text)

    def test_core_skill_uses_only_shared_frontmatter_fields(self):
        text = (ROOT / "skills/prd-knowledge-engineering/SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        keys = {
            line.split(":", 1)[0].strip()
            for line in frontmatter.splitlines()
            if ":" in line and not line.startswith(" ")
        }
        self.assertEqual({"name", "description"}, keys)
        self.assertIn("protocols/onboarding.md", text)
        self.assertIn("protocols/source-priority.md", text)
        self.assertIn("protocols/confirmation-gates.md", text)

    def test_core_skill_local_references_exist(self):
        skill_dir = ROOT / "skills/prd-knowledge-engineering"
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        refs = re.findall(r"`(references/[^`]+\.md)`", text)
        self.assertGreaterEqual(len(refs), 3)
        missing = [ref for ref in refs if not (skill_dir / ref).is_file()]
        self.assertEqual([], missing)

    def test_minimal_domain_template_does_not_invent_business_facts(self):
        overview = (
            ROOT / "templates/knowledge-base/domains/_template/business/overview.md"
        ).read_text(encoding="utf-8")
        self.assertIn("status: draft", overview)
        self.assertIn("confidence: low", overview)
        self.assertIn("unknown", overview)
        self.assertNotIn("示例客户", overview)


if __name__ == "__main__":
    unittest.main()
