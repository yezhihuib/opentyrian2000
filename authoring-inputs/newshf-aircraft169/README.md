# NEWSHF record169 three-pose HD art candidate

Cycle1 straight base79; cycle2 bank base77; cycle3 opposite bank base115. Left/right labels are deliberately not asserted. The registered masters are192×224 RGBA for the original24×28 quartet at anchor6/7. Smooth broad blue-gray metal planes, a few structural seams and independently generated dimensional banks replace the small aircraft’s dense-grid look.

Each pose was created separately using built-in image_gen. Raw RGBA sources, exact prompts, provenance and the deterministic registration recipe are retained. Run `python3 rebuild.py` with Pillow, NumPy and SciPy to regenerate masters, preview4x/8x and statistics. No procedural painting or transformed straight-pose stand-in was used. The adapted registration recipe is the existing record166 approach; record166 files were not modified.

Native masks are byte-identical to the audited source. Master pixels outside native support are exactly RGBA0, as are pixels behind alpha0. Originally occupied cells may become empty or partially transparent; the runtime must restore the verified underlay. The median visible alpha is253 in every pose (approximately0.7843% underlay contribution for those pixels). Per-pose coverage and alpha measurements are in stats.json.

Visual inspection covered the originals, all three raw generations, and both preview sizes. Major silhouettes and opposite bank appearances are retained within immutable support. No focused iteration was necessary. Rebuild checks reproduce all three master PNGs and generated previews byte-for-byte.

`preview-reference-comparison-8x.png` is PRIVATE: it includes original sprite thumbnails from the local audited game-data references and is not a publication deliverable. `PUBLISHABLE-ALLOWLIST.txt` is the legacy-named selective import list, not permission to publish; it excludes the private comparison. This directory is an art candidate, not runtime qualification or a public release. No long tests or natural gameplay were run for this art task.
