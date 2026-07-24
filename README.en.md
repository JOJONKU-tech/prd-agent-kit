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

Follow the concise [Getting Started guide](docs/getting-started.md). You do not need to read the full architecture first.

## Status

The repository is currently in private release preparation. The three agent runtimes are design targets. Full end-to-end runtime verification has not yet been completed. See `compatibility.yaml` and `docs/testing/e2e/` for the current status and manual test procedures.

## End-to-end example

See the [fully fictional Nova Event Admin example](examples/nova-event-admin/README.md) for the complete source → knowledge base → Skill → PRD IR → Markdown/DOCX/Block Plan → Gate/Receipt chain.

## Documentation

- [Getting Started](docs/getting-started.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release checklist](docs/release-checklist.md)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Architecture](docs/architecture.md)

## Principles

- Build knowledge before generating documents.
- Structure content before rendering it.
- Confirm before publishing.
- Verify before claiming completion.
- Never invent internal fields, metrics, permissions, or defaults.
- Never store credentials in the repository or knowledge base.

## License

MIT
