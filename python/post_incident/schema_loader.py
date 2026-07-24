"""JSON Schema loading for PIP and vendored PCS schemas."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

REPO_ROOT = Path(__file__).resolve().parents[2]
PIP_SCHEMA_DIR = REPO_ROOT / "schemas" / "pip" / "v1"
PCS_SCHEMA_DIR = REPO_ROOT / "schemas" / "pcs"


def _load_json(path: Path) -> dict[str, Any]:
    # utf-8-sig tolerates BOM from some Windows writers without rejecting schemas.
    return json.loads(path.read_text(encoding="utf-8-sig"))


@lru_cache(maxsize=1)
def _registry() -> Registry:
    resources: list[tuple[str, Resource[Any]]] = []
    for directory in (PIP_SCHEMA_DIR, PCS_SCHEMA_DIR):
        for path in directory.glob("*.json"):
            if path.name == "SCHEMA_MIRROR.json":
                continue
            doc = _load_json(path)
            uri = doc.get("$id") or path.as_uri()
            resources.append((uri, Resource.from_contents(doc, DRAFT202012)))
            # Also register by basename for relative $ref resolution
            resources.append(
                (path.name, Resource.from_contents(doc, DRAFT202012))
            )
    registry: Registry = Registry()
    for uri, resource in resources:
        registry = registry.with_resource(uri, resource)
    return registry


@lru_cache(maxsize=32)
def validator_for(schema_filename: str) -> Draft202012Validator:
    path = PIP_SCHEMA_DIR / schema_filename
    if not path.is_file():
        path = PCS_SCHEMA_DIR / schema_filename
    if not path.is_file():
        raise FileNotFoundError(f"schema not found: {schema_filename}")
    schema = _load_json(path)
    return Draft202012Validator(schema, registry=_registry())


def validate_instance(
    instance: dict[str, Any], schema_filename: str
) -> list[str]:
    """Return list of validation error messages (empty => ok)."""
    try:
        v = validator_for(schema_filename)
    except FileNotFoundError as exc:
        return [str(exc)]
    errors: list[str] = []
    for err in sorted(v.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        loc = "/" + "/".join(str(p) for p in err.absolute_path)
        errors.append(f"{loc}: {err.message}")
    return errors


def load_json_file(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")
    return data
