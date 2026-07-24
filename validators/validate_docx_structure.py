#!/usr/bin/env python3
"""Inspect DOCX OOXML for native numbered paragraphs and independent logic cells."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile
from xml.etree import ElementTree as ET


NS={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W=f"{{{NS['w']}}}"


def _attr(element: ET.Element | None, name: str) -> str | None:
    return None if element is None else element.get(W+name)


def validate_docx_structure(path: str | Path) -> dict[str, object]:
    docx_path=Path(path);errors=[]
    try:
        with zipfile.ZipFile(docx_path) as archive:
            names=set(archive.namelist())
            required={"[Content_Types].xml","word/document.xml","word/styles.xml","word/numbering.xml"}
            missing=sorted(required-names)
            if missing:return {"valid":False,"errors":[f"missing DOCX part: {item}" for item in missing],"numbered_paragraphs":0,"logic_cells":0,"independent_num_ids":False,"max_level":0}
            document=ET.fromstring(archive.read("word/document.xml"));numbering=ET.fromstring(archive.read("word/numbering.xml"))
    except (OSError,zipfile.BadZipFile,ET.ParseError) as exc:
        return {"valid":False,"errors":[f"load: {exc}"],"numbered_paragraphs":0,"logic_cells":0,"independent_num_ids":False,"max_level":0}

    defined_num_ids={_attr(item,"numId") for item in numbering.findall("w:num",NS)}
    abstract_levels={}
    for abstract in numbering.findall("w:abstractNum",NS):
        abstract_id=_attr(abstract,"abstractNumId")
        abstract_levels[abstract_id]={int(_attr(level,"ilvl") or 0) for level in abstract.findall("w:lvl",NS)}
    num_to_abstract={}
    for item in numbering.findall("w:num",NS):
        abstract=item.find("w:abstractNumId",NS)
        num_to_abstract[_attr(item,"numId")]=_attr(abstract,"val")

    numbered=0;logic_cells=0;first_num_ids=[];levels=[]
    for cell in document.findall(".//w:tc",NS):
        cell_numbering=[]
        for paragraph in cell.findall("w:p",NS):
            num_pr=paragraph.find("w:pPr/w:numPr",NS)
            if num_pr is None:continue
            num_id=_attr(num_pr.find("w:numId",NS),"val")
            level_text=_attr(num_pr.find("w:ilvl",NS),"val")
            level=int(level_text or 0)
            numbered+=1;levels.append(level);cell_numbering.append((num_id,level))
            if num_id not in defined_num_ids:errors.append(f"paragraph references undefined numId: {num_id}")
            abstract_id=num_to_abstract.get(num_id)
            if abstract_id not in abstract_levels or level not in abstract_levels[abstract_id]:errors.append(f"numbering level {level} is undefined for numId {num_id}")
        if cell_numbering:
            logic_cells+=1;first_num_ids.append(cell_numbering[0][0])
            if cell_numbering[0][1]!=0:errors.append("logic cell numbering must restart at level 0")
            if any(item[0]!=cell_numbering[0][0] for item in cell_numbering):errors.append("one logic cell must use one independent numId")
    independent=len(first_num_ids)>=2 and len(first_num_ids)==len(set(first_num_ids))
    if logic_cells<2:errors.append("Golden DOCX requires at least two numbered logic cells")
    if not independent:errors.append("logic cells must use independent numIds")
    if max(levels,default=0)<2:errors.append("Golden DOCX must demonstrate three numbering levels")
    return {"valid":not errors,"errors":errors,"numbered_paragraphs":numbered,"logic_cells":logic_cells,"independent_num_ids":independent,"max_level":max(levels,default=0)}


def main(argv: list[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("docx",type=Path);args=parser.parse_args(argv);result=validate_docx_structure(args.docx);print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result["valid"] else 1


if __name__=="__main__":sys.exit(main())
