# Assurance Matrix

This matrix links implemented checks to runtime commands and CI enforcement.

| Assurance Goal | Lean Module / Symbol | Runtime Command | CI Gate |
| --- | --- | --- | --- |
| Log integrity verification | `PostIncidentProofs.Logging.verify_chain_integrity` | `lake exe log_verifier` | `ci.yml` verify |
| Rate-limit behavior check | `PostIncidentProofs.Rate.Verification.verify_algorithm_correctness` | `lake exe rate_verifier` | `ci.yml` verify |
| Version roundtrip check | `PostIncidentProofs.Version.Verification.verify_diff_roundtrip` | `lake exe version_verifier` | `ci.yml` verify |
| Bundle validation | `PostIncidentProofs.Bundle.Builder.validate_bundle` | `lake exe verify_bundle <path>` | `ci.yml` verify/validate |
| Security metrics baseline | `PostIncidentProofs.Security.ThreatModel.runSecurityTests` | `lake exe security` | `ci.yml` verify |
| Observability health checks | `PostIncidentProofs.Observability.Metrics.runHealthChecks` | `lake exe observability` | `ci.yml` verify + `slo-gate.yml` |
| End-to-end readiness | `PostIncidentProofs.validate_system_resilience` | `lake exe validate` | `ci.yml` verify + `slo-gate.yml` |
