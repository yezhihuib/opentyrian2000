# SHOP neutral Talon preview — accepted resource reuse

## Boundary

The small ship in `JE_weaponSimUpdate` now has its own scoped SHOP observer.
It reuses the existing global resource **90233**, without changing its header
or decoded RGBA bytes: logical 24×28, density 8, anchor (5,7).
The original `JE_drawItem` still executes once at `(player.x-5,player.y-7)`;
its four bank-9 tile writes execute once in their original order. The anchor
already describes that native origin and is **not applied a second time**.

This is distinct from the previously accepted large OPTION31 ship illustration
and the static NEWSH1 item icons. The old trial-preview exclusion in
`shop-sprite-talon.md` described that earlier slice, not a permanent exclusion.
No new art, battle pose/tick, level gate, generic tile replacement, or Pulse
birth authority is introduced. The original front/rear/sidekick/generator
navigation determines when the real preview runs; no category allowlist grants
ship eligibility. Pulse's category-3 envelope is unchanged.

The role requires the actual player-0 Talon item 1, not simply graphic 233.
The complete loaded 40-byte record (30 name bytes and every numeric field) is
serialized without host padding and pinned to `b03fc6f5a4145aae`; the terminating
name byte is checked separately. This record is identical in all three original
item-table sources. Fang item 9 happens to share graphic 233, but is not granted
this role. Custom ships, static item draws, other menus, wrong surfaces,
incorrect coordinates and unscoped quads remain native.

## Ownership and failure

`shop_ship_render.inc` authenticates a live product update, the single scoped
preview call, actual player coordinates and ship record, bank pointer/size,
the four decoded source tiles (233,234,252,253), canonical shop palette, global
resource root/operator controls, exact HDR1 metadata/length/EOF, and immutable
payload hash. Warm-cache draws and rendering revalidate source, record, palette
and resource memory. There is no second simulator and no state/RNG/audio write.

An ordered `C_SHIP` command observes every original indexed write. The compositor
replays these writes for exact indexed verification and later classic arithmetic,
while the authored pixels blend over the real pre-draw underlay. It uses the
existing alpha-weighted 2×2 reduction from density 8 to the owner's density 4
canvas. Later interface/text/cursor writes retain native occlusion and ordering;
fade uses the same established owner gain. Retained bytes include the new
172,032-byte payload and remain under the existing 16 MiB owner bound.

Invalid art falls back to classic indexed command replay, without deleting
unrelated accepted frontend layers. An observed failure after contribution
latches for that command frame: restoring a source, flag, or root cannot revive
it. A fresh valid product update can establish a new role. Root changes free
old payloads; owner disposal frees the cache. Duplicate/reentrant call attempts
and event/command exhaustion reject the frontend frame without altering native
drawing. No additional packaged asset is needed: 90233 is already included in
the accepted global resource package.

## Checks

- `tests/shop_ship_integration.py`: exact source reverse projection and unchanged
  accepted assets/battle-family implementations.
- `tests/shop_ship_composer_test.py`: isolated actual four-tile calls with original
  data read only in process memory; source/record/palette/resource failures,
  ordered replay/sampling, invalid contexts, cache/lifetime and capacity tests.
- Native navigation evidence is recorded separately from synthetic composer
  checks. Validation claims are limited to the tested Linux SDL software paths;
  these are not Windows/GPU or full-campaign claims.

### Verified candidate (2026-10-21)

The isolated composer passed **44,913 ASan+UBSan checks**; independent review
reran those and **45,368** expanded checks, including whole-output equivalence
between a retired ship command and explicit classic replay. Existing static
and Pulse composers passed 108,973 and 41,092 checks; Pulse provenance passed
41,993; shared frontend typography passed 126 states / 16,252 checks.

Ten native variants each completed 286 observed shop frames. The full 2× and
4× variants each produced 265 ship-command frames, including all five normal
equipment categories and 27 Pulse coexistence frames. Missing/corrupt resource,
reference, and same-graphic Fang negatives produced no ship HD commands and
matched their corresponding baseline output. State, indexed/backup surfaces,
palette, RNG, inventory/cash, audio queues, shots, input and call/timer traces
matched across paired runs. Independently reconstructed accepted-resource alpha
blending had zero mismatches; changed output stayed inside the original 24×28
canvas. Peak observed retained memory was 12,624,666 bytes.

These runs use a labeled deterministic-clock and initial-cash fixture, not
natural campaign progression. Front power 1/2 and rear power 1 selection were
covered; no claim of exhaustive native power coverage is made. Renderer checks
are Linux SDL software only; audio queue parity is not acoustic verification.
