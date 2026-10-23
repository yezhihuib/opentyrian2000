# NEWSHF168 V4 preferred max-canvas revision

This is the explicitly user-approved **max-canvas** V4, not the smaller178px
alternative. Its three unchanged PNG files are assigned to slots55/17/93 in the
approved authored column order. Original source slots are calibrated; **original
roll-direction semantics are not calibrated**. No claim that original E1 events
exercise all three poses, or that these are automatic animation frames.

The visual nose target is approximately(96.32,208) in the192×224 canvas. It is a
feature-alignment aid, **not** the engine registration point. Logical24×28,
density8, logical anchor(6,7), canvas anchor(48,56), original bank/record/palette
identity and role IDs remain unchanged. The common-scale artwork is about195px
high, approximately6.25% smaller than the prior208px envelope as accepted in the
preview. It does not use separate side-pose bbox stretching. Integer extent
rounding introduces the documented tiny per-axis quantization differences.

## Finite alpha contract

Schema2 adds `art_policy` separately from immutable original `identity`. The
legacy `identity.alpha` value remains unchanged; it describes the historical
binary source contract and does not grant a general soft-art exception.
The new policy is exactly `newshf168-v4-max-canvas-soft-alpha-v1`, record168,
bases55/17/93, straight RGBA8 with transparent RGB zero, and **three explicit
selected PNG hashes**. Unselected revision/hash/base/policy changes fail closed.
Records163/167 remain binary0/255 and all six approved fine-v2 PNG bytes remain
unchanged. Schema1 remains readable but binary-only.

Selected168 alpha-value counts are242/244/243; partially transparent pixel
counts are2,951/3,458/3,648 respectively. Final alpha1 is deliberately retained;
this revision must not be thresholded, hardened, or treated as opaque merely
because alpha is nonzero. HDR1 transports exact source RGBA bytes. Native blend,
foreign-underlay safety and final-output acceptance are tested separately.

## Provenance and reproduction

The exact selected AI raw PNG, `normalize-max-canvas.py`, and original candidate
normalization receipt are retained here. That archived normalizer depends on its
original workspace layout; the focused reproduction test independently executes
the image operations from the recorded raw source and provenance transforms.

The raw source's nominal opaque mode253 is globally scaled by round(alpha×255/253)
and clamped255; values below2 are cleared **before resizing only**. Each entire
occupied source column is cropped at full raw height783, rather than cropping
to the core-alpha bounding box. All columns use one common scale, then Pillow
RGBA LANCZOS resize, paste, and zero RGB at final alpha0. Final soft alpha is not
thresholded. The provenance matrices describe the actual quantized crop/resize/
paste transform; source_bbox is the full column, not the landmark/core bbox.

The raw neutral left wing touches x0 at eight core-alpha pixels. Full uncropped
outline fidelity cannot be certified, and no repair was invented. This is
approved authored art, not a true3D model or exact original silhouette.

## History and acceptance boundaries

`previous-binary-revision/` preserves all twelve previous source-bundle files
exactly at commit0112ec8d. Earlier mislabeled-v1 and corrected-six-fine-v2 records
remain intact in their existing documentation. Tests keep the previous strict
physical assignment authority against this snapshot, keep current163/167 byte
identity, and establish a new strict nine-source current authority.

The candidate manifests retained here are historical records and retain their
original candidate-only wording. `selection.json` is the current approved source
selection. Original/native binary data and original reference pixels are not
included. Runtime/build/gameplay results belong in the separate validation
receipt; source approval alone is not native or actual-game acceptance. No
default-on activation, laptop change, publication or forced event spawn.

## Renderer safety

The only executable change is the finite NEWSHF underlay guard: alpha below
255 now rejects a foreign HD owner, instead of rejecting only alpha zero.
The pre-existing alpha-zero/outside-native-mask no-op remains before that guard.
Opaque pixels may replace foreign RGB; partial alpha may blend over indexed
background or a proven NEWSHF owner. No general foreign-owner lifetime is
borrowed, and failed proof still rejects the complete frame, including copied
NEWSHF RGB. Native indexed writes, quadrant/mask accounting, allocation/bank/
palette leases, output cache proof and conservative fade fallback are unchanged.

The C final-output oracle independently computes rounded integer straight-alpha
blending. Coverage includes alpha 0, 1, 2, 127, 254 and 255 at densities 4/8,
filtered/unfiltered, within/outside the native mask, with indexed/foreign/same-
NEWSHF underlays. The deliberately restored binary-era guard must fail the
foreign-alpha-2 regression. See `validation.json` for executed results and the
bounded original-game observations, not a full-campaign or platform claim.
