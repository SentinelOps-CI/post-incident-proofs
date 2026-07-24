# API Surface

## Primary: `post-incident` CLI (ITE)

Install:

```bash
pip install -e "./python[dev]"
```

Commands (JSON diagnostics on stdout; fail closed):

```bash
post-incident source validate <file>
post-incident lineage validate <file>
post-incident lineage graph <file> --out <graph.json>
post-incident preservation verify <file>
post-incident redaction verify <file>
post-incident bundle validate <dir>
post-incident replay-check <dir> --replay-report <report.json>
```

Python package: `python/post_incident/` (schema loaders, digests, lineage, preservation, redaction, Morph linkage, release bundles).

Optional reconstruction binary: Rust `post-incident-kernel` under `rust/post-incident-kernel/` (digest / envelope / DAG helpers). Set `POST_INCIDENT_KERNEL` to its path when bridging from Python.

Schemas:

- PIP domain: `schemas/pip/v1/`
- Vendored PCS pin: `schemas/pcs/` (`SCHEMA_MIRROR.json`)

Claim boundary: `docs/adr/PIP-ITE-00-claim-boundary.md`. Ownership: `docs/adr/PIP-ITE-00-polyglot-ownership.md`.

## Legacy: Lean module import

```lean
import PostIncidentProofs
```

### Legacy public helpers (executable-oriented)

- `verify_log_chain`
- `verify_rate_limit`
- `apply_diff` / `revert_diff`
- `generate_dashboard`
- `create_incident_bundle` / `verify_incident_bundle`
- `run_security_tests` / `validate_security_properties`
- `run_performance_benchmarks` / `validate_performance_slas`
- `run_chaos_tests` / `validate_system_resilience`
- `collect_system_metrics` / `run_health_checks`
- Trace helpers: `create_trace_span`, `finish_trace_span`, `add_trace_tag`, `add_trace_log`

These support the frozen Lake executables. They are **not** ITE lineage/preservation evidence.

### Legacy Lake CLI targets

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

## Notes

- ITE digests: real SHA-256 (Rust/Python). Lean `PostIncidentProofs.Utils.Crypto` is a deterministic stub for legacy gates only (ADR-0001).
- Assurance mapping: `docs/ASSURANCE_MATRIX.md`.
