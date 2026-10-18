# Rear Multi-Cannon P10 mode 1: six-shot fan

Baseline commit `82c0d3ec0e0750cab217b9d8dc94696a6def0daa`, tree
`a13405cc5ef168e7c5717c641cd32ac0923784b8`.

## Exact scope and source identity

The additional route is ordinary player 1, rear port 10 / bay 1, power
index 9 (display P10), mode index 0 (display mode 1), physical normal
record 263. The budget, cyclic period and repeat are 6. Its ordered raw
identities are 277, 278, 297, 296, 203, 222. Birth dx is -2, 2, 2, -2, 0, 0;
birth dy is zero. Velocities are (-9,-2), (9,-2), (9,2), (-9,2), (-10,0),
(10,0). Damage is 2, 2, 2, 2, 4, 4. The complete 80-byte record, including
unused tails, has FNV1a64 `b1df50f478068705` and SHA256
`76acbc332189f8509d212edc60ff06c015d3cfa44c0cd4457d20f3441edd03d8`.

Admission requires the original record-local mapping `op[0][9] == 263`
and the existing original-data and gameplay-scope guards. The byte-identical
physical alias 1263 is excluded, as are opposite-mode 274, later powers,
alternate banks and shared/generic/linked/shadow consumers. The existing
first-level scope is Normal physical 9 / Hard physical 15. The maximum
budget remains 7; prior budgets 261=6, 262=6 and 272/273=7 are unchanged.
There are now 19 routes, 83 canonical phases, 23 drawable identities and
25 observed source identities. IDs 163/164 remain pass-through.

Only the four `rear_multi_p1` core/header/pins/adapter production files
change. The other 153 top-level source files are byte-exact to the baseline;
including three vendored files, 156 other tracked source-tree files are unchanged.
Gameplay
coordinates, original allocator, damage, energy, cooldown, collisions and
indexed shadows are unchanged. A source-only reverse patch restores the
four files exactly to the baseline.

## New four-lobe art

Phases 277/278/297/296 reuse accepted art unchanged. Native bank-8 resources
203/222 have a 12x14 canvas and are exact horizontal reflections. Their
104 covered source cells form four lobes in rows 1-3, 4-6, 7-9 and 10-12.
A bounded exact comparison against 29 accepted source identities under
eight axial transformations and integer translation/clipping could cover
only 6 of 104 cells. It does not justify claiming an exact composition of
accepted art.

The new repository-native cubic vector family therefore preserves the
four-lobe semantics and accepted yellow/orange/red heat field, with an
inward 0.30-logical-pixel soft edge. It does not trace or enlarge the original
pixel staircase. Canvas, anchor (0,0), and occupied bounds [0,1,12,13]
remain fixed. Density 4 and 8 are rendered independently; canonical 222 RGBA
is the exact full-density horizontal byte reflection of 203. The package
records the small rasterizer rounding differences of standalone 222 SVGs
rather than treating those SVG rasterizations as the canonical payload.

Native 1x/2x/4x dark, neutral and bright previews were directly reviewed
before freezing. The two default packs each gain four HDA resources;
four source PNGs and a 28-file generated-only rebuild package are added.
Their catalogs increase from 617 to 621 entries with an exact inverse.
Existing art bytes are unchanged. The scoped package verifier and relocated
rebuild pass; sixteen relocated outputs match byte-for-byte. Original game
rasters, private comparisons and captures are excluded from the package.

## New baseline recovery and source tests

This batch uses newly reconstructed local evidence. Earlier private P9
harnesses and captures were not available in the replacement environment;
their historical published validation is not represented as rerun here.
The exact published baseline was restored without repository history.
Original inputs were obtained from the archive linked by the repository
README, safely extracted without running its programs, and compared with
the committed original-file and semantic pins. All five historically
recorded whole-file hashes and all 18 prior full-record / 23 source pins
matched. The new audit also validates exact 263 and both new source pins.

- All 18 strict core suites pass plain and ASan/UBSan, 36 runs. The P10
  ownership suite performs 2,857,331 checks per configuration.
- Actual allocator/adapter/decoder/loader-wrapper tests pass 9,566,877 checks
  per configuration, including 736 malformed resource variants. A separate
  synthetic zero-RGBA-pin fail-closed test passes 897 checks per configuration.
- Authentic-input checks pass all 19 full-record and 25 decoded source pins;
  all 99 extracted original files were independently rehashed.
- The original-source inverse, scoped art/catalog inverse and source-only
  rollback pass. The final uninstrumented candidate builds with the strict
  warning profile and local official SDL2 development headers.

The strict profile suppresses misleading-indentation, format-truncation
and missing-field-initializers warnings; this is not an unsuppressed-all-
warnings result. ASan/UBSan is not a LeakSanitizer qualification. Full
historical asset suites were not run from this deliberately sparse checkout.

## Actual offline compositor

The final frozen art passes 430 synthetic offline cases, 1,468 admitted
draws and 162 in-memory actual SDL native outputs. Both densities, all 15
phase pairs in both orders through separation, 32 mixed old-262/new-263
birth cases and 32 restoration cases are covered. Independent ordered
integer-alpha, ownership and restoration oracles agree; their targeted
mutants fail as intended. The actual source adapter, decoder, loader,
compositor and SDL software renderer are used without overriding production
art pins. These fixtures are not gameplay.

Two native 640x400 offline compositor outputs were retained and directly
reviewed: the bright-background six-head fan and a mixed-birth separation.
Four lobes, the warm palette and neighboring accepted heads remain readable,
without an observed black canvas fringe. This visual gate is separate from
actual-game runtime acceptance.

## One bounded actual-game pair

One newly reconstructed baseline/candidate pair completed the first Normal
level's initial 180 ticks at native 2x (640x400), using density-8 art and the
actual SDL software renderer with dummy video. Both processes exited zero.
There were sixteen emission-driven capture groups per process: ticks
4, 5, 6, 8, 11, 54, 55, 56, 58, 61, 114, 115, 116, 118, 121 and 179.
Each group contains classic, final-upload and actual SDL readback images;
this is 48 BMPs per process, not an unrestricted screenshot sequence.

The public render-test bootstrap uses demo mode and cannot qualify this
ordinary-only rear route. The new private copies instead drive normal SDL
menu and keyboard handlers through an actual P4 purchase. The original
`mt_srand(time(NULL))` call is unchanged. A launch barrier checks natural
seed/full RNG equality, and a second barrier checks the canonical player
and full RNG state after the purchase and at gameplay entry. Player pointer
relocation is checked separately. A disclosed private diagnostic changes
only the rear-power byte 4->9 at tick 0, 9->10 at tick 50 and 10->9 at tick
110. Before/after raw player bytes differ only at that offset, and full RNG
state is unchanged at each diagnostic. This is not ordinary P9/P10 purchase
or progression acceptance. Energy, cooldown, phase, movement, allocator,
collision and RNG rules are not overridden. Twelve genuine energy-rejected
requests remain rejected.

All 180 original state ticks and five original allocation/draw/birth trace
streams are pair-identical. Complete selected births at ticks 4/54/114
have the exact six ordered cyclic phases, original tuple and velocities,
and distinct original slots. Every eligible original normal 262/263 draw
is accounted for exactly once; no omitted or duplicate HD draws are hidden
by merely checking the phases that happened to be logged. All 688 new 263
HD draws retain exact birth/call/slot/phase identity and a stable nonzero
seal. The baseline keeps those same original 263 shots on classic fallback.
All 1,334 protected 262 HD draw rows match the baseline exactly. There are
113 old-262 draws across tick 50 and 89 old-263 draws across tick 110;
selection changes do not reclassify these retained births.

The per-draw independent integer-alpha/owner checks have zero errors.
All six new phases have sampled final opaque authored-pixel witnesses.
Old/new visible coexistence is witnessed at 55/56/58/61 and 115/116/118/121.
Every retained native SDL readback exactly equals the expected nearest
samples of its final upload. Full visible frame differences are confined
to the admitted 263 viewport rectangles; this confinement alone is not a
proof of the ideal interior composition. Full protected P9 upload/native
frames are pair-identical before P10 at 4/5/6/8/11 and after return at 179.

The original runtime analyzer is retained unchanged with 89 of 90 checks
passing. Its one failed check demanded literal unfaded artwork RGB to
establish the before-P10 P9 witness. Original startup effects at tick 8
have brightness -5 and filter_fade 1, so that demand is inappropriate.
An additive read-only check, independently reviewed, binds all six exact
admitted 262 owners to the unchanged captures and finds respectively
228/235/233/232/369/385 final native pixels inside their authored support
that differ from the classic image. Complete native/upload equality and
direct actual-size inspection establish visible protected P9 under this
fade. The failed result, original analyzer, binary, gameplay and captures
are preserved; no color normalization or replacement run was used.

Direct native visual review of 56/58/116 passes for those frames: compact
and separated four-lobe shapes retain the warm palette and bright cores,
coordinate with the diagonal heads, and show no observed black rectangles
or square bright cores. This is not a claim about every frame or background.
Acceptance combines the complete ordered offline compositor/restoration
checks, runtime exact per-draw and missing-draw accounting, original state
parity, final sampled visibility, SDL sampling, P9 protection and this
limited visual review. It does not reconstruct or prove an ideal entire
final frame for the new 263 route.

Both children have kernel-enforced soft=hard 512 MiB address-space limits.
Process outputs were 284,270,569 and 284,313,907 bytes at exit, within the
512 MiB/process and 1 GiB/pair limits. The free-space guard remained at
least 4 GiB; 29,169,156,096 bytes remained at process completion. There was
one gameplay pair and no gameplay rerun. Prelaunch rejected analyzers and
a compile failure are preserved outside the repository. Raw captures,
original inputs, private builds and diagnostic instrumentation are excluded
from the change.

## Reproduce and boundaries

```
python3 tests/run_rear_multi_p1_core_tests.py
python3 tests/run_rear_multi_p1_adapter_tests.py
python3 tests/test_rear_multi_p1_source_inverse.py
python3 tests/test_rear_multi_p10_mode1_inputs.py /path/to/tyrian2000
python3 assets/hd/artwork/player-rear-multicannon-p10-mode1-fourlobes-v1/verify.py
```

Core and adapter suites use synthetic inputs; the explicitly optional
original-input test requires a matching local copy. Art rebuild dependencies
and the fresh-output-only command are documented in the family README.
No original input, runtime capture or private diagnostic program is included
in this change. Actual Hard/4x, full-level/full-game completion, ordinary
P10 acquisition, later progression, every ship/resolution and Windows/GPU
acceptance remain outside this batch.

## Evidence seals

The private evidence is retained separately. SHA256 bindings:

- New exact-input audit: `bea3321355ee4e6843469ecda257b0dffb49322e206b613c0031d9d51c26abfc`
- Final source/input binding: `6bcf6fef002e01389abd6e60e61fd07f209d8e2020e6f9e6f6488c6d3e36d916`
- Uninstrumented candidate executable: `ab5c1311de851c31e3f915e15644c5392fe2b48d9e5a2eb95f25d52edfdb5b99`
- Source rollback receipt: `63ef71751162db1ae5731ad00acbda41c54ba21f784517a0e33b0f2184805cd7`
- Frozen art contract: `07e98e2c6af206d72ec19d6a62614b9d14c0966f0ed9b510993c75f26cca767c`
- Reviewed launch/input manifest: `a8c694b72dffda42640e39852b013e4960e40ca27caeeb7f38dd6222ee8b6d6b`
- Completed pair receipt: `9b0be5557538f13c0b3dbb5d7bfab479dbe41fb43566e9ec8d1d7ee5517001e5`
- Preserved original 89/90 runtime analysis: `d06187ef2ae411db693a7d3aac69f47657c70e784c86378a2a78bc702ee23ce5`
- Additive faded-P9 visibility receipt: `f0838a11eccdca7574106b650facc5d34f48338fdf04489a9ad6952efa924d6d`
