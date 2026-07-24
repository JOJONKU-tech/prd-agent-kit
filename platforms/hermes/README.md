# Hermes Adapter

Hermes loads project context files including `AGENTS.md`. This repository relies on that root entry and does not duplicate instructions in a Hermes-specific project file.

## Skill path

Install the Wrapper under the current active profile:

`<active-profile>/skills/<name>/SKILL.md`

Do not hardcode the default profile when another profile is active. Project workflows continue to use root `AGENTS.md`.

After installation, use `/reload-skills` or start a new session, then invoke the Skill and verify that it reads the Canonical source.

Official references:

- https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files
- https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
