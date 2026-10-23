# Selected revision and corrected physical pose assignments

Records163/167 use the six user-approved fine-v2 candidate bytes, unpainted and
unmodified. Record168 retains the old v1 artwork; neither rejected fine-v2 nor
unapproved single-master-v3 art is installed. All remain default-off opt-in.

The audit found a real historical labeling error, not a renderer animation bug:
original167 strip columns are base3/1/5, but old normalization named them1/3/5;
original168 columns are55/17/93, but normalization named them17/55/93. Fine-v2
inherited those filename labels. Corrected assignment uses **physical column**,
not filename sort order. `selection.json` binds original-reference RGBA hashes,
column numbers, explicit physical base IDs and selected candidate hashes.
`physical-column-audit.json` records independently decoded strip-cell equality
with individual original reference sprites. Hashes alone do not prove pose;
the audited source-column correspondence supplies that evidence.

`historical-mislabeled-v1/` preserves the complete previous source bundle as
historical evidence, **not valid pose acceptance**. Existing Git commits and
historical runtime fixtures remain unchanged. The new regression rejects first-
two pose swaps even if the mutable art hashes are repinned. A future intentional
art revision must explicitly review/version this selection authority as well.

Editable filenames retain `v1-bbox-fit` solely for consumer-path compatibility;
the current provenance identifies the actual generation, transforms and selected
hashes. Two fine-v2 raw generation PNGs and the exact normalizer are retained here;
its original workspace-dependent paths are provenance, not a portable build kit.
No original game image/binary is included in this documentation bundle.

The compiler changes eight payloads: six fine-v2 and two reassigned old168.
Record168/base93 is byte-identical. Roles2100000–2100008, original bank/record/
palette pins, logical24×28 density8, anchor(6,7), and selectable enemycycle poses
are unchanged. These are not automatic three-frame animations.

Fine-v2 retains the prior outer bounding envelopes by physical column, **not
exact silhouettes**. Gray mask IoU against prior artwork is approximately0.73–
0.75; inner form/centroid changes remain real. There is no new blur, sharpening,
mask clipping, forced event spawn, gameplay mutation or default-on activation.
Build/package tests do not establish actual-game observation; see the separate
new-revision validation receipt for native and assisted-game evidence.
