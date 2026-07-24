#!/usr/bin/env python3
"""Fail if required PIP-ITE ADRs / baseline scaffolds are missing for landed artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Always required once ITE scaffolding begins.
REQUIRED_ALWAYS = [
    ROOT / "docs" / "adr" / "PIP-ITE-00-claim-boundary.md",
    ROOT / "docs" / "adr" / "PIP-ITE-00-polyglot-ownership.md",
    ROOT / "docs" / "baseline" / "PIP-ITE-00.md",
    ROOT / "schemas" / "pcs" / "SCHEMA_MIRROR.json",
]

# If a feature artifact exists, its ADR must exist (progressive gate for stacked PRs).
FEATURE_GATES: list[tuple[Path, Path]] = [
    (
        ROOT / "schemas" / "pip" / "v1" / "IncidentSourceRecord.schema.json",
        ROOT / "docs" / "adr" / "PIP-ITE-01-incident-source.md",
    ),
    (
        ROOT / "schemas" / "pip" / "v1" / "LineageBundle.schema.json",
        ROOT / "docs" / "adr" / "PIP-ITE-02-transformation-lineage.md",
    ),
    (
        ROOT / "schemas" / "pip" / "v1" / "PreservationClaim.schema.json",
        ROOT / "docs" / "adr" / "PIP-ITE-03-preservation-claims.md",
    ),
    (
        ROOT / "src" / "PostIncidentProofs" / "Preservation" / "Deciders.lean",
        ROOT / "docs" / "adr" / "PIP-ITE-04-lean-soundness.md",
    ),
    (
        ROOT / "schemas" / "pip" / "v1" / "RedactionCommitment.schema.json",
        ROOT / "docs" / "adr" / "PIP-ITE-05-redaction-commitments.md",
    ),
    (
        ROOT / "schemas" / "pip" / "v1" / "MorphReplayReport.schema.json",
        ROOT / "docs" / "adr" / "PIP-ITE-06-morph-replay.md",
    ),
    (
        ROOT / "schemas" / "pip" / "v1" / "IncidentRelease.schema.json",
        ROOT / "docs" / "adr" / "PIP-ITE-07-incident-release.md",
    ),
]


def main() -> int:
    missing: list[str] = []
    for path in REQUIRED_ALWAYS:
        if not path.is_file():
            missing.append(str(path.relative_to(ROOT)))
    for artifact, adr in FEATURE_GATES:
        if artifact.is_file() and not adr.is_file():
            missing.append(str(adr.relative_to(ROOT)))
    if missing:
        print({"status": "error", "code": "missing_adr_scaffold", "missing": missing})
        return 1
    print({"status": "ok", "code": "adr_scaffold_present"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
