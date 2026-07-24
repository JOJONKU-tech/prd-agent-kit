from pathlib import Path
import tempfile
import unittest

import yaml

from validators.validate_router import route_request, validate_router_file


class RouterValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "schemas").mkdir()
        project_schema = (
            Path(__file__).resolve().parents[1] / "schemas/router.schema.json"
        )
        (self.root / "schemas/router.schema.json").write_text(
            project_schema.read_text(encoding="utf-8"), encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def _write_yaml(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return path

    def test_domain_router_accepts_existing_safe_references(self):
        domain = self.root / "domains/demo"
        (domain / "business").mkdir(parents=True)
        (domain / "business/overview.md").write_text("# Overview\n", encoding="utf-8")
        router = self._write_yaml(
            "domains/demo/sop/router.yaml",
            {
                "schema_version": "1.0",
                "router_type": "domain",
                "domain": "demo",
                "always_read": ["business/overview.md"],
                "routes": [],
                "excluded_by_default": [
                    "sources/raw/**",
                    "templates/**",
                    "skills/**",
                ],
            },
        )
        result = validate_router_file(router, self.root)
        self.assertTrue(result["valid"], result["errors"])

    def test_missing_reference_is_rejected(self):
        router = self._write_yaml(
            "domains/demo/sop/router.yaml",
            {
                "schema_version": "1.0",
                "router_type": "domain",
                "domain": "demo",
                "always_read": ["business/missing.md"],
                "routes": [],
                "excluded_by_default": [
                    "sources/raw/**",
                    "templates/**",
                    "skills/**",
                ],
            },
        )
        result = validate_router_file(router, self.root)
        self.assertFalse(result["valid"])
        self.assertTrue(any("does not exist" in error for error in result["errors"]))

    def test_raw_template_and_skill_references_are_rejected(self):
        domain = self.root / "domains/demo"
        for relative in ["sources/raw/a.md", "templates/a.md", "skills/a.md"]:
            path = domain / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x", encoding="utf-8")
        for forbidden in ["sources/raw/a.md", "templates/a.md", "skills/a.md"]:
            with self.subTest(forbidden=forbidden):
                router = self._write_yaml(
                    "domains/demo/sop/router.yaml",
                    {
                        "schema_version": "1.0",
                        "router_type": "domain",
                        "domain": "demo",
                        "always_read": [forbidden],
                        "routes": [],
                        "excluded_by_default": [
                            "sources/raw/**",
                            "templates/**",
                            "skills/**",
                        ],
                    },
                )
                result = validate_router_file(router, self.root)
                self.assertFalse(result["valid"])
                self.assertTrue(any("forbidden" in error for error in result["errors"]))

    def test_ambiguous_multi_domain_request_requires_confirmation(self):
        router = {
            "schema_version": "1.0",
            "router_type": "root",
            "default_domain": None,
            "domains": [
                {
                    "slug": "sales-ops",
                    "name": "Sales Operations",
                    "path": "domains/sales-ops",
                    "keywords": ["campaign", "dashboard"],
                },
                {
                    "slug": "event-ops",
                    "name": "Event Operations",
                    "path": "domains/event-ops",
                    "keywords": ["campaign", "dashboard"],
                },
            ],
            "shared": {"always_read": [], "routes": []},
        }
        result = route_request(router, "Create a campaign dashboard PRD")
        self.assertEqual("needs_confirmation", result["status"])
        self.assertEqual({"sales-ops", "event-ops"}, set(result["candidates"]))

    def test_explicit_domain_resolves_ambiguity(self):
        router = {
            "schema_version": "1.0",
            "router_type": "root",
            "default_domain": None,
            "domains": [
                {
                    "slug": "sales-ops",
                    "name": "Sales Operations",
                    "path": "domains/sales-ops",
                    "keywords": ["campaign"],
                },
                {
                    "slug": "event-ops",
                    "name": "Event Operations",
                    "path": "domains/event-ops",
                    "keywords": ["campaign"],
                },
            ],
            "shared": {"always_read": [], "routes": []},
        }
        result = route_request(router, "Create a campaign PRD", "event-ops")
        self.assertEqual("selected", result["status"])
        self.assertEqual("event-ops", result["domain"])


if __name__ == "__main__":
    unittest.main()
