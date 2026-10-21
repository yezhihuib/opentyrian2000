# Global ordinary small-explosion source identity

The ordinary type 1 small explosion uses a separate global semantic owner,
not a level whitelist. Twelve accepted 8× HDA resources are reused byte for
byte: newsh6 122–133, logical size 12×14, anchor (0,0). No artwork was redrawn,
resampled, or newly approved by this change. Earlier six families retain their
resource records and semantics.

## Bounded role

The observer witnesses the native free-slot selection in `JE_setupExplosion`
and the initialized type 1, sprite 120, TTL 12 record. It admits only non-fixed,
non-follow-player instances. There is no position offset. Every subsequent
native draw must match allocation generation, phase 122–133, TTL 12→1,
coordinates, background drift and delta Y with the game's signed-16-bit
narrowing. Other explosions, aliases, fixed pickup effects and large quadrant
explosions do not gain this role merely by using a matching sprite.

The complete decoded family, exact used palette colors, content-addressed HDA
payloads, surface leases and original indexed-write transaction must match.
Resource failure is cached until an explicit root reset. A failed witness or
missing/corrupt resource falls back to classic rendering; no simulation fields,
RNG, input or original indexed writes are changed.

Ordered ownership transfer preserves the original drawing order. Contribution
proof outlives transferred owner bits. Observed invalidity is sticky until the
next frame: restoring a mode, source or palette before Finish cannot revive
already-invalid RGB. Final mapping, cached output and integer fades are also
validated. Sharing art never shares admission authority with another role.

## Reproducible checks

- `tests/test_global_small_explosion_registry.py`: twelve exact approved assets,
  prior registry preservation, source pins and deterministic header generation.
- `tests/global_small_explosion_reconstruction.py`: extracted production helpers,
  real allocator function and independent decoder/compositor in a bounded SDL
  shim, with ASan/UBSan and fault-removal negative control.
- `tests/global_small_explosion_integration.py`: reverse projection of observer
  additions against the preceding accepted white-smoke commit.
- Existing six battle-family, shared-HUD and SHOP regression tests remain active.
  Isolated test shims disable unrelated owners explicitly, not in production.

Native scenario results and formal packaging acceptance are separate evidence,
not implied by the isolated suites. Original commercial game data are excluded
from source and runtime packages. Linux software/dummy SDL verification does
not establish Windows/GPU behavior, whole-campaign coverage or audio listening.
Paused terrain145, unresolved cloud adjacency, green effects, pickups and enemy
families remain outside this change.

## Bounded native and package acceptance

Eight native scenarios cover TYRIAN (physical 9) and MINES (physical 7, outside
legacy eligibility), normal/Pulse and blend/Vulcan loadouts at actual 2×/4×.
Each compares full, original reference, missing and corrupt variants for 160
frames: 32 runs and 5,120 frames. Controlled calls to the real type 1 allocator
exercise all twelve phases and delta Y 0, 1, −1 and −2. Original INDEX8, state,
RNG, input and audio-call traces match. Including two additional 70-frame
six-family overlap fixtures, independent RGBA reconstruction checks 6,343,680
pixels with zero mismatch and no changes outside accepted support.

A separate native mutation transfers 1,047 subpixels into Hitflare, observes a
temporary resource-failure flag, then restores it before Finish. That Present
remains completely classic; the healthy control differs and the next frame
recovers. All six existing battle families have measured overlap. HUD coexists,
but native explosion-to-HUD RGB ownership transfer is not established.
These are controlled native allocator/render tests, not natural enemy-death or
whole-campaign coverage.

The final package has 954 assets plus its executable, with 958 ZIP entries.
All payload/ZIP bytes, 31 packaging checks, deterministic manifest rebuilding,
exact source/build-input binding, clean Linux build and a relocated 16-second
startup pass. The precommit source binding deliberately has a null commit;
the external checkpoint identifies the final immutable local commit instead.
