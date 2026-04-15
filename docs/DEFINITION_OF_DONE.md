# Definition of Done

A change is done when all criteria below are true.

- `lake build` succeeds.
- `make ci` succeeds locally or equivalently in CI.
- Affected CLI targets still run successfully.
- Security and secret-handling posture is preserved or improved.
- Documentation is updated to match implementation.
- New dependencies are pinned and justified.
- No unmanaged credential material is introduced.
