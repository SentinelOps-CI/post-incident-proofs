"""Incident release bundle fixture tests (PIP-ITE-07)."""

from __future__ import annotations

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


def test_bundle_validate() -> None:
    proc = run_cli(
        "bundle", "validate", str(FIX / "release" / "valid_incident_release")
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
