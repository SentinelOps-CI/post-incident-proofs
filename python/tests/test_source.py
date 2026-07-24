"""Source validation fixture tests (PIP-ITE-01)."""

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


def test_source_valid_complete() -> None:
    proc = run_cli("source", "validate", str(FIX / "source" / "valid_complete.json"))
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["status"] == "pass"


def test_source_valid_incomplete() -> None:
    proc = run_cli("source", "validate", str(FIX / "source" / "valid_incomplete.json"))
    assert proc.returncode == 0


def test_source_changed_digest_fails() -> None:
    proc = run_cli("source", "validate", str(FIX / "source" / "changed_source_digest.json"))
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert payload["status"] == "error"
    assert any(d["code"] == "envelope_digest_mismatch" for d in payload["diagnostics"])


def test_fail_closed_missing_file() -> None:
    proc = run_cli("source", "validate", str(FIX / "source" / "does_not_exist.json"))
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert payload["status"] == "error"
