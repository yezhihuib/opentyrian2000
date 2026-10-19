# Optional dynamic shop shield

This presentation-only extension replaces the original terminal OPTION26 draw
with the reviewed code-native shallow arc and four soft endpoints. It is an
independent optional PSS1 material, separate from the fixed RGBA Talon, Pulse
and generator resources. Its identity is bank 5 / index 26, 99 × 23 logical
pixels, unchanged anchor (28, 23), density 4 (396 × 92 material samples).

## Live original color behavior

Each sample contains independent alpha8 and Q4 tone. For each of the two
adjacent integer tones, the presenter applies the exact original signed-byte
HV addition, Uint8 wrap and two-sided clamp before reading the current palette
at hue 15. It linearly interpolates the two RGB colors at fraction/16, rounding
channels to nearest, then uses the existing correlated-alpha compositor. The
live palette already carries accepted fades, so the material receives no
second metal/sprite fade gain. No clock, phase, RNG or equipment state is added.

The eleven actual shield values are −8, −7, −6, −5, −4, −3, −1, −3, 0, 2, 4;
None uses −10. The duplicate −3 color does not collapse equipment identities.
The shader preserves the full original Sint8 domain, including negative and
high-value legacy clamps. The current draw value is captured from the original
blitter, including temporary equipment previews.

## Bounded identity and ordering

The original ordered Talon hull, generator and first weapon calls authenticate
the assembly independently of which optional sibling files are installed. Only
root/category ship illustrations and product categories 2 (Ship Type) and
5 (Shield) may select the material. It requires exact bank/index/anchor/hue,
known source bytes, and a terminal shield position. Any shield-face call closes
the assembly even when PSS1 is absent; repeated or later reused draws cannot
select the material. Trial pages and unrelated hulls, anchors, banks, modes,
palettes or foreign pages retain their existing classic paths.

Every original indexed draw, pixel write, event and replay still executes.
C_SHIELD replays the real original writes for validation and subsequent indexed
arithmetic while preserving the true pre-shield presentation underlay. It then
composes the new continuous-alpha material last in assembly order. Later
classic writes, including same-index writes, keep their full authored-cell
erasure behavior, and cursor masks and guarded smoothing remain unchanged.

A missing, malformed or allocation-failed PSS1 disables only this material;
fonts, metal, hull, Pulse, generator and root typography remain independent.
The normal end/reset path frees it. The complete compile-time lease remains
below the existing 11 MiB cap.

## Reproducible resource

Run from the source checkout:

    python3 scripts/export_shop_shield.py --data ORIGINAL_DATA

The analytic authoring recipe creates a shallow soft ribbon and four radial
endpoints without source-mask fitting, source-raster editing or imagegen. The
original binary mask is used only to assert the existing one-logical-cell
Chebyshev support bound. Every nonzero-alpha sample passes that guard.
Reviewed assembly and eleven-state previews remain in development only.
The authoring recipe and generated geometry use the repository GPL-2.0-or-later
license; the existing COPYING notice remains in the runtime package.
The generated material is byte-identical to the accepted sample.

The 128-byte little-endian header consists of PSS1, fifteen fixed uint32 fields
and eight uint64 provenance slots. Header fields pin version, bank, index,
logical/raster geometry, density, anchor, exact plane lengths, hue, fraction
bits and reserved zero. Provenance pins PIC1 base/palette, original source RLE,
decoded indices/mask and payload. The loader rejects wrong fields/hashes,
short or trailing bytes, nonregular files, tones greater than 240, nonzero tones
at alpha zero, and support outside the existing guard. Allocation geometry
never comes from the file.

- Original RLE/index/mask FNV1a: 2b70bbc97a03a906 / b2954b44fe9312bd / b3481df839c0dec8
- Alpha/tone FNV1a: 9c0ae0f6a65255c9 / 747a5079e7a8a3ef
- Payload: 72,864 bytes; FNV1a 12adb0f5c62fab83
- Complete HDA: 72,992 bytes; SHA256 d93bf60729fc2154c0274847e01910e15484db34935d296782d7d7b218c547a2

Install the single optional HDA beside valid SFN1 resources in the existing
absolute `--startup-assets` directory. Packaging explicitly selects this one
HDA; PNG previews, plane binary, JSON and authoring sources never ship at
runtime. The previous generated runtime directory and ZIP remain unchanged
pre-shield snapshots. No game data, gameplay pack, saved loadout, original
blitter or menu code is modified.

## Verification

The focused harness uses external original game data and a directory containing
SFN1 plus the accepted optional siblings and new shield:

    PREGAME_TEST_MAX_KIB=524288 tests/run_shop_shield_tests.sh DATA COMPLETE_STARTUP
    PREGAME_TEST_MAX_KIB=524288 tests/run_shop_shield_tests.sh --ubsan DATA COMPLETE_STARTUP

The earlier plain/UBSan pregame and natural-menu suites remain applicable with
their original resource directories. Measured results are below. SDL dummy/software checks do not certify
Windows, GPU/fullscreen, purchases, all inventory traversal or full gameplay.

### Measured actual-engine checks (2026-10-19 UTC)

Eighteen bounded SDL dummy/software runs exited successfully. The full natural
640 × 400 route produced 33 paired frames with exact INDEX8 bytes and logged
cash, loadout, selection, mode, RNG and presenter ownership. Twenty-two frames
changed only within [56, 254) × [46, 92); all fixed right-menu pixels matched.
Nine trial captures, help and the fully black fade were RGB-identical. The
native 1280 × 800 root changed only within [112, 508) × [92, 184).

Missing or corrupt shield resources reproduced accepted baseline RGB, INDEX8
and state exactly. Separate actual pairs removed hull, front, generator, metal
or optional menu-run0 individually and retained the independent shield. A
missing required tiny font closed the whole lease to the same classic baseline.
Real cursor motion, idle redraw, cursor erasure, F1 help/reload/return and
sampled outgoing/incoming ten-step fades passed.

The natural inventory exercised current shield ID4/value−5 and preview
ID3/value−6. The first ship inventory has Talon and Done only; its second
selection is a Done boundary, not an alternate ship. All eleven shield values
and None are covered in the core material tests, not claimed as natural
purchases. Maximum observed runtime RSS was 23,340 KiB under the 512 MiB
address-space cap. Captures total 21,904,318 bytes, below 128 MiB; more than
8.8 GiB disk space remained free.

The focused plain and UBSan shield suites each passed 53 material states,
143 parser rejections and 65,654,619 checks. These include all eleven states
plus None, every signed-byte HV value/Q4 tone, exact indexed write traces,
full material-raster composition, live palette fades, support/mutation guards,
later-write occlusion, malformed resources, all seven optional menu-run
missing/corrupt cases, and presented RGB samples at 640/1280/2560 widths.

The legacy plain and UBSan pregame suites each passed 121 states / 13,145,147
checks. Their natural-menu coexistence suites each passed 16 states / 411,592
checks. The complete shield-plus-typography lease owns 8,209,354 heap bytes,
including exactly 72,864 additional shield bytes; static state is 809,496
bytes. Its compile-time reservation is 10,891,794 bytes, below 11,534,336.
The changed presenter passes unsuppressed C99/pedantic warning-as-error
compilation. The complete project release uses the established warning
suppressions, including its existing misleading-indentation convention;
unrelated source warnings were not changed in this batch.
