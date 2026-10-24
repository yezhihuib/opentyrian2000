# Assisted original-event enemy projectile validation

This is **test-only symmetric-survival validation**, not natural gameplay or an
unmodified production-binary deep-level test. The source baseline is public
`044a8d8c5cd302548f554622efb0b2628a45b85a`.

## Explicit intervention

An external fixture copied the public source and added exactly one statement
after the existing `JE_eventSystem()` event loop in `tyrian2.c`:

```c
if(asset_debug_enabled&&getenv("OT_LATE_TERRAIN_INVULNERABLE")&&player[0].is_alive&&player[0].invulnerable_ticks<2)player[0].invulnerable_ticks=2;
```

Only `tyrian2.o` changed among 86 compiled objects. This statement is **not**
installed in the production repository or shipped binary. Setting the variable
on an ordinary production binary does not enable this fixture. Its guard checks
presence, not a boolean value; the runner clears inherited `OT_*` variables and
sets this one to `1` only for assisted lanes.

Off/on lanes use the same fixture executable, original data, assets, seed,
input and environment. Only the existing explicit reuse-session flag and output
locations differ. No actor, projectile, event, seed checkpoint, tick limit,
source-resource pin or renderer eligibility guard is changed. An initial
280-row dormant-fixture comparison, with the variable absent, matches the
production binary's state/RNG/INDEX8 and original draw/event/collision streams.

The intervention changes damage, collision push-back, player flashing and
downstream causality compared with natural play. Projectile contact can still
retire shots and produce hit effects. Equality between the assisted lanes is
not evidence of equality to an uninterrupted natural playthrough.

## Positive paired results

All state rows, including RNG and original INDEX8 hashes, match within each
pair. Original draw and event streams match after excluding only the HD
`mirrored` diagnostic and elapsed wall-clock time. Present leaves RNG unchanged.

| Family | Original target | Input | State rows | Accepted role146 draws | HD + Present ticks |
|---|---|---|---:|---:|---:|
| P02 Sonic 105/106/124/125 | E1 physical2, event721, reached tick5528 | Existing v1, front36/rear37 power11 | 5649 | 160 | 43 |
| P04 guided 20/21 | E1 physical5, event295, reached tick2457 | Existing enemy-hit, default loadout | 2698 | 575 | 151 |
| P05 green 214/215/216 | E2 physical2, event781, reached tick4911 | Existing enemy-hit, default loadout | 5032 | 216 | 84 |

P02 uses the existing strong-loadout input to clear the original stop-and-kill
gate; it does not skip that gate. P04 uses 240 existing step commands after its
target rather than the initial 120-step observation window. The normal 6000-tick
limit is unchanged. Zero-acceptance and earlier unsuccessful runs are retained
as diagnostic evidence, not relabeled as successes.

Final paired captures contain four actual 640×400 SDL readbacks per group:
P02 ticks5546–5549, P04 ticks2600–2603 and P05 ticks4929–4932. Captured runs
reproduce the exploratory state/original streams; every selected HD frame has
same-tick role146 acceptance, ordered HD output, zero coverage mismatch and a
real Present. The P02 target is partially clipped by the upper viewport edge:
these images prove that boundary rendering, not complete silhouette readability
or full-lifetime visual quality. See the
[compact validation record](ENEMY_ASSISTED_SEGMENTS_VALIDATION.json) for paired
checks, binary hashes and all off/on capture hashes.

## Asset completeness matters

P02 and P04 intentionally share the atomic six-member family
`105/106/124/125/20/21`. The initial 647-file test root lacked the four Sonic
members. Both groups therefore correctly fell back even when original shots
were drawn. A new independent 651-file root retained every original file and
added only the four approved public Sonic HDA blobs, verified against their
original headers and payload pins. No eligibility check was relaxed.

That test did **not** add those four resources to its public044 formal runtime
manifest: its 1025 destinations and the global registry's 120 entries stayed
unchanged. The tested formal root alone therefore lacked the P02/P04 family.
A subsequent [Sonic runtime closure](current-sonic-runtime-package.md) adds the
quartet to the current formal package; it does not rewrite this test's baseline
or frozen validation JSON. The complete test root and current-preview export
are separate distributions; their counts are not formal package counts.

## Scope

These results establish original-event target rendering and off/on neutrality
under the disclosed intervention on Linux SDL software output. They do not
certify natural survival, ordinary player damage behavior, full-campaign
coverage, Windows, physical GPUs, or future artwork edits. Historical receipts
and source authority remain frozen; this note records the later bounded test.
