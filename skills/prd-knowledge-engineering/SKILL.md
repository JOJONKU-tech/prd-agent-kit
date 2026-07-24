---
name: prd-knowledge-engineering
description: Use when initializing a PRD knowledge base, learning PRD standards, generating a domain skill, or producing and publishing a structured PRD.
---

# PRD Knowledge Engineering

## Overview

This is the canonical cross-agent workflow for `prd-agent-kit`. During the current repository phase, the approved behavior is defined in `docs/architecture.md` and root `AGENTS.md`.

## When to use

Use this skill for PRD workflow initialization, business-source ingestion, knowledge routing, template learning, structured PRD generation, renderer selection, and verified document publishing.

## Current implementation status

The repository is in the `0.1.0` implementation stage. Protocol references, Schemas, fixtures, and validators are being added phase by phase. Do not claim features are implemented until their files and verification checks exist.

## Required behavior

1. Read sources before interviewing the user.
2. Respect Gate 1 before knowledge-base writes.
3. Generate PRD IR before rendering.
4. Respect Gate 2 before online publishing.
5. Verify outputs before reporting completion.
6. Never invent internal business facts.
7. Never store credentials.

## References

- `../../docs/architecture.md`
- `../../AGENTS.md`
