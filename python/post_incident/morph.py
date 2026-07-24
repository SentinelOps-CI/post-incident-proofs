"""Morph replay-check against recorded fixtures (no live Morph Cloud)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from post_incident.diagnostics import Diagnostic, Report, Status
from post_incident.lineage import validate_lineage_obj
from post_incident.schema_loader import load_json_file, validate_instance

REPORT_SCHEMA = "MorphReplayReport.schema.json"


def replay_check_objs(
    report_obj: dict[str, Any],
    lineage_obj: dict[str, Any],
    report_path: str,
    lineage_path: str,
) -> Report:
    out = Report(command="replay-check")
    for msg in validate_instance(report_obj, REPORT_SCHEMA):
        out.add(
            Diagnostic(
                status=Status.ERROR,
                code="schema_invalid",
                path=report_path,
                message=msg,
            )
        )
        return out

    lin = validate_lineage_obj(lineage_obj, lineage_path)
    if not lin.ok:
        out.diagnostics.extend(lin.diagnostics)
        return out

    node_digests = {n["artifact_digest"] for n in lineage_obj.get("nodes") or []}
    node_ids = {n["node_id"] for n in lineage_obj.get("nodes") or []}

    for digest in report_obj.get("output_artifact_digests") or []:
        if digest not in node_digests:
            out.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="replay_output_not_in_lineage",
                    path=report_path,
                    message=f"replay output digest missing from lineage: {digest}",
                    evidence_refs=[digest],
                )
            )
            return out

    for digest in report_obj.get("input_artifact_digests") or []:
        if digest not in node_digests:
            out.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="replay_input_not_in_lineage",
                    path=report_path,
                    message=f"replay input digest missing from lineage: {digest}",
                    evidence_refs=[digest],
                )
            )
            return out

    for nid in report_obj.get("lineage_node_ids") or []:
        if nid not in node_ids:
            out.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="replay_node_missing",
                    path=report_path,
                    message=f"lineage_node_id not in bundle: {nid}",
                )
            )
            return out

    identity = report_obj["replay_identity_digest"]
    if not any(n["artifact_digest"] == identity for n in lineage_obj.get("nodes") or []):
        out.add(
            Diagnostic(
                status=Status.ERROR,
                code="replay_identity_mismatch",
                path=report_path,
                message="replay_identity_digest not bound to any lineage node",
                evidence_refs=[identity],
            )
        )
        return out

    if report_obj.get("status") == "mismatch":
        out.add(
            Diagnostic(
                status=Status.ERROR,
                code="replay_status_mismatch",
                path=f"{report_path}/status",
                message="recorded Morph report status=mismatch",
            )
        )
        return out

    out.add(
        Diagnostic(
            status=Status.PASS,
            code="replay_linked",
            path=report_path,
            message="Morph replay report digests bind to lineage nodes",
            evidence_refs=[report_obj["replay_id"], identity],
        )
    )
    return out


def replay_check(
    release_dir: Path, replay_report: Path, lineage_path: Path | None = None
) -> Report:
    try:
        report_obj = load_json_file(replay_report)
    except (OSError, ValueError) as exc:
        r = Report(command="replay-check")
        r.add(
            Diagnostic(
                status=Status.ERROR,
                code="load_failed",
                path=str(replay_report),
                message=str(exc),
            )
        )
        return r

    if lineage_path is None:
        # Convention inside incident_release/
        candidate = release_dir / "lineage_bundle.json"
        if not candidate.is_file():
            # Also allow manifest-driven path
            manifest = release_dir / "incident_release.json"
            if manifest.is_file():
                man = load_json_file(manifest)
                candidate = release_dir / man["lineage_bundle"]
        lineage_path = candidate

    try:
        lineage_obj = load_json_file(lineage_path)
    except (OSError, ValueError) as exc:
        r = Report(command="replay-check")
        r.add(
            Diagnostic(
                status=Status.ERROR,
                code="load_failed",
                path=str(lineage_path),
                message=str(exc),
            )
        )
        return r

    return replay_check_objs(
        report_obj, lineage_obj, str(replay_report), str(lineage_path)
    )
