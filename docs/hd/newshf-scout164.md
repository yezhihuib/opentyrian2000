# Shared NEWSHF record 164: three original poses

This finite rendering extension adds record 164 in logical bank 10 (`newshf.shp`).
The three original 24 × 28 poses use bases 11, 9 and 13, quartet offsets 0, 1,
19 and 20, and the unchanged anchor (6, 7). Rendering resources 2100028–2100030
occupy phases 28–30; the 31-resource witness remains within its uint32 capacity.
No movement, animation clock, allocation pool, health, collision or level event
is modified. Original pixels are not included in the source identity header.

## Finite routing and fallback

NEWSHI is explicitly phases 18–27 in logical bank 13, not all phases at or above
18. The appended scout phases resolve bank 10. Wrong phase/bank pairings reject
before composition. The independent optional three-resource group is atomic:
missing or corrupt scout art leaves this actor classic without revoking intact
unrelated groups. A group mutation after contribution invalidates retained RGB,
including cached output or pixels later covered by another actor.

“Independent group” describes optional-art loading, not independence from the
historical bank-10 source contract. The original full bank and three prototype
records remain shared source prerequisites. The new record has its own exact
77-byte identity hash and original quartet tile hashes. Record 164 is not
allowed to enter a damage-art or invented animation state.

Registered 8× RGBA masters remain entirely zero outside each original native
mask. Partial alpha and alpha-zero cells inside native support retain a proven
background instead of leaking the old body through. Whole-actor preflight uses
only the already qualified native, ShapesY layer-1 and cyan layer-2 lifetimes;
it does not add a provider or general permission to sample foreign HD pixels.
The source-owner mask, allocation generation, pose, bank epoch, resource bytes
and actual borrowed dependencies remain checked through final/cached output.

## Native row-wrap boundary

An otherwise valid actor whose quartet would physically wrap a native row is
kept completely classic before its first HD quadrant. Normal native pixel
observation remains active at the actual normalized buffer addresses and retires
any overlapping HD ownership. This prevents an unrelated previously rendered
scout from turning an ordinary offscreen actor into a whole-frame fallback.
The exception never applies after that slot has already contributed HD, while
an HD call is unfinished, or when identity/quad/source/lifetime checks fail.
Existing historic wrap tests stay unchanged; additional boundary fixtures prove
the new per-actor admission rule without admitting wrapped pixels as HD.

## Evidence scope

An unchanged pre-integration scout observed natural E1 physical level 8 straight
pose draws at ticks 160–381. Original event time 220 is not rendered tick 220.
Bases 9 and 13 were not naturally observed; any opposite-bank evidence must be
explicitly labeled controlled diagnostics, never natural three-pose acceptance.
E1 physical level 12 uses a different enemy pool, so ownership is not restricted
to a particular pool or level. The initial E1 level-12 no-fire scout ended before
the target appeared; that result is not positive coverage or a game defect.

The renderer retains its existing internal densities 4 and 8. Physical output
scales, native INDEX8/state/RNG/log parity, resource absence, old-family regression
and typed-underlay behavior require separate execution receipts. This document
is a contract, not a claim that those checks have already passed. No Windows or
complete-campaign acceptance is implied.

## Reproduction

- `scripts/check_scout164_newshf_pins.py --game-data PATH` privately rechecks the
  original source hashes without emitting original source bytes.
- `scripts/build_current_scout164_newshf.py` stages and applies the finite three
  registered masters; stage/apply preserves its explicit preflight and handled
  write-error rollback limits.
- `tests/scout164_smoke.py` is only an index/source/runtime smoke subset.
- `tests/run_scout164_qualification.py` runs the full bounded source, inventory,
  SHOP and nested projection gate against an unchanged checkout and Git index.
- Native and actual-gameplay drivers write separate receipts. Historical ledgers
  and accepted masters are never repinned to hide a failure.
