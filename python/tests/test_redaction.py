"""Redaction commitment fixture tests (PIP-ITE-05)."""

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


def test_redaction_valid() -> None:
    proc = run_cli(
        "redaction", "verify", str(FIX / "redaction" / "valid_commitment.json")
    )
    assert proc.returncode == 0


def test_redaction_mismatch_fails() -> None:
    proc = run_cli(
        "redaction", "verify", str(FIX / "redaction" / "commitment_mismatch.json")
    )
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert any(d["code"] == "commitment_mismatch" for d in payload["diagnostics"])


def test_redaction_unauthorized_fails() -> None:
    proc = run_cli(
        "redaction", "verify", str(FIX / "redaction" / "unauthorized_redactor.json")
    )
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert any(d["code"] == "unauthorized_redactor" for d in payload["diagnostics"])
