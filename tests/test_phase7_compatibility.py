from pathlib import Path
import unittest

import yaml

from validators.validate_compatibility import validate_repository_compatibility


ROOT = Path(__file__).resolve().parents[1]


class Phase7CompatibilityTests(unittest.TestCase):
    def test_required_platform_and_manual_files_exist(self):
        required = [
            "protocols/skill-installation.md",
            "templates/wrappers/wrapper-template.md",
            "templates/wrappers/installation.example.yaml",
            "platforms/claude/README.md",
            "platforms/claude/wrapper-template.md",
            "platforms/claude/mcp-setup.md",
            "platforms/codex/README.md",
            "platforms/codex/wrapper-template.md",
            "platforms/codex/openai-yaml.example",
            "platforms/codex/mcp-setup.md",
            "platforms/hermes/README.md",
            "platforms/hermes/wrapper-template.md",
            "platforms/hermes/mcp-setup.md",
            "docs/agent-compatibility/claude-code.md",
            "docs/agent-compatibility/codex.md",
            "docs/agent-compatibility/hermes.md",
            "docs/testing/e2e/claude-code.md",
            "docs/testing/e2e/codex.md",
            "docs/testing/e2e/hermes.md",
            "validators/validate_compatibility.py",
        ]
        missing = [item for item in required if not (ROOT / item).is_file()]
        self.assertEqual([], missing)

    def test_claude_imports_agents_without_copying_it(self):
        self.assertEqual("@AGENTS.md\n", (ROOT / "CLAUDE.md").read_text(encoding="utf-8"))
        guide = (ROOT / "platforms/claude/README.md").read_text(encoding="utf-8")
        self.assertIn("~/.claude/skills/", guide)
        self.assertIn(".claude/skills/", guide)
        self.assertIn("@AGENTS.md", guide)

    def test_codex_uses_current_agents_and_skill_paths(self):
        guide = (ROOT / "platforms/codex/README.md").read_text(encoding="utf-8")
        self.assertIn("AGENTS.md", guide)
        self.assertIn("~/.agents/skills/", guide)
        self.assertIn(".agents/skills/", guide)
        self.assertIn("legacy", guide.lower())
        self.assertIn("$CODEX_HOME/skills", guide)

    def test_hermes_uses_project_context_and_active_profile(self):
        guide = (ROOT / "platforms/hermes/README.md").read_text(encoding="utf-8")
        self.assertIn("AGENTS.md", guide)
        self.assertIn("active profile", guide.lower())
        self.assertIn("/reload-skills", guide)
        self.assertNotIn(".hermes/skills/<name>", guide)

    def test_wrapper_template_points_to_one_canonical_skill(self):
        wrapper = (ROOT / "templates/wrappers/wrapper-template.md").read_text(encoding="utf-8")
        self.assertIn("{{skill_name}}", wrapper)
        self.assertIn("{{canonical_skill_path}}", wrapper)
        self.assertIn("Verify the file exists", wrapper)
        self.assertNotIn("allowed-tools:", wrapper)

    def test_installation_protocol_refuses_unmanaged_conflicts(self):
        protocol = (ROOT / "protocols/skill-installation.md").read_text(encoding="utf-8")
        self.assertIn("managed_by: prd-agent-kit", protocol)
        self.assertIn("非管理", protocol)
        self.assertIn("禁止覆盖", protocol)
        self.assertIn("managed_copy", protocol)
        self.assertIn("sha256", protocol)

    def test_compatibility_status_remains_honest(self):
        data = yaml.safe_load((ROOT / "compatibility.yaml").read_text(encoding="utf-8"))
        for runtime in ["claude-code", "codex", "hermes"]:
            self.assertEqual("not_run", data["runtimes"][runtime]["e2e"])
            self.assertEqual("documented", data["runtimes"][runtime]["mcp_setup"])

    def test_each_e2e_manual_covers_the_full_manual_flow(self):
        required_terms = [
            "temporary HOME",
            "AGENTS.md",
            "Gate 1",
            "Wrapper",
            "new session",
            "Gate 2",
            "not_run",
        ]
        for runtime in ["claude-code", "codex", "hermes"]:
            text = (ROOT / "docs/testing/e2e" / f"{runtime}.md").read_text(encoding="utf-8")
            for term in required_terms:
                self.assertIn(term, text, f"{runtime} manual missing {term}")

    def test_static_compatibility_validator_passes_repository(self):
        result = validate_repository_compatibility(ROOT)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(3, result["runtimes"])
        self.assertEqual("not_run", result["e2e_status"])


if __name__ == "__main__":
    unittest.main()
