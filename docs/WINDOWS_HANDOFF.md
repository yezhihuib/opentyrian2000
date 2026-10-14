# Windows handoff to dot

## Optional external MP3 source/launcher support (2026-10-14)

The source supports `--music-dir=DIR`, with the vendored single-header dr_mp3
compiled through `src/external_music.c`. The Visual Studio project lists that
source, its header and `src/third_party/dr_mp3.h`. No new decoder DLL, SDL_mixer,
SDK path, linker dependency or DLL-copy rule is required. Existing SDL2 and
optional SDL2_net setup remains unchanged. **This is not a Windows build,
bundle, real-device listening or runtime acceptance claim.**

After building this revision through the existing build entrypoint, opt in with
an existing absolute directory:

```powershell
& .\prototype\build-game.ps1
& .\prototype\start-manual-hd.ps1 -DataDirectory 'C:\Games\Tyrian 2000' `
  -MusicDirectory 'C:\Music\我的配乐'
```

The launcher resolves `-MusicDirectory` before changing to the dedicated profile
and quotes it through the existing Windows argument helper. Relative, empty and
missing launcher directories are rejected. The direct EXE option instead accepts
relative paths (relative to its launch working directory), and a nonempty
unavailable directory gives per-song FM fallback. Omitting the option preserves
the original audio path and its first-song behavior.

Supply exact lowercase `track01.mp3` through `track41.mp3` names only as needed;
`track18.mp3` is **Tyrian, The Level**. Keep MP3s and original data external to Git
and public bundles. Complete original data, including `music.mus`, remains
required. See [EXTERNAL_MUSIC.md](EXTERNAL_MUSIC.md) for all 41 titles, resource
limits, timing, fade and loop behavior.

The next authorized Windows checks should separately cover:

- `python prototype/test-windows-project.py` for source inventory only, then
  actual MSVC x64 Release and Debug builds.
- No option; an empty directory; valid, missing and rejected replacement songs;
  paths with spaces and Chinese characters; repeated launches and clean quit.
- First-level/title/shop transitions, jukebox change/restart, one-shot endings,
  music volume/mute/fade and the unchanged eight-channel SFX mixer.
- Real output-device listening, balance and loop boundaries. Mono output remains
  mono: stereo MP3s are downmixed and converted to the actual device sample rate.
  PCM wrapping does not guarantee gapless MP3s; original LDS timing still controls
  song-end/loop transitions and can cut short or outlast a replacement.

No new Windows package or runtime run accompanies these source/launcher changes.

## Current material source-list repair (2026-10-12)

The Visual Studio project now explicitly lists the five existing world-material
modules and their eight associated headers/generated indices. The PowerShell
build entrypoint uses this project; MSYS/Cygwin Makefile builds already include
all source files through a wildcard. No compiler, SDK, macro, gameplay, artwork
or runtime setting changed. `python prototype/test-windows-project.py` verifies
all current C sources are present exactly once and the project paths resolve.
Linux rebuilding passes; pinning the same revision string reproduces the
accepted forest executable bytes. The normal build embeds the current Git
revision string instead. **Windows compilation
and runtime remain untested at this checkpoint.**

The last actual Windows acceptance was7a5c62f: classic/HD first15-second SDL runs,
limited2×/4× checks and audio initialization. The next bounded smoke should use
this current branch and rebuild all18 packs (2,946 HDA entries;369 active PNGs).
Keep both lower-world parts, the cap sidecar, and the forest sidecar/declaration
with each default pack. Start with classic and HD ordinary first15 seconds at
native2×/4×, then inspect ordinary road/rock phase around500–559. Verify corrupt
or absent material inputs follow their documented family fallback. Later cap and
forest windows require explicitly labeled private-survival tools; the forest
layer-isolated preview is authoring evidence, not ordinary gameplay. Manual
keyboard behavior, listening, fullscreen and later-scene Windows review are
still pending. No user-computer task was started for this source-list repair.

Historical handoffs and counts follow.

Latest cloud milestone and current Windows acceptance command: [FIRST30_HD_COVERAGE.md](FIRST30_HD_COVERAGE.md). The remainder below is historical, including its old counts and WIP claims.

This is the historical eaebe318 handoff. Current cloud integration and corrected214–217 mapping are documented in [GREEN_RENDER_VALIDATION.md](GREEN_RENDER_VALIDATION.md). Use `prepare-green-review.py` for the current renderer; `prepare-effects.py` intentionally reproduces the archived historical fixture.

The laptop stops mainline development after publishing this handoff. Dot owns the remaining green projectile/smoke work in the complete cloud checkout. Future laptop work requires a supplied commit for Windows acceptance or an explicitly independent task. No new A/B/test was run after the stop instruction.

Current production uses green trail v2 (IDs78–84) with ORIGINAL point sampling, peak-value blend,12×14logical size,8x RGBA andanchor0,0. No extra+22offset. v1 remains unchanged; `-BeforeGreenV2` selects it, and `-BeforeGreenTrail` selects the pre-green shield stage. Renderer SHA256 fc53fad690a361ac2c3316bacc8258f1ed16f72054c9955776334939b1912a1f; last production Windows EXE SHA256 d2913de9a7beaa0f18179ec12f702f62e70c91616232a10c3255a711f3f387a0. EXE is a local build output, not a Git artifact.

White and shield are parent visually accepted within docs/EFFECTS_ACCEPTANCE.md limits. Green v1 and v2 are WIP: v1 has the original finite normal/nonblend/missing81/classic/repeat/real2x/clear checks; v2 has art-only actual normal/nonblend/real2x26frames each,64 spawns / 448 draws, original gameplay/input/collision/RNG/indexed logs unchanged, all RGB differences inside current smoke footprints,103 last draw and104–115clear. V2 missing81/classic/repeat were not rerun. Parent green visual acceptance, other weapons/maps/palettes/full-level/FPS remain unverified.

At tick90call0 the pre-smoke canvas is exact8xexpanded indexed RGB (HDowner 0). The unchanged HSV-value average carries its brightness blocks into even opaque smoke pixels. Source8x RGBA loads correctly. Actual processor1 has a different underlying image too, so the original diagnostic additionally labels a same-input nonblend FORMULA REPLAY; it is not called a native screenshot.

The interpolation B candidate in prototype/experiments/green-background is UNAPPLIED WIP: source patch and a private halo observer were prepared; private Windows build succeeded. No B runtime/A/B/visual result exists. B would interpolate only original-background peak under mapped green78–84whenowner 0, leave existing HD/background alpha and original hue/valueaverage unchanged. Do not treat it as selected or passed.

Projectile spriteSheet8/214 is still unmapped. CORRECTION: Original weapons71 and1071 use base214 but loaded weapani3, hence the four-frame214–217 pulse; the earlier static214 claim was incorrect. Geometry is12×14logical,anchor0,0, draw shotX+1,shotY and separate original shadow. Screenshot alone cannot distinguish71from1071. Dot has original-frame/mapping evidence and is creating replacement art. Nothing new was bound for214.

Tracked formal resources are197 PNG sources and2236 exact HDR entries in16 stage packs; current debug/preview counts190/186. Main engine/build/launcher/index files are tracked. Original data at siblingruntime-data/tyrian2000, local SDL SDKs at siblingproject-deps, EXE/DLL/PDB/build products, run captures/videos and rollback ZIPs remain external. Exact tested private fixture source overrides and hashes are tracked; the newly exported preparation command was not executed during handoff. HISTORICAL_PROTOTYPE_AUDIT.jsonlists64retained untracked files individually, their hashes/dependencies and reasons. No active tracked build/runtime dependency on those64was found. Their old local evidence dependencies are not advertised as portable. The prior screenshot/recycle discrepancy remains unverified; nothing was deleted or placed into recycle.

Windows future acceptance commands (not executed after stop):
```powershell
& .\prototype\build-game.ps1
& 'C:\Program Files\Python311\python.exe' .\prototype\build-hd-assets.py
& .\prototype\start-asset-debug.ps1 -Preset blue -Tick 194 -Until 275 -Running -Capture -CaptureStart 194 -CaptureCount 9 -WindowOnly -ExplosionLog
```
The last command checks the natural shield window using production code; it does not inject the green weapon. For the original71 green fixture:
```powershell
& 'C:\Program Files\Python311\python.exe' .\prototype\fixtures\prepare-effects.py --family green-trail --output ..\green-fixture
& ..\green-fixture\prototype\build-game.ps1
# Use a fresh run directory with the same4x/Integer config, and legal data separately.
$env:OT_FX_FIXTURE='1'; $env:OT_FX_PROBE='1'
# Run the prepared fixture EXE from that fresh directory with:
# --data=<legal-data> --no-sound --no-joystick --no-xmas --asset-debug=custom
# --asset-debug-tick=90 --asset-debug-running --render-ticks=116
# --render-assets=<repo>/assets/hd/packs/packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-test
# --render-test=local --asset-debug-explosion-log --asset-debug-capture
# --asset-debug-window-only --asset-debug-capture-start=90 --asset-debug-capture-count=26
Remove-Item Env:OT_FX_FIXTURE,Env:OT_FX_PROBE -ErrorAction SilentlyContinue
```

Existing Library IDs only; do not duplicate archives:
- V1board libfile_86544cb18a9c819197c49706d4501dfe,12.2s video libfile_15485d572e008191bb6787c558cca06e,218KB evidence libfile_f84ec05cbf088191943b756ec8d40d27.
- Same-frame blend diagnostic libfile_6048d764b5388191a939b97c49a0dc2b.
- V2actual42crop board libfile_aaed7270a1d88191a85151cb90d30232,9.15s A/B video libfile_b4c105c9e4b08191b1077b50110de8b4.
-214full original frame libfile_e0e9749b6cd481918264d5e262222405; mapping ZIP libfile_03f143291a4481918b078086676dee40.

Local rollback checkpoints in the recorded task/checkpoints directory: before-white-smoke-v1-after-git-resources, before-shield-v1-after-white-smoke, before-green-trail-v1-after-shield, before-green-trail-v2-after-v1. They are not Git-required cloud dependencies. Original prior Talon/blue/filters/turret/foundation/type10/death approvals,5frame/classic/missing compatibility and paused109/107/120 remain preserved.


## Purple installation / Layer3 foundation batch

See [PURPLE_INSTALLATION_VALIDATION.md](PURPLE_INSTALLATION_VALIDATION.md) for exact identities, reproduction and bounded cloud acceptance. Adds13 persistent terrain tiles and9 independent components; final gray fringe correction is accepted. Current packs316/320, canonicalPNG328, totalHDA2872. Windows native2×/4× acceptance remains pending; use the existing local fixture commands and current manifest defaults.


## 60–75 second bounded closure and cloud64

See [WINDOW60_75_VALIDATION.md](WINDOW60_75_VALIDATION.md). The final522-frame private-survival window has103 visible material identities with zero mapping gaps. Cloud64 lower-edge brightness/contour is corrected with14 cloud peers unchanged; production code is unchanged. Current packs316/320 and all18pack verification pass. Windows acceptance remains pending.


## Low grass / sand9 and75–90 mapping closure

See [GRASS_SAND_VALIDATION.md](GRASS_SAND_VALIDATION.md) and [WINDOW75_90_VALIDATION.md](WINDOW75_90_VALIDATION.md). Nine finite Layer1 assets are added; defaults325/329,337 active canonical PNGs,2,890 HDA entries across18 packs. The120-frame private-survival grass tail is visually accepted. Final 522-frame native 2×75–90 visual review passed; original-state/mapping audit has zero gaps. Windows native acceptance remains pending. Verify with `python prototype/build-hd-assets.py`; rebuild generated grass with `python prototype/build-grass-sand-art.py --output NEW_EXTERNAL_DIRECTORY`.

## Pulse-Cannon upgrade follow-up

Four additional player heads58/60/62/165 are accepted at powers1/2/6/11.
See [PULSE_UPGRADE_VALIDATION.md](PULSE_UPGRADE_VALIDATION.md) for bounded actual
2×/4× evidence and reproduction. Current18 packs:2898 HDA entries,341 PNGs;
default preview329/debug333. This batch still needs Windows-specific acceptance.

## Coordinated island continuity correction

41 existing art resources are revised together: gray rims/interiors/craters,
purple gray backings and the three turret144 backings. No production code or
asset-count change. See [ISLAND_CONTINUITY_VALIDATION.md](ISLAND_CONTINUITY_VALIDATION.md).
Windows acceptance of this art revision remains pending.

### Poison Bomb parent103 / region65,536 follow-up

Cloud acceptance now includes selected port33 powers1/6/11, original collision
chain and dense bursts without HD-region fallback. Windows has not yet run this
batch. Build and use the exact command in `POISON_PARENT_CAPACITY_VALIDATION.md`,
with your legal data path and2×/4× configuration; inspect ticks284–303 at power11.
The two-megabyte static registry changes no gameplay pools. Keep original shadow
behavior and do not treat this as full arsenal or whole-game acceptance.

## Guided four-identity follow-up

Player bank8 heads19/171 and shared warm20/21 are accepted in the bounded
Micro/Heavy/Guided and Widget context matrix. ID22 remains original.
Current18 packs:2,908 HDA entries,346 PNGs; preview334/debug338.
See [GUIDED_BOMB_VALIDATION.md](GUIDED_BOMB_VALIDATION.md) for exact scope,
fallback checks and reproduction. This batch has not been Windows-validated.

## Coordinated matte sand follow-up

21 existing road/grass backing assets now use the accepted quieter sand material.
Protected stone/grass pixels and all production source remain unchanged.
Historical road regeneration retains an explicit hash-checked old input route.
Counts:18 packs,2,908 HDA entries,350 active canonical PNGs; preview334/debug338.
See [SAND_ROAD_GRASS_VALIDATION.md](SAND_ROAD_GRASS_VALIDATION.md) for the
bounded road/grass-tail evidence and ID38 static-only limit. Windows remains pending.

## Optional world-coordinate ground material

The default packs now include `ground101-world-material.g101.0` and `.1`; retain
both beside the HDA files. They form one verified stream; either missing part
disables the complete material feature. Verify with `python prototype/build-hd-assets.py` and
`python prototype/build-ground101-world-material.py --verify`, then build normally.
The runtime has no new crypto-library dependency. A missing or incompatible
sidecar coherently disables this finite feature and renders the selected pack.
The 15.63MiB payload supplements existing renderer memory; diagnostic cloud timing
is not a Windows FPS guarantee. New Windows acceptance remains pending.

Start with the existing ordinary blue fixture around ticks500–559 at native2×
and4×. Check scrolling rock phase, road/plateau transitions and foreground order.
The later lifecycle footage uses explicitly private survival/original-control
fixtures, not a claim that the ordinary run survives those later windows.
See [GROUND101_WORLD_ATLAS.md](GROUND101_WORLD_ATLAS.md) for scope and reproduction.
