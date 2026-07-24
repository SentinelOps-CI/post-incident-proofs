"""Adversarial / fail-closed cases."""

from __future__ import annotations

import json
from pathlib import Path

from post_incident.source import validate_source_obj


def test_empty_object_fails() -> None:
    report = validate_source_obj({}, "mem")
    assert not report.ok
    assert report.to_dict()["status"] == "error"


def test_malformed_digest_fails(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"schema_version": "pip.IncidentSourceRecord.v1"}), encoding="utf-8")
    from post_incident.source import validate_source_file

    report = validate_source_file(path)
    assert not report.ok
