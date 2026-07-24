import hashlib
import json
import os
from pathlib import Path
import re
import struct
from typing import cast
import unittest

import jsonschema
import yaml

from validators.validate_adapter import validate_publish_plan_file, validate_receipt_file
from validators.validate_block_plan import validate_block_plan_file
from validators.validate_docx_structure import validate_docx_structure
from validators.validate_markdown import validate_markdown_file
from validators.validate_prd_ir import validate_prd_ir_file
from validators.validate_render_manifest import validate_render_manifest_file
from validators.validate_router import validate_router_file


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/nova-event-admin"


class Phase8NovaExampleTests(unittest.TestCase):
    def test_complete_example_file_set_exists(self):
        required = [
            "README.md",
            "source-materials/business-brief.md",
            "source-materials/system-guide.md",
            "source-materials/meeting-notes.md",
            "source-materials/standard-prd.md",
            "source-materials/prototype.html",
            "source-materials/prototype.png",
            "knowledge-base/_meta/config.yaml",
            "knowledge-base/_meta/router.yaml",
            "knowledge-base/_meta/index.md",
            "knowledge-base/_shared/standards/prd-baseline.md",
            "knowledge-base/domains/nova-events/domain.yaml",
            "knowledge-base/domains/nova-events/index.md",
            "knowledge-base/domains/nova-events/sources/manifest.yaml",
            "knowledge-base/domains/nova-events/business/overview.md",
            "knowledge-base/domains/nova-events/systems/event-admin.md",
            "knowledge-base/domains/nova-events/concepts/glossary.md",
            "knowledge-base/domains/nova-events/processes/event-configuration.md",
            "knowledge-base/domains/nova-events/sop/router.yaml",
            "knowledge-base/domains/nova-events/standards/prd-format.yaml",
            "knowledge-base/domains/nova-events/skills/domain-prd/SKILL.md",
            "generated-skill/SKILL.md",
            "generated-skill/wrapper.md",
            "prd-ir/format-profile.yaml",
            "prd-ir/prd-ir.yaml",
            "outputs/prd.md",
            "outputs/prd.docx",
            "outputs/block-plan.yaml",
            "outputs/render-manifest-markdown.yaml",
            "outputs/render-manifest-docx.yaml",
            "outputs/render-manifest-blocks.yaml",
            "gates/gate1.md",
            "gates/gate2.md",
            "gates/publish-plan.yaml",
            "gates/publication-receipt.example.yaml",
        ]
        missing = [item for item in required if not (EXAMPLE / item).is_file()]
        self.assertEqual([], missing)

    def test_root_readme_links_to_nova_example(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("examples/nova-event-admin/README.md", readme)

    def test_prototype_is_offline_light_b2b_html_and_real_png(self):
        html = (EXAMPLE / "source-materials/prototype.html").read_text(encoding="utf-8")
        self.assertNotRegex(html, r"<(?:script|link)[^>]+(?:src|href)=[\"']https?://")
        self.assertNotIn("linear-gradient", html)
        self.assertIn("#0052d9", html.lower())
        self.assertIn("#f5f7fa", html.lower())
        self.assertIn("system-ui", html)
        self.assertNotIn("addEventListener", html)
        png = (EXAMPLE / "source-materials/prototype.png").read_bytes()
        self.assertEqual(b"\x89PNG\r\n\x1a\n", png[:8])
        width, height = struct.unpack(">II", png[16:24])
        self.assertGreaterEqual(width, 1200)
        self.assertGreaterEqual(height, 700)

    def test_example_routers_and_source_manifest_validate(self):
        kb = EXAMPLE / "knowledge-base"
        for relative in ["_meta/router.yaml", "domains/nova-events/sop/router.yaml"]:
            result = validate_router_file(kb / relative, kb)
            self.assertTrue(result["valid"], result["errors"])
        schema = json.loads((ROOT / "schemas/source-manifest.schema.json").read_text(encoding="utf-8"))
        manifest = yaml.safe_load((kb / "domains/nova-events/sources/manifest.yaml").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(manifest)

    def test_source_manifest_hashes_match_real_files(self):
        manifest_path = EXAMPLE / "knowledge-base/domains/nova-events/sources/manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        for item in manifest["sources"]:
            source_path = (manifest_path.parent / item["location"]).resolve()
            self.assertTrue(source_path.is_file(), source_path)
            actual = hashlib.sha256(source_path.read_bytes()).hexdigest()
            self.assertEqual(actual, item["sha256"], item["source_id"])

    def test_example_ir_profile_and_all_source_refs_validate(self):
        ir_path = EXAMPLE / "prd-ir/prd-ir.yaml"
        profile_path = EXAMPLE / "prd-ir/format-profile.yaml"
        result = validate_prd_ir_file(ir_path, profile_path, EXAMPLE)
        self.assertTrue(result["valid"], result["errors"])
        ir = yaml.safe_load(ir_path.read_text(encoding="utf-8"))
        manifest = yaml.safe_load((EXAMPLE / "knowledge-base/domains/nova-events/sources/manifest.yaml").read_text(encoding="utf-8"))
        known = {item["source_id"] for item in manifest["sources"]}
        serialized = yaml.safe_dump(ir)
        used = set(re.findall(r"SRC-[A-Za-z0-9._-]+", serialized))
        self.assertTrue(used)
        self.assertEqual(set(), used - known)

    def test_markdown_docx_and_block_outputs_validate(self):
        ir = EXAMPLE / "prd-ir/prd-ir.yaml"
        markdown = validate_markdown_file(
            EXAMPLE / "outputs/prd.md",
            ir,
            EXAMPLE / "outputs/render-manifest-markdown.yaml",
        )
        self.assertTrue(markdown["valid"], markdown["errors"])
        self.assertEqual(2, markdown["requirement_rows"])
        block = validate_block_plan_file(
            EXAMPLE / "outputs/block-plan.yaml",
            ir,
            EXAMPLE / "outputs/render-manifest-blocks.yaml",
        )
        self.assertTrue(block["valid"], block["errors"])
        self.assertGreaterEqual(block["logic_blocks"], 6)
        docx = validate_docx_structure(EXAMPLE / "outputs/prd.docx")
        self.assertTrue(docx["valid"], docx["errors"])
        logic_cells = cast(int, docx["logic_cells"])
        self.assertGreaterEqual(logic_cells, 2)
        for name in [
            "render-manifest-markdown.yaml",
            "render-manifest-docx.yaml",
            "render-manifest-blocks.yaml",
        ]:
            manifest = validate_render_manifest_file(EXAMPLE / "outputs" / name)
            self.assertTrue(manifest["valid"], manifest["errors"])

    def test_render_manifests_bind_to_real_output_hashes(self):
        for name in [
            "render-manifest-markdown.yaml",
            "render-manifest-docx.yaml",
            "render-manifest-blocks.yaml",
        ]:
            manifest = yaml.safe_load((EXAMPLE / "outputs" / name).read_text(encoding="utf-8"))
            for output in manifest["outputs"]:
                output_path = ROOT / output["path"]
                actual = hashlib.sha256(output_path.read_bytes()).hexdigest()
                self.assertEqual(actual, output["sha256"], name)

    def test_gate_plan_and_simulated_receipt_validate(self):
        plan = validate_publish_plan_file(EXAMPLE / "gates/publish-plan.yaml")
        self.assertTrue(plan["valid"], plan["errors"])
        receipt_path = EXAMPLE / "gates/publication-receipt.example.yaml"
        receipt = validate_receipt_file(receipt_path)
        self.assertTrue(receipt["valid"], receipt["errors"])
        receipt_data = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual("published_unverified", receipt_data["status"])
        self.assertEqual("not_run", receipt_data["verification"]["result"])
        self.assertEqual(plan["computed_plan_sha256"], receipt_data["input"]["publish_plan_sha256"])
        readme = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        self.assertIn("fully fictional", readme.lower())
        self.assertIn("simulated", readme.lower())
        self.assertIn("not a real publication", readme.lower())
        gate1 = (EXAMPLE / "gates/gate1.md").read_text(encoding="utf-8")
        gate2 = (EXAMPLE / "gates/gate2.md").read_text(encoding="utf-8")
        self.assertIn("Gate 1", gate1)
        self.assertIn("Gate 2", gate2)
        self.assertIn("side effects", gate2.lower())

    def test_domain_skill_is_minimal_and_source_driven(self):
        for relative in [
            "knowledge-base/domains/nova-events/skills/domain-prd/SKILL.md",
            "generated-skill/SKILL.md",
        ]:
            text = (EXAMPLE / relative).read_text(encoding="utf-8")
            frontmatter = text.split("---", 2)[1]
            keys = {
                line.split(":", 1)[0].strip()
                for line in frontmatter.splitlines()
                if ":" in line and not line.startswith(" ")
            }
            self.assertEqual({"name", "description"}, keys)
            self.assertIn("router.yaml", text)
            self.assertIn("source", text.lower())

    def test_example_contains_no_private_identifiers_or_credentials(self):
        forbidden = [
            "PRIVATE_COMPANY_NAME",
            "INTERNAL_PLATFORM_CODENAME",
            "Bearer" + " ",
        ]
        extra = os.environ.get("PRD_AGENT_KIT_EXTRA_FORBIDDEN_TERMS", "")
        forbidden.extend(term.strip() for term in extra.split(",") if term.strip())
        home_path = re.compile(r"/Users/[^/\s]+")
        hits = []
        for path in EXAMPLE.rglob("*"):
            if not path.is_file() or path.suffix in {".png", ".docx"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if home_path.search(text):
                hits.append((str(path.relative_to(EXAMPLE)), "absolute home path"))
            for term in forbidden:
                if term.lower() in text.lower():
                    hits.append((str(path.relative_to(EXAMPLE)), term))
        self.assertEqual([], hits)


if __name__ == "__main__":
    unittest.main()
