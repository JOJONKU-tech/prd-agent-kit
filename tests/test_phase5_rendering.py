from pathlib import Path
import tempfile
import unittest

import yaml

from validators.validate_block_plan import validate_block_plan_file
from validators.validate_docx_structure import validate_docx_structure
from validators.validate_markdown import validate_markdown_file
from validators.validate_render_manifest import validate_render_manifest_data


ROOT = Path(__file__).resolve().parents[1]


class Phase5RenderingTests(unittest.TestCase):
    def test_required_phase5_artifacts_exist(self):
        required = [
            "schemas/render-manifest.schema.json",
            "protocols/renderer-contract.md",
            "docs/renderer-protocols.md",
            "validators/validate_render_manifest.py",
            "validators/validate_markdown.py",
            "validators/validate_docx_structure.py",
            "validators/validate_block_plan.py",
            "templates/golden/neutral-prd-template.docx",
            "templates/golden/neutral-prd-template.manifest.yaml",
            "fixtures/simple-prd/output.md",
            "fixtures/simple-prd/render-manifest.yaml",
            "fixtures/nested-logic/block-plan.yaml",
            "fixtures/nested-logic/render-manifest.yaml",
            "fixtures/image-heavy/prd-ir.yaml",
            "fixtures/image-heavy/assets/neutral.png",
            "fixtures/incompatible-capabilities/render-manifest.yaml",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual([], missing)

    def test_ready_for_publish_rejects_unsupported_required_capability(self):
        manifest = {
            "schema_version": "1.0",
            "render_id": "RENDER-1",
            "renderer": "docx",
            "input": {"prd_ir": "prd-ir.yaml", "prd_ir_sha256": "a" * 64, "format_profile": "demo", "format_spec_sha256": "b" * 64},
            "capabilities": {"required": {"native_ordered_lists": "unsupported"}, "preferred": {}},
            "status": "ready_for_publish",
            "outputs": [],
            "degradations": [],
            "checks": {"schema_valid": "passed", "structure_valid": "passed", "visual_valid": "passed"},
        }
        result = validate_render_manifest_data(manifest)
        self.assertFalse(result["valid"])
        self.assertTrue(any("required capability" in error for error in result["errors"]))

    def test_preferred_capability_degradation_must_be_reported(self):
        manifest = {
            "schema_version": "1.0",
            "render_id": "RENDER-2",
            "renderer": "markdown",
            "input": {"prd_ir": "prd-ir.yaml", "prd_ir_sha256": "a" * 64, "format_profile": "demo", "format_spec_sha256": "b" * 64},
            "capabilities": {"required": {}, "preferred": {"requirements_table": "unsupported"}},
            "status": "ready_for_review",
            "outputs": [],
            "degradations": [],
            "checks": {"schema_valid": "passed", "structure_valid": "passed", "visual_valid": "not_run"},
        }
        result = validate_render_manifest_data(manifest)
        self.assertFalse(result["valid"])
        self.assertTrue(any("degradation" in error for error in result["errors"]))

    def test_portable_markdown_fixture_is_valid(self):
        fixture = ROOT / "fixtures/simple-prd"
        result = validate_markdown_file(
            fixture / "output.md",
            fixture / "prd-ir.yaml",
            fixture / "render-manifest.yaml",
        )
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(1, result["requirement_rows"])

    def test_markdown_fullwidth_pipe_is_rejected(self):
        fixture = ROOT / "fixtures/simple-prd"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.md"
            path.write_text("| A | B |\n|---|---|\n｜x｜y｜\n", encoding="utf-8")
            result = validate_markdown_file(
                path, fixture / "prd-ir.yaml", fixture / "render-manifest.yaml"
            )
            self.assertFalse(result["valid"])
            self.assertTrue(any("fullwidth" in error for error in result["errors"]))

    def test_markdown_allows_separate_tables_with_different_widths(self):
        fixture = ROOT / "fixtures/simple-prd"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "two-tables.md"
            original = (fixture / "output.md").read_text(encoding="utf-8")
            path.write_text(
                original + "\n| A | B |\n|---|---|\n| x | y |\n",
                encoding="utf-8",
            )
            manifest = yaml.safe_load((fixture / "render-manifest.yaml").read_text(encoding="utf-8"))
            import hashlib
            manifest["outputs"][0]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest_path = Path(temp) / "manifest.yaml"
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            result = validate_markdown_file(path, fixture / "prd-ir.yaml", manifest_path)
            self.assertTrue(result["valid"], result["errors"])

    def test_markdown_output_hash_mismatch_is_rejected(self):
        fixture = ROOT / "fixtures/simple-prd"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "tampered.md"
            path.write_text((fixture / "output.md").read_text(encoding="utf-8") + "\nTampered\n", encoding="utf-8")
            result = validate_markdown_file(path, fixture / "prd-ir.yaml", fixture / "render-manifest.yaml")
            self.assertFalse(result["valid"])
            self.assertTrue(any("output hash" in error for error in result["errors"]))

    def test_nested_block_plan_preserves_logic_depth(self):
        fixture = ROOT / "fixtures/nested-logic"
        result = validate_block_plan_file(
            fixture / "block-plan.yaml",
            fixture / "prd-ir.yaml",
            fixture / "render-manifest.yaml",
        )
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(3, result["logic_blocks"])
        self.assertEqual(2, result["max_depth"])

    def test_block_plan_output_hash_mismatch_is_rejected(self):
        fixture = ROOT / "fixtures/nested-logic"
        with tempfile.TemporaryDirectory() as temp:
            plan = Path(temp) / "tampered.yaml"
            plan.write_text((fixture / "block-plan.yaml").read_text(encoding="utf-8") + "\nnotes: tampered\n", encoding="utf-8")
            result = validate_block_plan_file(plan, fixture / "prd-ir.yaml", fixture / "render-manifest.yaml")
            self.assertFalse(result["valid"])
            self.assertTrue(any("output hash" in error for error in result["errors"]))

    def test_golden_docx_has_native_numbering_and_independent_cells(self):
        result = validate_docx_structure(
            ROOT / "templates/golden/neutral-prd-template.docx"
        )
        self.assertTrue(result["valid"], result["errors"])
        self.assertGreaterEqual(result["numbered_paragraphs"], 6)
        self.assertGreaterEqual(result["logic_cells"], 2)
        self.assertTrue(result["independent_num_ids"])
        self.assertGreaterEqual(result["max_level"], 2)

    def test_skill_includes_renderer_reference(self):
        skill_dir = ROOT / "skills/prd-knowledge-engineering"
        skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`references/rendering.md`", skill)
        self.assertTrue((skill_dir / "references/rendering.md").is_file())

    def test_no_fixed_renderer_implementation_is_committed(self):
        forbidden = {
            "render_markdown.py",
            "render_docx.py",
            "render_feishu.py",
        }
        found = {path.name for path in ROOT.rglob("*.py") if path.name in forbidden}
        self.assertEqual(set(), found)

    def test_incompatible_fixture_fails_safely(self):
        manifest = yaml.safe_load(
            (ROOT / "fixtures/incompatible-capabilities/render-manifest.yaml").read_text(encoding="utf-8")
        )
        result = validate_render_manifest_data(manifest)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual("failed", manifest["status"])
        self.assertEqual("unsupported", manifest["capabilities"]["required"]["native_ordered_lists"])


if __name__ == "__main__":
    unittest.main()
