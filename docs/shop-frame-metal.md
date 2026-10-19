# Optional PIC1 static metal skin

The local candidate replaces only the static PIC1 metal on the ordinary
single-player shop root, upgrade categories, Ship Type and Shield pages.
The original cavity and list/cash/bar floors remain visible. Ships, weapons,
sidekicks, shield arcs, cash, bars, pointers and all text are still live draws.
Trial pages retain the original independent OPTION[12] frame and original PIC1
skin. Help, navigation, ship specifications and unsupported states are excluded.

## Resource and installation

`assets/shop-frame-v1/source-imagegen.png` is the approved existing OpenAI
imagegen output `exec-40e633a6-95b6-48ca-b95c-6e4927a6ea0d`, SHA256
`455e3b1b64754def2243583f9f19233eb926ea73ff546a9cc5311de1d24ab551`.
Its actual size is 1586 × 992. It is normalized with Lanczos to a 1280 × 800
working canvas, mapping exactly to 320 × 200 logical coordinates. It is not
native eight-times artwork. No new painting or equipment image is baked in.

Reproduce with Python and Pillow 12.3.0:

    python3 scripts/export_shop_frame.py

The retained 64,000-byte binary mask is an authenticated-original-PIC1 layout
constraint, not the final enlarged alpha. A narrow continuous contour is
reconstructed before export. The only explicit correction to the conservative
mask is the empty lower-left list margin x159..169/y136..181, where the original
rectangle otherwise preserved a diagonal strip of old metal. Item text starts
at x185 and is untouched. The JSON manifest records source, mask, processing,
dimensions, run count, byte count and checksums.

PMF1 consists of a 128-byte little-endian header and sorted non-overlapping
row runs, each with a start index, pixel count and straight RGBA8 pixels with
nonzero alpha. Current payload: 1,276,820 bytes; whole resource: 1,276,948 bytes.
Runtime loading has fixed bounds and verifies version, dimensions, original
PIC1/palette fingerprints, all header/reserved fields, exact length, FNV1a
payload and every run. The loader accepts only this version's approved payload.
Missing, malformed or allocation-failed metal falls back independently to the
original frame while the accepted SFN1 fonts remain active.

Copy only the exported resource beside the three existing SFN1 files in a
separate startup directory, then launch with that directory:

    install -m 644 assets/shop-frame-v1/shop-frame-metal-v1.hda /your/startup-directory/
    ./opentyrian2000 --startup-assets=/your/startup-directory

There is no automatic install into a selected art pack, and this candidate
does not alter the small selected pack or original `tyrian.pic`, shape tables,
palette, startup fonts or game data. Source PNG and layout mask are export
inputs, not runtime requirements.

## Composition contract

The indexed screen remains authoritative and unchanged. Optional metal is the
first premultiplied layer in the existing pregame presenter. All classic write
events clear its entire 4 × 4 logical-pixel footprint in order, including
same-index writes; the implementation never infers ownership from final colors.
Existing HD fonts compose above it with their existing per-run ordering.
The 40,000-event limit and contiguous no-text-segment last-write merge are
unchanged. No new C module or extra framebuffer cache is added.

Reduction uses the existing output-footprint integration. Enlargement uses the
existing continuous premultiplied sampler. Logical cells touched by any classic
write retain the original nearest reconstruction, even if text follows, so
nearby static metal cannot interpolate back over dynamic art. Cursor/filter
neighbourhoods still restore the exact original reference. Metal fades follow
the same explicitly declared ten-step transition; resources and masks are freed
with the existing pregame lease. The bounded lease budget is 11 MiB, including
the sparse payload, unchanged 4 MiB working layer and shared sampler allowance.

## Verification scope

`tests/run_pregame_font_tests.sh DATA SFN1_DIR [SFN1_WITH_METAL_DIR]` exercises
the existing font suite and the optional metal checks. `--ubsan` enables bounded
UBSan; `PREGAME_TEST_MAX_KIB=524288` bounds the test process separately from
compilation. Metal cases cover permitted pages, repeated render, ordered opaque
same-index writes, classic → partial HD font → actual 2560 output, fades,
invalidation and missing/corrupt/truncated/extra/directory/FIFO/allocation-failed
resource fallback while fonts remain available.

Actual SDL software-renderer native 640 × 400 comparisons and a native
2560 × 1600 root readback are retained separately from the offline design
preview. This is a local candidate, not a complete shop-art overhaul. Full
equipment inventories, Windows and GPU rendering are outside this bounded run.
