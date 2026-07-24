from copy import deepcopy
import json
from pathlib import Path
import unittest

import jsonschema
import yaml

from validators.validate_adapter import (
    compute_plan_hash,
    validate_adapter_file,
    validate_publish_plan_data,
    validate_receipt_data,
)


ROOT = Path(__file__).resolve().parents[1]


class Phase6PublishingTests(unittest.TestCase):
    def test_phase6_files_exist(self):
        required = [
            "schemas/document-adapter.schema.json",
            "schemas/publish-plan.schema.json",
            "schemas/publication-receipt.schema.json",
            "protocols/generic-document-mcp.md",
            "docs/publishing.md",
            "validators/validate_adapter.py",
            "examples/document-adapters/generic.yaml",
            "examples/document-adapters/feishu.yaml",
            "fixtures/publishing/publish-plan.yaml",
            "fixtures/publishing/publication-receipt.yaml",
            "skills/prd-knowledge-engineering/references/publishing.md",
        ]
        missing = [item for item in required if not (ROOT / item).is_file()]
        self.assertEqual([], missing)

    def test_phase6_schemas_are_valid_draft_2020_12(self):
        for name in [
            "document-adapter.schema.json",
            "publish-plan.schema.json",
            "publication-receipt.schema.json",
        ]:
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema.get("$schema"))
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_public_adapter_examples_validate_and_are_write_verified(self):
        for name in ["generic.yaml", "feishu.yaml"]:
            result = validate_adapter_file(ROOT / "examples/document-adapters" / name)
            self.assertTrue(result["valid"], result["errors"])
            self.assertIn(result["verification_status"], {"write_verified", "structure_verified"})

    def test_adapter_rejects_delete_permission_and_share_capabilities(self):
        adapter = yaml.safe_load((ROOT / "examples/document-adapters/generic.yaml").read_text(encoding="utf-8"))
        for capability in ["delete_document", "change_permissions", "share_document"]:
            with self.subTest(capability=capability):
                candidate = deepcopy(adapter)
                candidate["capabilities"][capability] = {
                    "tool": "dangerous_tool",
                    "status": "write_verified",
                }
                with self.assertRaises(jsonschema.ValidationError):
                    schema = json.loads((ROOT / "schemas/document-adapter.schema.json").read_text(encoding="utf-8"))
                    jsonschema.Draft202012Validator(schema).validate(candidate)

    def test_adapter_rejects_embedded_credentials(self):
        adapter = yaml.safe_load((ROOT / "examples/document-adapters/generic.yaml").read_text(encoding="utf-8"))
        adapter["mcp"]["authorization"] = "Bearer" + " secret-value"
        with tempfile_directory() as temp:
            path = Path(temp) / "adapter.yaml"
            path.write_text(yaml.safe_dump(adapter, sort_keys=False), encoding="utf-8")
            result = validate_adapter_file(path)
            self.assertFalse(result["valid"])
            self.assertTrue(any("credential" in error.lower() for error in result["errors"]))

    def test_adapter_rejects_destructive_tool_hidden_under_safe_capability(self):
        adapter = yaml.safe_load((ROOT / "examples/document-adapters/generic.yaml").read_text(encoding="utf-8"))
        adapter["capabilities"]["create_document"] = {
            "tool": "delete_document",
            "status": "write_verified",
        }
        with tempfile_directory() as temp:
            path = Path(temp) / "adapter.yaml"
            path.write_text(yaml.safe_dump(adapter, sort_keys=False), encoding="utf-8")
            result = validate_adapter_file(path)
            self.assertFalse(result["valid"])
            self.assertTrue(any("destructive" in error for error in result["errors"]))

    def test_confirmed_plan_hash_detects_post_confirmation_mutation(self):
        plan = yaml.safe_load((ROOT / "fixtures/publishing/publish-plan.yaml").read_text(encoding="utf-8"))
        plan["confirmation"].update({
            "status": "confirmed",
            "plan_sha256": compute_plan_hash(plan),
            "confirmed_at": "2026-07-24T10:00:00Z",
        })
        self.assertTrue(validate_publish_plan_data(plan)["valid"])
        plan["target"]["title"] = "Mutated title"
        result = validate_publish_plan_data(plan)
        self.assertFalse(result["valid"])
        self.assertTrue(any("plan_sha256" in error for error in result["errors"]))

    def test_publishing_status_requires_confirmed_plan(self):
        plan = yaml.safe_load((ROOT / "fixtures/publishing/publish-plan.yaml").read_text(encoding="utf-8"))
        plan["status"] = "publishing"
        result = validate_publish_plan_data(plan)
        self.assertFalse(result["valid"])
        self.assertTrue(any("confirmed Gate 2" in error for error in result["errors"]))

    def test_side_effect_counts_must_match_executed_operation(self):
        plan = yaml.safe_load((ROOT / "fixtures/publishing/publish-plan.yaml").read_text(encoding="utf-8"))
        plan["side_effects"]["create_documents"] = 0
        result = validate_publish_plan_data(plan)
        self.assertFalse(result["valid"])
        self.assertTrue(any("side_effects" in error for error in result["errors"]))

    def test_update_fallback_requires_versioned_title_and_reason(self):
        plan = yaml.safe_load((ROOT / "fixtures/publishing/publish-plan.yaml").read_text(encoding="utf-8"))
        plan["operation"] = {
            "requested": "update",
            "executed": "create_new_version",
            "fallback_reason": "Target document could not be read.",
        }
        plan["target"]["document_id"] = None
        plan["target"]["title"] = "Demo PRD V2"
        self.assertTrue(validate_publish_plan_data(plan)["valid"])
        plan["target"]["title"] = "Demo PRD updated"
        result = validate_publish_plan_data(plan)
        self.assertFalse(result["valid"])
        self.assertTrue(any("V2/V3" in error for error in result["errors"]))

    def test_receipt_rejects_signed_or_credential_urls(self):
        receipt = yaml.safe_load((ROOT / "fixtures/publishing/publication-receipt.yaml").read_text(encoding="utf-8"))
        self.assertTrue(validate_receipt_data(receipt)["valid"])
        for url in [
            "https://docs.example.test/doc/1?X-Amz-" + "Signature=secret",
            "https://docs.example.test/doc/1?q-" + "sign-algorithm=sha1",
            "https://user:" + "password@docs.example.test/doc/1",
        ]:
            with self.subTest(url=url):
                candidate = deepcopy(receipt)
                candidate["document"]["url"] = url
                result = validate_receipt_data(candidate)
                self.assertFalse(result["valid"])

    def test_protocol_requires_sandbox_and_forbids_destructive_capabilities(self):
        text = (ROOT / "protocols/generic-document-mcp.md").read_text(encoding="utf-8")
        self.assertIn("sandbox", text)
        self.assertIn("write_verified", text)
        self.assertIn("delete_document", text)
        self.assertIn("禁止", text)


class tempfile_directory:
    def __enter__(self):
        import tempfile
        self._temp = tempfile.TemporaryDirectory()
        return self._temp.name

    def __exit__(self, exc_type, exc, tb):
        self._temp.cleanup()


if __name__ == "__main__":
    unittest.main()
