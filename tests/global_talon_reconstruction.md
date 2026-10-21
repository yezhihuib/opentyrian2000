# Talon13 reconstruction observer

This is a fresh, focused test of the reconstructed global Talon13 stage. It is not proof of a complete game run, GPU presentation, Windows packaging, or native player call-site integration. Parent integration tests exercise the native player wrappers and lifecycle hooks separately.

## What executes

The Python runner snapshots current source and compiles:

- The complete `global_talon_mirror.inc`, including the real resource loader and exact generated registry.
- Current production palette, alpha, shadow, source-decode, and upscaling primitives.
- The complete current `render_mirror_pixel` callback.
- The complete current blend callback and original `blit_sprite2_blend`. Accepted invulnerability tests execute four actual native blend tiles in original quadrant order and compare every resulting INDEX8 byte with an independent decoder.
- The complete current generic entity dispatch, with traps on legacy routes, to verify that migrated Talon quads cannot borrow a generic role or warm legacy cache.
- The complete current finish function, with a fatal upscaling sentinel, solely to prove invalid layouts return before unsafe composition or upscaling. Unrelated HUD/scene hooks are inert in this test.
- The feature-disabled public header in a separate compiled executable.

SDL surfaces are bounded structural shims, not real SDL/GPU objects. Normal and shadow original writes use an independent in-memory RLE walker and the real pixel observer, rather than the native normal/shadow blitters. This distinction is deliberate and recorded in each receipt.

## Exercised cases

- Thirty invalid semantic/player, operator, index, bank, source, palette, surface, configuration and reference cases, both before any resource load and after a valid warm cache. A valid pose alone must perform no resource I/O.
- All thirteen authored files independently missing, payload-corrupt, header-corrupt, or trailing-byte-corrupt. No partial family is admitted; selecting a valid root recovers. A root containing only Talon files works without any other global family.
- All thirteen visual positions at 4x and 8x with normal, invulnerability, and shadow operators. Full-canvas comparisons use independently loaded authored RGBA and independent arithmetic over mixed classic/HD underlays.
- Ordered repeated shadows, body/shadow overlap, same-index later writes, native blend INDEX8 identity, duplicate/missing/wrong-style/wrong-value/out-of-rectangle callbacks, and overlapping uncompleted transactions.
- Every painted cell in all twenty pinned original Talon tiles mutated in place, plus altered coverage commands, source-size/pointer replacement, reset, asset-root replacement, overlong root and feature/reference rejection.
- Per-player banking, repeated same-tick observations, tick advancement and gaps, increased invulnerability, and disabled interpolation.
- Scene-to-output mapping of x=24..287 into output x=0..263 and y=0..183, supported/unsupported output operators, exact final-cell mismatch, uncovered source writes, and final same-index pixel/rectangle retirement before and after composition.
- Relevant source colors, actual classic underlay colors and shadow shade colors, unrelated unused palette colors, pre-draw palette refresh, and foreign-HD underlay rejection.
- Cached output/source/palette invalidation and malformed or replaced source/canvas/output/final surfaces. Density mutation before a pixel callback, composition, or the actual finish guard must fail closed.

The recovered thirteen files have only alpha 0 and 255. Tests assert this rather than claiming authored partial alpha. Invulnerability exercises the real half-opacity operator, including alpha 128 for opaque source pixels.

## Running

From the repository root, with a C99 compiler available:

    python3 tests/global_talon_reconstruction.py --data /read-only/path/to/tyrian2000 --receipt /outside-repo/talon-plain.json
    python3 tests/global_talon_reconstruction.py --data /read-only/path/to/tyrian2000 --receipt /outside-repo/talon-asan-ubsan.json --sanitize

`--case` selects `guards`, `resources`, `alpha`, `source`, `pose`, `output`, `cache`, `underlay`, `transactions`, `finish`, or `role`; the default is `all`. `--assets` can select the exact authored global asset root.

Original `tyrian.shp` bank9 bytes and palette5 are read only, independently validated, and passed to the test executable on stdin. They are never written to a fixture, source, log, receipt, or image. Core dumps are disabled. Mutated resource fixtures contain only authored replacement files and are removed after each run. Receipts contain source/resource hashes, result text and the source-stability check, not original game bytes.

ASan and UBSan halt on the first error. LeakSanitizer is disabled because the executor uses ptrace. CPU time and generated-file size are bounded; this is not a general memory-exhaustion or allocation-failure campaign.

## Preserved regression evidence

Fresh receipts reside under `../reconstruction-checkpoints-20261020/global-talon-stage/`.

- `finish-guard-before-fix.json` preserves the first reproduced failure unchanged: active 4x legacy/global rendering changed to 8x and reached the upscaling sentinel despite a rejection flag. Its recorded renderer SHA256 is `dbef21c78955169e3629d8778cadac65d2c508249655d47fec57261b3e62d6e1`.
- `finish-guard-regression-pass.json` records the fixed early return across nine density/output/final-surface mutation cases, with no unsafe upscaling.
- Final plain and ASan/UBSan receipts record the exact current inputs, the full matrix result, and whether every input remained unchanged throughout the run. Earlier preparation and subgroup receipts are historical checkpoints, not substitutes for the final matrix.

The runner does not enable other global asset families, edit production code, modify authored replacements, or persist original assets.

## Native-alias, retained-cache and night restoration (2026-10-21)

The global source lease now follows the stable game_screen allocation, not the
mutable VGAScreen draw alias. Exact call destination checks remain mandatory.
Reset retires owned RGB before clearing proof bits. Fade capture, steps and
later final-index writes validate saved-buffer geometry, identity and separation;
the native integer palette progression is checked before retained RGB is read.

Night uses the actual native output kind and light coordinates, full palette
identity, pitch-320 source/final inputs, and exact complete final INDEX8 mapping.
It reuses the existing pure cone transform without borrowing any legacy level or
scene lease. Retained authored RGB receives one palette-anchored transform,
not a second alpha draw or repeated Present-time lighting. Independent tests
exercise all ramp levels and cone branches, extreme coordinates, 4x/8x,
normal/invulnerability/shadow, wrong mapping, palette, pitch and output kind.

The shared HUD's original blend-write observation is independent of the global
owner. A focused callback regression tests its ledger without resource loading;
real enabled HUD plus Talon tests are recorded separately in native evidence.
The HUD-only oracle still stubs global ownership and is not cross-family proof.
A deliberately revoked cached owner conservatively invalidates the combined
RGB buffer for that Present. The unchanged classic renderer is authoritative;
remaining valid owners may rebuild on the next frame. Same-Present preservation
of sibling HD is not claimed.
