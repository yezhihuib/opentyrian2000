# Bounded renderer units

These tests extract production C functions and run finite isolated recorders under AddressSanitizer and UndefinedBehaviorSanitizer. They do not initialize SDL or the game, run events or combat, execute lifecycle branches, take screenshots, or establish native visual acceptance. No production file was changed by the tests.

## Binding and original-RLE recorder

Run from the checkout, with a fresh output directory outside it:

```
python3 prototype/test-boss-whole-family-binding.py \
  --out /absolute/fresh/external/boss-binding \
  --original-data /absolute/read-only/data/newsh4.shp
```

`unit-binding-receipt.json` and `unit-binding-log.txt` retain the passing result. Both selected default packs pass. Coverage includes:

- Every one of40 possible first members,40 allocation-failure positions, all40×4 parts×256 filter arguments, and all20 exact source-record/base pairings.
- All source type values0..1701 crossed with40 bases and four parts. Record1 cannot borrow the eight center images. Records470/473 cannot borrow boss bases86/124 even when their original small-cell indices overlap. Existing entry-six composite bindings still pass.
- Every16 combination of score-item/damaged/motion/static flags, availability0..2 and pool-slot `UINT_MAX`. These fields do not gate the family.
-520 resource failures:13 variants for each40 member. They include missing, magic, payload truncation, trailing bytes, alpha/RGB changes and every HDR1 field. Any single failure disables all40; no density4 retry occurs.
-160 actual on-disk mutation cases establish cached success/failure until a fresh cache reset. Every earlier finite family, including type3, is checked independently in both failure directions.
-633,600 physical-layout/coordinate cases, invalid format/layout cases over all40×4×256 filters, and integer extremes without coordinate subtraction or scaling on rejected calls.
-350,880 comparisons of unmodified original normal/filter RLE blitters against independently decoded linear-address writes for all43×4 source cells.100,929 cases differ from rectangular clipping, validating the classic fallback needed at physical row boundaries.15,209 logical opaque cells have exact8× alpha.
- Full earlier namespace/terrain traces are identical to baseline5629b3d in both packs. Every baseline `src` file other than the renderer is byte-identical, including `tyrian2.c`, `mainint.c`, `varz.c` and `entity_draw.c`.

The binding recorder checks call arguments and resources; it does not render final RGB. Gameplay-source equality is a preservation check, not executed lifecycle evidence.

## Actual extracted pixel unit

```
python3 prototype/test-boss-whole-family-pixels.py \
  --out /absolute/fresh/external/boss-pixels \
  --original-data /absolute/read-only/data/newsh4.shp
```

Both selected default packs pass. `unit-pixels-receipt.json` and `unit-pixels-log.txt` retain their results.

This harness executes the actual loader, family routing, draw, filter, ownership, original RLE and ordinary output-crop code, with independent pixel/index/ownership oracles. The exact ground-material eligibility function is also extracted with its bundle state enabled; role102 remains ineligible. The40 body assets and three empty audit assets are compared with original source masks and pinned approved outputs.

Per selected pack, it performs84,240 transactions:48,960 HD and35,280 classic. The test includes all43×4×256 filter routes,1,179,648 independent filter/alpha operator cases,600 ordered overlapping two-actor/four-quadrant sequences, mixed geometric HD/classic calls, and320 exact production crop cases. It compares every64-subpixel affected ROI and allocation/indexed-storage canaries for every transaction. Whole-frame RGB/index/selection/ownership comparisons occur periodically and at phase boundaries,2,047 times per pack; immutable under-layer state is checked at phase boundaries. Whole-frame comparisons are not claimed after every transaction.

LeakSanitizer is disabled; every harness and Asset allocation is explicitly freed. Unrelated material selection, font rendering and local-blend paths are fail-if-entered stubs. Neither pixel success nor original-source equality proves boss lifecycle, HUD visual acceptance, projectile closure or native presentation.
