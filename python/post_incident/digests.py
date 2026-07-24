"""Real SHA-256 digests (not Lean stub crypto)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

DIGEST_RE = re.compile(r"^sha256:[a-f0-9]{64}$")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def is_digest(value: str) -> bool:
    return bool(DIGEST_RE.match(value))


def canonical_json_bytes(obj: Any) -> bytes:
    """RFC-style canonical JSON: UTF-8, sorted keys, no insignificant whitespace."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_canonical_json(obj: Any) -> str:
    return sha256_bytes(canonical_json_bytes(obj))


def verify_declared_digest(data: bytes, declared: str) -> bool:
    if not is_digest(declared):
        return False
    return sha256_bytes(data) == declared
