# Level-2 terrain continuity and static border checkpoint

This is an opt-in source candidate, not a replacement for the frozen Windows
preview and not a claim that all sprites or a complete level are HD.

## What the reported preview was actually showing

The reported image identifies asset-debug level 2, tick 303. The frozen preview
uses that mode and the 23 base family controls. Most public actor candidates
require ordinary gameplay and reject asset-debug; having their files on disk
does not make them visible. The original family renderer also excluded the
shared HUD route, leaving the border as an upscale of the native image.

The original building guard rejected partially visible top/bottom quadrants,
discarding the entire HD canvas. All 20 building animation cycles were mapped;
missing animation artwork was not the cause of this specific rejection. The
preceding vertical-clipping checkpoint fixed the row contract without changing
native rendering, but exposed more event/lifetime rejection transitions. It was
not a flicker fix by itself.

This checkpoint adds two independent, default-off outputs:

- `--terrain-fallback`: on an actor-scene rejection, rebuild from the final
  native frame and retain only terrain cells proven untouched since the validated
  ground pass. Native writes retire entire cells, even when the value is unchanged.
- `--static-hud`: sample the existing approved static border using the real PIC3
  source contract, independently of scene acceptance. Dynamic text and meters
  remain native.

No old actor witness is renewed. Unknown effects, incomplete writes, palette or
storage changes, terrain/source failures, and invalid post-lock state still
reject. One recognized native blend path rejects the old scene only: the real
writer callback has already retired its exact cell, and the independent output
must still pass all final checks. General shared-HUD activation remains excluded.

## Actual asset-debug engine replay

All runs use the pinned original data, a fresh private profile, unchanged engine
objects plus a read-only actual-Present wrapper, and the frozen preview's 600-tick
mode. Only ticks 245–599 produce visible gameplay Presents: 355 frames.

| Candidate | Full-family HD | Terrain-only HD | Native world | HD/native world switches |
|---|---:|---:|---:|---:|
| Original source `88dbfb90` | 218 | 0 | 137 | 78 |
| Vertical clipping only | 276 | 0 | 79 | 86 |
| Initial independent terrain | 276 | 73 | 6 | 9 |
| Final terrain + border, 4× | 276 | 79 | 0 | 0 |

The final source digest is
`733b1bfec201243c5011235afff39ac006a917aa86c3a15139b06c34a98b5df1`;
the 112-unit Linux binary SHA-256 is
`669af09663a986a7c4ccfbd1b9e2ecf428213ee5f4d8a8470869e8e902ec9eac`.
Every native stream (`state`, collisions, player projectiles, shot emissions,
shot results and scene hits) is byte-identical to the original baseline.
The state stream includes indexed framebuffer and RNG hashes. Original input
hashes remained unchanged.

At ticks 504, 514, 542, 590, 591 and 599, the legacy blend-fallback counter still
increases and the old scene still rejects. The independent terrain Presents now
succeed. This directly distinguishes a known native blend from an unsupported
effect rather than suppressing a failure counter.

Full-family versus terrain-only output still switches 86 times. Actors can
therefore still change between HD and native rendering. Zero whole-world mode
switches in this bounded run does **not** mean zero visible sprite flicker.
At the earlier immutable integration stage, actual captured frames 334–345 were
pixel-identical with terrain fallback off on all nine accepted family frames;
only the three fallback frames changed, confined to the 264×184 playfield.
With both new options off, the final source again produces 276 HD / 79 native
Presents and 86 switches. All six native streams and all 12 captured BMP files
at ticks 298–309 are byte-identical to the clipping-only checkpoint.

## Ordinary gameplay bootstrap, final combined source

A separate harness loads original ASTEROID2 through a deterministic bootstrap
and samples keys into the original movement/firing code. Asset-debug and probe
remain off. It uses the public actor preset, with terrain fallback on in both
arms and static HUD on versus off:

- 2×, 540 ticks: 368 full-family, 158 terrain-only and 14 native-world Presents.
- 4×, 240 ticks: 205 full-family, 21 terrain-only and 14 native-world Presents.
- In each run the native-world frames are startup ticks 0–13. Every later frame
  retains HD terrain. Full-family/terrain-only actor transitions remain.
- The border is correct in all 780 frames, including native-world startup.
  There are zero authored-border or native dynamic-HUD pixel mismatches.
- All 10,140 native-state field comparisons and every actual playfield readback
  hash match the corresponding border-off run. Original input hashes are unchanged.

```sh
python3 tests/check_family_static_hud_scene.py \
  --data /path/to/original-data --out /fresh/private/output \
  --terrain-fallback --scale 2 --ticks 540
```

These are bounded original-gameplay observations, not physical-input/menu or
full-level qualification. Initial 14-frame native output is not hidden from
the counts, and static-border success is not counted as scene HD admission.

## Reproduction and scope

```sh
python3 scripts/build_level2_family.py --jobs 4
python3 tests/check_level2_preview_continuity.py \
  --data /path/to/original-data --out /fresh/private/output \
  --terrain-fallback --static-hud --scale 4 \
  --capture-start 500 --capture-count 16
python3 scripts/launch_level2_family.py --data /path/to/original-data \
  --hd --public-candidates --terrain-fallback --static-hud --check-only
```

The launcher requires explicit `--launch` to start a game. Neither new option is
included by default or silently inserted into the frozen package. Original game
data, screenshots, local diagnostic output and binaries are not part of this
source checkpoint. Existing user profiles and saves are not opened or migrated.

The independent terrain fixture checks 4,096,544 assertions with real SDL and
the actual native writer under ASan/UBSan, including 28 post-lock mutations.
The static-HUD oracle checks 13,570,686 assertions under ASan/UBSan, including
missing/corrupt resources, native dynamic cells, late writes and 2×/4× output.
LeakSanitizer is disabled. Forty-two counted regressions pass; eight frozen-package
tests require a separately supplied Windows package and remain skipped.

See [terrain ownership](TERRAIN-FALLBACK-CANDIDATE.md) and
[static border validation](STATIC-HUD-CANDIDATE.md) for their contracts.
Bounded software rendering does not qualify Windows, GPU behavior, physical
controls, menus, saves/reload, sound, a complete level, or runtime performance.
Two extra terrain surfaces use about 32 MiB, with additional resource hashing.
