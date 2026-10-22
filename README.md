[English](README.md) | [简体中文](README.zh-CN.md)

# OpenTyrian2000 HD visual branch

This branch progressively modernizes OpenTyrian2000's visuals while preserving
original gameplay, logical coordinates, collisions, level data, events and RNG.
It builds on OpenTyrian2000 and OpenTyrian; the upstream README is preserved below.

## Current scope and limits

- Integrated work covers selected ships, enemies, weapons/effects, layered
  terrain, clouds and world materials. The finite single-player HUD includes
  its frame, weapon labels, shield bands, mode indicators and refined corner.
- Manual gameplay HD is opt-in for local single-player Episode 1. Existing
  physical-level-9 support is joined by the normal-data Hard+ first-level
  variant, physical level 15, in ordinary Full Game. Other levels and excluded
  modes retain their existing presentation. Controlled preview/asset-debug
  entrypoints remain separate. Manufacturer cards and layered title artwork
  have explicit startup opt-ins below; ordinary startup without those options
  retains classic rendering.
- Uncovered, missing or incompatible inputs use documented per-feature
  fallbacks. Pause/help/options retain classic presentation.
- Acceptance covers documented, bounded Linux scenarios, including native
  2×/4× checks. It is not whole-game, all-level, GPU/fullscreen or performance
  certification. The latest changes still need Windows runtime acceptance.
- Fixed MODE/SHIELD/ARMOR lettering and finite gameplay tiny-font rendering
  are integrated, along with finite firepower, generator and coarse armor
  meter refinement. One optional complete startup pack includes manufacturer
  PIC10/PIC12, PIC4 and both title logos, plus title/menu/settings/load and the
  documented selector/pregame typography below.
  Title checks pass in eight bounded cases / 13 actual-engine executions, plus one
  exact post-merge regression. Native 2×/4×, cursor/restart and real idle handoff are covered.
  Manufacturer startup checks passed at native 2×/4× output sizes
  using the actual engine with SDL dummy/software; physical-window/GPU acceptance
  remains separate.

- Enemy tank shells 146/147 pass bounded native 2×/4× checks with paired fallback.
  Five process starts include one retained failed fixture attempt and its corrected
  replacement. See [scope and receipts](docs/enemy-tank-shell-pair-v1/VALIDATION.md).

- Normal player Vulcan heads 67/70 have bounded P1/P7 native 2× paired checks: four
  90-tick runs, with all 11 powers covered separately by source units. Original
  indexed behavior remains exact. Numeric and author review pass within this scope.
  See [scope and receipts](docs/player-vulcan-two-v1/README.md).
  A [finite smooth-shadow follow-up](docs/player-vulcan-shadow-v1/README.md) also passes
  two new 90-tick P1/P7 comparisons against retained captures. That follow-up changes
  only these two normal player shadows; guarded negative-x calls remain classic.

- Rear-power pickup 534 has a three-phase HD body; the shared fixed-145 collection
  effect remains unchanged. Bounded original-input checks passed in three attempts
  with 22 native 2×/4× images; the observed reward is the empty-rear cash fallback.
  See [scope and receipts](docs/rear534-three-v1/README.md).

- The Data cube (record 513) adds twelve authored body phases with whole-family
  classic fallback. Bounded original-input lifecycle checks, native 2× frames
  and four native 4× body spots pass numeric and author review. See
  [Data cube scope and receipts](docs/data513-twelve-v1/README.md).

- A combined-source coexistence checkpoint joins rear 534, Data 513 and Vulcan
  heads 67/70 with smooth shadows, keeping their canonical artwork unchanged.
  Four separate bounded Linux witnesses pass: 69 new native 2× images and 12
  INDEX8 images exactly match the retained final family candidates, with exact
  state/trace comparisons except wall-clock timing. This verifies the families
  installed together; simultaneous multi-family exposure, full-level and Windows
  acceptance remain untested. See [combined scope and receipts](docs/qualified-family-coexistence-v1/README.md).

- Protron uses three independently authored shadow masks for normal player IDs
  225/244/226, preserving the accepted head bytes and original indexed writes.
  Interiors retain the existing full shadow strength; only the contour edge has
  partial coverage. Fresh P1/P6/P11 baseline/candidate checks pass numerical and
  bounded author review: six 90-tick Linux SDL dummy/software runs, 36 native 2×
  images and 36 INDEX8 images. Original state/RNG/indexed comparisons are exact;
  translucent head pixels may inherit the changed underlay. See
  [scope and receipts](docs/player-protron-shadow-three-v1/README.md).

- Normal front Multi (port 2) adds eight authored player heads. Bounded P2/P4/P7/P11
  native 2× baseline/candidate checks pass numerical and author review: eight
  90-tick runs, 48 native frames and 48 INDEX8 frames. All eight new IDs have visible
  witnesses across the fixed
  capture windows; some individual frames are cropped. A subsequent smooth-shadow
  extension reuses the frozen eight heads' alpha: four new 90-tick P2/P4/P7/P11 runs
  provide 24 native 2× frame pairs against retained head-only references, with exact
  original state/RNG and INDEX8 comparisons. Numerical and author review pass within
  this bounded scope. That Multi follow-up left existing 58/59, enemy and Protron
  operators unchanged, although overlapping translucent pixels can inherit a
  changed underlay. All-power,
  Christmas and other shared-use coverage remain separate source/unit checks. See
  [scope and receipts](docs/player-front-multi-eight-v1/README.md).

- Normal-data Hard+ first-level night HD preserves the original indexed cone,
  uses bounded palette-anchored residuals for nonlit authored detail and keeps
  cash locally classic. Source/unit review and one unprotected 23-finish Hard
  opening pass, with five actual 640×400 images and four independently checked
  indexed/palette pairs. A separate protected mid-level/Boss diagnostic also
  passed five selected windows through 7,429 ticks, with 360 sampled oracles.
  This is bounded renderer acceptance, not natural Hard survival, a full clear
  or Windows acceptance. See [scope and validation](docs/firstlevel15-night-v1/README.md).

- Christmas enemy shots preserve their original sprites for nine IDs whose normal
  replacements do not match Christmas data. Shells 146/147 stay eligible. This
  independent fallback has source/unit coverage, separate from the normal-data
  night extension. See [scope and historical receipts](docs/christmas-enemy-fallback-v1/README.md).

## Build and try

Original Tyrian 2000 data is required separately and is not included here.
Keep it outside the repository; see the upstream data information below.

Linux needs a C compiler, make, pkg-config, SDL2 and SDL2_net. Resource verification
also needs Python 3 and Pillow. Build with the [Makefile](Makefile):

```sh
make
python3 prototype/build-hd-assets.py
./opentyrian2000 --data=/absolute/path/to/tyrian2000
```

The last command is ordinary classic startup.

### Manual first-level HD

Start the ordinary menus and choose New Game / Episode 1 normally:

```sh
python scripts/build_current_craft267.py view --kind preview --output /absolute/path/to/new-current-preview
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --manual-hd-assets=/absolute/path/to/new-current-preview
```

The flag selects density-8 display assets, blend handling and the existing
13-pose Talon display. Native controls, random seed, health/damage/death, restart,
saves and progression remain in charge. There is no automatic firing/movement,
forced loadout or time limit. Eligible gameplay is local single-player Episode 1:
the existing physical-level-9 route, plus ordinary Full Game with normal data
and original Hard+ selection on physical level 15. These are internal first-level
variants, not menu level numbers. Title demos, two-player/Galaga and other levels
retain classic presentation. Missing or incompatible art retains existing
fallbacks. Pause/help/setup and outgoing level/menu transition fades can use
classic presentation.

The existing manual acceptance report describes the earlier physical-level-9
checkpoint. [Hard+ night scope and validation](docs/firstlevel15-night-v1/README.md)
record this additional route separately; Windows acceptance remains open.

Do not combine this flag with any `--render-*` / `--asset-debug*` option, network,
record, constant, death or loot mode (including legacy spellings). Those combinations
are rejected. A Release/NDEBUG build may independently add
`--startup-assets=/absolute/path/to/repo/assets/hd/packs/startup-title-settings-v1`
for manufacturer/title/settings/load art. Asset paths are independent of `--data`.

Windows uses the separate [manual launcher](prototype/start-manual-hd.ps1):

```powershell
& .\prototype\start-manual-hd.ps1 -DataDirectory 'C:\Games\Tyrian 2000'
```

It resolves the EXE and reviewed gameplay pack beside the script's repository,
uses a persistent dedicated profile under `%LOCALAPPDATA%\OpenTyrian2000-HD\manual-first-level`,
and creates windowed 2x/Integer settings only when absent. Later settings and saves
are retained. `-InitialScale 4x` applies only to a new profile; change an existing
profile through the normal game settings. Absolute `-Executable`, `-AssetsDirectory`,
`-StartupAssetsDirectory` and `-ProfileDirectory` overrides are available. An existing
unmarked nonempty profile is refused to avoid overwriting personal saves. Default current-pack materialization requires Python 3 and Pillow;
see [NEWSH2 base267 authoring](docs/CRAFT267_SINGLE_SOURCE_WORKFLOW.md). Original data and Windows dependencies stay external.

This is a bounded first-level manual mode, not full-campaign HD certification.
Windows runtime/device acceptance must be reported separately from source/build checks.
[Earlier bounded acceptance and open checks](docs/MANUAL_HD_ACCEPTANCE.md) record the
physical-level-9 source/unit/build checkpoint and its four headless synthetic-SDL engine runs.
The [preview launcher](prototype/start-actual-preview.ps1) and
[asset-debug launcher](prototype/start-asset-debug.ps1) remain controlled replay tools;
see [debug controls](docs/ASSET_DEBUG.md).

### Separate ASTEROID1 asteroid opt-in

A separate `--asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1` option replaces
the coherent ten-piece and two four-piece grey rock families, eight static random
rocks shared by records135–137,260–262,263–265,266–268,317–324, and record282’s fixed
gold shell and three-state jewel pulse, plus record286’s continuous four-state
rock-jewel pulse, record284’s static fork craft and record545’s static silver-grey
capsule with a red lower tip on normal-data Episode 1 physical level 1
(ASTEROID1, campaign section 5). Other artwork stays classic.
Use ordinary campaign progression; this flag does not select or play a level.
It cannot be combined with the existing manual HD or diagnostic flags. Physical
level 2 and excluded modes remain classic. See [ten-piece scope](docs/asteroid1-ten-v1/README.md),
[four-piece scope](docs/asteroid1-four-v1/README.md),
[frequent four-piece scope](docs/asteroid1-common4-v1/README.md),
[first static random-rock scope](docs/asteroid1-random5-v1/README.md),
[two static random-rock scopes](docs/asteroid1-random43-85-v1/README.md),
[large and small static random-rock scopes](docs/asteroid1-random123-95-v1/README.md),
[three small static random-rock scopes](docs/asteroid1-random114-133-152-v1/README.md),
[continuous random-rock jewel pulse](docs/asteroid1-random286-v1/README.md),
[scheduled fork craft](docs/asteroid1-fork284-v1/README.md),
[scheduled capsule enemy](docs/asteroid1-capsule545-v1/README.md), and
[gold-wing identity and bounded validation](docs/asteroid1-goldwing-v1/README.md).
These are fifteen bounded second-stage families, not a completed second stage or Windows acceptance.

### Optional external MP3 music

Add `--music-dir` to replace selected songs with your own MP3 files:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --music-dir=/absolute/path/to/my-music
```

Use exact lowercase names `track01.mp3` through `track41.mp3`; for example,
`track18.mp3` replaces **Tyrian, The Level**. Missing, rejected or over-limit files
fall back to the original FM song independently. Without this option the original
music path, including its first-song behavior, is unchanged. Original game data,
including `music.mus`, is still required for timing, fades and fallback.

The Windows manual launcher accepts an existing absolute directory, including
paths with spaces or Chinese characters:

```powershell
& .\prototype\start-manual-hd.ps1 -DataDirectory 'C:\Games\Tyrian 2000' `
  -MusicDirectory 'C:\Music\我的配乐'
```

MP3s are decoded before playback, downmixed to the existing mono output and
resampled to the actual device rate. Original song-end/loop controls and volume
fades remain authoritative; MP3 EOF wraps independently. Input is limited to
32 MiB and 10 minutes, final PCM to 64 MiB, and tracked temporary allocations to
256 MiB. This does not promise universally gapless MP3 loops. Keep user songs
outside the repository and public packages. See the [full track list, controls,
limits and verification boundaries](docs/EXTERNAL_MUSIC.md).

### Optional manufacturer cards

A release/NDEBUG build can use the two reviewed manufacturer cards during its
normal local startup:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-settings-v1
```

Run from the repository root, or give an absolute asset-directory path. The
retained complete pack includes PIC10 (XSIV GAMES) and PIC12 (ECLIPSE), layered title
art and the supported UI typography described below. It does not enable gameplay
HD by itself. Missing, invalid or incompatible cards fall back independently to
their originals.
Original fades and skip/input code are preserved. Do not combine this option
with network, render-test or asset-debug modes; those combinations are rejected.
Without this option, ordinary startup remains classic. Debug builds reject it
because their original startup skips the cards.

[Historical startup contract and checks](docs/STARTUP_MANUFACTURER.md) record passing source/
unit checks and 12 bounded actual-engine executions: native-sized 2×/4×, original
fades, queued key/held-mouse skipping, independent missing-card fallback and
classic title handoff. These used SDL dummy/software; physical desktop/GPU,
fullscreen, physical joystick and Windows runtime remain untested. Instrumented
clips/timings are not original-speed or FPS proof. This option does not provide
manual-gameplay HD coverage.

### Optional layered title

The same complete startup pack includes the two manufacturer cards, PIC4
background and independently moving Tyrian and 2000™ logo layers:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-settings-v1
```

The original 29 positions, split art/UI fades, version, menu/highlight and cursor
writes are retained. Missing resources fall back per layer; invalid ownership
returns the whole title to classic. Earlier subset directories have been retired;
see [historical pack recovery and rebuilds](docs/RETIRED_HD_PACKS.md).
[Historical title contract and checks](docs/STARTUP_TITLE.md) record eight passing cases / 13
actual-engine executions: native 2×/4×, independent missing layers, keyboard/mouse
menu and cursor erase, Instructions/settled restart, fade-time input and the real
30-second idle demo handoff. A further media-free merged regression matches all
142 original-state/output presentations. These use SDL dummy/software; timings
include observer overhead. Explicit title CPU storage peaks at 12,075,752 bytes,
plus one nominal 4,096,000-byte SDL texture. Physical GPU/fullscreen, Windows,
physical joystick and demo gameplay remain untested; gameplay HD selection is unchanged.

### Optional title menu typography trial

The same nine-file complete pack includes the reviewed medium-font V3.1 lettering
alongside the manufacturer/title artwork and settings/load typography:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-settings-v1
```

Native 2×/4× retain their accepted output exactly. Other valid output sizes use
font-only coverage reduction and premultiplied linear magnification, while title
art keeps its original sampling. Only the seven main-title rows use the new glyphs.
Original colors, indexed text, widths, centering, hit boxes, input, palette fades
and cursor remain authoritative. Missing or incompatible typography restores the
whole classic menu while valid title art remains active. Version text and gameplay
HUF1 remain separate; Settings/Load typography uses the same complete pack as
explained below. Ordinary startup without the option stays classic.
See the [historical protocol and acceptance](docs/TITLE_MENU_FONT.md) and
[current output-portability checks and limits](docs/TITLE_MENU_FONT_PORTABILITY.md),
including actual 1920×1200 and odd/letterboxed software output.

Windows: use the [build entrypoint](prototype/build-game.ps1) and
[setup/acceptance limits](docs/WINDOWS_HANDOFF.md). These instructions do not
constitute a new Windows build or runtime acceptance claim.

## Resources and evidence

The [manifest](assets/hd/manifest.json) defines current pack defaults and hashes;
older reports retain checkpoint-specific counts. See [terrain/circuits](docs/CIRCUIT10.md),
[forest material](docs/FOREST13_WORLD_CANOPY.md), [HUD frame](docs/GAMEPLAY_HUD_V5.md),
[labels/shield/mode](docs/GAMEPLAY_HUD_COMPONENTS_INDICATORS.md),
[corner V2](docs/GAMEPLAY_HUD_CORNER_V2.md),
[fixed green labels](docs/GAMEPLAY_HUD_FIXED_TEXT.md), and
[gameplay tiny font](docs/GAMEPLAY_HUD_DYNAMIC_FONT.md), and
[remaining meters](docs/GAMEPLAY_HUD_METERS.md) for exact scope and fallback limits.
Upstream attribution and [COPYING](COPYING) are retained.

## Upstream README (preserved)

OpenTyrian2000
================================================================================

OpenTyrian2000 is an open-source port of the DOS game Tyrian. It is a fork of
OpenTyrian, with the end goal being to replicate the experience of Tyrian 2000
as closely as possible.

Tyrian is an arcade-style vertical scrolling shooter.  The story is set
in 20,031 where you play as Trent Hawkins, a skilled fighter-pilot employed
to fight MicroSol and save the galaxy.

Tyrian features a story mode, one- and two-player arcade modes, and networked
multiplayer.

== Additional Necessary Files ==================================================

OpenTyrian2000 requires the Tyrian 2000 data files, which have been released
as freeware:
  https://www.camanis.net/tyrian/tyrian2000.zip

== Keyboard Controls ===========================================================

alt-enter      -- toggle full-screen

arrow keys     -- ship movement
space          -- fire weapons
enter          -- toggle rear weapon mode
ctrl/alt       -- fire left/right sidekick

== Network Multiplayer =========================================================

Currently OpenTyrian2000 does not have an arena; as such, networked games must
be initiated manually via the command line simultaneously by both players.

syntax:
  opentyrian2000 --net HOSTNAME --net-player-name NAME --net-player-number NUM

where HOSTNAME is the IP address of your opponent, NUM is either 1 or 2
depending on which ship you intend to pilot, and NAME is your alias

OpenTyrian2000 uses UDP port 1333 for multiplayer, but in most cases players
will not need to open any ports because OpenTyrian2000 makes use of UDP hole
punching.

Note that Network play has not been tested for OpenTyrian2000.

== Links =======================================================================

* For OpenTyrian2000
project: https://github.com/KScl/opentyrian2000

* For OpenTyrian
project: https://github.com/opentyrian/opentyrian
irc:     ircs://irc.oftc.net/#opentyrian
forums:  https://tyrian2k.proboards.com/board/5

### Optional settings typography

The retained nine-file complete startup pack includes the six manufacturer/title/menu
resources and smooth large, medium and tiny settings lettering:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-settings-v1
```

Only Setup, Graphics, Sound and their pickers are enhanced. Native nearest
2×/4× preserve the accepted compositor; other valid output geometry, including
filtered/aspect output, uses the font-only portable path. Original colors, PIC2,
bars, cursor, indexed text, metrics, input and saved settings remain authoritative.
Missing or incompatible SFN1 files keep the complete settings menu classic while
valid title resources remain usable. Ordinary startup without the option stays
classic.
See [current output handling, fallback and validation](docs/SETTINGS_LOAD_FONT_PORTABILITY.md).
[Protocol and bounded acceptance](docs/settings-font-v1/ACCEPTANCE.txt) include
paired actual-engine controls, fades and lifecycle checks on SDL dummy/software,
plus source/sanitizer and retained-still author review. Physical GPU/display and
Windows execution are not claimed. Reproduce the exact nine files with
`python3 prototype/settings_font_bundle.py --output /absolute/new/directory`.

The same `startup-title-settings-v1` pack supports bounded Load typography with
the same portable output path. Unsupported names, source data or resources retain
whole-frame classic fallback. The [output-portability note](docs/SETTINGS_LOAD_FONT_PORTABILITY.md)
updates the geometry limits in the [historical Load usage](docs/load-font-v1/USAGE.txt).

The same `startup-title-settings-v1` pack now covers Players/mode, Episode,
Difficulty (including original unlock rows) and Timed Battle selection. These
four selectors map font coverage to actual output/viewport geometry; native
2×/4× and an odd 1365×767 output passed bounded software-renderer checks.
Title/Settings/Load output handling is documented above. The same pack now adds
text-only support for the ordinary single-player pre-game root and Upgrade Ship category; item
purchase pages and original ship/background artwork remain unchanged. Keep the
same `--startup-assets` directory and
existing large/medium SFN1 filenames; no new artwork is required.
[Selector scope, cursor fallback and acceptance limits](docs/selector-font-v1/NATIVE-ACCEPTANCE.txt).
