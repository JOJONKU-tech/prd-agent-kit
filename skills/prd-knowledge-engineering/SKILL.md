---
name: prd-knowledge-engineering
description: Use when initializing a PRD knowledge base, learning PRD standards, generating a domain skill, or producing and publishing a structured PRD.
---

# PRD Knowledge Engineering

## Purpose

Build a reusable, source-traceable PRD workflow instead of producing an isolated document. The workflow separates business knowledge, format rules, structured PRD content, rendering, publishing, and verification.

## Activate when

- initializing a PRD workflow or business knowledge base;
- reading business materials or historical PRDs;
- learning a team's PRD template or writing style;
- generating or updating a domain-specific PRD skill;
- creating, rendering, or publishing a PRD.

## Required repository protocols

Read the relevant canonical protocol before executing:

- `protocols/onboarding.md`
- `protocols/source-priority.md`
- `protocols/confirmation-gates.md`

Local operational summaries are available at:

- `references/onboarding.md`
- `references/source-priority.md`
- `references/confirmation-gates.md`
- `references/template-learning.md`
- `references/prd-ir.md`
- `references/rendering.md`
- `references/publishing.md`

## Workflow

### 1. Initialize

Follow `references/onboarding.md`.

1. Ask only for source files, directories, or online document links in the first message.
2. Read and classify all accessible sources.
3. Separate confirmed facts, conflicts, gaps, format candidates, and irrelevant material.
4. Ask no more than three gap questions per round.
5. Preserve unknown information as `unknown`; never invent it.
6. Present Gate 1 before creating or updating the knowledge base.

### 2. Build knowledge

- Use one root knowledge base with multiple domains.
- Store reusable knowledge in `_shared/` and domain knowledge in `domains/<slug>/`.
- Keep `router.yaml` as the machine source of truth and `index.md` as human navigation.
- Record page-level sources everywhere.
- Record rule-level `source_id` for fields, defaults, permissions, metrics, validation, migration, and system boundaries.
- Propose router changes and wait for user confirmation.

### 3. Learn format

Keep business and format evidence separate. A format sample may teach headings, tables, lists, image placement, and writing style, but it does not establish current business facts.

If no confirmed standard exists, use a neutral profile marked `provisional`.

### 4. Generate PRD IR

Generate YAML that validates against the repository Schema. Keep publishing configuration outside the IR. Represent requirement logic as semantic kinds and nested children. Do not hand-write display numbering or HTML formatting in IR text.

Blocking open questions prevent formal publishing.

### 5. Render

Follow the renderer contract available in the repository. Renderers may use current tools or temporary scripts, but must not mutate the IR or publish online documents.

Each renderer produces a manifest containing:

- input hashes;
- capabilities;
- output paths;
- degradations;
- structural checks;
- visual checks;
- readiness status.

### 6. Confirm and publish

Follow `references/confirmation-gates.md`.

Gate 2 must show the target, operation, format profile, capabilities, degradations, assets, side effects, previews, and verification strategy. Confirmation is bound to `plan_sha256`.

Only update an explicitly identified document. If the target cannot be read, propose a V2/V3 document and ask again.

### 7. Verify

A successful API response is not enough. Verify through MCP structure inspection or read-only browser inspection. Without either, request user confirmation and keep status `published_unverified`.

## Hard rules

1. Read sources before broad interviewing.
2. Gate 1 before knowledge-base writes.
3. Separate business facts from format rules.
4. Do not invent systems, fields, metrics, permissions, defaults, interfaces, or ownership.
5. Generate structured IR before rendering.
6. Report Required/Preferred capability gaps.
7. Gate 2 before online writes.
8. Do not overwrite same-name documents without an explicit identifier.
9. Do not store credentials or signed URLs.
10. Verify before claiming completion.

## Installation

The canonical domain skill belongs in the user's knowledge base. Install a thin runtime wrapper only after explicit approval. If the runtime cannot read the canonical path, offer a managed copy with source-hash checking. Never overwrite an unmanaged skill with the same name.

## Current implementation status

The repository is under phased `0.1.0` development. Use only protocols, Schemas, validators, and fixtures that actually exist. Compatibility marked `not_run` must not be presented as E2E-verified.
