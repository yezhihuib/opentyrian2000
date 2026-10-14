# Normal front Vulcan: two static tracer heads

Historical head-only checkpoint: `4e75dbda875922303fda92d514fe6d9755e40696`.
The coarse shadows described below belong to that retained baseline. The current
[finite shadow follow-up](player-vulcan-shadow-v1/README.md) has separate source and actual-runtime evidence.
Head-only binding-test commands below target that historical checkout; current
shadow tests are described in `docs/PLAYER_VULCAN_SHADOWS.md`.


This display change adds normal player bank8/TILE heads67 and70 to
role8 using the existing loader and compositor. Front port7 ordinary P1–6 uses67;
P7–11 uses70. The two frozen authored SVG tracer designs preserve a narrow
single/twin form, logical12×14, anchor(0,0), density8 and straight RGBA.

Only `src/render_mirror.c` changes production behavior: cache capacity524,
normal-only finite slots522/523, and explicit original indexed-shadow
preservation. Slots507–521 remain zero/unbound on this independent baseline;
separately staged rear and Data work is not included. The normal-data guard
precedes cache lookup, including warm caches. Christmas ice-blue originals,
shop/direct blits, enemy routes, original indexed writes and all gameplay
source remain unchanged. Missing or invalid files independently use the
existing8→4→indexed fallback; no family-atomic gate was added.

The binding is player-wide: Single Shot Option1, Satellite Marlo30, and rear15
charge0/1 share these heads. Their physical bodies and later charge stages,
linked rear fire, and ordinary rear Vulcan132/133/151/152 are not covered.

Both current default packs gain only `bullet-67-8.hda` and `bullet-70-8.hda`.
Each manifest count moves515→517. Each effective physical HDA count is521→523;
six existing unlisted files stay unlisted. Other16 packs and prior resources
are unchanged. Frozen inventory is in `assets/hd/artwork/player-vulcan-two-v1`.

## Verification and limits

- `prototype/build-vulcan-art.py` verifies inventory, SVG inputs, PNG/HDR1 bytes,
  canonical sources, both default packs, alpha/bboxes and exact source-only rebuild.
- `prototype/test-vulcan-binding.py` extracts the production loader, mirror,
  wrappers, RLE and compositor. Candidate and exact published baseline are tested
  against both packs with ASan/UBSan. Coverage includes normal/Christmas cold and
  warm cache, original shadows, finite wrong-role/bank/layout/neighbor paths,
  independent missing/invalid resources,8→4 fallback, straight alpha, ordered
  overlaps, clipping, indexed/RGBA padded pitch, ownership and blend restoration.
- `prototype/test-vulcan-original.py` independently decodes original item bytes
  and executes exact shot-creation/movement functions plus the main-weapon cadence
  block. It covers11 powers in all3 table groups, two phase cycles per row,
  mouse-drift clamp, static frames, acceleration, lifetime decrement, screen exit,
  conditional shadow order, held/released fire and power failure. E4/E5 retain
  blast filter112; E1–3 retain208. Power/pools are unit-owned fixture inputs.
- The renderer also compiles with real retained SDL headers under strict syntax
  checking. These implementation-stage checks did not build or launch the full game;
  later bounded engine evidence is recorded separately below.

Original `.shp`, item tables, decoded fixtures, raw output and captures remain
outside Git. Receipt copies in `vulcan-two-v1` contain hashes and bounded results,
not original game data. The receipt copies are historical source/unit evidence only. Subsequent
[bounded native 2× P1/P7 engine checks and review status](player-vulcan-two-v1/README.md)
are recorded separately. Natural acquisition, shared-option/rear live use,
other episodes, long motion and Windows/manual acceptance remain outside those
cases. Publication is separate.

## Local invocations

Use a new output directory outside this checkout for each test. The legal
original data and audit packet are caller-supplied retained inputs.

```sh
python3 prototype/build-vulcan-art.py
python3 prototype/test-vulcan-binding.py \
  --candidate "$PWD" --baseline /path/to/published-ee2b90cf \
  --art "$PWD/assets/hd/artwork/player-vulcan-two-v1" \
  --original-data /path/to/tyrian2000/tyrian.shp \
  --xmas-data /path/to/tyrian2000/tyrianc.shp \
  --source-packet /path/to/front-vulcan-source-packet.json \
  --out /path/to/new-binding-results
python3 prototype/test-vulcan-original.py \
  --original-data /path/to/tyrian2000 \
  --source-packet /path/to/front-vulcan-source-packet.json \
  --out /path/to/new-original-results
```

The SVG rebuild requires Node.js and `sharp`; image checks use Python/Pillow.
Source units use a C compiler with optional platform sanitizer availability.
