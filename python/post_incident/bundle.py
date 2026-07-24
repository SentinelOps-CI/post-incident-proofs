"""Incident release bundle validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from post_incident.diagnostics import Diagnostic, Report, Status
from post_incident.digests import sha256_file
from post_incident.lineage import validate_lineage_file
from post_incident.morph import replay_check
from post_incident.preservation import verify_claim_file
from post_incident.redaction import verify_commitment_file
from post_incident.schema_loader import load_json_file, validate_instance
from post_incident.source import validate_source_file

MANIFEST_NAME = "incident_release.json"
SCHEMA = "IncidentRelease.schema.json"


def validate_bundle(release_dir: Path) -> Report:
    report = Report(command="bundle validate")
    release_dir = release_dir.resolve()
    if not release_dir.is_dir():
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="missing_release_dir",
                path=str(release_dir),
                message="incident_release path is not a directory",
            )
        )
        return report

    manifest_path = release_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="missing_manifest",
                path=str(manifest_path),
                message="incident_release.json required",
            )
        )
        return report

    try:
        manifest = load_json_file(manifest_path)
    except (OSError, ValueError) as exc:
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="load_failed",
                path=str(manifest_path),
                message=str(exc),
            )
        )
        return report

    for msg in validate_instance(manifest, SCHEMA):
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="schema_invalid",
                path=str(manifest_path),
                message=msg,
            )
        )
        return report

    non_claims = release_dir / manifest["non_claims_path"]
    if not non_claims.is_file():
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="missing_non_claims",
                path=str(non_claims),
                message="NON_CLAIMS.md required in release bundle",
            )
        )
        return report

    checksums_path = release_dir / manifest["checksums_manifest"]
    if not checksums_path.is_file():
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="missing_checksums",
                path=str(checksums_path),
                message="checksums manifest required",
            )
        )
        return report

    try:
        checksums: dict[str, Any] = json.loads(
            checksums_path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="checksums_invalid",
                path=str(checksums_path),
                message=str(exc),
            )
        )
        return report

    files_map = checksums.get("files") or {}
    if not isinstance(files_map, dict) or not files_map:
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="checksums_empty",
                path=str(checksums_path),
                message="checksums.files must be a non-empty object",
            )
        )
        return report

    for rel, expected in files_map.items():
        fp = release_dir / rel
        if not fp.is_file():
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="checksum_file_missing",
                    path=str(fp),
                    message=f"checksums lists missing file {rel}",
                )
            )
            return report
        actual = sha256_file(fp)
        if actual != expected:
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="checksum_mismatch",
                    path=str(fp),
                    message="file digest does not match checksums manifest",
                    evidence_refs=[str(expected), actual],
                )
            )
            return report

    # Nested validations
    source_path = release_dir / manifest["source_record"]
    sub = validate_source_file(source_path)
    report.diagnostics.extend(sub.diagnostics)
    if not sub.ok:
        return report

    lineage_path = release_dir / manifest["lineage_bundle"]
    sub = validate_lineage_file(lineage_path)
    report.diagnostics.extend(sub.diagnostics)
    if not sub.ok:
        return report

    for rel in manifest.get("preservation_claims") or []:
        sub = verify_claim_file(release_dir / rel)
        report.diagnostics.extend(sub.diagnostics)
        if not sub.ok:
            return report

    for rel in manifest.get("redaction_commitments") or []:
        sub = verify_commitment_file(release_dir / rel)
        report.diagnostics.extend(sub.diagnostics)
        if not sub.ok:
            return report

    morph_rel = manifest.get("morph_replay_report")
    if morph_rel:
        sub = replay_check(
            release_dir,
            release_dir / morph_rel,
            lineage_path=lineage_path,
        )
        report.diagnostics.extend(sub.diagnostics)
        if not sub.ok:
            return report

    report.add(
        Diagnostic(
            status=Status.PASS,
            code="bundle_valid",
            path=str(release_dir),
            message="incident_release bundle validated without protected content",
            evidence_refs=[manifest["release_id"]],
        )
    )
    return report
