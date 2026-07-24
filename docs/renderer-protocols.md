# Renderer Protocols

## 选择Renderer

| 目标 | Renderer | 核心验收 |
|---|---|---|
| 通用文本协作 | Portable Markdown | 表格、Requirement标记、降级 |
| 高保真Office文档 | DOCX | OOXML原生编号、独立numId、视觉预览 |
| 在线协作文档 | Native Block Plan | Block顺序、Logic深度、平台能力 |

## 不提供固定Renderer代码

这不是少做，而是故意的：不同Agent拥有不同文件工具、Office环境和MCP。仓库固定的是输入输出协议、Fixtures和验证标准，而不是一段注定在另一台机器失效的胶水代码。

## Markdown验收

```bash
.venv/bin/python validators/validate_markdown.py \
  fixtures/simple-prd/output.md \
  --ir fixtures/simple-prd/prd-ir.yaml \
  --manifest fixtures/simple-prd/render-manifest.yaml
```

Portable Markdown无法保证表格单元格内原生多级列表，所以必须在Manifest报告降级，不能只追求外观看起来像。

## DOCX验收

```bash
.venv/bin/python validators/validate_docx_structure.py \
  templates/golden/neutral-prd-template.docx
```

验证器检查：

- DOCX关键Part；
- `numbering.xml`；
- `numPr`；
- 每个逻辑单元格独立`numId`；
- 首段从level 0开始；
- 三级编号定义。

结构通过后仍需Quick Look、Word或LibreOffice视觉检查。

## Block Plan验收

```bash
.venv/bin/python validators/validate_block_plan.py \
  fixtures/nested-logic/block-plan.yaml \
  --ir fixtures/nested-logic/prd-ir.yaml \
  --manifest fixtures/nested-logic/render-manifest.yaml
```

Logic Block必须与IR的`logic_id`、顺序和depth逐项一致。

## 状态含义

- `failed`：Required能力不足或渲染失败；
- `rendered`：产生文件，但尚未完成结构验收；
- `ready_for_review`：结构通过，需要视觉或用户检查；
- `ready_for_publish`：Required能力与规定验收全部通过。

## Golden Template

中性Golden DOCX只包含中性标题、四列表格、原生三级编号和无业务含义的占位文字。它不包含品牌、内部字段、作者信息、评论、修订或真实业务图片。
