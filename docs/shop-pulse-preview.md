# Live shop Pulse preview: independent observer

## Scope

This slice reuses the five accepted global Pulse resources (80058, 80059,
80060, 80062, 80165) in the **ordinary front-weapon product preview only**.
It introduces no art and does not authorize any battle, rear, sidekick,
other-weapon, terrain, or enemy draw. Resource 80059's -1 anchor is already
baked into the accepted pixels; it is not applied a second time.

The actual `JE_weaponViewFrame` still creates and simulates the original
projectiles. The original bank-8 blitter still writes every INDEX8 sample.
The observer does not change positions, timings, power/cash, random state,
audio, item selection, or shot allocation. No battle tick or battle front-call
proof is borrowed. There is no generic sprite-index replacement permission.

## Independent proof

`shop_pulse_proof.inc` binds the original raw port-1 record, including its disk
name bytes, and complete 80-byte weapon records against the existing global
registry. It authenticates a separate shop lifetime, preview tick, front-call
generation, and allocation-slot generation. A birth must occur inside the
ordinary front-port-1 call; named shot fields, phase, position, and TTL must
match that record. Every accepted head must be exactly the next original
simulation step from the prior witnessed birth/head. Duplicate, skipped,
recycled, out-of-context, changed-selection, or changed-table witnesses do not
revive a retired birth. Raw table reloads also retire old witnesses.

The pregame owner grants this envelope only while its authenticated category-3
product update is building. Exits and product rebuilds retire the shop proof.
Source bank pointer/size, all five decoded source tiles, canonical shop palette,
all used weapon records, global root, reference/missing/invalid flags, and the
loaded immutable RGBA payload hashes are checked separately from birth.

## Ordered composition and failure

`shop_pulse_render.inc` records a `C_PULSE` command only when the scoped normal
blitter agrees on surface, source pointer, index, x/y, and every ordered original
indexed write. Each command replays the original indexed samples for exact
verification and later classic arithmetic, while its HD samples composite over
the true pre-draw underlay. Later classic/interface/font/cursor writes retain
their established ordering and occlusion. The accepted 8x RGBA is reduced to
the pregame owner's fixed 4x canvas with alpha-weighted 2x2 area sampling.

If source, palette, table, resource, root, or reference proof fails, the command
is replayed as classic indexed content; unrelated accepted frontend layers are
not discarded merely because Pulse art is unavailable. A failure after a
contribution latches for the remaining command frame, so restoring bytes or a
flag cannot resurrect that frame's retired HD content. A fresh authorized
preview tick establishes new proof. Owner disposal frees all five payloads.

A Pulse command necessarily splits the formerly coalesced classic preview
background and interface writes. The event pool is therefore bounded at 65,536
entries rather than 40,000; it never coalesces across an authored command.
Capacity exhaustion rejects the frontend frame without changing the original
simulation or indexed drawing. The 16 MiB compile-time owner budget includes
additional fixed head-proof/art allowance, and runtime accounting includes the
new payloads and state.

## Reproducible checks

- `tests/shop_pulse_integration.py`: reverse-projects the actual allocator,
  simulator, and shop preview function to the accepted base, and checks all
  existing assets and battle-family implementations remain unchanged.
- `tests/shop_pulse_proof_test.py --data ORIGINAL_DATA --sdl-root SDL_SYSROOT
  --sanitize --receipt RECEIPT`: isolated production proof with original data
  passed only through process memory; no original bytes are written into tests.
- Existing global Talon/Shield/Pulse/Hitflare/Vulcan reconstruction suites remain
  battle-only shims. Their explicit no-op SHOP hooks do not claim native shop
  proof.
- Native validation uses real title/selectors/shop navigation, original input
  selection and preview calls, all 11 front powers, wrong front/rear negatives,
  exit/reentry, and classic/frontend/full/reference comparisons. Its one
  high-cash fixture is explicitly disclosed; shot/item/RNG state is not patched.
  Captures are bounded and losslessly compressed.

This document describes the adapter contract, not a substitute for the separate
hash-frozen native and independent-review receipts.

## Accepted validation (2026-10-21)

- Birth/lifetime proof: ASan+UBSan, **41,993 assertions**.
- Independent composer: ASan+UBSan, **41,092 checks**, including cold missing/
  corrupt/header resources, allocation failures 0–4, warm source/payload/
  palette/root/reference invalidation, ordered occlusion, sampling, and exact
  event/command-capacity refusal. These tests use synthetic command arms, not
  a claim of native birth.
- Existing pregame typography: ASan+UBSan, **126 states / 16,252 checks**.
- Battle regressions: Talon 365, Shield 354, Pulse 551, Hitflare 200, Vulcan
  1,008 cases passed; unchanged family implementations and assets.
- Final native four-mode route: **521 presents / 299 shop frames per mode**;
  exact indexed/backup/palette, shot state, RNG, economy/items, and audio-call
  parity. Full mode recorded **706 accepted heads**, all 11 powers and all five
  existing assets. Wrong front, rear, missing global root and reference modes
  recorded zero replacements.
- **36 paired full/frontend captures**, 23 visually changed; zero differing
  pixels outside the union of original head ink and authored alpha support.
  Exit/reentry restores live proof. A full frame and 11-power contact sheet were
  visually inspected.
- Native peak: **42,546 events / 329 commands / 10 simultaneous heads**;
  **12,150,322 retained bytes**, below the 16 MiB cap.

Independent review accepted the exact eight production-file and Visual C++
project hashes recorded by the final composer receipt, matching native source
freeze. Captures remain losslessly compressed; no original game data is bundled
with this implementation. Local commit/checkpoint is distinct from publication.
