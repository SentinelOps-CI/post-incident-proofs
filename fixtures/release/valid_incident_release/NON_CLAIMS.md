# Non-claims

This `incident_release/` validates **structural / integrity** properties only
(source, lineage, declared preservation, redaction linkage, optional Morph
replay linkage, checksums). See `docs/adr/PIP-ITE-00-claim-boundary.md`.

This release does **not** assert:

- Causation, blame, or fault attribution
- Remediation effectiveness or policy certification
- That the incident is fully captured in the real world
- Partner-secret contents or protected plaintext
- Live Simulation / Synthetic Development Environment (SDE) or Morph Cloud operation
- Cryptographic signing, non-repudiation services, or production-grade crypto backends beyond implemented digest/schema checks (ADR-0001)
- That legacy `lake exe *` gates constitute lineage or preservation evidence
