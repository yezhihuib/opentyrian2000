# Regular Missile Launcher: finite three-head update

## Scope and original behavior

Front port17 uses three static physical spriteSheet8 heads31/32/33. The narrow31 and wider-finned32 remain gray/silver metal;33 retains its copper/red finish and original left-shifted registration. All are12×14 logical, density8, anchor(0,0), in distinct slots333–335. They are upgrade designs, not animation phases. Original launch offsets, spread, acceleration, cadence, energy cost, collision functions, shadows and game pools are unchanged.

Source closure covers all33 power/table combinations across episodes1–3,4 and5. Child records12/13/14/16 reuse accepted20/21, white smoke135–141 and warm trails122–133. No22 is reachable. E4/5 substitute some simultaneous21 fragments and retain their original blast-filter difference. Source31 also serves special19 Missile Pod; its special-button route was not exercised. Latent records120/1120 may interpret30–33 as an animation in episodes1–3, but no supported named player acquisition was established;30 remains original. Enemy/shop paths and all other ammunition are outside this acceptance.

## Technical acceptance

- Four matched600-tick cases: E1 physical level9/P6,P8,P11 and E4 physical level3/P11. All2,400 frames per side execute the actual SDL software renderer. Natural collisions cover all four child records and E4 mixed20/21; no injected hits, resource refill or survival alteration.
- Twenty-three complete original-state streams and7,373,783 indexed blend rows match. Exactly9,497 normal31/32/33 calls gain HD;9,365 target shadow calls retain the original indexed path. No coverage/restoration errors.
- Missing31/32/33 affects only that head. All-three-missing matches baseline full RGB and raw blend proof. Malformed31 equals missing31. Classic and density4 missing-art old/new pairs match exactly.
- Portable ASan/UBSan binding oracle passes31,711 candidate assertions and31,531 baseline assertions, including boundaries30/34, wrong bank/layout, cache separation and prior Charge slots330–332. Existing Charge binding check also passes. LeakSanitizer is unavailable under this executor's ptrace environment; address/undefined checks ran with leak detection disabled.
- Generated-only source archive rebuild reproduces all three PNGs and HDAs byte-for-byte. Main asset verification checks18 packs,2,920 HDA entries,356 active source PNGs, four lower-world parts and two cap sidecars. Default pack counts340/344. Prior asset and material bytes remain exact.

## Presentation and fixture distinction

Four60-frame native2× windows cover E1/P6 andP8 at500–559, E1/P11 at240–299 and E4/P11 at60–119, plus three native4× stills. These weapon-isolation fixtures intentionally use `--render-scene-assets=off`; their backgrounds are original indexed graphics, not a production material regression.

Final delivery instead uses `--render-scene-assets=all`, the current default full pack and unchanged world materials: E1/P11 at240–299 with native4×245. Its600-tick baseline/candidate original-state and1,784,269 indexed blend rows match; all61 lower-ground and13 cap selected sources satisfy their existing bundle contracts. Every captured frame is direct SDL readback and verifies through lossless decoding. No gameplay interpolation or synthetic scroll is used.

Independent visual review passed all300 ordered native2× frames and the three native4× spots; every decoded frame matched direct readback hashes. This was exhaustive chronological frame inspection, not a claim of separate real-time playback. Exact receipts are recorded in the companion JSON. No full-arsenal, Windows, natural campaign acquisition, continuous4× motion or global clear-tail claim is made. Ongoing firing continues in these windows. Original grainy trails and indexed shadows are retained.

## Reproduction and retention

`python prototype/build-regular-missile-art.py --output NEW_EXTERNAL_DIRECTORY` rebuilds the frozen generated-only sources using ImageMagick and Pillow. The wrapper requires a new external output directory.

`python prototype/test-regular-missile-binding.py --candidate CURRENT_SOURCE --baseline SOURCE_AT_8542a2d --pack CURRENT_DEFAULT_PACK --out NEW_EXTERNAL_DIRECTORY` runs the portable finite sanitizer oracle. It does not run gameplay or require original game data. The baseline renderer must be the exact preceding source; its reverse-diff check deliberately rejects unrelated changes.

For gameplay use the existing documented legal-loadout fixture with front17, rear0, sidekicks0, the specified episode/level/power and600 ticks. Keep original licensed data external. Use `--asset-debug-reference`, `--render-scene=v1`, `--render-scene-assets=all`, density8 and `--render-no-capture`. Full observations should stream to lossless gzip and bounded blend-hash proofs; do not accumulate uncompressed repeated TSVs. Runtime media and original references are excluded from Git.
