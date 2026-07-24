# Reconstruction Guide

Rebuild and verify an offline `incident_release/` without protected content.

## Prerequisites

- Python 3.11+
- Rust toolchain (for kernel)
- Lean 4.7.0 / Lake (legacy + soundness)

## Install

```bash
pip install -e "./python[dev]"
cargo build --manifest-path rust/post-incident-kernel/Cargo.toml --release
```

Optional: `export POST_INCIDENT_KERNEL=rust/post-incident-kernel/target/release/post-incident-kernel`

## Validate a release

```bash
post-incident bundle validate fixtures/release/valid_incident_release
post-incident replay-check fixtures/release/valid_incident_release \
  --replay-report fixtures/release/valid_incident_release/morph_replay_report.json
```

## Component commands

```bash
post-incident source validate fixtures/source/valid_complete.json
post-incident lineage validate fixtures/lineage/valid_dag.json
post-incident lineage graph fixtures/lineage/valid_dag.json --out /tmp/graph.json
post-incident preservation verify fixtures/preservation/valid_claims.json
post-incident redaction verify fixtures/redaction/valid_commitment.json
```

## Lean + conformance

```bash
lake build
pytest python/tests/test_conformance.py -q
```

## Legacy gates (not lineage evidence)

```bash
make ci
```

Claim boundary: `docs/adr/PIP-ITE-00-claim-boundary.md`. Crypto humility: `docs/adr/ADR-0001-crypto-and-assurance-boundary.md`.
