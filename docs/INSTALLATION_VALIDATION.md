# Static physical installation125–128

Four exact newsh2 bases81,83,119,121 now use slots231–234 in the existing ordered enemy-quadrant path. Each is24×28 with anchor(6,7), density8. Together they form one opaque48×56 physical metal/ochre assembly with baked earth. These are static components, not animation or alternate destroyed states. Original order119,121,81,83, per-quadrant clipping, hit behavior, collision, linked destruction and foreground ordering remain unchanged. Only the finite mapping and asset capacity235 changed in production code.

The selected generated whole assembly and bounded earth correction are retained with prompts, identity, four formal PNGs and a byte-exact reproducer. Original references, captures and private fixtures are excluded. Default packs become232/236;18 packs contain2704 HDA entries and244 unique formal PNGs. All prior assets retain their bytes.

## Validation

- Natural original replay0–929 at actual4×/2×, presentation132–929:9,864 HD quadrant calls per scale,2,466 for each base. First/last rendered calls135/911. State/RNG/indexed, collision, effects, projectiles, materials and all prior scene rows exactly match the published baseline. Zero coverage/classic errors. Clear913–929 final RGB is exact.
- Actual three-placement views at232/456/764, native4×/2×, pass root and independent art review. Clouds and the accepted rotor remain in front; the second placement is partly obscured by clouds. A120-frame direct-render2× clip200–319 passes continuous review. All lossless frame hashes and noncapture state/RGB match. No synthetic scrolling. The clip ends while the installation is still active.
- Existing artificial-shot control diagnostic, separately labeled, uses original player-shot creation/collision at4×/2× without source hooks. Natural slots29–32 are types125–128/link21. Damage1 hits233–236 keep all16 quads intact; destroy29 at238 uses remaining armor9 and removes all four linked components by239. All320 state/RNG/indexed rows and52,424 material references match baseline. Every RGB frame239–319 matches baseline, including active explosions; effect pools are empty281–319. No residual pixels.
- These loaded types derive enemyground=false, so original nonlethal hits do not apply the ground-only palette flash. Normal hit/effect behavior is preserved; forced nonzero-filter support is tested separately by the renderer oracle, not claimed as natural behavior.
- Missing base119 at232–239 produces32 original quadrant fallbacks while each other component has32 HD calls. Missing all four at4× matches21 deterministic TSVs, including full final RGB. The oracle additionally covers null/missing/invalid assets, bad headers, unsupported sources/parts, classic density, clipping and reordered calls.
- Extracted production-code ASan/UBSan oracle:58,769,920 pixel comparisons,536 successful quadrant calls,105 guards. Existing ground/plateau, orb and rotor regressions and15 strict fixture tests pass. Formal four-PNG regeneration and all2704 runtime entries verify exactly.
- Actual cloud desktop4× window inspected paused232, resumed and exited0 at the finite240 bound. Windows/GPU/fullscreen/physical2K and whole-level performance remain unverified.

## Visible limitation and next terrain work

External baked-earth texture-phase joins are improved, not seamless. Original terrain323/324/333/334, especially the rectangular exposed top strip outside the48×56 footprint, remains visible and is a separate queued background family. This integration does not expand the object, feather opaque earth or alter foreground order to hide it. Roads are also a separate pending family.

## Reproduce on Windows later

Use the manifest's default_debug_pack and legal external game data. Run the normal executable with:

```
--data=<legal-data> --no-sound --no-joystick --no-xmas --asset-debug=custom
--asset-debug-tick=232 --asset-debug-running --render-ticks=320
--render-assets=<repo>/assets/hd/packs/<default_debug_pack> --render-test=local
```

Select2x or4x Integer scaling. Repeat targets456 and764 for the other placements. Keep captures bounded; original data and test media stay outside Git. Run `python prototype/build-installation-art.py --output <new-external-directory>` for exact formal PNG reproduction and `python prototype/fixtures/test-installation-enemy.py --sanitize` for the C renderer oracle.

Subsequent update: the separate terrain323/324/333/334 family is now integrated; see UNDERLAY_VALIDATION.md. The external texture-phase limitation remains, while the exposed original-resolution top strip is replaced.
