# PIP-ITE-05: Redaction Commitments

## Status

Accepted

## Decision

- Schema `RedactionCommitment` binds public digests without plaintext secrets.
- Offline allow-list for redaction service identities.
- Privacy CI guard scans fixtures for forbidden fields and secret-like material.

## Non-claims

Does not reveal or reconstruct redacted values; does not attest partner vault contents.

## Rollback

Remove redaction schema/CLI/fixtures/privacy tests.
