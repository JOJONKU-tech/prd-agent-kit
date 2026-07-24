#!/usr/bin/env python3
"""Mechanical release-readiness checks for the public repository."""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tarfile
from typing import Any, Iterable
import zipfile

import jsonschema
import yaml


IGNORED_PARTS = {".git", ".venv", "__pycache__", ".playwright-mcp"}
REQUIRED_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "LICENSE",
    "README.md",
    "README.en.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "compatibility.yaml",
    "docs/architecture.md",
    "docs/getting-started.md",
    "docs/troubleshooting.md",
    "docs/release-checklist.md",
    ".github/workflows/ci.yml",
)
GENERIC_FORBIDDEN: tuple[str, ...] = ()
HOME_PATH = re.compile(r"/(?:Users|home)/[^/\s]+")
SIGNED_QUERY_PREFIX = "q-" + "sign-"
SIGNED_AMAZON_PARAMETER = "X-Amz-" + "Signature="
CREDENTIAL_VALUE = re.compile(
    r"(?:^|[\s:=])(?:Bearer\s+[A-Za-z0-9._-]{6,}|AKID[A-Za-z0-9_-]{10,}|"
    + re.escape(SIGNED_QUERY_PREFIX)
    + "|"
    + re.escape(SIGNED_AMAZON_PARAMETER)
    + ")",
    re.I,
)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REVISION_TAG = re.compile(r"<w:(?:ins|del)(?:\s|>)")


def _iter_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.parts)
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_extra_terms(explicit: Iterable[str] | None) -> list[str]:
    terms = [term.strip() for term in (explicit or []) if term.strip()]
    env_terms = os.environ.get("PRD_AGENT_KIT_EXTRA_FORBIDDEN_TERMS", "")
    terms.extend(term.strip() for term in env_terms.split(",") if term.strip())
    return sorted(set(terms))


def _normalized_fingerprint(value: str) -> str:
    return re.sub(r"[\s\"'`+._-]+", "", value).lower()


def _history_variants(term: str) -> tuple[str, ...]:
    encoded = term.encode("utf-8")
    return (
        term.lower(),
        base64.b64encode(encoded).decode("ascii").lower(),
        encoded.hex().lower(),
    )


def _matches_forbidden(term: str, name: str, text: str) -> bool:
    lower_name = name.lower()
    lower_text = text.lower()
    variants = _history_variants(term)
    normalized_term = _normalized_fingerprint(term)
    return (
        any(variant in lower_name or variant in lower_text for variant in variants)
        or normalized_term in _normalized_fingerprint(name)
        or normalized_term in _normalized_fingerprint(text)
    )


def _check_reachable_git_history(root: Path, terms: list[str], errors: list[str]) -> None:
    if not terms or not (root / ".git").exists():
        return
    revisions = subprocess.run(
        ["git", "rev-list", "--all"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if revisions.returncode != 0:
        errors.append("cannot enumerate reachable Git history")
        return

    pending = set(terms)
    refs = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname)"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if refs.returncode == 0:
        for term in tuple(pending):
            if _matches_forbidden(term, refs.stdout, ""):
                errors.append(f"forbidden term in reachable Git history: {term} (ref name)")
                pending.remove(term)

    for commit in revisions.stdout.splitlines():
        if not pending:
            break
        message = subprocess.run(
            ["git", "show", "-s", "--format=%B", commit],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if message.returncode != 0:
            errors.append(f"cannot inspect reachable Git commit message: {commit}")
        else:
            for term in tuple(pending):
                if _matches_forbidden(term, commit, message.stdout):
                    errors.append(
                        f"forbidden term in reachable Git history: {term} ({commit[:12]}:commit message)"
                    )
                    pending.remove(term)
        if not pending:
            break
        archive = subprocess.run(
            ["git", "archive", "--format=tar", commit],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if archive.returncode != 0:
            errors.append(f"cannot inspect reachable Git commit: {commit}")
            continue
        with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as bundle:
            for member in bundle.getmembers():
                if not member.isfile() or not pending:
                    continue
                extracted = bundle.extractfile(member)
                payload = extracted.read() if extracted is not None else b""
                text = payload.decode("utf-8", "ignore")
                for term in tuple(pending):
                    if _matches_forbidden(term, member.name, text):
                        errors.append(
                            f"forbidden term in reachable Git history: {term} ({commit[:12]}:{member.name})"
                        )
                        pending.remove(term)


def _check_docx(path: Path, errors: list[str], relative: str) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            if "word/comments.xml" in names:
                errors.append(f"DOCX comments are forbidden: {relative}")
            xml = b"\n".join(
                archive.read(name)
                for name in names
                if name.endswith((".xml", ".rels"))
            ).decode("utf-8", "ignore")
            if REVISION_TAG.search(xml):
                errors.append(f"DOCX tracked revisions are forbidden: {relative}")
            if HOME_PATH.search(xml):
                errors.append(f"DOCX contains an absolute home path: {relative}")
            if CREDENTIAL_VALUE.search(xml):
                errors.append(f"DOCX contains a credential-like value: {relative}")
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"invalid DOCX {relative}: {exc}")


def _check_png(path: Path, errors: list[str], relative: str) -> None:
    try:
        data = path.read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            errors.append(f"invalid PNG signature: {relative}")
            return
        offset = 8
        metadata_chunks: list[str] = []
        while offset + 12 <= len(data):
            size = struct.unpack(">I", data[offset : offset + 4])[0]
            kind = data[offset + 4 : offset + 8].decode("ascii", "replace")
            if kind in {"tEXt", "zTXt", "iTXt", "eXIf"}:
                metadata_chunks.append(kind)
            offset += 12 + size
            if kind == "IEND":
                break
        if metadata_chunks:
            errors.append(
                f"PNG metadata chunks are forbidden in {relative}: {', '.join(metadata_chunks)}"
            )
    except OSError as exc:
        errors.append(f"cannot inspect PNG {relative}: {exc}")


def _check_markdown_links(path: Path, root: Path, text: str, errors: list[str]) -> None:
    relative = str(path.relative_to(root))
    for target in MARKDOWN_LINK.findall(text):
        target = target.strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#", "file://")):
            continue
        destination = (path.parent / target.split("#", 1)[0]).resolve()
        try:
            destination.relative_to(root.resolve())
        except ValueError:
            errors.append(f"Markdown link escapes repository: {relative} -> {target}")
            continue
        if not destination.exists():
            errors.append(f"broken Markdown link: {relative} -> {target}")


def _check_source_hashes(root: Path, path: Path, data: Any, errors: list[str]) -> None:
    if path.name != "manifest.yaml" or "sources" not in path.parts:
        return
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        return
    for item in data["sources"]:
        if not isinstance(item, dict):
            continue
        location = item.get("location")
        expected = item.get("sha256")
        if not isinstance(location, str) or not isinstance(expected, str):
            continue
        source = (path.parent / location).resolve()
        if not source.is_file():
            errors.append(f"source manifest path missing: {path.relative_to(root)} -> {location}")
        elif _sha256(source) != expected:
            errors.append(f"source manifest hash mismatch: {item.get('source_id', location)}")


def _check_render_hashes(root: Path, path: Path, data: Any, errors: list[str]) -> None:
    if not path.name.startswith("render-manifest") or not isinstance(data, dict):
        return
    outputs = data.get("outputs")
    if not isinstance(outputs, list):
        return
    for item in outputs:
        if not isinstance(item, dict):
            continue
        output_path = item.get("path")
        expected = item.get("sha256")
        if not isinstance(output_path, str) or not isinstance(expected, str):
            continue
        output = (root / output_path).resolve()
        if not output.is_file():
            errors.append(f"render output missing: {output_path}")
        elif _sha256(output) != expected:
            errors.append(f"render output hash mismatch: {output_path}")


def _check_golden_hash(root: Path, path: Path, data: Any, errors: list[str]) -> None:
    if not path.name.endswith(".manifest.yaml") or not isinstance(data, dict):
        return
    template_file = data.get("template_file")
    expected = data.get("sha256")
    if isinstance(template_file, str) and isinstance(expected, str):
        template = path.parent / template_file
        if not template.is_file() or _sha256(template) != expected:
            errors.append(f"golden template hash mismatch: {path.relative_to(root)}")


def validate_release_readiness(
    root: str | Path,
    extra_forbidden_terms: Iterable[str] | None = None,
) -> dict[str, Any]:
    base = Path(root).resolve()
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (base / relative).is_file():
            errors.append(f"missing release file: {relative}")

    files = _iter_files(base)
    forbidden_terms = list(GENERIC_FORBIDDEN) + _load_extra_terms(extra_forbidden_terms)

    for path in files:
        relative = str(path.relative_to(base))
        lower_name = relative.lower()
        for term in forbidden_terms:
            if term.lower() in lower_name:
                errors.append(f"forbidden term in filename: {relative}")

        if path.suffix.lower() == ".docx":
            _check_docx(path, errors, relative)
            continue
        if path.suffix.lower() == ".png":
            _check_png(path, errors, relative)
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for term in forbidden_terms:
            if term.lower() in text.lower():
                errors.append(f"forbidden term in {relative}")
        if HOME_PATH.search(text):
            errors.append(f"absolute home path in {relative}")
        if CREDENTIAL_VALUE.search(text):
            errors.append(f"credential-like value in {relative}")

        if path.suffix.lower() == ".md":
            _check_markdown_links(path, base, text, errors)
        if path.suffix.lower() == ".json":
            try:
                data = json.loads(text)
                if path.name.endswith(".schema.json"):
                    jsonschema.Draft202012Validator.check_schema(data)
            except (json.JSONDecodeError, jsonschema.SchemaError) as exc:
                errors.append(f"invalid JSON/Schema {relative}: {exc}")
        elif path.suffix.lower() in {".yaml", ".yml"} or path.name.endswith(".yaml.example"):
            try:
                data = yaml.safe_load(text)
                _check_source_hashes(base, path, data, errors)
                _check_render_hashes(base, path, data, errors)
                _check_golden_hash(base, path, data, errors)
            except yaml.YAMLError as exc:
                errors.append(f"invalid YAML {relative}: {exc}")

    _check_reachable_git_history(base, forbidden_terms, errors)

    license_path = base / "LICENSE"
    if license_path.is_file() and "MIT License" not in license_path.read_text(encoding="utf-8"):
        errors.append("LICENSE is not MIT")

    compatibility_path = base / "compatibility.yaml"
    runtimes = 0
    if compatibility_path.is_file():
        data = yaml.safe_load(compatibility_path.read_text(encoding="utf-8")) or {}
        runtime_data = data.get("runtimes") if isinstance(data, dict) else {}
        if isinstance(runtime_data, dict):
            runtimes = len(runtime_data)
            for runtime, item in runtime_data.items():
                if not isinstance(item, dict) or item.get("e2e") != "not_run":
                    errors.append(f"dishonest or malformed E2E status: {runtime}")

    forbidden_renderers = {
        "render_markdown.py",
        "render_docx.py",
        "render_feishu.py",
    }
    committed_names = {path.name for path in files}
    for name in sorted(forbidden_renderers & committed_names):
        errors.append(f"fixed renderer implementation is forbidden: {name}")

    architecture = base / "docs/architecture.md"
    if architecture.is_file() and "Repository Not Created" in architecture.read_text(encoding="utf-8"):
        errors.append("architecture status is stale")

    return {
        "valid": not errors,
        "errors": sorted(set(errors)),
        "checked_files": len(files),
        "runtimes": runtimes,
    }


def _run_command(command: list[str], root: Path) -> tuple[bool, str]:
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode == 0, completed.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--run-tests", action="store_true", help="Run unittest and Python compile checks")
    args = parser.parse_args(argv)

    result = validate_release_readiness(args.root)
    test_results: dict[str, Any] = {}
    if args.run_tests:
        commands = {
            "unittest": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
            "py_compile": [
                sys.executable,
                "-m",
                "compileall",
                "-q",
                "validators",
                "tests",
            ],
        }
        for name, command in commands.items():
            passed, output = _run_command(command, args.root)
            test_results[name] = {"passed": passed, "output": output[-4000:]}
            if not passed:
                result["errors"].append(f"{name} failed")
        result["valid"] = not result["errors"]
    result["test_results"] = test_results
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
