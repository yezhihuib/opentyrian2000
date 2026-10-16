# Plasma Storm: three-piece HD projectile pilot

Baseline: `18a54527795971a4aa8492f86a0fc4996a51961d`.

This presentation-only pilot fits one generated master across the three simultaneous
Plasma Storm projectile pieces. It extends the existing
[blend and vertical-clipping fixes](../option-plasma-projectile-vertical-v1/VALIDATION.md).
The original compatibility implementation remains byte-exact.

## Bounded scope

- OPTION_SHAPES table 5, zero-based indices 22, 23 and 24; original encoded frames
  60023, 60024 and 60025. These are independent simultaneous pieces, not animation frames.
- Logical sizes 62×24, 65×28 and 62×23, with zero anchors. Their existing offsets
  are (−32,−24), (−32,0) and (−32,28), forming a 65×75 envelope with joins at y=24/52.
- Normal-data local single player, episode 1: Normal physical level 9 or Hard
  physical level 15. Left sidekick empty, right Plasma Storm 9, style 0 and charge 0.
  Actual weapon 88, right-bay/player-1 emission identity is recorded per allocated slot.
- Existing independent allocation, placement, shot-follow motion, collision radii,
  removal and raw draw order stay authoritative. Original indexed writes, palette,
  RNG, ammo, inputs, timing and gameplay are not replaced.

Christmas, network, two-player/linked/Galaga, demos, recording, action/arcade/bonus
contexts, weapon 1088, left/dual equipment and harder difficulties are excluded.
Sonic coverage remains 17/21; IDs 105/106/124/125 remain classic. The dynamic STORM
HUD label is a separate inherited visual gap.

## Artwork and blend

The [generated-only package](../../assets/hd/artwork/option-plasma-projectile-art-v1/)
retains the original returned master, exact prompt and deterministic whole-master
resize/split. Integration and recovery made no generation calls or art changes.
Six density-4/8 PNG/HDA resources use role 130 and IDs 1300022/1300023/1300024.
No original game raster, palette, mask, decoded array or capture is bundled.

Each draw checks complete current original source indices and coverage, including
hidden rows, before optional art/cache work. HDA header, size and pinned RGBA bytes
are checked every admitted draw. Projection caches verify the current warm palette,
density and cached-value checksum.

Generated RGB is projected to the nearest current warm-ramp position in 1/256
steps, choosing the lowest position on a tie. Source value is averaged with
continuous underlay max-channel value for HD owner 1, or the original low indexed
nibble for owners 0/2. The averaged value is interpolated on the current warm ramp;
generated alpha mixes that result with the underlay. This preserves the original
value-average semantics rather than substituting ordinary RGB-art alpha-over.

The complete visible source-sized rectangle is staged, including authored contours
outside the old mask. Full indexed-ledger preflight occurs before intersecting
retained text is stripped and before the underlay snapshot. The original raw blit
and callbacks still execute. Commit verifies the synchronous surface/target, format,
dimensions, pitch, provenance pointers, density, tick, warm palette and all indexed
results. Equipment/HDA-root flags are not reread at commit; the original synchronous
blit does not mutate them.

Original-covered cells with authored alpha zero retain HD ownership, preventing
the old mask from reappearing during Hard composition or fades. Uncovered alpha-zero
cells preserve the existing underlay and owner/cloud/green provenance.

Fallback is per piece. A missing or corrupt middle resource keeps that piece on
the previous compatibility path while valid outer pieces can remain authored.
Missing all selected-density resources restores the prior presentation. Horizontal
row-wrap, wholly offscreen, source/palette/context mismatches and unrelated sprites
retain their previous paths. No all-or-nothing family fallback is claimed.

## Verification and limits

The accompanying receipts separately record artwork reconstruction, exact source
scope, optimized/sanitized units, complete production builds, actual menu-purchase
runtime pairs, independent supplements and native visual review. Recovery produced
a newly validated candidate; historical results are not substituted for fresh tests.

- Optimized and ASan/UBSan stage units each pass 81,870,383 assertions over 4,721 draws.
- Ten qualified menu-purchase pairs cover four Normal/Hard native-scale combinations
  and six missing/corrupt/mixed-resource controls, for 20 processes and 6,400 ticks.
- Ten unresampled author-reviewed native views cover both difficulties and scales.
  All 12 clear-frame comparisons at ticks 190/220/319 match the paired baseline.
- Independent source, generated-art, blend/projection, retained-font/fade and runtime
  replay checks are recorded separately, with their exact sampling limits.

Runtime qualification is bounded to 320-tick Normal/Hard menu-purchase scenarios,
native 640×400/1280×800 and resource-fallback controls. Original-state comparisons
and authored-draw oracles must be distinguished from sampled final display frames.
Both native scales select density-8 art. Density 4, owner 2, rejected contexts,
alternate palettes and isolated retained-font/fade cases are unit-only where stated.
See RUNTIME.json and INDEPENDENT_SUPPLEMENT.json for exact counts and sampling bounds.

Linux SDL dummy/software rendering is used. No Windows, physical GPU, fullscreen,
performance, later refill, whole-level or full-campaign qualification is claimed.
ASan and UBSan are enabled in sanitized runs; LeakSanitizer is disabled.

## Reproduction

Generated-art verification requires no original game data:

    python3 prototype/build-plasma-projectile-art.py
    python3 prototype/build-hd-assets.py
    python3 prototype/test-plasma-storm-art.py --source-only
    python3 prototype/test-plasma-storm-art-scope.py --out /new/external/scope.json

Focused source and integration checks are supplied by
`prototype/test-plasma-storm-art.py` and `prototype/test-plasma-storm-art-scope.py`.
Use their `--help` output for required paths. Runtime/unit tests require separately
obtained original game data, a C compiler, sanitizers and the historical Git objects
used by the source checks. For example:

    python3 prototype/test-plasma-storm-art.py --data /path/to/tyrian2000 --assets assets/hd/packs/packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test --out /new/external/units

Private inputs and observer fixtures are not published.

Publication must use the independently reviewed frozen overlay with an expected-parent,
non-force branch update. A durable generated-art/source archive is retained before
publication; original game data, private captures and binaries remain excluded.
