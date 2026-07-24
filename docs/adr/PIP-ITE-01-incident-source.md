# PIP-ITE-01: Incident Source Schema

## Status

Accepted

## Context

ITE needs a versioned source integrity record before lineage or preservation claims.

## Decision

- Introduce `schemas/pip/v1/IncidentSourceRecord.schema.json`.
- Integrity envelope references PCS `ArtifactIntegrity.v1` (vendored), not a fork.
- Completeness is explicit: `complete` | `incomplete` with gaps; silence never implies completeness.
- CLI: `post-incident source validate`.
- Rust provides real SHA-256 helpers; Lean stub crypto remains legacy-only.

## Non-claims

Does not assert that a real-world incident is fully captured.

## Rollback

Remove schema, fixtures, and `source validate` command; leave PIP-ITE-00 intact.
