# Finite HUD1 bottom-right corner candidate

This source-only candidate starts at `f82630507ab7f405117dc84ca70095ca04dc470a`.
It neither imports nor approves corner artwork, adds no runtime file/header,
and preserves the original V5 loader/rendering path. The original V5 resource
remains valid. Asset revision and publication are separate review steps.

## Exact contract

- Conditional rectangle: half-open `[248,184,269,200)`, 336 logical cells.
- Previous V5 ownership: 150 cells; proposed addition: 186 cells.
- V5 union corner: exactly 6,853 cells, binary 64,000-byte mask.
- Mask FNV-1a64: `b0f84ef16e11c6a2`.
- Mask SHA256: `dfc1e98e0d25b1a45645fc572d42396cf0407db975e44b3aefe91662255811b8`.
- Full decoded PIC3 FNV-1a64: `14c1441f3d5dc0e2`.
- Row-major 336-cell source-region FNV-1a64: `ca5548b4cdd8767a`.

The full-image and region hashes have different domains. Neither identifies
the artwork. As in HUD1, FNV hashes detect corruption, not authentication.
The exact mask hash is mandatory for any new corner allowance. Partial or
different unions keep the legacy geometry/count restrictions and are rejected
if they contain the proposed additions. All alpha/subpixel checks remain.

Only the exact corner mask with both source identities may own source index
zero, and only inside that rectangle. The original 6,667-cell limit and all
source-zero restrictions remain unchanged for other masks. Capture still
checks the expanded glyph moats and the full original picture identity.

`gameplay_hud_prepare_corner` compares every one of the 336 current bytes with
captured PIC3 immediately before each ordinary composition. Any mismatch
disables all 336 cells, including the 150 original V5 cells. Other HUD cells
are independent. A fresh capture does not itself prepare the corner. Invalid
input, failed capture, forget and shutdown invalidate its preparation. The
existing gameplay/PIC3 lease, modes, modal suspension, output rejection and
cache guards continue to dominate composition.

No game writer is modified. Overlong text can extend beyond the classic
`[16,189,244,198)` eraser and persist there after a shorter message or expiry.
These tails cause classic corner fallback; the renderer never cleans them.
The corner is disjoint from playfield `y < 184`, the shield channel `x >= 270`,
the normal eraser and the 82-cell HUL1 overlap elsewhere.

## Run

```
python3 prototype/tests/gameplay-hud-corner/run_tests.py
python3 prototype/tests/gameplay-hud-corner/run_tests.py --sanitize
```

The coordinate-only fixture independently pins the exact union and reconstructs
the old V5 mask using its known corner rows, with both mask SHA256s checked.
RGBA and source indices are generated synthetic data; the 46 synthetic zero
cells are not a copy of the game's source-region content. Only source identity
constants are overridden in the test build. The production mask constant is
never overridden. Production defaults are checked separately.

Tests cover every single-cell corner mismatch and whole-region fallback,
partial/wrong masks, checksums, source identity, nonbinary masks, alpha mismatch,
source zero scope, row padding, invalid preparation and capture lifetime.
The renderer oracle compiles extracted production bodies and exercises 4x/8x
output, both fades/restoration, stale cache, mode/lease rejection, suspension,
recreation and lingering message tails. `JE_outText`, its unsafe RLE writer,
and `JE_drawTextWindow` are extracted directly; only the unchanged classic
eraser's audited rectangle is modeled because no game sprite data is used.
The old V5 synthetic resource's complete output/ownership/cache/fade digest is
compared with the published base's renderer and loader.

These checks do not claim final-art visual acceptance, original game-data
runtime coverage, interactive end-to-end gameplay, or a Windows build.

## Optional selected-resource check

`test_resource.py --legacy V5_DIRECTORY --corner V2_DIRECTORY --data DATA_DIRECTORY`
reads the caller-selected resources and original `tyrian.pic` in memory. It
checks selected V2 SHA256 `98cd6cfefa02a9ae79b75a65e02dd2566d3dec1492552f20b042b3c61c19cd17`,
decodes PIC3, validates both production source identities and all 46 source-zero
cells, loads/captures original V5 and V2 with unmodified production constants,
and checks exact 4x/8x samples and atomic fallback. It also verifies every old
6,667-cell RGBA block and all bytes outside the corner are unchanged. It creates
no screenshot, game-data copy or artwork copy. This source/resource check is
distinct from the still-required actual runtime visual review. V2 is selected
by the user; rejected V1 is never read or accepted by this check.
