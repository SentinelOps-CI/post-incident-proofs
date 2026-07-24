# PIP-ITE-00: Polyglot Ownership Map

## Status

Accepted (companion to PIP-ITE-00 claim boundary)

## Ownership map

| Path | Owner | Purpose |
| --- | --- | --- |
| `schemas/pcs/` | vendored PCS | `ArtifactIntegrity.v1`, `common.defs`, `SCHEMA_MIRROR.json` |
| `schemas/pip/v1/` | local PIP | Domain schemas (`IncidentSourceRecord`, …) |
| `python/post_incident/` | Python | Public `post-incident` CLI + validators |
| `rust/post-incident-kernel/` | Rust | Digest / envelope / DAG kernel |
| `src/PostIncidentProofs/Lineage/` | Lean | DAG model + soundness |
| `src/PostIncidentProofs/Preservation/` | Lean | Order/projection deciders + soundness |
| `fixtures/` | all | Synthetic public digests only |
| `docs/adr/PIP-ITE-*.md` | docs | One ADR per PR that changes ownership/semantics |
| `CHANGELOG.md` | docs | Versioned release notes |

## CLI surface

```text
post-incident source validate <file>
post-incident lineage validate <file>
post-incident lineage graph <file> --out <graph.json>
post-incident preservation verify <file>
post-incident redaction verify <file>
post-incident bundle validate <dir>
post-incident replay-check <dir> --replay-report <report.json>
```

Optional reconstruction binary: `post-incident-kernel` (Rust) with matching subcommands for digests/DAG.

## Non-divergence rule

Do not add a second public product CLI for ITE. Language-specific helpers are allowed only as libraries or reconstruction shims that implement the same contract.
