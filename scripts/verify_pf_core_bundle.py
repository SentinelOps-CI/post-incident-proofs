#!/usr/bin/env python3
"""Verify PF-Core emit-artifacts five-file bundle layout (Phase 7 PR-1)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REQUIRED_FILES = (
    "runtime_observation.json",
    "event.json",
    "trace.json",
    "certificate.json",
    "audit.jsonl",
)

GENESIS = "0" * 64


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_hash(value: str) -> str:
    text = str(value).strip().lower()
    if text.startswith("sha256:"):
        text = text[7:]
    if len(text) != 64 or any(c not in "0123456789abcdef" for c in text):
        raise ValueError(f"invalid hash: {value!r}")
    return text


def _verify_structure(bundle_dir: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (bundle_dir / name).is_file():
            errors.append(f"missing required file: {name}")
    if errors:
        return errors

    cert = _load_json(bundle_dir / "certificate.json")
    trace = _load_json(bundle_dir / "trace.json")
    event = _load_json(bundle_dir / "event.json")
    obs = _load_json(bundle_dir / "runtime_observation.json")

    if cert.get("safe") is not True:
        errors.append("certificate.safe must be true for passing bundles")

    cert_trace = _normalize_hash(str(cert.get("trace_hash", "")))
    trace_hash = _normalize_hash(str(trace.get("trace_hash", "")))
    if cert_trace != trace_hash:
        errors.append(
            f"certificate.trace_hash ({cert_trace}) != trace.trace_hash ({trace_hash})"
        )

    events = trace.get("events")
    if not isinstance(events, list) or not events:
        errors.append("trace.events must be a non-empty list")
        return errors

    prev = GENESIS
    for idx, ev in enumerate(events):
        if not isinstance(ev, Mapping):
            errors.append(f"events[{idx}] must be an object")
            continue
        prev_field = _normalize_hash(str(ev.get("previous_event_hash", "")))
        if prev_field != prev:
            errors.append(
                f"events[{idx}].previous_event_hash mismatch: expected {prev}, got {prev_field}"
            )
        event_hash = _normalize_hash(str(ev.get("event_hash", "")))
        prev = event_hash

    if events:
        top_event_hash = _normalize_hash(str(event.get("event_hash", "")))
        last_trace_hash = _normalize_hash(str(events[-1].get("event_hash", "")))
        if top_event_hash != last_trace_hash:
            errors.append("event.json event_hash must match last trace event")

    audit_lines = [
        line.strip()
        for line in (bundle_dir / "audit.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not audit_lines:
        errors.append("audit.jsonl must contain at least one line")
    else:
        audit = json.loads(audit_lines[0])
        audit_trace = _normalize_hash(str(audit.get("trace_hash", "")))
        if audit_trace != trace_hash:
            errors.append("audit.jsonl trace_hash must match trace.trace_hash")
        audit_event = _normalize_hash(str(audit.get("event_hash", "")))
        event_hash = _normalize_hash(str(event.get("event_hash", "")))
        if audit_event != event_hash:
            errors.append("audit.jsonl event_hash must match event.json")

    if obs.get("schema_version") != "pf-core.runtime_observation.v1":
        errors.append("runtime_observation.json schema_version must be v1")

    return errors


def _verify_with_pf_core(bundle_dir: Path, schemas_dir: Path | None) -> list[str]:
    try:
        from pf_core.hash_chain import validate_trace_hashes
        from pf_core.schemas import load_registry, validate_object
    except ImportError:
        return []

    errors: list[str] = []
    if schemas_dir is None:
        return errors

    registry = load_registry(schemas_dir)
    for name in ("runtime_observation.json", "event.json", "trace.json", "certificate.json"):
        obj = _load_json(bundle_dir / name)
        try:
            validate_object(obj, registry)
        except Exception as exc:  # noqa: BLE001 - aggregate validation errors
            errors.append(f"{name}: schema validation failed: {exc}")

    trace = _load_json(bundle_dir / "trace.json")
    try:
        validate_trace_hashes(trace)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"trace hash chain recomputation failed: {exc}")

    return errors


def verify_bundle(
    bundle_dir: Path,
    *,
    pf_core_version: str | None = None,
    schemas_dir: Path | None = None,
) -> tuple[bool, list[str]]:
    errors = _verify_structure(bundle_dir)
    if pf_core_version:
        version_file = bundle_dir / "VERSION"
        if version_file.is_file():
            if version_file.read_text(encoding="utf-8").strip() != pf_core_version:
                errors.append(f"bundle VERSION mismatch (expected {pf_core_version})")

    if schemas_dir and schemas_dir.is_dir():
        errors.extend(_verify_with_pf_core(bundle_dir, schemas_dir))

    return (len(errors) == 0, errors)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify PF-Core artifact bundle")
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--pf-core-version", default=None)
    parser.add_argument("--schemas", type=Path, default=None)
    args = parser.parse_args(argv)

    ok, errors = verify_bundle(
        args.bundle_dir,
        pf_core_version=args.pf_core_version,
        schemas_dir=args.schemas,
    )
    if ok:
        print(f"verify_bundle: PASS ({args.bundle_dir})")
        return 0
    for err in errors:
        print(f"verify_bundle: FAIL — {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
