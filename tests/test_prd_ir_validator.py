from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import yaml

from validators.validate_prd_ir import resolve_profile, validate_prd_ir_file


ROOT = Path(__file__).resolve().parents[1]
SIMPLE_IR = ROOT / "fixtures/simple-prd/prd-ir.yaml"
SIMPLE_PROFILE = ROOT / "fixtures/simple-prd/format-profile.yaml"


class PrdIrValidatorTests(unittest.TestCase):
    def _load_ir(self):
        return yaml.safe_load(SIMPLE_IR.read_text(encoding="utf-8"))

    def _write_yaml(self, directory, name, data):
        path = Path(directory) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return path

    def test_simple_fixture_passes_semantic_validation(self):
        result = validate_prd_ir_file(SIMPLE_IR, SIMPLE_PROFILE, SIMPLE_IR.parent)
        self.assertTrue(result["valid"], result["errors"])

    def test_unregistered_extension_kind_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            ir = self._load_ir()
            ir["requirements"][0]["logic"][0]["kind"] = "x-unregistered-rule"
            path = self._write_yaml(temp, "prd-ir.yaml", ir)
            result = validate_prd_ir_file(path, SIMPLE_PROFILE, temp)
            self.assertFalse(result["valid"])
            self.assertTrue(any("not registered" in error for error in result["errors"]))

    def test_registered_extension_kind_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            ir = self._load_ir()
            ir["requirements"][0]["logic"][0]["kind"] = "x-domain-rule"
            profile = yaml.safe_load(SIMPLE_PROFILE.read_text(encoding="utf-8"))
            profile["custom_logic_kinds"] = [
                {
                    "kind": "x-domain-rule",
                    "label": "Domain Rule",
                    "description": "A confirmed domain-specific rule.",
                    "high_risk": False,
                }
            ]
            ir_path = self._write_yaml(temp, "prd-ir.yaml", ir)
            profile_path = self._write_yaml(temp, "profile.yaml", profile)
            result = validate_prd_ir_file(ir_path, profile_path, temp)
            self.assertTrue(result["valid"], result["errors"])

    def test_logic_deeper_than_three_levels_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            ir = self._load_ir()
            node = ir["requirements"][0]["logic"][0]
            for index in range(3):
                child = {
                    "logic_id": f"LOGIC-DEEP-{index}",
                    "kind": "branch",
                    "text": "Nested branch",
                    "status": "confirmed",
                    "source_refs": ["SRC-DEMO"],
                    "children": [],
                }
                node["children"] = [child]
                node = child
            path = self._write_yaml(temp, "prd-ir.yaml", ir)
            result = validate_prd_ir_file(path, SIMPLE_PROFILE, temp)
            self.assertFalse(result["valid"])
            self.assertTrue(any("maximum depth" in error for error in result["errors"]))

    def test_high_risk_confirmed_logic_without_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            ir = self._load_ir()
            logic = ir["requirements"][0]["logic"][0]
            logic["kind"] = "permission"
            logic["source_refs"] = []
            path = self._write_yaml(temp, "prd-ir.yaml", ir)
            result = validate_prd_ir_file(path, SIMPLE_PROFILE, temp)
            self.assertFalse(result["valid"])
            self.assertTrue(any("source" in error.lower() for error in result["errors"]))

    def test_missing_local_asset_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            ir = self._load_ir()
            ir["assets"] = [
                {
                    "asset_id": "ASSET-1",
                    "type": "image",
                    "source": "assets/missing.png",
                    "alt": "Missing image",
                    "status": "confirmed",
                }
            ]
            ir["requirements"][0]["prototype_asset_refs"] = ["ASSET-1"]
            path = self._write_yaml(temp, "prd-ir.yaml", ir)
            result = validate_prd_ir_file(path, SIMPLE_PROFILE, temp)
            self.assertFalse(result["valid"])
            self.assertTrue(any("asset source does not exist" in error for error in result["errors"]))

    def test_blocking_open_question_prevents_confirmed_document(self):
        with tempfile.TemporaryDirectory() as temp:
            ir = self._load_ir()
            ir["document"]["status"] = "confirmed"
            ir["open_questions"] = [
                {
                    "question_id": "Q-1",
                    "question": "Which permission applies?",
                    "blocking": True,
                    "status": "open",
                    "answer": None,
                    "source_refs": [],
                }
            ]
            path = self._write_yaml(temp, "prd-ir.yaml", ir)
            result = validate_prd_ir_file(path, SIMPLE_PROFILE, temp)
            self.assertFalse(result["valid"])
            self.assertTrue(any("blocking" in error.lower() for error in result["errors"]))

    def test_malformed_ir_returns_errors_instead_of_crashing(self):
        with tempfile.TemporaryDirectory() as temp:
            ir = self._load_ir()
            ir["document"] = "not-an-object"
            path = self._write_yaml(temp, "prd-ir.yaml", ir)
            result = validate_prd_ir_file(path, SIMPLE_PROFILE, temp)
            self.assertFalse(result["valid"])
            self.assertTrue(any("schema" in error for error in result["errors"]))

    def test_profile_inheritance_deep_merges_maps_and_replaces_lists(self):
        with tempfile.TemporaryDirectory() as temp:
            base = yaml.safe_load(SIMPLE_PROFILE.read_text(encoding="utf-8"))
            base["profile_id"] = "base"
            child = {
                "schema_version": "1.0",
                "profile_id": "child",
                "name": "Child",
                "status": "confirmed",
                "extends": "base.yaml",
                "writing": {"tone": "concise"},
                "capabilities": {"preferred": ["repeat_table_header"]},
            }
            self._write_yaml(temp, "base.yaml", base)
            child_path = self._write_yaml(temp, "child.yaml", child)
            resolved = resolve_profile(child_path)
            self.assertEqual("concise", resolved["writing"]["tone"])
            self.assertIn("requirements_table", resolved["presentation"])
            self.assertEqual(["repeat_table_header"], resolved["capabilities"]["preferred"])
            self.assertEqual("child", resolved["profile_id"])

    def test_profile_inheritance_cycle_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            a = {
                "schema_version": "1.0",
                "profile_id": "a",
                "name": "A",
                "status": "confirmed",
                "extends": "b.yaml",
            }
            b = deepcopy(a)
            b.update({"profile_id": "b", "name": "B", "extends": "a.yaml"})
            a_path = self._write_yaml(temp, "a.yaml", a)
            self._write_yaml(temp, "b.yaml", b)
            with self.assertRaisesRegex(ValueError, "cycle"):
                resolve_profile(a_path)


if __name__ == "__main__":
    unittest.main()
