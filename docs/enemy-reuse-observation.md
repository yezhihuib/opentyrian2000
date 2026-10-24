# Normal-game enemy projectile observation (default off)

This is a display-only development entry point for the already approved finite
P02/P04/P05/P09 enemy-projectile reuse contracts. It is **not** the render probe,
a new projectile family, a gameplay shortcut, an input replay, or general HD mode.

## Opt in

Build with `-DENEMY_REUSE_HD_PROTOTYPE=1`, without `RENDER_MIRROR_DISABLED`,
then pass one option:

```sh
XDG_CONFIG_HOME=/path/to/isolated-test-config ./opentyrian2000 \
  --enemy-reuse-observe-assets=/path/to/approved-hda-directory
```

Use the project's ordinary build/data setup; the switch does not install original
Tyrian data or generate asset files. The directory must exist and be nonempty as
a command-line string. Its *contents* may be empty or invalid: those resources
fail closed to original rendering, not substitute assets. Missing or corrupt
members are still checked by the finite renderer's atomic family validation.

Use an isolated `XDG_CONFIG_HOME` for development runs. This is a **normal game**:
its existing backup saves, configuration persistence, input handling, menus and
exit behavior remain operative. The observer does not disable these writes or
copy the user's real save data. Load only a separately authorized legitimate save,
or start a new game through the ordinary title UI.

Without the compile-time prototype, the new option is not consumed and the normal
unknown-option handling applies. Without the option, no observer lease is granted.
No saved preference silently enables it on later runs.

## Authority boundary

- `game_probe_enabled` stays false, and `game_probe_assets` is not assigned by this
  switch. The observer owns a separately copied, immutable asset-root string.
- Only display density is selected (`8`). Episode, level, difficulty, lives,
  equipment, RNG, events, enemy allocation and normal keyboard/mouse input are
  never selected or rewritten by the observer.
- The normal title/new-game/load flow remains reachable. No probe start, injected
  input, tick-limit exit, or synthetic enemy shot is introduced.
- The switch rejects duplicates and combinations with `--render-*`,
  `--asset-debug*`, manual/asteroid HD, HUD, or global asset options, regardless of
  order. Empty, excessively long, nonexistent or non-directory roots are rejected.
- Only ordinary single-player campaign play qualifies. Demos, recording, network,
  two-player, linked/galaga, arcade/super-arcade/SuperTyrian, timed-battle, bonus and
  Christmas-data modes remain excluded. Constant-play, forced-death and loot-test
  modes are also rejected after normal CLI parsing and by the live scope check. Keeping `!play_demo && !record_demo` is
  intentional; the original probe cannot substitute for this session.
- Physical scopes remain E1 sections 2 and 5, E2 section 2, and E3 section 1.
  Existing record/weapon allowlists narrow these further. Merely being in one of
  these sections does not establish accepted HD output.
- The ordinary broad `mirror_enabled()` authority is not expanded. An observer
  session can activate the shared compositor, but its asset admission is restricted
  to private role 146 under a single-use enemy draw lease. Private material 1470227
  remains P09-only. Player, other-enemy, pickup, HUD/font and terrain asset paths
  are not enabled by the session.
- Original bank identity, byte pins, record/weapon pins, allocation generations,
  animation transitions, per-draw witnesses, geometry, ownership, palette,
  resources and final-output proofs remain required. A candidate or intermediate
  draw is not evidence of an accepted presentation.

## Lifetime and fallback

A lease starts only at the successful original gameplay PIC3 boundary, after
normal scope validation, and snapshots episode/physical level. The renderer's
existing level-start/reset paths revoke resources and presentation state before
new level loading. Returning to the title or loading a save explicitly revokes
observer identity. Leaving normal scope or changing the episode/level invalidates
the lease; returning requires a new legitimate gameplay start, not a stale flag.

Native bank changes invalidate actor/shot provenance. New generations must pass
the original source checks again; the source bank is not permanently trusted by
an earlier observation. The CLI root cannot be changed during the session. Frame,
output-mode, palette, ownership and cache failures preserve classic fallback;
observer frames do not grant fade-cache authority.

The CLI and successful gameplay lease produce small read-only diagnostic lines.
Any renderer acceptance/rejection diagnostics describe display decisions only.
They are not probe tick control, gameplay manipulation, or evidence of human-input
replay equivalence.

## Evidence standard

Keep three claims separate:

1. **Normal entry-point reachability:** an actual full program enters normal title
   and gameplay with `game_probe_enabled == false`; a lease can be established on
   a qualifying section without state injection.
2. **Accepted output:** an original event/shot reaches all identity and final-output
   checks in that normal run. If the run never reaches the event, report that limit
   rather than adding lives, skipping events, changing equipment or injecting shots.
3. **Strict paired noninterference:** existing native production-object harnesses
   compare matching simulation/RNG/INDEX8 states and deliberate negative controls.
   Two manually played runs with different input timing do not establish this.

A release receipt should list macro-off/default-off checks, CLI cases, normal and
excluded modes, lifecycle tests, empty/corrupt resources, role-isolation and native
mutation/fallback controls separately from live UI observations. Do not report an
unrun phase as passed. This change authorizes neither GitHub publication nor runs
on the user's notebook.

## Local validation, 2026-10-23

Baseline: `6488220464055166c69267abee7b3a11b41fe16b`. The baseline worktree
was left unchanged; this change uses a separate worktree. No artwork or original
game-data bytes were changed. No GitHub upload or notebook execution occurred.

- Opt-in Linux binary SHA-256:
  `6b4632bf17aa5d571d07ec1badadbb47174d7e2b119129edea18f016f161b729`.
- With the same toolchain and fixed build-version string, the default-off
  binary is byte-identical to baseline:
  `d98d83cdeddacf862a417825e15028c930d7ddcbf0cb69fde10960344f11ce21`.
  Mirror-disabled binary is also byte-identical:
  `58cfd6ebf7c14b0a56b1b76ddbaec52a7eaf1985422da263a0e84e20cdc49602`.
  Every source file in all three build snapshots matches the final worktree.
- CLI: 23 cases passed, including order-independent conflicting asset/probe
  switches, empty/invalid roots, duplicates, and normal CLI cheat/record/network
  rejection. Macro-off binaries retain their original unknown-option behavior.
- Native production-object validation with source-stability checks and
  ASan/UBSan passed: 271 existing P09/P05 setups and 32 observer setups,
  195,913,857 assertions total. **New observer-mode positives cover only the two
  P09 profiles**, not every approved family and not actual full-game events.
  Checks include 19 excluded modes, all 149 tested non146 roles, same-level lease
  revocation, zero-contribution mode changes, five in-place mutations, and seven
  independently selected empty/missing/corrupt resource roots.
- Existing P02/P04 native regression passed separately: 310 cases and 79,076
  assertions. Deliberately broken RGB-store, swapped-mapping and bank-pin
  implementations were all caught by independent native assertions, without
  sanitizer errors. All five final native receipts bind the final production
  source hashes; intermediate source-changing runs are excluded.
- Source/history binding: 20 focused tests and the 265-source production binding
  passed. Runtime packaging: 40 tests passed. Historical ledgers are preserved;
  the observer has its own whole-blob and finite-hunk inverse and exact new-module
  pins, rather than relaxed old assertions.

Live cloud-desktop UI evidence is deliberately narrower. An early build entered
Full Game → Episode 3 → default Normal → unchanged-equipment Start Level →
**Gauntlet**, then naturally died; pause/resume, return to title and normal exit
worked. The original campaign order did **not** reach CAMANIS, so no approved
observer lease or HD-positive event was observed. The final binary was separately
confirmed to show the complete title menu and exit normally; no level was entered
in that final check. These runs used only normal UI controls and an isolated
`XDG_CONFIG_HOME`. Screenshots existed only as CUA session images, not persistent
PNG artifacts. ALSA had no device, so audio is not validated. Manual UI runs do not
establish paired simulation equivalence.

Detailed build, CLI, native, source-binding and UI receipts are retained locally
under the sibling `enemy-observe-validation` directory. Earlier intermediate runs
whose source changed during testing are retained but are **not** final passes.

The additional full historical-inverse run was **not initially green**: 54 tests,
3 failures, 1 error and 1 skip. Two stale test declarations omitted newer exact
source-inverse steps/paths; the other failure/error and consequent fixture-protective
skip came from the authoring tool's unchanged baseline source-authority digest.
The fixes preserve all historical ledgers and strict authority: exact expected
chains/paths were updated, and the authoring digest now binds all 254 non-generated
source inputs (the same 11 generated headers remain excluded). No art was changed.
After repair, the 14 affected source-projection class tests and all 8 affected
authoring class tests passed; the authoring rerun had no skips. The full 54-test
run was not repeated. Its original log and the precise passing reruns are retained,
rather than relabeling the original failed run as a pass. These non-runtime fixes
did not change the source hashes already certified by the native tests.
