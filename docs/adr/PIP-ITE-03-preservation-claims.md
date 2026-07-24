# PIP-ITE-03: Preservation Claims

## Status

Accepted

## Decision

- Schema `PreservationClaim` with declared claim classes.
- Deterministic deciders for order, auth-chain, projection, acyclicity, undeclared-source, digest lineage.
- Failure-predicate requires supported `predicate_ast`; otherwise `indeterminate`.

## Non-claims

Predicate selection and semantic sufficiency remain external.

## Rollback

Remove preservation schema/deciders/fixtures.
