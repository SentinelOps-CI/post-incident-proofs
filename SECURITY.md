# Security Policy

## Supported Branches

| Branch | Support Status |
| --- | --- |
| `main` | Supported |
| non-default branches | Best effort |

## Reporting a Vulnerability

Do not open a public issue for security reports.

- Report privately through repository security advisories.
- Include reproduction details, impact, and affected files/modules.
- If possible, include a minimal proof-of-concept.

## Triage Targets

- Initial acknowledgement: within 2 business days
- Triage update: within 7 business days
- Remediation plan or mitigation: as soon as validated

## Current Security Controls

- Secret scanning in CI (`repo-hygiene` workflow with gitleaks)
- Dependency review on pull requests
- Dependabot automation for actions/docker/pip
- Environment-driven runtime credentials in compose
- Policy lint workflow for YAML policy checks

## Operational Security Requirements

- Never commit `.env`, key files, or private credentials.
- Use `.env.example` as template only.
- Rotate runtime secrets regularly.
- Ensure release artifacts include checksum verification.

## Security Validation in This Repo

Run locally:

```bash
lake exe security
lake exe validate
```

These commands are also executed in CI quality gates.
