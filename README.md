[English](README.md) | [简体中文](README.zh-CN.md)

# OpenTyrian2000 HD visual branch

This branch progressively modernizes OpenTyrian2000's visuals while preserving
original gameplay, logical coordinates, collisions, level data, events and RNG.
It builds on OpenTyrian2000 and OpenTyrian; the upstream README is preserved below.

## Current scope and limits

- Integrated work covers selected ships, enemies, weapons/effects, layered
  terrain, clouds and world materials. The finite single-player HUD includes
  its frame, weapon labels, shield bands, mode indicators and refined corner.
- Gameplay HD is opt-in through controlled preview/asset-debug entrypoints.
  Manufacturer cards and layered title artwork have explicit startup opt-ins below. Ordinary
  startup without those options retains classic rendering.
- Uncovered, missing or incompatible inputs use documented per-feature
  fallbacks. Pause/help/options retain classic presentation.
- Acceptance covers documented, bounded Linux scenarios, including native
  2×/4× checks. It is not whole-game, all-level, GPU/fullscreen or performance
  certification. The latest changes still need Windows runtime acceptance.
- Fixed MODE/SHIELD/ARMOR lettering and finite gameplay tiny-font rendering
  are integrated, along with finite firepower, generator and coarse armor
  meter refinement. Manufacturer PIC10/PIC12 have a separate opt-in. A separate
  combined pack adds PIC4 and the two title logos; live title UI remains classic.
  Title checks pass in eight bounded cases / 13 actual-engine executions, plus one
  exact post-merge regression. Native 2×/4×, cursor/restart and real idle handoff are covered.
  Manufacturer startup checks passed at native 2×/4× output sizes
  using the actual engine with SDL dummy/software; physical-window/GPU acceptance
  remains separate.

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

The last command is ordinary classic startup. Gameplay HD uses the separate bounded
[preview launcher](prototype/start-actual-preview.ps1) or
[asset-debug launcher](prototype/start-asset-debug.ps1), with their documented
external data/dependencies. These are controlled replay tools, not a full-campaign
manual-input HD release. See [debug controls](docs/ASSET_DEBUG.md) and the
[bounded command example](docs/FIRST30_HD_COVERAGE.md#later-windows-acceptance).

### Optional manufacturer cards

A release/NDEBUG build can use the two reviewed manufacturer cards during its
normal local startup:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-manufacturer-v1
```

Run from the repository root, or give an absolute asset-directory path. This
two-card directory replaces only PIC10 (XSIV GAMES) and PIC12 (ECLIPSE); title, menus and
subsequent manual gameplay retain their existing classic presentation. Missing,
invalid or incompatible cards fall back independently to their originals.
Original fades and skip/input code are preserved. Do not combine this option
with network, render-test or asset-debug modes; those combinations are rejected.
Without this option, ordinary startup remains classic. Debug builds reject it
because their original startup skips the cards.

[Startup contract and checks](docs/STARTUP_MANUFACTURER.md) record passing source/
unit checks and 12 bounded actual-engine executions: native-sized 2×/4×, original
fades, queued key/held-mouse skipping, independent missing-card fallback and
classic title handoff. These used SDL dummy/software; physical desktop/GPU,
fullscreen, physical joystick and Windows runtime remain untested. Instrumented
clips/timings are not original-speed or FPS proof. This option does not provide
manual-gameplay HD coverage.

### Optional layered title

The separate combined pack keeps the two manufacturer cards and adds the PIC4
background plus independently moving Tyrian and 2000™ logo layers:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-v1
```

The original 29 positions, split art/UI fades, version, menu/highlight and cursor
writes are retained. Missing resources fall back per layer; invalid ownership
returns the whole title to classic. The old two-card directory remains unchanged.
[Title contract and checks](docs/STARTUP_TITLE.md) record eight passing cases / 13
actual-engine executions: native 2×/4×, independent missing layers, keyboard/mouse
menu and cursor erase, Instructions/settled restart, fade-time input and the real
30-second idle demo handoff. A further media-free merged regression matches all
142 original-state/output presentations. These use SDL dummy/software; timings
include observer overhead. Explicit title CPU storage peaks at 12,075,752 bytes,
plus one nominal 4,096,000-byte SDL texture. Physical GPU/fullscreen, Windows,
physical joystick and demo gameplay remain untested; gameplay HD selection is unchanged.

### Optional title menu typography trial

The separate six-file pack adds the reviewed medium-font V3.1 lettering to the
existing manufacturer/title artwork:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-menu-v1
```

Native2× uses font-only coverage integration; native4× retains crisp canonical
lettering. Other output sizes use classic menu text while keeping title artwork.
Only the seven main-title rows use the new glyphs. Original indexed text, widths,
centering, hit boxes, input, palette fades and cursor remain authoritative. Missing
or incompatible typography falls back to the whole classic menu while valid title
art remains active. Version text, setup/load screens and gameplay HUF1 are unchanged.
The old five-file title pack and default pack selections are unchanged.
[Protocol and current checks](docs/TITLE_MENU_FONT.md) distinguish source/synthetic
checks from the still-pending actual-engine visual and interaction acceptance.

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
