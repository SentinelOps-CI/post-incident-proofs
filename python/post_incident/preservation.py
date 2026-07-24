"""Preservation claim deciders. Fail closed / indeterminate when unsupported."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from post_incident import kernel_bridge
from post_incident.diagnostics import Diagnostic, Report, Status
from post_incident.schema_loader import load_json_file, validate_instance

SCHEMA = "PreservationClaim.schema.json"

SUPPORTED_PREDICATE_KINDS = {"equals", "not_equals", "contains_event"}


def retained_event_order_preserved(full: list[Any], retained: list[Any]) -> bool:
    """True iff retained is a subsequence of full (order-preserving)."""
    return kernel_bridge.is_retained_subsequence(
        [str(x) for x in full], [str(x) for x in retained]
    )


def authorization_chain_preserved(
    original_refs: list[str], projected_refs: list[str]
) -> bool:
    """Every projected auth ref must appear in the original chain (set + multiplicity)."""
    from collections import Counter

    return Counter(projected_refs) <= Counter(original_refs)


def state_projection_equivalent(a: Any, b: Any) -> bool:
    return a == b


def evaluate_predicate_ast(ast: dict[str, Any], binding: dict[str, Any]) -> Status:
    kind = ast.get("kind")
    if kind not in SUPPORTED_PREDICATE_KINDS:
        return Status.INDETERMINATE
    left_key = ast.get("left_key")
    if not isinstance(left_key, str):
        return Status.INDETERMINATE
    left = binding.get(left_key)
    right = ast.get("right")
    if kind == "equals":
        return Status.PASS if left == right else Status.ERROR
    if kind == "not_equals":
        return Status.PASS if left != right else Status.ERROR
    if kind == "contains_event":
        events = binding.get("events") or []
        return Status.PASS if right in events else Status.ERROR
    return Status.INDETERMINATE


def verify_claim_obj(claim: dict[str, Any], path: str) -> Report:
    report = Report(command="preservation verify")
    schema_errors = validate_instance(claim, SCHEMA)
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

    claim_class = claim["claim_class"]
    inputs = claim.get("inputs") or {}
    outputs = claim.get("outputs") or {}

    status = Status.INDETERMINATE
    code = "unsupported_claim_class"
    message = f"no decider for claim_class={claim_class}"

    if claim_class == "retained_event_order_preserved":
        full = inputs.get("events") or []
        retained = outputs.get("retained_events") or inputs.get("retained_events") or []
        if not isinstance(full, list) or not isinstance(retained, list):
            status, code, message = (
                Status.ERROR,
                "malformed_order_inputs",
                "events/retained_events must be arrays",
            )
        elif retained_event_order_preserved(full, retained):
            status, code, message = Status.PASS, "order_preserved", "retained subsequence OK"
        else:
            status, code, message = (
                Status.ERROR,
                "reordered_retained_events",
                "retained events are not an order-preserving subsequence",
            )

    elif claim_class == "authorization_chain_preserved":
        original = inputs.get("authorization_refs") or []
        projected = outputs.get("authorization_refs") or []
        if not isinstance(original, list) or not isinstance(projected, list):
            status, code, message = (
                Status.ERROR,
                "malformed_auth_inputs",
                "authorization_refs must be arrays",
            )
        elif authorization_chain_preserved(
            [str(x) for x in original], [str(x) for x in projected]
        ):
            status, code, message = Status.PASS, "auth_chain_preserved", "auth refs consistent"
        else:
            status, code, message = (
                Status.ERROR,
                "authorization_reference_removed",
                "projected authorization refs not subset of original",
            )

    elif claim_class == "relevant_state_projection_equivalent":
        left = inputs.get("projection")
        right = outputs.get("projection")
        if state_projection_equivalent(left, right):
            status, code, message = Status.PASS, "projection_equivalent", "projections equal"
        else:
            status, code, message = (
                Status.ERROR,
                "projection_mismatch",
                "relevant state projections differ",
            )

    elif claim_class == "transformation_graph_acyclic":
        edges = inputs.get("edges") or []
        pairs = [(str(e["from"]), str(e["to"])) for e in edges]
        if kernel_bridge.dag_is_acyclic(pairs):
            status, code, message = Status.PASS, "graph_acyclic", "graph is a DAG"
        else:
            status, code, message = Status.ERROR, "cyclic_lineage", "graph has a cycle"

    elif claim_class == "no_undeclared_source_artifact":
        declared = set(inputs.get("declared_source_digests") or [])
        observed = set(inputs.get("observed_source_digests") or [])
        extra = observed - declared
        if not extra:
            status, code, message = Status.PASS, "no_undeclared_source", "no undeclared sources"
        else:
            status, code, message = (
                Status.ERROR,
                "undeclared_source_artifact",
                f"undeclared sources: {sorted(extra)}",
            )

    elif claim_class == "digest_lineage_preserved":
        expected = inputs.get("lineage_output_digest")
        actual = outputs.get("artifact_digest")
        if expected and actual and expected == actual:
            status, code, message = Status.PASS, "digest_lineage_ok", "output digest matches"
        else:
            status, code, message = (
                Status.ERROR,
                "digest_lineage_mismatch",
                "lineage output digest mismatch",
            )

    elif claim_class == "selected_failure_predicate_preserved":
        ast = claim.get("predicate_ast")
        if not isinstance(ast, dict):
            status, code, message = (
                Status.INDETERMINATE,
                "predicate_ast_missing",
                "failure-predicate selection/sufficiency external; embed supported predicate_ast",
            )
        else:
            binding = {
                **(inputs.get("binding") or {}),
                "events": inputs.get("events") or [],
            }
            # Also require output binding still satisfies predicate
            out_binding = {
                **binding,
                **(outputs.get("binding") or {}),
                "events": outputs.get("events") or inputs.get("events") or [],
            }
            in_status = evaluate_predicate_ast(ast, binding)
            out_status = evaluate_predicate_ast(ast, out_binding)
            if Status.INDETERMINATE in (in_status, out_status):
                status, code, message = (
                    Status.INDETERMINATE,
                    "predicate_unsupported",
                    f"unsupported predicate kind={ast.get('kind')}",
                )
            elif in_status == Status.PASS and out_status == Status.PASS:
                status, code, message = (
                    Status.PASS,
                    "failure_predicate_preserved",
                    "predicate holds on inputs and outputs",
                )
            else:
                status, code, message = (
                    Status.ERROR,
                    "failure_predicate_lost",
                    "supported failure predicate does not hold after transformation",
                )

    elif claim_class == "redacted_values_irrelevant_to_declared_predicate":
        # Structural check only: claim must declare irrelevance assumption + predicate id.
        assumptions = claim.get("assumptions") or []
        has_irrelevance = "irrelevance_assumption" in assumptions or any(
            isinstance(a, str) and "irrelevant" in a.lower() for a in assumptions
        )
        if "predicate_id" in inputs and has_irrelevance:
            # Without protected values we can only check declaration completeness.
            if inputs.get("redacted_field_ids") and outputs.get(
                "predicate_result"
            ) == inputs.get("predicate_result"):
                status, code, message = (
                    Status.PASS,
                    "redacted_irrelevant_declared",
                    "declared predicate result unchanged under redaction commitment",
                )
            else:
                status, code, message = (
                    Status.ERROR,
                    "redaction_relevance_mismatch",
                    "predicate_result changed or redacted_field_ids missing",
                )
        else:
            status, code, message = (
                Status.INDETERMINATE,
                "redaction_irrelevance_undeclared",
                "missing irrelevance assumption or predicate_id",
            )

    report.add(
        Diagnostic(
            status=status,
            code=code,
            path=path,
            message=message,
            evidence_refs=[claim["claim_id"], claim_class],
        )
    )
    return report


def verify_claim_file(path: Path) -> Report:
    try:
        obj = load_json_file(path)
    except (OSError, ValueError) as exc:
        report = Report(command="preservation verify")
        report.add(
            Diagnostic(
                status=Status.ERROR,
                code="load_failed",
                path=str(path),
                message=str(exc),
            )
        )
        return report
    # Allow a single claim or a list wrapper {"claims": [...]}
    if "claims" in obj and isinstance(obj["claims"], list):
        report = Report(command="preservation verify")
        for i, claim in enumerate(obj["claims"]):
            sub = verify_claim_obj(claim, f"{path}#claims/{i}")
            report.diagnostics.extend(sub.diagnostics)
        if not report.diagnostics:
            report.add(
                Diagnostic(
                    status=Status.ERROR,
                    code="empty_claims",
                    path=str(path),
                    message="claims array empty",
                )
            )
        return report
    return verify_claim_obj(obj, str(path))
