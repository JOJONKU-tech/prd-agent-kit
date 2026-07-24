---
name: nova-events-prd
description: Use when creating or updating source-grounded PRDs for the fictional Nova Events domain.
---

# Nova Events PRD

1. Read `sop/router.yaml` and load only the matched knowledge files.
2. Treat `sources/manifest.yaml` as the source registry.
3. Keep template evidence separate from business facts.
4. Use `standards/prd-format.yaml` and the resolved Format Profile.
5. Require source references for fields, validation, permissions, and system boundaries.
6. Generate PRD IR before rendering.
7. Respect Gate 2 before any publication.
