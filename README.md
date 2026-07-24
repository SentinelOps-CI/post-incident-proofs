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

**Post-Incident-Proofs (PIP)** is an offline incident-lineage and preservation-verification toolkit (ITE: Incident Trace Evidence), plus a frozen Lean executable baseline for operational gates.

The public product surface is the `post-incident` CLI (Python), backed by a Rust digest/DAG kernel and Lean soundness modules. Digests used for ITE are real SHA-256 in Rust/Python. Lean `Utils.Crypto` remains a deterministic stub for legacy gates only — not a cryptographic oracle (see [ADR-0001](docs/adr/ADR-0001-crypto-and-assurance-boundary.md) and [PIP-ITE-00](docs/adr/PIP-ITE-00-claim-boundary.md)).

---

## What ITE claims (and does not)

| Claims | Non-claims |
| --- | --- |
| Source / lineage / declared preservation / redaction-link / Morph replay-link structural checks | Causation, blame, remediation effectiveness |
| Fail-closed schema + digest verification on declared material | Live SDE / Morph Cloud operation |
| Lean soundness for selected normalized predicates | “Full capture” when completeness is incomplete/silent |
| | Partner secrets or protected plaintext in public fixtures |

Full boundary: [`docs/adr/PIP-ITE-00-claim-boundary.md`](docs/adr/PIP-ITE-00-claim-boundary.md).

---

## Capability snapshot

| Area | What exists today | How to validate |
| --- | --- | --- |
| Incident source | Schema + integrity envelope refs | `post-incident source validate` |
| Lineage DAG | Acyclic graph, pinned refs, digest checks | `post-incident lineage validate` |
| Preservation | Deterministic declared claim deciders | `post-incident preservation verify` |
| Redaction | Public↔protected digest commitments | `post-incident redaction verify` |
| Morph replay | Fixture linkage to lineage digests | `post-incident replay-check` |
| Release bundle | Offline `incident_release/` validation | `post-incident bundle validate` |
| Polyglot CI | Lint + Lean + Rust + pytest | `make ite` |
| Legacy Lean gates | Logging / rate / version / ops executables | `make ci` (not lineage evidence) |

---

## Quick start (ITE)

```bash
pip install -e "./python[dev]"
post-incident source validate fixtures/source/valid_complete.json
post-incident lineage validate fixtures/lineage/valid_dag.json
post-incident preservation verify fixtures/preservation/valid_claims.json
post-incident redaction verify fixtures/redaction/valid_commitment.json
post-incident bundle validate fixtures/release/valid_incident_release
make ite
```

Optional Rust kernel (reconstruction / digest helpers):

```bash
cargo build --manifest-path rust/post-incident-kernel/Cargo.toml --release
```

Reconstruction guide: [`docs/RECONSTRUCTION.md`](docs/RECONSTRUCTION.md).

---

## Legacy Lean executables (frozen baseline)

These gates remain supported for the historical Lean package. They are **not** incident-lineage or preservation evidence.

```bash
lake build
lake exe tests
lake exe log_verifier
lake exe rate_verifier
lake exe version_verifier
lake exe verify_bundle <path>
lake exe security
lake exe observability
lake exe validate
lake exe benchmarks
```

Make aliases: `make build`, `make test`, `make security`, `make observability`, `make validate`, `make benchmark`, `make ci`, `make release`.

Baseline freeze: [`docs/baseline/PIP-ITE-00.md`](docs/baseline/PIP-ITE-00.md).

---

## Environment and secrets

1. Copy `.env.example` to `.env` only if you run the optional compose stack.
2. Set strong values for `GF_SECURITY_ADMIN_USER`, `GF_SECURITY_ADMIN_PASSWORD`, and `APP_HMAC_KEY`.
3. Never commit `.env`, private keys, or partner plaintext.
4. Optional local helper: `python scripts/generate_secrets.py` (writes outside the tracked tree).

### Optional Docker compose

`docker-compose.yml` is an **optional observability scaffold** for Grafana/Prometheus/Loki. It mounts provisioning paths (`dashboards/`, `datasources/`, `prometheus.yml`, `alerts.yml`) that are **not shipped** in this repository. Do not treat compose as part of ITE verification; use it only after supplying your own provisioning files locally.

---

## Quality and release pipeline

- Legacy Lean CI: `.github/workflows/ci.yml`, hygiene, policy lint, SLO gate.
- ITE CI: `.github/workflows/ite.yml` (`make ite` equivalent).
- Release automation publishes a source tarball + checksum. Release notes must stay within ADR claim boundaries (no fake crypto/performance guarantees).

---

## Documentation map

| Doc | Purpose |
| --- | --- |
| [`docs/API.md`](docs/API.md) | `post-incident` CLI + legacy Lake surface |
| [`SECURITY.md`](SECURITY.md) | Private disclosure + controls |
| [`docs/ASSURANCE_MATRIX.md`](docs/ASSURANCE_MATRIX.md) | Claim → command → CI mapping |
| [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) | ITE threat model |
| [`docs/RECONSTRUCTION.md`](docs/RECONSTRUCTION.md) | Offline rebuild / verify |
| [`docs/REVIEWER_CHECKLIST_ITE.md`](docs/REVIEWER_CHECKLIST_ITE.md) | PR checklist |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history |
| [`docs/SLOS.md`](docs/SLOS.md) | Build / verify objectives |
| [`docs/DEFINITION_OF_DONE.md`](docs/DEFINITION_OF_DONE.md) | Done criteria |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Local workflow |
| [`docs/adr/`](docs/adr/) | ADR-0001 + PIP-ITE-00..07 |
