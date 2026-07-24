# Service Level Objectives

## Build and verification SLOs

### ITE

- `make ite` on `main` / protected feature branches: 100% pass target for required ITE workflows.
- `pytest python/tests` and Rust kernel tests: 100% pass target when those paths are in scope.
- `.github/workflows/ite.yml` completion: 100% pass target.

### Legacy Lean gates

- `lake build` on `main`: 100% pass target.
- `lake exe validate` on `main`: 100% pass target.
- CI verify workflow (`.github/workflows/ci.yml`) completion: 100% pass target.

## Performance SLOs (legacy gates only)

- `lake exe benchmarks` must complete successfully in CI.
- Benchmark regressions must be investigated before release tagging.
- These numbers are **executable completion** targets, not published throughput/latency product guarantees.

## Observability and security SLOs

- `lake exe observability` and `lake exe security` succeed in CI and local pre-release checks (legacy).
- ITE privacy checks remain green when fixtures or public docs change.
- Scheduled `slo-gate` workflow remains green.

## Incident response KPI baseline

- Time-to-triage for CI breakages: same business day.
- Security finding acknowledgement: within 2 business days (see `SECURITY.md`).
