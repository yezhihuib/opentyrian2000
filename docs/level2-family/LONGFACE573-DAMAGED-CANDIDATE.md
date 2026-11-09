# Longface exact-group damaged-state and top-entry candidate

The existing `LONGFACE573_FAMILY_CANVAS_ENABLE` path now admits the four
already-packaged damaged components for actors 573–576: NEWSHD bases 167/163
and NEWSHP bases 129/125. No new switch, image or asset hash is introduced.
The family remains disabled without its existing explicit parent/family controls.
The standard HD plan already supplies those controls; this change therefore
extends that opt-in plan, not the native/default-off game.

The default HD family admits only the witnessed first group at event array
index105 / time1084. The public preset can additionally request the two exact
later groups described below. The existing source-bank/record pins, exact actor/state/base shape,
slot generation, event epoch, palette and asset checks are unchanged. All four
quadrants must complete, with body x24..264/y-13..156 geometry. The existing
full-body y0..156 path is retained; a bounded extension admits top entry at
y-13..-1. Side/bottom clipping, y<-13, filters and unknown states still fall
back or invalidate the provisional frame.

The production nonlethal damage branch keeps the object and bank: for these
records (`edani=0`, positive `edgr`, `edlevel=10`) it toggles `edamaged`, switches
`egr[0]` to the recorded damaged base, resets single-frame animation and caps
armor. It does not retire the longface witness. The lifecycle still rejects
removed/dead or replaced actors, and the `edlevel=-1` destruction route does not
match this family's shape. No gameplay or damage code was changed.

The removed entry check rejected every `edamaged` actor even though the shape,
resources and sparse native writer already cover both states. Existing per-frame
recorded gate/base comparisons remain: a damage transition after a contribution
invalidates that frame rather than mixing states. The next tick clears old
ownership and may admit the new state. No transition is synthesized by the adapter.

## Bounded top-entry extension

For body y-13..-1, production `tyrian2.c` still schedules parts0/1/19/20:
`enemy.ey=body_y+7` satisfies both upper and lower call conditions. The real
`blit_sprite2` consumes source rows above the physical buffer but does not issue
pixel callbacks for them. Because side wrapping is excluded, the adapter starts
its sparse cursor at `-tile_y * 12` for a negative tile y. It still consumes
transparent cells and requires the remaining visible native stores through the
end of each 168-cell quadrant. A wholly transparent visible remainder may
legitimately complete with no callbacks; no opaque cells are synthesized.

Callback coordinate comparisons use signed 64-bit arithmetic. Material offsets
come from the validated source cursor, not unsigned subtraction of a negative
origin. Four-part order, identity, generation, damage gate and finish checks are
unchanged. This extends the existing HD family control, with no new switch.

## Bounded offline evidence

`python3 tests/test_longface573_damaged.py` compiles the actual production
`private_longface573_shape`, `longface573_pixel` and `longface573_end` functions,
plus the actual tile geometry/initial cursor expressions and nonlethal
damage-assignment block from `tyrian2.c`. It checks
four component transitions, mismatched state/base, birth-state rejection,
zero armor and incorrect link rejection. It feeds all eight existing pinned
native-index arrays through the sparse pixel/end functions at body y-13..-1
and the previous y40 complete-body case: 24,588 opaque native writes. It checks
all visible HD cells against the eight HDA payloads, transparent cells
remaining untouched, full quartet completion and missing-write rejection.
Geometry extraction rejects y-14, y157, side overflow and unknown parts.
Each HDA's alpha is checked against every corresponding native mask cell.

This is a data-free extraction harness, not the game: bank-source validation and
writer readiness are stubbed valid; other-family ownership clears are no-ops;
actor fields, palette context, canvas and quartet setup are synthetic. It does
not execute event allocation, live witness checks, native RLE decoding, damage
trigger/collision selection, Present, cache retirement or gameplay. The asset
manifest/release checks verify the unchanged asset hashes separately.

These checks establish a bounded code/material candidate only. No real damaged
scene, GUI, final visible pixels or normal gameplay acceptance is claimed.

## Later groups, public-preset candidate

The source-only archive at
`experimental/late-level/sources/03c5968bda89ae17/longface573_family_mirror.inc`
contains origin pins for two additional original case12 groups:

| Zero-based event index | Time | X | Link | Components |
| --- | --- | --- | --- | --- |
| 105 | 1084 | 42 | 19 | 573–576 |
| 229 | 1616 | 138 | 19 | 573–576 |
| 239 | 1750 | 138 | 18 | 573–576 |

Only the archive's bounded origin/lifecycle extension was transplanted. The
newer damaged-state and signed top-entry writer code is retained. These pins
come from that public archived code: no original level file or independent
script dump was available in this cloud workspace. This batch does not claim
to have revalidated the event tuples against original game data.

Admission is fail-closed against the actual runtime event table. Level begin
requires every enabled row to match its time/type12/record573/x/link/zero fields
and initial dat6=4. The real case12 code selects pool75, clears dat6 to0, then
calls begin/create/position-adjust/commit for each of four components. Begin and
commit require matching current time, event position and the cleared dat6.
There are three separate four-bit consumed masks; allocation failure consumes
that component's attempt, and only an actual level begin clears them. Link18
is accepted only for the third origin, not as a global link relaxation. Existing
call-token, slot-generation, bank, record and live-witness checks remain.

`LONGFACE573_LATER230240_ENABLE` must be exactly `1` at level begin and remain
unchanged; a change invalidates scope rather than adding origins mid-level.
The launcher supplies it only with `--hd --public-candidates`, never plain
`--hd`, and removes inherited `LONGFACE573_` controls. No new CLI option or
asset is added; the extra scope is eight component allocation attempts, not an
unbounded family or a promise that all allocations succeed.

The existing extraction test additionally compiles actual origin selection,
level begin, event matching, scope, event begin/commit and witness functions.
It checks default isolation, switch latching, separate origin consumption after
failed allocations, wrong pool rejection, exact per-origin links and unknown
origin witness rejection. Level mode/source/logging and reset side effects are
stubbed; slots and event rows are synthetic, so these are not live allocation
or original-event-data checks. The launcher test checks inherited-control
removal and preset-only selection. Actual later scenes remain unverified.
