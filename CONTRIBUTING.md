# Contributing

## Development Prerequisites

- Lean 4 toolchain via `lean-toolchain`
- Lake build tool
- Python 3.11+ for policy and docs tooling

## Local Validation Workflow

Before opening a pull request, run:

```bash
make ci
pre-commit run --all-files
```

## Contribution Standards

- Keep changes focused and reviewable.
- Keep `lake build` and all executable checks passing.
- Update docs when behavior, APIs, or workflows change.
- Do not add secrets, credentials, or key material to tracked files.
- Pin new dependencies and justify them in the PR description.

## Pull Request Checklist

- Scope and intent are clearly described.
- Tests/validation updated where applicable.
- Security and operational impact considered.
- CI workflows pass without manual fixes.
- Documentation and examples reflect the final behavior.
