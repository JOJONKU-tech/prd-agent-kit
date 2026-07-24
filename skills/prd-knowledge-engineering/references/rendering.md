# Rendering Operational Summary

Canonical source: `../../../protocols/renderer-contract.md`.

1. Validate PRD IR and resolve the Format Profile first.
2. Preflight Required and Preferred capabilities.
3. Fail when a Required capability is not supported.
4. Record every Preferred degradation in the Render Manifest.
5. Keep Renderer execution local; do not call publishing MCPs.
6. Markdown uses requirement markers and reports native-list degradation.
7. DOCX uses native numbered paragraphs and independent `numId` per logic cell.
8. Block Plans preserve every `logic_id`, order, and depth.
9. Run structural and required visual checks before setting readiness.
10. Never commit temporary renderer implementations to the repository.
