# Changelog

All notable changes to this project are documented in this file.

The format tracks shipped capability. Claims stay within ADR-0001 and PIP-ITE-00.

## [0.2.0] - 2026-07-24

### Added

- PIP-ITE incident lineage stack: Python `post-incident` CLI, Rust `post-incident-kernel`, Lean lineage/preservation soundness modules.
- Vendored PCS `ArtifactIntegrity.v1` + `common.defs` pin under `schemas/pcs/`.
- PIP domain schemas under `schemas/pip/v1/` (source, lineage, preservation, redaction, Morph replay, incident release).
- Fixture corpus (valid/invalid) and conformance vectors.
- ADRs PIP-ITE-00 through PIP-ITE-07; baseline record at commit `3cdfdf09c20f08ad5221d29607b5a9726295ad10`.
- CI workflow `.github/workflows/ite.yml` and `make ite` aggregate target.
- Threat model, reconstruction guide, reviewer checklist, release `NON_CLAIMS.md`.

### Claims / non-claims

- Establishes source, lineage, declared preservation, redaction-link, and Morph replay-link **structural** checks.
- Does **not** claim causation, remediation effectiveness, partner-secret contents, live SDE/Morph operation, or production cryptographic proofs beyond implemented digest/schema verification.

### Changed

- Documentation and policies aligned to the ITE claim boundary; legacy `lake exe *` gates labeled as frozen baseline (not lineage evidence).

## [0.1.0] - baseline

- Legacy Lean executable gates and documentation at freeze commit `3cdfdf09c20f08ad5221d29607b5a9726295ad10`.
