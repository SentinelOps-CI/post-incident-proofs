# ADR-0001: Crypto and Assurance Boundary

## Status

Accepted

## Context

The repository emphasizes deterministic, reproducible verification workflows and executable gates. Full production-grade cryptographic backends and formal crypto proofs are out of scope for the current assurance story.

Two crypto surfaces coexist:

1. **ITE digests** — real SHA-256 in Rust (`post-incident-kernel`) and Python helpers for source/lineage/redaction/release checks.
2. **Legacy Lean `PostIncidentProofs.Utils.Crypto`** — deterministic stub hashes for historical lake executables. Props such as `sha256_collision_resistance` are placeholders (`True`), not theorems about real SHA-256.

## Decision

- Keep Lean crypto helpers scoped to repository verification behavior for **legacy gates only**; never market them as real SHA-256 or HMAC security proofs.
- Prefer Rust/Python SHA-256 for all ITE integrity claims.
- Avoid overstating cryptographic guarantees beyond implemented checks (schema validation, digest equality, checksums, fail-closed diagnostics).
- Maintain explicit mapping from claims to executable validations and CI gates (`docs/ASSURANCE_MATRIX.md`).
- Treat stronger crypto backend integration (signing services, KMS, formal crypto proofs) as a separate planned milestone requiring its own ADR.

## Consequences

- Predictable local and CI behavior.
- Clear documentation boundary between current guarantees and future targets.
- Lower risk of claim/implementation drift with PIP-ITE-00.
