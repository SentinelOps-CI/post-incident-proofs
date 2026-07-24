"""Privacy guards: public fixtures must not contain secrets or forbidden fields."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "redacted_value",
        "raw_partner_payload",
        "partner_secret",
        "private_key",
        "password",
        "api_key",
        "authorization_token",
    }
)

# High-entropy hex/base64-ish secrets (excluding sha256: digests).
HIGH_ENTROPY_RE = re.compile(
    r"(?<!sha256:)(?<![a-f0-9])[A-Za-z0-9+/]{40,}={0,2}(?![a-f0-9])"
)
AWS_KEY_RE = re.compile(r"AKIA[0-9A-Z]{16}")
PEM_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")

# Signature / identity fields that are expected to be high-entropy in public fixtures.
ALLOWED_HIGH_ENTROPY_KEYS = frozenset({"value", "key_id", "signed_at", "collector_id"})


def _is_sha256_digest(value: str) -> bool:
    return value.startswith("sha256:") and len(value) == 71


def scan_obj(obj: Any, source: str) -> list[str]:
    findings: list[str] = []

    def visit(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                loc = f"{path}.{key}"
                if key in FORBIDDEN_FIELD_NAMES:
                    findings.append(f"{source}:{loc}: forbidden field name")
                visit(value, loc)
            return
        if isinstance(node, list):
            for i, value in enumerate(node):
                visit(value, f"{path}[{i}]")
            return
        if not isinstance(node, str):
            return
        key = path.rsplit(".", 1)[-1]
        if PEM_RE.search(node) or AWS_KEY_RE.search(node):
            findings.append(f"{source}:{path}: secret-like material")
            return
        if _is_sha256_digest(node):
            return
        if key in ALLOWED_HIGH_ENTROPY_KEYS:
            return
        if "digest" in key.lower():
            return
        if HIGH_ENTROPY_RE.fullmatch(node) and len(node) >= 48:
            findings.append(f"{source}:{path}: high-entropy secret-like string")

    visit(obj, "$")
    return findings


def scan_path(path: Path) -> list[str]:
    if path.is_file() and path.suffix == ".json":
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return [f"{path}: load_failed: {exc}"]
        return scan_obj(obj, str(path))
    if path.is_dir():
        findings: list[str] = []
        for fp in sorted(path.rglob("*.json")):
            findings.extend(scan_path(fp))
        return findings
    return []


def assert_fixtures_private_free(fixtures_root: Path) -> None:
    findings = scan_path(fixtures_root)
    if findings:
        raise AssertionError("privacy guard failed:\n" + "\n".join(findings))
