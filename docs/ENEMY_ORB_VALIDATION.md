# Enemy-only energy orb112/113

## Identity and narrow hook

Original spriteSheet8 IDs112/113 are a complete two-frame12×14 energy family, anchor0,0. Enemy animation preincrements and wraps count2, so113 appears first. Eighteen loaded weapon records share this family;49 enemy records reference those weapons, but only the finite original type13/14 wave is claimed here. No rotation or damaged sprite variants exist. Player weapon animation instead uses count+1 and shadows, so no player get_asset mapping was added.

At the original surviving enemy-shot bank8 call site, only computed IDs112/113 enter draw_enemy_shot_sprite2. The bank12 branch and other IDs retain their original blits. Dedicated render_mirror_enemy_shot uses slots218/219, shared asset capacity220, exact bank/ID/surface guards, existing normal-alpha draw_asset and12×14 anchor0,0. It does not use green-head protection or a later overlay pass. The wrapper executes the original indexed blitter exactly once and resets suppression exactly once on success or fallback. Role108 scene logging identifies these enemy-only attempts. Movement, duration, collision, retirement, animation expressions and RNG stay in their original order.

Only two generated PNG/HDR assets are added to each current default pack:224/228 entries; total18 packs,2688 HDR entries,236 unique formal PNGs. The source regenerator reproduces both PNGs byte-for-byte; no original game data is included.

## Actual finite lifecycle and native review

Natural original replay through1043, with native4×/2× presentation from880, records349 explicitly ID-logged surviving shot attempts:168 for112 and181 for113, all HD. Every logged draw matches exactly one surviving enemy projectile origin, with no duplicates or retired-shot draws. State, collisions, player/enemy projectile motion, effects and poses are identical to original-art baseline at both scales. Nine original enemy-shot collisions are retained.

Frames with no live orb match original final RGB exactly:880–888 and948–958. The latter interval follows collisions and proves no retained orb pixels. Missing each phase gives eight HD and eight original fallbacks over889–896; missing both gives all349 original fallbacks and exact baseline RGB/state. The formal pack matches the reviewed candidate RGB and source logs.

Native contact889–896 and120 consecutive actual2× frames889–1008 show the orange/red core, controlled brightness pulse and soft perimeter over turret and terrain. Video inputs are direct SDL readback; all lossless decoded-frame hashes and noncapture RGB/state match. The MP4 is a lossy viewing copy. Actual cloud desktop4× paused889, resumed through897 and exited0. Original sprite-shadow/damage artwork is not invented because this enemy-shot path has none.

## Focused correctness and reproducibility

`python prototype/fixtures/test-enemy-orb.py --sanitize` extracts current production helper, wrapper and original RLE blitter. ASan/UBSan checks46,024,704 pixel comparisons,108 wrappers,18 clipped helper draws and783 scope/ID guards. It proves unchanged indexed bytes, one blit/one reset, both phases, densities4/8 and8←4 fallback, alpha and clipping, missing/invalid/classic/unsupported paths, huge/wrong IDs, player isolation, region-capacity fallback, cloud provenance, green-head→orb→smoke→foreground ownership and later original shadows. A disabled-render build also passes. LeakSanitizer is disabled under ptrace; address/undefined checks remain active.

Ground6107 checks, rotor101,573,120-pixel checks and cloud/green ordered-layer regressions pass. Fifteen strict fixture tests accept only exact reviewed source deltas before historical hash verification; unknown or duplicate edits remain rejected. All three archived families prepare, and current preparation restores the new hook/headers while retaining the existing read-only diagnostic observers.

This is finite episode1/physical-level9 coverage, not all49 emitter types, later levels, native Windows/GPU/fullscreen, physical2K or whole-level performance acceptance. Road candidates remain separate.
