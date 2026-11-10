# Compound 309–312 HD candidates

**Not runtime-qualified.** Twelve 8x HDR1 resources, three generated masters and three assembly previews. No adapter, runtime manifest, accepted pin or launcher is modified by this batch. Resource names/identities are proposals for a later reviewed integration, not proof of in-game use.

## Source correspondence

NEWSHS bank: 46,566 bytes, FNV64 `f22ec1295ced5d11`. The exact archived `compound309270_native.inc` and `compound309270_asset_pins.inc` under `experimental/late-level/sources/03c5968bda89ae17` establish component sequences and callback order. Each 24×28 component uses native parts `[0,1,19,20]` at offsets `[(0,0),(12,0),(0,14),(12,14)]`. All 672 cells are occupied, so no transparency mask is needed.

Assembly quadrant order was independently checked against the private reference by comparing every source RGB callback at all 672 cells per component, not guessed from appearance. The three full images matched exactly at all quadrants. The top components have identical native contents across phases; their phase identities come from the archived sequences.

- Top left: record311, bases39/43/47, origin(0,0).
- Top right: record312, bases41/45/49, origin(24,0).
- Bottom left: record309, bases77/81/85, origin(0,28).
- Bottom right: record310, bases79/83/87, origin(24,28).

## Artwork and registration

Built-in image generation produced the smooth gray/brass industrial master, then two referenced state edits. Exact prompts are stored alongside the untouched generated masters. The private native RGB references and original game data are not included. All resource RGB is generated artwork.

The assembly is downsampled with Pillow LANCZOS to384×448, then split into192×224 components. Phase0 fixes the shared housing. Generated state pixels replace only the native phase-difference bounding rectangle `[15,38,32,53]` in logical assembly coordinates. This contains167 changed source cells, but uses a smooth rectangular region rather than copying the stair-stepped native difference mask. The final previews were visually inspected. Phase0 has a small white lower port, phase1 red charge, and phase2 a visibly larger open red aperture with bright right rim. Every final pixel is opaque.

This is a faithful art candidate, not a claim of exact runtime geometry or visual approval. In-game size, palette fit, event placement, timing and composition still require review. Native references remain private.

## Rebuild and validate

From the repository root (Pillow and NumPy required):

    python prototype/build-compound309-312-candidates.py --data /private/tyrian2000 --out /tmp/compound-candidates
    python tests/check_compound309_312_candidates.py
    python tests/check_compound309_312_candidates.py --data /private/tyrian2000

The optional private-source test rebuilds all bytes into a temporary directory and checks the committed candidates. The builder rejects the wrong bank identity or changed phase geometry. `candidates/art-inventory.json` records source/master/resource hashes, identities, phase and quadrant placements, and explicitly sets `runtime_qualified: false`.

### Safe reproduction contract

The shipped byte reproduction was verified with Python 3.12.14, Pillow 13.0.0 and NumPy 2.3.5. Other Pillow versions may encode PNGs or resample differently; run the byte-comparison test rather than assuming equivalence. No package installation or version change is performed by the builder.

Output must be a **new directory whose parent already exists**, outside both the private source directory and this artwork directory. Existing destinations, ancestor/descendant input overlaps and symlink paths (including ancestors) are rejected before writes. Every original/master read has a fixed byte-size limit and SHA-256 pin. Master PNG mode and exact dimensions are also checked before decoding. Native geometry validation uses explicit exceptions, including under `python -O`. Validation failures leave the destination absent and existing inputs unchanged. An I/O failure after output creation can leave an incomplete new output directory; remove that newly created directory yourself before retrying.

The standalone test now includes negative source-size/hash, master-size/hash/mode/dimension, native coverage/phase geometry, overlap, existing-destination and symlink cases. No source data is needed for these negative tests.

## Continuation review (2026-11-10)

All three original generated masters were retained after visual review.
`review-three-phases.png` is a lossless contact-sheet packing of the three
assembly previews. `candidate-pins.inc` lists the twelve proposed new runtime
RGBA pins. See `INTEGRATION.md` for the precise opt-in integration checklist;
these files do not claim the assets are loaded by the current game.

The validator now runs 12 tests, including exact record/base/phase/quadrant
mapping, every stored RGBA FNV, exact output file set, archived native animation
sequences, fixed housing, and all pairwise bottom-half phase differences.
Both normal and optimized Python runs passed full private-source byte rebuilds.
