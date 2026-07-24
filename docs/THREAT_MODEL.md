# Threat Model (ITE)

## Assets

- Public incident release bundles (digests, schemas, claims)
- Integrity of lineage DAGs and preservation decider outputs
- Offline redaction commitments (public digests only)

## Trust boundaries

| Component | Trust |
| --- | --- |
| Lean kernel predicates | Trusted for pure properties on normalized inputs |
| Rust digest/DAG kernel | Trusted for SHA-256 and graph helpers |
| Python CLI / parsers | Untrusted adapters; fail closed on malformed input |
| Fixtures | Synthetic public digests only |
| Morph Cloud | Untrusted / out of default CI; consume recorded reports only |

## Adversaries

- Tamper with source digests, substitute transformed artifacts, introduce cycles, reorder retained events, forge redaction mappings, or mismatch Morph replay identity.

## Mitigations

- Schema validation + semantic checks
- Real SHA-256 (Rust/Python), not Lean stub crypto (ADR-0001)
- Append-only transformation `record_digest`
- Privacy grep/CI for forbidden fields and secret-like strings
- Conformance vectors shared across Lean/Python/Rust
- Fail-closed diagnostics (`error` / `indeterminate`, never false `pass`)

## Out of scope

Causal inference, remediation judgment, partner plaintext, live SDE/Morph operation, production signing/KMS backends, and marketing of Lean stub crypto as real SHA-256 security proofs.
