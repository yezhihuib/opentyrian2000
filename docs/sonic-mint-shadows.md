# Remaining Sonic and Mint alpha shadows

## Finite scope

Normal bank8/TILE IDs6,44,73,63,82,16,54,130,131,149,150,223,224,242,243,
143,144 and27 reuse their already accepted density8 head alpha for the existing
command-scoped smooth-shadow compositor. Together with105/106/124/125 this
completes all21 normal Sonic shadow identities. Mint27 is a player-owned
Mint-O-Ship sidekick projectile, using the same bank8 player-shot renderer.
No head pixels, manifests, resources, gameplay data, collision geometry, RNG,
indexed blitters, shot origins or visibility decisions change.

Each new shadow requires canonical decoded source indices plus coverage, exact
bank identity/size, frozen full RGBA, matching resource pointer/path and the
current command epoch. Preparation, native-blitter begin and native-write
consumption independently reject two-player, Galaga and linked modes. This does
not narrow the previously accepted head routes. Density4, Christmas, original,
missing/invalid resources, wrong warm roots, malformed/truncated source and
unsupported geometry keep the existing classic path. Source and cached in-memory resource
restoration work in the same allocation/cache; this does not promise automatic
reload of repaired on-disk resources after a cached load failure. The original INDEX8 darkening
still executes exactly once, in its original write order and with its original
palette-ramp floor. Alpha only controls the composed visual operation; RGB never
colors the shadow. Alpha-zero preserves the underlay and partial alpha retains
the accepted darkening strength, including cloud provenance.

The previous17 shadow pin rows remain unchanged. At this checkpoint, Regular Missile31–33,
Charge252–254 and green214–217 kept explicit classic-shadow exclusions.
A [separate finite follow-up](ten-weapon-shadows.md) adds those ten shadows.
This batch does not claim second-level acceptance.

## Original source identity

Five ordinary-bay controlled Sonic scenes cover the remaining17 IDs:

- Rear11/mode1/P3, original weapon278:6,44,223,224
- Rear11/mode1/P4, original weapon279:16,54,63
- Rear11/mode1/P8, original weapon283:73,82
- Rear11/mode1/P9, original weapon284:73,242,243
- Rear11/mode1/P11, original weapon286:130,131,149,150
- Front41/P1, original weapon756, added to the P3 scene:143,144

The P8/P9/P11 rows also emit the already accepted quartet. All selected rear
rows use shotrepeat6 and weapani0; front756 uses shotrepeat3 and weapani0.
Selected original rows and exact+1000 copies were inspected in tyrian.hdt,
tyrian4.lvl and tyrian5.lvl. Identity mappings, full port11/41 rows and the Mint
item row carry across those tables. Rear Sonic shipblastfilter is208 in the
first table and192 in the latter two; this original gameplay distinction is
preserved. Unused record tails also differ, so full cross-episode weapon-row
equality is not claimed.

Mint is real option16: pwr0, wport16, wpnum452, ammo0, tr3, option1, ani16.
Weapon452 and its+1000 copy1452 are the only live records containing ID27.
Weapon452 has multi1, max1, weapani0, shotrepeat4, sg27, del255, sx0, sy10,
bx0 and by0. The ordinary sidekick fire site calls player_shot_create using
this item; shots.c then sends its bank8 shadow/head through the shared player
wrappers. No named main-gun port is claimed to be a separate Mint27 loadout.

## Verification

The dedicated suite extracts actual production preparation, begin, pixel,
end and original indexed blitters. A separate arithmetic oracle checks shadow
composition over classic, HD and cloud underlays. Frozen expectations and
manifest hashes protect the shared decoding/alpha inputs. All18 identities
exercise bounded pairwise geometry plus full per-identity mode, source, cache,
resource, epoch and later-write checks. The shared quartet suite retains its
original full coordinate sweep. Unit HD-head drawing and font hooks remain
stubs; actual-engine pairs establish the bounded full integration evidence.

The actual-engine scope is six baseline/candidate 90-tick comparisons in
Episode 1/Normal/physical 9, seed 0x5eed, native 640×400 SDL dummy/software output.
Five use ordinary front/rear loadouts above. The sixth selects both real Mint16
mounts and presses their original sidekick inputs through an external,
diagnostic-only game_probe copy shared by baseline and candidate. It preserves
normal initialization, orbit, fire and shot simulation; no diagnostic probe
change ships in the repository. PNG-only interception captures actual SDL
framebuffers without writing BMP files.

Final optimized and ASAN/UBSAN runs each pass 4,968 bounded geometry cases,
332,419,200 native INDEX8 bytes and 84,860,928 RGB samples. They include 2,052
early denials, 954 source cases, 2,772 resource cases from 1,062 malformed or
missing fixtures, 613 begin identity/epoch cases, 522 pixel/epoch/mode cases,
108 later ordered-write cases and 30 remaining classic-route cases. All alpha
zero, partial and full categories are observed. The six meaningful shadow-guard
mutants are rejected. Peak child RSS is 316,460 KiB. The separate quartet
regression also passes optimized and ASAN/UBSAN runs, including 25,440 geometry
cases and 1,656,316,800 native INDEX8 bytes per run. The frozen quartet artwork
rebuild/corruption regression passes; all existing head/resource bytes remain
unchanged. Independent source/code/test review finds no blocking defect.

The six main pairs pass. Three additional P8/P9/P11 pairs use the same external
QA-only probe in both sides, setting initial player y to 120 instead of 160 and
exporting only tick 4. This exposes the otherwise bottom-clipped downward IDs
82/242/243/130/131 without changing their original shot simulation. These nine
pairs each finish 90 ticks, admit 3,101 new shadow draws and retain 105 guarded
out-of-bounds classic calls. Every target ID has a visible native-frame witness.
The source, state, RNG, input, collision, loadout, palette, native INDEX8 and
ordered draw geometry remain exact; only eligible shadow mirrored bits change.
Head commands and all other draw commands are unchanged. Added shadow ownership
raises the diagnostic HD-subpixel count for some later overlapping blend writes,
strictly inside admitted shadow rectangles; native blend bytes/order are exact.
All 39 classic PNG pairs are byte-identical. Coverage mismatches and renderer
rejections are zero. No runtime font restoration event occurs in these opening
windows; full font-restoration acceptance is not claimed by these runs.

The 234 runtime PNGs total 47,298,881 bytes, with peak game RSS 111,849,472 bytes.
All batch PNGs including native contact sheets total 48,353,656 bytes, below the
64 MiB cap; the final disk check retains more than 5 GB free. Native-scale review
of all 18 contour crops and representative full-frame pairs accepts the aligned
smoother silhouettes and unchanged heads/surroundings. Crops are rectangle
witnesses in actual composed scenes, so overlapping pixels are not claimed as
isolated per-projectile output. The assisted tick-4 visibility samples preserve
the original opening fade and are correspondingly dark.
Windows, GPU rendering, natural purchased-loadout playthroughs, full-level
clears, later levels and multiplayer are outside this bounded acceptance.
LeakSanitizer is unavailable under executor ptrace; ASAN/UBSAN remain enabled.
Runtime processes are capped at 512 MiB, compilers at 1 GiB, this batch's PNG output
at 64 MiB, with a 5 GB free-disk reserve and no deletion of old output.

## Reproduce finite compositor checks

Run from the repository with separately supplied original game data and the
complete accepted resource pack:

```sh
python3 tests/run_energy_shadow_tests.py --data ORIGINAL_DATA_DIR \
  --pack COMPLETE_ACCEPTED_PACK --out NEW_EXTERNAL_OUTPUT --sanitize --mutants
python3 tests/run_sonic_quadrant_shadow_tests.py --data ORIGINAL_DATA_DIR \
  --pack COMPLETE_ACCEPTED_PACK --out NEW_EXTERNAL_QUARTET_OUTPUT --sanitize
```
