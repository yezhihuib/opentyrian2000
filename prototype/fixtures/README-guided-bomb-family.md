# Guided-bomb family finite source/binder/RGBA oracle

Baseline: `3f05b84b6b63141f9f7ce3bc3b7e9399ccbb4b8e`.
The entire production edit is `assets[326]` → `assets[330]` and the finite
player `spriteSheet8` + `ENTITY_TILE` binding `19/171/20/21` → `326/327/328/329`.
The existing 65536 region budget, all other renderer bytes, and all 106 other
source/header files must remain byte-identical. No capture hooks are permitted
in the formal source-scope check.

All four assets retain logical size 12×14, anchor (0,0), ordinary straight-alpha
and shadow handling. 19 and 171 are physical parents. 20 and 21 are independent
static shared fragment/Widget sizes, not animation frames. Frame22 remains
unmapped, uses its normal indexed fallback, and must not disable the frame or
prevent subsequent20/21 draws. No blanket disable or new rejection is added.

## Run

Requires Python3, Pillow and a C99 compiler. No game process, network, SDL,
original game data, or capture is needed for the portable default checks.
Rebuild the frozen art from its clean source archive into an external directory.
Combine the unchanged334-file debug pack with exactly the four new HDA files
for the338-file candidate. The original334-file pack is the all-four-missing
baseline. The fixture pins both file inventories and every previous file hash.

```sh
python prototype/fixtures/test-guided-bomb-family.py \
  --source /path/to/finite-candidate-source \
  --art /path/to/guided-bomb-family-v1 \
  --assets /path/to/candidate338 \
  --baseline-assets /path/to/baseline334 \
  --sanitize --mutations \
  --report /path/to/guided-bomb-family-result.json
```

The art input needs the immutable candidate manifest, its four selected masters,
and the exported PNG/HDA files named in that manifest. Earlier rejected20/21
masters are not used. No original sprite reference images are needed or copied.
The pinned manifest SHA256 is
`3215fbd2d733e592da92fb46e23152460035c07b94f161944a5b879a78954f20`.

The optional argument below additionally checks the external source-audit
closure for99 guided configurations and33 Widget configurations. This evidence
contains original decoded table records, so keep it outside the repository.
The fixture reads it without modification and emits summary counts and its hash;
it never copies the records into its fixture, JSON report, or source package.

```sh
  --source-closure /external/guided-bomb-source-audit/independent-closure.json
```

## Coverage

- Six bank identities, three layout values and IDs0–599, against an independent
  old/new registry. Cross-bank numeric collisions and unrelated layouts cannot
  acquire the new assets. All previous slots remain fixed, including103→325,
  Pulse321–324, and59's exceptional anchor(-1,0).
- Frozen whole-object master crop/Lanczos resize/placement independently rebuilt
  and compared to actual straight RGBA bytes, PNG and HDA hashes. Headers must be
  exactly80019/80171/80020/80021, density8, logical12×14 and anchor0,0. All334 old
  HDA files remain byte-identical; exactly four additions are permitted.
- Each of the six header words, magic, short/trailing payload, real missing file,
  explicit invalid/missing/1x gates, cached misses and8→4 authored fallback.
- Every target independently missing from a physically distinct337-file pack.
  Other new targets,103,59, green214–217, and parent/child smoke still draw with
  normal flags. All-four-missing334 retains Pulse, green, poison, smoke and
  enemy112/113. No global renderer disable substitutes for a real missing file.
- Actual RGBA and synthetic alpha0/1/17/63/127/128/191/254/255 independently checked
  at output2×/4×/8× in normal/shadow modes, on classic/HD ownership, with normal,
  negative/clipped and bottom-right-clipped origins. Padded pitch is guarded;
  ownership, cloud and green bookkeeping must match each pixel's coverage.
- The unchanged production `draw_entity_sprite2` boundary is extracted and
  executed. Recorder blits prove exactly one indexed draw with the same
  bank/index/style/layout/origin after either successful HD output or fallback.
  This is a call-boundary oracle, not a decoding of original indexed art.
- All11 static Widget patterns exercise20/21 and ordinary22 misses, including
  an immediate22→20→21 sequence proving the miss cannot poison later output.
  Enemy bank8 remains its separate exact112/113 route. Green head compositing
  and green-only shadow exceptions do not expand to the four new identities.
- Real source setup/frame statements and normal/shadow origin statements are
  compiled in a separate bounded equation harness. Active positions1–8, chain
  thresholds, spawn offsets, TTL0/1/4/8/98/99/100/101/119/120/121/122/255,
  animation lengths, last admitted TTL tick and shadow guards are checked.
  The collision reset→logical-origin child spawn→parent removal sequence and
  all gameplay source bytes are pinned unchanged.
- With the external audit: each guided parent and child is independently
  re-derived from active raw slots, including shot28's zero-damage visible
  positions5–8. Parent filters208/80 and child112 remain metadata. Every guided
  configuration excludes22; Widget shots738–748 are static and powers8–11
  legitimately use22 alongside shared20/21. No inactive legacy tail bytes are
  treated as reachable patterns.

`--mutations` requires16 renderer/entity and five source-equation negative
controls to reach genuine oracle assertions. They cover capacity, absent/wrong
bank/layout/slot bindings,21→22 expansion,20/21 swap, origin, expanded enemy
scope, opaque alpha, wrong shadow alpha, expanded green layers, shadow bypass,
missing-parent cascade,22 poisoning the frame, skipping original indexed draws,
and chain/animation/TTL/spawn/draw-order equation errors. Setup or compiler
failures are not accepted as killed controls.

All production helpers are extracted without modification. Temporary test
files and generated C are retained in reported work directories. Sanitized main
binder/pixel tests use ASan/UBSan; LeakSanitizer alone is disabled for executor
ptrace. Mutation builds intentionally use ordinary diagnostics.

## Boundaries

This suite establishes a narrow source/binder/compositor contract. It does not
claim actual game visibility, naturally realized collisions, complete shared-user
runtime coverage, timing/RNG parity, Windows acceptance, visual approval, or
publication. Those require separate bounded runtime evidence.
