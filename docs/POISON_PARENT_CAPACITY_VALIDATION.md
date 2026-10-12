# Poison Bomb parent103 and HD region capacity

## Accepted scope

One static physical bronze/green player projectile, spriteSheet8 ID103, uses
slot325, logical12×14, density8 and anchor(0,0). The original shot origin,
indexed drawing, shadow, weapon tables, collision, RNG and child/trail logic
are unchanged. All333 preceding debug-pack assets are byte-identical.
The existing green214–217 heads and explosion78–84 trail remain unchanged.
The optional Talon preview retains its four pre-existing omitted enemy assets;
its prior329 files and the blue-four pack's prior333 files are unchanged.
Current totals:18 packs,2,900 HDA entries,342 canonical PNGs; default preview330,
debug334. This is one finite weapon family, not complete player-weapon coverage.

## Fixed presentation failure

Dense original Poison Bomb collisions exceeded the old256-entry HD region
registry, causing a whole-frame indexed fallback. The old600-tick runs had
15/21/44 such frames at powers1/6/11. Some also occur without the new parent
binding; parent103 adds normal/shadow records and exposes the existing limit.

At the user's request the registry now has65,536 entries. It is a static BSS
array of32-byte records:2,097,152 bytes total,2,088,960 bytes more than before.
The count and loop indices are unsigned int (4 bytes on the checked ABI).
Every scan ends at the active count; reset does not clear the whole array.
There is no capacity-derived stack/heap allocation. Existing active-count
quadratic searches are unchanged. All gameplay object pools are unchanged.

The original bounds guard and fail-closed behavior remain. ASan/UBSan tests
seed65,535 valid records, successfully add the65,536th, deduplicate at capacity,
reject the65,537th without changing pixels/ownership/count, and verify reset.
10,792,208 boundary checks pass, including negative controls. Nonoverflow
256/1,024/65,536 compositions match at2×/4×/8×. Current conservative raw draw-call
bound is1,122; the current deduplicated bound is822. Observed peak is398.
See [the boundary test](../prototype/fixtures/README-hd-region-budget.md).

## Runtime and visual evidence

- Original selected-loadout fixture, front port33, powers1/6/11. No survival,
  weapon-record injection or scripted collision controls. The fixture supplies
  the documented deterministic firing/input and starting loadout.
- Final65,536 matrix:3,600 rendered frames at2×/4×, including600-tick runs for
  all three powers and parent-only missing cases. Zero capacity/coverage errors.
  Independent audit confirms19 original/effect logs byte-exact across modes and
  scales, including state, collisions, projectiles, effects, fades and scene hits.
  Missing and invalid same-density RGB outputs match; classic uses density1,
  so its raw hash is not directly compared with density8 fallback output.
- All final output RGB hashes match the corrected1,024 trial. Previously
  nonoverflow output remains exact. A fresh production build without private
  capture/probe hooks additionally reproduces510 power11 frames exactly across
  27 deterministic TSVs; only the wall-clock control log differs.
- Actual SDL native2× streams:60 frames each, power1 ticks180–239, powers6/11
  ticks270–329. The corrected1,024 capture output is byte-equivalent to final
  65,536 output for every captured frame. Final65,536 native4× peak292 is also
  captured directly. Original failing videos remain private diagnostic evidence.
- Power1 collision199 immediately consumes all eight children, so that event
  visually shows214 only. Power6 collision284 supplies surviving214/215/216/217
  at284/285/286/287 and all seven trail phases78–84 at284–290.
- Independent exhaustive chronological inspection passed all180 native frames.
  Physical canister, original shadow, parent impact, surviving child cycle,
  dense burst and effect decay are reviewed. The strong stacked original shadow
  under dense collisions is retained; this is not a whole-game visual approval.
- Sequential headless ABBA120-frame trials averaged12.58s at1,024 and12.59s at
  65,536. Peak resident memory was approximately82.2MiB in both, since untouched
  BSS pages need not become resident. These log-writing trials are not an FPS
  benchmark or a promise about all hardware/scenes.

Episode-table audit covers all33 port33 power rows across e1–3/e4/e5. Parent
shipblastfilter remains240 in e1–3 and16 in e4/e5. The e4/e5 result is source
coverage only, not an actual episode play test. Windows acceptance is pending.

## Reproduction

From the repository root with normal build dependencies and legal external data:

```sh
make -j2
python prototype/build-hd-assets.py
python prototype/build-poison-parent-art.py --output NEW_EXTERNAL_DIRECTORY
python prototype/fixtures/test-hd-region-budget.py --source . --report region-result.json
```

For the selected-loadout runtime, substitute the legal data directory and run
powers1,6,11 separately with scaler2x/4x in their normal isolated config:

```sh
./opentyrian2000 --data=/legal/tyrian2000 --no-sound --no-joystick --no-xmas \
  --asset-debug=custom --asset-debug-tick=90 --asset-debug-running \
  --render-ticks=600 --render-test=local \
  --render-assets=assets/hd/packs/packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test \
  --render-front-port=33 --render-front-power=11 --render-scene=v1 --render-no-capture
```

The committed source archive is generated-only; source manifests retain their
freeze-time “runtime pending” wording. This integration report supersedes that
status without modifying the frozen artwork provenance. No original game RGB,
private readback hooks or test captures are committed.
