# Normal front Multi: eight static player heads and smooth shadows

Status: source/unit checks, independent numerical review and direct author review pass within the separately documented head-only and smooth-shadow P2/P4/P7/P11 native 2× scopes.

## Historical head-only change

Baseline: `7df8368acb90a73b170b1238b3161eefddb7a8e1`.
Production renderer SHA256: `534065b887bf37c3792bbe16db28cd49211c05b9d5791ab21ef49a5815387796`.

Only `src/render_mirror.c` changes production behavior: capacity 524 → 532; normal-only player role-8 bank-8/TILE IDs 121, 122, 163, 164, 201, 202, 279 and 280 occupy slots 524–531. Admission precedes cache lookup, preserving cold/warm Christmas fallback. These eight shadows bypass the player asset cache and retain original coarse indexed contours, position and order. Existing 58/59, enemy roles including enemy-only 163/164, and the Vulcan 67/70 shadow lease remain unchanged. One adjacent comment corrects the existing rear-534/Data-513 slot ranges.

No gameplay, shot, collision, enemy hook, original blitter, public API, loader or compositor changes are included. The inverse restores all 148 production files exactly to the baseline. Both default packs add eight resources: 532 → 540 listed and 538 → 546 physical HDA files, retaining six unlisted files per pack and all old resources/provenance.

The [frozen generated-only art package](../../assets/hd/artwork/player-front-multi-eight-v1/README.md) supplies standalone semantic SVGs, pinned rebuild scripts and eight PNG/HDR1 pairs: density 8, logical 12×14, anchor (0, 0), straight RGBA and exact 28-byte headers. No density-4 art is added; independent 8 → 4 → indexed fallback remains unchanged. Its offline receipts retain their historical status; later runtime acceptance is recorded separately below.

## Historical head-only actual-engine acceptance

Eight Linux SDL dummy/software attempts compare baseline and candidate at P2, P4, P7 and P11. Each runs 90 logic ticks (0–89) and retains six actual native 640×400 BMPs plus six palette-correct 320×200 INDEX8 BMPs at fixed ticks 38–43. Total: 720 ticks, 48 native and 48 INDEX8 frames; no retries, retargets or capture-window searches.

The private fixture sets a diagnostic starting loadout once: Episode 1, physical level 9, Normal story mode, seed `0x5eed`, front port 2, no rear weapon or sidekicks. An input-only adapter feeds ordinary replay keys to unchanged movement/firing routines: fire, left+fire, right+fire, neutral, then fire. Original protection counts down 100 → 10; shield recharge, energy failures and generator recovery remain active. No power refill, projectile injection, extra protection or collision exclusion is added. This is not natural acquisition or manual input.

Per-run counts match within each pair:

- P2: 22 requests, 19 complete volleys, 38 members; power failures at ticks 1/26/27. New IDs 201/202.
- P4: 17 requests, 16 complete volleys, 48 members; power failure at tick 1. New IDs 163/164 plus unchanged 59.
- P7: 14 requests, 13 complete volleys, 39 members; power failure at tick 1. New IDs 121/122 plus unchanged 58.
- P11: 14 requests, 13 complete volleys, 65 members; power failure at tick 1. New IDs 121/122/279/280 plus unchanged 59.

Original member order, cost 40 once per complete volley and static `del255` velocity independent of mouse delta are verified. All 90 ticks match in state/RNG and compared original traces; all 24 paired INDEX8 files and normalized original blend writes are exact. Independent review compares 6,144,000 native pixel pairs: 44,169 changed pixels, all within eligible new-head rectangles. Non-target draws match, and 41,148 original-shadow native sample comparisons outside head overlap are exact. Existing 58/59 pixels there also match. Collision/hit logs are empty, so equality does not establish collision coverage.

### Fixed-window visibility

Acceptance requires a qualifying witness for every selected identity across each fixed six-frame window, one qualifying member in every frame and one complete visible single-call volley per window. Each new-head witness meets majority original-mask support and majority frozen high-alpha native-core support. Opaque RGB is exact; fractional core samples meet source-alpha bounds and actually differ from baseline. Full fractional composition is covered by separate renderer units.

- P2: 201/202 qualify at 38–43.
- P4: 163 qualifies at 38–40 and 43; 164 and unchanged 59 at 38–43.
- P7: 121 qualifies at 39–41; 122 and unchanged 58 at 38–43.
- P11: 121 qualifies at 39–41; 122/279/280 and unchanged 59 at 38–43.

P4/163 is clipped below required support at tick 41 and absent at 42. P7/P11/121 does not qualify at 38 or 42 and is absent at 43. Before launch, the earlier projection's omitted 24-pixel viewport shift was corrected to this per-ID window criterion; inputs, capture ticks, physics and support thresholds were unchanged. These partial frames are not full-head witnesses.

The author directly reviewed all 24 candidate and 24 matching baseline native frames. Slender, diagonal and fan heads retain their distinct warm forms over clouds and rocky terrain; twins 279/280 retain separate luminous cores and a central gap. No added halo, trail or visible head-form/color flicker appears in the six-frame sequences. Original coarse indexed shadows were a known limitation of this head-only checkpoint; the later extension below addresses their eligible normal-player calls.

## Historical head-only source/unit coverage and limits

The added resources complete normal front Multi port-2 ordinary P1–11 membership, including existing 58/59. Exact source/unit checks cover all 11 powers × 3 tables and finite reuse by rear 10 mode 2/P4, Hyper Pulse 27/P9–11, NortShip Spreader 37/P1–7, options 20/22, charge 461 and `linkMultiGr`/`linkMult2Gr`. This does not establish completion or live acceptance of those larger weapons.

Historical tests remain unchanged. Portable tests accept external input paths and keep outputs outside Git:

- `prototype/test-front-multi-original.py`: exact shot creation/movement/direction/cadence, ordered volleys, cost, capacity shortages, drift rejection and finite reuse; requires verified original item files and the reviewed external contract.
- `prototype/test-front-multi-binding.py`: both defaults, alpha/RLE oracles, independent missing/invalid/8 → 4 → indexed fallback, normal/Christmas cold/warm cache, role isolation, original shadows and existing Vulcan shadow interleaving; requires frozen art pins and external normal/Christmas sprite files.
- `prototype/test-front-multi-scope.py`: exact production/manifest inverse, resource/header/input pins and preservation; requires a baseline checkout and external output location, without full baseline packs.

`make -j2 WITH_NETWORK=false` passes with the existing indentation warnings in [build-result.json](build-result.json). Both executable unit suites pass optimized and ASan/UBSan builds; LeakSanitizer is disabled. Source/unit receipts keep their historical zero-run counts. They are separate from the normal P2/P4/P7/P11 actual runs.

No native-4× gameplay, Christmas/every-power gameplay, live linked/charge/option/rear-family, shop acquisition, full-level/campaign, unprotected survival, Windows, physical GPU/fullscreen, performance or whole-arsenal acceptance is claimed.

[Runtime summary](runtime-summary.json) and [author-review summary](author-review-summary.json) contain portable hashes and bounded results. Original game data, decoded reference arrays, gameplay screenshots and private logs are excluded from public files.

## Smooth-shadow extension

Only `src/render_mirror.c` changes production behavior relative to the head-only
checkpoint. Renderer SHA256:
`cc54f1096e118c4a8388e6a9c4e0db4347cfc713621e94fa4b5566c8ed7fe0df`.
A finite ten-entry identity table retains Vulcan 67/70 and adds normal player
121/122/163/164/201/202/279/280 to the existing single-command shadow protocol.
It reuses the exact frozen density-8 alpha and original 12×14 canvas, shadow
origin and draw order. Each sample applies the unchanged full-strength shadow
operation, then the unchanged straight-alpha blend. Alpha zero preserves the
composed underlay; authored support outside the old coarse mask is retained.
No new art, manifests, resource slots or pack copies are needed.

Admission remains fail-closed: exact selected source semantics and resource
identity/metadata, explicit normal mode, compatible surface/canvas/storage/pitch,
current root/tick/origin and original indexed pre-write values are required.
Missing, invalid, density-4-only, Christmas, reference-mode or incompatible inputs
retain classic fallback. Horizontal admission remains x=0…308 and vertical
admission y=−13…199; negative-x row-wrap calls are not widened. Identical selected
121/122 bytes under an artificial normal-mode flag satisfy the semantic check;
this is not a whole-bank provenance test. Actual Christmas mode rejects every
member, including a warm cache.

Original indexed writes still occur exactly once. Heads, existing 58/59, enemy
roles and Protron retain their assets and operators. Their final translucent
pixels can nevertheless change where an earlier new shadow changes the underlay;
no blanket head-crop equality is claimed. Other normal-player paths reusing these
IDs inherit the same finite admission, but linked, charge, option and rear-family
runtime acceptance is not established by the front-Multi captures.

### New bounded runtime evidence

Four new candidate-only Linux SDL dummy/software runs cover P2/P4/P7/P11, each
90 ticks with six native 640×400 frames and six INDEX8 320×200 frames at ticks
38–43. They compare against the retained head-only candidates using the same
inputs, seed, loadout and capture window described above. There are 24 native
frame pairs and 24 INDEX8 pairs; no new baseline, retry or capture search is used.
All 360 compared ticks preserve original state/RNG and ordered original traces;
normalized original blend writes and the 24 paired INDEX8 files are exact.

Across 6,144,000 native pixel comparisons, 9,267 pixels change. All changes lie
within original source support UNION sampled nonzero alpha, with original crop
and draw order applied; there are zero differences outside that support or after
opaque-head erasure. All eight new IDs have real and fractional-alpha change
witnesses across their fixed windows. P7/P11 include 143 changed head-support
pixels through legitimate overlap. Full fractional composition is established by
source units, not inferred from these image comparisons. The inherited head
visibility results retain their original partial-frame qualifications.

The original target-shadow / admitted-shadow counts are P2 594/590, P4 574/510,
P7 468/415 and P11 894/838. The remaining 177 calls retain guarded classic
fallback; P2/P4/P7/P11 include 0/10/9/9 such calls in the capture windows.
The author directly inspected all 24 new frames and all 24 retained references
at original resolution. Eligible shadows are smoother and narrower at the
original offset; slender, diagonal, fan and twin heads remain distinct, including
bounded dense P11 near-ship volleys. Cropped members and guarded old contours
remain outside the upgrade claim.

### Focused source and presentation checks

Independent source/unit review passes. Primary and supplemental suites each pass
optimized and ASan+UBSan builds against both default packs. Each primary
combination checks 29,418 transactions, all 100 ordered identity pairs, 864 guards,
1,102 lifecycle cases and 524,288 exact-alpha arithmetic cases. Each supplemental
combination adds 120 presentation checks across all ten IDs, including frame
begin, crop, repeated Present and black/white/restoration fades. The original
blitters, shadow operator, 58/59, enemy and Protron controls remain exact. These
are extracted-source tests with integration stubs; LeakSanitizer is disabled.

See [shadow source scope](shadow-source-scope.json),
[shadow source/unit results](shadow-units.json),
[shadow runtime summary](shadow-runtime-summary.json) and
[shadow author review](shadow-author-review-summary.json).
Run the focused harnesses from the checkout root, using separately supplied
original data and a fresh output directory outside the checkout:

```sh
python3 prototype/test-front-multi-shadow.py \
  --normal-data /path/to/tyrian.shp --xmas-data /path/to/tyrianc.shp \
  --out /fresh/external/unit-output
```

`--prepare-only` generates and preflights without compiling or running. Candidate
and baseline default to this checkout; `--baseline` can select a Git repository
containing the pinned parent commit. These harnesses do not launch the engine.
Historical head-only receipts above are preserved rather than relabeled as
shadow-extension results.

This extension adds no native-4× actual-engine, every-power or Christmas gameplay,
noncaptured shared-weapon family, full-level/campaign, Windows, physical GPU or
performance acceptance. Empty collision/hit traces do not establish collision
coverage. Public summaries contain no original game data, decoded reference
arrays, private paths, original pixel payloads or engine captures.
