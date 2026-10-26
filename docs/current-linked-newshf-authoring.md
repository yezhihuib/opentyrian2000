# Linked NEWSHF171–173 authoring

Final creative artwork was visually reviewed and locally applied on2026-10-26.
Synthetic fixture pixels are tests only and were not installed as production art.

Fixed inputs under `authoring-inputs/newshf-linked/`:

* `cold-whole.png`: RGBA 192×672 (24×84 logical at 8×).
* `alternate-middle-overlay.png`, `hot-bottom-overlay.png`: RGBA 192×224 each.
* `mask-{43,45,81,83,119,121}.png`: immutable audited 24×28 native masks.

All authored alpha is binary. Transparent overlay pixels inherit the cold
master; opaque overlay pixels replace RGBA, not blend. No generated creative
strokes or resampling occur. Slice boundaries are exactly y=0,224,448,672.
Each slice is then registered to its nearest8× original mask, with transparent
RGB zeroed. Artwork must cover every original opaque pixel; alternate121 has
11 different mask cells, so its overlay must cover newly opaque cells as needed.
One shared cold edit propagates to both states except explicitly overridden
alternate pixels. Alternate overlays may only touch the exact40/63 native RGBA-difference cells, enforced by immutable change masks. Middle83 is a mechanical piston extension, not a glowing firing state. Top43/45 derives identically from one slice; there is no top overlay.

Identity order is 17143,17145,17281,17283,173119,173121; IDs2100009–2100014.
All outputs remain24×28, anchor(6,7), density8. Native cycle is A,B,B,A.
The naturally observed firing combination is43/81/121, **not45/83/121**.
Middle83 is latent: tooling support does not claim ordinary gameplay capture.
No actor synchronization, gameplay timing, collision or weapon changes occur.

Selection schema `opentyrian-linked-newshf-authoring-v1` has exactly `schema`,
`version`, and `inputs` (fixed eleven input paths mapped to SHA256). Native mask
hashes are additionally immutable constants, so updating the selection cannot
authorize altered geometry.

```
python scripts/build_current_linked_newshf.py --root "$PWD" stage \
  --selection /absolute/candidate.json --destination /external/new-stage
python scripts/build_current_linked_newshf.py --root "$PWD" apply \
  --destination /external/new-stage
python tests/test_current_linked_newshf_authoring.py
```

Stage is read-only for the repository. Apply rederives and compares the entire
finite plan and every staged byte before writes; stale inputs, tampered bytes,
and unexpected temporary paths fail. Handled write failures roll back, but
power/process loss is not transactional. This builder installs only the art
bundle, mapping and separate generated header; production bindings/package
manifests require separate reviewed refresh. Old nine-pose headers/assets and
historical evidence are never rewritten. `load(root)` independently regenerates
and verifies every installed PNG, transport, mapping row and header byte.

## Reviewed raw registration

`register_linked_newshf.py` registers the reviewed cold V2 raw (SHA256 pinned)
using crop `(80,250,646,1830)` resized to192×552 and placed at(0,0) on192×672.
This deliberately excludes8.38% of raw alpha mass (thin outer side-plate rims,
upper cap and bottom lip). Applying original native masks clips another3.50%
of resized opaque pixels. It preserves **game** silhouette/anchors, not the
complete AI-generated silhouette. Cold coverage has zero holes, full192-pixel
top edge, and full192-pixel rows on both sides of y224/448 slice seams.

Alternate raw images use the exact same transform. Only immutable native
state-difference regions become overlays; raw transparent pixels remain
transparent. The registration receipt records raw/output SHA256 and metrics.
The parent reviewed cold, actual-bottom-hot and latent-middle composites covering
all six resources before local stage/apply. Future artwork changes require a new
review; registration alone does not approve them.
