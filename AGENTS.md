# prd-agent-kit Agent Instructions

## Mission

Help the user build a reusable PRD knowledge system. Do not jump directly to producing a one-off PRD when the user's business knowledge, source hierarchy, or format standard has not been initialized.

## Activation

Activate this workflow when the user asks to:

- initialize a PRD workflow or knowledge base;
- ingest business materials or historical PRDs;
- learn a PRD template or writing standard;
- create a domain-specific PRD skill;
- generate, update, render, or publish a PRD.

Before executing a full workflow, read:

1. `docs/architecture.md` for the approved V1 boundaries;
2. `skills/prd-knowledge-engineering/SKILL.md` for the operational workflow;
3. the relevant files under `protocols/` when they exist.

## Non-negotiable rules

1. Read user-provided sources before asking broad business questions.
2. Ask only for gaps that materially affect the result, no more than three questions per round.
3. Do not write to the user's knowledge base before Gate 1 confirmation.
4. Do not publish or update an online document before Gate 2 confirmation.
5. Do not treat historical PRD content as current business truth.
6. Do not copy business content from a document that was provided only as a format template.
7. Do not invent systems, pages, fields, metrics, permissions, defaults, interfaces, or ownership boundaries.
8. Keep business knowledge, PRD content, rendering, publishing, and verification as separate layers.
9. A successful API response is not proof that a document rendered correctly.
10. Never store credentials, cookies, authorization headers, secrets, or signed URLs in the repository or knowledge base.
11. Do not expose private company names, internal platforms, real screenshots, employee identifiers, or customer data in public examples.
12. Do not silently degrade a required format capability.

## Initialization state machine

```text
S0 Environment discovery
   ├─ S0a Agent runtime & capabilities
   └─ S0b Knowledge-base tool check
S1 Source intake
S2 Source audit
S3 Gap interview
S4 Gate 1 confirmation
S5 Knowledge-base and skill creation
S6 Initialization verification
```

### S0b：知识库工具检查

知识库使用标准 Markdown + Wikilink（`[[页面名]]`）组织。Agent 必须确认用户有能浏览、搜索和可视化链接关系图的工具。不满足时，Agent 应主动提出协助配置，不能跳过此步骤继续初始化。

检查顺序：

1. **已有 Obsidian Vault** → 询问用户将知识库放在 vault 内还是独立目录。如果在 vault 内，`[[wikilink]]` 自动可用。
2. **已装 Obsidian 但无 Vault** → 建议用户在当前工作目录创建 vault，或直接使用 `~/prd-knowledge-base` 作为 vault 根目录。
3. **未装 Obsidian** → 告诉用户：
   - Obsidian 免费，官网 https://obsidian.md ，下载即用；
   - Markdown 文件本身不依赖 Obsidian，用 VS Code、Typora 甚至 Finder 都能看；
   - 但 `[[链接]]` 的跳转和图谱视图需要 Obsidian 才能发挥完整价值。
4. **拒绝安装** → 知识库仍可正常创建和读写，Agent 改用显式路径链接（`页面名` → `./路径.md` 格式），放弃 Wikilink 和关系图谱能力。

此步骤必须在 S1 素材接收前完成。工具不到位就进 S1，等于让用户建一个自己没法用的知识库。

## First initialization message

The first user-facing message must only request source material:

```text
I will read your existing business materials and historical PRDs first, then ask only for information that is genuinely missing.

Please provide the files, directories, or online document links that contain your business materials. You do not need to organize them in advance; I will classify them.
```

Follow the user's language. Do not ask for the knowledge-base path, source-copy policy, template choice, MCP platform, or agent runtime in the first message.

## Source audit

Classify sources as:

```text
business_overview
system_document
terminology
metric_definition
meeting_record
mrd
prd_sample
prd_template
image_asset
irrelevant
unknown
```

Read complete source content. For DOCX files, inspect embedded images when they may contain requirements or UI evidence. Record facts, conflicts, gaps, and candidate templates separately.

## Source priority

```text
Current explicit user confirmation
> current meeting conclusion or MRD
> current business knowledge
> current system documentation
> historical PRD
> agent general knowledge
```

General knowledge may help formulate questions, but it must not be stored as the user's business fact without confirmation.

Format priority is separate:

```text
User-designated standard template
> user-confirmed historical PRD
> built-in neutral provisional profile
```

## Gate 1

Before writing the knowledge base, present:

- business scope;
- roles and main process;
- systems and pages;
- terminology, metrics, and rules;
- resolved conflicts;
- remaining unknowns;
- selected format source;
- planned files;
- planned domain-skill behavior;
- knowledge-base path;
- source handling mode (`reference` or `copy`).

Ask for explicit confirmation. Without confirmation, do not create the knowledge base or install a skill.

## Knowledge-base defaults

- Ask for a path after source audit; default to `~/prd-knowledge-base`.
- Default source handling to `reference`.
- Support multiple domains under `domains/` and shared standards under `_shared/`.
- Use `router.yaml` as the machine source of truth and `index.md` as human navigation.
- Require page-level sources and rule-level `source_id` for high-risk rules.
- Propose router changes and wait for confirmation before applying them.
- Use Obsidian-compatible `[[wikilink]]` syntax for cross-page links. Agent creates links; Obsidian renders the graph. If user has no Obsidian (see S0b), fall back to explicit Markdown paths.

## PRD generation

Generate a YAML PRD IR that validates against the repository Schema. Keep document content separate from publishing configuration. Logic labels come from semantic `kind`; do not hand-write numbering, HTML line breaks, or display labels in IR text.

High-risk logic kinds require sources. Blocking open questions prevent formal publishing.

## Rendering

The repository defines renderer protocols rather than fixed renderer implementations. Use available tools or temporary scripts, then produce a render manifest. Do not modify the IR during rendering.

- Markdown defaults to portable mode and must report format degradation.
- DOCX must use native numbered paragraphs and verify OOXML plus visual output.
- Feishu output must use native blocks or report an approved layout degradation.

## Gate 2 and publishing

Before publishing, show a concise summary of:

- content version;
- target platform and location;
- create, update, or create-new-version operation;
- format profile and renderer;
- unsupported or degraded capabilities;
- uploaded asset count;
- side effects;
- preview artifacts;
- verification strategy.

Bind confirmation to a plan hash. If the plan changes, confirmation expires.

Only update a document when the user explicitly provides its identifier. If an update target cannot be read, propose a new V2/V3 document and disclose the change before confirmation.

## Verification

After publishing, verify through MCP structure inspection or read-only browser inspection. If neither is available, request explicit user confirmation and mark the result `published_unverified` until confirmed.

## Cross-agent compatibility

- Codex and Hermes read this `AGENTS.md` directly.
- Claude Code reads `CLAUDE.md`, which imports this file.
- Keep the canonical skill platform-neutral.
- Install only a thin wrapper into the current runtime after user approval.
- Do not overwrite an unmanaged skill with the same name.

## Current project status

This repository is in the `0.1.0` design and implementation stage. Compatibility is designed but full E2E verification is not yet complete. Never claim otherwise.
