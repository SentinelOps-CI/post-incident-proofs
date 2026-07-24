# PIP-ITE-02: Transformation Lineage

## Status

Accepted

## Decision

- Schemas: `TransformationRecord`, `LineageBundle`.
- Validators enforce resolved refs, DAG acyclicity, declared inputs/outputs, pinned implementation metadata, output digest match, and append-only `record_digest` immutability.
- CLI: `post-incident lineage validate`, `lineage graph --out`.

## Non-claims

Does not assert semantic correctness of transformations beyond declared digest/graph constraints.

## Rollback

Remove lineage schemas/validators/fixtures; keep source validation.
