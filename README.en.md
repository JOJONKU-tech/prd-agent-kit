# prd-agent-kit

An agent-native PRD knowledge engineering kit designed for Claude Code, Codex, and Hermes.

It helps an agent ingest business materials and historical PRDs, initialize a traceable knowledge base, learn a team's PRD format, generate a domain-specific skill, produce structured `prd-ir.yaml`, and publish verified documents through MCP integrations.

## Quick start

```bash
git clone https://github.com/JOJONKU-tech/prd-agent-kit.git
cd prd-agent-kit
```

Then tell your agent:

```text
Read AGENTS.md and initialize my PRD workflow.
```

## Status

The three agent runtimes are design targets. Full end-to-end runtime verification has not yet been completed. See `compatibility.yaml` and the future E2E manuals for the current status.

## Principles

- Build knowledge before generating documents.
- Structure content before rendering it.
- Confirm before publishing.
- Verify before claiming completion.
- Never invent internal fields, metrics, permissions, or defaults.
- Never store credentials in the repository or knowledge base.

## License

MIT
