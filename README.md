<div align="center">
  
<pre>
###############################################################################################
#                                                                                             #
#   ____           _       ___            _     _            _     ____                   __  #
#  |  _ \ ___  ___| |_    |_ _|_ __   ___(_) __| | ___ _ __ | |_  |  _ \ _ __ ___   ___ / _ | #
#  | |_) / _ \/ __| __|    | || '_ \ / __| |/ _` |/ _ \ '_ \| __| | |_) | '__/ _ \ / _ \ |_   #
#  |  __/ (_) \__ \ |_     | || | | | (__| | (_| |  __/ | | | |_  |  __/| | | (_) | (_) |  _| #
#  |_|   \___/|___/\__|   |___|_| |_|\___|_|\__,_|\___|_| |_|\__| |_|   |_|  \___/ \___/|_|   #
#                                                                                             #
#                                                                                             #
###############################################################################################
</pre>

[![Lean](https://img.shields.io/badge/Lean-4.7.0-blue)](https://leanprover.github.io/)
[![CI](https://img.shields.io/badge/CI-verified-success)](.github/workflows/ci.yml)
[![Security](https://img.shields.io/badge/Security-policy%20present-green)](SECURITY.md)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

</div>

Post-Incident-Proofs is a Lean 4 repository focused on verifiable post-incident evidence workflows.
It provides executable checks for logging integrity, rate-limit behavior, version transitions, bundle validation, and operational readiness.

---

## Why This Repository

Incident workflows are often hard to trust when verification is manual or inconsistent.
This project makes verification explicit and repeatable through Lean modules plus executable gates that run both locally and in CI.

## Current Capability Snapshot

| Area | What exists today | How to validate |
| --- | --- | --- |
| Build integrity | Lean package and library compile | `lake build` |
| Logging checks | Log verifier and integrity checks | `lake exe log_verifier` |
| Rate checks | Rate model verifier | `lake exe rate_verifier` |
| Version checks | Version roundtrip verifier | `lake exe version_verifier` |
| Bundle checks | Bundle validation command | `lake exe verify_bundle <path>` |
| Ops checks | Security, observability, full validation executables | `lake exe security`, `lake exe observability`, `lake exe validate` |
| Delivery quality | CI gates, hygiene checks, release artifacts | `.github/workflows/` |

## Quick Start

```bash
lake build
lake exe tests
lake exe security
lake exe observability
lake exe validate
```

## Command Reference

### Lake executables

```bash
lake exe verify_bundle <path>
lake exe log_verifier
lake exe rate_verifier
lake exe version_verifier
lake exe tests
lake exe benchmarks
lake exe security
lake exe observability
lake exe validate
```

### Make targets

```bash
make build
make test
make security
make observability
make validate
make benchmark
make ci
make release
```

## Environment and Secrets

1. Copy `.env.example` to `.env`.
2. Set strong values for:
   - `GF_SECURITY_ADMIN_USER`
   - `GF_SECURITY_ADMIN_PASSWORD`
   - `APP_HMAC_KEY`
3. Never commit `.env` files or private key material.
4. Optional helper for local generation: `python scripts/generate_secrets.py`.

## Quality and Release Pipeline

- CI includes verification, benchmark, dependency review, policy lint, and repository hygiene workflows.
- Release automation publishes:
  - source tarball
  - source checksum
  - release notes
- Scheduled SLO checks run through `slo-gate`.

## Documentation Map

- API surface: `docs/API.md`
- Security policy: `SECURITY.md`
- Assurance mapping: `docs/ASSURANCE_MATRIX.md`
- SLOs: `docs/SLOS.md`
- Definition of done: `docs/DEFINITION_OF_DONE.md`
- Contributing guide: `CONTRIBUTING.md`
- Architecture decisions: `docs/adr/`
