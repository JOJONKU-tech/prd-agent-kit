#!/usr/bin/env python3
"""Validate renderer manifests and capability/degradation semantics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/render-manifest.schema.json"


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("render manifest must be an object")
    return data


def _schema_errors(manifest: dict[str, Any]) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors=[]
    for error in sorted(validator.iter_errors(manifest), key=lambda item:list(item.absolute_path)):
        location=".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"schema:{location}: {error.message}")
    return errors


def validate_render_manifest_data(manifest: dict[str, Any]) -> dict[str, Any]:
    errors = _schema_errors(manifest)
    capabilities = manifest.get("capabilities")
    capabilities = capabilities if isinstance(capabilities, dict) else {}
    required = capabilities.get("required")
    required = required if isinstance(required, dict) else {}
    preferred = capabilities.get("preferred")
    preferred = preferred if isinstance(preferred, dict) else {}
    status = manifest.get("status")

    unsupported_required = sorted(
        feature for feature, value in required.items() if value != "supported"
    )
    if unsupported_required and status != "failed":
        errors.append(
            "required capability is not supported; status must be failed: "
            + ", ".join(unsupported_required)
        )

    degradations = manifest.get("degradations")
    degradations = degradations if isinstance(degradations, list) else []
    degraded_features = {
        item.get("feature") for item in degradations if isinstance(item, dict)
    }
    unsupported_preferred = sorted(
        feature for feature, value in preferred.items() if value != "supported"
    )
    for feature in unsupported_preferred:
        if feature not in degraded_features:
            errors.append(f"preferred capability degradation is not reported: {feature}")

    checks = manifest.get("checks")
    checks = checks if isinstance(checks, dict) else {}
    if status == "ready_for_publish":
        if checks.get("schema_valid") != "passed" or checks.get("structure_valid") != "passed":
            errors.append("ready_for_publish requires passed schema and structure checks")
        if manifest.get("renderer") == "docx" and checks.get("visual_valid") != "passed":
            errors.append("DOCX ready_for_publish requires passed visual validation")

    return {
        "valid": not errors,
        "errors": errors,
        "unsupported_required": unsupported_required,
        "unsupported_preferred": unsupported_preferred,
    }


def validate_render_manifest_file(path: str | Path) -> dict[str, Any]:
    try:
        manifest=_load(Path(path))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return {"valid":False,"errors":[f"load: {exc}"]}
    return validate_render_manifest_data(manifest)


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest",type=Path)
    args=parser.parse_args(argv)
    result=validate_render_manifest_file(args.manifest)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["valid"] else 1


if __name__=="__main__":
    sys.exit(main())
