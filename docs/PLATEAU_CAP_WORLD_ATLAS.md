# Finite optional plateau-cap world material

This additive extension samples the frozen warm cap atlas on eleven Layer1,
NORMAL terrain IDs:96,97,99,100,106,107,108,109,110,119,120. IDs98/118 are zero-cap
guards. Their cap-on output equals their existing lower-material output; they
are not forced back to raw historical HDA RGB. No actors receive cap material.

The opaque768x896 RGBA atlas is density8 with a96x112 logical period. The existing
Layer1 preflight's saved world transform, positive modulo and fast row/column
offsets are reused. Clipping does not change phase; there is no new offset,
scroll-global read, map mutation, random variant or physics change.

## Exact composition and dependencies

For RGB only, the cap blend is
`(accepted * (255 - cap_weight) + cap_world_sample * cap_weight + 127) / 255`
with integer division. Alpha stays unchanged. The accepted input is the result
of the existing lower-material selection. Every positive cap weight is disjoint
from all lower primary, generated-footer and ground-footer weights, checked
against the loaded accepted lower bundle. Thus cap pixels have an unchanged
historical base underneath, while every lower-material pixel stays exact.
The whole lower40 HD rows of119/120 are protected independently.

The frozen source package is `assets/hd/artwork/plateau-cap-atlas-v1`; an external
package path may also be passed explicitly. Its pinned inventory is
`2ed570352eabad2f9e552635bf1602eac47cfcfe5ebe008de26ef2e1503d7f91`.
The source wrapper independently checks semantic cap polygons and the narrowed
108 rim profile rather than treating the inverse lower mask as a cap domain.

Before cap activation, the unchanged lower family must load, validate all61
selected source assets and complete the eight-row Layer1 preflight. Then the cap
loader validates its complete finite sidecar and the renderer explicitly checks
all13 selected cap-family sources: ten shared enabled bases,109 and both guards.
Existing HDA parsing provides header/bank/ID checks; the cap callback also checks
bank, ID, density, dimensions and anchors. One missing or incompatible source
disables the entire cap family. A cap error leaves the already validated lower
family and selected pack unchanged. An absent/incompatible lower family disables
the dependent cap. No historical pack is substituted for the selected pack.

## Bounded sidecar

The selected pack may contain `plateau-cap-world-material.pcap`:

- Header/inventory:188 bytes;13 finite records, including zero guards
- Opaque atlas:2,752,512 bytes
- Eleven masks:473,088 bytes
- Additional terrain109 baseline:172,032 bytes
- Payload:3,397,632 bytes, or3.240234375 MiB
- Whole file:3,397,820 bytes
- Additional fast lookup tables:0 bytes; existing11,520-byte tables are reused

The loader validates exact length, dimensions, version, identities, slots,
record spans and bounds before its one bounded allocation. It then checks the
compiled FNV64 and opaque atlas, nonempty masks, full109 mask, footer band and
lower-weight disjointness before activation. Runtime FNV64 detects accidental
corruption; it is not authentication. SHA256 identifies the approved source and
binary package. No payload allocation occurs per frame.

Whole-file SHA256:
`f6a8714193a7f837c3f931e5126399ae885f7982a7d2f320298a50f96f20dbd9`

Whole-file FNV64:`b7cd77280defa87c`.

Existing HDA files, lower atlas, lower sidecar parts, old C bundle index and
artwork packages are unchanged. The runtime payload uses the lower bundle's ten
shared bases and its two guards instead of storing them again.

## Reproduction

`python3 prototype/build-plateau-cap-world-material.py --package PACKAGE --selected-pack PACK --output NEW_EXTERNAL_DIRECTORY`

The wrapper requires the pinned inventory before output creation and before any
optional `--rebuild-art` invocation of the immutable author rebuilder. It verifies
all source file/decoded hashes, selected HDA bytes, exact lower bundle and weight
bytes, semantic boundaries, guards, and footer restrictions. It emits a separate
sidecar, generated C index and receipt. It does not write a selected pack or edit
an HDA. `--verify` checks an already installed sidecar and generated C index.
The source package's existing rebuilder can reproduce the art separately.

## Validation boundary

Standalone tests in `prototype/tests/plateau-cap` cover scalar/fast equivalence,
full/zero/partial weights, alpha, phase/wrap/clipping, unchanged lower output,
finite IDs, exact selected sources, malformed sidecars, load/source atomicity,
allocation bounds and actual extracted renderer gating. Normal and
RENDER_MIRROR_DISABLED Linux builds and the existing lower-material suite pass.
The disabled build keeps its pre-existing unused-variable/style warnings.

These source tests do not certify cap/cliff visual joins, full-game or all-map
appearance, performance, Windows, or CI. Actual native2x/4x runtime joins,
scrolling phase,109 repetition/wrap and selected-pack fallback remain integration
and visual-review gates. No gameplay run or capture is part of this source-only
implementation.

## Bounded actual acceptance

The integrated material was checked in private-survival ticks1094–1121 using original scrolling and no weapon/hit injection. All28 native640×400 frames and a native1280×800 still at1104 passed visual review. The eleven cap identities and both zero-weight guards occur in this window; occurrence is not a claim of unobscured visibility at every placement. Rare narrow forms also retain static source coverage:1,164 map contacts,134 directed types,15×108→110 and17×99-above119. No whole-map or Windows visual certification is claimed.

Every changed display pixel is within the exact positive cap support sampled from density8 at2::4, without a dilation allowance. All zero-mask pixels, lower material, ordered footer bands, guard98/118 outputs, alpha and HUD are byte-exact to the accepted cap-off baseline. A48×56 native109 patch has one identical registered RGBA hash across all28 frames while moving by the original one-logical-pixel scroll. The cap-off baseline itself matches the previously accepted lower-atlas RGB. Actual4× logical logs/RGB also match2×; SDL window dimensions differ as expected. Original wall-clock timing is excluded from deterministic control comparisons.

The new source art and cap sidecar are additive. All2,914 HDA entries,353 active canonical PNGs, existing lower bundle parts, Charge Cannon bindings and original game logic remain unchanged. Added payload is3,397,632bytes (3.24MiB), sidecar file3,397,820bytes. The96×112logical world period remains a finite repeat. No per-frame allocation, extra lookup table or gameplay FPS improvement is claimed. FNV64 is a non-security corruption check; structural bounds precede allocation.

The final actual fallback matrix passes11 runs/436 frames: absent/corrupt/truncated sidecar retains accepted cap-off RGB; missing lower dependency and changed109 each match their identical selected pack with cap disabled. Both negative controls differ from the unmodified accepted lower pack, preventing a false fallback claim. Classic and density4 each pass paired60-tick exact output/log checks. No new media was created.

The final merged renderer includes the published Charge Cannon binding and reproduces every reviewed28-frame RGB hash, deterministic log and streamed blend proof exactly; no visual recapture was needed.
