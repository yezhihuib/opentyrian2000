Charge Cannon heads: frozen art pilot for bounded runtime trial

Exactly spriteSheet8 IDs252,253,254, three separate STATIC charge designs for option3 Charge Cannon. Charges0/1/2 use shot records101/102/103, damage2/5/10, vertical velocity-12/-10/-8. No trail, child, or phase animation is supplied. Shot record103 is not Poison sprite103. Original bank9 launcher bodies remain untouched. Latent unused records793/1793 are outside this acceptance scope.

Root approved this final rim-corrected pilot for a bounded runtime trial on2026-10-12 at07:02UTC. It is not runtime-accepted, and no repository changes or game captures were made by this art task. Final master/PNG/HDA paths and hashes are in candidate-manifest.json. generation-provenance.json records the built-in imagegen process and exact saved prompts. Earlier images remaining in the working folder are rejected review history, not selected assets.

The three final transparent PNGs are frames8x/shapes8-id252-96x112.png,253,254. They retain logical12x14, density8, canvas96x112, anchor(0,0). Alpha>0 footprints are252=[24,0,56,88],253=[16,0,56,88],254=[0,0,80,112]. These equal original occupied bounds at8x. Runtime HDA files are runtime/bullet-252-8.hda,253,254, headers HDR1+[80252/80253/80254,8,12,14,0,0], with byte-for-byte matching straight RGBA PNG payloads. No anchor exception from Pulse59 applies.

Selected generated masters:
- sources/stage0-generated-soft-edge-v2.png
- sources/stage1-generated-soft-edge.png
- sources/stage2-generated-soft-edge.png

All art edits used built-in imagegen. Production extraction is only the recorded whole-object crop, Lanczos resampling and placement. Generated alpha is preserved; no procedural painting, recoloring, alpha remapping, source-pixel tracing, independent-lobe shifting, or fabricated animation. Crops omit very low-alpha generated background speckles outside alpha>1 bounds. The original legal game images were references only and are not supplied in distributable ZIP packages.

Reproduce selected PNGs and HDA without original game data:
  python build_pilot.py --no-preview
Requires Python, Pillow and NumPy. The source ZIP includes only the three selected masters; earlier rejected masters are excluded. Complete prompt and provenance records are included. The unchanged candidate-manifest.json is the frozen authority; do not rerun finalize_pilot.py from a partial/source-only package.

Native comparisons are in previews/comparison-literal-2x.png and4x.png (Lanczos) and comparison-point-literal-2x.png and4x.png (nearest/point). These are literal-size offline alpha-over composites on dark, mid, light and checker backgrounds, not engine screenshots. They contain original reference pixels and are local-only; exclude from Git and shipped assets. Generated-only preview files are safe to include in the art packages.

Runtime visual review is still required. Inspect all three designs on both mounts at actual Integer2x and targeted Integer4x, particularly253/254 fine bright wisps for sparkle/aliasing, cyan-core readability and contour stability on cloud/terrain. Also inspect254's extreme right soft fringe: source artwork met its right edge; exported target edge atx79 has maximum alpha42/255 with no pixels beyondx80. Root froze this appearance for runtime trial; no further offline changes were made after acceptance. Preserve original coordinates, launcher bodies, shadows, gameplay, RNG, damage, collisions and fallback.
