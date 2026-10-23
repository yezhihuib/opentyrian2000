# NEWSHF compositor hook audit — deferred, not implemented

> Historical phase receipt. The separately opt-in actual compositor is now
> documented in [NEWSHF HD compositor](newshf-hd-compositor.md); the original
> limits and results below describe this earlier phase, not its successor.

Audit baseline: `b62a2b00cd2311bc215caa9807c0c85cbd901164`.
Function names below are stable lookup anchors; line numbers in that baseline
are illustrative, not a patch recipe. This is a source inspection, not game
acceptance or evidence that the listed compositor work has been completed.

## Current boundary

The selected next step is an **opt-in identity-validation prototype only**.
It must not load/draw HD art, grant renderer eligibility, change indexed blits,
or alter gameplay/RNG. Every NEWSHF pixel remains on its existing classic path.
The nine PNGs remain the source-only art contract. A native identity harness
cannot establish compositor correctness, packaging readiness, or real E1
acceptance. Everything in the compositor inventory below remains deferred.

Scope is logical bank **10 / `newshf.shp`**, never static `spriteSheet10`:
records 163 (poses 125,123,127), 167 (3,1,5), 168 (55,17,93), logical 24x28,
anchor (6,7), density 8, quadrant offsets 0,1,19,20. Records use ani=1,
animate=0. Pose selection is not an automatic three-frame animation.

## Identity-only lifetime audit

| Location | Required observation / invariant |
|---|---|
| `tyrian2.c:JE_makeEnemy`, entry (~4033) | Invalidate any previous role for the actor slot and advance its allocation generation, including allocations of unrelated records. Observe requested record and unique-shape override before native initialization. Never modify either. |
| `JE_makeEnemy`, bank resolution (~4050–4076) | The native path leaves the previous `sprite2s` pointer intact if the requested bank is absent. Require exactly one currently loaded logical-10 slot and the exact `&enemySpriteSheets[i]` object, not merely equal bytes or a base ID. |
| `JE_makeEnemy`, before return (~4323) | Consume the pending allocation witness once; require the same generation, record, bank generation, slot object, data pointer, size and content stamp. Verify the native returned availability plus exact initialized fields. A re-query of current bank 10 alone cannot prove continuity. |
| `tyrian2.c:JE_drawEnemy`, after native animation block (~252) | Observe a draw opportunity once per simulation tick, before visibility/quadrant branches. NEWSHF expects `ani==1`, `aniactive==0`, `animin==1`, `animax==0`, `aniwhenfire==0`; allow the exact current pose 1..3, not rotor's `next_phase` rule. Snapshot native origin/filter and permitted quadrant sequence. |
| `tyrian2.c:blit_enemy` (~180) | Match each observed quadrant against the actor snapshot, exact base/pose/bank binding, coordinates and order. Original `blit_sprite2[_filter]` calls remain unchanged and authoritative. |
| `render_mirror_begin` (~1442) / existing native tick boundary (`tyrian2.c` ~1126) | Identity ticks must advance independently of HD eligibility. The original renderer has an early return **before** `++mirror_logic_tick`; do not accidentally starve identity observation in classic/manual-scope-excluded runs. Never use repeated Present or per-sprite calls as a simulation clock. |
| `sprite.c:free_sprite2s` (~548) | Retire NEWSHF bank witnesses **before** freeing a matched enemy-bank slot. Advance a generation even if the allocator later returns the same address and bytes. Existing global reset here covers only static sheets 8/9 and explosions, not enemy sheets. Use a targeted observer rather than silently broadening unrelated owner resets. |
| `sprite.c:JE_loadCompShapes` (~524) | Calls `free_sprite2s` before replacement, so the pre-free observer covers the production enemy-bank load route. `JE_loadCompShapesB` loads bytes directly: audit future/new callers and synthetic tests rather than assuming every possible write uses the wrapper. |
| `tyrian2.c`, event type 5 (~4501–4524) | Current production bank-ID changes occur after load/free. Every changed slot reaches `JE_loadCompShapes` or `free_sprite2s`; no-op same-ID events do not reload. Validate IDs anew at each observation and test logical-ID removal/rebind and duplicate-ID rejection. A future ID-only mutation route would need explicit invalidation. |
| `tyrian2.c`, startup array clear (~1084) | `enemySpriteSheetIds` and actor arrays are reset. Existing start-level reset paths must invalidate identity first; do not allow an old witness to survive a cleared/reused pool. |
| `render_mirror_global_reset` (~1714) | Include identity invalidation. Existing callers cover `start_level`, `start_level_first`, debug/probe exits, map begin, and video teardown. Audit those callers rather than adding a new level-eligibility predicate. |
| `render_mirror_set_global_assets` (~1249) | Actual root change, invalid root rejection, and disabling root must retire identity state if the prototype shares this lifecycle. The existing same-root fast return is not a resource reload. |
| `render_mirror_hud_shutdown`, `video.c:deinit_video` | Explicit shutdown invalidation; all observers must be no-ops when the opt-in feature is absent, including disabled-renderer compilation. |

Bank proof must cover the entire pinned 33,543-byte source, not only selected
RLE tiles. Record proof must serialize the canonical 77-byte records (not C
padding), with immutable source pins. A stamp is an observed content check, not
an allocation-generation substitute. Recheck exact current binding and proof at
initialization and draw; permanently retire a failed role until fresh allocation.
All 20 egraphic entries and record/type/data-object association matter. Record
824 and overlapping NEWSH2 IDs do not gain eligibility.

Required negative cases include missing/duplicate bank 10, stale inherited
pointer, equal data through a different slot object, bank relocation, same-address
reload, in-place content mutation, record mutation, actor reuse, wrong unique
shape, duplicate initialization, missing allocation, changed tick, invalid pose,
wrong quadrant/order/origin/filter, interrupted quartet and every reset route.
Testing calls to helper functions alone does not establish the production wiring;
a source-delta check should also prove only observational statements were added
around unchanged native gameplay statements.

## Deferred compositor inventory

A separate finite owner would need **all** of these categories. Merely copying
`global_rotor_mirror.inc` and replacing 1 with 10 is unsafe.

1. **Independent admission:** an explicit default-off request and resource root;
   add that owner to early admission checks in `render_mirror_begin`,
   `shared_hud_finish`, `render_mirror_finish`, `render_mirror_fade_start`,
   `render_mirror_fade_step`, and `render_mirror_present`. Those checks currently
   use `global_talon_requested()` as the global-root signal. Do not broaden
   `mirror_enabled`, `manual_hd_scope`, asteroid level predicates, or generic
   enemy-bank routing.
2. **Declarations/build boundary:** independent state/prototypes and include in
   `render_mirror.c`; declarations and disabled no-op API in `render_mirror.h`.
   Unique finite resource roles, not reuse of overlapping NEWSH2 base IDs.
3. **Resource/root lifetime:** all-or-classic exact-nine loading; dimensions,
   anchor, density, source and palette proofs; shutdown on actual root change
   and `render_mirror_hud_shutdown`; reset through `render_mirror_global_reset`.
   Resource failures cannot leave a partially admitted family.
4. **Frame lifetime:** frame begin, owner/foreign allocation and clearing,
   source/final/canvas/output surface leases, contribution/fault flags and
   underlay palette tracking. Include owner state in begin reset assignments
   and all active-frame early-return conditions.
5. **Draw routing:** independent path at the top of
   `render_mirror_enemy_tile`, before legacy scene predicates; exact candidate
   context and logical bank proof. Retain native quadrant coordinates,
   visibility clipping, filtered indexed blits and ordered actor observation.
6. **Native-write observation:** `render_mirror_pixel` final-output observer,
   active guard and owner dispatch; `render_mirror_rect` final rect observer
   and active guard; `render_mirror_unsupported` active guard;
   `render_mirror_sprite2_blend_pixel` blend admission. Preserve expected-index
   tracking, ordinary occlusion, shadows, filters and partial clips.
7. **Entity completion:** `render_mirror_entity_end` must close native-pixel
   expectations. Missing, duplicate or interrupted writes/quadrants cannot
   retain an HD prefix.
8. **Cross-owner transfer:** bidirectional clearing with
   `global_talon`, `global_shield`, `global_pulse`, `global_vulcan`,
   `global_hitflare`, `global_smoke`, `global_green`,
   `global_small_explosion`, `global_cash25`, and `global_rotor` owners in
   their respective `*_mirror.inc` files. Track dependencies where RGB from
   one owner is incorporated by another. HUD/font transfer also matters.
9. **Finish proof:** `render_mirror_finish` must run NEWSHF proof before any
   composition; include it in whole-frame failure/cache reset assignments and
   surface-lease checks. Faults after RGB ownership transfer must reject the
   **complete HD Present**, not just pixels still tagged NEWSHF.
10. **Both composition branches:** include independent composition in
    `shared_hud_finish` and the active-scene branch of `render_mirror_finish`.
    Include its frame flag in fallback/normal15 early paths. Preserve final
    INDEX8 mapping and approved output kinds; unsupported kinds stay classic.
11. **Cached output:** `render_mirror_present` and fade start must recheck
    bank/record/source/surface/palette proof before reusing output. Final pixel
    and rectangle observers must invalidate affected cached/fade pixels.
12. **Fades:** integrate buffer safety/disjointness, capture lease, integer
    palette-step proof, palette update and cache decline into
    `render_mirror_fade_start` and `render_mirror_fade_step`. Alternatively an
    explicitly documented prototype may always decline NEWSHF cached/fade HD,
    but it still must prevent stale contribution reuse by other owners.

## Deferred asset/package proof

Generate HDA deterministically from the selected nine PNGs; never redraw or
copy original game bytes. Preserve old approved pixels and historical manifests.
New destinations require an exact additive nine-entry extension analogous to
Charge in `scripts/rebuild_recovered_runtime_manifest.py`, retaining the generic
unknown-consumer rejection. Current authoring/build binding and historical
inverse checks must admit only the reviewed new module/hash delta. No registry,
package, compositor or publication acceptance follows from this audit document.

Before any future compositor claim, test all nine resources, corrupt/missing
members, default fallback, native quadrant order and partial clipping, filters,
owner overlap/transfer, frame rejection, bank/actor lifecycle, roots, shutdown,
cache/fades, feature-on/off builds, exact package binding and unchanged old-family
pixels. Clearly distinguish helper harnesses, native production-path execution
and an actually observed E1 playthrough.
