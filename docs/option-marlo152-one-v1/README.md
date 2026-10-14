# Satellite Marlo: one normal body, fresh restored batch

Baseline is published commit `cf2019726c1891e558df0959b415558ae598b386`, tree `72bafdfce4b2ac5d0efb2821534dec2816596489`. This batch uses a fresh generated master and fresh verification; the previously lost unpublished candidate is not reused.

## Artwork and scope

One first-shop Satellite Marlo option30 body, normal bank9/152. Its real option record has pwr0/ani1/style4, so152 is the sole active frame; stored113/132/151 tails are not animation frames. Weapon470's existing bank8/67 projectile, HUD icon, shop simulation, other sidekicks, Talon and Mint remain outside this artwork scope.

Independent resource role126/index152/slot536 uses HDR1 `[1260152,8,12,14,0,0]`, logical12×14, physical96×112 RGBA, anchor0,0. New HDA SHA256 is `aefe1218aaf7959b1623d877bf14ad5bb75b52a4520183e85d563d2ef3726fda`. Each existing default manifest adds exactly this one resource,544→545; old resource records remain unchanged. The full Git-tracked default directory separately contains550 old HDA files (including six HUD resources outside that manifest list) plus five auxiliary material files; preserve all555 and add only Marlo to reach551 HDA/556 files. Sparse development worktrees may leave old resources unmaterialized; that is not a complete pack distribution.

The generated master and exact fixed crop[148,132,1130,1114]→LANCZOS64×64→paste16,16 are frozen under `assets/hd/artwork/option-marlo152-one-v1/`. No repaint, recolor, alpha threshold or shape edit is used. The original support bbox[2,2,10,10] and center6,6 are preserved on the full tile. Actual native2x offline review accepted the visible hot lower core and orange/red width; the73.84% alpha-weighted area is a known reviewed soft-edge tradeoff. No original sprite pixels, original game files or private screenshots are included in this source batch.

## Original rendering contract

Only the existing option30/style4/charge0/body152 bank9 TILE site enters a dedicated wrapper and source guard. The decoded zero-filled168-byte indices followed by168-byte coverage must match FNV1a64 `840f92ed11537363` before every cold or warm lookup, including same-address reload or mutation. Christmas152 is empty and keeps its original invisible indexed fallback; cached normal art must never fill it.

The original indexed blitter always runs once at unchanged sidekick.x/y. It keeps its original clipping and physical-row-wrap behavior; HD can conservatively decline wrapping placements. No Talon5,7 anchor is applied. Original single/dual orbit0.15/0.2, animation, draw ordering, movement/death/endLevel branches, input, equipment, cash, shots, RNG, collision and palette logic remain unchanged. Production changes are limited to `mainint.c`, `entity_draw.c/.h` and `render_mirror.c/.h`; generic Talon/Mint binding, compositor, pixel bridge and original blitters remain unchanged.

## Reproduction and completed finite checks

The asset checker uses only the stored independent generated master:

```
python prototype/build-marlo-art.py
python prototype/test-marlo-binding.py --data /path/to/your/licensed/tyrian2000 --out /external/new-check-directory --compile-engine
python prototype/test-marlo-scope.py --out /external/new-scope.json
```

The generated-master rebuild passes. Exact scope inversion checks all153 production source files and rejects19 forbidden mutations. Optimized and ASan/UBSan extracted-production units each pass171 admission cases,188 source-identity cases,18 resource variants,103 wrapper calls,101 full pixel cases,99 original draw-block state cases,30 regression cases and360 original orbit ticks. Each run compares2,084,864,000 RGBA bytes and6,513,600 indexed bytes. Equal semantic source with a different valid RLE encoding is accepted; same-address Christmas reload remains empty. All72 C translation units compile and link, and classic-disabled entity/renderer units compile. Separate optimized and ASan/UBSan classic-disabled wrapper checks produce exactly two original blits for two calls; their build suppresses unused-parameter warnings because the disabled macro consumes none of the three new context arguments. The tracked version header is unchanged.

These units extract actual production loader, guard, wrapper, dispatch, compositor, pixel bridge and original RLE bodies. Function-name-only shims observe calls and original writes; unrelated font/material/green-smoke/shadow collaborators are no-op or fail-if-entered stubs. LeakSanitizer is disabled for this executor; ASan/UBSan remain enabled. Malformed sources are exercised only at the guarded HD admission, not passed to the intentionally raw original RLE blitter. Full original data is not part of this repository.

## Original-menu runtime evidence

A private input/observer copy, exactly reversible to all153 production source files, completed one bounded v2 batch: Normal physical9 and Hard physical15, baseline/candidate, each120 real gameplay ticks and exit0. Both packs use the same binary; the baseline retains all555 old files, while the candidate adds only the new HDA. Original time(NULL) seeding is untouched; both Normal processes naturally used seed1792020433 and both Hard processes seed1792020460. Only ordinary SDL key events control the original Full Game EP1 menus and held main fire. No equipment, cash, protection, position, orbit or RNG state is forced.

Each case really purchases left Satellite Marlo30 for2000, cash10000→8000, rightNone. The original shop sorts the available items as9/16/30/0, so currentNone begins at submenu selection5; ordinary Up selects Marlo, then Enter selects Done and another Enter commits the purchase. Two earlier v1 menu-only attempts rejected the fixture's incorrect unsorted selection expectation at this boundary, before purchase, gameplay or PNGs. Their failure evidence is retained; they are not counted as successful runtime runs, and the v2 correction changes only private fixture expectations/input navigation.

For each paired120-tick run, original player/enemy/shot/particle/global state, RNG, indexed game/display surfaces, palette, positions, Talon draws and shot traces match exactly. Every frame records one original Marlo blit and52 original indexed writes,6240 writes per case. There are24 original weapon470 requests and24 emissions per case. Baseline body HD admission is0 and candidate admission1 throughout.

Each case retains five real640×400 SDL renderer readbacks: selected and purchased shop screens plus three gameplay frames. The shop images are identical between packs. Normal captures ticks5/100/119; Hard captures first fully visible61-cell NIGHT dark support at5, fully lit support at15, and119. All six gameplay pairs have a visible final-display difference confined exactly to the Marlo bbox's16×16 screen region,208–211 changed pixels, with no difference outside it. Actual Normal100 and Hard5/15 images were visually reviewed and accepted; darkness follows the original light cone and the bright orange core remains legible.

The private PNG writer initially emitted an invalid zero CRC for the empty IEND chunk, causing strict container validation to fail after all four engines had completed. Original PNGs and failure evidence remain untouched. Separate lossless-recovered copies change only the four final IEND CRC bytes to the correct value; every IHDR/IDAT CRC, zlib payload, decoded scanline and captured RGBA hash is identical to the originals. Strict validation passes on those copies. This metadata recovery makes no new game starts or captures and does not edit any pixel. Input/observer helpers, original/recovered screenshots and traces remain private and are excluded from this20-file source/art batch.

## Explicit coverage limits

Right and dual Marlo actual purchases remain uncovered; those placements and duplicate/overlap paths are focused-unit coverage only. Initial spawn invulnerability is100 ticks. Although ticks99–119 record non-invulnerable Talon draws, positions alone do not prove a non-invulnerable ship-body occlusion witness, so that visual remains unverified. No collision-contact result, whole-level/campaign survival, Christmas actual play, all backgrounds, Windows package or performance qualification is implied. The final20-file source/art candidate is prepared separately from private evidence; publication remains a separate action.
