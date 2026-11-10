# Compound 309–312 integration handoff

Status: artwork complete; runtime integration and in-game qualification pending.
This batch includes 12 HDR1 slices, their PNG counterparts, three assembly
previews, three untouched imagegen masters and exact generation prompts.
`review-three-phases.png` packs the assemblies left-to-right as phases 0/1/2.
`candidate-pins.inc` gives proposed NEWSHS RGBA pins in archived table order.
Neither file changes an accepted runtime pin or enables the sidecar.

## Recommended narrow opt-in path

Extend the current `experimental/level2-family/src/normal270_family_mirror.inc`
behind a separate compound enable flag. Do not wholesale restore the older
`experimental/late-level/sources/9a69cfe175a0bbc0/compound309270_family_mirror.inc`:
the current sidecar adds stronger event-pointer, sequential script and mutable
script validation that must remain in force. The archived file is a reference
for compound lifecycle semantics, not a substitute for current hardening.

1. Admit records 309–312 only with the compound opt-in. Existing record270
   behavior, native pin tables and three bank8/role141 artwork pins stay intact.
2. Extend event matching, current-event validation and level-begin checks to
   events242/243 when opted in. Require exact type12/time1840/record309,
   x66 or162 and link24 or25. Retain event244/245 checks and all level guards.
3. Permit offsets0..3 for events242/243 only; retain offset0 for244/245.
   Use distinct consumption bits `(event-242)*4+ofs` for242/243 and
   `8+event-244` for244/245. Each component remains an independently witnessed
   allocation. Allocation failure consumes that component's origin.
4. Observe event-begin/commit around each native type12 component allocation,
   without changing native construction, movement, collision or link behavior.
   Keep existing allocation/initialization/reuse/bank-change/retirement hooks.
5. Include images0..11 in image lookup, load, readiness, current-resource checks
   and shutdown only for the opt-in. Use candidate-pins.inc's verified new
   hashes, never disable the source/record/palette/resource pin checks.
6. `f270_dependencies` currently hardcodes cycle<=6. Use the record-specific
   bound, 6 for270 and20 for309–312. Source, shape, allocation placement and
   animation branches already retain compound logic but need execution tests.
7. Prepare a dedicated runtime pack with these12 HDA resources and unchanged
   normal270 resources. Have the launcher check all exact SHA-256 hashes and
   report compound status separately. Preserve default-off operation and
   curLoc<1960/eventLoc<=259. No extension beyond this reviewed scope is implied.

## Required qualification before acceptance

- Verify default-off retains previous behavior and no compound assets load.
- Test all eight242/243 component admissions, all three phases, normal270
  regressions, allocation failure, replay, wrong event/offset/pool, source and
  record mutation, altered RGBA/header/size, bank reuse and linked retirement.
- Test both bottom components and invariant top housing; audit callback order,
  exact672-cell support and alpha255. These are opaque foundation tiles, not
  transparent cutouts. Never punch holes in the native occupied rectangle.
- Build the actual experimental executable and observe all four records in
  the real event sequence with contribution/material counters and captures.
  Static checks and preview sheets cannot prove in-game use or visual quality.
- Inspect seams, neighboring terrain, clipping, firing timing, palette fit,
  native/HD switching and death/overdraw behavior at gameplay scale.

## Validation performed 2026-11-10

12 tests passed normally and under `python -O`. Both runs rebuilt every
candidate byte from the privately held pinned NEWSHS bank and matched the
checked-in candidate file list and bytes. Exact record/base/phase/quadrant,
RGBA FNV, master SHA, native sequence, fixed housing and pairwise distinct
bottom phases are tested. Original RGB reference and game data remain private.
All masters and phase assemblies were visually inspected. No new imagegen
call was needed because the existing complete generated masters were retained;
no synthetic replacement artwork or source RGB was introduced.
