#!/usr/bin/env python3
"""Generate PIP-ITE fixtures with consistent digests (public digests only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from post_incident.digests import sha256_canonical_json, sha256_text  # noqa: E402

FIX = ROOT / "fixtures"
COMMIT = "3cdfdf09c20f08ad5221d29607b5a9726295ad10"
CONTAINER = sha256_text("pip-ite-container-v1")


def d(label: str) -> str:
    return sha256_text(label)


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def envelope(artifact_digest: str) -> dict:
    return {
        "schema_version": "v1",
        "artifact_type": "pip.IncidentSourceRecord",
        "canonicalization_version": "v1",
        "artifact_digest": artifact_digest,
        "signature": {
            "algorithm": "ed25519",
            "key_id": "pip-ite-fixture-key",
            "signed_at": "2026-07-01T12:00:00Z",
            "value": "dGVzdC1zaWduYXR1cmUtbm90LXNlY3JldA",
        },
    }


def source_record(*, incomplete: bool = False, digest: str | None = None) -> dict:
    trace = digest or d("source-trace-incident-1")
    gaps = ["authz-sidecar-logs"] if incomplete else []
    return {
        "schema_version": "pip.IncidentSourceRecord.v1",
        "incident_id": "inc-001",
        "source_trace_digest": trace,
        "source_system_id": "synth-orchestrator",
        "environment_id": "env-fixture-1",
        "model_version": "model-1.0.0",
        "harness_version": "harness-1.0.0",
        "tool_version": "tool-1.0.0",
        "policy_version": "policy-1.0.0",
        "authorization_version": "authz-1.0.0",
        "initial_state_commitment": d("initial-state-1"),
        "final_state_commitment": d("final-state-1"),
        "observed_outcome": "policy_denied",
        "collection_time": "2026-07-01T12:05:00Z",
        "collector_id": "collector-fixture",
        "completeness": "incomplete" if incomplete else "complete",
        "known_missing_evidence": gaps,
        "confidentiality_class": "public",
        "redaction_status": "none",
        "integrity_envelope": envelope(trace),
    }


def xform(
    tid: str,
    ttype: str,
    inputs: list[str],
    output: str,
) -> dict:
    material = {
        "schema_version": "pip.TransformationRecord.v1",
        "transformation_id": tid,
        "transformation_type": ttype,
        "input_artifact_digests": inputs,
        "output_artifact_digest": output,
        "implementation_id": "pip-ite-normalizer",
        "implementation_version": "1.0.0",
        "container_digest": CONTAINER,
        "source_commit": COMMIT,
    }
    material["record_digest"] = sha256_canonical_json(material)
    return material


def valid_lineage() -> dict:
    n0, n1, n2 = d("node-source"), d("node-norm"), d("node-replay")
    t1 = xform("t-norm", "normalization", [n0], n1)
    t2 = xform("t-replay", "synthetic_variant_derivation", [n1], n2)
    return {
        "schema_version": "pip.LineageBundle.v1",
        "bundle_id": "lin-001",
        "incident_id": "inc-001",
        "nodes": [
            {"node_id": "n0", "artifact_digest": n0, "role": "source"},
            {"node_id": "n1", "artifact_digest": n1, "role": "intermediate"},
            {"node_id": "n2", "artifact_digest": n2, "role": "replay"},
        ],
        "edges": [
            {"from_node_id": "n0", "to_node_id": "n1", "transformation_id": "t-norm"},
            {"from_node_id": "n1", "to_node_id": "n2", "transformation_id": "t-replay"},
        ],
        "transformations": [t1, t2],
    }


def cyclic_lineage() -> dict:
    a, b = d("cycle-a"), d("cycle-b")
    t1 = xform("t-ab", "normalization", [a], b)
    t2 = xform("t-ba", "normalization", [b], a)
    return {
        "schema_version": "pip.LineageBundle.v1",
        "bundle_id": "lin-cyclic",
        "incident_id": "inc-001",
        "nodes": [
            {"node_id": "a", "artifact_digest": a, "role": "source"},
            {"node_id": "b", "artifact_digest": b, "role": "intermediate"},
        ],
        "edges": [
            {"from_node_id": "a", "to_node_id": "b", "transformation_id": "t-ab"},
            {"from_node_id": "b", "to_node_id": "a", "transformation_id": "t-ba"},
        ],
        "transformations": [t1, t2],
    }


def undeclared_input_lineage() -> dict:
    n0, n1, ghost = d("node-source"), d("node-norm"), d("ghost-input")
    t1 = xform("t-norm", "normalization", [n0], n1)
    # Edge claims from ghost node digest not in transformation inputs
    return {
        "schema_version": "pip.LineageBundle.v1",
        "bundle_id": "lin-undeclared",
        "incident_id": "inc-001",
        "nodes": [
            {"node_id": "n0", "artifact_digest": n0, "role": "source"},
            {"node_id": "ghost", "artifact_digest": ghost, "role": "source"},
            {"node_id": "n1", "artifact_digest": n1, "role": "intermediate"},
        ],
        "edges": [
            {
                "from_node_id": "ghost",
                "to_node_id": "n1",
                "transformation_id": "t-norm",
            }
        ],
        "transformations": [t1],
    }


def substituted_lineage() -> dict:
    n0, n1, bad = d("node-source"), d("node-norm"), d("substituted-output")
    t1 = xform("t-norm", "normalization", [n0], n1)
    return {
        "schema_version": "pip.LineageBundle.v1",
        "bundle_id": "lin-subst",
        "incident_id": "inc-001",
        "nodes": [
            {"node_id": "n0", "artifact_digest": n0, "role": "source"},
            {"node_id": "n1", "artifact_digest": bad, "role": "intermediate"},
        ],
        "edges": [
            {"from_node_id": "n0", "to_node_id": "n1", "transformation_id": "t-norm"}
        ],
        "transformations": [t1],
    }


def mapping_commitment(original: str, redacted: str, manifest: str, service: str) -> str:
    return sha256_canonical_json(
        {
            "original_digest": original,
            "redacted_digest": redacted,
            "redaction_manifest_digest": manifest,
            "redaction_service_id": service,
        }
    )


def main() -> None:
    # Source
    write(FIX / "source" / "valid_complete.json", source_record())
    write(FIX / "source" / "valid_incomplete.json", source_record(incomplete=True))
    write(
        FIX / "source" / "changed_source_digest.json",
        source_record(digest=d("tampered-trace")),
    )
    # For changed_source_digest, also break envelope match relative to a "known" digest:
    bad = source_record()
    bad["source_trace_digest"] = d("tampered-trace")
    # leave envelope pointing at original -> mismatch
    write(FIX / "source" / "changed_source_digest.json", bad)

    # Lineage
    write(FIX / "lineage" / "valid_dag.json", valid_lineage())
    write(FIX / "lineage" / "cyclic.json", cyclic_lineage())
    write(FIX / "lineage" / "undeclared_input.json", undeclared_input_lineage())
    write(FIX / "lineage" / "artifact_substituted.json", substituted_lineage())

    # Preservation
    write(
        FIX / "preservation" / "valid_claims.json",
        {
            "claims": [
                {
                    "schema_version": "pip.PreservationClaim.v1",
                    "claim_id": "c-order",
                    "claim_class": "retained_event_order_preserved",
                    "inputs": {"events": ["e1", "e2", "e3", "e4"]},
                    "outputs": {"retained_events": ["e1", "e3"]},
                    "assumptions": ["events are totally ordered by collector clock"],
                    "checker_id": "post-incident.preservation",
                    "checker_version": "1.0.0",
                    "evidence_refs": ["fixtures/preservation/valid_claims.json"],
                },
                {
                    "schema_version": "pip.PreservationClaim.v1",
                    "claim_id": "c-auth",
                    "claim_class": "authorization_chain_preserved",
                    "inputs": {"authorization_refs": ["auth/a", "auth/b"]},
                    "outputs": {"authorization_refs": ["auth/a"]},
                    "assumptions": ["refs are opaque identifiers"],
                    "checker_id": "post-incident.preservation",
                    "checker_version": "1.0.0",
                    "evidence_refs": ["fixtures/preservation/valid_claims.json"],
                },
                {
                    "schema_version": "pip.PreservationClaim.v1",
                    "claim_id": "c-proj",
                    "claim_class": "relevant_state_projection_equivalent",
                    "inputs": {"projection": {"status": "failed"}},
                    "outputs": {"projection": {"status": "failed"}},
                    "assumptions": ["projection keys are declared relevant"],
                    "checker_id": "post-incident.preservation",
                    "checker_version": "1.0.0",
                    "evidence_refs": ["fixtures/preservation/valid_claims.json"],
                },
                {
                    "schema_version": "pip.PreservationClaim.v1",
                    "claim_id": "c-pred",
                    "claim_class": "selected_failure_predicate_preserved",
                    "inputs": {
                        "binding": {"outcome": "denied"},
                        "events": ["e1"],
                    },
                    "outputs": {
                        "binding": {"outcome": "denied"},
                        "events": ["e1"],
                    },
                    "assumptions": ["predicate selection external"],
                    "checker_id": "post-incident.preservation",
                    "checker_version": "1.0.0",
                    "evidence_refs": ["fixtures/preservation/valid_claims.json"],
                    "predicate_ast": {
                        "kind": "equals",
                        "left_key": "outcome",
                        "right": "denied",
                    },
                },
            ]
        },
    )
    write(
        FIX / "preservation" / "reordered_retained_events.json",
        {
            "schema_version": "pip.PreservationClaim.v1",
            "claim_id": "c-order-bad",
            "claim_class": "retained_event_order_preserved",
            "inputs": {"events": ["e1", "e2", "e3", "e4"]},
            "outputs": {"retained_events": ["e3", "e1"]},
            "assumptions": [],
            "checker_id": "post-incident.preservation",
            "checker_version": "1.0.0",
            "evidence_refs": ["fixture"],
        },
    )
    write(
        FIX / "preservation" / "authorization_reference_removed.json",
        {
            "schema_version": "pip.PreservationClaim.v1",
            "claim_id": "c-auth-bad",
            "claim_class": "authorization_chain_preserved",
            "inputs": {"authorization_refs": ["auth/a"]},
            "outputs": {"authorization_refs": ["auth/a", "auth/missing"]},
            "assumptions": [],
            "checker_id": "post-incident.preservation",
            "checker_version": "1.0.0",
            "evidence_refs": ["fixture"],
        },
    )
    write(
        FIX / "preservation" / "failure_predicate_lost.json",
        {
            "schema_version": "pip.PreservationClaim.v1",
            "claim_id": "c-pred-bad",
            "claim_class": "selected_failure_predicate_preserved",
            "inputs": {"binding": {"outcome": "denied"}, "events": []},
            "outputs": {"binding": {"outcome": "allowed"}, "events": []},
            "assumptions": [],
            "checker_id": "post-incident.preservation",
            "checker_version": "1.0.0",
            "evidence_refs": ["fixture"],
            "predicate_ast": {
                "kind": "equals",
                "left_key": "outcome",
                "right": "denied",
            },
        },
    )

    # Redaction
    orig, red, man = d("original-artifact"), d("redacted-artifact"), d("redaction-manifest")
    service = "pip-ite-redactor-v1"
    write(
        FIX / "redaction" / "valid_commitment.json",
        {
            "schema_version": "pip.RedactionCommitment.v1",
            "commitment_id": "red-001",
            "original_digest": orig,
            "redacted_digest": red,
            "redaction_manifest_digest": man,
            "mapping_commitment": mapping_commitment(orig, red, man, service),
            "redaction_service_id": service,
            "verification_result": "pass",
            "protected_location_class": "protected_store",
            "public_disclosure_class": "public_digests_only",
        },
    )
    write(
        FIX / "redaction" / "commitment_mismatch.json",
        {
            "schema_version": "pip.RedactionCommitment.v1",
            "commitment_id": "red-bad",
            "original_digest": orig,
            "redacted_digest": red,
            "redaction_manifest_digest": man,
            "mapping_commitment": d("wrong-mapping"),
            "redaction_service_id": service,
            "verification_result": "pass",
            "protected_location_class": "protected_store",
            "public_disclosure_class": "public_digests_only",
        },
    )
    write(
        FIX / "redaction" / "unauthorized_redactor.json",
        {
            "schema_version": "pip.RedactionCommitment.v1",
            "commitment_id": "red-unauth",
            "original_digest": orig,
            "redacted_digest": red,
            "redaction_manifest_digest": man,
            "mapping_commitment": mapping_commitment(
                orig, red, man, "evil-redactor"
            ),
            "redaction_service_id": "evil-redactor",
            "verification_result": "pass",
            "protected_location_class": "protected_store",
            "public_disclosure_class": "public_digests_only",
        },
    )

    # Morph
    lin = valid_lineage()
    identity = lin["nodes"][2]["artifact_digest"]
    write(
        FIX / "morph" / "valid_replay_linkage.json",
        {
            "schema_version": "pip.MorphReplayReport.v1",
            "replay_id": "morph-replay-001",
            "branch_id": "branch-fixture",
            "replay_identity_digest": identity,
            "input_artifact_digests": [lin["nodes"][1]["artifact_digest"]],
            "output_artifact_digests": [identity],
            "status": "recorded",
            "lineage_node_ids": ["n2"],
        },
    )
    write(
        FIX / "morph" / "identity_mismatch.json",
        {
            "schema_version": "pip.MorphReplayReport.v1",
            "replay_id": "morph-replay-bad",
            "branch_id": "branch-fixture",
            "replay_identity_digest": d("not-in-lineage"),
            "input_artifact_digests": [lin["nodes"][1]["artifact_digest"]],
            "output_artifact_digests": [identity],
            "status": "recorded",
            "lineage_node_ids": ["n2"],
        },
    )

    # Conformance vectors (hand-checked against Lean #eval gates)
    write(
        FIX / "conformance" / "order_projection_dag.json",
        {
            "schema_version": "pip.ConformanceVectors.v1",
            "vectors": [
                {
                    "id": "order_ok",
                    "decider": "retained_event_order_preserved",
                    "full": ["e1", "e2", "e3", "e4"],
                    "retained": ["e1", "e3"],
                    "expected": True,
                },
                {
                    "id": "order_bad",
                    "decider": "retained_event_order_preserved",
                    "full": ["e1", "e2", "e3", "e4"],
                    "retained": ["e3", "e1"],
                    "expected": False,
                },
                {
                    "id": "proj_ok",
                    "decider": "relevant_state_projection_equivalent",
                    "left": [["k", "v"]],
                    "right": [["k", "v"]],
                    "expected": True,
                },
                {
                    "id": "dag_ok",
                    "decider": "transformation_graph_acyclic",
                    "edges": [["a", "b"], ["b", "c"]],
                    "expected": True,
                },
                {
                    "id": "dag_bad",
                    "decider": "transformation_graph_acyclic",
                    "edges": [["a", "b"], ["b", "a"]],
                    "expected": False,
                },
            ],
        },
    )

    # Release bundle
    rel = FIX / "release" / "valid_incident_release"
    write(rel / "source_record.json", source_record())
    write(rel / "lineage_bundle.json", lin)
    write(rel / "preservation_claims.json", json.loads((FIX / "preservation" / "valid_claims.json").read_text()))
    write(rel / "redaction_commitment.json", json.loads((FIX / "redaction" / "valid_commitment.json").read_text()))
    write(rel / "morph_replay_report.json", json.loads((FIX / "morph" / "valid_replay_linkage.json").read_text()))
    (rel / "NON_CLAIMS.md").write_text(
        "# Non-claims\n\n"
        "This release does not assert causation, remediation effectiveness, "
        "partner-secret contents, or SDE operation.\n",
        encoding="utf-8",
    )

    # checksums after files exist (except checksums itself and manifest)
    from post_incident.digests import sha256_file

    tracked = [
        "source_record.json",
        "lineage_bundle.json",
        "preservation_claims.json",
        "redaction_commitment.json",
        "morph_replay_report.json",
        "NON_CLAIMS.md",
    ]
    files = {name: sha256_file(rel / name) for name in tracked}
    write(rel / "checksums.json", {"schema_version": "pip.Checksums.v1", "files": files})
    files["checksums.json"] = sha256_file(rel / "checksums.json")
    # Re-write checksums without including self recursively; keep checksums out of self-hash
    write(
        rel / "checksums.json",
        {"schema_version": "pip.Checksums.v1", "files": {k: files[k] for k in tracked}},
    )

    public_digests = {
        "source_trace": source_record()["source_trace_digest"],
        "lineage_output": identity,
    }
    write(
        rel / "incident_release.json",
        {
            "schema_version": "pip.IncidentRelease.v1",
            "release_id": "rel-001",
            "incident_id": "inc-001",
            "source_record": "source_record.json",
            "lineage_bundle": "lineage_bundle.json",
            "preservation_claims": ["preservation_claims.json"],
            "redaction_commitments": ["redaction_commitment.json"],
            "public_artifact_digests": public_digests,
            "checksums_manifest": "checksums.json",
            "non_claims_path": "NON_CLAIMS.md",
            "morph_replay_report": "morph_replay_report.json",
        },
    )
    # Add release manifest + checksums to checksums? Bundle validator checks listed files only.
    # Include incident_release.json in checksums for stronger integrity.
    tracked2 = tracked + ["incident_release.json"]
    files2 = {name: sha256_file(rel / name) for name in tracked2}
    write(rel / "checksums.json", {"schema_version": "pip.Checksums.v1", "files": files2})

    print("fixtures generated under", FIX)


if __name__ == "__main__":
    main()
