# Rear Multi-Cannon P7 mode1 reflections

The exact pinned reflections passed offline visual review. The catalog binds
only these new resources; production ownership and bounded runtime evidence are
reported separately in [validation](../../../../docs/REAR_MULTI_P7_MODE1_VALIDATION.md).
The preservation receipt and provenance are historical offline-art snapshots;
no gameplay acceptance can be inferred from a successful artwork rebuild.

The four variants are 296 = vertical reflection of accepted 277 and
297 = vertical reflection of accepted 278, each at density 4 and 8. The only
inputs are the eight pinned PNG/RGBA files from the accepted, already-composited
player-rear-multicannon-p5-mode2-twins-v1 package. The builder does not access
original game data, palettes, indexed coverage, masks, screenshots, captures or
the components used to make those accepted twins.

## Exact transformation and preservation

For every sample, target(x,y) = accepted_composited(x,H-1-y). This is a full
canvas permutation, not a crop, resampling or redraw. Logical size stays 12×14
and anchor stays (0,0). All color and alpha samples, including zero-alpha
samples, are preserved exactly. No blur, tint, normalization or brightness
compensation is applied. The accepted overlap colors are carried intact; no
source-over operation is recomputed.

The source's lower-over-upper composition is reflected as one finished image.
The same component remains foreground after reflection; that reflected
foreground is now spatially upper. Reconstructing two components and choosing
a new lower-over-upper order would be a different image and is prohibited.

Both target IDs retain 989 nonzero-alpha samples at density4 and 3,739 at
density8. Each target's full-density alpha sum is 205,342 at density4 and
837,512 at density8. Channel sums and RGB×alpha totals match their accepted
counterpart exactly; zero samples are clipped or discarded. Inverse reflection
recovers the exact accepted RGBA bytes.

Logical nonzero bounds, with exclusive right/bottom edges:

- 296: [0,4,11,14], reflected from 277's [0,0,11,10]
- 297: [1,4,12,14], reflected from 278's [1,0,12,10]

The four-logical-pixel empty vertical margin moves from bottom to top as part
of the reflection. Horizontal margins are unchanged. No canvas or anchor
translation is introduced.

## Rebuild

Python3 standard library only. Use fresh, non-overlapping output directories:

    python3 build.py --output NEW_ART_DIRECTORY --hda-output NEW_HDA_DIRECTORY

The default source is the sibling accepted package's output directory. To
relocate the builder, provide just the eight pinned accepted PNG/RGBA files:

    python3 build.py --source ACCEPTED_DIRECTORY --output NEW_ART_DIRECTORY --hda-output NEW_HDA_DIRECTORY

The builder independently checks PNG CRCs and decoded PNG-to-RGBA equality,
input SHA-256 pins, expected output SHA-256/FNV pins, reflection, bounds, sample
multiset and numerical preservation before creating outputs. Asset PNGs use
fixed zero filters and stored DEFLATE blocks for version-independent encoding.
Every generated HDR1 payload has role131, key1310296 or1310297, exact density,
logical12×14, anchor(0,0), and the exact reflected RGBA bytes after its28-byte
header. The HDA candidates are not installed into any pack by this builder.

The package path is
assets/hd/artwork/player-rear-multicannon-p7-mode1-reflections-v1.
binding.json names four catalog source PNGs and eight pack
copies, with exact hashes and headers. Existing 277/278 files are inputs only
and remain unchanged.

## Native sampling and synthetic preview limits

Direct center-nearest sampling is floor((2q+1)*density/(2*display_scale)).
The intended native phases within each logical pixel are:

- density4 → native2x: 1,3
- density4 → native4x: 0,1,2,3
- density8 → native2x: 2,6
- density8 → native4x: 1,3,5,7

Integer logical origins and anchor(0,0) retain those phases. Downsampled
reflection can select a different source Y residue class, so preserved
full-density energy does not imply equal native brightness. Across these
variants, target native alpha differs from accepted by −0.543% to +0.438%.
No corrective adjustment is applied. Density4→native4x is an exact native
reflection with equal totals. Detailed per-variant statistics, coordinates
and hashes are in output/preservation-receipt.json.

The private offline review sheets use explicitly synthetic brown/cloud
backgrounds. Normal and Hard-lit rows use identity transfer; Hard transition
and dark rows apply the source-derived Normal15 integer residual transfer
around declared synthetic before/after RGB anchors. These anchors are not
original palette samples or actual runtime indexed anchors. Magnified detail
sheets enlarge the already-sampled native image and are labeled accordingly.

Those static sheets assess bright-head/tail direction, reflected margins and
the inherited composited design. They cannot prove absence of temporal old-art
flashes, actual SDL presentation, real night lighting, indexed coverage,
same-volley overlap, slot/draw ordering, ownership restoration, later foreground
occlusion, resource-negative fallback or ordinary P7 purchase/progression.

Scope is ordinary player1 rear port10/bay1, power index6, mode index0,
exact normal-bank record260 and phases277,278,297,296. P7 mode2 record271,
byte-identical alias1260, linked/shared consumers and original shadows are
excluded. No game is launched and no gameplay state is changed by this work.
