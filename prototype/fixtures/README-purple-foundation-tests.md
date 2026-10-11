# Finite purple foundation and selected-pack tests

These tests extract the repository's actual source functions and use independent
literal scope/pixel oracles. They do not launch the game, generate artwork,
modify production files, or publish. Reports and synthetic inputs are retained.
No private checkout or absolute environment path is required.

## Requirements and commands

Python3.9+, a C99 compiler with ASan/UBSan, and Pillow for the selected-pack audit.
Original game data is not bundled. Set `TYRIAN_DATA_DIR` to your licensed
Tyrian2000 data directory, or pass `--data`. Set `OUT` to an external report
directory. Commands below run from the repository root.

```sh
mkdir -p "$OUT"
python prototype/fixtures/test-layer3-purple-binder.py --sanitize \
  --data "$TYRIAN_DATA_DIR" --report "$OUT/purple-binder.json"
python prototype/fixtures/test-layer3-purple-alpha.py \
  --report "$OUT/purple-alpha.json"
python prototype/fixtures/test-layer3-purple-mutations.py \
  --binder-report "$OUT/purple-binder.json" \
  --alpha-report "$OUT/purple-alpha.json" \
  --report "$OUT/purple-mutations.json"
python prototype/fixtures/test-purple-selected-pack.py \
  --baseline 0044d19ca92f54f2160a3f773da22b6fcb64188c \
  --report "$OUT/purple-selected-pack.json"
```

`--source` selects another repository; otherwise source resolves relative to
`__file__`. The binder decodes level9's three lookup arrays directly from
hash-verified original level bytes. `--topology` and `--reference` optionally
supply independent JSON audits for additional cross-checks; neither is needed.
The selected-pack audit resolves both defaults and canonical PNG paths from the
repository manifest. Omit `--baseline` when Git history is unavailable; all
current artifact/hash/pixel checks still run, without a prior-entry claim.

## Independent coverage

- Exact13 terrain IDs150/156/157/158/159/160/166/168/169/170/176/177/178 map to
  slots290..302. Exact312 asset capacity and153 terrain registry capacity.
- Original map loader:91 pointers, including duplicate351 and every purple
  source. Synthetic213-slot overflow retains first153 without aliasing; later
  pointers fall back. Exact pointer identity, null, wrong bank/layer, UINT_MAX,
  map reset, and same-pointer first-binding precedence.
- All38 malformed-file cases; missing-all/each, malformed-member isolation,
 4x fallback, disabled guards and every non-NORMAL style class. Future entity
  slots303..311 and turret269..271 remain untouched by terrain-only tests.
-90 co-resident terrain assets,182 purple and252 mixed gray/purple full/partial
  rows with exact masks, coordinates, ordering and trace behavior.
- Actual NORMAL compositor, original indexed blitter and pixel callbacks at
 2x/4x/8x. Opaque, binary holes, fractional alpha, artificial transparent holes
  over opaque originals, allzero-alpha controls, clipping and guard bytes.
  Exact RGB, indexed bytes, selected flags and ownership metadata. Missing,
  invalid, null and unbound-source fallbacks;63 mixed pixel-level rows.
-23 deliberate mutations must compile and fail with real oracle/sanitizer
  diagnostics. Random process failures never count as caught faults.
- Default packs316/320: every file hash/header/size; all22 new canonical PNG/HDA
  payloads;13 fully opaque terrain cells and9 exact original sparse-alpha
  entity contracts. Optional baseline verifies precisely22 additions per pack
  and unchanged prior manifest entries.

Verified combined-renderer counts:433,512,512 binder assertions and932,258,673
pixel/ownership/indexed assertions. All23 foundation faults were rejected.
LeakSanitizer is disabled for the executor environment; ASan/UBSan are enabled.
Original purple cells are all opaque. Artificial alpha holes are compatibility
controls, not requirements for replacement artwork. These tests do not establish
runtime visibility, destruction timing or aesthetic acceptance.

## Optional entity negative-oracle checks

First run the full portable `test-installation9.py` fixture documented in its
README. Read `retained_work` from its report, set `ENTITY_WORK` to that directory,
and then run:

```sh
python prototype/fixtures/test-installation9-positive-control.py \
  --work "$ENTITY_WORK" --report "$OUT/entity-positive-control.json"
python prototype/fixtures/test-installation9-mutations.py \
  --work "$ENTITY_WORK" --report "$OUT/entity-mutations.json"
```

The unmodified native8 pass is a positive control for the faster mutant runs.
All17 negative mutations cover wrong bank/slot/base/anchor, pointer aliasing,
terrain169/entity169 cache collision, filtering, quadrant order/extent, original
indexed filter, original blit count, end count, and enemy-record immutability.
The full9×24×256/scales/wrapper suite remains authoritative; negatives narrow
only their execution to its unchanged native8 pass and full wrapper assertions.
