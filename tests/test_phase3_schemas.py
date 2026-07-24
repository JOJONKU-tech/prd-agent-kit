import json
from pathlib import Path
import unittest

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]


class Phase3SchemaTests(unittest.TestCase):
    def test_schema_files_are_valid_draft_2020_12(self):
        for name in [
            "source-manifest.schema.json",
            "business-profile.schema.json",
            "router.schema.json",
        ]:
            path = ROOT / "schemas" / name
            self.assertTrue(path.is_file(), f"missing {name}")
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                "https://json-schema.org/draft/2020-12/schema",
                schema.get("$schema"),
            )
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_source_manifest_template_validates(self):
        schema = json.loads(
            (ROOT / "schemas/source-manifest.schema.json").read_text(encoding="utf-8")
        )
        data = yaml.safe_load(
            (
                ROOT
                / "templates/knowledge-base/domains/_template/sources/manifest.yaml"
            ).read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator(schema).validate(data)

    def test_root_and_domain_router_templates_validate(self):
        schema = json.loads(
            (ROOT / "schemas/router.schema.json").read_text(encoding="utf-8")
        )
        for relative in [
            "templates/knowledge-base/_meta/router.yaml",
            "templates/knowledge-base/domains/_template/sop/router.yaml",
        ]:
            data = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator(schema).validate(data)

    def test_always_read_more_than_three_is_rejected(self):
        schema = json.loads(
            (ROOT / "schemas/router.schema.json").read_text(encoding="utf-8")
        )
        data = {
            "schema_version": "1.0",
            "router_type": "domain",
            "domain": "demo",
            "always_read": ["a.md", "b.md", "c.md", "d.md"],
            "routes": [],
            "excluded_by_default": ["sources/raw/**", "templates/**", "skills/**"],
        }
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(data))
        self.assertTrue(errors)

        def flatten(error):
            yield error
            for child in error.context:
                yield from flatten(child)

        messages = [item.message for error in errors for item in flatten(error)]
        self.assertTrue(any("too long" in message for message in messages))

    def test_business_profile_rejects_confirmed_high_risk_rule_without_source(self):
        schema = json.loads(
            (ROOT / "schemas/business-profile.schema.json").read_text(encoding="utf-8")
        )
        profile = {
            "schema_version": "1.0",
            "domain": {"slug": "demo", "name": "Demo"},
            "scope": {"status": "confirmed", "summary": "Demo scope", "source_refs": ["SRC-1"]},
            "roles": [],
            "systems": [],
            "terms": [],
            "metrics": [],
            "rules": [
                {
                    "rule_id": "RULE-1",
                    "kind": "permission",
                    "status": "confirmed",
                    "statement": "Only admins may publish",
                    "source_refs": [],
                }
            ],
            "open_questions": [],
        }
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(profile))
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
