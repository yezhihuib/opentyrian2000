Pulse-Cannon: four missing HD player-head sprites, bank8 IDs58/60/62/165.

Root approved the revised actual2x/4x contact on2026-10-12 for runtime trial. Final in-game visual acceptance is still required. This does not claim that all weapon upgrades have HD coverage.

New frame58 is one pulse,60 is a three-lobe cluster,62 is the broad five-lobe cluster,165 is the four-lobe pair-of-pairs. Existing59 remains byte-identical and is included only as a review reference.

Each export is96x112 straight RGBA, density8, logical12x14, anchor(0,0), with one static binding and no invented animation. The current engine's(-1,0) anchor exception applies only to accepted59, not these new heads. HDA files have HDR1 plus six little-endian u32 header values and exact RGBA bytes.

All new artwork was made with built-in image_gen. Selected generated masters and the prompt set are supplied. Reproduce PNGs, HDA files, metrics and review sheets with: python export_final.py. Requires Pillow. Export applies only a recorded whole-sprite crop/resample/placement; it does not repaint, recolor, remask alpha, synthesize art, shift individual lobes, or alter shot tables.

The generated62 master arrived in a different aspect ratio and narrowed the cluster; its recorded whole-sprite horizontal crop restores the source's broad span before logical-canvas resampling. Frame58's whole-sprite height is registered to the accepted59 family. Internal painted highlights are not pixel-identical to the original indexed art. Check actual in-game registration.

Review/contact-true4x2x.png shows real4x and2x dimensions on black, lightgray and green. Review/alpha-true4x2x.png exposes actual transparency at those same sizes. These are offline source-over contacts, not runtime screenshots. A numerically low outermost alpha does not alone demonstrate perceived softness; the root's visual review assessed the corrected shoulders.

Before publication, require isolated legal Pulse-Cannon powers1/2/6/11, observed58/59/60/62/165 IDs, classic/HD/missing/invalid modes at2x/4x, correct nucleus/halo/color/origin/occlusion, and identical state/RNG/collision checks. Engineer is the only main-repository writer.

Original game data and original source bitmap references are excluded from both packages. All work stays in this isolated artifact directory; no gameplay capture batches or main-repository changes were made here.
