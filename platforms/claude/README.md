# Claude Code Adapter

Claude Code does not use root `AGENTS.md` as its primary project memory entry. This repository keeps one instruction source by making root `CLAUDE.md` contain only:

```text
@AGENTS.md
```

Do not copy AGENTS content into CLAUDE.md.

## Skill paths

- User: `~/.claude/skills/<name>/SKILL.md`
- Project: `<project>/.claude/skills/<name>/SKILL.md`

Default to user scope; offer project scope. Install the thin Wrapper only after user approval.

## Verification

Start a new Claude Code session, confirm project instructions are loaded, invoke the domain task, and verify that the Wrapper reads the Canonical Skill.

Official references:

- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/skills
