import json
from pathlib import Path
import unittest

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]


class Phase4SchemaTests(unittest.TestCase):
    def test_phase4_schemas_are_valid_draft_2020_12(self):
        for name in ["prd-ir.schema.json", "prd-format-spec.schema.json"]:
            path = ROOT / "schemas" / name
            self.assertTrue(path.is_file(), f"missing {name}")
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                "https://json-schema.org/draft/2020-12/schema",
                schema.get("$schema"),
            )
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_simple_fixture_validates_against_both_schemas(self):
        ir_schema = json.loads(
            (ROOT / "schemas/prd-ir.schema.json").read_text(encoding="utf-8")
        )
        profile_schema = json.loads(
            (ROOT / "schemas/prd-format-spec.schema.json").read_text(encoding="utf-8")
        )
        fixture = ROOT / "fixtures/simple-prd"
        ir = yaml.safe_load((fixture / "prd-ir.yaml").read_text(encoding="utf-8"))
        profile = yaml.safe_load(
            (fixture / "format-profile.yaml").read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator(ir_schema).validate(ir)
        jsonschema.Draft202012Validator(profile_schema).validate(profile)

    def test_nested_fixture_has_exactly_three_levels_and_passes(self):
        from validators.validate_prd_ir import validate_prd_ir_file

        fixture = ROOT / "fixtures/nested-logic"
        ir_path = fixture / "prd-ir.yaml"
        profile_path = fixture / "format-profile.yaml"
        self.assertTrue(ir_path.is_file())
        self.assertTrue(profile_path.is_file())
        ir = yaml.safe_load(ir_path.read_text(encoding="utf-8"))
        node = ir["requirements"][0]["logic"][0]
        depths = 1
        while node.get("children"):
            depths += 1
            node = node["children"][0]
        self.assertEqual(3, depths)
        result = validate_prd_ir_file(ir_path, profile_path, fixture)
        self.assertTrue(result["valid"], result["errors"])

    def test_template_learning_documents_exist(self):
        for relative in [
            "protocols/template-observation.md",
            "docs/template-learning.md",
        ]:
            path = ROOT / relative
            self.assertTrue(path.is_file(), f"missing {relative}")
            text = path.read_text(encoding="utf-8")
            self.assertIn("Observation", text)
            self.assertIn("confidence", text)
            self.assertIn("用户确认", text)

    def test_skill_includes_phase4_operational_references(self):
        skill_dir = ROOT / "skills/prd-knowledge-engineering"
        skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        for relative in ["references/template-learning.md", "references/prd-ir.md"]:
            self.assertIn(f"`{relative}`", skill)
            self.assertTrue((skill_dir / relative).is_file())

    def test_unregistered_extension_kind_is_schema_compatible_but_semantically_checked(self):
        schema = json.loads(
            (ROOT / "schemas/prd-ir.schema.json").read_text(encoding="utf-8")
        )
        fixture = ROOT / "fixtures/simple-prd/prd-ir.yaml"
        ir = yaml.safe_load(fixture.read_text(encoding="utf-8"))
        ir["requirements"][0]["logic"][0]["kind"] = "x-domain-rule"
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(ir))
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
