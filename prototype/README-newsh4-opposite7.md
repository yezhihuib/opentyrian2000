# Finite opposite newsh4 seven-part source integration

This append starts from published `67656d102a67cd1bd76c823a2b20f6023f7bb9f0`.
It imports the separately approved opposite-facing art for bank2/newsh4 records
73–79, bases231/233/235/267/269/271/273, link2. Each complete composite is24×28,
density8, anchor(6,7). Seven adjacent actors form a horizontal168×28 assembly.
This is not a mirror of the left/link1 artwork or a new game object.

The existing namespace102 and enemy-newsh4 prefix are reused. Slots389–395,
a separate seven-member readiness cache and an explicit allowlist are the only
renderer additions. Removing those additions restores the predecessor renderer
byte-for-byte. Left/link1 slots382–388 and its readiness function are unchanged.
All previous resources, original gameplay/startup code, terrain registry,
filters, layering, coordinates, movement, collision and explosions are preserved.

Before the first right-family replacement, all seven selected-pack resources
must pass the original HDR1 loader and exact frozen RGBA FNV-1a64 stamps.
FNV is only an accidental-corruption check; SHA256 source receipts are the
verification authority. Missing, malformed, allocation-failed, modified-alpha
or modified-RGB members make the whole right family fall back for the current
startup-selected cache lifetime. Left/right fallback is independent. There is
no4x substitution or per-frame disk I/O. Guarded disabled/missing/invalid/density
and scene modes remain effective after caching; reload is a fresh process.

Base231 must not be skipped because its first quadrant is empty. Quadrant232
has2 opaque cells; lower quadrants250/251 have34/74. The complete piece owns110
logical cells. All seven pieces retain exact original RLE opacity,2,027 cells
in total, including the asymmetric269→271 seam. Transparent RGBA remains zero.
No original indexed/RGB imagery or game data is imported.

## Frozen source and reproduction

`assets/hd/artwork/newsh4-opposite7-v1` preserves all29 package files. Its manifest
SHA256 is`fce309722a55c0f62ab563af15ff7af41b9a739d09b3099878753030ec5774bd`.
The only raster build inputs are its generated master and logical opacity mask.
Both default packs gain exactly seven8x HDR1 files; counts become400/404.

Run with fresh output directories outside the checkout:

```
python3 prototype/build-newsh4-opposite7-art.py --output /tmp/opposite7-rebuilt
python3 prototype/build-newsh4-opposite7-art.py --output /tmp/opposite7-original-proof --original-data /path/to/tyrian2000
python3 prototype/test-newsh4-opposite7-binding.py --out /tmp/opposite7-binding
python3 prototype/test-newsh4-opposite7-source-guards.py --out /tmp/opposite7-source-guards
python3 prototype/test-newsh4-opposite7-preservation.py --out /tmp/opposite7-preservation.json
python3 prototype/build-hd-assets.py
python3 prototype/tests/startup-manufacturer/test_package.py
python3 prototype/tests/title-package/test_package.py
make
```

The new binding recorder extracts the actual production functions and compares
all bank identities0–36/bases0–700 and terrain bindings to the published left
checkpoint. It verifies every quadrant and256 filters, all possible first
members, missing/corrupt members, each allocation-failure position, and cache
and disabled-mode behavior under ASan/UBSan. It explicitly tests every left
member missing/corrupt while all right bindings stay HD, and the inverse.
It also checks the partially empty231 composite and unchanged199-entry terrain
capacity. Recorder fixtures use immutable-by-workflow hardlinks; all mutated
files are independent. This recorder, rather than the historical left-only
allowlist recorder, covers current mixed left/right routing.

Source guards validate the exact generated-only inventory and output hashes,
reject altered/extra/symlink inputs and widened scope, and optionally re-decode
all1,701 enemy records, all1,010 source events and original RLE opacity.
Preservation checks every predecessor tracked file, restores its complete
manifest exactly, and checks unchanged Windows project XML/compilation paths.
No Windows compiler/runtime result is claimed.

## Bounded actual-game result

The executed source checkpoint is`ac95ac1e5bfd64bead95eee33da6d1c10e477985`.
The final renderer differs only by clarification of an inherited left-only
comment. Reverting that comment restores the executed source byte-for-byte;
no functional code or art change follows actual validation.

One no-fire predecessor/candidate pair matched all5,625 original-state ticks,
36,000 six-phase/all100-slot census rows and original draw order. At5590 all7
link2 actors were live; naturally they left through original bounds at5615–5624.
The separate link1 group appeared5614 and survived. Actual native640×4005590
exposes all support of bases231–271. Cap273 exposes1,284/2,016 support pixels;
732 are covered by original Layer3. All7,376 changed pixels are exact authored
RGB. All pixels outside the8,108-pixel support are identical; replay of later
Layer3 reconstructs the complete support exactly.

Observed live state and original collision geometry selected slot53/type76/
base267. Three explicitly artificial original Pulse155 requests at5591/5593/
5595 used damage1, ice99 and the then-live armor49. Actual collision logs hit
only the intended slot. The armor change50→49 affected only that actor; all7 linked ground
actors received the original hit filter208, then ice40 without further armor
loss. Original movement continued while iced. Drawing occurs before projectile
collision: hit filter208 appears5592, first ice filter208 at5594, and filter9 at
5595. Exact independently exposed filter208/9 pixels pass for every member.
Original later pulse/spark/effect coverage is identified from logged draw order
and kept separate from directly exposed-art claims.

Immediately before lethal5595 the live census counted7 link2 actors. All7 were
removed through original collision code, cash increased1,000, enemyKilled rose7,
and7 observed ground=true/explonum12 calls reached the original large-explosion
routine. Explonum12 means big=true with repeating TTL2, not12 repeaters.
The right strip is absent from5596. All36 native frames have exact RGBA equality
outside right support; the remaining full frames5596–5625 are A/B-identical,
including the later left wave. The pools clear after update5622, while that
presentation still draws the final faint rings. Tick5623 is the first visually
explosion-free equal frame. These are distinct original draw/update ordinals.

The lifecycle pair matches all5,626 original-state/RNG/indexed-output ticks,
21,600 six-phase census rows,26 original raw streams and95,236 normalized
original blend-operation rows. Every frame has zero coverage/classic/restore
mismatches. Author review passes intact2×, all36 ordered native-size frames and
genuine4×. The slowed12fps derivative is for viewing; raw PNGs are pixel authority.

A separate actual1280×800 native5590 readback at unchanged density8 reconstructs
all32,432 source-support pixels and original Layer3 exactly. It is not an
upscaled2× image. Cap273 exposes5,136 of8,064 native4× support pixels; the remainder stays
covered. Missing235 and same-length corrupted235 runtime fixtures fall back as
one complete right family, with zero right-HD callbacks and exact predecessor
native RGBA. Render-density4 matches its own density4 predecessor control.
Those short fixtures compare5,591 original-state ticks and all retained log
prefixes, without claiming unavailable unretained prefix hashes.

Source review, author review and exact bounded receipts are in
`docs/NEWSH4_OPPOSITE7_SOURCE_REVIEW.json`,
`docs/NEWSH4_OPPOSITE7_AUTHOR_REVIEW.json` and
`docs/NEWSH4_OPPOSITE7_VALIDATION.json`. Original game data, private hooks and
captures are excluded from Git. Existing art/startup/HUD/gameplay resources
remain byte-identical to the published predecessor.

Limits: private stationary/no-fire player setup with artificial projectiles;
no natural combat, full-level, GPU/fullscreen/physical-display or Windows test.
Early lethal precedes the left spawn, so this is not simultaneous cross-link
combat-isolation proof. Occluded cap art remains outside actual visual coverage.
