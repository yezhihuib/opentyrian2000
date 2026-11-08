# Linked props287/288: independent default-off candidate

Use `--hd --linked-props` in `scripts/launch_level2_family.py` to request this
candidate. The launcher prepares a plan unless its separate launch option is
chosen. This change does not run the game, broaden graphics permissions, change
canonical `src`, or modify the 52-file baseline manifest.

## Exact scope

Only episode1, physical level2 / ASTEROID2, the original731-event stream, the
pinned NEWSHD source bank and normal single-player state are admitted. The six
one-based case6 origins are:

| Event | Time | Record | X | Link | Y adjustment |
|---|---|---|---|---|---|
|183|1392|287|210|23|-28|
|184|1392|288|90|22|0|
|185|1392|287|90|22|-28|
|186|1392|288|210|23|0|
|286|2456|288|162|26|0|
|287|2456|287|162|26|-28|

Each native allocation is witnessed independently. Failure consumes only that
origin; no paired allocation or partner-survival requirement is imposed. The
single explicit flag enables these six entries, not a global late-reuse gate.
Inherited environment toggles are stripped by the launcher.

Three existing public NEWSHD images245/281/283 are SHA256 checked by the launcher
and content checked at renderer boundaries. Normal287 stays at cycle1; normal288
retains its native20-cycle sequence. Native cells number672/670/670 respectively.
HD alpha blends only inside exact native-written cells, never filling the two
native holes in281/283 or adding coverage beyond the original sprite.

## Gameplay and safety contract

All hooks observe existing allocation, initialization, animation and native
retirement. They do not change enemy health, hit damage, movement, linking,
allocation order or random numbers. Hit receipts begin after native damage
normalization and end after the complete armor/link branch. Direct death,
linked death, damage transformation, script clear/replacement, slot reuse,
bank changes and offscreen retirement invalidate the relevant render witness.
Damage graphics are not added by this candidate.

Fork284, turret273, linked338 and linked props retire their sparse owners before
any per-family native-writer early return. Shadows keep sparse ownership; later
normal/blended native writers retire it. Per-pixel checks use cheap configuration
and identity gates; full asset/source hashing stays at tile/output boundaries.
Any unsupported state or broken callback contract fails closed.

## Validation status

`tests/test_linked_props287288.py` provides isolated launcher, origin-consumption,
animation/hit-receipt, native-cell/alpha/retirement and hook-placement tests.
These are observer tests with stubs, not a simulation of the complete game.
At this checkpoint the new tests and full build are pending consolidated
validation. Actual gameplay, visible linked destruction, scene overlap and
performance qualification remain untested. No game was launched.
