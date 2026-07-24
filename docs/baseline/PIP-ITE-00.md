# PIP-ITE-00 Baseline Record

## Freeze point

| Field | Value |
| --- | --- |
| Base commit | `3cdfdf09c20f08ad5221d29607b5a9726295ad10` |
| Branch at freeze | `main` |
| Lean toolchain | `leanprover/lean4:v4.7.0` (`lean-toolchain`) |
| Recorded on | 2026-07-24 |
| Host | Windows 10 (local developer capture) |

## Baseline commands and results

Commands below are the **legacy** gates. They remain frozen behavior for ITE work; new lineage/preservation evidence is produced by `post-incident`, not by these executables.

| Command | Exit code | Notes |
| --- | --- | --- |
| `lake build` | `0` | Library build succeeded (~8s cold) |
| `lake exe tests` | `0` | Printed `tests: PASS` |
| `make ci` | `0` | `build` → `test` → `security` → `observability` → `validate` → `benchmark` |

### Capture method

```bash
python scripts/capture_baseline.py
```

Optional local raw streams (e.g. `_raw_capture.txt`, `_raw_make_ci.txt`) may be produced by the capture script for developer debugging. They are **not** tracked and are not normative; this table is the authoritative baseline record.

## What the baseline includes

- Lean executable gates: logging, rate, version, bundle size path, security-ops, observability, validate, tests, benchmarks.
- Claim discipline docs: `docs/adr/ADR-0001-crypto-and-assurance-boundary.md`, `docs/ASSURANCE_MATRIX.md`.
- Stub crypto in `PostIncidentProofs.Utils.Crypto` (not a SHA-256 oracle). Real digests for ITE live in the Rust kernel and Python helpers.

## What the baseline does **not** include

- JSON Schema domain models for incident lineage
- PCS integrity envelope validation
- Transformation DAG / preservation / redaction / Morph replay checks
- `post-incident` CLI

## Repair note

No baseline repairs were required. All recorded commands exited `0` at commit `3cdfdf09c20f08ad5221d29607b5a9726295ad10`.

## Rollback

Revert this document and `docs/adr/PIP-ITE-00-claim-boundary.md` plus PCS pin scaffold only. No runtime behavior depends on PIP-ITE-00.
