# ADR-0001: Crypto and Assurance Boundary

## Status

Accepted

## Context

The repository currently emphasizes deterministic, reproducible verification workflows and executable gates.  
Full cryptographic proofs and production-grade crypto backend integrations are tracked as deeper hardening work.

## Decision

- Keep deterministic crypto helpers scoped to repository verification behavior.
- Avoid overstating cryptographic guarantees beyond implemented checks.
- Maintain explicit mapping from claims to executable validations and CI gates.
- Treat stronger crypto backend integration as a separate planned milestone.

## Consequences

- Predictable local and CI behavior.
- Clear documentation boundary between current guarantees and future targets.
- Lower risk of claim/implementation drift.
