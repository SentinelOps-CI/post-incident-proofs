"""Morph replay fixture tests (PIP-ITE-06)."""

from __future__ import annotations

import json
import shutil
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


def _lineage_dir(tmp_path: Path) -> Path:
    release = tmp_path / "replay_ctx"
    release.mkdir()
    shutil.copyfile(
        FIX / "lineage" / "valid_dag.json", release / "lineage_bundle.json"
    )
    return release


def test_morph_replay_ok(tmp_path: Path) -> None:
    proc = run_cli(
        "replay-check",
        str(_lineage_dir(tmp_path)),
        "--replay-report",
        str(FIX / "morph" / "valid_replay_linkage.json"),
    )
    assert proc.returncode == 0


def test_morph_identity_mismatch_fails(tmp_path: Path) -> None:
    proc = run_cli(
        "replay-check",
        str(_lineage_dir(tmp_path)),
        "--replay-report",
        str(FIX / "morph" / "identity_mismatch.json"),
    )
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert any(d["code"] == "replay_identity_mismatch" for d in payload["diagnostics"])
