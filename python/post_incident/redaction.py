"""Redaction commitment verification (public digests only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from post_incident.diagnostics import Diagnostic, Report, Status
from post_incident.digests import is_digest, sha256_canonical_json
from post_incident.schema_loader import load_json_file, validate_instance

SCHEMA = "RedactionCommitment.schema.json"

# Offline allow-list of authorized redaction service identities (synthetic).
AUTHORIZED_REDACTORS = frozenset(
    {
        "redaction-service.pip-ite.local",
        "pip-ite-redactor-v1",
    }
)


def verify_commitment_obj(obj: dict[str, Any], path: str) -> Report:
    report = Report(command="redaction verify")
    schema_errors = validate_instance(obj, SCHEMA)
    if schema_errors:
        for msg in schema_errors:
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="schema_invalid",
                    path=path,
                    message=msg,
                )
            )
        return report

    for field in (
        "original_digest",
        "redacted_digest",
        "redaction_manifest_digest",
        "mapping_commitment",
    ):
        if not is_digest(obj[field]):
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="digest_malformed",
                    path=f"{path}/{field}",
                    message=f"malformed {field}",
                )
            )
            return report

    service = obj["redaction_service_id"]
    if service not in AUTHORIZED_REDACTORS:
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="unauthorized_redactor",
                path=f"{path}/redaction_service_id",
                message=f"redaction_service_id not in offline allow-list: {service}",
                evidence_refs=[service],
            )
        )
        return report

    # Mapping commitment binds the four digests; verifier recomputes expected commitment.
    material = {
        "original_digest": obj["original_digest"],
        "redacted_digest": obj["redacted_digest"],
        "redaction_manifest_digest": obj["redaction_manifest_digest"],
        "redaction_service_id": service,
    }
    expected_mapping = sha256_canonical_json(material)
    if obj["mapping_commitment"] != expected_mapping:
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="commitment_mismatch",
                path=f"{path}/mapping_commitment",
                message="mapping_commitment does not match bound digests",
                evidence_refs=[obj["mapping_commitment"], expected_mapping],
            )
        )
        return report

    if obj["original_digest"] == obj["redacted_digest"]:
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="commitment_mismatch",
                path=path,
                message="original and redacted digests must differ for a redaction commitment",
            )
        )
        return report

    if obj.get("verification_result") == "fail":
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="declared_verification_fail",
                path=f"{path}/verification_result",
                message="commitment declares verification_result=fail",
            )
        )
        return report

    report.add(
        Diagnostic(
            status=Status.PASS,
            code="redaction_commitment_valid",
            path=path,
            message="redaction commitment digests and allow-listed service OK",
            evidence_refs=[obj["commitment_id"], expected_mapping],
        )
    )
    return report


def verify_commitment_file(path: Path) -> Report:
    try:
        obj = load_json_file(path)
    except (OSError, ValueError) as exc:
        report = Report(command="redaction verify")
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="load_failed",
                path=str(path),
                message=str(exc),
            )
        )
        return report
    return verify_commitment_obj(obj, str(path))
