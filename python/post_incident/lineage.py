"""Transformation lineage DAG validation and graph export."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from post_incident import kernel_bridge
from post_incident.diagnostics import Diagnostic, Report, Status
from post_incident.digests import is_digest, sha256_canonical_json
from post_incident.schema_loader import load_json_file, validate_instance

BUNDLE_SCHEMA = "LineageBundle.schema.json"


def _node_map(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {n["node_id"]: n for n in bundle.get("nodes") or []}


def _xform_map(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {t["transformation_id"]: t for t in bundle.get("transformations") or []}


def is_acyclic(edges: list[tuple[str, str]]) -> bool:
    """Kahn topological check; True iff DAG."""
    return kernel_bridge.dag_is_acyclic(edges)


def validate_lineage_obj(bundle: dict[str, Any], path: str) -> Report:
    report = Report(command="lineage validate")
    schema_errors = validate_instance(bundle, BUNDLE_SCHEMA)
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

    nodes = _node_map(bundle)
    xforms = _xform_map(bundle)
    edges = bundle.get("edges") or []

    # Unique node ids
    if len(nodes) != len(bundle["nodes"]):
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="duplicate_node_id",
                path=f"{path}/nodes",
                message="node_id values must be unique",
            )
        )
        return report

    digest_to_nodes: dict[str, list[str]] = defaultdict(list)
    for nid, node in nodes.items():
        digest_to_nodes[node["artifact_digest"]].append(nid)

    edge_pairs: list[tuple[str, str]] = []
    for i, edge in enumerate(edges):
        frm = edge["from_node_id"]
        to = edge["to_node_id"]
        tid = edge["transformation_id"]
        epath = f"{path}/edges/{i}"
        if frm not in nodes or to not in nodes:
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="unresolved_edge_ref",
                    path=epath,
                    message=f"edge references unknown node ({frm} -> {to})",
                )
            )
            return report
        if tid not in xforms:
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="unresolved_transformation_ref",
                    path=epath,
                    message=f"edge references unknown transformation_id={tid}",
                )
            )
            return report
        edge_pairs.append((frm, to))

        xform = xforms[tid]
        # Each output declares inputs: edge endpoints must match transformation digests
        in_digests = set(xform["input_artifact_digests"])
        out_digest = xform["output_artifact_digest"]
        if nodes[frm]["artifact_digest"] not in in_digests:
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="undeclared_transformation_input",
                    path=epath,
                    message=(
                        f"from_node digest not in transformation {tid} inputs"
                    ),
                    evidence_refs=[nodes[frm]["artifact_digest"], tid],
                )
            )
            return report
        if nodes[to]["artifact_digest"] != out_digest:
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="transformed_artifact_substituted",
                    path=epath,
                    message=(
                        "to_node digest does not match declared transformation output"
                    ),
                    evidence_refs=[nodes[to]["artifact_digest"], out_digest],
                )
            )
            return report

    if not is_acyclic(edge_pairs):
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="cyclic_lineage",
                path=f"{path}/edges",
                message="transformation lineage graph contains a cycle",
            )
        )
        return report

    # Immutability: record_digest must match canonical content excluding itself
    for tid, xform in xforms.items():
        material = {k: v for k, v in xform.items() if k != "record_digest"}
        expected = sha256_canonical_json(material)
        if xform.get("record_digest") != expected:
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="record_digest_mismatch",
                    path=f"{path}/transformations/{tid}/record_digest",
                    message="record_digest does not match content (immutability check)",
                    evidence_refs=[str(xform.get("record_digest")), expected],
                )
            )
            return report
        for d in list(xform["input_artifact_digests"]) + [
            xform["output_artifact_digest"],
            xform["container_digest"],
        ]:
            if not is_digest(d):
                report.add(
                    Diagnostic(
                        status=Status.ERROR,
                        code="digest_malformed",
                        path=f"{path}/transformations/{tid}",
                        message=f"malformed digest {d}",
                    )
                )
                return report

    # Every transformation output must appear as a node (no silent orphan outputs)
    node_digests = {n["artifact_digest"] for n in nodes.values()}
    for tid, xform in xforms.items():
        if xform["output_artifact_digest"] not in node_digests:
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="output_not_in_graph",
                    path=f"{path}/transformations/{tid}",
                    message="transformation output digest missing from nodes",
                )
            )
            return report
        for inp in xform["input_artifact_digests"]:
            if inp not in node_digests:
                report.add(
                    Diagnostic(
                        status=Status.ERROR,
                        code="undeclared_transformation_input",
                        path=f"{path}/transformations/{tid}",
                        message=f"input digest {inp} not present as a lineage node",
                        evidence_refs=[inp],
                    )
                )
                return report

    report.add(
        Diagnostic(
            status=Status.PASS,
            code="lineage_valid",
            path=path,
            message="LineageBundle refs resolve, DAG acyclic, digests consistent",
            evidence_refs=[bundle["bundle_id"]],
        )
    )
    return report


def validate_lineage_file(path: Path) -> Report:
    try:
        obj = load_json_file(path)
    except (OSError, ValueError) as exc:
        report = Report(command="lineage validate")
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="load_failed",
                path=str(path),
                message=str(exc),
            )
        )
        return report
    return validate_lineage_obj(obj, str(path))


def export_graph(bundle: dict[str, Any]) -> dict[str, Any]:
    """Export a JSON graph suitable for visualization / reconstruction."""
    return {
        "bundle_id": bundle.get("bundle_id"),
        "incident_id": bundle.get("incident_id"),
        "nodes": [
            {
                "id": n["node_id"],
                "digest": n["artifact_digest"],
                "role": n["role"],
            }
            for n in bundle.get("nodes") or []
        ],
        "edges": [
            {
                "from": e["from_node_id"],
                "to": e["to_node_id"],
                "transformation_id": e["transformation_id"],
            }
            for e in bundle.get("edges") or []
        ],
        "acyclic": is_acyclic(
            [(e["from_node_id"], e["to_node_id"]) for e in bundle.get("edges") or []]
        ),
    }


def lineage_graph_file(path: Path, out: Path) -> Report:
    report = validate_lineage_file(path)
    if not report.ok:
        return report
    bundle = load_json_file(path)
    graph = export_graph(bundle)
    out.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report.command = "lineage graph"
    report.add(
        Diagnostic(
            status=Status.PASS,
            code="graph_exported",
            path=str(out),
            message="lineage graph written",
        )
    )
    return report
