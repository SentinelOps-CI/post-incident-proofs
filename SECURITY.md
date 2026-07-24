# Security Policy

## Supported Branches

| Branch | Support Status |
| --- | --- |
| `main` | Supported |
| non-default branches | Best effort |

## Reporting a Vulnerability

Do not open a public issue for security reports.

- Report privately via **GitHub Security Advisories** (repository Security tab → Advisories → Report a vulnerability), or the private disclosure channel configured for this repository.
- Include reproduction details, impact, and affected files/modules.
- If possible, include a minimal proof-of-concept.
- Do not attach partner secrets, protected plaintext, or production credentials to reports or fixtures.

## Triage Targets

- Initial acknowledgement: within 2 business days
- Triage update: within 7 business days
- Remediation plan or mitigation: as soon as validated

## Current Security Controls

- Secret scanning in CI (`repo-hygiene` workflow with gitleaks)
- Dependency review on pull requests
- Dependabot automation for actions/docker/pip
- Environment-driven credentials for optional compose (never commit `.env`)
- Policy lint workflow for YAML policy checks
- ITE privacy tests for forbidden fields / secret-like strings in public fixtures

## Operational Security Requirements

- Never commit `.env`, key files, or private credentials.
- Use `.env.example` as a scrubbed template only.
- Rotate runtime secrets regularly if using the optional compose stack.
- Ensure release artifacts include checksum verification.
- Public fixtures use synthetic digests only (see PIP-ITE-00).

## Security Validation in This Repo

```bash
# Legacy Lean security/ops gate
lake exe security
lake exe validate

# ITE release + privacy
post-incident bundle validate fixtures/release/valid_incident_release
pytest python/tests/test_privacy.py -q
make ite
```

Threat model: `docs/THREAT_MODEL.md`. Crypto humility: `docs/adr/ADR-0001-crypto-and-assurance-boundary.md`.
