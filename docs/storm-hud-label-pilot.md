# STORM HUD heading pilot

Bounded implementation based on `50449c21e74063223d9f77028398498351cdfe8b`.
The runtime source and authored resource were qualified at local source commit
`b3e4a3200680dad6c82a7e2b0260d3d3777e6a5e`; later packaging/documentation adds no
runtime source or artwork changes. This document does not authorize publication.

## Exact scope

Only the five-row **STORM** heading embedded in OPTION_SHAPES (bank5), zero-based
sprite37 (25×13), is refined. The original option9 identity is Plasma Storm,
icongr38, weapon88, ammo6. Initial admission is normal data, episode1,
local single-player, LEFT0/RIGHT9, Normal physical level9 or Hard physical level15.
The exact current mode and option tuple are checked at draw and display.
Unsupported left placement, siblings, Christmas, demos, networking, arcade,
bonus and other modes remain classic. Siblings are inventory only.

The finite output rectangle is half-open `[284,82,309,87)`: 125 logical cells.
The original lower eight icon rows and the ammo gauge starting y95 remain
untouched. The runtime source guard covers all325 original icon cells,
including172 transparent source cells. Transparency is distinct from opaque
index0; original slot clearing establishes the index0 backdrop.

## Original writes and history

Observer-only begin/end calls surround the existing JE_drawOptions slot
clear/blit/gauge, without changing any original argument, branch, order or write.
Admission requires a gameplay PIC3 hash, exact surface/pixel/format/pitch identity,
fixed sprite dimensions/size, exact bytecode hash, decoded indices and coverage
hashes, one complete29×16 zero clear, and each original opaque sprite pixel
observed exactly once. The completed full325-cell footprint must match.
An interrupted/nested draw is not admitted. A left-slot operation cannot move
the right-slot lease. Observed unsupported equipment invalidates it.

Every pixel/rectangle callback runs the independent observer before the normal
mirror's active/surface early returns. Any subsequent write intersecting the
whole original icon revokes the record even when its value is unchanged.
Gauge writes start below that footprint and cannot invalidate it.
Surface identity mutation observed during a callback revokes the lease.
OPTION_SHAPES free/reload explicitly resets its generation, including allocator
reuse. Reset, HD shutdown and level/PIC changes revoke all history. Suspension
and renderer release revoke recorded draws; simply restoring identical indexed
pixels or beginning another frame cannot reacquire them. A new real completed
JE_drawOptions call is needed, so some modal-return cases intentionally remain
classic until that redraw. No broad modal-continuity claim is made.

## Presentation and palette

After the renderer copies current composed RGB into its locked texture, a fresh
preflight rechecks source, complete indexed footprint, scope and optional art
integrity. Every subpixel of the full25×13 region must equal its current classic
palette projection. Any existing HD overlay therefore wins even if its INDEX8
values happen to coincide. A source, footprint, palette, RGB, cache or layout
failure revokes the draw record until a new original draw. A full source/view
generation reset instead requires a new authenticated gameplay PIC3 start as
well as the completed original draw.

Only the locked texture's25×5 rectangle is changed. Original INDEX8, composed
output, canvas, ownership masks, fade snapshots and palette arrays are read-only.
Each successful display starts with another full texture copy, so no cached
STORM output can survive a later rejected display. The old classic glyph is
fully removed within the owned rectangle before antialiased authored strokes
are projected onto current palette[0]. All coverage values, including zero,
are composited. Green roles192–207 are the only accepted authored indices.
The accepted artwork uses197–201.

The baseline full RGB palette hash is fixed. A different palette is accepted
only when the existing renderer actually executes an accepted fade step and
provides that exact palette. The grant expires on a normal frame begin,
suspension or fresh right-slot transaction. The global current RGB palette,
not SDL's palette allocation identity, is the projection authority. Black,
white and restore fades therefore follow the actual current palette0 and green
entries without needing a new retained true-color fade layer.

No ordinary per-frame allocations, filesystem reads, RNG calls, simulation
state changes or gameplay callbacks are introduced. Static resource budget is
20,000 authored bytes plus a small source/history ledger. The texture-only layer
is visible in native renderer readback; old game_probe exports of retained output
are intentionally not sufficient evidence of this layer.

## HSI1 resource

`gameplay-hud-storm-label-v1.hda` is optional in the selected asset directory.
Both default packs contain the same resource. The fixed96-byte little-endian
header pins magic/version, dimensions25×5, both densities4/8,20,000-byte payload,
full source25×13/230-byte identity, original PIC3/palette hashes, and the exact
reviewed authored payload hash. Reserved fields are zero. The fixed payload is
4× index2000,4× coverage2000,8× index8000,8× coverage8000.

The loader checks the opened object is a regular file, exact length, complete
bounded reads, EOF and successful close. Missing, malformed, oversized, truncated,
corrupt, wrong-source or unsupported resources independently fall back to the
published classic heading. FIFOs cannot block the POSIX loader. Source validation
precedes optional resource loading and every cached payload lookup. Authored
payload bytes are hashed again on each display, so poisoned cached art fails
closed. Data-file changes require a new gameplay resource capture; no file watcher
or hot replacement is implied. The asset directory is a startup-only CLI
setting in production. A valid in-memory resource survives disk removal/corruption
until the next capture, while missing-at-start does not recover merely because
the disk file later appears. A new authenticated start reloads the selected root.

Reproduce the authored planes with
`python3 assets/hd/artwork/gameplay-hud-storm-label-v1/build_assets.py --output /tmp/storm-art-fresh`,
using a fresh output directory. Compare those planes to checked-in generated
planes. Pack the checked-in planes
with `python3 assets/hd/artwork/gameplay-hud-storm-label-v1/pack_resource.py`.
Neither script reads original game assets. Original indices, bytecode, palettes,
private native screenshots and hooks are not distributed.

## Standalone checks

- `python3 tests/run_gameplay_hud_storm_tests.py`: strict C99 synthetic source,
  history, cache, palette, lifecycle, negative-resource and4×/8× exact-delta tests;
  also ASan+UBSan. LeakSanitizer is disabled by default because ptrace-based
  executors cannot run it; this module performs no allocation.
- `python3 tests/test_storm_source_inverse.py`: removes only observer integrations
  and proves every pre-existing source file byte-identical to the baseline.
- The existing Makefile picks up the new portable C module automatically.

These tests use independently generated synthetic fixtures and source hashes.
They do not substitute for native gameplay trace/indexed/RNG equality, true native
2×/4× readback, original-data identity checks or visual acceptance. Arbitrary
unobserved memory edits that are restored entirely between observer/display calls
are outside the mutation model; known production source reload paths are hooked.

## Fresh qualification and reproducible packs

The sanitized receipts in `docs/storm-hud-label-v1/` record the separate gates:

- `BUILD.json`: exact source, original-data, executable and dependency hashes;
  fresh clean baseline72/candidate73-translation-unit builds; reversible private
  observer patches. Both full builds use the same explicitly recorded baseline
  warning exemptions with `-Werror`, and emit no warnings. An earlier integration
  attempt without the inherited misleading-indentation exemption failed and is
  excluded from the successful build claim. New standalone core/adapter tests
  use strict C99 and sanitizers without those warning exemptions.
- `UNITS.json`: synthetic density4/8, malformed-source/resource, history, palette,
  lifecycle, adapter-scope and source-inverse checks. All153 pre-existing source
  files are byte-identical after removing only the finite observer additions.
- `RUNTIME.json`: ten pairs, twenty processes,6,880 logic ticks and484 actual
  native captures. Four main Normal/Hard native2×/4× pairs and four missing/corrupt
  resource pairs run320 ticks; two Normal/Hard native2× refill pairs run440 ticks.
  Original state/RNG/INDEX8/palette/draw traces match every tick. All212 paired
  gameplay captures have exact retained output and no uploaded/native RGB change
  outside the125-cell heading; all30 paired shop views are unchanged. Both modes
  deplete at tick140 and genuinely regain ammo at415 without state injection.
- `ASSETS.json`: both optional sidecars reproduce exactly; all3,436 fresh pack
  files match the repository, all6,879 earlier asset files other than the extended
  manifest remain exact, and all old manifest fields are preserved.
- `AUTHOR_REVIEW.json`: actual native visual inspection and precise limits.
- `INDEPENDENT_REVIEW.json`: separate source, synthetic, adapter, native capture,
  packaging and privacy review of the qualified source/art.

Both native scales select internal density8. Density4, alternate palettes,
unsupported equipment/modes and interrupted/reload/modal histories are separate
unit/adapter evidence. Final RGB is checked at20 or26 sampled ticks per process,
not every logic tick. No dedicated native fade sequence, Windows/GPU/fullscreen,
performance, whole-level or campaign certification is claimed. Suspend/release
deliberately falls back until a new completed original option draw.

Run `python3 prototype/build-hd-assets.py` to verify the complete existing pack
catalog plus this optional sidecar. Add `--output /tmp/fresh-hd-packs` to rebuild
into a new directory. The finite manifest family names exactly the two current
default packs; older rollback packs are not extended. The original art-stage
README/contract status is retained verbatim as creation-stage provenance, not a
statement of the later integration qualification recorded here.

No original game payloads, private traces, gameplay captures, test hooks or
executables are included in this patch.
