# LAMP272 lower-edge candidate (reconstructed, default off)

LAMP272_BOTTOM_CLIP_ENABLE=1 requests a separate narrow adapter for body
x24..264/y157..183. This does not enable the parent family or any launcher.
Existing four materials are reused. Physical native stores continue through
row199; only rows0..183 belong to the later displayed playfield. At y157..174 all four
quadrants have stores; at y175..183 only native parts0/1 are scheduled. Whole-body and top-edge guards remain intact.
Existing source, generation, writer, palette and retirement gates still apply.
Unknown boundaries, side wrapping, filters and wholly invisible tiles fail closed.

This is a reconstruction from retained code context after the first cloud
workspace was lost, NOT the old stage11 ZIP or its hash. Tests and hashes must
be established anew. No runtime admission, final visible pixels or normal
play/GUI acceptance is claimed. No laptop development or execution is involved.
Keep off pending independent review and a bounded real-source/renderer test.

Data-free test:
cc -std=c99 -Wall -Wextra -Werror -pedantic tests/lamp272_bottom_clip_contract_test.c -o /tmp/lamp-bottom-test
/tmp/lamp-bottom-test

Cloud review corrected a reconstruction error: the lower-edge adapter now
reads only `LAMP272_BOTTOM_CLIP_ENABLE`, never the top-edge flag. A regression
compiles both actual opt-in readers and exercises all 49 unset/value pairs;
requesting the established top path alone cannot activate this candidate.

Independent review also found that the production scheduler stops issuing
lower parts19/20 at enemy.ey >=182 (body_y >=175). The first reconstruction was therefore narrowed to 157..174. A subsequent
bounded extension now handles y175..183 as an ordered two-call tail, preserving
9 down to 1 visible rows rather than falling back to native appearance early.
It still consumes all 168 physical stores per top tile, not just displayed rows.
Only completion of both validated tail calls writes a per-slot frame proof;
mask3 without that proof remains invalid. Other paths still require mask15.
Parts19/20 are rejected throughout the tail; y184 and later remain native.
No new assets, switches, origins, gameplay writes or shared geometry relaxation
are introduced. A regression mirrors the scheduler and pins its source boundary.

Cloud contract checks and an integrated build are recorded separately from
runtime qualification. Synthetic contracts and compilation do not prove native
RLE replay, runtime admission, final displayed pixels, performance, or gameplay.
No game or laptop was run. The parent family and this adapter both remain
opt-in; the public preset does not enable the bottom flag. Explicit
`--hd --lamp-bottom-clip` selection is now available in the standard launcher;
see [launcher scope](PUBLIC-CANDIDATES.md).
