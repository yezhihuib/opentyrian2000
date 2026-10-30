# Gold enemy pulse — generated epoch2

Normal bank8 selectors **168/169**, enemy-only role153, keep the original12×14
canvas and anchor0,0 at internal density8 (96×112 RGBA). Weapon63 uses two
animation frames of one shot (actual169 then168); weapon133 also uses static168.
No extra shots, coordinates, speed, hit boxes, collision or RNG logic is added.
Christmas and player role8 remain classic; density4 is not goldHD-supported.

## Fixed generated authoring

One generated RGBA master1774×887 and one historical generation prompt are
included. The master retains its AI/C2PA provenance; the prompt is a historical
build record, not executable instructions. Original colored pixels were viewed
privately for reference but neither those images nor original game data are
included or read during rebuilding. The finite binary support masks and five
native palette identity constants123–127 are compatibility data, not RGB art.

*168: crop(0,0,887,887), LANCZOS88×88, paste(0,8) in96×112.
*169: crop(887,0,1774,887), LANCZOS72×72, paste(8,16).

Pillow12.3.0 is fixed. Only generated pixels are used; RGBA is cleared outside
the immutable native masks or wherever alpha is zero. No fitting, crop search,
alpha promotion, original-RGB sampling or painted fill is permitted.

|selector|native cells|maxalpha≥200|1..199|whole zero cells|soft pixels|native alpha0 subpixels|
|---|---:|---:|---:|---:|---:|---:|
|168|97|72|25|0|5894|314|
|169|69|45|24|0|3575|841|

Both have maxalpha253 and **zero opaque255 pixels**. Every occupied nativecell
has some authored alpha, but314/841 individual subpixels are transparent. These
are not whole empty cells. Exact14×12 matrices, hashes and counts are closed by
`coverage-contract.json`; transparent supported pixels preserve authenticated
underlay and still participate in native ownership/dependency checks.

The production FNV-1a64 seed is `0xcbf29ce484222325`
(decimal14695981039346656037), prime`0x100000001b3`. Payload pins are
168:`d35eb01e52fbf3a5`,169:`28baab1d924b1433`.
The first epoch2 registration mistakenly omitted the seed's last digit; its
run01FAIL remains retained. Only pins/metadata were corrected for run02; the
bitmap and oracles were not relaxed. Unavailable original-environment gold
source/raw/native outcome remains **UNKNOWN**, not recovered as these new bytes.

## Rebuild/check

```sh
python3 scripts/build_current_projectile_gold_pulse.py --root .
python3 scripts/build_current_projectile_gold_pulse.py --root . --write
```

Check mode writes nothing. Explicit`--write` regenerates exactly six products:
two PNGs,two HDAs,compatibility mapping and payload header. There are no
stage/apply/check subcommands and no whole-inventory claim. A complete current
package requires both members. Unrelated historical manifests do not consume
the new inputs; pure package checks are not C runtime isolation proof.

## Existing bounded runtime evidence

`runtime-evidence.json` references immutable private receipts/backups, without
embedding experiment wrappers or original game screenshots/data.

The controlled internal8 production-TU probe passed880cases/50,255,790assertions
in four processes: original107+157+365 byte-exact, then new251. It reused83
previously sanitized project objects and compiled three changed/new TUs; it is
not a fresh fullgame build. Both payloads share the five native palette colors,
including123/124 shared with old61. Unused payload isolation does not waive the
whole-bank source, actual underlay colors or full cached-palette dependencies.
At fixed Talon geometry, authored-positive copies were168:974 and169:735 (all
soft); extra native-alpha0 transferred support86/85 is counted separately.
These are gold softRGB retained through native-covered transparent Talon pixels,
not Talon softalpha. All8 used bits255, bit128/reset, fulltile straightalpha,
alpha0underlay, playerclassic, resource/callback/final/cache faults are covered.

The separate JE_main differential used the original enemy schedule in E1physical5
under existing deterministic **no-player-movement/no-player-fire input**.
401ticks completed; actual generation29/slot1 enemy559/link10/weapon63 drew169
at364 and168 at365. Three variants preserved17native files and6actual INDEX8/
palette buffers. Present-image delta was nonzero only inside actual native masks;
missinggold matched qualifiedblue. FinalRGB witnesses are surviving exact subsets,
not proof of an exclusive final writer. Cached flags were passive observations.

“Stationary” describes input, not fixed x: native damage/push ended at x48,y160,
armor2,shield3. There were **28collision/player-damage rows**. No invulnerability
override was added; original initialization100 remained and terminaltick400 was
alive1/invulnerable0. This does not claim all401ticks lacked invulnerability.
Zero blend/fire/scene-hit/player-projectile rows do not cover those paths.
Only two screenshots364/365 and runtime logs were examined: this is not a full
continuous-animation smoothness, freeplay or fullcampaign result. Ordinary
compiler warnings and first-run missing-config/save warnings were retained.

## Fresh builds on the final production bytes

The separately recorded full-fresh epoch completed all **86 project translation
units in each of four fresh configurations**: default HD-off, HD-on, HD-on with
mirror disabled, and HD-on with ASan/UBSan. All build directories began empty;
no historical project objects, executables, dependency files or copied historical
source trees were reused. The sanitizer configuration used O1, debug information,
ASan/UBSan, frame pointers and no PIE. System/SDL libraries were not recompiled
with sanitizers; this is not a claim that every external library was sanitized.

The newly linked production-TU harness then passed **880 cases / 50,255,790
assertions** in the same four processes: 107 + 157 + 365 + 251. Original 629
source/input/output bytes remain exact; the reversible seventh outer wrapper
only provides dispatch to the gold process. All four stdout files also match
the accepted corrected epoch2 outputs exactly. The full-tile straight-alpha,
transparent-underlay, all-eight-member dependency, real player-classic and
Talon transfer/failure assertions were retained, not replaced by screenshot
inspection or opaque-pixel assumptions.

All ten build/link/native commands exited zero. The three ordinary builds
retained compiler warnings (stderr 46,079 / 46,894 / 41,376 bytes); the sanitized
build and remaining six commands had empty stderr. Twelve final source/input/
artifact/index checks passed. Actual sampled peak was 231,710,720 bytes and
final allocation was 194,723,840 bytes, below the 384/256 MiB limits. The main
receipt is SHA256
`7a5026f5b19bfd88becd8e453d899cd65c4b4e000309ea682fed2a2fffb0a9f5`.

A separate current-link-input supplement checked the actual compiler-selected
libc/libm/libgcc linker scripts and fixed targets, library aliases and the
explicit SDL pkg-config search path before and after the build. Both checks
passed; this supplements rather than rewrites the main driver's receipt, and
is not a recursive qualification of every runtime library. The combined
execution receipt is SHA256
`dd4dd8404a5713aa42c74d3466ece03a70112e1ca075cb68b57545917b10303a`.

`runtime-evidence.json` deliberately remains the immutable reference to the
previous incremental native probe and two-frame gameplay experiment. Its
historical non-claim of fresh/full-gate results is not the current aggregate
status; the distinct fresh result is recorded above. The gameplay experiment
is not rerun or relabeled as this full-fresh invocation.

## Complete selected qualification boundary

The final projection, metadata/QA epoch, selected-method collection and full
segmented campaign are separately bound. This README update is a subsequent
documentation epoch; it does not retroactively change the fresh invocation's
source snapshot. Fresh/native success alone is not selected-campaign PASS,
CI PASS, a new post-commit invocation or a claim that every repository test ran.
The unrelated stale historical method with a 1015-row expectation is not part
of the selected suite; the actual package-rebuild byte-equality method is kept.
No gold public-upload permission is implied by these checks or private backups.
