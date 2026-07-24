#!/usr/bin/env python3
"""Statically validate cross-agent entry files and honest compatibility claims."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import yaml


RUNTIMES = ("claude-code", "codex", "hermes")
REQUIRED_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "compatibility.yaml",
    "protocols/skill-installation.md",
    "templates/wrappers/wrapper-template.md",
    "templates/wrappers/installation.example.yaml",
    "platforms/claude/README.md",
    "platforms/codex/README.md",
    "platforms/hermes/README.md",
    "docs/testing/e2e/claude-code.md",
    "docs/testing/e2e/codex.md",
    "docs/testing/e2e/hermes.md",
)
E2E_TERMS = ("temporary HOME", "AGENTS.md", "Gate 1", "Wrapper", "new session", "Gate 2", "not_run")


def _frontmatter_keys(text: str) -> set[str]:
    if not text.startswith("---\n") or "\n---\n" not in text:
        return set()
    frontmatter = text.split("---", 2)[1]
    return {
        line.split(":", 1)[0].strip()
        for line in frontmatter.splitlines()
        if ":" in line and not line.startswith((" ", "\t"))
    }


def validate_repository_compatibility(root: str | Path) -> dict[str, Any]:
    base = Path(root)
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (base / relative).is_file():
            errors.append(f"missing compatibility file: {relative}")

    claude = base / "CLAUDE.md"
    if claude.is_file() and claude.read_text(encoding="utf-8") != "@AGENTS.md\n":
        errors.append("CLAUDE.md must contain only @AGENTS.md")

    skill = base / "skills/prd-knowledge-engineering/SKILL.md"
    if skill.is_file() and _frontmatter_keys(skill.read_text(encoding="utf-8")) != {"name", "description"}:
        errors.append("canonical skill must use only shared name/description frontmatter")

    wrapper = base / "templates/wrappers/wrapper-template.md"
    if wrapper.is_file():
        text = wrapper.read_text(encoding="utf-8")
        for marker in ("{{skill_name}}", "{{canonical_skill_path}}", "Verify the file exists"):
            if marker not in text:
                errors.append(f"wrapper template missing marker: {marker}")
        if "allowed-tools:" in text:
            errors.append("generic wrapper may not contain Claude-only allowed-tools")

    compatibility_path = base / "compatibility.yaml"
    e2e_values: set[str] = set()
    runtimes = 0
    if compatibility_path.is_file():
        data = yaml.safe_load(compatibility_path.read_text(encoding="utf-8")) or {}
        runtime_data = data.get("runtimes") if isinstance(data, dict) else {}
        runtime_data = runtime_data if isinstance(runtime_data, dict) else {}
        for runtime in RUNTIMES:
            item = runtime_data.get(runtime)
            if not isinstance(item, dict):
                errors.append(f"compatibility entry missing: {runtime}")
                continue
            runtimes += 1
            e2e_values.add(str(item.get("e2e")))
            if item.get("e2e") != "not_run":
                errors.append(f"E2E status must remain not_run until real execution: {runtime}")
            if item.get("mcp_setup") != "documented":
                errors.append(f"MCP setup must be documented: {runtime}")

    for runtime in RUNTIMES:
        manual = base / "docs/testing/e2e" / f"{runtime}.md"
        if not manual.is_file():
            continue
        text = manual.read_text(encoding="utf-8")
        for term in E2E_TERMS:
            if term not in text:
                errors.append(f"{runtime} E2E manual missing: {term}")

    return {
        "valid": not errors,
        "errors": errors,
        "runtimes": runtimes,
        "e2e_status": next(iter(e2e_values)) if len(e2e_values) == 1 else "mixed",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    result = validate_repository_compatibility(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
