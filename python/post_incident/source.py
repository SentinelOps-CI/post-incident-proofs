"""IncidentSourceRecord validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from post_incident.diagnostics import Diagnostic, Report, Status
from post_incident.digests import is_digest
from post_incident.schema_loader import load_json_file, validate_instance

SCHEMA = "IncidentSourceRecord.schema.json"


def validate_source_obj(obj: dict[str, Any], path: str) -> Report:
    report = Report(command="source validate")
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

    completeness = obj.get("completeness")
    gaps = obj.get("known_missing_evidence") or []
    if completeness == "incomplete" and not gaps:
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="incomplete_without_gaps",
                path=f"{path}/known_missing_evidence",
                message="completeness=incomplete requires explicit known_missing_evidence gaps",
            )
        )
        return report
    if completeness == "complete" and gaps:
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="complete_with_gaps",
                path=f"{path}/known_missing_evidence",
                message="completeness=complete forbids known_missing_evidence entries",
            )
        )
        return report

    for field in (
        "source_trace_digest",
        "initial_state_commitment",
        "final_state_commitment",
    ):
        digest = obj.get(field)
        if not isinstance(digest, str) or not is_digest(digest):
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="digest_malformed",
                    path=f"{path}/{field}",
                    message=f"invalid digest for {field}",
                )
            )
            return report

    envelope = obj.get("integrity_envelope") or {}
    art = envelope.get("artifact_digest")
    if art != obj.get("source_trace_digest"):
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="envelope_digest_mismatch",
                path=f"{path}/integrity_envelope/artifact_digest",
                message="integrity_envelope.artifact_digest must equal source_trace_digest",
                evidence_refs=[str(art), str(obj.get("source_trace_digest"))],
            )
        )
        return report

    report.add(
        Diagnostic(
            status=Status.PASS,
            code="source_valid",
            path=path,
            message="IncidentSourceRecord schema and integrity envelope reference OK",
            evidence_refs=[obj["incident_id"], obj["source_trace_digest"]],
        )
    )
    return report


def validate_source_file(path: Path) -> Report:
    try:
        obj = load_json_file(path)
    except (OSError, ValueError) as exc:
        report = Report(command="source validate")
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="load_failed",
                path=str(path),
                message=str(exc),
            )
        )
        return report
    return validate_source_obj(obj, str(path))
