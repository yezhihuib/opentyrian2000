# P02 / P04 enemy projectile reuse — finite prototype

This local change reuses **six approved, unchanged** PNG/HDR1 payloads. It is
**default-off** and is not normal-game/global HD activation. Compile with
`-DENEMY_REUSE_HD_PROTOTYPE=1`, use the established `--render-test=8` probe,
and select a gameplay asset directory containing `bullet-{105,106,124,125,20,21}-8.hda`.
No player eligibility, NEWSHF eligibility, original asset pixels, simulation
coordinates, collision, weapon timing, or RNG behavior is changed.

## Exact admission

- E1 physical level2 (ASTEROID2), enemy record550, weapon76, native NEWSHS bank:
  simultaneous static directional frames **105,124,106,125**; not animation.
- E1 physical level5 (DELIANI), enemy record240, weapon143, native NEWSHC bank:
  successive static frames **21,20**; not a two-frame animated shot.
- Canonical full enemy records, weapon records, actor banks and normal bank8
  are authenticated. Unique shape overrides, other emitters and altered records
  decline. Actor and shot generations, birth, retirement, native single-use draw
  witness, generic-end revocation and same-address bank reloads are tracked only
  in private display state. Existing bullets may outlive the emitter; reusing
  its actor slot invalidates the old display identity.
- Independent semantic role146 uses six private descriptors. Its disk headers
  remain role8 identities80000+frame, 12×14, density8, anchor(0,0). There is no
  `get_asset` call, player shadow lease, green-head ownership, source duplication,
  header rewrite, rotation, recoloring or mask cropping. Approved smooth alpha
  outside original pixel support is preserved.
- Six resources preflight atomically. Full header/length/payload pins and regular
  file checks are enforced. Every draw and retained-output proof rechecks loaded
  payloads and live sources. Root changes decline until renderer shutdown;
  shutdown frees private resources and revokes identity. No warm fallback to
  stale resources or partial family admission.
- Only normal single-player ordinary output is admitted. Christmas, network,
  two-player/Galaga/linked/special modes, invalid/missing/original-reference,
  non8×, unsupported surfaces, horizontal native row-wrap and unsupported
  output/filter modes remain classic. Partial vertical clips retain native
  coordinates. Fades explicitly discard this prototype's retained output.
- The original indexed blit always runs exactly once. Ordered normal alpha,
  later classic occlusion and other owners use existing compositor semantics.
  Source/final surface geometry, palette, indexed cache, resources and identity
  are checked before retained output is reused; faults decline coherently.

## Evidence and limits

`tests/enemy_reuse_validation.py` drives real native SDL production objects,
`JE_makeEnemy`, wrapper, indexed blitter and renderer with ASan+UBSan on touched
units. It is **not a natural game playthrough**. The final positive suite covers
310 cases / 79,076 assertions, including all six final-RGB alpha oracles,
INDEX8 and shot-byte equality, clips, mutations, atomic loader failures,
stale slots/banks, one-use witness, generic-role isolation, cross-owner
occlusion, cache mutation and fade decline. Deliberate source-pin and compositor
store removals must fail their independent test oracles.

Default-off, opt-in and mirror-disabled native builds are checked separately.
The four touched pre-existing default-off object files are byte-identical after
stripping debug metadata to base461604a8. Windows project includes the module,
but Windows/GPU execution has **not** been tested.

Actual-game paired, unchanged-control replays of levels2/5 died before their
selected target events. Their state/RNG/indexed-pixel logs matched between modes
(1342 and485 rows), but **zero target HD game-loop draws were observed**. This
is a bounded negative observation, not positive gameplay acceptance. Positive
all-six HD evidence is the native production-object harness only.

`tests/test_enemy_reuse_sources.py` verifies the six PNGs and both packs' twelve
HDA payloads against `enemy-reuse-source-pins.json`. All runtime payload rows stay
unchanged; only the current source-binding receipt row and source-manifest
metadata change. Source inventory is262 files, with a newest exact finite
historical inverse (`enemy-reuse-source.json`); historical ledgers are not rebased.

**P05 remains deferred:** its green head/smoke/player-slot ownership needs a
separate adapter. **P09 remains deferred:** frame227 is missing, so no mixed or
substituted animation is enabled.

**Independent known baseline issue:** the parent audit identified incorrect
NEWSHF pose-to-art binding in base461604a8 (168, with167 under audit). This change
leaves NEWSHF artwork and contracts untouched and does not certify those poses.
The correction belongs to the separately authorized art-integration change.

The legacy enemy-orb112/113 extracted-production regression also passes optimized
and sanitized runs (32,060 cold and warm bank-byte mutations;720 shot traces).
Its stale hitflare stub was updated without changing the production collision
path. The older standalone Sonic quadrant/shadow helpers do not compile because
of missing global-helper stubs; the same failures were reproduced on unchanged
base461604a8. They are reported blocked, not passed; the new native suite and
byte-identical default-off objects provide separate relevant evidence.
