# Codex Adapter

Codex reads project instructions from `AGENTS.md`, walking from the project root toward the current directory. This repository uses only the root file and does not ship an override.

## Skill paths

- User: `~/.agents/skills/<name>/SKILL.md`
- Project: `<project>/.agents/skills/<name>/SKILL.md`
- `$CODEX_HOME/skills` is a legacy compatibility location, not the default for new installs.

Install the thin Wrapper only after user approval. Optional Codex interface metadata belongs beside the Wrapper, not in the Canonical Skill.

Official references:

- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/skills
