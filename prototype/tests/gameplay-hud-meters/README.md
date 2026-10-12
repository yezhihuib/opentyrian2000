# HUM2 finite raster-history meters

Source-only implementation based on published `56efa26181cd342347f8645f1c9adefc1e45d4ef`.
This directory contains synthetic tests and source-extracted original writer
oracles. It contains no original game data, authored artwork, or captures.
Actual game rendering and visual acceptance remain a separate gate.

## Display authority and original writers

The four half-open rectangles are HUD coordinates, without the scene's x−24 crop:

| Field | Rectangle | Owner bit |
| --- | --- | --- |
| Front firepower | (289,17)–(311,20) | 4 |
| Rear firepower | (289,38)–(311,41) | 8 |
| Generator | (269,12)–(277,104) | 16 |
| Armor | (307,137)–(316,195) | 32 |

All 1,390 logical cells are matched atomically per field against accepted indexed
history. No sampler reads live player armor, weapon power, power, or lastPower.
Only nonzero accepted cells receive replacement RGB; black stays indexed black.

Four observer pairs bracket existing writes, without changing their logic:

1. The existing changed-firepower block: begin before its full clear, end after
   the segment loop. The actual write argument P is checked before any write.
   P0–P11 are supported. P12 (and larger) revokes the field before the original
   overflow: its in-box pixels can equal P11, so an in-box guard is insufficient.
2. The normal generator changed-q block: begin with original old/new q, end after
   the existing fill/erase and before its unchanged lastPower assignment. The
   onePlayerAction branch gets no notification because it paints nothing and
   skips lastPower updates. Fresh PIC3 with power900 is blank; entering this mode
   later retains whatever raster was actually painted, rather than forcing blank.
3. Armor wipe: begin before any original clears; end after the function's clears.
   A wipe is allowed to produce an intermediate blank/partial raster. No refill
   is synthesized.
4. Armor draw: begin after both original player clamps and before drawing; end
   after drawing. A0 still draws its original two-row baseline. A28 occupies all
   58 rows, hence A+1 geometry. A smaller draw without wiping preserves a higher
   earlier bar. Live state changes without drawing do not change the display.

Before each write, cached current/saved RGB ownership for that field is removed.
End verifies every actual field index, including unchanged rows against accepted
history and changed rows against the exact original write. Only then is history
renewed. Generator keeps all 92 actual uniform rows and groups only equal adjacent
palette indices 113–125. Armor keeps 58 actual rows and preserves original coarse
same-color groups: index226 heights2/4/6, indices227–239 heights2/4.

Mismatch revokes only the affected field. Merely restoring plausible pixels does
not restore authority. Full real writes may recover: valid firepower clear+draw,
generator0→90 or90→0, armor wipeA0 or drawA28. Otherwise an explicit fresh pristine
PIC3 grant is required. An invalid target, missing/mismatched notification, invalid
argument, or unexpected retained history cannot seed a partial-write recovery.

## Resource, parser and finite memory

The optional file is `gameplay-hud-meters-v2.hda` in the selected asset directory.
Frozen wrapper SHA256:
`3f8d9c35a3a9791d554a3c46f3431289c8ecd68b57419747ce3a40c225dafa4c`.

The 112-byte little-endian header is `<4s11I8Q>`:

- magic HUM2
- u32: 2,112,4,320,200,4224,51840,120832,444912,944,222456
- u64: PIC3, palette, four sections, entire payload, then reserved0

| Section | Payload offset | Bytes | FNV-1a64 |
| --- | ---: | ---: | --- |
| Eleven firepower tiles | 0 | 4224 | 92ce2a65c65f67db |
| Twenty-nine coarse armor tiles | 4224 | 51840 | 33f13810daec0125 |
| 944 unique 32-pixel RGBA rows | 56064 | 120832 | c4231771a5413868 |
| 222456 LEu16 row IDs | 176896 | 444912 | 1d129d23c2edc134 |

Payload total621808; header+payload file621920. Payload FNV is
`fcc77c108870c9db`; PIC3 `14c1441f3d5dc0e2`; palette `5e80e83992be2927`.
These are fixed compatibility/corruption guards, not authentication.

Generator lookup entry `(index−113)*17112 + 2*h*(h−1)` starts a run of 4h
material rows. Armor index226 starts at0/1152/3456 for h2/4/6. Higher armor indices
start at6912+3456*(index−227), with h4 adding1152. The whole-field guard and finite
range checks precede sampling. Authored4x pixels repeat exactly2×2 at density8.
Other densities fall back.

One attempt per shutdown opens a nonblocking regular-file descriptor, verifies
its exact size and fixed header before one621808-byte allocation, then reads and
validates all section/whole checksums, every alpha255, all row IDs0–943, EOF and
close. Missing, malformed, oversized, short/racing, FIFO, I/O or allocation
failures fail closed. No file-declared product controls an allocation or offset;
all dimensions/counts are exact constants. Index pitch arithmetic is checked.

Retained history is152 bytes, prepared row offsets600 bytes, plus small flags and
pending-write metadata. There are no new64K arrays. No I/O or allocations occur
at capture/write/sample/compose time.

## Ownership and lifetime

HUC1 and HUM2 share the already-existing component source lease and generation.
Their load/capture/readiness are independent: HUM2 can work without HUC1 and
vice versa. Owner bits1/2 remain HUC1 labels/shield; bits4/8/16/32 are HUM2. Full
component invalidations use63. Owned/retained checks and saved-generation cleanup
recognize all six bits. Removing HUC1 bits3 cannot discard a generation still
owned by a meter, and removing meters60 cannot discard HUC1 ownership.

PIC changes, reset/shutdown, mode incompatibility, or a changed surface/pixels/
format/pitch/dimensions revoke the source and stamps. Modal suspension and texture
recreation clear baked ownership while retaining the valid lease/history for the
next ordinary frame. Palette incompatibility declines ordinary HD composition.
Fades transform already-composed RGB; they never reconstruct meters from values.
Current/saved cache layout, generation (including corrupted zero), owner-tag
correspondence and presence, original index snapshot, palette, and saved-storage
availability are checked before reuse.
Unsafe cached presentation fails closed. Last-field removal clears the relevant
current/saved generation and last-owner cache, while independent HUD owners survive.

## Reproducible source gates

From repository root, run each with and without `--sanitize`:

```
python3 prototype/tests/gameplay-hud-meters/run_tests.py
python3 prototype/tests/gameplay-hud-meters/test_writers.py
python3 prototype/tests/gameplay-hud-meters/test_renderer.py
python3 prototype/tests/gameplay-hud-meters/test_no_meters.py
```

- Loader/history/sampler:898 malformed/I/O cases,9410 transition cases,1390
  per-cell mismatch/recovery cases, all1196 generator material spans, every
  supported sample at densities4/8, descriptor/allocation accounting, no runtime
  allocation/I/O. Direct sampler-only synthetic row injection is labeled and is
  not writer-provenance evidence.
- Source writers: token-exact original56efa261 bodies after removing only four
  observer pairs, with actual source-extracted rectangle/bar writers.20516 A/B
  comparisons preserve full64000 indexed bytes and relevant game state. Includes
  P12/255 overflow, both-player clamps, stale armor, wipes, blank900/history,
  generator transitions/lastPower timing, and invalid oldq.
- Extracted production compositor: independent HUC1/HUM2 resource fallback,
  per-field history, all current/saved owners, each final-field removal,
  cross-resource removal, corrupted generations/storage/source/density/palette,
  mode/modal/recreation, and whole-output black/white/restore counterfactuals.
  Eighteen independent current/saved metadata faults run through each actual
  fade_start, fade_step and present entry (54 cases), including saved-generation-
  only loss with intact current generation and both owner arrays.
- No-HUM2: exact published56efa261 versus candidate, all existing synthetic HUD
  families, full RGB/indexed/state/fingerprint/ownership/cache/fade parity at4/8.
  Both digests are `9d25d32b65aad19f`. This is not a game-run parity claim.

`verify_frozen.py --resource /external/path/gameplay-hud-meters-v2.hda` reads the
frozen wrapper and its adjacent `tile-layout.json` and
`all-generator-run-material-hashes.json`. It checks SHA/header/sections, all40 tiles,
all1196 reconstructed materials, and loads the file using unmodified production
pins. No art/data is copied into this worktree.

ASan/UBSan use leak detection disabled: this traced executor reports that
LeakSanitizer cannot run under ptrace. The two pure suites expose `--leak-check`
for suitable hosts; no LeakSanitizer pass is claimed here. Explicit allocation and
descriptor probes do pass. Linux production build and disabled-renderer syntax
are separate gates; Visual C source entries are checked, but no Windows build is
claimed. Actual rendering remains to be checked later in the existing tick5/100/
250 contexts, including density4/8, classic/no-HUM2 and relevant fade/modal modes.

Recovery correction is isolated in a preceding test-only commit. The unavailable
local-only HUL oracle dc1a2cf is replaced with published pre-HUL d2f0a36; its
normalized original MODE body is pinned to SHA256
`ce11aa104558ab266b63ce7053b3b111b00df3b93d720b3011ccbb4fae11945a` and compared
against current minus its sole original HUL notification. The corner harness also
receives its missing post-HUT fixed-function extraction/link dependency. Its
original baseline/candidate legacy digest remains `116844147d0c1645`.
