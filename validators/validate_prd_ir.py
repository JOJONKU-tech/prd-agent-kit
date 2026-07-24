#!/usr/bin/env python3
"""Validate PRD IR, Format Profile inheritance, sources, logic depth, and assets."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
from typing import Any

import jsonschema
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IR_SCHEMA_PATH = PROJECT_ROOT / "schemas/prd-ir.schema.json"
PROFILE_SCHEMA_PATH = PROJECT_ROOT / "schemas/prd-format-spec.schema.json"
STANDARD_HIGH_RISK = {
    "field_source",
    "default_value",
    "permission",
    "metric_formula",
    "validation",
    "data_migration",
    "system_boundary",
}
REMOTE_SOURCE = re.compile(r"^https?://", re.IGNORECASE)


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return data


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def _deep_merge(base: Any, child: Any) -> Any:
    """Deep-merge maps; child lists and scalar values replace base values."""
    if isinstance(base, dict) and isinstance(child, dict):
        result = deepcopy(base)
        for key, value in child.items():
            result[key] = _deep_merge(result[key], value) if key in result else deepcopy(value)
        return result
    return deepcopy(child)


def resolve_profile(profile_path: str | Path, _stack: tuple[Path, ...] = ()) -> dict[str, Any]:
    """Resolve Format Profile inheritance relative to each child profile file."""
    path = Path(profile_path).resolve()
    if path in _stack:
        chain = " -> ".join(item.name for item in (*_stack, path))
        raise ValueError(f"profile inheritance cycle: {chain}")
    profile = _load_yaml(path)
    parent_ref = profile.get("extends")
    if not parent_ref:
        return profile
    parent_path = (path.parent / str(parent_ref)).resolve()
    if not parent_path.is_file():
        raise ValueError(f"parent profile does not exist: {parent_ref}")
    parent = resolve_profile(parent_path, (*_stack, path))
    return _deep_merge(parent, profile)


def _schema_errors(data: dict[str, Any], schema_path: Path, prefix: str) -> list[str]:
    validator = jsonschema.Draft202012Validator(_load_json(schema_path))
    errors: list[str] = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{prefix} schema:{location}: {error.message}")
    return errors


def _walk_logic(nodes: Any, depth: int = 1):
    if not isinstance(nodes, list):
        return
    for node in nodes:
        if not isinstance(node, dict):
            continue
        yield node, depth
        yield from _walk_logic(node.get("children", []), depth + 1)


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def validate_prd_ir_data(
    ir: dict[str, Any], profile: dict[str, Any], assets_root: Path
) -> dict[str, Any]:
    errors = _schema_errors(ir, IR_SCHEMA_PATH, "IR")
    errors.extend(_schema_errors(profile, PROFILE_SCHEMA_PATH, "profile"))
    if errors:
        # Continue semantic checks only when required containers exist.
        if not isinstance(ir.get("requirements"), list):
            return {"valid": False, "errors": errors}

    registered_custom = {
        item["kind"]: item
        for item in profile.get("custom_logic_kinds", [])
        if isinstance(item, dict) and isinstance(item.get("kind"), str)
    }
    logic_nodes: list[tuple[dict[str, Any], int]] = []
    requirement_ids: list[str] = []
    sequences: list[int] = []
    referenced_assets: list[str] = []
    for requirement in ir.get("requirements", []):
        if not isinstance(requirement, dict):
            continue
        if isinstance(requirement.get("requirement_id"), str):
            requirement_ids.append(requirement["requirement_id"])
        if isinstance(requirement.get("sequence"), int):
            sequences.append(requirement["sequence"])
        asset_refs = requirement.get("prototype_asset_refs", [])
        if isinstance(asset_refs, list):
            referenced_assets.extend(item for item in asset_refs if isinstance(item, str))
        logic_nodes.extend(_walk_logic(requirement.get("logic", [])))

    for duplicate in sorted(_duplicates(requirement_ids)):
        errors.append(f"duplicate requirement_id: {duplicate}")
    for duplicate in sorted(str(value) for value in _duplicates([str(item) for item in sequences])):
        errors.append(f"duplicate requirement sequence: {duplicate}")

    logic_ids: list[str] = []
    for logic, depth in logic_nodes:
        logic_id = logic.get("logic_id")
        if isinstance(logic_id, str):
            logic_ids.append(logic_id)
        kind = logic.get("kind")
        if depth > 3:
            errors.append(f"logic maximum depth is 3: {logic_id or '<unknown>'} has depth {depth}")
        if isinstance(kind, str) and kind.startswith("x-") and kind not in registered_custom:
            errors.append(f"custom logic kind is not registered in profile: {kind}")
        high_risk = kind in STANDARD_HIGH_RISK or bool(registered_custom.get(kind, {}).get("high_risk"))
        if high_risk and logic.get("status") == "confirmed" and not logic.get("source_refs"):
            errors.append(f"confirmed high-risk logic requires source_refs: {logic_id or '<unknown>'}")
    for duplicate in sorted(_duplicates(logic_ids)):
        errors.append(f"duplicate logic_id: {duplicate}")

    assets = [item for item in ir.get("assets", []) if isinstance(item, dict)]
    asset_ids: list[str] = [
        item["asset_id"]
        for item in assets
        if isinstance(item.get("asset_id"), str)
    ]
    for duplicate in sorted(_duplicates(asset_ids)):
        errors.append(f"duplicate asset_id: {duplicate}")
    known_assets = set(asset_ids)
    for asset_ref in referenced_assets:
        if asset_ref not in known_assets:
            errors.append(f"prototype asset reference is not declared: {asset_ref}")
    for asset in assets:
        source = asset.get("source")
        if not isinstance(source, str) or REMOTE_SOURCE.match(source):
            continue
        target = (assets_root / source).resolve()
        try:
            target.relative_to(assets_root.resolve())
        except ValueError:
            errors.append(f"asset source escapes assets root: {source}")
            continue
        if not target.is_file():
            errors.append(f"asset source does not exist: {source}")

    document = ir.get("document")
    document = document if isinstance(document, dict) else {}
    questions = ir.get("open_questions")
    questions = questions if isinstance(questions, list) else []
    if document.get("status") == "confirmed":
        for question in questions:
            if not isinstance(question, dict):
                continue
            if question.get("blocking") is True and question.get("status") == "open":
                errors.append(f"confirmed document has blocking open question: {question.get('question_id', '<unknown>')}")

    profile_ref = document.get("profile_ref")
    profile_id = profile.get("profile_id")
    if profile_ref and profile_id and profile_ref != profile_id:
        errors.append(f"document profile_ref {profile_ref!r} does not match resolved profile_id {profile_id!r}")

    return {"valid": not errors, "errors": errors}


def validate_prd_ir_file(
    ir_path: str | Path,
    profile_path: str | Path,
    assets_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load and validate one IR file with its resolved Format Profile."""
    ir_file = Path(ir_path)
    root = Path(assets_root) if assets_root is not None else ir_file.parent
    try:
        ir = _load_yaml(ir_file)
        profile = resolve_profile(profile_path)
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": [f"load: {exc}"]}
    return validate_prd_ir_data(ir, profile, root)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ir", type=Path, help="PRD IR YAML path")
    parser.add_argument("--profile", type=Path, required=True, help="Format Profile YAML path")
    parser.add_argument("--assets-root", type=Path, help="Base directory for local asset sources")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    result = validate_prd_ir_file(args.ir, args.profile, args.assets_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
