# Bounded 60–75 second HD closure and cloud64 correction

Base: `805304fcf423f90d134711a633eacafb372c7f16`. This batch changes one generated cloud asset and its reproduction/proof files. Production renderer and gameplay source are unchanged.

## Coverage

The existing private-survival, no-weapon-injection/no-hit-control trace covers ticks2088–2609: **522 consecutive frames**,15.007512 seconds,103 visible-material identities and77,774 material references. All103 resolve to finite accepted bindings and current resources. Category counts:29 Layer1 terrain,14 Layer2 cloud,26 Layer3 terrain,26 enemy,7 effects and1 player identity.

This denominator excludes separate enemy-projectile112/113 calls and three additional offscreen terrain callbacks97/351/352. The combined material-plus-HD-call resource audit therefore checks108 identities. All82,372 logged HD calls are accounted for; success logging alone is not used to infer coverage. HUD/text and other unindexed paths are outside this material denominator.

Ordinary gameplay ends around tick1052. This continuation uses only the existing private survival guard; it is not ordinary full-level play. No restore-from-fingerprint claim, Windows acceptance or whole-game HD claim is made. The final tick2609 remains active; this video does not demonstrate destruction, drops or a full clear-tail.

## Cloud64 defect and bounded repair

The first full-window review found a bright ruler-straight cloud bottom at tick2178. Source/map inspection identified row438 cols7–11:63,64,64,64,65. Original64 has nearly flat opacity support but a strong dark-blue taper over its last3–4 logical rows; the prior HD fill stayed bright to that edge. This was an inherited authored-pixel limitation, not a new renderer bug.

The accepted correction changes only cloud64, still24×28 at8×, anchor0,0, slot199. Changed pixels lie within HDx1–190,y129–199. All four tile faces and rows0–127/200–223 are exact; all10 nonzero-facing joins remain exact. All14 other cloud tiles, including55/63/65, are unchanged. All other319 current debug-pack resources are byte-identical. Neighbor/source review covers98 static contexts; no larger cloud family redraw is implied.

Selected HDA SHA256:
`1f9378615e16157f59113a47066dd28a52433c28e5a36d8845491b355e64a3b8`

Generated-only addendum: `assets/hd/artwork/cloud64-v3`. It includes two authored inputs and a bounded C++ registration helper, with no original RGB or game files. Fresh standalone and relocated rebuilds reproduce exactRGBA/HDR1. PNG encodings may differ; committed PNG hashes and decoded RGBA are separately checked.

    python prototype/build-cloud64-art.py --output /absolute/new-cloud64-directory
    python prototype/build-cloud-art.py --output /absolute/new-cloud15-directory --data /external/licensed/tyrian2000
    python prototype/build-hd-assets.py

The full15-cloud builder preserves its accepted v2 reconstruction, then applies64 v3. All15 current HDR1 outputs verify. The full builder uses external original opacity geometry only; the64 addendum itself needs no original data. Current18 packs contain2872 HDA entries and328 active canonical PNGs, with316/320 resources in default preview/debug packs. Prior canonical files and original accepted cloud sources remain retained.

## Runtime and visual proof

- Ordinary early baseline/candidate0–1052: all state, materials, collisions, projectiles, effect/frame/presentation logs and444,080 original blend rows are byte-exact. Native2× ticks20/209 verify the repeated edge in the earlier accepted scene.
- Late bounded correction2118–2237: all original state/material/collision/effect behavior matches; all120 direct readbacks round-trip exactly through lossless RGB video. Only93 images change, strictly inside projected64 correction regions.
- Missing64: only its HD ownership/draw counts change to the original fallback. ProcessorType4 baseline/candidate are identical including RGB, preserving the original cloud BLEND route.
- Final complete0–2609 state/material prefix is identical to the pre-correction baseline, including2610 state rows and405,984 material rows. All522 rendered frames are healthy; no unmirrored supported calls, coverage mismatches, restoration errors or presentation RNG changes.
- Final actual640×400 stream uses density8 composition and nearest native2× presentation. Each of522 frames is directSDL_RenderReadPixels, independently decoded and matched to its originalRGBA/BGRA hash and noncapture RGB audit. No synthetic scrolling/interpolation.
- Complete prior522-frame visual inspection plus exact final-frame comparison:427 frames are pixel-identical; all95 changed frames2145–2239 were individually reviewed in native2× regions. Differences remain inside64's lower correction ROI; HUD is exact. The former straight bright cut becomes stable rounded/shaded terminations without a new seam, detached halo, dark stripe or flicker.

The moving craft, turret firing, energy orbs, gray island and purple installation remain readable and ordered. Minor established ground/backing texture-phase differences remain; no seamless/perfect claim is made.

## Evidence retention and limits

The superseded flat-edge stream is retained but is not delivered as the final accepted video. The corrected final delivery is labeled private survival with no weapon or hit injection. The old/new full streams, bounded correction and early stills together with delivery files total49,663,288 bytes, below50MB. No BMP/raw frame batch or deletion. Global retained image/video/raw/binary buffers were6.332GiB with about13GiB free at this checkpoint.

An early tick20 screenshot attempt hit the parser's minimum60 render-ticks and produced no frame; the private recorder was corrected to retain at least60 logic ticks. This setup failure is not a production change.

No CI result is claimed. Later windows remain unaudited until separately scoped.
