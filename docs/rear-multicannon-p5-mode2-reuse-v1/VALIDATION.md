# Rear Multi-Cannon P5 mode 2: four-head ownership and reviewed twin reuse

Baseline: `1dc8fe136bab12f45e8107bbe6a9a5fa9ffdafaf`.

Status: **PASS: bounded P5 mode 2 diagnostic qualification, independently reviewed.**

## Bounded source scope

Only player-one rear Multi-Cannon 10, power 5, mode 2, exact HDT record 269,
may receive this new ownership in the existing episode-one Normal level 9 / Hard
level 15 scope. Its full 80-byte record FNV pin is `5a43f51bab88be8b`; the
conditional port mapping is `op[1][4] == 269`. P5 mode 1 record 258 remains
classic. P1–P4 retain their previously qualified modes. Later powers, alternate
source tables, Christmas banks, linked/charged/chained/enemy consumers and
byte-identical alternate record IDs do not gain ownership from shared raw IDs.
This is partial P5 coverage, not a whole-family or full-campaign replacement.

Record 269 emits 277, 278, 183, 182. Its finite invocation budget and cyclic
period are both four, decreasing from P4's five. Ownership validates every
actual allocation and original phase, including continuation after partial
capacity. Every previously used slot in the invocation is checked for duplicates.
Existing power failure, sound, cooldown, allocation and original phase advancement
remain gameplay behavior; the observer cannot repair or advance them.

Drawable resource indices and observed source indices are separate explicit
maps. Appending 277/278 cannot accidentally turn observed-only 163/164 into
drawable rear heads. P4 mode 2 retains those two validated pass-through
observations and their original generic normal-head and shadow paths. Old source,
record and resource pin prefixes remain exact.

Records 268 and 269 share mode-2 phases 3/4 and the same live 183/182 shots.
Live shape validation alone cannot distinguish a corrupted retained record tag.
A renderer-owned per-slot birth identity seal retains the admitted record, mode,
phase, raw identity, generation and slot. Allocation clears the recycled slot;
reset clears all seals; failed current identity revokes only that birth. Normal
call/frame endings and mode/power changes preserve valid flying births. The
fixed-width hash excludes structure padding. This detects the tested individual
retagging/copy errors; it is not a cryptographic boundary against coordinated
memory corruption. No identity data is embedded in gameplay shots.

## Reviewed component assembly

New twins 277/278 reuse accepted R2 components 281/282 at offsets (0,0) and
(0,+4), on the original 12×14 logical canvas with anchor (0,0). The selected HD
convention is lower-over-upper: the translated lower component is composited
last. Original occupied pixels are disjoint and reveal no historical internal
layer order. The reverse HD order was independently compared, not inferred as
an original rule.

There are exactly five fractional-alpha overlaps per twin at each authored
density. The 984 density-4 and 3,734 density-8 nonoverlap supported samples remain
byte-exact. Support equals the translated accepted union and no occupied sample
clips. The union touches 77 logical cells versus the original 66; the additional
11 cells are inherited accepted antialias support within the same bounds.
No new generation, resampling, blur, recoloring, halo expansion or normalization
is performed.

Exact source-over uses the existing encoded RGB space, with independent half-up
quantization of alpha and straight RGB. Alpha sum falls 22 at density 4 and 12
at density 8 versus two independent copies, respectively 0.010712686% and
0.001432795%. Encoded weighted-luma falls 0.004642397% and 0.000633787%. Tiny
blue C×A sum increases of 45/22 are quantization residues, not added illumination.
These are encoded-code measurements, not physical light energy. Both reviewed
orders have identical alpha; displayed ordering differences are at most one
channel code on the tested backgrounds, with no difference at native 1×.
Offline plates are illustrative and do not qualify actual gameplay.

Only role 131 keys 1310277/1310278 receive new density 4/8 resources, under the
historical `rear-multicannon-p1-bank8` loader prefix. Existing 183/182 resources
remain byte-exact and density 8 only. Public manual-HD density 8 can replace all
four admitted mode-2 heads; private density 4 diagnostics retain classic 183/182.
Missing or invalid exact-density art falls back without changing the original
indexed writes or allocation observations. Unsupported density never causes
upward fallback or resource access.

The package builder reads only eight pinned published accepted PNG/RGBA files.
It emits the selected order only and reproduces deterministic PNG/RGBA/HDR1
bytes in isolated destinations. Original game data, decoded masks, palettes,
private observers and captures are not builder inputs or package members.

## Affordability and diagnostic attribution

A fresh ordinary-menu witness selected New Game, Full Game, Episode 1, Normal,
Upgrade Ship, Rear Gun and Multi-Cannon. The original wallet is 10,000. Cumulative
P1–P5 prices are 750, 1,500, 3,750, 8,250 and 15,750. At P4, tentative remaining
cash is 1,750 and the next upgrade costs 7,500; the ordinary Right input is refused.
The witness commits no purchase, enters no level, executes zero gameplay ticks
and leaves the actual wallet at 10,000. Tentative selection balance is not the
wallet. Source-derived maximum starter-equipment savings of 2,400 still leave
3,350 missing; those trades were not executed or claimed as an actual witness.

Consequently, no ordinary fresh-start P5 first-level gameplay is established.
The approved diagnostic protocol first genuinely purchases P4 for 8,250 through
ordinary menus. At the first level-loop entry before its first logic tick, a
private reversible hook changes only rear power 4→5 on both baseline and candidate.
It records the committed P4 shop and the separate diagnostic mutation, proving
cash remains 1,750 and all other player bytes plus RNG state remain unchanged.
Production funds, loadout, source records, seed and gameplay are not edited.
P5 runtime cases are explicitly diagnostic. Affordable P1–P4 regressions use
ordinary purchases and remain separately attributed.

## Qualification gates

Focused qualification passes against an immutable freeze of 160 source files,
7,094 assets, 50 public test files and Makefile. Only the four dedicated rear
provenance source files change; all other 156 source files and every old pin
prefix are exact. P5 core tests pass 111,657 checks per plain and ASan/UBSan build;
the actual synthetic allocator/adapter passes 615,149 plus 416 malformed resource
variants. Private authentic-source allocator/adapter tests pass 623,376 per build,
including 78 excluded physical record identities in all three original bays,
byte-identical record 1269, alternative episode records and Christmas sources.
All prior core suites, rear asset tests, source inverse and strict enabled/disabled
builds pass with their established warning profile. SOURCE_TESTS.json separates
final evidence from retained exploratory failures and pre-seal test runs.

Independent identity-seal stress tests additionally pass 7,530,132 checks per
plain and ASan/UBSan build, across 30 valid canonical record/phase births and all
80 slots. They cover individual bit mutations, copied birth-plus-seal to another
slot, retention, recycling/reset and both directions of shared-phase 268/269
retagging. Final independent integration review also passes; its distinct test counts are recorded in INDEPENDENT_REVIEW.json.

All 7,065 prior non-manifest assets remain byte-exact. The new 28-file asset
addition contains only the selected twins, metadata, builder and pack/source
copies. Removing its additive catalog rows restores exact baseline bytes.
The catalog has 3,438 pack entries, 654 source mappings and 601 entries per
default pack. Pack entries reference 613 source PNG paths; 720 PNG files
physically reside in the source directory. Those are different inventory counts.
A relocated isolated builder reproduces all 13 selected PNG/RGBA/HDR1/contract
outputs; corrupt inputs and unsafe output destinations are rejected.

Candidate native runs began only after the complete source/art/test freeze.
The fresh matrix passes 26 pairs, 52 qualifying processes and 6,480 logic ticks,
with 768 native gameplay captures and 156 native shop captures. Two baseline-only
preparation processes remain separate. Including those, all 54 processes exit zero
across 6,720 ticks, 818 gameplay captures and 162 shop captures. Each qualifying process completed on its
first launch; no game process failure or candidate retry occurred. The two initial
preparation validators retained an inherited P4-only movement expectation that
failed after the declared P5 preset. Their successful process outputs were kept
unchanged, and corrected expectations revalidated those same observations.

All 20 original-state streams are pairwise exact, including gameplay, RNG,
INDEX8 surfaces, palette, collision, allocation, shot state and original draw
order. The four main Normal/Hard native 2×/4× pairs each have 409 newly owned
record-269 head draws, joined to exact original births. All live payloads match
frozen art; every captured native frame reconstructs exactly and no change
escapes admitted original/authored support. All four heads have fully exposed
brown and cloud witnesses at both native scales and difficulties. Fractional
alpha and the original final Hard transfer remain exact; the dark filter is not
brightened to compensate for the artwork.

Eight Normal/Hard fallback pairs cover missing 277, corrupt 278, both twins
missing, and all four targets missing. The all-missing output is baseline-exact.
Eight genuine ordinary-menu P1–P4 regression pairs exercise both firing modes
with no diagnostic preset and zero changed native pixels or new admissions.
Both private density 4 cases admit only 277/278, leaving 183/182 classic.
Repeated/skipped Present preserves original-state streams and cannot advance
ownership; intentionally skipped ticks do not claim a native readback.

Both 180-tick diagnostic transition pairs use ordinary switches at ticks 60 and
100. Classic mode-1 3/41 shots survive the first switch at tick 64. Mode-2
278/183/182 births survive the switch back at tick 104; that frame does not
establish natural 277 retention. Controlled tests cover retention of every
qualified identity. Fire stops at tick 120; by tick 179 there are no new admissions
and native output is baseline-exact. Ordinary pickups may increase the wallet
after the initial unchanged 1,750 diagnostic setup balance.

Each main case observes 11,069 fractional points clipped beyond the playfield
and 726 later writes inside original ship bounds. Natural authored new-head/head
support overlap is zero and is not claimed as a runtime witness. Independent
controlled compositor tests separately exercise 240 overlap/clipping cases.
Natural partial capacity and every cyclic start likewise remain separate from
controlled allocator tests. All six reversible ordinary/Present/density-4 observer
projections restore all 160 source files with zero fuzz or offsets. Ten strict
builds pass; the 15 existing disabled-mode diagnostics remain unchanged.

RUNTIME.json records final process accounting and numerical evidence.
Independent review verifies all 26 pairs and reconstructs all 384 candidate
native frames. It rehashes all 6,946 completed observation files and 36 helpers,
reconciles all 54 process receipts, and confirms the frozen source/art/tests are
unchanged. INDEPENDENT_REVIEW.json records the full bounded disposition. Final
archive integrity and remote byte verification are separate publication gates.

## Reproduction and limits

From the repository root:

    python3 tests/run_rear_multi_p1_core_tests.py
    python3 tests/run_rear_multi_p1_adapter_tests.py
    python3 tests/test_rear_multi_p1_source_inverse.py
    python3 tests/test_rear_multi_p5_mode2_assets.py

The new art builder is under
`assets/hd/artwork/player-rear-multicannon-p5-mode2-twins-v1/build.py`; its README
requires fresh isolated output destinations. P1-prefixed test and loader names
are retained for compatibility.

Public core and adapter fixtures are synthetic. Authentic source tests and
native fixtures remain private; their sanitized hashes/results may be recorded
here without original payloads or captures. Natural partial capacity and authored
head/head overlap must not be inferred from controlled tests. A private loadout
preset cannot establish ordinary affordability, later-level availability or a
normal full campaign. Linux SDL software/dummy testing does not qualify Windows,
physical GPU performance or LeakSanitizer. No disk hot-reload claim is made.
