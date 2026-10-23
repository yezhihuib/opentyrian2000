# NEWSHF HD compositor — explicit opt-in prototype

> Latest selected artwork policy: [168 V4 finite soft-alpha revision](newshf168-v4-soft-alpha/README.md). The previous binary-alpha revision and its receipts remain historical, not overwritten.

> Current art/pose revision: [corrected physical selection](newshf-fine-v2-corrected-poses/README.md). Earlier unchanged-art/pose claims below describe historical integration only; the first-two167/168 artwork assignments were subsequently found mislabeled and corrected.

This phase adds actual HD composition for the nine selected NEWSHF poses. It
supersedes the *deferred compositor* status of the earlier identity-only audit,
without changing that earlier prototype's scope or its historical test receipts.

Compile with `-DNEWSHF_HD_COMPOSITOR=1` and configure the existing global asset
root containing `newshf/newshf-role2100000-8.hda` through
`newshf/newshf-role2100008-8.hda`. This flag also enables the exact identity
observer. The default build and `RENDER_MIRROR_DISABLED` do not enable this owner.
An identity-only build remains an observer, not a compositor. Enabled prototype
hash checks are conservative and not performance-qualified.

## Finite scope and fallback

Only logical enemy bank 10 / NEWSHF, records 163, 167 and 168, with their three
selected poses each. There is no static `spriteSheet10` route, generic bank
whitelist, NEWSH2 alias, record824 route, new animation, level permission,
`mirror_enabled` or `manual_hd_scope` expansion. Native allocation, motion,
coordinates, collision, RNG, record bytes and indexed blits are unchanged.

The separate owner uses 24×28 composites, anchor (6,7), authored density8;
output density4 and density8 sample the selected pixels directly. The nine
resources load all-or-classic. Their finite IDs 2100000–2100008 are independent
of the fixed 120-entry global registry and existing material identifiers.
The selected PNG bytes and all pre-existing production asset bytes are retained.

Every quartet consumes the exact allocation/bank/record/pose witness and ordered
native quadrant submissions. Native pixel writes are observed, never suppressed;
filters and vertical clipping retain the original indexed semantics. Horizontal
physical-row wrapping deliberately remains classic instead of reinterpreting its
pixels as a clipped HD sprite. Transparent art over surviving foreign-owner
RGB also conservatively declines the complete frame, rather than borrowing an
unproven underlay lifetime; opaque overlap and ordinary indexed occlusion remain
supported. Partial failures reject the complete HD frame,
including NEWSHF RGB already transferred to another owner. Native post-draw
movement and filter reset are allowed; allocation generation, bank lifetime,
source shape and complete quartet proofs remain required.

Frame, source/final/output/canvas surface leases, palette, cached output, bank
reload/free, actor reuse, resource root and shutdown are independently checked.
Ordinary Present rechecks source and cached index/palette evidence. This bounded
prototype **declines all NEWSHF-provenance fades to classic**, even after another
owner has taken its RGB. It does not claim HD fade acceptance.

## Assets and reproducibility

`python scripts/build_newshf_hd.py build` deterministically regenerates the nine HDA
files and `src/newshf_hd_assets.h` from the selected phase-A PNGs. The exact
additive package extension retains the old 1,015 destinations and adds nine;
unknown consumers still fail closed. Mutable art revisions do not change
immutable original bank, record, palette, geometry or pose identity pins.

Validation results and limitations are recorded separately after running the
native production-path harness, compile/link modes, historical finite inverses,
current authoring and package checks. A harness is not an actual E1 playthrough,
Windows/GPU acceptance, installation, publication, or evidence all three families
were naturally encountered in gameplay. No original game binaries are included.

## Bounded verification result

- Native production-path test: **155 cases, 2,731,716 assertions**, including
  the final output RGB oracle, all nine poses at both densities, four filters,
  vertical clips, physical-row-wrap fallback, ordinary/low-detail/night output,
  native indexed equivalence, resource corruption/missing members, allocation,
  bank/source/palette/lifecycle/cache failures and bidirectional Talon overlap.
  Renderer, sprite, enemy allocation and harness run under ASan/UBSan; remaining
  linked game objects are optimized native code. Leak detection is disabled in
  this ptrace environment, not reported as passed.
- Both temporary negative controls are caught: removing bank integrity and
  removing the actual HD output store. No production guards are removed.
- Default-off, HD-on and mirror-disabled full native compile/link pass. The
  three default-off optimized translation-unit objects are byte-identical to
  the previously baseline-verified objects after debug stripping.
- Earlier identity test retains 24,594 assertions. Existing rotor/Talon helper
  composition retains 120 cases / 12,071,086 assertions with an explicit
  NEWSHF-disabled adapter; this shim regression is not native game proof.
- Exact source binding (259 files), package (1,024 destinations), current-art,
  40 package tests, 7 asset/closure tests, 13 phase-A tests, 12 pin tests,
  independent source/history guards and the 7,225-file historical inverse pass.
  Five existing current-authoring pipelines pass without changing 1,276
  runtime/source files. Existing historical fixtures remain unchanged.

A separate assisted cloud observation used the actual game loop, E1 physical
level8, debug-selected starting level, stationary/no-fire controlled input and
headless software SDL. Record163/base125 obtained its native witness at tick38
and retained HD output at tick42. The bounded 60-tick run completed successfully,
with unchanged RNG fingerprints around every Present. **Records167/168 and the
other poses were not observed in this gameplay window**; their coverage is the
native harness, not a natural playthrough. No installation, GPU/Windows test,
full campaign claim, laptop change, push or publication is part of this phase.
