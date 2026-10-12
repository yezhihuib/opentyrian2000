# Finite newsh4 long-seven source integration

This source checkpoint imports the approved V2 brown left structure as seven
complete 24×28 composites. Bank2/newsh4 types 66–72 use bases 153,155,157,159,191,193,
195, at density 8 and anchor 6,7. The 168×28 assembly is not a new game object.
Original ordered quadrant calls (0,1,19,20), movement, collision, filters, links,
layering, score and explosions remain authoritative. Types73–79 are excluded.

The renderer adds only ASSET_NEWSH4=102, the enemy-newsh4 filename prefix, seven
slots 382–388 and an exact bank 2/base allowlist. HDR1 keys are1020000+base. Existing
slots 0–381 and the 199-entry terrain registry are unchanged. No sampler, original
engine code, material route, startup resource or HUD resource changes.

Before any family replacement, all seven selected-pack resources are loaded at 8x
and checked by the existing HDR1 reader and frozen full-RGBA FNV-1a64 stamps.
FNV is an accidental-corruption check, not authentication. Exact SHA256 receipts
and original-RLE support comparisons are the source verification authority.
Missing, malformed, allocation-failed, altered-alpha or altered-RGB members make
all seven remain classic. There is no 4x substitution. Failure/success is cached
for the existing startup-selected Asset-cache lifetime; explicit disabled,
missing, invalid, density and scene guards still apply after caching. The
existing reload operation starts a fresh process. No per-frame I/O is added.

Original bank 2 reuse was independently decoded from all 1,701 enemy records:
only types 66–72 can use these bases. All have armor 50, static art, ground=true and
explonum 12; no damaged sprites, turrets, launchers or default drops. Only type 72
has value 1000. Difficulty scaling and live original flags must be observed,
never forced by a test. The three spawn sets reuse link 1 at event times 3574,
3798,4068. Event20 changes horizontal acceleration after 5 and 15 to +2 and−2.
Event times are not logic ticks. Count every active linked actor at collision.

The frozen source package contains generated artwork, technical alpha and
source facts only. Original RGB, retained game captures and external game-data
files are not imported. The importer preserves the entire approved source
inventory dd6c3f91282e98b9dc583701267ef4963833bbc7ec0dbaaa8ade450be2726fbb.
Default preview/debug packs gain exactly seven files each (393/397 entries).

## Reproduce source and loader gates

Use fresh output directories outside the checkout:

```
python3 prototype/build-newsh4-long7-art.py --output /tmp/newsh4-rebuilt
python3 prototype/build-newsh4-long7-art.py --output /tmp/newsh4-original-proof --original-data /path/to/tyrian2000
python3 prototype/test-newsh4-long7-binding.py --out /tmp/newsh4-binding
python3 prototype/test-newsh4-long7-source-guards.py --out /tmp/newsh4-source-guards
python3 prototype/test-newsh4-long7-preservation.py --out /tmp/newsh4-preservation.json
python3 prototype/build-hd-assets.py
python3 prototype/tests/startup-manufacturer/test_package.py
make
```

The binding recorder extracts production functions, runs ASan/UBSan and compares
all prior actor/terrain bindings with the pinned pre-integration commit. It
checks every bank identity 0–36 and base 0–700, all quadrants and 256 filters,
coherent missing/corrupt cases for each member, each allocation-failure position,
all possible first members, disabled modes and the unchanged terrain capacity.
Fixtures use read-only-by-workflow hardlinks; mutated files are independent.
Source guards require generated-only reproduction and reject altered or extra
source inputs, symlink paths, packed/canonical corruption and widened 4x scope.
The preservation check removes only the finite renderer additions to recover
identical prior source; all previous tracked files are checked. Windows project
XML and all C compilation paths are checked, without claiming a Windows build.

No test above starts the game. The separately approved bounded actual-game
validation is recorded in `docs/NEWSH4_LONG7_VALIDATION.json`. Source/loader tests
now compare against the merged title parent349b3ca. Title artwork, startup/HUD
bytes and original gameplay source remain identical to that parent.

## Bounded actual-game result

The original private-survival, stationary no-fire setup first logged all100
actor slots at six update/draw ordinals before choosing a target. All5869 initial
state ticks and156600 census rows matched. At5868, seven live eligible link1
actors occupied slots50-56; the prior set used57-63. Original collision geometry
and exposed source support identified slot53/type69/base159 as the unique target.
This is a live census result, never a rule that there are always seven actors.

Three explicitly artificial Pulse155 shots used the original creation, collision,
filter, removal and explosion routines at5869/5871/5873. No enemy fields were
forced. The target's armor50 became49 after damage1; all eligible linked ground
actors received filter208. Damage99 left armor49 and set iced40/filter208 on all
seven. Since original top-actor draw precedes shot collision, hit filter208 was
presented at5870, ice's first filter208 at5872, and filter9 at5873. The5872 draw
set filter9 for the next draw while iced decremented to39. Filter208 and9 both
have actual exposed pixels exactly matching the unchanged palette operator.

At lethal5873 the complete live-link census again counted all seven. The original
collision hit slot53 with its live armor49, removed every live linked member,
added1000 cash and7 to enemyKilled, and made seven observed ground=true,
explonum12 calls. `JE_setupExplosionLarge` interprets12 as big=true and subtracts
10, giving repeater TTL2. The frozen source prose saying “twelve repeaters” is
clarified here without modifying its inventory. Draw-before-collision explains
why the final filter9 structure and original explosions coexist at5873; the
structure is absent and full RGBA equal from5874, with explosion pools clear at5900.

All5904 original-state/indexed-output/RNG ticks matched A/B. Each of36 actual
native640x400 frames5868-5903 had zero coverage/restoration errors and exact RGBA
outside original source support. Later Layer3 alpha composition was replayed
exactly at intact5868, including57 partially blended changed pixels. Both ends,
153 and195, were wholly covered at that intact ordinal. Sparse later tinted
pixels of195 do not establish full end-art acceptance; no fully unobscured
168x28 assembly is claimed. Author review passes the visible bounded sequence.

One genuine1280x800 native readback at5868 retains the same internal density8
output and exactly reconstructs all32736 support pixels plus original Layer3
blending. It is not an enlargement of the2x image. Actual missing-one,
same-length corrupt-RGBA and render-density4 fixtures all fall back coherently
and exactly match their respective original baseline outputs. Density4 was
compared against its own density4 baseline, not the8x-render baseline.

After merging title349b3ca, a fresh complete Linux build and one36-ordinal
hash-only lifecycle regression matched all5904 state ticks, every native RGBA
hash and all raw observer streams except wall time. It saved no new media.
The earlier A/B lifecycle did not retain normalized intermediate blend fields;
no equality claim is made for those intermediate fields.

The final aggregate checks3026 standard HDA entries,409 exact source PNGs and18
packs, plus the separate3 title resources/2 manufacturer compatibility copies.
Default preview/debug counts remain393/397. Independent source review and
bounded author receipt hashes are pinned in the validation document.

Limits: diagnostic input and private player survival, one placement/window;
no natural manual combat, full-level, GPU/fullscreen or Windows runtime test.
Right types73-79/link2 remain unbound and source-only in this checkpoint.
Private hooks and game captures are excluded from production source and assets.
