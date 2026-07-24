# PIP-ITE-06: Morph Replay Fixtures

## Status

Accepted

## Decision

- Local PIP schema `MorphReplayReport` references Morph field names without vendoring Morph runtime.
- `post-incident replay-check` binds report digests to lineage nodes.
- Default CI uses recorded fixtures only; live Morph Cloud is opt-in and out of default CI.

## Non-claims

Does not operate Morph Cloud or assert live replay execution in CI.

## Rollback

Remove morph schema/fixtures/`replay-check`.
