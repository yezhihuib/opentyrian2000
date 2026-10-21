# Shared rotor enemies: native types 5 and 11

## Bounded identity and assets

The eighth battle material owner reuses the existing eight NEWSH2 composite
poses, bases 229, 231, 233, 235, 237, 239, 241 and 243. Each authored resource is
24×28 at density 8, anchor 6,7. Their bytes are unchanged. Type 5 traverses the
poses forward and type 11 backwards. This is not a generic grant for matching
sprite numbers or a level allowlist.

Canonical full 77-byte enemy records 5 and 11 are independently pinned. The
native allocation, initialized slot generation and actual animation step are
observed without changing simulation. The bank must be the unique currently
loaded shape-table ID 1 (NEWSH2), not a stale pointer or another numeric bank.
Four native calls retain their original offsets and order: base,+1,+19,+20.
The vertical visibility guards may omit the top or bottom pair. An incomplete,
reordered or duplicated quartet cannot regain authority in the next frame.

The original indexed calls, movement, collision, reward, RNG, hit-filter timing
and animation remain unchanged. Existing enemy_filter_rgba applies the original
filter ramp to authored color brightness, retaining alpha and continuous detail;
filter indices are not confused with half-alpha blending. The full canonical
palette is conservatively pinned. Native physical-row wrapping remains classic.

## Ordered contribution and fallback

One dedicated rotor owner shares the content-addressed loader, not the role of
coins, player ships, shots or explosions. All eight resources and both source
records form one all-or-classic dependency group. Cold resource failure does
not borrow the old scene-specific rotor cache. Frame source, palette, layout,
owner transfers, final-indexed output, cache and fade are validated. Observed
invalidity stays sticky after a later owner has copied rotor RGB. Final proof
rejects the whole current HD Present if such a contribution becomes invalid.

## Verification boundaries

Focused sanitizer identity and compositor tests, an independent native matrix,
prior-family regressions and formal packaging validation accompany this slice.
The final private receipt states exact measured cases and limits. Native fixtures
use controlled original allocation and may load the original NEWSH2 bank in a
scene that does not normally load it; this proves rendering independence from
the old scene lease, not that the original campaign naturally spawns both types
in every level. No Windows/GPU, full campaign, physical display or acoustic
validation is implied. Previous finite natural type-5 evidence remains historical
and is not silently presented as new evidence for this global path.
