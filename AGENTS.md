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

知识库是给 Agent 用的，Agent 直接读写 Markdown 文件、解析 `[[wikilink]]`、遵循 `router.yaml` 路由，不需要任何第三方工具。

此步骤只做一件事：如果用户装了 Obsidian，建议将知识库放在 vault 内，这样用户可以借助 Obsidian 的关系图谱浏览 Agent 建好的知识网络。Obsidian 是给人用的，不是给 Agent 用的。

- **已有 Obsidian Vault** → 询问用户是否将知识库放在 vault 内。
- **未装 Obsidian** → 一句话提一下 Obsidian 免费、可以提供可视化图谱，但绝不阻塞流程。
- **不管装没装** → Agent 继续进入 S1。Agent 自己就是知识库的读写引擎。

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
- Use Obsidian-compatible `[[wikilink]]` syntax for cross-page links. Agent reads these directly; Obsidian is optional for human browsing.

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
