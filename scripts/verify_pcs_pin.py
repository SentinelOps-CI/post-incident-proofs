#!/usr/bin/env python3
"""Verify vendored PCS schema bytes match SCHEMA_MIRROR local_digests (fail closed)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRROR = ROOT / "schemas" / "pcs" / "SCHEMA_MIRROR.json"
PCS_DIR = ROOT / "schemas" / "pcs"


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not MIRROR.is_file():
        print({"status": "error", "code": "missing_mirror", "path": str(MIRROR)})
        return 1
    try:
        meta = json.loads(MIRROR.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print({"status": "error", "code": "mirror_load_failed", "message": str(exc)})
        return 1

    digests = meta.get("local_digests")
    files = meta.get("vendored_files")
    if not isinstance(digests, dict) or not isinstance(files, list) or not files:
        print({"status": "error", "code": "mirror_incomplete"})
        return 1

    mismatches: list[dict[str, str]] = []
    for name in files:
        if not isinstance(name, str):
            mismatches.append({"file": str(name), "reason": "invalid_name"})
            continue
        path = PCS_DIR / name
        if not path.is_file():
            mismatches.append({"file": name, "reason": "missing"})
            continue
        expected = digests.get(name)
        actual = sha256_file(path)
        if expected != actual:
            mismatches.append(
                {
                    "file": name,
                    "reason": "digest_mismatch",
                    "expected": str(expected),
                    "actual": actual,
                }
            )

    if mismatches:
        print({"status": "error", "code": "pcs_pin_drift", "mismatches": mismatches})
        return 1
    print({"status": "ok", "code": "pcs_pin_verified", "files": files})
    return 0


if __name__ == "__main__":
    sys.exit(main())
