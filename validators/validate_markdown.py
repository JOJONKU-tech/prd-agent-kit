#!/usr/bin/env python3
"""Validate portable Markdown output against PRD IR and render manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

import yaml

try:
    from validators.validate_render_manifest import validate_render_manifest_data
except ModuleNotFoundError:
    from validate_render_manifest import validate_render_manifest_data


REQUIREMENT_MARKER = re.compile(r"<!--\s*requirement:([A-Za-z0-9._-]+)\s*-->")
MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def _load_yaml(path: Path) -> dict[str, Any]:
    data=yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data,dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return data


def _split_row(line: str) -> list[str]:
    text=line.strip()
    if text.startswith("|"): text=text[1:]
    if text.endswith("|"): text=text[:-1]
    cells=[]; current=[]; escaped=False
    for char in text:
        if escaped:
            current.append(char); escaped=False
        elif char=="\\":
            current.append(char); escaped=True
        elif char=="|":
            cells.append("".join(current).strip()); current=[]
        else:
            current.append(char)
    cells.append("".join(current).strip())
    return cells


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_markdown_file(markdown_path: str | Path, ir_path: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    md_path=Path(markdown_path); ir_file=Path(ir_path); manifest_file=Path(manifest_path)
    errors=[]
    try:
        text=md_path.read_text(encoding="utf-8")
        ir=_load_yaml(ir_file)
        manifest=_load_yaml(manifest_file)
    except (OSError,ValueError,yaml.YAMLError) as exc:
        return {"valid":False,"errors":[f"load: {exc}"],"requirement_rows":0}

    manifest_result=validate_render_manifest_data(manifest)
    errors.extend(f"manifest: {item}" for item in manifest_result["errors"])
    if manifest.get("renderer")!="markdown": errors.append("manifest renderer must be markdown")
    expected_hash=manifest.get("input",{}).get("prd_ir_sha256")
    if expected_hash and expected_hash!=_sha256(ir_file): errors.append("manifest PRD IR hash does not match")
    outputs=manifest.get("outputs")
    outputs=outputs if isinstance(outputs,list) else []
    output_hash=outputs[0].get("sha256") if outputs and isinstance(outputs[0],dict) else None
    if output_hash and output_hash!=_sha256(md_path): errors.append("manifest output hash does not match Markdown file")
    if "｜" in text: errors.append("fullwidth table pipe is forbidden")

    first_table_columns=0
    current_table_columns=None
    for line_number,line in enumerate(text.splitlines(),1):
        if not line.lstrip().startswith("|"):
            current_table_columns=None
            continue
        columns=len(_split_row(line))
        if current_table_columns is None:
            current_table_columns=columns
            if first_table_columns==0: first_table_columns=columns
        elif columns!=current_table_columns:
            errors.append(f"table column mismatch at line {line_number}: expected {current_table_columns}, got {columns}")

    expected_ids=[item.get("requirement_id") for item in ir.get("requirements",[]) if isinstance(item,dict)]
    markers=REQUIREMENT_MARKER.findall(text)
    if markers!=expected_ids:
        errors.append(f"requirement markers do not match IR order: expected {expected_ids}, got {markers}")

    for source in MARKDOWN_IMAGE.findall(text):
        if re.match(r"^https?://",source,re.I): continue
        if not (md_path.parent/source).resolve().is_file(): errors.append(f"Markdown image does not exist: {source}")

    return {"valid":not errors,"errors":errors,"requirement_rows":len(markers),"table_columns":first_table_columns}


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown",type=Path);parser.add_argument("--ir",type=Path,required=True);parser.add_argument("--manifest",type=Path,required=True)
    args=parser.parse_args(argv)
    result=validate_markdown_file(args.markdown,args.ir,args.manifest)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["valid"] else 1


if __name__=="__main__": sys.exit(main())
