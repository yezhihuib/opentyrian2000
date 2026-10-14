# Normal front Multi: eight static player heads

Status: source/unit checks, independent numerical review and author review pass for the bounded normal P2/P4/P7/P11 native 2× cases.

## Finite change

Baseline: `7df8368acb90a73b170b1238b3161eefddb7a8e1`.
Production renderer SHA256: `534065b887bf37c3792bbe16db28cd49211c05b9d5791ab21ef49a5815387796`.

Only `src/render_mirror.c` changes production behavior: capacity 524 → 532; normal-only player role-8 bank-8/TILE IDs 121, 122, 163, 164, 201, 202, 279 and 280 occupy slots 524–531. Admission precedes cache lookup, preserving cold/warm Christmas fallback. These eight shadows bypass the player asset cache and retain original coarse indexed contours, position and order. Existing 58/59, enemy roles including enemy-only 163/164, and the Vulcan 67/70 shadow lease remain unchanged. One adjacent comment corrects the existing rear-534/Data-513 slot ranges.

No gameplay, shot, collision, enemy hook, original blitter, public API, loader or compositor changes are included. The inverse restores all 148 production files exactly to the baseline. Both default packs add eight resources: 532 → 540 listed and 538 → 546 physical HDA files, retaining six unlisted files per pack and all old resources/provenance.

The [frozen generated-only art package](../../assets/hd/artwork/player-front-multi-eight-v1/README.md) supplies standalone semantic SVGs, pinned rebuild scripts and eight PNG/HDR1 pairs: density 8, logical 12×14, anchor (0, 0), straight RGBA and exact 28-byte headers. No density-4 art is added; independent 8 → 4 → indexed fallback remains unchanged. Its offline receipts retain their historical status; later runtime acceptance is recorded separately below.

## Bounded actual-engine acceptance

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

The author directly reviewed all 24 candidate and 24 matching baseline native frames. Slender, diagonal and fan heads retain their distinct warm forms over clouds and rocky terrain; twins 279/280 retain separate luminous cores and a central gap. No added halo, trail or visible head-form/color flicker appears in the six-frame sequences. Original coarse indexed shadows remain a known visual limitation.

## Source/unit coverage and limits

The added resources complete normal front Multi port-2 ordinary P1–11 membership, including existing 58/59. Exact source/unit checks cover all 11 powers × 3 tables and finite reuse by rear 10 mode 2/P4, Hyper Pulse 27/P9–11, NortShip Spreader 37/P1–7, options 20/22, charge 461 and `linkMultiGr`/`linkMult2Gr`. This does not establish completion or live acceptance of those larger weapons.

Historical tests remain unchanged. Portable tests accept external input paths and keep outputs outside Git:

- `prototype/test-front-multi-original.py`: exact shot creation/movement/direction/cadence, ordered volleys, cost, capacity shortages, drift rejection and finite reuse; requires verified original item files and the reviewed external contract.
- `prototype/test-front-multi-binding.py`: both defaults, alpha/RLE oracles, independent missing/invalid/8 → 4 → indexed fallback, normal/Christmas cold/warm cache, role isolation, original shadows and existing Vulcan shadow interleaving; requires frozen art pins and external normal/Christmas sprite files.
- `prototype/test-front-multi-scope.py`: exact production/manifest inverse, resource/header/input pins and preservation; requires a baseline checkout and external output location, without full baseline packs.

`make -j2 WITH_NETWORK=false` passes with the existing indentation warnings in [build-result.json](build-result.json). Both executable unit suites pass optimized and ASan/UBSan builds; LeakSanitizer is disabled. Source/unit receipts keep their historical zero-run counts. They are separate from the normal P2/P4/P7/P11 actual runs.

No native-4× gameplay, Christmas/every-power gameplay, live linked/charge/option/rear-family, shop acquisition, full-level/campaign, unprotected survival, Windows, physical GPU/fullscreen, performance or whole-arsenal acceptance is claimed.

[Runtime summary](runtime-summary.json) and [author-review summary](author-review-summary.json) contain portable hashes and bounded results. Original game data, decoded reference arrays, gameplay screenshots and private logs are excluded from public files.
