# PIP-ITE-04: Lean Soundness

## Status

Accepted

## Decision

- Lean modules: `Lineage/Graph.lean`, `Preservation/Order.lean`, `Preservation/Projection.lean`, `Preservation/Deciders.lean`.
- Finished proofs only (no `sorry`).
- Conformance vectors under `fixtures/conformance/` must match Python/Rust.

## Non-claims

Lean soundness covers selected pure predicates only; not partner-specific semantics.

## Rollback

Drop new Lean modules from `PostIncidentProofs.lean` imports; retain runtime deciders as best-effort without formal link.
