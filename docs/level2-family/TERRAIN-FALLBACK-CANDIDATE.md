# Independent terrain fallback candidate

`BUILDING313_TERRAIN_FALLBACK_ENABLE=1` is a separate default-off experimental
family-canvas control. It does not enable any family by itself, change the frozen
preview, or weaken building event, group-lifetime, source or phase guards.
The normal full-scene family candidate is still tried first. If it cannot be
presented, this candidate may present current native actors over untouched HD
terrain. HUD-only fallback remains the final option.

## Proof and ownership

The renderer starts the transaction before the ground pass. Only a fully
validated original ground pass can supply HD samples. Ground, cliff, corner366
and static340 use their existing source, map and asset pins. The optional
red-vent extension is deliberately excluded from this initial candidate.
The capture has its own RGB storage and logical-cell mask. Every subsequent
native store retires that cell, including same-value writes, shadows and blends.
No actor bounds, previous-frame image, saved-under rectangle or rejected canvas
is replayed. A partially occluded cell becomes entirely native.

The existing native writer ledger is consumed exactly once: when enabled, the
independent callback runs before the old actor-failure return and the old path
skips its duplicate consumption. It continues through actor rejection, as do
validated rectangle callbacks. Unknown effects, incomplete/unpaired writes,
structural failures and terrain failures reject the candidate. The one legacy
actor-canvas rejection for a recognized `MIRROR_BLEND` over unsupported HD
ownership rejects only that scene: its native callback has already consumed the
writer ledger and retired the exact terrain cell. It does not grant fallback
admission. Unknown effects, unsupported brightness and invalid shadow results
still invalidate both candidates. An actor source
failure is not itself permission: independent surface, palette, map, source,
asset, complete indexed-write and final crop proofs must all still hold.

Finish builds a separate candidate from the current native output, then overlays
only surviving terrain cells. Dedicated source/output storage and formats are
bound. Present rechecks those identities, all source/resource witnesses, final
indexed output, texture/renderer geometry and modes after locking, before any
texture writes. It never regrants a failed transaction. A successful old-scene
Present consumes the unused candidate; this Present is also single-use. Resets
retire candidates without counting normal frame transitions as proof failures.

Static HUD composition uses the shared target-surface API and cannot paint the
playfield. The public read-only `render_mirror_terrain_fallback_status()` exposes
separate capture/preparation/presentation counters and a `presenting` flag active
during actual SDL Present. Old canvas admission counters are not repurposed.

## Checks and limits

Run `python -m unittest discover -s tests -p test_b313_terrain_fallback.py` for the
real-include fixture linked to the real native writer and SDL software renderer.
It covers exact pixel composition, retirement, invalid writes and post-lock
mutation with address/undefined-behavior sanitizers. It does not replace actual
original-data playback, native-state/RNG parity, or final-window pixel checks.

This candidate allocates two 2560×1600 ARGB surfaces (about 32 MiB) and rechecks
terrain payload hashes. Runtime cost and visual coverage must be measured in
bounded playback. It preserves untouched terrain, not complete actor HD or
full-level visual continuity. Default-off behavior remains the old path.
