# Shared NEWSHF turret / pod family — current authoring

This private extension starts at qualified local dual-missile commit
`d2937f0471de5f9b967dfdab4314aad213d5a928`. It is not a publication receipt.
Runtime and actual-scene qualification are recorded separately; this document
alone does not assert Windows, full-campaign, or user visual acceptance.

## Canonical editable source

`authoring-inputs/newshf-turret/cold-master.png` is the one generated full, opaque
192×224 pod master. The fixed shaped `pod-composition-mask8x.png` blends that
master over `native-peripheral-source.png`, preserving exact original outer
ground pixels rather than drawing a rectangular new-ground patch. Original
fully covered interior cells are omitted from the peripheral source; all used
peripheral cells and the composition matte are immutable pinned inputs. `hot-overlay.png` changes only the immutable original
22 native cells in `native-hot-mask.png`. The hot image is alpha-composited on
the same derived, ground-composited cold image. The V1 full-ground candidate was superseded after actual scene inspection.
V2 preserves the original peripheral ground. Both derived 24×28-at-8× transports remain fully opaque:
the brown backplate is part of the original sprite, not transparent scenery.
All seven original animation slots map to these two derived images.

Raw image-generation output, exact prompts, registration recipe and original
candidate metrics are kept under `provenance/`. They are source provenance,
not a claim that the raw image is a game-ready resource. No original game data
files or banks are bundled. The pinned peripheral source contains only the
required 408 extracted original ground cells; 264 fully covered cells are omitted. The current candidate was reviewed locally under the automatic
project workflow; user-specific visual acceptance is not implied.

Stage and apply with `scripts/build_current_turret_newshf.py`. The complete
request hash, input closure and every staged byte are rederived before writing.
Handled write errors roll back; power or process loss is not transactional.
Editing a master does not automatically grant runtime qualification or rewrite
`packaging/current-production-validation.json`.

## Exact consumers and preserved semantics

Only NEWSHF logical bank 10, palette 5, records 162 and 840 are admitted.
Both use seven native slots `[39,41,41,41,39,39,39]`; resources 2100016 and
2100017 represent the cold and hot states. Quartet anchors stay `(6,7)`.
Record identity, original tile hashes, palette/source generations and cached
value/pose validation remain guarded. Missing either new resource falls back
for the turret group only, without disabling the prior 16 resources.

The renderer only observes the original cycle. Record 162 activates after a
normal enemy-shot slot is acquired. Record 840 activates before its enemy
allocation, including a failed allocation when the enemy pool is full.
A settled cycle 7 is valid; reactivation wraps through native animation logic.
No new clock, movement, weapon 59 ammunition, record 841, collision, smoke or
launch behavior is introduced. Zero x/y movement does not fix the body to the
screen: original background-relative positions remain authoritative.

## Additive source proof

`tests/turret_newshf_projection.py` independently qualifies all added inputs
and the exact new master/overlay outputs, then restores only its explicitly
owned current paths to the private base. Runtime source paths are kept separate
from validation wrapper paths. All prior ledger bytes and expected historical
digests remain unchanged. Current-source, P9, SHOP and cached-proof call orders
have explicit nested-chain tests; non-owned paths must pass through unchanged.

This family is entirely opaque and does not expand the dual-missile typed
ShapesY underlay permission. The new independent group uses resources 16–17;
the old dual-missile preflight and borrowing still apply only to resource 15.
