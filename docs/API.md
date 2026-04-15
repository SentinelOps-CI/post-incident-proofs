# API Surface

## Public Module

```lean
import PostIncidentProofs
```

## Core Public Functions

- `verify_log_chain`
- `verify_rate_limit`
- `apply_diff`
- `revert_diff`
- `generate_dashboard`
- `create_incident_bundle`
- `verify_incident_bundle`
- `run_security_tests`
- `validate_security_properties`
- `run_performance_benchmarks`
- `validate_performance_slas`
- `run_chaos_tests`
- `validate_system_resilience`
- `collect_system_metrics`
- `run_health_checks`
- `create_trace_span`
- `finish_trace_span`
- `add_trace_tag`
- `add_trace_log`

## CLI Targets

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

- Function contracts are intentionally lightweight and executable-oriented.
- For assurance mapping and CI linkage, see `docs/ASSURANCE_MATRIX.md`.
