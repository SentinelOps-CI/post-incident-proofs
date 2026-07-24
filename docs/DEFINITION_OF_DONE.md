# Definition of Done

A change is done when all applicable criteria below are true.

## Always

- Documentation matches implementation (no overclaims vs ADR-0001 / PIP-ITE-00).
- No unmanaged credential material, `.env`, or partner plaintext is introduced.
- New dependencies are pinned and justified.
- Assurance matrix rows are honest (`PASS` only with evidence).

## When touching ITE (Python / Rust / PIP schemas / fixtures)

- `make ite` succeeds (lint, `lake build` for soundness modules, Rust fmt/clippy/test, pytest).
- Affected `post-incident` subcommands succeed on valid fixtures and fail closed on invalid ones.
- Privacy posture preserved (`pytest python/tests/test_privacy.py` when fixtures/docs change).

## When touching legacy Lean gates

- `lake build` succeeds.
- `make ci` succeeds locally or equivalently in CI.
- Affected `lake exe *` targets still run successfully.
