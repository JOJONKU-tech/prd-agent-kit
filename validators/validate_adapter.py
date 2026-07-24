#!/usr/bin/env python3
"""Validate document adapters, publish plans, and publication receipts."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlsplit

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "adapter": ROOT / "schemas/document-adapter.schema.json",
    "plan": ROOT / "schemas/publish-plan.schema.json",
    "receipt": ROOT / "schemas/publication-receipt.schema.json",
}
CREDENTIAL_KEY = re.compile(r"(?:authorization|cookie|password|secret|token|api[_-]?key|credential|private[_-]?key)", re.I)
SIGNED_QUERY_PREFIX = "q-" + "sign-"
CREDENTIAL_VALUE = re.compile(r"(?:^Bearer\s+|^Basic\s+|X-Amz-Signature=|" + re.escape(SIGNED_QUERY_PREFIX) + r"|(?:token|secret|signature|password)=)", re.I)
VERSIONED_TITLE = re.compile(r"\sV(?:[2-9]|[1-9][0-9]+)$")
DESTRUCTIVE_TOOL = re.compile(r"(?:^|[._-])(?:delete|remove|destroy|permission|share|move)(?:[._-]|$)", re.I)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _load_yaml(path: Path) -> dict[str, Any]:
    data=yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data,dict): raise ValueError(f"YAML root must be an object: {path}")
    return data


def _schema_errors(data: dict[str, Any], schema_path: Path) -> list[str]:
    schema=json.loads(schema_path.read_text(encoding="utf-8"));validator=jsonschema.Draft202012Validator(schema);errors=[]
    for error in sorted(validator.iter_errors(data),key=lambda item:list(item.absolute_path)):
        location=".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"schema:{location}: {error.message}")
    return errors


def _credential_errors(value: Any, path: str="$" ) -> list[str]:
    errors=[]
    if isinstance(value,dict):
        for key,item in value.items():
            item_path=f"{path}.{key}"
            if CREDENTIAL_KEY.search(str(key)): errors.append(f"embedded credential field is forbidden: {item_path}")
            errors.extend(_credential_errors(item,item_path))
    elif isinstance(value,list):
        for index,item in enumerate(value): errors.extend(_credential_errors(item,f"{path}[{index}]"))
    elif isinstance(value,str) and CREDENTIAL_VALUE.search(value):
        errors.append(f"embedded credential value is forbidden: {path}")
    return errors


def _url_errors(url: Any, path: str) -> list[str]:
    if url is None:return []
    if not isinstance(url,str):return [f"URL must be a string: {path}"]
    errors=[];parts=urlsplit(url)
    if parts.username or parts.password:errors.append(f"credential-bearing URL is forbidden: {path}")
    if CREDENTIAL_VALUE.search(url):errors.append(f"signed or credential URL is forbidden: {path}")
    return errors


def validate_adapter_data(adapter: dict[str, Any]) -> dict[str, Any]:
    errors=_schema_errors(adapter,SCHEMAS["adapter"]);errors.extend(_credential_errors(adapter))
    capabilities=_as_dict(adapter.get("capabilities"))
    for capability,mapping in capabilities.items():
        tool=_as_dict(mapping).get("tool")
        if isinstance(tool,str) and DESTRUCTIVE_TOOL.search(tool):
            errors.append(f"destructive tool mapping is forbidden: capabilities.{capability}.tool")
    status=adapter.get("verification_status")
    if status in {"write_verified","structure_verified"}:
        sandbox=_as_dict(adapter.get("sandbox"))
        if not sandbox.get("test_document_id") or not sandbox.get("last_verified_at"):
            errors.append("write_verified adapter requires a completed sandbox document and verification time")
    return {"valid":not errors,"errors":errors,"verification_status":status}


def validate_adapter_file(path: str | Path) -> dict[str, Any]:
    try:data=_load_yaml(Path(path))
    except (OSError,ValueError,yaml.YAMLError) as exc:return {"valid":False,"errors":[f"load: {exc}"],"verification_status":None}
    return validate_adapter_data(data)


def compute_plan_hash(plan: dict[str, Any]) -> str:
    """Hash the plan while normalizing mutable confirmation metadata."""
    payload=deepcopy(plan)
    confirmation=_as_dict(payload.get("confirmation"))
    confirmation.update({"required":True,"status":"pending","plan_sha256":None,"confirmed_at":None})
    payload["confirmation"]=confirmation
    encoded=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_publish_plan_data(plan: dict[str, Any]) -> dict[str, Any]:
    errors=_schema_errors(plan,SCHEMAS["plan"]);errors.extend(_credential_errors(plan))
    confirmation=_as_dict(plan.get("confirmation"))
    if confirmation.get("status")=="confirmed":
        expected=compute_plan_hash(plan)
        if confirmation.get("plan_sha256")!=expected:errors.append("confirmation plan_sha256 does not match the current publish plan")
        if not confirmation.get("confirmed_at"):errors.append("confirmed plan requires confirmed_at")
    if plan.get("status") in {"publishing","partial","published_unverified","published_verified"} and confirmation.get("status")!="confirmed":
        errors.append("publishing or published status requires a confirmed Gate 2 plan")
    operation=_as_dict(plan.get("operation"))
    target=_as_dict(plan.get("target"))
    executed=operation.get("executed")
    if executed=="update" and not target.get("document_id"):errors.append("update operation requires an explicit document_id")
    if executed=="create_new_version":
        if operation.get("requested")!="update":errors.append("create_new_version is only valid as an update fallback")
        if not operation.get("fallback_reason"):errors.append("create_new_version requires fallback_reason")
        if not VERSIONED_TITLE.search(str(target.get("title") or "")):errors.append("create_new_version title must end with V2/V3 or a higher integer version")
    compatibility=_as_dict(plan.get("compatibility"))
    required=_as_dict(compatibility.get("required"))
    unsupported=[name for name,status in required.items() if status!="supported"]
    if unsupported:errors.append("publish plan contains unsupported required capabilities: "+", ".join(sorted(unsupported)))
    side_effects=_as_dict(plan.get("side_effects"))
    if side_effects.get("delete_documents",0)!=0:errors.append("publish plan may not delete documents")
    if executed in {"create","create_new_version"} and (side_effects.get("create_documents")!=1 or side_effects.get("update_documents")!=0):
        errors.append("side_effects must declare one created document and zero updated documents")
    if executed=="update" and (side_effects.get("create_documents")!=0 or side_effects.get("update_documents")!=1):
        errors.append("side_effects must declare zero created documents and one updated document")
    assets=_as_dict(plan.get("assets"))
    if isinstance(assets.get("count"),int) and side_effects.get("upload_assets")!=assets.get("count"):
        errors.append("side_effects upload_assets must match assets count")
    return {"valid":not errors,"errors":errors,"computed_plan_sha256":compute_plan_hash(plan)}


def validate_publish_plan_file(path: str | Path) -> dict[str, Any]:
    try:data=_load_yaml(Path(path))
    except (OSError,ValueError,yaml.YAMLError) as exc:return {"valid":False,"errors":[f"load: {exc}"]}
    return validate_publish_plan_data(data)


def validate_receipt_data(receipt: dict[str, Any]) -> dict[str, Any]:
    errors=_schema_errors(receipt,SCHEMAS["receipt"]);errors.extend(_credential_errors(receipt))
    document=_as_dict(receipt.get("document"))
    errors.extend(_url_errors(document.get("url"),"document.url"))
    status=receipt.get("status");verification=_as_dict(receipt.get("verification"))
    if status=="published_verified" and verification.get("result")!="passed":errors.append("published_verified receipt requires passed verification")
    if status in {"published_verified","published_unverified"} and not document.get("id"):errors.append("published receipt requires document id")
    return {"valid":not errors,"errors":errors}


def validate_receipt_file(path: str | Path) -> dict[str, Any]:
    try:data=_load_yaml(Path(path))
    except (OSError,ValueError,yaml.YAMLError) as exc:return {"valid":False,"errors":[f"load: {exc}"]}
    return validate_receipt_data(data)


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("kind",choices=sorted(SCHEMAS));parser.add_argument("path",type=Path);args=parser.parse_args(argv)
    funcs={"adapter":validate_adapter_file,"plan":validate_publish_plan_file,"receipt":validate_receipt_file};result=funcs[args.kind](args.path);print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result["valid"] else 1


if __name__=="__main__":sys.exit(main())
