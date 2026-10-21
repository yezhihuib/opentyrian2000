# Shared green heads and trails

## Bounded identity, not a scene or front-port shortcut

The shared owner reuses the eleven existing authored resources without changing art:
bank 8 heads 214–217 and newsh6 smoke 78–84. Only canonical weapon records 71 and
1071 can establish a head role. Admission observes the actual `player_shot_create`
call, allocation, slot generation, phase, initialized state, native movement,
lifetime, animation and draw. It is not restricted to front port 7 and does not
infer identity from sprite number, level, palette resemblance or draw position.
Both complete 80-byte weapon records are checked, including when smoke outlives
its emitting head. Allocation with sharing disabled cannot later acquire a role.

Smoke additionally requires a live, same-generation native trail-emission lease
around the original `JE_setupExplosion`, exact type 12 and original coordinates,
then its own allocation, initialization, lifetime and actual-draw evidence.
Unrelated type-12 explosions do not obtain this role merely by matching a tile.
The observer does not change indexed writes, damage, coordinates, input, audio,
RNG, animation, physics or the native allocator.

## Selected compositing semantics

This is not a copy of white smoke. The selected implementation retains the
head-over-green-smoke ordering documented in `GREEN_RENDER_VALIDATION.md`:
store the head-free underlay, compose smoke there, then replay applicable heads
in original order. Do not compose a head twice over its previous result.
Unrelated foreground ownership retires the corresponding saved layer.

In blend mode, let `P=max(source RGB)` and `D=max(destination RGB)`.
The original hue-preserving value operator is `N=(P+D+1)/2`, with each source
channel changed to `(channel*N+P/2)/P` (zero when P is zero); integer divisions
truncate. Authored alpha remains coverage, not an extra half-opacity effect.
Only indexed-background brightness for green smoke is bilinearly interpolated.
A pre-draw 14×16 logical center-sample snapshot covers the 12×14 tile plus a
one-pixel halo. With denominator `2*d`, the four weighted brightness taps use
round-to-nearest `(sum+den*den/2)/(den*den)`. HD-owned or outside taps use the
current destination brightness. Existing HD destinations keep the original
operator. This neither blurs neighboring HD entities nor changes source hue or
alpha. Nonblend remains authored alpha composition.

Heads draw at the original `shotX+1, shotY`. Shadows remain on the original
indexed path, with the original conditional and `shotY+shadowYDist`; no HD green
shadow is introduced. Terrain and cloud families remain paused.

## Fail-closed family

All eleven resources, both original source banks, the complete gameplay palette
and both canonical records form one strict dependency group. Missing or corrupt
members, changed source/layout/palette, invalid birth/draw evidence, unfinished
calls, or observed transient faults revoke the affected contribution rather
than silently broadening identity or reviving a stale role. Frame-local observed
faults remain sticky until the next frame; retired slot identity still requires
a fresh genuine allocation. Ownership transfer does not erase dependency on a
green contribution. Cached output and fade paths recheck dependencies and leases.
The unchanged classic indexed path is the fallback, not a substitute HD family.

## Evidence and limits

`tests/global_green_integration.py` projects only nine exact shot observer lines,
two explosion observer lines, nine owner-transfer clears and three entity-dispatch
insertions away, then compares every other existing native source file byte for
byte with `d5b08f5d9cde1dea43819daaa8a52bc8f211e20b`. It also checks every existing
asset byte except the intentionally extended registry. The main mirror, public
mirror header and generated registry header are explicitly excluded from that
projection: they require their own tests. New shared resource blobs are tested
against existing art by the registry tests, not by the projection.

The identity sanitizer test has passed 176 cases / 4,992 assertions covering
native record/phase/lifetime witnesses, mutations, reuse, shadows, disabled births,
strict record-group checks and leaked scopes. The reconstruction test separately
checks compositing; its identity boundary is stubbed and is not a native-engine
provenance claim. See `tests/global_green_reconstruction.md` for that boundary.
Actual-engine visual/oracle acceptance is a separate gate, summarized below. No Windows/GPU, full-campaign, controller, acoustic or arbitrary
palette acceptance follows from these bounded tests. Original game media and
native captures remain outside Git.

The frozen current renderer harness passes 74 cases / 3,977,889 checks under
ASan+UBSan, including a negative control that removes observed-revocation
preflight. The older `prototype/fixtures/test-green-head-layer.py` extractor has
a confirmed pre-existing compile failure against the clean rotor base: its
historical shim lacks modern record types. It is retained as a known failed
historical test, not counted as a pass; current combined-renderer coverage is
provided by the separate production harness. The unchanged historical background
helper oracle still passes 346,480 checks. A copied allocator comment mentioning
98/198 describes white-smoke history only; actual green code and proof require
native type 12 and never grant authority to those other types.


## Bounded actual-engine acceptance (2026-10-21)

The Tyrian and MINES controlled native fixtures pass at presented 2× and 4×,
with native normal/blend settings and full/missing/corrupt/classic variants:
8 scenarios, 32 runs and 3,200 frames. Both original `player_shot_create`
records 71/1071 emit their original moving heads and type-12 trails. An independent
ordered-layer oracle checks 22,400 actual draw calls and 240,844,800 RGB subpixels
with zero mismatch. All four head IDs and seven smoke IDs occur; native shadows
remain indexed. Final capture differences stay within exact current native
coverage plus existing authored RGBA support, without support dilation.
State, RNG, indexed output, input and audio-call traces match paired runs.

A separate 60-frame adversarial native comparison transfers 1,318 green-owned
subpixels to Hitflare, observes and restores a dependency fault in that same
frame, and still requires exact classic output at Finish; the next frame
recovers. Other prior-family/HUD coexistence is not a claim of every pairwise
ownership transfer. Native packed bank8 comes from `tyrian.shp` offsets 7–8,
not external `newsh8.shp`; an initial analyzer mask-input mistake was independently
located at head214 local (0,4), corrected without production changes, and the
complete oracle was rerun. Superseded failure diagnostics remain in the checkpoint.

The final source-bound gates also pass all ten prior-family/HUD reconstruction
suites, six SHOP/UI suites, 26 registry tests and 40 packaging tests. The package
manifest is deterministic (1,006 assets); a relocated Linux dummy/software startup
runs 16 seconds with 143 Presents and leaves package contents unchanged.
These are controlled Linux proofs, not natural campaign/loadout population,
Windows/GPU, human listening or full-game acceptance. Exact native receipt and
compact source checkpoint remain outside Git; no original game banks are included.
