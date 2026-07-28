#!/usr/bin/env bash
# Unit tests for PF-Core bundle verification (Phase 7 PR-1).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PF_CORE_ROOT="${PF_CORE_ROOT:-$ROOT/../provability-fabric-core}"
OUT="${TMPDIR:-/tmp}/pip-pf-core-bundle-test-$$"
OBS="$PF_CORE_ROOT/pf-core/examples/valid/mcp_sidecar_observation.json"
VERSION="$(cat "$PF_CORE_ROOT/pf-core/VERSION" 2>/dev/null || echo "0.6.0")"

cleanup() { rm -rf "$OUT"; }
trap cleanup EXIT

if [ ! -f "$OBS" ]; then
  echo "SKIP: provability-fabric-core not found at $PF_CORE_ROOT"
  exit 0
fi

PYTHON="${PYTHON:-python3}"
export PYTHONPATH="$PF_CORE_ROOT/pf-core/validator"
$PYTHON -m pip install -q -e "$PF_CORE_ROOT/pf-core/validator" jsonschema referencing 2>/dev/null || true

$PYTHON -m pf_core.cli core emit-artifacts \
  --schemas "$PF_CORE_ROOT/pf-core/schemas" \
  --file "$OBS" \
  --out-dir "$OUT"

$PYTHON "$ROOT/scripts/verify_pf_core_bundle.py" \
  --bundle-dir "$OUT" \
  --pf-core-version "$VERSION" \
  --schemas "$PF_CORE_ROOT/pf-core/schemas"

lake exe verify_bundle -- --bundle-dir "$OUT" --pf-core-version "$VERSION"

# Tampered trace_hash must fail
cp -r "$OUT" "${OUT}-bad"
$PYTHON - <<'PY' "${OUT}-bad/trace.json"
import json, sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
data["trace_hash"] = "f" * 64
json.dump(data, open(path, "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
if $PYTHON "$ROOT/scripts/verify_pf_core_bundle.py" --bundle-dir "${OUT}-bad" --pf-core-version "$VERSION"; then
  echo "expected tampered bundle to fail"
  exit 1
fi

# unsafe certificate must fail
cp -r "$OUT" "${OUT}-unsafe"
$PYTHON - <<'PY' "${OUT}-unsafe/certificate.json"
import json, sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
data["safe"] = False
json.dump(data, open(path, "w", encoding="utf-8"), indent=2, sort_keys=True)
PY
if $PYTHON "$ROOT/scripts/verify_pf_core_bundle.py" --bundle-dir "${OUT}-unsafe" --pf-core-version "$VERSION"; then
  echo "expected unsafe certificate to fail"
  exit 1
fi

echo "OK: PF-Core bundle verification tests passed"
