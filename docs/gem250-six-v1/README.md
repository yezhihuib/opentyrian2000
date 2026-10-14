# Finite red/orange250 gem family

The reviewed source candidate39186dd945b8883ee6d21157644bda6b6c57770c is based on published4597e39c75b949d8f4e1f22bbc6117b432294132. Its bounded original-gameplay comparison passes: an image-free baseline,25 actual native2× frames and one native4× fixed250 popup still. See [RUNTIME-ACCEPTANCE.md](RUNTIME-ACCEPTANCE.md) and [runtime-acceptance.json](runtime-acceptance.json) for exact controls, hashes and limits.

## Finite display scope

- Original record395, actual global spriteSheet11 pointer, size0/part0 and bodies14–18 only.
- Five held brightness forms, never rotation:14,14,15,15,16,16,17,17,18,18,17,17,16,16,15,15.
- Fixed effect40 stores187 and draws the blue250 glyph188 for eight ticks. Moving effect36 may reach188 and remains classic.
- Roles120/121, slots499–504, capacity505. Original12×14 tile/anchor(0,0), authored96×112 RGBA at8×.
- All six exact resources must validate together. A missing/invalid member leaves only250 classic;25/50/75/100 and enemy-energy routes remain independent.
- Original indexed writes, filtering, clipping, draw order, NORMAL/BLEND operations, authored fractional alpha and gameplay are preserved.
- Normal/Christmas spriteSheet11 bytes are identical and both source/render paths pass units. The actual replay is explicitly no-xmas.
- Both current default packs gain exactly six files and entries:507→513 manifest entries and518→524 physical files each. Every prior payload/entry is preserved, including current type4/type15 contours.

Frozen generated-only artwork remains in assets/hd/artwork/gem250-six-v1. Inventory SHA256:e0b29e08ce061510940701831c259155d2fafdb9a7f146885d1ae549c8a5fc09. Body alpha is predominantly252/253 and popup alpha predominantly254, unchanged.

Only render_mirror.c/.h and the existing explosion loop's two-line display eligibility hook change production. Removing this exact gem delta restores current4597e39 byte-for-byte. The Data266 compositor fix, menu/selector typography and all other current source are preserved.

## Source and finite regressions

The current rebase passes both selected packs, all32 five-family readiness combinations,80 missing/malformed resource cases, exact alpha/BLEND/indexed ownership oracles, normal/Christmas positives,17 killed mutations and exact six-art rebuild. Original-source units pass14,764 scenarios and124,340 assertions per optimized and ASan/UBSan build. They cover original SKY carrier17/event15 and event33 assignment, allocation before release, full-pool omission, constructor RNG/copy, held16/+1 movement, strict collection, difficulty/linked shares, fixed40/moving36 and five-family isolation.

Both current Linux production builds pass with WITH_NETWORK=false:Release and RENDER_MIRROR_DISABLED. Current Data compositor4×/8× regression, settings/load/selector/pregame normal and sanitized units, and output sampler pass. Windows project/source inventory passes; no Windows build/runtime claim is made here.

PLAN.md, source-validation.json, unit-result.json, mutation-result.json, original-unit-result.json and the old source excerpts retain their historical93008cc/c92dc94 evidence. The original semantic fixture intentionally stays pinned to unchanged historical gameplay source; the current whole-source inverse separately proves4597e39 preservation. RESUME-4597e39.md records the rebase; runtime-acceptance.json records the completed current result.

## Reproduce non-game checks

Use fresh external output directories:

    python3 prototype/build-gem250-six-art.py
    python3 prototype/test-gem250-six.py --out /tmp/gem250-unit-new --original-data /path/to/original/tyrian2000
    python3 prototype/test-gem250-mutations.py --units /tmp/gem250-unit-new --out /tmp/gem250-mutations-new
    python3 prototype/test-gem250-original.py --out /tmp/gem250-original-new
    python3 prototype/test-windows-project.py
    make -j4

Original Tyrian2000 data and SDL development dependencies stay external. The private finite replay is evidence, not a production control or a general-purpose gameplay harness. No additional runtime is needed for this acceptance.
