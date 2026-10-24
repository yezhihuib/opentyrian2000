# Normal observer output validation

Status at public commit `044a8d8c5cd302548f554622efb0b2628a45b85a`.
This note updates the reader-facing status, not historical validation receipts.

## Fixed and verified

The normal-game observer previously accepted draws on `game_screen` but rejected
the original game's later `VGAScreenSeg` output alias. The fix gives a valid
normal observer session its own nonzero generation, captured by the frame proof.
Output accepts only the captured game/final surfaces and their unchanged pixel
stores, formats and layouts while that session remains valid. It does not grant
new draw permissions, ordinary-demo access or additional asset families.

- The old production implementation failed the new actual-alias regression.
- The final normal-session native matrix passed 360 setups and 202,137,286
  assertions, including actual SDL software-renderer Present/readback and
  session, surface, layout and stale-cache rejection cases.
- The controlled-session fixture passed 3,109,406 assertions.
- The original-event P09 segments at events 37 and 150 retained identical
  old/new state, presentation and draw logs, plus four captures per segment.
- Default-off and mirror-disabled binaries remained byte-identical to their
  corresponding pre-fix builds.

The source change is recorded in
[`normal-observer-surface-source.json`](../tests/fixtures/accepted-later-changes-v1/normal-observer-surface-source.json).
Its exact source inverse and current authority are checked by
[`test_normal_observer_surface_binding.py`](../tests/test_normal_observer_surface_binding.py).
The native cases are in
[`enemy_observe_validation.c`](../tests/enemy_observe_validation.c).

## Still separate acceptance work

Native controlled scheduling is not a natural UI campaign playthrough.
Normal UI target-family visual acceptance, Windows/GPU validation, and complete
campaign coverage are not established by these tests. The controlled P09
original-event captures are positive assisted-gameplay evidence; earlier
P02/P04/P05 attempts ended before their target events and are not positive
target-family visual evidence. A later, separate
[test-only symmetric-survival validation](ENEMY_ASSISTED_SEGMENTS.md) reaches
these targets; it does not turn those earlier attempts into passing evidence
or establish natural UI acceptance.

The earlier [controlled probe receipt](ENEMY_CONTROLLED_PROBE_VALIDATION.json)
is intentionally unchanged. Its statement that the normal observer alias was
still unverified describes that earlier change, not this later fixed baseline.
