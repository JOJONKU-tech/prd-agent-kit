---
title: Nova Event Admin
status: confirmed
sources:
  - SRC-NOVA-SYSTEM
  - SRC-NOVA-MEETING
---

# Event Admin

## Page

Event Templates / Basic Information.

## Current fields

- Event name: required, up to 60 characters.
- Event format: required single choice.
- Status: Draft or Published.

## New conditional fields

- Team size: integer 4–8. `source_id: SRC-NOVA-MEETING`
- Checkpoint count: integer 3–10. `source_id: SRC-NOVA-MEETING`
- Scoring mode: fixed Cumulative. `source_id: SRC-NOVA-MEETING`
- Publish permission: Event Admin only. `source_id: SRC-NOVA-MEETING`
