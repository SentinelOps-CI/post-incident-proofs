"""Privacy guards over public fixtures."""

from __future__ import annotations

from pathlib import Path

from post_incident.privacy import assert_fixtures_private_free, scan_obj

ROOT = Path(__file__).resolve().parents[2]


def test_fixtures_have_no_forbidden_secrets() -> None:
    assert_fixtures_private_free(ROOT / "fixtures")


def test_forbidden_field_detected() -> None:
    findings = scan_obj({"redacted_value": "secret"}, "mem")
    assert findings
