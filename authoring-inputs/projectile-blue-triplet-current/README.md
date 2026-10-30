# Blue-white enemy shot triplet — selected multi-source epoch

Normal bank8 selectors **101 / 120 / 139**, enemy role152, retain 12×14 native
canvases, anchor0,0 and internal density8 (96×112 RGBA). Weapon34 still emits
three separate shots in order101,139,120 with original vertical velocities14,12,13.
This is not a new persistent beam or player-projectile replacement. Native masks,
callbacks, coordinates, hit boxes, timing and production state/RNG are unchanged.
Christmas artwork differs and remains classic.

## Fixed generated sources and coverage

This v2 authoring schema closes exactly one source record for each selector:

* **101 V6:** generated1160×1355 full frame, fixed LANCZOS to96×112.
* **120 V4 registration:** generated V2 source1160×1355, fixed crop
  `(350,0,810,1355)`, LANCZOS to96×112.
* **139 original:** generated725×2168 shared-era master, unchanged crop
  `(224,1550,502,1870)`. Its master, registered PNG and HDA remain byte-identical.

Only generated pixels are used. Original colored pixels were viewed privately
for reference but are not included or consumed by rebuilding. The generated
masters retain their original C2PA provenance metadata; two source prompts are
historical build records, not instructions executed by rebuilding. No alpha
promotion, painted fill, native RGB sampling, crop search or endpoint copying.
RGBA is zero outside the immutable native masks and wherever alpha is zero.

`coverage-contract.json` pins every entry of each14×12 maximum-alpha matrix,
the exact PNG/HDA/payload, first/last-row alpha, and these distributions:

| Selector | Native mask cells | max alpha≥200 | 1..199 | Fully alpha-zero |
|---|---:|---:|---:|---:|
|101|164|132|26|6|
|120|168|107|61|0|
|139|130|130|0|0|

The six101 zero cells are zero-based `(row,column)`:
`(12,0),(12,11),(13,0),(13,1),(13,10),(13,11)`. They remain occupied native
callback/support cells. Their HD alpha is deliberately zero, not alpha1 fill;
correct rendering preserves the authenticated underlay while retaining the
native ownership/dependency protocol. This is a finite, exact selected-art
contract, not a blanket reduction of the native-mask or alpha safety checks.

**Erratum / epoch boundary:** the former one-shared-master, contiguous-crop,
adjacent-row seam-threshold and every-native-cell≥200 assertions describe the
old epoch only. They do not hold for selected101/120. The new closed schema and
exact matrices/payloads replace those authoring assumptions prospectively.
Old tests, FAILs and historical reports remain retained; they are not rewritten
as PASS, and old629 native/fresh/fullgate results are not transferred to new art.

## Deterministic finite rebuild

```sh
python3 scripts/build_current_projectile_blue_triplet.py --root .
python3 scripts/build_current_projectile_blue_triplet.py --root . --write
python3 authoring-inputs/projectile-blue-triplet-current/rebuild.py
```

The repository builder checks or writes exactly8 derivative products:
three registered PNGs, three HDAs, mapping and payload-pin header. The standalone
rebuild checks generated candidate PNGs and payload-pins.json; its explicit
`--write` changes only those four files. Both use Pillow12.3.0, fixed source
path/SHA/dimensions/crop/encoding and exact selected bytes. There is no stage/apply
subcommand or full package/inventory claim. The package transport revision tag
is retained for row compatibility; source cardinality is governed by v2 schema.

## Runtime and evidence limits

The existing enemy-only loader independently authenticates members and actual
used colors. Shared91/145/61 ownership uses distinct blue bits8/16/32; unused
missing/invalid members must not disable another member. Used dependencies
remain relevant to final/cache checks and ownership transfer. Native callbacks,
underlay rules, complete source guard and cached-palette checks remain unchanged.
A complete package requires all three resources; pure authoring tests do not
prove C runtime missing-member independence.

The selected-art observation at E3 physical1 tick1425 uses a **controlled
survival fixture with invulnerability2000**, not unmodified natural survival.
It does not authorize a production behavior change or claim collision/death
coverage. Per-shot geometry, supported-delta and the six zero-cell underlay
reads belong to separately bound runtime evidence; they do not themselves
constitute new cache-failure, native-suite or complete qualification.

## Selected-art fresh validation

The selected payloads were tested in a new, fully hydrated source epoch. Four
independent empty build directories compiled all **86 project translation units**
each: default HD-off, HD-on, mirror-disabled, and HD-on with ASan/UBSan. No old
object or executable was reused. The lifecycle executable used freshly sanitized
project objects plus a fresh renamed main and the real renderer/harness; external
SDL/system libraries remained native and leak detection was disabled. Three
ordinary builds retained compiler warnings; the sanitizer build, supplemental
compile/link and all three native runs had empty stderr.

The three native processes passed **629 cases / 12,208,831 assertions**:

* Original 107 + 157 cases: original source, input and stdout remained byte-exact
  (264 cases / 1,045,894 assertions).
* Selected-art 365 cases: 11,162,937 assertions, including full-tile straight-alpha
  oracles, all six blue draw orders, actual player-wrapper classic fallback,
  resource isolation, callbacks/wrap/reset and final/cache failure checks.
* The fixed 101 transparent cells retained all **384 samples** through draw,
  finish and cache in two native-underlay patterns and an actual 120 HD-underlay
  case. Used-resource/source/palette faults were applied only after valid real
  ownership was demonstrated. A later legal 120 write is checked against the
  composed final RGB, not incorrectly against an earlier 101 underlay.

At the separately fixed Talon geometry, actual authored-positive copied counts
were 101: **1,756** (1,721 soft), 120: **1,864** (all soft), and 139: **1,481**
(1,454 soft), in both final/cache variants. These are soft pixels of the blue
resources retained through native-covered transparent Talon pixels, not soft
Talon alpha. The six deliberately empty 101 cells are not claimed as transferred.

Fresh receipt SHA256:
`d7152087e826b6982bb06dc1053fa8a2c3ce7c79359dd4adfb6f34e0bb0dde38`.
This is a new selected-art native/fresh result, not a transfer of the old-art629
PASS and not itself the final whole-batch test gate.

## Controlled gameplay evidence and qualification boundaries

The final selected set was also captured at the same controlled tick1425 in
present, all-three-missing, and qualified61 variants. All **11 retained native
state/RNG/INDEX8/palette-related files** were byte-equal. Missing-blue images
matched the qualified61 images; present-image changes were nonzero and zero
outside the union of the unchanged native masks. Each selector retained nonzero
expected nonclassic RGB witnesses. These overlapping witnesses are not disjoint
causal attribution or proof of an exclusive final pixel writer.

Two actual 101 columns independently retained 384 transparent-cell samples each
before/after drawing and after finish, with authentic native/HD ownership and
used dependencies. Cached flags in that observation were passive reads, not an
additional cache-fault test; the new native suite above supplies the separate
active final/cache tests. Selected E6 receipt SHA256:
`58ee37c46530c3d9c5a5cd1485c65b77a04c4d5d4e69c4295835908f59f5b4c0`.
Its explicit selected payload header and all three HDA/PNG bytes match this
production source epoch. The original instrumented producer/input/code/image
and restoration references remain a separately frozen private evidence set;
those external experimental methods are not silently counted as final-gate tests.

All three gameplay variants used stationary/no-fire input and one tick0
invulnerability assignment from100 to2000. Invulnerability changes collision,
damage, enemy-contact and ship-blend behavior indirectly; equality is only
between variants sharing this controlled fixture, not with an uncontrolled
trajectory. Earlier ordinary stationary and moving/firing trials remain FAIL:
they had ended dead at terminal counters481 and542 respectively, before the blue
window (the exact fatal-hit ticks were not recorded). Zero collision/player-fire
rows mean only zero rows in retained tick0/1425 diagnostics, not whole-run path
coverage. Other native blend writes are not blue-projectile blend coverage.

Final whole-batch qualification uses its own frozen source/profile and complete
ordered test set; it is separate from these local native/gameplay receipts.
Any subsequent packaging/README/test-adapter metadata epoch records its exact
changes and preserves the original fresh receipt and producer bytes rather than
retroactively rebinding them. Original natural deaths, rejected art, old coverage
FAILs and the accepted art-budget accounting erratum remain retained.
