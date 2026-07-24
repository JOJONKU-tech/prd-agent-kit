import base64
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

from validators.release_check import validate_release_readiness


ROOT = Path(__file__).resolve().parents[1]


class Phase9ReleaseReadinessTests(unittest.TestCase):
    def test_required_release_files_exist(self):
        required = [
            "docs/getting-started.md",
            "docs/troubleshooting.md",
            "docs/release-checklist.md",
            "SECURITY.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            ".github/workflows/ci.yml",
            "validators/release_check.py",
        ]
        missing = [item for item in required if not (ROOT / item).is_file()]
        self.assertEqual([], missing)

    def test_readmes_link_to_release_documentation(self):
        expected = [
            "docs/getting-started.md",
            "docs/troubleshooting.md",
            "docs/release-checklist.md",
            "SECURITY.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
        ]
        for name in ["README.md", "README.en.md"]:
            text = (ROOT / name).read_text(encoding="utf-8")
            for target in expected:
                self.assertIn(target, text, f"{name} missing {target}")

    def test_getting_started_is_short_and_agent_first(self):
        text = (ROOT / "docs/getting-started.md").read_text(encoding="utf-8")
        self.assertIn("请阅读AGENTS.md，并初始化我的PRD工作流。", text)
        self.assertIn("Gate 1", text)
        self.assertIn("Gate 2", text)
        self.assertLessEqual(len(text.splitlines()), 220)
        self.assertNotIn("必须先理解完整架构", text)

    def test_troubleshooting_covers_actual_validator_failures(self):
        text = (ROOT / "docs/troubleshooting.md").read_text(encoding="utf-8")
        for term in [
            "always_read",
            "x-",
            "Required",
            "plan_sha256",
            "published_unverified",
            "DOCX",
            "MCP",
        ]:
            self.assertIn(term, text)

    def test_security_and_contributing_docs_are_actionable(self):
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("private vulnerability reporting", security.lower())
        self.assertIn("Do not open a public issue", security)
        self.assertIn("credentials", security.lower())
        contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("validators/release_check.py --run-tests", contributing)
        self.assertIn("unittest discover", contributing)
        self.assertIn("No fixed renderer", contributing)

    def test_changelog_does_not_claim_an_unpublished_release(self):
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## [Unreleased]", text)
        self.assertNotRegex(text, r"## \[0\.1\.0\] - \d{4}-\d{2}-\d{2}")

    def test_architecture_status_matches_repository(self):
        text = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
        self.assertNotIn("Repository Not Created", text)
        self.assertIn("V1 Implemented", text)
        self.assertIn("### Phase 9：文档与发布准备", text)

    def test_repository_visibility_claim_is_private_release_preparation(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        english = (ROOT / "README.en.md").read_text(encoding="utf-8")
        architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
        self.assertIn("Private release preparation", readme)
        self.assertIn("private release preparation", english)
        self.assertIn("可见性：Private", architecture)
        self.assertNotIn("Public development", readme)

    def test_ci_runs_release_check_and_full_tests(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("validators/release_check.py --run-tests", workflow)
        self.assertIn("requirements-dev.txt", workflow)
        self.assertIn("pull_request", workflow)
        self.assertNotIn("secrets.", workflow)

    def test_compatibility_claims_remain_honest(self):
        data = yaml.safe_load((ROOT / "compatibility.yaml").read_text(encoding="utf-8"))
        for item in data["runtimes"].values():
            self.assertEqual("not_run", item["e2e"])

    def test_release_readiness_validator_passes_repository(self):
        result = validate_release_readiness(ROOT)
        self.assertTrue(result["valid"], result["errors"])
        self.assertGreaterEqual(result["checked_files"], 100)
        self.assertEqual(3, result["runtimes"])

    def test_release_readiness_rejects_extra_private_terms(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sample.md").write_text("CONFIDENTIAL_SENTINEL", encoding="utf-8")
            result = validate_release_readiness(root, extra_forbidden_terms=["CONFIDENTIAL_SENTINEL"])
            self.assertFalse(result["valid"])
            self.assertTrue(any("forbidden term" in error for error in result["errors"]))
    def test_release_readiness_rejects_extra_term_in_reachable_git_history(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            commands = [
                ["git", "init", "-q"],
                ["git", "config", "user.email", "release-check@example.test"],
                ["git", "config", "user.name", "Release Check"],
            ]
            for command in commands:
                subprocess.run(command, cwd=root, check=True, capture_output=True)
            sensitive = root / "temporary.md"
            split_term = "HISTORY_SPLIT_SENTINEL"
            encoded_term = "HISTORY_ENCODED_SENTINEL"
            split_payload = '"HISTORY_SPLIT_" + "SENTINEL"'
            encoded_payload = base64.b64encode(encoded_term.encode("utf-8")).decode("ascii")
            sensitive.write_text(
                split_payload + "\n" + encoded_payload,
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
            message_term = "HISTORY_MESSAGE_SENTINEL"
            subprocess.run(
                ["git", "commit", "-qm", f"add {message_term}"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            sensitive.unlink()
            (root / "safe.md").write_text("neutral", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-qm", "remove temporary"], cwd=root, check=True, capture_output=True)
            result = validate_release_readiness(
                root,
                extra_forbidden_terms=[split_term, encoded_term, message_term],
            )
            self.assertFalse(result["valid"])
            history_errors = [
                error for error in result["errors"] if "reachable Git history" in error
            ]
            self.assertEqual(3, len(history_errors), history_errors)


if __name__ == "__main__":
    unittest.main()
