# Bounded tank shells146/147 candidate

Only the existing `--hd --public-candidates` preset selects this candidate.
Plain `--hd` remains off, inherited `ENEMY_SHOT_FAMILY_` controls are cleared,
and no new CLI option is introduced. The launcher checks the exact full-file
size and SHA-256 of existing `current-compat/tank-shell` images146/147.
The Windows pinned resource list includes both images.

Birth admission is restricted to the already witnessed tank194 encounters,
not merely an enemy using the same weapon. Once born, the projectile has its
own allocation generation and native lifecycle; emitter death or reuse is not
a reason to manufacture or revoke that projectile's identity. The candidate
does not change native weapon selection, movement, damage, collisions or RNG.

This is a presentation candidate, not evidence of a successful Windows game
or final visible-image acceptance. Source/lifecycle and ownership checks must
remain authoritative. No orb, projectile145/91/304 or legacy global path is
enabled by this material selection.

## Preserved alpha and sparse native alignment

Each shell has 39 original indexed stores. The 8x material is sampled at its
unchanged 12x14 origin with no translation, scaling change or alpha threshold.
Native-written cells own all64 output subpixels, including authored alpha0;
native holes do not acquire native ownership. After all39 callbacks succeed,
only authored nonzero-alpha subpixels outside the native mask are composited:
80 for146 and11 for147. These extras have separate subpixel ownership. All
normal/blend writers retire them before early returns; shadows preserve the
tags and darken only surviving extra subpixels. No old background is restored.

The birth gate requires the existing tank194 scope, live generation/shape and
captured token/event. After birth the projectile's own epoch/generation and
weapon/source/state sequence control survival. Parent death, slot reuse or the
tank's event259 cutoff do not alone retire an already flying shell. This does
not grant new display admission or extend tank birth coverage.

Finite extracted tests cover actual sparse writers, both source alpha payloads,
all91 extras, ownership and captured-birth survival; source/scope/constructor
readiness are modeled. Central dispatch tests cover121 ordered family pairs
and extra shadow/overwrite behavior. No original RLE stream or real game was
executed by these tests, and no final visible-image acceptance is claimed.

## Native lifecycle regression

`tests/test_tank_shell_lifecycle.py` now extracts the actual native shot-pool
allocation/initialization and full shot-update blocks from the experimental
`tyrian2.c`, together with the actual mirror lifecycle functions and native
record declarations. It does not replace those blocks with a movement model.

The finite harness checks both shells through emitter death, actor-slot reuse,
and the real event259 cutoff handler. Existing shells keep moving after those
changes while new births reject. It also covers all 60 shot slots, pool
exhaustion/reset, replacement generations, same-frame and next-frame first
motion, missed/duplicate steps, stale state and draw-lease invalidation. Native
expiry, exact boundary limits, strict collision edges, invulnerability and
collision-before-lethal-damage ordering are exercised. Retirement receipts must
match the entire final native state. Ten enabled/disabled pairs compare native
shot/availability/player state and draw, damage and RNG-call counts.

Run the bounded checks without starting a game:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_tank_shell_lifecycle.py -v
```

Inputs remain synthetic: weapon records, tank birth receipts, players, frame
numbers and the event-prefix state are prepared by the fixture. Source-hash,
body-shape and outer level-admission gates are stubbed. The cutoff check does
not traverse events1–258. Renderer completion, audio, RNG and damage effects are
stubbed; no original-data replay, full enemy constructor, native RLE, clipping,
HD presentation, Windows build or actual game acceptance is established.

The cloud regression pass ran 48 focused family/lifecycle/package tests and
the 121-pair central-writer check. Four temporary source mutations (parent
coupling, cutoff coupling, missing slot-generation advance, and off-by-one
expiry) were each rejected by the new harness. ASan/UBSan passed with leak
checking disabled because LeakSanitizer cannot run under the executor's ptrace
wrapper. Two pre-existing fork/turret source assertions were updated to allow
the additional negative ownership gates before terrain retirement, preserving
their required older gates. No runtime, artwork, launcher or gameplay code
changed. The 339-file canonical production binding and runtime-source metadata
checks passed. A full SDL build was not rerun in this cloud pass because its
development dependencies were absent.
