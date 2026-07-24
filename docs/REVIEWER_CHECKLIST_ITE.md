# PIP-ITE Reviewer Checklist

Use with each ITE PR (PIP-ITE-00..07).

- [ ] One principal contract stated in the ADR
- [ ] Tests cover valid + required invalid fixtures
- [ ] Fail closed: malformed/missing never returns pass
- [ ] Non-claims explicit; no causal/remediation/SDE claims
- [ ] No secrets / forbidden fields in public fixtures
- [ ] Schemas immutable: incompat → new `vN`, no silent rewrite
- [ ] Lean ITE modules have no `sorry` (`python scripts/lint_no_sorry.py`)
- [ ] Legacy `lake exe *` gates still green (`make ci`)
- [ ] Python ruff + mypy strict; Rust fmt + clippy `-D warnings`
- [ ] Assurance matrix updated honestly (no fake PASS)
