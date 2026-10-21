# Global white-smoke source identity

White smoke now uses an independent global semantic owner, not a level whitelist.
The seven approved 8× HDA resources are byte-for-byte copies of the accepted
newsh6 frames 135–141, with logical size 12×14 and anchor (0,0). No artwork was
redrawn or resampled. The previous five families and their resource records are
unchanged.

## Admission and fallback

The observer sees the actual free-slot choice in `JE_setupExplosion`, before
native type 98/198 normalizes to type 6. It binds allocation generation, original
type, initialized fields, and every subsequent TTL7→1 draw. Only ordinary,
non-fixed, non-follow-player smoke is admitted. Type 6 retains its native x+2,
y+12 offset; aliases retain their original coordinates. Background drift and
per-instance delta Y use the same two signed-16-bit narrowing steps as the game.

The entire decoded source family, used palette colors, complete content-addressed
resource payloads, original write order, and output surface leases must match.
A failed witness does not alter simulation or indexed pixels. Generic sprite
matching cannot grant the global role, and missing or corrupt resources fall
back to original rendering. Resource absence is cached until explicit asset-root reconfiguration,
so incomplete resources cannot silently reappear mid-session.

Every contributing family retains proof even when later drawing transfers all
its ownership bits to another family or HUD. An observed source, mode, palette,
layout, or role invalidation remains sticky for that Present; restoring the input
before Finish cannot revive its earlier pixels. Final mapping, cached output,
and integer palette fades are independently checked.

## Repeatable verification

- `tests/global_smoke_reconstruction.py` checks extracted production helpers with
  an independent decoder and compositor, using ASan/UBSan. It is an isolated SDL
  structure shim, not a game-engine run. Its `--negative-control` removes only the
  sticky-fault preflight from a temporary copy and requires the exact assertion
  to fail.
- `tests/global_smoke_integration.py` reverses the observer-only additions to the
  native allocator and draw dispatcher and verifies the other gameplay source
  files against the preceding accepted commit.
- `tests/test_global_smoke_registry.py` verifies the seven exact reused resources,
  previous family preservation and deterministic generated C pins.
- Existing five-family, shared-HUD and SHOP proof/composer tests are retained;
  their isolated shims explicitly disable unrelated families.

Original game data are not included in source, test receipts or runtime packages.
Linux software/dummy SDL tests do not establish Windows, GPU, audio listening,
physical frame rate or whole-campaign acceptance. Terrain145 remains outside this
change.

## Bounded native acceptance

Eight controlled native scenarios cover TYRIAN and MINES (physical 7, outside
legacy physical 9/15 and asteroid1 eligibility), both real 2×/4× display sizes,
normal/Pulse and transparent/Vulcan loadouts. Each compares full, original
reference, missing-frame137 and corrupt-frame137 variants over 160 frames.
All seven smoke phases and allocator types 6/98/198, including delta Y −2,
are exercised. Original INDEX8, state, RNG, input and audio-call traces match;
independent RGBA reconstruction reports zero pixel mismatches.

Separate short fixtures measure actual overlaps with each of the five existing
global battle families. A native smoke-to-Hitflare contribution-transfer fixture
observes and restores a temporary missing-resource flag before Finish: the
faulted Present remains completely classic, while the healthy control differs
and the next frame recovers. These are controlled allocator and rendering tests,
not a claim that every natural weapon trail or campaign encounter was played.

The final package contains 942 assets plus the executable. Its exact source
inventory is bound independently of a future Git commit; the precommit receipt
intentionally records a null commit rather than an invented one. Source and
build-input hashes, all package/ZIP bytes, deterministic rebuild, and a relocated
16-second startup are checked separately from the native rendering matrix.

HUD coexistence and a real cash-HUD footprint intersection are exercised, but the
bounded native probe does not establish smoke-to-HUD RGB ownership transfer.
That specific native transfer is not claimed. Contribution persistence is covered
by isolated fault-restoration tests and the measured native Hitflare transfer.
