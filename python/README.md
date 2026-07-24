# post-incident Python package

Primary public CLI for PIP-ITE (offline incident lineage and preservation verification).

## Install

```bash
pip install -e "./python[dev]"
```

## CLI

```bash
post-incident source validate fixtures/source/valid_complete.json
post-incident lineage validate fixtures/lineage/valid_dag.json
post-incident lineage graph fixtures/lineage/valid_dag.json --out graph.json
post-incident preservation verify fixtures/preservation/valid_claims.json
post-incident redaction verify fixtures/redaction/valid_commitment.json
post-incident bundle validate fixtures/release/valid_incident_release
post-incident replay-check fixtures/release/valid_incident_release \
  --replay-report fixtures/release/valid_incident_release/morph_replay_report.json
```

## Tests

```bash
pytest python/tests -q
# or: make ite-python
```

Claim boundary: `docs/adr/PIP-ITE-00-claim-boundary.md`. Full API: `docs/API.md`.
