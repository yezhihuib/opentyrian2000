# Audited first-30-second HD milestone

## Coverage

Episode 1, physical level 9, the fixed no-fire material trace at ticks **0–1043** contains **172,635 ordered references and 227 distinct (category, sheet, ID) identities**. All **222 nonempty identities** now have accepted HD art/bindings. The remaining **five identities are intentionally empty original shield tiles** (251, 270, 271, 273, 274): 95 rectangle references contain no occupied RLE pixels and remain no-ops.

Breakdown: 142 effect identities (137 painted and five empty), 28 enemy bases, five player poses, 37 layer1 terrain tiles and 15 layer2 cloud tiles. Multi-piece enemy/player bases can expand into several HD resources. These counts do not mean 227 painted PNGs, all HUD/text pixels, arbitrary uninstrumented blitters or the whole game. Enemy orb112/113 also has separate direct enemy-role proof (349 attempts); those attempts are not added to the material-index count.

## Integrated acceptance

The final native 2× preview contains every ordinary tick 0–1043, lasting 30.015 seconds. All 1,044 frames come directly from SDL readback, with one frame per original tick and no synthetic scrolling or frame interpolation. Lossless decode hashes match every readback frame; state and RGB audits match the non-capture run. The game viewport is 640×400; the delivery adds a 24-pixel label outside it. A real dot-cloud desktop window was also inspected at native 4× (1280×800 game area), tick1000, and resumed to the finite exit at1044 with status0.

The ordinary run sees only the bottom of tile114. A separate, explicitly labeled **private survival diagnostic**, ticks1080–1143 (64 native2× frames, 1.840 seconds), exposes its full geometry. It uses the same conditional invulnerability hook on both reference sides, original events/scrolling, and no hook in production. Every lossless frame and matched non-capture state/RGB row passes. An earlier attempted comparison selected an old green-injection fixture reference; it diverged at tick90. Correctly matched natural-preset references resolved that test-configuration mismatch without any production-code change.

Independent visual review covered all1,044 ordinary frames and all64 private-survival frames, with no obvious old-art flashes, missing components, foreground-order errors or flashing seams. The ordinary clip ends active; lifecycle clearing is covered separately below.

Final ordinary 4×/2× runs extend through1052, with exact original state and indexed operations versus the road checkpoint. Missing111/114 exactly restores its RGB. The highest-detail paired window preserves cloud style fallback. Source/asset freezing and focused sanitizer tests are in [TERRAIN_HOLES_VALIDATION.md](TERRAIN_HOLES_VALIDATION.md).

The current guarded green fixture additionally checks both scales and the same pack with only four heads214–217 and seven trail frames78–84 missing. Original motion, RNG, indexed drawing and lifecycle remain equal; full-versus-missing final RGB agrees after the last trail, ticks104–115. Original green shadows remain original. The original installation controls apply nonlethal hits at233–236 and a lethal hit at238; linked removal occurs239 onward. Final and road executables with the same final pack retain identical state, collision, effects and full RGB throughout232–319, including the revealed accepted physical underlay. Synthetic hit/reverse/filter diagnostics from earlier batches retain their explicit labels; they are not natural encounters.

## Accepted checkpoints

- `082f591ccc5e88f2f7d22f920c369a0ded381bcc`: Renderer/diagnostic foundation.
- `d1dcfbed7b464c25894b2ba167848ea9400d7c55`: Accepted ship, blue enemies, static turret/foundation and core effects resources.
- `9d52edfbb65af430db0b241875818f813ced1553`: White smoke and shield.
- `009eb6ffb3a2fca03c38e19a207381c2ae47e142`: Green heads/trail and scoped smoke compositing.
- `acbdf1b32f122f807f40b796aa9650601f64607d`: Orange/red energy59.
- `c4ed2c6d82fc3e1bd8752f231297b0d9b4396520`: Layer2 clouds and palette-aware shadows.
- `7a9f36c2a85889cfa41cf06fd342d5ef793254a1`: Physical rotor5/11 complete8-frame family.
- `ad22c26954fa8365820385d0bc24316cf5829358`: Nine brown ground tiles.
- `61d23fd08d15001038447ee1c37ba7ec8c5b7156`: Enemy-only energy orb112/113.
- `37b381577e17840510de5269d8290a5bdf6c365a`: Four missing plateau tiles.
- `b13d5c677565071da61be3353ac9f1f563ee65fd`: Static installation125–128.
- `1daf3f6d06dd01cfda1d0d7f5991f0e3ec147375`: Physical terrain underlay323/324/333/334.
- `71f53819927f8f84a60bc1158537b357c820ec58`: Nine remaining road tiles.
- This commit: final111/114 terrain and combined first-30-second acceptance.

## Remaining limits and intentional behavior

- Original HUD/text, empty shield no-ops, original green indexed shadows, unsupported/missing-resource fallback and high-detail cloud BLEND remain intentional.
- Dense smoke remains volumetric and mottled; energy heads retain the approved soft edge and scoped head-over-own-smoke presentation. Physical munitions retain their solid structure.
- Some earth texture-phase joins and tiny original-palette/HD ground-shadow floor differences remain documented. Finite tile repetition is still visible. No universal seamless-world claim is made.
- Static whole-map adjacency audits exceed dynamic coverage. Three cloud relationships and later/unseen terrain placements are outside bounded visual acceptance; the separate road late-area diagnostic did not reach every repeated47 row.
- This is a Linux dot-cloud software-rendered acceptance. Windows, GPU/fullscreen behavior, a physical2K display, whole-level performance, other player inputs, later levels and the rest of the game remain unverified.

## Later Windows acceptance

Build with `prototype/build-game.ps1`, verify `python prototype/build-hd-assets.py`, and select `default_debug_pack` from `assets/hd/manifest.json`. Keep legally obtained game data outside the repository. In a fresh run directory configured for Integer2x or Integer4x, run:

```
opentyrian2000.exe --data=<legal-data> --no-sound --no-joystick --no-xmas --asset-debug=custom --asset-debug-tick=0 --asset-debug-running --render-ticks=1044 --render-assets=<repo>/assets/hd/packs/<default_debug_pack> --render-test=local
```

Use the current `prepare-green-review.py` only for the explicitly labeled green fixture; do not substitute the archived historical `prepare-effects.py` output for production. The private survival video is not a production command. Keep any Windows captures short and bounded. No Windows test was performed after the laptop handoff.
