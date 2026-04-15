# Service Level Objectives

## Build and Verification SLOs

- `lake build` on `main`: 100% pass target.
- `lake exe validate` on `main`: 100% pass target.
- CI verify workflow completion: 100% pass target.

## Performance SLOs

- `lake exe benchmarks` must complete successfully in CI.
- Benchmark regressions must be investigated before release tagging.

## Observability and Security SLOs

- `lake exe observability` returns metrics and health check output.
- `lake exe security` succeeds in CI and local pre-release checks.
- Scheduled `slo-gate` workflow remains green.

## Incident Response KPI Baseline

- Time-to-triage for CI breakages: same business day.
- Security finding acknowledgement: within 2 business days.
