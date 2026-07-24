# Security Policy

## Supported versions

`prd-agent-kit` is pre-release software. Security fixes are applied to the current `main` branch.

## Reporting a vulnerability

Use GitHub private vulnerability reporting when the repository exposes it. Otherwise, open a minimal issue without sensitive details and ask the maintainers to provide a private reporting channel.

Do not open a public issue for vulnerabilities, credentials, private business data, internal system identifiers, or unredacted documents.

Include:

- affected file or protocol;
- impact;
- minimal reproduction using neutral data;
- suggested mitigation if known.

Do not include live credentials, cookies, authorization headers, signed URLs, or real company documents in the report.

## Repository security boundaries

The repository must not contain:

- credentials or authentication material;
- private business knowledge;
- internal system or company identifiers;
- temporary signed URLs;
- document deletion, permission-changing, or sharing automation;
- personal absolute filesystem paths.

Document MCP credentials stay in the runtime or MCP server configuration. Adapter, Publish Plan, Receipt, Knowledge Base, and Wrapper files must remain credential-free.

## Release verification

Run:

```bash
.venv/bin/python validators/release_check.py --run-tests
```

Private forbidden terms must be injected through `PRD_AGENT_KIT_EXTRA_FORBIDDEN_TERMS`; do not commit the private list.
