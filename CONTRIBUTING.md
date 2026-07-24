# Contributing

## Development prerequisites

- Python 3.11+ (primary ITE CLI and tests)
- Rust toolchain (stable) for `post-incident-kernel`
- Lean 4 toolchain via `lean-toolchain` + Lake (soundness + legacy gates)
- Optional: `pre-commit` for local hooks

## Install ITE tooling

```bash
pip install -e "./python[dev]"
cargo build --manifest-path rust/post-incident-kernel/Cargo.toml
```

## Local validation

### ITE (preferred for lineage / preservation work)

```bash
make ite
# or piecemeal:
make ite-lint
make ite-rust
make ite-python
post-incident bundle validate fixtures/release/valid_incident_release
pytest python/tests -q
```

### Legacy Lean gates (must stay green)

```bash
make ci
# equivalent: lake build + lake exe tests/security/observability/validate/benchmarks
```

### Pre-commit

```bash
pre-commit run --all-files
```

## Contribution standards

- Keep changes focused and reviewable; one principal contract per ITE ADR when semantics change.
- Prefer fail-closed diagnostics (`error` / `indeterminate`, never false `pass`).
- Update docs and `docs/ASSURANCE_MATRIX.md` when behavior, APIs, or workflows change.
- Do not add secrets, credentials, partner plaintext, or key material to tracked files.
- Do not overclaim: no causation, remediation, SDE operation, or production crypto guarantees beyond ADR-0001 / PIP-ITE-00.
- Pin new dependencies and justify them in the PR description.
- Lean ITE modules must remain `sorry`-free (`python scripts/lint_no_sorry.py`).

## Pull request checklist

- Scope and intent clearly described; link the relevant PIP-ITE ADR when applicable.
- Valid + required invalid fixtures covered.
- `make ite` (and `make ci` if Lean/legacy touched) green.
- Security / privacy impact considered; public fixtures stay synthetic digests only.
- Documentation and examples match final behavior.

Reviewer aid: `docs/REVIEWER_CHECKLIST_ITE.md`.
