# Shared NEWSHF dual-missile actor 169

This is the static enemy-body family for original records **2 and 500** in
logical NEWSHF bank 10, not a weapon projectile or a new animation. Both records
use quartet 169/170/188/189. Their different movement values remain original.
The generated 12×28-at-8× single master is copied twice into one 24×28 resource
2100015 with the original anchor 6,7. Original native support is unchanged.
Transparent RGB is canonicalized when composing the pair. The original type-6
white smoke is neither painted into the master nor moved by this extension.

## Editing and rebuilding

`authoring-inputs/newshf-dualmissile/single-master.png` is the single editable
96×224 master. The fixed original mask, selection, generation source/prompt and
registration explanation are retained beside it. The canonical builder is
`scripts/build_current_dualmissile_newshf.py`; use its stage/apply workflow.
The single HDA, derived PNG, compatibility row and payload header must all match
an independent reconstruction. Records 2 and 500 share this resource but keep
separate complete 77-byte identity checks. Runtime changes do not create or
advance enemy cycles, smoke, movement, attacks, damage or collision state.

## Safe optional rendering and underlay dependency

The new resource is a third independent optional group. Missing/corrupt new
art must not disable the old nine craft resources or six linked resources.
A static dual-missile's complete visible quartet is preflighted before drawing.
Unknown foreign partial-alpha underlays stay classic for that actor rather than
poisoning unrelated HD contributions.

To render the antialiased missile over the existing ShapesY platform, the
renderer seals a typed subpixel value witness only after a valid complete
Layer1 pass including its qualified straight-edge treatment. Only guarded
ShapesY writes enter the witness. A sample must match its recorded RGB and
same-frame generation/source/surface/layout/density/geometry context. Final
and cached presentation retain and revalidate the dependency, including the
ShapesY resource payloads; a generic `hd_owner` bit or a live-frame flag alone
is never authority. Unknown writers, changed values and stale dependencies
are not silently accepted. The witness is retired with the corresponding
frame/map/root/shutdown lifetime.

The buffer costs 16,384,000 bytes at internal density 8 (15.625 MiB), and is
reused rather than allocated per actor. This is a bounded ShapesY-to-NEWSHF
composition dependency, not a general permission to blend arbitrary foreign
owners. Final/cache validation does extra work; no performance improvement is
claimed.

## Evidence and limits

The initial integration failed an actual-game comparison at tick 22: a
partial-alpha missile on foreign ShapesY HD triggered the pre-existing global
fallback guard. Those failed runs are preserved separately; they do not count
as a visual pass. The typed witness addresses that concrete observed case.

Corrected E1 physical-level 12 pairs have 43 native 1280×800 frames per mode
and 61 game states, using actual RGB-audit internal densities 4 and 8 (the
explicit render mode is last after asset options). In each density, 796,672
changed output pixels are wholly within same-tick original missile quartet
masks. The game-pixel, enemy, particle, global and RNG state hashes match the
missing-new-resource control. All 43 presentation rows stay HD-ordered,
including the formerly failing interval. Smoke behavior is unchanged; everything outside
missile support remains pixel-identical. Detailed projectile/collision traces
are header-only in this non-shooting probe, so they are not evidence of
naturally exercised attacks or collisions. Record 2's separate identity is
covered by native tests, not claimed as a natural E1L12 encounter.

Native validation covers both records, previous 15 resources, internal
4×/8×, filters/clipping, late/cached mutations and optional-group orderings.
Typed-underlay adversarial checks, old ShapesY geometry/resource regressions,
source/package compatibility and final immutable-input qualification are
required together before publication; no one focused result is the whole gate.
The scope is selected Linux SDL software-rendered scenes and fixtures, not
Windows, GPU drivers or the whole campaign.

`tests/dualmissile_newshf_projection.py` is a finite exact inverse against the
qualified **private** platform commit 68d35712770281f72b0e55f96a764c5656bc8272.
It qualifies the new family before any new paths are removed from older
inventories. The old ShapesY and linked-family ledgers and historical hashes
are preserved; new changes are not relabeled as old acceptance.
