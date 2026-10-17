# Rear Multi-Cannon P9 mode 2: seven-shot fan

Baseline commit `be3df38ee5b7c64627c86e0630faa894a8ee0f1e`, tree
`e798190fc72eef8d6bfc25b2770f21fb80dc1a24`.

## Exact admission and lossless art

The new route is ordinary player 1, rear port 10 / bay 1, power index 8
(display P9), mode index 1 (display mode 2), physical normal record 273.
Budget and cyclic period are 7; repeat remains 6. Phases are
277, 278, 295, 294, 77, 298, 299. Birth dx is -2, 2, 4, -4, 0, -4, 4;
birth dy is zero. Velocities are (-9,-2), (9,-2), (6,6), (-6,6), (0,10),
(-2,9), (2,9). The exact full-80-byte record has FNV1a64
`df6661ef4d03f02b` and SHA256
`162d5ec2a1f10a5fb68f1eca339884a9898cc2b9af011a3de6af67817024f869`.

Record-local `op[1][8]==273`, opnum 2 and poweruse 40 are required.
Physical alias 1273, wrong selectors, later powers, alternate data,
Christmas banks and generic/shared/linked consumers remain excluded.
The first-level scope remains Normal physical 9 / Hard physical 15.
Indexed shadows and the gameplay allocator are unchanged.

New generated 298/299 use exact full-density coordinate permutations of
accepted generated 277 at d4 and d8: 298 maps (x,y) to (y,14d-1-x), and
299 maps to (12d-1-y,14d-1-x). The same geometry is independently proved
against every authentic original index and coverage cell. Original pixels
and masks are not copied into the generated art package. Every supported
RGBA sample, alpha sum and premultiplied RGB energy is preserved; only
transparent black falls outside the canvas. There is no resampling,
normalization, recoloring, filtering or artistic redraw. The outputs are
exact horizontal mirrors, with the existing soft-color edges, 12×14 logical
canvas and anchor (0,0). Native sampling is applied after the full-density
transform; transforming an already sampled native image is not equivalent.

All 7,187 earlier non-catalog asset files are byte-exact. Additions are eight
HDA pack copies, four source PNGs and a 26-file generated-only rebuild
package. Catalog changes have an exact inverse. The source and RGBA pins
and identity maps are append-only: 18 routes / 77 canonical phases,
21 drawable identities and 23 observed identities. Maximum budget 7,
80 slots, 168 cells and the 32,060-byte normal-bank guard remain unchanged.
Budgets 262=6, 261=6 and 272=7 are preserved; 163/164 stay pass-through.
Only the four `rear_multi_p1` core/header/pins/adapter production files change.

## Focused qualification

- All 17 strict C99 core suites pass plain and ASan/UBSan, 34 runs. The
  new suite performs 3,529,045 checks per run, including all 448 cyclic
  continuation designs, every 80×80 slot pair, seven admissions/eighth
  rejection, and retained identities across all 18 routes.
- Actual allocator/adapter/decoder/loader/wrapper tests pass 8,242,522 checks
  per build with 672 malformed-resource variants. They cover all 640
  record-bit changes at every phase, source/RGBA failures, each of seven
  resources missing/corrupt at d4/d8, warm disk replacement/restart,
  exact startup root/density and linked 451 directions producing 298/299.
  Gameplay state equals the observer-stripped allocator. Drawing is stubbed
  in this suite and does not establish compositor quality.
- Four authentic production-pin runs pass 1,762,349 checks each across both
  accepted packs and plain/ASan/UBSan builds, with no pin overrides. They
  cover all 18 routes, 55 excluded shared records, nine excluded genuine
  mappings, 36 alternate payloads, aliases and energy 0/39 parity.
- All nine asset suites pass, including cell-exact transforms, energy,
  mirror/header/payload/source pins, relocated rebuilds and corrupt-input,
  catalog-tamper and symlink controls. All 15 targeted core mutants fail.
- The original-source inverse passes. Uninstrumented enabled and
  renderer-disabled builds each compile 74 units with zero warnings/errors
  under the established strict profile. Other 156 source files are exact.

Leak detection is disabled in ASan/UBSan; no LeakSanitizer claim is made.
Production suppressions are misleading-indentation, format-truncation and
missing-field-initializers; disabled builds also suppress unused-variable
and unused-parameter. This is not an unsuppressed-all-warning result.

Before integration, the source-extracted actual allocator, movement,
wrapper, indexed blitter and compositor pass 786 rendered cases, 1,293
allocator comparisons, 3,136 draws, 84 phase-pair checks and 32 actual SDL
nearest native outputs, in strict and sanitized builds. A separate mixed
supplement passes 144 cases, 288 native outputs, 1,872 draws, 101 allocator
comparisons, 2,832 movement comparisons, 864 retained-identity checks and
48 overlapping mixed-birth cases. Independent ordered integer-alpha and
ownership/restoration oracles agree. These synthetic offline checks are
separate from actual gameplay; experimental 273 dispatch does not broaden
the unchanged baseline production ownership core.

## One completed actual-game pair and retained failure history

One baseline/candidate pair completed on the first Normal level at native
2× (640×400), using density 8 art: 180 ticks and 31 gameplay captures per
process, both exits successful. Twenty original trace streams and four full
startup-state streams match. A genuine P4 purchase is followed by a private
diagnostic changing only the rear-power byte from 4 to 9; all other player
bytes and full RNG state match, with pointer relocation verified separately.
This is not a genuine P9 purchase or progression test. Natural seed, energy,
input, cooldown, emission, movement and collision rules are not overridden;
genuine low-energy requests emit nothing.

All 539 new HD draws belong to exact record 273. The complete birth at
tick 68 is captured at ticks 69/70/71, ages 1/2/3. All 21 pairs are checked
at each age: expected age-1 overlap separates by age 2. Fourteen strict
brown/cloud head-and-rim witnesses cover all seven phases. Independent
integer-alpha checks pass 141 baseline and 406 candidate selected patches,
with zero errors. Actual SDL output matches upload samples; shop and
shot-free tick 179 images match. Birth identities survive the switch at 100.
Direct native visual review, including parent review of tick 70, passes:
the warm fan and near-vertical twins remain readable with no observed matte.

The initial launch attempt spawned two children but aborted at its first
memory observation before seed/state/capture gates: a `/proc/limits` parser
rejected trailing whitespace. Its evidence and failed preparation snapshot
remain intact. Only that parser was corrected and tested with harmless
capped children. The explicitly authorized replacement produced the one
completed pair above. There was no third pair or additional gameplay run.

The completed pair's original validator still reports failure for its
post-switch-100 requirement that every protected record-262 head have an
unobscured, full-support native witness. IDs 277, 296 and 41 have zero
visible samples after tick 100 in the retained captures: their support is
off-playfield. That original condition is impossible on these captures and
is not reported as passed. No uncaptured early-age pixels are claimed.

An additive, independently reviewed corrected contract instead verifies the
full visible composite and exact original birth/slot/draw ownership on the
same retained data. All 200 post-100 original draws are accounted for:
180 exact HD admissions and 20 matching exclusions. At ticks 119/120/130,
visible authored support, whole visible rectangles, their enclosing native
boxes and final SDL samples are baseline/candidate exact. Legitimate later
scene overdraw remains included; pixels are not selected for equality or
unobscured survival. The 23 captured HD patches are bound to exact allocator
call, phase, slot, position and source-alpha identity. Owner bytes are
renderer class flags, not unique birth IDs. All six protected phases have
full-support witnesses before tick 60; no equivalent post-100 all-head
visibility or survival claim is made. Source, binaries, gameplay, captures
and original failed validator are unchanged. Acceptance is explicitly under
this corrected visible-composite contract.

The completed pair uses 259,702,247 evidence bytes, within 512 MiB/process
and 1 GiB/pair caps. Each child has kernel-enforced soft=hard RLIMIT_AS of
512 MiB; observed peak RSS is 130,678,784 / 129,523,712 bytes (baseline /
candidate). RSS observations are not the cap mechanism. The 4 GiB free-space
guard is retained. Raw captures, original data and private instrumentation
are excluded from publication.

## Reproduce and boundaries

```
python3 tests/run_rear_multi_p1_core_tests.py
python3 tests/run_rear_multi_p1_adapter_tests.py
python3 tests/test_rear_multi_p1_source_inverse.py
python3 -B tests/test_rear_multi_p9_mode2_assets.py
```

Public tests use synthetic records and generated art. Actual Hard/4×,
full-level/full-game completion, ordinary P9 acquisition, later progression,
and every ship/resolution are not claimed. Offline d4/d8 and native 2×/4×
coverage is distinct from the single Normal/native2×/d8 gameplay diagnostic.
Historical validation documents describe their own earlier baseline scope.

## Evidence seals

Private evidence remains outside the repository. SHA256 seals:

- Reviewed generated art build:
  `34cc9eb9117a7311d77804f0a3617ee877033b7abb7dfa06022bc2211d1de6ba`

- Unified source/art/test freeze:
  `a5c61ac94ee0f0939087694b2a53b3543c0f8d027ff87cddaa9c93ce3855149b`

- Source test receipt:
  `3b900e1139918245a418c48e05055a5e3ae7b6c90d28dae78911c1192d619892`

- Authentic production-pin receipt:
  `fb4fcacf3405ee00ff83e0107d98626521b8edb22bd996552fa374563df2c556`

- Actual compositor receipt:
  `8e31e6c1990bd01e39fb1cc5deebea9f798ad54260e3b467db862ab2b644f6ec`

- Mixed compositor receipt:
  `86b698c7ce1598f04aa3655310c90e27da4a883d2cd9edf70df5fbbf81c9f655`

- Independent corrected visible-composite review:
  `f64b823eda0e6c7b879a8cf2c1a85fe853bbae5f2e6bf2d353b9269e5717a445`

- Parent actual-native art review:
  `a5f8e6b933c26f00f5c8b2770793156788b2d9195b7c60a6a877c78a41655090`

- Final additive runtime acceptance:
  `92ad6234fcf70f1d05c4d3947953df05420b2f1aac94568893b3cf598b5b3613`
