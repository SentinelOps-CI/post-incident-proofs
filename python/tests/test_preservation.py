"""Preservation claim fixture tests (PIP-ITE-03)."""

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


def test_preservation_valid() -> None:
    proc = run_cli(
        "preservation", "verify", str(FIX / "preservation" / "valid_claims.json")
    )
    assert proc.returncode == 0


def test_preservation_reordered_fails() -> None:
    proc = run_cli(
        "preservation",
        "verify",
        str(FIX / "preservation" / "reordered_retained_events.json"),
    )
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert any(d["code"] == "reordered_retained_events" for d in payload["diagnostics"])


def test_preservation_auth_removed_fails() -> None:
    proc = run_cli(
        "preservation",
        "verify",
        str(FIX / "preservation" / "authorization_reference_removed.json"),
    )
    assert proc.returncode != 0


def test_preservation_predicate_lost_fails() -> None:
    proc = run_cli(
        "preservation",
        "verify",
        str(FIX / "preservation" / "failure_predicate_lost.json"),
    )
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert any(d["code"] == "failure_predicate_lost" for d in payload["diagnostics"])
