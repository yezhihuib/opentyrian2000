# Normal-data Protron three-head family

Current addition (2026-10-14): the separate [three-mask shadow route](player-protron-shadow-three-v1/README.md) preserves these head resources and original indexed writes, with full-strength interiors and antialiased contour edges. Six fresh P1/P6/P11 baseline/candidate runs pass bounded native 2× numerical and author review. The head-family scope and acceptance below remain historical evidence; their unchanged coarse-shadow and head-rectangle-only statements describe that earlier checkpoint, not the new shadow compositor.

## Scope

Front port13 Protron uses records322–332 for powers1–11. Its three static
spriteSheet8 designs are225 (P1–8),244 (P6–11) and226 (an additional P11 head).
P11 emits244×5 followed by226×3. These are distinct designs, not animation
frames. Preserve original12×14 logical canvases, anchor(0,0), spawn offsets,
velocities, spread, cadence, generator use, hit behavior and simulation.

The finite player TILE bindings use independent slots469–471. Normal RGB
heads gain generated cyan energy artwork with inward-softened straight alpha.
The original indexed blit still executes exactly once. Player shadows retain
their original indexed silhouettes and origin. Generic bullet blend behavior
is unchanged.

Christmas244 has a different original image. The entire three-head HD family
requires `!xmas` before cache lookup; Christmas gameplay retains its original
heads. Direct enemy shots, shop simulation, shop icons and Christmas prompt
snowflakes retain their original routes. No global sprite-table or blitter
replacement is made. Missing or invalid assets fall back independently per
head through the existing player loader, including its existing8→4 behavior.

## Frozen art and checks

`assets/hd/artwork/player-protron-three-v1/inventory.json` pins the approved
softened V2 generated master, prompts, technical support-mask geometry and
three outputs. Original RGB/indexed sprite payloads and decoded weapon tables
are excluded. The PNGs are96×112 RGBA; each HDR1 HDA is43,036 bytes with keys
80225/80244/80226,density8,logical12×14,anchor0,0.

Run `python prototype/build-protron-art.py --output NEW_EXTERNAL_DIRECTORY`
to verify the canonical resources and rebuild the three PNG/HDA outputs
byte-for-byte. Pillow, NumPy and SciPy are required. The ordinary
`python prototype/build-hd-assets.py` includes this verification. Both current
default packs gain exactly three entries; all prior resources stay unchanged.

## Bounded actual acceptance

Twelve90-tick runs (1,080 actual renderer ticks), with no failures or retries:
- E1 physical9 P1/P6/P11 baseline/candidate at Integer2×; six consecutive
  native frames40–45 each.
- P11 baseline/candidate at Integer4×; one native frame42 each.
- Candidate missing-all P6/P11 at2×, frame42; reuse matching normal baselines.
- Christmas P11 baseline/candidate at2×, frame42.

Exactly42 native SDL readbacks and42 true INDEX8 snapshots were retained.
Every tested original state/RNG/indexed/projectile/request/emission/draw and
non-target material comparison passes. P1 observes225,P6 observes225+244,
P11 observes244+226. Native RGB differences are confined to the actual target
head draw rectangles; this is not an independent full-frame RGB reconstruction.
Missing-all and Christmas match their baselines exactly in native RGB and
all90-tick RGB audits. Christmas has zero new Protron HD draws. All collision
logs are empty; no natural-collision acceptance is claimed.

The existing streamed blend helper consumed287,280 rows across the twelve
runs (23,940 per run), retaining whole raw-byte SHA256 and separately normalized
original indexed-column SHA256, plus90 per-tick proofs. Matched normalized
original proofs agree. Raw blend rows were not retained; other selected TSVs
remain complete lossless gzip. `protron-three-v1/STREAMED_BLEND.json` records
coverage and hashes separately from the RGB-delta/visual claim.

Artist review passes all18 candidate2× sequence frames and the P11single4×
spot:225 stays tiny and readable;244 keeps its softened offset shoulder;226
remains distinct. No observed head flicker, matte box or size jump. Original
indexed shadows remain visibly pixelated and unchanged. The accepted work is
these normal-data head designs, not a replacement for every weapon effect.

## Source/unit and reproduction boundary

The finite ASan/UBSan suite passes both default packs and the pinned baseline.
Each candidate pack passes28,848 finite binding cases,1,032 indexed/RGBA
transactions,13,867,232 affected-subpixel comparisons,50 complete unit-frame
checks,589,824 exact-alpha cases and12 actual blend fallback/restoration cases.
It covers independent caches, cold/warmed Christmas rejection, overlapping
heads, clipping/pitch/ownership, prior player paths, malformed/missing assets,
existing8→4 fallback and indexed shadows. Font/material integration is stubbed
or fail-if-entered in units; exact unit alpha is distinct from actual-game RGB
rectangle confinement. LeakSanitizer alone is disabled for executor ptrace.

`prototype/test-protron-binding.py` and its companion C driver take explicit
candidate, pinned Git baseline, frozen art, legal normal/Christmas game data,
private source-audit packet and fresh external-output paths. The source audit
and generated decoded-bank fixtures are external inputs, not distributed game
data. See `protron-three-v1/SOURCE_UNIT.md` for invocation and boundaries.

The source proof reverses exactly four renderer fragments to e54ebee and checks
all142 production files. Independent technical review and capture hashes are
in `protron-three-v1/FINAL_REVIEW.json` and `capture-pins.json`; bounded author
acceptance is pinned in `author-receipt.json` and `capture-hashes.json`. The frozen art
contract records its offline state; this document records subsequent bounded
runtime acceptance without modifying that frozen inventory.

Source closure covers all11 powers and all three item-table groups. Actual
cases cover P1/P6/P11 in E1 only. No other-power/episode gameplay, campaign
acquisition, full-arsenal, continuous4× motion, broad lifecycle or Windows
acceptance is claimed. Original RGB/indexed sprite payloads, decoded tables,
raw runtime traces and captures remain outside Git.
