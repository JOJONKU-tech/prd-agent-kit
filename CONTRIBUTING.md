# Contributing

Contributions should preserve the protocol-first, source-grounded V1 boundary.

## Setup

```bash
git clone https://github.com/JOJONKU-tech/prd-agent-kit.git
cd prd-agent-kit
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

## Before changing code or protocols

1. Read `AGENTS.md`.
2. Keep business facts separate from format evidence.
3. Add or update a failing test before changing validator behavior.
4. Use fictional, neutral fixtures only.
5. Do not add private integrations or credentials.

## V1 boundaries

- No fixed renderer implementation.
- No heavy CLI or web editor.
- No document deletion, permission, or sharing capabilities.
- No silent capability degradation.
- No compatibility claims without real E2E evidence.
- No private company or internal platform identifiers, including split or encoded forms.

## Verification

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python validators/release_check.py --run-tests
```

For private local scans, inject terms with `PRD_AGENT_KIT_EXTRA_FORBIDDEN_TERMS`. Never commit the list.

## Pull requests

A pull request should include:

- the problem and intended behavior;
- tests or fixtures proving the change;
- protocol or Schema compatibility impact;
- security and privacy impact;
- honest runtime verification status.

Keep changes focused. Do not bundle unrelated refactors.
