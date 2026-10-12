# Type4 five-pose source integration

Status: approved V3 generated artwork, source/loader tests and bounded actual
cycle3340–3359 passed, including author review. One true4×spot at3348 also passed.
See [the compact validation receipt](ENEMY_TYPE4_VALIDATION.json) for exact scope
and evidence hashes. No full-level or Windows runtime claim is made.

## Finite binding

Enemy record4 uses dynamic bank1, `newsh2.shp`, with five complete24×28 composites:

| Base | Top left | Top right | Bottom left | Bottom right | Asset slot |
| --- | --- | --- | --- | --- | --- |
|159|159|160|178|179|369|
|161|161|162|180|181|370|
|163|163|164|182|183|371|
|165|165|166|184|185|372|
|167|167|168|186|187|373|

Each generated image is192×224 at density8. The composite anchor is6,7,
so its top-left is `(enemy.ex + tempMapXOfs - 6, enemy.ey - 7)`.
The engine retains its separate12×14 quadrant calls at offsets0/1/19/20,
including their order and original clipping. Do not crop or recenter poses.

The existing bank-identity route must resolve `newsh2`; coincident numeric IDs
in shapesZ or newsh4 do not bind. All1701 loaded enemy records were independently
read from the original table: only record4 uses these five bank1 bases, including
damage-form references. The terrain registry remains195 entries. All prior
renderer behavior and manifest entries are unchanged.

## Original behavior retained

The source20-tick sequence remains:

159,159,161,161,163,163,165,165,167,167,165,165,163,163,161,161,159,159,159,159.

The engine advances before drawing when x+map offset is inside(-29,300).
The endpoint159 holds six ticks across the loop. No animation scheduler,
movement, damage, collision, event, input, RNG or drop logic is changed.
First source eventtime2700 aligns with retained logic tick3300; these clocks
must not be interchanged when planning runtime validation.

NORMAL drawing uses the existing composite route and palette-filter helper.
Nonlethal hits and ice retain the selected pose and original filter timing.
There is no independent original shadow or painted hurt frame; the source's
dark craft pixels are retained within the binary occupancy masks. Death uses
the already mapped shared ground-large/small effects. Record default drop0
does not remove the conditional event45 arcade drops618/602/628.

Missing or invalid resources fail per asset through the established indexed
fallback. The pack contains no invented4× version. Existing render invalidation,
local palette-blend fallback and original indexed writes are unchanged; actual
interruption/occlusion appearance remains a runtime check.

## Reproduction and provenance

`assets/hd/artwork/type4-fivepose-v1` is an immutable copy of the frozen artist
package, plus `IMPORT.json` recording every imported file hash. Its generated
master, exact binary alpha masks, prompt history, contract and recipe reproduce
all five approved PNG/RGBA/HDR1 payloads without original RGB or game data.
The embedded `pilot-proof.json` retains its historical "unapproved offline
pilot" label; the later freeze README and import status identify the selected
V3 approval. The subsequent actual full-cycle author review passed without artwork changes.

Use the guarded public wrapper, with a new output directory outside the repo:

```sh
python3 prototype/build-type4-art.py --output /absolute/new/type4-rebuild
```

Optional read-only original-source checks add `--original-data /path/newsh2.shp`
and `--enemy-data /path/tyrian.hdt`. Neither source is copied or required for
artwork generation. The wrapper checks generated input hashes, exact approved
canonical PNG bytes, HDA headers/payloads, both default packs, original RLE
support, composition/anchor, timing order and absence from all other packs.
The normal aggregate `prototype/build-hd-assets.py` invokes this source check.

## Source and loader tests

```sh
python3 prototype/test-type4-binding.py --out /absolute/new/type4-binding-test
python3 prototype/test-type4-source-guards.py --out /absolute/new/type4-source-test
python3 prototype/build-hd-assets.py
python3 prototype/test-windows-project.py
make
```

The binding oracle extracts actual production helpers from the candidate and
pinned pre-type4 baseline (initiallyeec06f5; after the additive startup merge,
93de0fe4cb935f1d7cf7d737c86e0ff3f3f8c218). It reverse-checks the
two permitted renderer fragments, all preexisting checked-out files and full
manifest preservation. Exhaustive bank/base enumeration retains all55 prior
enemy bindings and adds precisely five. ASan/UBSan cover the20-step order,
four quadrant rectangles and common origin, header/anchor identity, original
filter routing and independent source namespaces. The actual filter helper is
also checked across all byte filters and brightness values.

All-present plus50 per-pose absent/corrupt cases cover magic, every header field,
truncation and trailing bytes. A valid old neighbor remains available in each
case. Disabled, invalid, density1, unavailable4× and scene-off paths retain
fallback. The source wrapper has17 rejected path/provenance/pack-scope cases.
The harness records draw calls; it does not render game pixels or establish
visibility. LeakSanitizer is disabled; AddressSanitizer and UBSan are enabled.

Linux compilation and all64 Visual Studio C source-list entries pass. The
aggregate verifies2996 HDA entries and394 canonical PNGs across18 packs; the
two default packs contain378/382 entries. These counts describe this checkpoint.

## Bounded actual acceptance

The original first spawn is at tick3300. A logs-only discovery through3360
selected the naturally occurring20-tick cycle3340–3359. Candidate4470694 and
baselineeec06f5 used the same original no-fire replay, seed, full scene pack and
private min2 survival control. No spawns, animation timing or inputs were added.

All complete original state/indexed/RNG and source traces match through3359.
Every native2×pixel outside all type4 rectangles and original alpha support is
exactly unchanged across all20 frames. Every opaque sample of the selected
actor matches the canonical artwork at the original anchor, establishing full
exposure of all five poses in chronological order. The true4×spot also matches.
All frames report zero coverage/classic mismatch and no renderer rejections.
Missing-family full RGB hashes equal the baseline; corrupt163 fails locally
while159/161/165/167 remain active. The author reviewed all20 chronological
frames and both normal-scene scales and approved without changes.

The type4 source-qualified callback count is280 over the cycle, with268 visible
quadrant references. Some additional offscreen instances have no visible opaque
pixels; they are not claimed as additional fully exposed actors. Paired control
semantics are exact, excluding the diagnostic wall-clock measurement column.
The4×spot retains full state/indexed/RNG comparison through3348; two hash-only
auxiliary traces have only the pre-onset prefix retained at that scale.

Natural hit/ice and death visuals were not exercised by this no-fire window.
The existing scene-hits observer tracks other enemy types and is not evidence
of type4 hurt coverage. Keep those limits, plus manual-input/fullscreen/GPU,
full-level and Windows acceptance, separate from this bounded approval.

## Sequential startup compatibility

Startup checkpoint93de0fe is included additively. All production startup source,
artwork, resource bytes and its manifest subtree remain exact. The original
startup package test pinned the gameplay manifest from before the already
published round inserts190/200. Its one compatibility assertion now validates
exact entries, header/payload/PNG hashes, complete family IDs/slots and the two
default-pack scope for190/200 and the five type4 poses, then removes only those
seven entries and their counts before checking the original historical hash.
Unexpected additions or changed old entries still fail. This repairs a stale
test assumption; it does not change startup or gameplay runtime behavior.
