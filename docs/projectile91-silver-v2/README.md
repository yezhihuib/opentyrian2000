# Shared enemy projectile91 — approved silver V2

Private integration based on public `f58647e7ff74e2276a1413b3675e651f1232bb41`.
No launcher7204 or private SHOP0ef62184 changes; no remote publication.

## Source and registration

The unchanged approved bitmap is
`authoring-inputs/projectile91-current/projectile91-silver-v2-concept.png`.
Its prompt, original-bank identity, original12×14 support mask and Library IDs
are preserved alongside it. It is one source for both original weapon24
consumers (records173 and285), not two separately edited copies.

The deterministic recipe is `scripts/current_projectile91_compatibility.py`:
- 1161×1354 straight-RGBA input; visible alpha>127 bounds `[311,121,850,1305)`.
- Remove low-alpha source dust (alpha≤127) before resampling; no painted/redrawn geometry.
- Preserve aspect by fitting to 44×96 (integer raster rounding +0.6803% aspect),
  not stretching to original visible6×12 proportions.
- Premultiplied-alpha bicubic downsampling, placed at `(26,16)` on96×112.
- Clip only to original62-cell logical support; trim0.0047345% resampled alpha
  mass. Transparent RGB canonicalized to zero. All62 original cells retain coverage.
- Full12×14 logical canvas, zero anchors,8× density. Original indexed shot
  blitter still executes; speed, rotation, firing, collision and RNG are unchanged.
- Generated role149/identity1490091 HDR1 transport is exclusive to authenticated
  normal bank8 enemy-shot selector91. NEWSH2/NEWSHD body91 and player role8 are not it.

Natural-size and4× display previews were visually inspected before asset
installation. The4× preview is an enlarged inspection aid, not native game pixels.

## Current workflow

```sh
python scripts/build_current_projectile91.py stage --selection <candidate.json> --stage <new-external-directory>
python scripts/build_current_projectile91.py apply --stage <staged-directory>
python scripts/build_current_projectile91.py check
```

Stage is non-mutating. Apply rederives, rejects stale/tampered plans and uses
existing batch rollback for handled write failures; it is not crash-safe across
process/power loss. Source geometry changes require a separate registration review.

`packaging/current-projectile91-compatibility.json` declares exactly one runtime
transport. No historical assets or global registry identities are overwritten.
Other current builders include this family's finite dependency closure; source
navigation and current preview overlays resolve to the same master/transport.

## Evidence boundaries

Native callback/production-shot-loop fixtures are not in-game screenshots.
Actual game captures must identify original event/seed/tick and original emitter,
with classic comparison and indexed-state equality. See final validation manifest
for completed checks and any explicitly unrun checks. Palette/Christmas/layout or
source failures must decline to classic rather than grant an unrelated role.

## Validated rendering scope

The independent `global_projectile91` owner does not enable the legacy mirror or
change asteroid/304 scope. It authenticates the normal bank and the silver source
palette entries, binds surfaces/resources, and rejects unknown source, Christmas,
foreign palettes and unsupported output/layout states to classic. Eleven existing
owner modules each gain exactly one clear of the *new91* owner/foreign flags at
their existing ownership-transfer point; no old role eligibility is widened.

Actual-game checks replay original level events with fixed normal input/seed:
record173 in E1 physical12, ticks70–77; record285 in E5 physical5, ticks830–837.
The native640×400 screenshots are direct SDL output captures, not a reconstructed
mockup or a resized8× art preview. Present/missing/corrupt91 share the same candidate
binary; public-base and full-original-reference runs supply extra comparisons.
The isolated missing91 pair retains other HD assets to isolate this one change.

Separate ordinary-lifecycle tests use the complete production renderer translation
unit and real wrapper/sprite linkage with legacy `active=false`. Their37cases and
81,611 assertions cover independent91 activation, palette/source/resource/layout,
ownership, root/cache/final-write rejection, and actual Talon overlap. ASan/UBSan
instrument the touched renderer/sprite/entity/harness units; other linked units
are optimized and LeakSanitizer is off. Fade testing covers capture and invalid
steps, not an exhaustive successful-fade sequence. These fixtures do not replace
the actual-game event replay evidence.

Not claimed: menu-to-campaign interactive launch, Windows/GPU platform acceptance,
compatibility with separately private launcher7204/SHOP0ef62184, or a full historical
suite pass. Several older stage-specific tests require missing historical Git
objects in this recovery repository; their old ledgers were not rewritten.
