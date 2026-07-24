# Knowledge Base Contract

This directory describes the root knowledge-base configuration.

Required root files:

- `config.yaml`: knowledge-base identity and defaults;
- `router.yaml`: machine-readable domain routing;
- `index.md`: human navigation;
- `log.md`: confirmed structural changes.

Rules:

1. `router.yaml` is the machine source of truth.
2. `index.md` must not contain routing rules absent from YAML.
3. Credentials and signed URLs are forbidden.
4. Source paths may remain external when source mode is `reference`.
5. Router updates require user confirmation.
