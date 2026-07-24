"""Lineage validation fixture tests (PIP-ITE-02)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "fixtures"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "post_incident", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_lineage_valid_and_graph(tmp_path: Path) -> None:
    proc = run_cli("lineage", "validate", str(FIX / "lineage" / "valid_dag.json"))
    assert proc.returncode == 0
    out = tmp_path / "graph.json"
    proc = run_cli(
        "lineage", "graph", str(FIX / "lineage" / "valid_dag.json"), "--out", str(out)
    )
    assert proc.returncode == 0
    graph = json.loads(out.read_text(encoding="utf-8"))
    assert graph["acyclic"] is True


def test_lineage_cyclic_fails() -> None:
    proc = run_cli("lineage", "validate", str(FIX / "lineage" / "cyclic.json"))
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert any(d["code"] == "cyclic_lineage" for d in payload["diagnostics"])


def test_lineage_undeclared_input_fails() -> None:
    proc = run_cli("lineage", "validate", str(FIX / "lineage" / "undeclared_input.json"))
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert any(
        d["code"] == "undeclared_transformation_input" for d in payload["diagnostics"]
    )


def test_lineage_substituted_fails() -> None:
    proc = run_cli(
        "lineage", "validate", str(FIX / "lineage" / "artifact_substituted.json")
    )
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert any(
        d["code"] == "transformed_artifact_substituted" for d in payload["diagnostics"]
    )
