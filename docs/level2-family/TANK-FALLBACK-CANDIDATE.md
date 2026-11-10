# Independent normal tank fallback candidate

`BUILDING313_TANK_FALLBACK_ENABLE=1` is default off and additionally requires
terrain fallback and the existing tank194 family. It retains only the existing
eighteen witnessed births in slots 75..99, eight pinned normal poses and event
prefix through 258. Full-family presentation remains preferred. Full bodies must
fit x 24..264/y 0..156. No clipped, filtered, additional-event or additional-pose
admission is introduced.

## Same-frame proof

Metadata-only phase hooks bracket the original ground `JE_drawEnemy(100)` call.
The original `blit_enemy` supplies each actual tile immediately before legacy
admission, so unrelated scene rejection cannot suppress independent observation.
All four native calls 0/1/19/20 and their entity ends must complete in order.
Unrelated stores between parts reject the pending tank. Normal native callbacks
must match the pinned coordinates, indexed values and per-part counts exactly.

Each slot has its own transaction and immutable same-frame draw origin. Native
movement after drawing is expected, not compared to the saved origin. Current
epoch, generation, birth token/event, script serial/event, pose, shape, live
availability, source bank/record, palette and eight separate cached HDA payloads
remain required. No legacy draw, mutable legacy asset cache, building witness or
scene acceptance grants permission.

The acquisition descriptor is separately bound and checked throughout the
transaction. Its origin and other immutable metadata cannot be altered before
finish, and the completed descriptor is sealed alongside the patch and mask.
Composition rechecks both the original geometry and the descriptor seals.

Observed identity, source, filter or shape disqualification records an independent
lifetime denial. It survives ordinary frames, full-family presentation, resets
and renderer recreation. Only a fully verified replacement birth with greater
generation and token and a nondecreasing epoch replaces that denial. It never
changes legacy lifetime evidence. Geometry, missing material and incomplete
per-frame callbacks reject that frame without inventing a new lifetime.

Genuine semantic observations still occur after an earlier per-frame rejection,
including a witnessed slot temporarily reporting a different enemy type. The
denied epoch, generation and token retain independent nondecreasing high-water
marks. An invalid or rolled-back receipt cannot reduce them, and a later valid
replacement does not erase protection against restoring the older identity.
If an existing witnessed birth loses any identity field or has inconsistent
generation fields before acquisition, each remaining denial axis is retained.
They grant no positive identity permission. If only the epoch survives, the
same-epoch identity cannot be distinguished from restoration, so that slot is
conservatively suppressed until a fully verified newer epoch. Normal complete
receipt replacement is unchanged. No recovery guarantee applies to total
erasure of all identifying evidence.
Positive admission separately requires nonzero epoch, generation and token;
equal zero-valued generation fields do not constitute a witnessed birth.

## Underlay, ownership and failure isolation

Before part 0 a 192×224 ARGB patch captures surviving independent terrain or the
current palette-expanded native index. It never imports rejected actor canvas,
earlier local actor HD, previous-frame pixels or historical saved rectangles.
Only actual native writes acquire logical ownership; native holes remain
unowned. Alpha-zero and partial-alpha subpixels retain this captured underlay.

Every subsequent native store retires prior ownership in the affected logical
cell, including same-value writes, shadows, blends and fills. Tank masks and the
independent player mask are disjoint. Earlier ownership is never resurrected if
a later tank fails. A later overlapping actor uses native/terrain underlay,
which is deliberately conservative and is **not full-family multi-actor alpha
equivalence**. This prevents failed actors from becoming hidden dependencies of
otherwise valid patches.

Individual tank failures clear only that slot. Shared terrain, writer, surface,
palette, crop or lifecycle failures revoke all local actors. Completed patches
and masks are sealed at finish and revalidated after texture lock, before any
copy to the independent output. Existing HUD composition remains last. Output
is single use and requires at least one surviving terrain cell. No gameplay,
indexed drawing, RNG, asset bytes or legacy admission counters are changed.

Storage is bounded: twenty-five patches plus native/mask arrays consume 4,334,400
bytes, descriptors are additional, and the separate eight-image cache consumes
1,376,256 bytes. There is no previous-frame cache.

## Read-only receipts and qualification

`render_mirror_tank_fallback_status()` reports per-slot identity, origin, pose,
completion/currentness and surviving cells. Preparation is not presentation.
`presented_slots` is a 25-bit mask for slots 75..99 and is nonzero only during the
actual independent Present/readback interval. `presents` counts SDL frames with
at least one tank, not individual actors. The sample API additionally requires
the specified slot to be actually presenting and rechecks its sealed proof.
Its 672-byte relative mask and 43,008 ARGB samples are integration evidence, not
an independent artwork oracle. No authority follows from unowned samples.

Tests and native scene receipts must separately establish their bounded scope.
Source design alone does not qualify runtime coverage, all eighteen encounters,
full-level behavior, physical controls, Windows/GPU or performance. Original
data remains private and unchanged.

The combined real-include/native-blitter/writer/SDL fixture passes 281,939,537
assertions under ASan/UBSan. Its independent archived callback oracle covers
all eight authored poses, synthetic receipts for all eighteen births and all
twenty-five slots, cross-tank/player orders, native holes and alpha arithmetic,
same-value/blend/shadow/fill retirement, per-slot failure isolation, phase and
four-part order failures, persistent-denial/reset/renderer-recreation boundaries,
malformed materials and post-lock mutations. The actual scope/event, source
binding, witness, live-shape and palette predicates are exercised; level
admission, original bank/record digest and raw birth receipts are explicitly
declared fixture substitutions. No constructor or native event execution is
claimed by that fixture. Leak detection is disabled. Review found and corrected
identical-content art-pointer substitution and captured-identity denial gaps
before this successful run. A separate review also found and corrected
semantic observations skipped by early returns, mutable draw metadata and
lifetime-denial rollback. Four independent regression groups fail against the
pre-fix source and pass against the corrected source. Additional tests cover
pre-seal acquisition metadata changes and restoration of an older denied
identity after a valid newer birth. The finite partial-receipt matrix also
exposed and corrected absent negative evidence for incomplete births and a
positive-proof omission for zero-valued generation fields.

The partial-receipt matrix covers 260 configurations: nonempty combinations of
missing epoch, token, record and generation representations, generation
mismatches, stripped-birth and witness-only cases, each before or after a local
order rejection and with native type 194 or 193. It checks that restoration
cannot revive the same identity, that unrelated actors still present, and that
a genuinely newer verified birth can qualify. A separate control keeps an
ordinary non-tank allocation without tank history unobserved. Cases with no
remaining monotonic identity evidence are explicitly excluded.

The existing player and terrain fixtures separately retain their 5,199,569 and
4,096,544 passing assertions. The original tank-family test retains its eighteen
birth selectors, event receipts, eight material poses and 1,196 native writes.
Those checks are not a substitute for bounded original-data scene receipts.

```sh
python3 -m unittest discover -s tests -p 'test_b313_tank_fallback.py'
python3 scripts/build_level2_family.py --jobs 8
```

## Bounded original-data scene result

The accepted source digest is
`2d2efc5d2c954676b5493423a7a40bc408930ac714606dc323670d2292ce3914`.
The uninstrumented 112-unit build has SHA256
`402a71476170f0e31e06044a64db46c1d0f7b3d311aea090fac98b5d08353d65`.
The scene checker rebuilds four bootstrap/read-only observer units from that
immutable stage and adds actual SDL Present readback. It uses the original
ASTEROID2 loader, movement, firing, collisions, animation and indexed drawing,
with a fixed seed and sampled keyboard inputs. Neither probe nor asset-debug
mode is enabled. The on/off pair changes only the new tank option; terrain,
static HUD, public candidates and the independent normal player are enabled
in both runs.

- At 2x over 540 ticks, independent tank patches appear in 149 frames and
  preserve 274 additional tank draws. The run encounters five real witnessed
  identities (slots 75..79) and all eight poses. Among 646 qualifying draws
  and 641 consecutive same-identity pairs, HD/native transitions fall from
  190 with the option off to 0 with it on. All 646 qualifying draws are HD.
- At 4x over 240 ticks, 12 frames preserve 12 additional tank draws. This
  shorter run encounters one real identity and poses 1, 2 and 4. Among 117
  qualifying draws and 116 consecutive same-identity pairs, transitions fall
  from 16 to 0. All 117 qualifying draws are HD.
- Across both pairs, all 10,140 native state-field comparisons agree. Existing
  family, terrain and player admission remains identical. Actual Present
  hashes outside the exact surviving tank-owned cells agree on every frame;
  candidate-patch readback has zero mismatches. All differences in 30 scheduled
  full-window captures are confined to those exact owned cells. Native holes
  remain unchanged; the check is not merely a rectangular envelope.
- With the option off, all 10,140 state comparisons, 3,120 existing admission
  comparisons and 30 common captures match the published player checkpoint
  `c2800d7a3f62bc76ded9dc2dd39814ae9d2e9a39` (source digest beginning `c9de6486`).

A qualifying draw is complete, currently witnessed and has surviving native
ownership. A transition is counted only between consecutive ticks for the same
slot, epoch, generation and birth token. Entry, exit, clipping and disqualified
lifetimes are not silently treated as qualifying pairs. These measurements do
not claim zero flicker for all actors or every level condition, and they do not
turn the eighteen synthetic fixture birth cases into eighteen native encounters.
Full-level behavior, menus, physical input, Windows/GPU and performance remain
unqualified. The older frozen Windows preview is unchanged.

The regression set plus the original tank test passes 76 tests, with eight
frozen-package tests explicitly skipped because that package was not supplied.
The separate tank and player sanitizer suites pass four further tests; the
three terrain tests are already included in that regression count. The existing
static HUD oracle also passes its valid, missing and corrupt cases.

```sh
python3 scripts/launch_level2_family.py --data /private/original-data \
  --hd --public-candidates --terrain-fallback --static-hud \
  --player-fallback --tank-fallback --check-only
python3 tests/check_tank_fallback_scene.py --data /private/original-data \
  --out /private/fresh-tank-2x --scale 2 --ticks 540
python3 tests/check_tank_fallback_scene.py --data /private/original-data \
  --out /private/fresh-tank-4x --scale 4 --ticks 240
```

Original data, profiles, binary builds, screenshots and detailed receipts stay
outside the checkout and are not part of the public source checkpoint.
