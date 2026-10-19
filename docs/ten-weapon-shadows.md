# Missile, Charge and green alpha shadows

## Finite scope

Normal bank 8/TILE player IDs 31–33 (Regular Missile Launcher), 252–254
(Charge Cannon) and 214–217 (green energy) reuse their existing accepted density 8
head alpha in the original command-scoped smooth-shadow compositor. The physical
Missile heads stay distinct from the energy heads. No artwork, manifest,
resources, original data, shot geometry, collisions, inputs, RNG or native
INDEX8 writes change. The previous 35 shadow pins stay exact.

Every admission requires canonical decoded original indices and coverage,
full frozen RGBA, bank identity and size, exact resource pointer/path/root,
8x dimensions and zero anchor. Preparation and native-blitter entry recheck
source and payload; all three compositor stages guard mode and command epoch.
Christmas, original-reference, two-player, Galaga, linked, missing/invalid,
4x-only resources, malformed source, wrong warm roots and unsupported geometry
retain classic drawing. Same-allocation source and in-memory resource repair
remain recoverable; repaired disk resources do not automatically bypass a
cached load failure. The explicit fallback statements remain in place.

The alpha operates at the original shadow call, x=shotX+1 and
y=shotY+shadowYDist. The original indexed blitter still runs exactly once,
retaining its palette high nibble and halving the low nibble in original order.
Alpha-zero leaves the composed underlay untouched; partial alpha blends the
existing darkening operation, including cloud provenance. RGB from the head
resource does not color the shadow. Later native draws retain ownership/order.

## Source and real loadouts

- Regular Missile Launcher port 17 P5 selects weapon 371 and ID 32; P11 selects 377
  and IDs 33/31. These remain physical missiles with their accepted head art.
- Real Charge Cannon option 3 has pwr=2, wport=16, base weapon 101. The existing
  charge-stages diagnostic preset uses original initialization and one-tick
  sidekick inputs at 2/24/66 to discharge 101/102/103, emitting 252/253/254.
- Poison Bomb port 33 P1 selects 636. Its original attack 171 collision route
  emits child weapon 71 with sg=214 and weapani=3, producing 214–217. Ordinary
  Protron Z port 6 supplies static 214 only and is not claimed as coverage for
  the animation. No child projectile is injected by a diagnostic selector.

The selected source rows and their +1000 copies match within tyrian.hdt,
tyrian4.lvl and tyrian5.lvl. Original episode distinctions remain: Missile
shipblastfilter 208 becomes 80 in episode 4/5; Poison 240 becomes 16. Child 71 and
Charge 101–103 active fields stay equal. Broader episode 4/5 row 793 and 1793 differ
in sound 30/31 and can emit additional animation IDs; equality of every shared
record or runtime acceptance of every episode is not claimed. Christmas source
changes 31/32 and 214–217; 33 and 252–254 decode identically, but this new shadow
route deliberately remains normal-only for all ten.

## Verification

The finite suite extracts the actual production wrapper, indexed blitters,
preparation/entry/pixel/end functions and loader. A separate arithmetic oracle
checks classic, HD and cloud underlays. It uses per-ID cold/warm mode, malformed
source, same-address reload, resource metadata/pointer/root, command epoch,
mid-command mode and later ordered-write cases. Pairwise/boundary geometry
avoids an unnecessary Cartesian repeat of the already accepted compositor
coordinate sweep. All 35 previous contours have ordinary-mode coexistence
checks; the first 13 retain their established broader mode checks. Head drawing
and font hooks are unit stubs, so runtime pairs are a separate integration gate.

Final optimized and ASAN/UBSAN ten-ID runs each pass 2,760 bounded geometry
cases, 195,696,000 native INDEX8 bytes and 49,553,408 RGB samples. They include 1,140
early denials, 530 source cases, 1,540 resource cases across 590 resource
variants, 341 begin identity/epoch cases, 290 pixel/epoch/mode cases, 60 later
ordered-write cases and 18 neighboring classic-route checks. The legacy JSON
counter named previous_thirteen_positive_cases is retained for compatibility;
in this ten-ID suite its 301 cases are 35×6 ordinary-mode positives plus 13×7
established extended-mode positives. Alpha-zero, partial and full categories
are observed. All six meaningful shadow-guard mutants are rejected. Peak child
RSS is 224,576 KiB. Independent source/code/test review finds no blocking defect.

Actual-engine acceptance consists of four baseline/candidate comparisons in
Episode 1/Normal/physical 9, seed 0x5eed, Linux SDL dummy/software at native 640×400:
two 90-tick Missile P5/P11 pairs, one 90-tick real Charge 3-stage pair and one 270-tick
Poison Bomb P1 pair. The latter naturally executes original enemy collisions
and child 71 animation; all ten IDs have visible native-frame witnesses. An
external QA-only probe copy selects exported framebuffer ticks identically for
both sides. No input, loadout-selection logic, simulation or shipping probe
changes are used. PNG-only interception captures actual SDL output without BMP.

All four final pairs complete, admitting 661 new shadow draws. State, RNG,
input, collisions, loadouts, palette, native INDEX8 and ordered draw geometry
remain exact. All 9 classic PNG pairs are byte-identical. Head commands and all
other commands are unchanged; only eligible shadow mirrored bits change.
Later blended writes may inherit new shadow ownership: 6,926 diagnostic
HD-subpixel-count changes occur strictly inside admitted shadow rectangles,
with native blend values and write order exact. All visible differences remain
inside the current original shadow rectangles. Renderer rejections and coverage
mismatches are zero. Crops are composed-scene rectangle witnesses, so overlaps
are not claimed as isolated per-projectile output. Charge 252's tick 4 sample
retains the original dark opening fade. These scenes do not exercise a runtime
font-restoration event; full font-restoration acceptance is not claimed.

One no-capture 360-tick green discovery and the first 360-tick green baseline
attempt stopped at the 8 MiB-per-file diagnostic blend-log cap, after all four
identities had appeared. Those outputs are retained. The final 270-tick pair
covers the required 199/260–262 windows and finishes below that cap. An earlier
90-tick mixed Missile/Poison discovery completed with no green collision and no
PNG export. These three discovery/failed attempts are not final acceptance pairs.

The 54 PNGs in final pairs total 13,373,262 bytes; peak game RSS is 118,435,840 bytes.
All batch PNGs, including retained failed-attempt captures and native contact
sheets, total 17,662,190 bytes, below 48 MiB. Parent native-scale review accepts the aligned smoother silhouettes and
unchanged heads/surroundings. The separate prior 18-ID Sonic/Mint regression
also passes optimized and ASAN/UBSAN runs, each with 4,968 bounded geometry
cases, 332,419,200 native INDEX8 bytes and 84,860,928 RGB samples. The established
full quartet coordinate sweep is reused from its prior accepted checkpoint;
this change does not alter the compositor algorithm. Final disk reserve remains
above 5 GB.

## Reproduce finite compositor checks

Run from the repository with separately supplied original game data and the
complete accepted resource pack:

```sh
python3 tests/run_ten_weapon_shadow_tests.py --data ORIGINAL_DATA_DIR \
  --pack COMPLETE_ACCEPTED_PACK --out NEW_EXTERNAL_OUTPUT --sanitize --mutants
```

Windows, GPU/fullscreen, natural purchased-loadout playthroughs, full-level
clears, later levels and multiplayer are outside this bounded acceptance.
LeakSanitizer is unavailable under executor ptrace; ASAN/UBSAN remain enabled.
Runtime processes are capped at 512 MiB, compilers at 1 GiB, this batch's PNG output
at 48 MiB, with a 5 GB free-disk reserve and no deletion of old output.
