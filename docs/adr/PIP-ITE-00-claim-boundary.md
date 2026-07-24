# PIP-ITE-00: Claim Boundary and Polyglot Ownership

## Status

Accepted

## Context

Post-Incident-Proofs historically shipped Lean executable gates for logging, rate limits, version diffs, and operational readiness. The ITE (Incident Trace Evidence) sequence extends the repository into an offline incident-lineage and preservation-verification backend.

Without an explicit claim boundary, reviewers may conflate structural integrity checks with causal analysis, remediation judgment, or SDE operation.

## Decision

### Claims established by ITE (structural / integrity)

| Claim class | Meaning |
| --- | --- |
| Source integrity | Declared `IncidentSourceRecord` fields and PCS integrity envelope references are well-formed; digests verify when material is presented |
| Lineage integrity | Transformation history is a DAG with resolved refs, pinned implementations, and matching output digests |
| Declared preservation | Named preservation classes evaluate deterministically against declared inputs/outputs/assumptions |
| Redaction linkage | Public↔protected digest commitments verify without exposing redacted plaintext |
| Replay linkage | Recorded Morph replay reports bind to lineage nodes by declared digests (fixture-only in default CI) |

### Explicit non-claims (exclusions)

This repository does **not**:

- Infer causation or blame
- Generate environment families or synthetic deployment topologies as truth
- Train or certify policies
- Judge remediation effectiveness
- Store partner secrets or protected plaintext in public fixtures/logs
- Operate the Simulation / Synthetic Development Environment (SDE)
- Assert that an incident is fully captured in the real world when completeness is `incomplete` or silent
- Promote PIP domain records into PCS protocol artifacts (requires a future separate protocol ADR)
- Treat legacy `lake exe *` gates as lineage or preservation evidence

Predicate **selection** and semantic **sufficiency** remain external. When a failure-predicate claim lacks a supported machine-checkable AST, deciders return `indeterminate`, never pass.

### Polyglot ownership (single contract)

One public CLI surface: `post-incident`. Roles do not diverge into parallel product CLIs.

| Layer | Owner | Responsibility |
| --- | --- | --- |
| Python | `python/post_incident/` | Primary CLI, schema validation, file I/O, structured diagnostics, fixture generation, orchestration |
| Rust | `rust/post-incident-kernel/` | Pinned SHA-256 digests, integrity-envelope structural checks, DAG acyclicity, order helpers |
| Lean | `src/PostIncidentProofs/Lineage/`, `.../Preservation/` | Pure models + finished soundness proofs; conformance vectors Python/Rust must match |

Rust may expose identical subcommands as `post-incident-kernel` for reconstruction. Python remains the primary user-facing entry point.

### Fail-closed diagnostics

Stable JSON diagnostics use: `status`, `code`, `path`, `message`, `evidence_refs`.

Missing, unknown, or malformed inputs yield `error` or `indeterminate` — never `pass`.

### PCS pin

Vendored PCS schemas live under `schemas/pcs/` with pin metadata in `schemas/pcs/SCHEMA_MIRROR.json`. PIP domain schemas stay under `schemas/pip/v1/` and are not promoted into PCS.

### Legacy gates

Existing `lake exe log_verifier|rate_verifier|version_verifier|verify_bundle|tests|benchmarks|security|observability|validate` and Make targets remain **legacy baseline**. ADR-0001 remains in force for crypto humility on those paths.

## Consequences

- Clear reviewer checklist for what ITE does and does not prove
- Stable ownership so later PRs do not invent competing CLIs
- Assurance matrix lists ITE rows as `PASS` only with landed evidence; unfinished work stays `planned` — no fake PASS

## Rollback

Revert this ADR and related baseline docs together with dependent PIP-ITE ADRs if rolling back the whole sequence.
