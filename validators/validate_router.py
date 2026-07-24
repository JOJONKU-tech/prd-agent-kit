#!/usr/bin/env python3
"""Validate knowledge-router YAML and preflight domain selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any

import jsonschema
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROUTER_SCHEMA = PROJECT_ROOT / "schemas/router.schema.json"
FORBIDDEN_PREFIXES = ("sources/raw", "templates", "skills")


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("router must be a YAML object")
    return data


def _load_schema() -> dict[str, Any]:
    return json.loads(ROUTER_SCHEMA.read_text(encoding="utf-8"))


def _format_schema_error(error: jsonschema.ValidationError) -> str:
    location = ".".join(str(part) for part in error.absolute_path) or "$"
    return f"schema:{location}: {error.message}"


def _route_paths(router: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    if router.get("router_type") == "root":
        shared = router.get("shared", {})
        paths.extend(shared.get("always_read", []))
        routes = shared.get("routes", [])
    else:
        paths.extend(router.get("always_read", []))
        routes = router.get("routes", [])
    for route in routes:
        read = route.get("read", {})
        paths.extend(read.get("required", []))
        paths.extend(read.get("optional", []))
    return paths


def _is_forbidden(path: str) -> bool:
    normalized = PurePosixPath(path).as_posix().lstrip("./")
    return any(
        normalized == prefix or normalized.startswith(f"{prefix}/")
        for prefix in FORBIDDEN_PREFIXES
    )


def _is_within(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def validate_router_data(
    router: dict[str, Any], router_path: Path, knowledge_base_root: Path
) -> dict[str, Any]:
    """Validate Schema plus filesystem semantics for one router."""
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(_load_schema())
    errors.extend(
        _format_schema_error(error)
        for error in sorted(validator.iter_errors(router), key=lambda item: list(item.path))
    )
    if errors:
        return {"valid": False, "errors": errors, "router_type": router.get("router_type")}

    router_type = router["router_type"]
    if router_type == "root":
        base = knowledge_base_root
        for domain in router["domains"]:
            target = knowledge_base_root / domain["path"]
            if not _is_within(target, knowledge_base_root):
                errors.append(f"domain path escapes knowledge-base root: {domain['path']}")
            elif not target.exists():
                errors.append(f"domain path does not exist: {domain['path']}")
        slugs = [domain["slug"] for domain in router["domains"]]
        if len(slugs) != len(set(slugs)):
            errors.append("domain slugs must be unique")
        default = router.get("default_domain")
        if default is not None and default not in slugs:
            errors.append(f"default_domain is not registered: {default}")
    else:
        base = router_path.parent.parent
        if not _is_within(base, knowledge_base_root):
            errors.append("domain router is outside knowledge-base root")

    for relative in _route_paths(router):
        if router_type == "domain" and _is_forbidden(relative):
            errors.append(f"forbidden router reference: {relative}")
            continue
        target = base / relative
        if not _is_within(target, base):
            errors.append(f"router reference escapes base directory: {relative}")
        elif not target.is_file():
            errors.append(f"router reference does not exist: {relative}")

    return {"valid": not errors, "errors": errors, "router_type": router_type}


def validate_router_file(
    router_path: str | Path, knowledge_base_root: str | Path
) -> dict[str, Any]:
    """Load and validate a router YAML file."""
    path = Path(router_path)
    root = Path(knowledge_base_root)
    try:
        router = _load_yaml(path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return {"valid": False, "errors": [f"load: {exc}"], "router_type": None}
    return validate_router_data(router, path, root)


def route_request(
    root_router: dict[str, Any], request: str, explicit_domain: str | None = None
) -> dict[str, Any]:
    """Select a domain or require confirmation when the request is ambiguous."""
    if root_router.get("router_type") != "root":
        return {"status": "invalid_router", "error": "route_request requires a root router"}

    domains = root_router.get("domains", [])
    by_slug = {domain["slug"]: domain for domain in domains}
    if explicit_domain is not None:
        if explicit_domain not in by_slug:
            return {
                "status": "invalid_domain",
                "domain": explicit_domain,
                "candidates": sorted(by_slug),
            }
        return {"status": "selected", "domain": explicit_domain, "reason": "explicit"}

    normalized = request.casefold()
    scores: dict[str, int] = {}
    for domain in domains:
        terms = [domain["slug"], domain["name"]]
        terms.extend(domain.get("aliases", []))
        terms.extend(domain.get("keywords", []))
        score = sum(1 for term in set(terms) if term.casefold() in normalized)
        if score:
            scores[domain["slug"]] = score

    if scores:
        highest = max(scores.values())
        candidates = sorted(slug for slug, score in scores.items() if score == highest)
        if len(candidates) == 1:
            return {"status": "selected", "domain": candidates[0], "reason": "keyword_match"}
        return {
            "status": "needs_confirmation",
            "candidates": candidates,
            "reason": "ambiguous_domain_match",
        }

    default = root_router.get("default_domain")
    if default in by_slug:
        return {"status": "selected", "domain": default, "reason": "default"}
    if len(domains) == 1:
        return {"status": "selected", "domain": domains[0]["slug"], "reason": "only_domain"}
    return {
        "status": "needs_confirmation",
        "candidates": sorted(by_slug),
        "reason": "no_domain_match",
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("router", type=Path, help="Router YAML path")
    parser.add_argument("--kb-root", type=Path, required=True, help="Knowledge-base root")
    parser.add_argument("--request", help="Optional request text for root-domain preflight")
    parser.add_argument("--domain", help="Explicit domain slug")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    result = validate_router_file(args.router, args.kb_root)
    if result["valid"] and args.request is not None:
        router = _load_yaml(args.router)
        result["routing"] = route_request(router, args.request, args.domain)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["valid"]:
        return 1
    if result.get("routing", {}).get("status") == "needs_confirmation":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
