"""Conformance vectors must agree across Python, Rust bridge, and Lean anchors."""

from __future__ import annotations

import json
from pathlib import Path

from post_incident.kernel_bridge import dag_is_acyclic, is_retained_subsequence
from post_incident.preservation import state_projection_equivalent

ROOT = Path(__file__).resolve().parents[2]
VECTORS = ROOT / "fixtures" / "conformance" / "order_projection_dag.json"


def test_conformance_vectors() -> None:
    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    for vec in data["vectors"]:
        expected = bool(vec["expected"])
        if vec["decider"] == "retained_event_order_preserved":
            actual = is_retained_subsequence(vec["full"], vec["retained"])
        elif vec["decider"] == "relevant_state_projection_equivalent":
            left = [tuple(p) for p in vec["left"]]
            right = [tuple(p) for p in vec["right"]]
            actual = state_projection_equivalent(left, right)
        elif vec["decider"] == "transformation_graph_acyclic":
            edges = [(a, b) for a, b in vec["edges"]]
            actual = dag_is_acyclic(edges)
        else:
            raise AssertionError(f"unknown decider {vec['decider']}")
        assert actual is expected, vec["id"]
