#!/usr/bin/env python3
"""Capture legacy baseline command results for PIP-ITE-00 documentation."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "baseline" / "baseline_results.json"

COMMANDS = [
    ["lake", "build"],
    ["lake", "exe", "tests"],
    ["make", "ci"],
]


def run(cmd: list[str]) -> dict:
    started = time.perf_counter()
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, shell=False)
    elapsed = time.perf_counter() - started
    return {
        "command": cmd,
        "exit_code": proc.returncode,
        "elapsed_sec": round(elapsed, 3),
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def main() -> int:
    results = [run(cmd) for cmd in COMMANDS]
    payload = {
        "base_commit_expected": "3cdfdf09c20f08ad5221d29607b5a9726295ad10",
        "lean_toolchain": "leanprover/lean4:v4.7.0",
        "results": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "path": str(OUT)}, indent=2))
    return 0 if all(r["exit_code"] == 0 for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
