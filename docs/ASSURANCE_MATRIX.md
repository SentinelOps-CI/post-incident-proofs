# Assurance Matrix

This matrix links implemented checks to runtime commands and CI enforcement.

## Legacy gates (frozen baseline)

| Assurance Goal | Lean Module / Symbol | Runtime Command | CI Gate | Status |
| --- | --- | --- | --- | --- |
| Log integrity verification | `PostIncidentProofs.Logging.verify_chain_integrity` | `lake exe log_verifier` | `ci.yml` verify | PASS (legacy) |
| Rate-limit behavior check | `PostIncidentProofs.Rate.Verification.verify_algorithm_correctness` | `lake exe rate_verifier` | `ci.yml` verify | PASS (legacy) |
| Version roundtrip check | `PostIncidentProofs.Version.Verification.verify_diff_roundtrip` | `lake exe version_verifier` | `ci.yml` verify | PASS (legacy) |
| Bundle validation | `PostIncidentProofs.Bundle.Builder.validate_bundle` | `lake exe verify_bundle <path>` | `ci.yml` verify/validate | PASS (legacy) |
| Security metrics baseline | `PostIncidentProofs.Security.ThreatModel.runSecurityTests` | `lake exe security` | `ci.yml` verify | PASS (legacy) |
| Observability health checks | `PostIncidentProofs.Observability.Metrics.runHealthChecks` | `lake exe observability` | `ci.yml` verify + `slo-gate.yml` | PASS (legacy) |
| End-to-end readiness | `PostIncidentProofs.validate_system_resilience` | `lake exe validate` | `ci.yml` verify + `slo-gate.yml` | PASS (legacy) |

Legacy gates are **not** incident-lineage or preservation evidence. See `docs/adr/PIP-ITE-00-claim-boundary.md`.

## Incident lineage / ITE (PIP-ITE)

Status is evidence-backed. Do not mark unfinished work `PASS`.

| Assurance Goal | Lean Module / Symbol | Runtime Command | CI Gate | Status |
| --- | --- | --- | --- | --- |
| Incident source schema + envelope ref | - (schema/Python) | `post-incident source validate` | `ite.yml` / pytest | PASS |
| Lineage DAG integrity | `PostIncidentProofs.Lineage.Graph` | `post-incident lineage validate` | `ite.yml` / pytest + Rust tests | PASS |
| Preservation deciders | `PostIncidentProofs.Preservation.Deciders` | `post-incident preservation verify` | `ite.yml` / pytest + conformance | PASS |
| Lean soundness for selected predicates | `Preservation.*` (no `sorry`) | conformance vector gate | `lake build` + pytest | PASS |
| Redaction commitment verify | - | `post-incident redaction verify` | `ite.yml` / pytest privacy | PASS |
| Morph replay fixture linkage | - | `post-incident replay-check` | `ite.yml` / pytest morph | PASS |
| Incident release bundle | - | `post-incident bundle validate` | `ite.yml` / pytest release fixture | PASS |

ITE claims are structural/integrity only (PIP-ITE-00). Legacy rows above are not lineage evidence.
