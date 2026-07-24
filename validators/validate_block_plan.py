#!/usr/bin/env python3
"""Validate a native document Block Plan against PRD IR and render manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import yaml

try:
    from validators.validate_render_manifest import validate_render_manifest_data
except ModuleNotFoundError:
    from validate_render_manifest import validate_render_manifest_data


def _load(path: Path) -> dict[str, Any]:
    data=yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data,dict): raise ValueError(f"YAML root must be an object: {path}")
    return data


def _walk(nodes: Any, depth: int=0):
    if not isinstance(nodes,list): return
    for node in nodes:
        if not isinstance(node,dict): continue
        yield node,depth
        yield from _walk(node.get("children",[]),depth+1)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_block_plan_file(plan_path: str | Path, ir_path: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    plan_file=Path(plan_path);ir_file=Path(ir_path);manifest_file=Path(manifest_path);errors=[]
    try:
        plan=_load(plan_file);ir=_load(ir_file);manifest=_load(manifest_file)
    except (OSError,ValueError,yaml.YAMLError) as exc:
        return {"valid":False,"errors":[f"load: {exc}"],"logic_blocks":0,"max_depth":0}
    manifest_result=validate_render_manifest_data(manifest)
    errors.extend(f"manifest: {item}" for item in manifest_result["errors"])
    if manifest.get("renderer")!="feishu_blocks": errors.append("manifest renderer must be feishu_blocks")
    if manifest.get("input",{}).get("prd_ir_sha256")!=_sha(ir_file): errors.append("manifest PRD IR hash does not match")
    outputs=manifest.get("outputs")
    outputs=outputs if isinstance(outputs,list) else []
    output_hash=outputs[0].get("sha256") if outputs and isinstance(outputs[0],dict) else None
    if output_hash and output_hash!=_sha(plan_file): errors.append("manifest output hash does not match Block Plan file")
    if plan.get("schema_version")!="1.0": errors.append("block plan schema_version must be 1.0")
    if not isinstance(plan.get("document"),dict): errors.append("block plan document must be an object")
    blocks=plan.get("blocks")
    if not isinstance(blocks,list):
        return {"valid":False,"errors":[*errors,"block plan blocks must be an array"],"logic_blocks":0,"max_depth":0}

    expected=[]
    for requirement in ir.get("requirements",[]):
        if isinstance(requirement,dict): expected.extend((node.get("logic_id"),depth) for node,depth in _walk(requirement.get("logic",[])))
    actual=[]
    for block in blocks:
        if not isinstance(block,dict): continue
        if block.get("logic_id") is not None:
            if block.get("type")!="ordered_list": errors.append(f"logic block must be ordered_list: {block.get('logic_id')}")
            depth=block.get("depth")
            if not isinstance(depth,int) or depth<0 or depth>2: errors.append(f"logic block depth must be 0..2: {block.get('logic_id')}")
            actual.append((block.get("logic_id"),depth))
    if actual!=expected: errors.append(f"logic blocks do not match IR order/depth: expected {expected}, got {actual}")
    ids=[block.get("id") for block in blocks if isinstance(block,dict) and isinstance(block.get("id"),str)]
    if len(ids)!=len(set(ids)): errors.append("block ids must be unique")
    max_depth=max((depth for _,depth in actual if isinstance(depth,int)),default=0)
    return {"valid":not errors,"errors":errors,"logic_blocks":len(actual),"max_depth":max_depth}


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("plan",type=Path);parser.add_argument("--ir",type=Path,required=True);parser.add_argument("--manifest",type=Path,required=True);args=parser.parse_args(argv)
    result=validate_block_plan_file(args.plan,args.ir,args.manifest);print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result["valid"] else 1


if __name__=="__main__":sys.exit(main())
