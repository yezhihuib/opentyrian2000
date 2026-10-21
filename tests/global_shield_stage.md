# Shield22 reconstruction batch

This batch adds the independently authenticated player shield-hit family to the
already restored Talon13 renderer. It reuses the exact 22 authored assets and
five authenticated empty phases already present in `global-assets-v1`; no art or
original game-data bytes are changed. Pulse5, Hitflare7 and front Vulcan2 remain
unimplemented globally. The published frontend launchers and packaging manifest
are intentionally unchanged. This development path still requires an explicit
`--global-assets=<global-assets-v1 directory>` option.

## Native boundary

Only the nine calls in the actual `JE_playerDamage` shield branch open a bounded
birth envelope. The original `JE_setupExplosion` allocator invalidates the slot
before its original initialization and consumes a fresh, free-slot, same-tick
allocation token afterward. Draws prove the recorded generation, phase sequence,
TTL, source bank/content, role flags, current position and normal/blend operator.
The original indexed draw, damage, animation advancement and sound behavior
remain unchanged. No episode, level, map or generic sprite index grants authority.

Empty phases retain their semantic identities. In particular 267, 268 and 269
share the same original tile fingerprint but select different authored resources;
268 is transparent and must not revive the original opaque graphic. A rejected
migrated identity cannot re-enter the old generic HD cache.

## Ownership and invalidation

Shield has independent source/canvas/output leases, pixel ownership, resources,
transaction observations, final composition, cache and fade proof. Overlaps with
Talon transfer exclusive output ownership while recording source dependencies.
A changed or faulted underlay owner invalidates dependent composites. A Shield
contributor lease survives ownership transfer into antialiased HUD glyphs even
when no final Shield-owned pixel remains; failed contributor proof declines the
entire current Present before final composition, and is retained for cache/fade. Normal
same-index writes retire owned RGB; supported later shadows preserve ordered
composition. Frame resets clear proof and cached pixels without changing engine
state. Cache invalidation deliberately falls back to the classic current Present;
it does not promise to preserve another family's HD within that same Present.

## Validation boundaries

`global_shield_reconstruction.py` exercises extracted current production with
ASan/UBSan, including the real allocation helper. See its companion documentation
for all positive/negative coverage and the explicit SDL/HUD stub limitations.
The separate native evidence uses a disclosed deterministic call to the actual
`JE_playerDamage` function at ticks 110 and 130 in every paired configuration. It
is not a claim of a naturally occurring enemy collision. Original engine drawing,
allocation, state and audio queues run afterward. State/audio parity is measured,
not a claim of subjective listening, Windows/GPU acceptance or full playthrough.

## Accepted-candidate results (2026-10-21)

- Full native build succeeds. Focused ASan/UBSan: 354 cases and 15,046,787
  assertions; separately reproduced by an independent reviewer against the frozen
  source and harness. Feature-disabled header compilation/execution also passes.
- Exact-source regression reruns with ASan/UBSan also pass: Talon13 has 365
  cases / 421,050,144 assertions; shared HUD has 166,155,902 checks.
- Native paired matrix: seven scenarios, three variants each, 160 frames per run.
  Includes normal/blended 1P and actual-menu 2P, Hard15 night and overlapping HUD.
  Each Shield-enabled run has 54 admitted draws (all 27 identities twice), ten
  authenticated empty-phase draws, exactly six retained hit frames and no faults.
- Matched original indexed canvases, palette, RNG, player/entity state, event and
  Present counters, sound queue and damage results remain equal. Differences
  attributable to Shield occur only on ticks 110–112 and 130–132, disappear on
  retirement, and stay within declared support in sampled native captures.

Native instrumentation and original read-only game files are not shipped with
this source batch. These are bounded test results, not exhaustive gameplay proof.

A native post-glyph source-mutation regression exposed and fixed a 12-pixel
antialiased HUD underlay residue before this batch was committed. The fixed
mutation frame is exactly classic RGB; contributor tests additionally simulate
zero final owner bits through pre-Finish, cache and fade mutation/recovery paths.
