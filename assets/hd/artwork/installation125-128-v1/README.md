# Physical installation125–128

One opaque48×56 generated assembly, split into four24×28 components at8× density. Bases81/83 form the upper row,119/121 the lower row; each retains anchor(6,7). Original draw order is119,121,81,83. These are static physical components, not animation or destroyed-state variants.

Selected generated source: earth-corrected-assembly.png. The two prompts document whole-assembly generation and the bounded earth-only correction. export_final.py scales the shared canvas once and splits it without per-component registration. prototype/build-installation-art.py reproduces the four committed PNG files exactly; no original game data is needed. Intermediate whole-canvas and individual tile outputs are verification artifacts only.

The baked earth remains fully opaque. External texture-phase joins are improved, not seamless. Original terrain323/324/333/334, including the exposed row outside the object footprint, remains a separate pending background family. No object footprint expansion, alpha feather or foreground reorder hides that limitation.
