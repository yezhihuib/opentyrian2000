# Approved shared shop static icons

This slice installs the three user-approved normalized PNGs for NEWSH1 quads
169, 235 and 199. The 192×224 RGBA bytes are preserved exactly in SQC1 payloads;
PNG SHA-256 and decoded payload SHA-256/FNV provenance are in
`assets/shop-static-v1/manifest.json`. There is no new drawing, contour clipping,
color editing, equipment-specific alias or borrowed battle permission.

These are **shared original source identities**, not equipment IDs. In
particular quad 235 is used by multiple sidekicks and quad 199 by both weapon
and sidekick records. Any genuine original draw of that canonical quad within
the already-authenticated shop product list or ship assembly can contribute.
The original item names, price calculations, input, purchases, audio, simulation
and four indexed tile blits are untouched.

## Boundaries

`blit_sprite2x2` opens/closes an observer around its existing four tile calls.
Admission requires the pregame owner's current surface/layout/PIC1 base and
palette proof, an ordinary product build or original ship assembly phase,
actual NEWSH1 pointer/size/full hash, one of the three canonical quads, bounded
geometry and no reference/missing/invalid operator flag. Tile source indices
and masks are separately pinned. No level/stage name allowlist is involved.

Each resource is independently loaded once per owner lifetime, with exact
regular-file size, fixed geometry/header and complete payload hash checks.
Failure leaves that quad classic; another valid quad is not disabled. Root
changes dispose the owner and cache. Cached payload, source pointer/content,
palette and operator flags are rechecked at presentation. An observed failure
after contribution cannot revive that resource within the current owner.

The command records all original writes in original tile order. Presentation
replays their INDEX8 values for exact scene validation, suppressing only their
old visible artwork. Accepted 8× RGBA is alpha-weighted area sampled onto the
existing 4× frontend canvas, not re-encoded or normalized. Transparent samples
show the real pre-draw background. Later classic/text/cursor writes retain
occlusion. Existing fade gain and guarded smooth output remain in use.

## Evidence

Runtime and negative-test receipts accompany the final checkpoint. Encoding
checks alone do not claim native gameplay or Windows/GPU validation. The
packaging manifest includes three SQC1 assets in the shared startup directory;
source PNGs and provenance are retained in source but not required at runtime.
