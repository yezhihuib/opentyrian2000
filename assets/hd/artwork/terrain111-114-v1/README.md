# Complete terrain111/114 in the bounded level9 scene

Two distinct authored ground identities:111 is a larger brown stone cluster with interior gaps;114 is a charcoal-gray physical boulder on warm brown earth. They are not aliases of accepted101. Full-map source audit found28 and8 placements respectively;33 canonical cardinal pair types/140 unique actual edges touch them. One side lies outside the map. The full36-placement neighbor context was inspected before drawing. This is a two-ID update, not a new whole-game rock family.

## Finite integration

Base: published `71f53819927f8f84a60bc1158537b357c820ec58`. All107 production source files of the private baseline and249 pack resources match this immutable checkpoint exactly. Slots111=241 and114=242, asset capacity243, terrain registry113→115. Preserve all road, cloud, plateau, installation and underlay assets. The included finite binder patch applies directly. No renderer, alpha-compositing operator, palette, shadow, gameplay, event, map or scrolling change is required.

HDA contract:172060 bytes; `HDR1`, then six little-endian U32 values `[2010000+ID,8,24,28,0,0]`, followed by192×224 straightRGBA. Logical24×28, anchor0,0. Manifest records every PNG/RGBA/HDA hash. Unknown/missing/invalid resources keep original fallback.

## Source ownership and exact reproduction

Each central tile was drawn with built-in imagegen in its exact3×3 original-map context, preserving the larger111 stones or gray114 boulder and using frozen101 material as reference. Only the authored central crop is included. The full masters retain unchanged original context and remain private. Master hashes, registered576×672 size and exact center crop `[192,224,384,448]` are recorded in source/crop-provenance.json.

The author-created crop RGB receives the required source-layout silhouette before edge processing. This constrained silhouette is baked into the included authored RGBA source. No standalone original binary-mask, raw palette/index data, original sprite or reference image is included. Included RGB is the newly generated artwork, not original-game raster colors.

Rebuild requirements: Python3 with Pillow and C++17. Set `TYRIAN_HD_BASE_PACK` to the accepted road-aware pack containing the exact13 dependency HDAs, and run:

    bash rebuild-selected.sh /absolute/new-output-directory

The native edge registration writes only111/114. It uses a32-HD-pixel harmonic inward RGB correction; frozen edges take priority, without extruding high-frequency edge differences into false ridges. Frozen context has intrinsic differences, leaving at most11RGB residual on a few boundary texels. Full outer perimeters remain opaque. No accepted image is changed.

##111 interior-hole visual alpha contract

Original111 has88 transparent logical pixels, corresponding exactly to5632 zero-alpha HD subpixels. Every one remains zero. Every originally occupied HD subpixel remains nonzero. Original indexed writes and occupied logical coverage remain exact.114 retains its original nine logical holes,576 zero-alpha HD subpixels, and completely binary alpha.

A direct binary88-hole upscale produced conspicuous small right-angle cuts in the new detailed111 stones, including in actual2× output. The selected111 therefore softens only the occupied side within0.5 logical pixel of each interior hole. RGB is unchanged by this alpha step; outer edges remain255. Precisely5090 occupied HD subpixels become fractional alpha. This is a bounded visual alpha change, not a claim of bit-identical full alpha.

The native `feather_occupied_alpha.cpp` finds the Euclidean distance d between an occupied HD pixel center and the nearest original zero-alpha HD pixel center. Let t=clamp((d-0.5)/4,0,1). Selected alpha=max(1,round(255*t*t*(3-2*t))). Original zero pixels bypass the operation. The4-HD-pixel denominator equals0.5 logical pixel at8×. Every zero/nonzero support bit, all original holes, every RGB channel and the opaque perimeter are preserved. There is no whole-image blur, outward hole fill or renderer change. At4× some structural turns of the original holes remain recognizable; the result is not described as geometrically round everywhere.

## Runtime and motion evidence

- Finite binder/loader ASan+UBSan:10,003,527 assertions, including missing/malformed resources and partial-alpha byte transport.
- Extracted unchanged production compositor ASan+UBSan:11,280,530 assertions covering actual holes, underlying RGBA/ownership, fractional occupied alpha, normal/shadow modes, clipping and native2×/8× processing.
-106 other source files and53 original render/entity function bodies remain unchanged; four private builds succeeded with the same inherited warning signatures.
- Ordinary baseline/candidate2× runs0–1052, ending naturally; identical original state, materials, effects, blends, foreground and prior scene commands. Both new IDs are NORMAL/HD;114 is only partially visible in that ordinary run. Zero coverage/classic errors.
- A clearly labeled identical private synthetic-invulnerability continuation0–1150 exposes114 fully from1064. Its original state/material/effect/foreground logs remain equal between both sides. Only the existing private test-pilot survival hook is used; it is not in this production patch or package.
- Real2× scrolling:111 ordinary930–1049 (120 frames),114 diagnostic1064–1143 (80 frames). Every frame comes directly from the actualSDL readback, once per original tick. All200 frames per side match their lossless decode hashes. HUD/bottom are byte-identical; all before/after differences are confined to111/114 tile rectangles, zero outside.
- For the unobstructed111 at physical map r259/c3, aligning all120 actual frames by logged tile position produces exactly oneRGBA hash. Maximum temporal RGB change at the softened edge is0; no old-base drift or edge flicker was observed in this bounded sequence. This is not a guarantee about every map placement or all rendering modes.
- Actual4×/2× tick1000 was inspected; internal RGB audits are exact over998–1001 and original state over0–1001. Longer production-scale/missing/highest-detail regression belongs to the engineer's merged integration check, not an invented all-scale art claim.

The full36 map contexts are static coverage. Earlier broader road diagnostic logs observed25/28 cells for111 and7/8 for114; only5 of those114 cells were fully on-screen. Unseen or clipped placements were not described as visually tested. The two short final clips use bounded current regions only.

## Exclusions and rollback

Original data, standalone source masks, user screenshots, original reference PNGs, runtime media, private executables/capture hooks, synthetic-survival patch and the binary-hole diagnostic candidate remain outsideGit. All rollback artwork and evidence is preserved. No subsequent background family is started until the combined first30-second milestone is integrated.
