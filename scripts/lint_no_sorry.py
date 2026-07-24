#!/usr/bin/env python3
"""Fail if ITE Lean modules contain sorry."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "src" / "PostIncidentProofs" / "Lineage",
    ROOT / "src" / "PostIncidentProofs" / "Preservation",
]
SORRY = re.compile(r"\bsorry\b")


def main() -> int:
    hits: list[str] = []
    for base in TARGETS:
        for path in base.rglob("*.lean"):
            text = path.read_text(encoding="utf-8")
            for i, line in enumerate(text.splitlines(), start=1):
                if SORRY.search(line) and not line.strip().startswith("--"):
                    hits.append(f"{path.relative_to(ROOT)}:{i}:{line.strip()}")
    if hits:
        print({"status": "error", "code": "sorry_found", "hits": hits})
        return 1
    print({"status": "ok", "code": "no_sorry"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
