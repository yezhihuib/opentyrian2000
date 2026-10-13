# Manual first-level HD: bounded acceptance

Date: 2026-10-13. Tested implementation: `365268fd7ab799297b5c4a5db13aaf1f81bab4e4`,
based on `2b36d6cae801881e31a5791aa2864b0b2d08614c`. This note and its README links
are documentation-only; the tested source, launcher, tests and artwork are unchanged.

## Entry and supported scope

Use `--manual-hd-assets=DIR` with a nonempty explicit gameplay-pack directory and
`--data=DIR` pointing to separately obtained original Tyrian 2000 data. The normal
title/new-game flow, controls, time-derived seed, damage, death, saves and progression
remain native. Only local single-player Episode 1 / physical level 9 (the first
TYRIAN level) can receive the gameplay PIC3 HD lease. Other levels, demos,
two-player and Galaga use classic rendering. Existing asset and full-frame
fallbacks remain authoritative; this does not promise complete first-level artwork.

The flag rejects all `--render-*` / `--asset-debug*` combinations and network,
record, constant, death and loot modes, including legacy spellings. Release builds
may independently combine the existing `--startup-assets=DIR` option. That
combination is covered by parser checks, not by this four-run runtime smoke.

The [Windows manual launcher](../prototype/start-manual-hd.ps1) takes an absolute
`-DataDirectory`, defaults to the reviewed green/Talon gameplay pack, and retains
a dedicated persistent profile. It creates windowed 2x/Integer settings only
when absent; `-InitialScale 4x` applies only to a new profile. An unmarked nonempty
profile is refused. Optional absolute EXE, assets, startup-assets and profile
paths can be supplied. No Python, replay, scripted input or timed exit is part of
the shipped launcher. See the [English](../README.md#manual-first-level-hd) or
[Chinese](../README.zh-CN.md#手动首关高清) invocation instructions.

## Source and build checks

- 69 real-source unit cases passed: parser/defaults and both-order conflicts;
  legacy-mode rejection; independent startup option; eligible PIC3 grant,
  lease revoke/regrant and scope exclusions; palette/fade/cache reset;
  missing/invalid assets and missing optional HUD; tick-zero Talon banking;
  diagnostics disabled and existing probe behavior.
- Linux Release and `RENDER_MIRROR_DISABLED` builds passed. The Visual Studio
  project source/header/resource inventory passed; this was not a Windows build.
- Independent source review found no remaining blocker. Original gameplay,
  input, RNG, save/config and indexed drawing files and all artwork were preserved.
  The out-of-scope forest-policy lookup found during review was fixed and checked.
- Unit fixtures do not execute the game loop. Unit state fixtures are not evidence
  of native input, naturally reached transitions or actual device behavior.

## Actual engine smoke

Exactly four executions used the unchanged Release ELF with an external test-only
`SDL_PushEvent` transport, original SDL event service, isolated profiles and finite
captures. SDL dummy video/audio plus the software renderer made these headless
checks. The transport sent keys, synthetic focus-gain and quit events; it did not
write gameplay fields or override seed, timing, level, loadout, health or survival.

1. Manual 2x: ordinary menus reached the eligible first level at 640×400. Captured
   output contained subpixel HD detail. Idle observations and Right/Left/Space
   press-release delivery were recorded; horizontal position responses, pause/
   resume and initial setup/resume were observed. Native shield loss and armor
   decrease from 10 to 9 occurred. Help dismissal/resumption was not completed.
2. Manual 4x: ordinary menus reached the eligible level at 1280×800 with HD detail.
   Quit Level returned to the classic Game Menu and revoked the lease.
3. Missing gameplay pack, 2x: ordinary gameplay entered successfully at 640×400.
   The captured output had only classic nearest-neighbor logical-pixel blocks.
4. No manual flag, 2x: ordinary menus/gameplay and return to Game Menu remained
   classic at 640×400, with the same block-uniformity result.

All four exited with code 0 through SDL quit events. The 2x/4x manual cases ended
at external test watchdog bounds; the two classic/fallback cases received explicit
quit events. Normal configuration/save files were written to their isolated
profiles. Engine working directories remained empty, with no probe/debug logs or
captures. All sampled probe/debug/demo/record flags were false and sampled
`game_probe_tick` values stayed zero. These are sampled observations, not exhaustive
per-instruction assertions.

## Limits that remain open

- No Windows execution, physical keyboard/mouse/joystick, visible desktop,
  audible audio, real focus recovery, resize, Alt-Enter or GPU/fullscreen proof.
- Fire key delivery was recorded; shot emission and cessation after release were
  not independently instrumented. Full firing acceptance remains open.
- Natural damage was observed, but death, game-over and restart were not reached.
  The long 2x case spent its final period in Help/setup, so it does not establish
  180 seconds of continuous gameplay. Help Escape entered setup; clean Help/resume
  was not established.
- Title return, title-idle demo, other episodes, later levels, first-level restart
  regrant and startup-art coexistence were not runtime-tested in this smoke.
  Scope/regrant units do not substitute for those naturally reached flows.
- Naturally seeded runs were independent. No deterministic A/B gameplay/RNG parity,
  whole-campaign coverage, sustained frame rate or performance acceptance is claimed.
  Software rendering, observation and captures affect pacing.

## Evidence identity

The frozen runtime receipt records case details and finite capture checks. Native
pixel-block detail distinguishes HD from classic output within each capture; it
is not cross-run pixel or simulation equivalence.

- Release ELF SHA256: `62b0263d7eb52a4dc640b4a9c25a1b861b4136bbfc47636cfeaa4246ec063da6`
- Tested source snapshot SHA256: `c311caf0e22c99da8a63298a57b6bf5e700639a4a298f01d86a509e6b6e87fbf`
- Runtime receipt SHA256: `958f9b711e1db1aae9956957987e6aa71b5856a19de095de12248b1d5810e3a8`
- Runtime report SHA256: `1d672e9b84b5f6acb4384338767a3471997b47cd4fd93d770ce603716c6ba9cd`
- Evidence archive: `manual-hd-smoke-evidence-365268f.tar.gz`, 12,503,818 bytes;
  SHA256 `b87276a921698ba83ba41cfb90d9994463cdc785cc8c09d63143b45cb2e013e7`.
