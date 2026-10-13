# Finite 50-credit red-copper coin family

This additive display-only family extends published commit
`8fc7a3b2638ed765d7aadc0a345d2c23cd036bfa`. The tested source candidate is
`e3ef8460783841dd0b1ed00ad3fa1823a3b7b8d2`. Source gates and the bounded
three-execution actual-engine matrix pass; final changes here are documentation
only. See the exact scope and limitations below.

## Contract

- Original record392, global bank11, small part0, bodies26..31; role116,
  keys1160026..1160031 and cache slots486..491.
- Original fixed newsh6:204 value50; role117, key1170204 and slot492.
  The asset array grows486→493. Each selected pack grows494→501 manifest
  entries; physical HDA count grows500→507, retaining six separate HUD bundles.
- Seven immutable density8 assets, 12×14 logical pixels, anchor(0,0), 96×112
  RGBA, 43036-byte HDR1 files. All seven must preflight or the entire50 family
  uses classic rendering. Existing25/75 decisions remain independent.
- Generated-only art and reconstruction inputs are retained at
  `assets/hd/artwork/cash50-seven-v1`. Inventory SHA256:
  `433d2e9e7748bd68fc7cfea808a1bfb0f9e9f03ff746022eb4f06f86b0dc2a67`.
  No artwork byte was changed by integration.
- A one-call display lease admits only original fixed/no-follow/zero-delta
  sprite203 with ttl≤8, drawn as204. Generic moving effect48 reaching204 stays
  classic. The lease is consumed on every entity call, including rejection,
  and cleared at frame begin/end. There is no global204 asset binding.
- NORMAL retains authored alpha. BLEND uses the existing continuous hue/value
  averaging then authored alpha. Original indexed RLE blits always execute.

## Preserved gameplay and original-source edge

No reward, constructor, allocator, collision, movement, RNG, event, difficulty,
mode, timing, game-data or build-membership change is included. Only
`src/render_mirror.c`, `.h` and one additive display hook in `src/tyrian2.c`
change in production. Removing only these additions restores all three files
byte-for-byte to the published baseline.

At the first selected time970 assignment, linked carriers13/14 can make two
separate record392 drops. Each allocation occurs before that carrier's release.
The second allocation can reuse the first carrier's just-freed slot. With an
initially full25-slot pool the first allocation fails and the second succeeds;
a final requirement that both former carrier slots stay vacant would be wrong.

The label is nominal50. Normal collection awards50; a linked collection awards
25 to each player. Original difficulty scaling and integer truncation remain.
The two carriers' separate25 rewards are not part of the pickup denomination.
Full effect capacity does not undo collection; fixed204 draws at most eight
frames and y187..189 is canceled at the original draw gate.

## Reproduce source-only gates

Use Python3, Pillow, NumPy, SciPy, a C compiler, and ASan/UBSan. The renderer
suite additionally needs the user's separately supplied original Tyrian2000
`tyrian.shp` and `newsh6.shp`; it pins their hashes before reading them. No
proprietary game data is bundled. Use fresh external output directories.

```
python3 prototype/build-cash50-seven-art.py
python3 prototype/test-cash50-seven.py --out /tmp/cash50-units-new --original-data /path/to/tyrian2000
python3 prototype/test-cash50-mutations.py --units /tmp/cash50-units-new --out /tmp/cash50-mutations-new
python3 prototype/test-cash50-original.py --out /tmp/cash50-original-new
make WITH_NETWORK=false
```

The new finite renderer harness reuses the unchanged published25 C oracle with
explicit family identifiers and capacity changes. Historical25/75 tests are
preserved unchanged. It checks all three families in both default packs,
all eight family-availability masks, 93 malformed/partial50 inputs, original
indexed transactions and ordered alpha/ownership overlaps. Tiny21-resource
fixtures suffice; no full pack is copied. Separate source receipts and their
limitations live beside this document. Those source checks alone do not certify runtime behavior. The separate
bounded actual-engine evidence below adds only its stated coverage.

## Bounded actual-engine and visual evidence

Exactly three executions used Episode1, physical level9, seed0x5eed, Normal
single-player story. The published baseline retained no images and froze the
observed schedule. Both candidate runs replayed identically through tick1089
(1090 logic ticks), below the1100 ceiling. Original demo input held RIGHT only
at20–34, then remained neutral. Original player movement settled at182/160.
The private fixture included the approved invulnerable-tick floor while alive
and one artificial original Pulse155 helper request at987. No player/enemy
movement fields were corrected, and there was no second shot or extra run.

Original linked carriers occupied slots25/26. Their ascending destruction
requested coin allocations before each carrier's own release. They produced
coins in slots31/25: the second coin reused the first carrier's released slot.
The separate carrier rewards were25+25. Original collision collected slot31 at
C1065, screen179/148, changing cash50→100 (+50 at Normal); sibling slot25 stayed
uncollected. The sibling's original offscreen removal at1087 and two clear
observations through1089 are trace evidence beyond the selected image window.

The original type37 effect occupied popup slot0, stored sprite203 and drew fixed
204 in BLEND exactly eight times1065–1072, TTL8..1. The last presented popup
frame is1072; first clear is1073, followed by a second clear observation1074.
Reusable slots are tracked by selected actor/effect identity, not by assuming
that every later occupant is the same coin or popup. Generic moving204 remains
classic by finite source and renderer tests. Linked25+25 per pickup and other
difficulty rewards are original-source unit results, not extra runtime runs.

Native2× retains exactly15 consecutive640×400 frames1059–1073. The collected
coin's body IDs1059–1065 are31,26,27,28,29,30,31, covering all six phases. The
original foreground occlusion and the pre-collection coin/value overlap at1065
are preserved. Native4× retains one1280×800 still1066, showing the popup and
sibling. Original state, RNG, indexed surfaces, collision, input/lifecycle,
shot and presentation streams matched across all three runs; the control stream
differs only in elapsed wall time. All186 selected candidate calls used HD:
78 collected-body,100 sibling-body and8 popup draws. The baseline remained
classic. No baseline RGB image comparison was performed.

Author review passed all15 chronological native2× target contexts and the true
4× still: coherent solid copper rotation, restrained rims, readable fixed
cyan50 against actual brown stone, legitimate collection overlap, clean popup
removal1073 and the continuing sibling. The independent technical release gate
is recorded in `technical-review.json`; the author gate in `author-receipt.json`.
`runtime-receipt.json`, `runtime-verification.json`, `frozen-schedule.json`,
`capture-index.json` and `evidence-manifest.json` pin the separate retained
evidence. Images and streams remain outside the repository.

This accepts only the controlled Normal story fixture with private survival
and one artificial Pulse. It does not certify unassisted/manual play, other
levels/difficulties/modes, bright-cloud contrast, arbitrary backgrounds, full
4× rotation/lifecycle, Christmas runtime, Windows/GPU/fullscreen behavior or
performance/FPS. No artwork, gameplay, production or test code changed after
the tested source freeze.
