# PIP-ITE-07: Incident Release Bundles

## Status

Accepted

## Decision

- `incident_release/` layout with source, lineage, claims, redaction commitments, public digests, checksums, `NON_CLAIMS.md`.
- CLI: `post-incident bundle validate`; wires `replay-check` when Morph report present.
- Quality bar: ruff/mypy, rustfmt/clippy `-D warnings`, Lean build, schema/fixture tests, privacy/gitleaks.

## Non-claims

Release validation does not include protected content and does not make causal or remediation claims.

## Rollback

Remove release schema/bundle validator/docs quality targets; keep prior ITE commands.
