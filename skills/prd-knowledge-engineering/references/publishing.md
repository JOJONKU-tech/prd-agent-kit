# Publishing Operational Summary

Canonical source: `../../../protocols/generic-document-mcp.md`.

1. Map semantic capabilities to the current MCP Tool Schema.
2. Never store credentials in Adapter, Plan, or Receipt.
3. Require authorized sandbox write and `write_verified` before formal publishing.
4. Present Gate 2 and bind confirmation to `plan_sha256`.
5. Update only an explicitly identified document.
6. If the target cannot be read, propose V2/V3 and reconfirm.
7. Use `query_before_retry`; never blindly repeat Create.
8. Preserve partial document handles for safe continuation.
9. Verify by MCP structure or read-only browser before completion.
10. Never delete documents or change sharing/permissions in V1.
