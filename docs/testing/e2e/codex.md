# Codex Manual E2E

Status before execution: `not_run`.

## Isolation

Use a `temporary HOME`, a fresh repository clone, neutral Nova/demo materials, and sandbox document targets. Do not reuse a real business knowledge base. Authentication may be copied only through the runtime's documented test mechanism; never commit it.

## Steps

1. Start Codex from the repository root.
2. Ask it to read `AGENTS.md` and initialize the PRD workflow.
3. Verify the first response only requests source materials.
4. Provide neutral fixture materials and complete source audit.
5. Inspect and confirm Gate 1.
6. Generate the knowledge base and Canonical Skill.
7. Approve installation of the thin Wrapper into the temporary runtime scope.
8. Start a `new session` and trigger a domain PRD request.
9. Verify the Wrapper reads the Canonical Skill and Router.
10. Generate PRD IR and a local preview.
11. Inspect Gate 2 without using a production target.
12. If an MCP is configured, use an authorized sandbox only.
13. Record test output, failures, runtime version, and commit SHA.

## Pass criteria

- Entry instructions load once;
- Gate 1 blocks knowledge writes;
- Wrapper reads the single Canonical Skill;
- Gate 2 blocks publication;
- output validates;
- no real credentials or business data enter artifacts.

After a real complete run, update compatibility evidence in a separate reviewed commit. Until then keep `not_run`.
