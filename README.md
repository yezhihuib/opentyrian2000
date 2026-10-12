[English](README.md) | [简体中文](README.zh-CN.md)

# OpenTyrian2000 HD visual branch

This branch progressively modernizes OpenTyrian2000's visuals while preserving
original gameplay, logical coordinates, collisions, level data, events and RNG.
It builds on OpenTyrian2000 and OpenTyrian; the upstream README is preserved below.

## Current scope and limits

- Integrated work covers selected ships, enemies, weapons/effects, layered
  terrain, clouds and world materials. The finite single-player HUD includes
  its frame, weapon labels, shield bands, mode indicators and refined corner.
- HD is currently opt-in through controlled preview/asset-debug entrypoints.
  Ordinary startup without those options retains classic rendering.
- Uncovered, missing or incompatible inputs use documented per-feature
  fallbacks. Pause/help/options retain classic presentation.
- Acceptance covers documented, bounded Linux scenarios, including native
  2×/4× checks. It is not whole-game, all-level, GPU/fullscreen or performance
  certification. The latest changes still need Windows runtime acceptance.
- Fixed MODE/SHIELD/ARMOR lettering and finite gameplay tiny-font rendering
  are integrated. Remaining meters are a separate candidate; startup screens
  and logos are planned work.

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

The last command is ordinary classic startup. HD uses the separate bounded
[preview launcher](prototype/start-actual-preview.ps1) or
[asset-debug launcher](prototype/start-asset-debug.ps1), with their documented
external data/dependencies. These are controlled replay tools, not a full-campaign
manual-input HD release. See [debug controls](docs/ASSET_DEBUG.md) and the
[bounded command example](docs/FIRST30_HD_COVERAGE.md#later-windows-acceptance).

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
[gameplay tiny font](docs/GAMEPLAY_HUD_DYNAMIC_FONT.md) for exact scope and fallback limits.
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
