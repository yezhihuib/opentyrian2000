# Rear Multi-Cannon P6 mode 1: bounded reuse of accepted heads

## Qualification status

**Source, unchanged artwork reuse, controlled tests, all 30 fresh diagnostic
runtime pairs and independent retained-observation restoration pass within the
bounds below. Publication and CI are separate gates.**

`SOURCE_TESTS.json` records the source/test qualification. `ART_REUSE.json`
records unchanged accepted resources and limits. `RUNTIME.json` records actual
process accounting, per-case results, observation epochs and retained failures.
The canonical runtime receipt has SHA-256
`cbe67393a6aee57c05f8b489fa1ba894ec3d7fcc6926b592e5473219ac65c0e8`.
`INDEPENDENT_REVIEW.json` records the bounded final review, SHA-256
`e24fc76e1f90775677650d127a3b5b145b14289301659e1d7c05d0e3fdebcd23`.

## Exact source scope

Baseline commit: `3db93021a3e7cc9dcc2332aeb2a8b97bca70c688`.
Baseline tree: `c90252406c0745c83b87d564a84d898f31e2b52b`.

The candidate admits only player 1, rear bay 1, port 10, power index 5,
mode index 0, exact normal-table record 259. The successful-allocation budget
is three and the cyclic phase period is three: left triple 41, right triple 3,
then downward single 77. These are distinct from the human-readable power
level P6 and mode 1. Existing episode-1 physical level 9/Normal and 15/Hard,
normal-data and ordinary-context gates remain in force.

The production guard checks the complete 80-byte record using FNV-1a-64
`f3c7e8dc12351dc8`. The independently audited record identity is SHA-256
`744d6ecf94d5b0a58e87e1ec261148cd62f73377f4cf3b1e066b9352146716f4`;
that SHA-256 identity is not a production runtime record check.
The additional port-table condition is local to record 259:
`record != 259 || op[0][5] == 259`. Prior accepted births gain no dependency on
the new table cell. Budget and period are explicit; neither is inferred from
the power index. Partial-capacity exits may change the next invocation's
starting phase, so all three cyclic starts require ownership qualification.

Only these three production files differ from the baseline:

- `src/rear_multi_p1.c`
- `src/rear_multi_p1_mirror.inc`
- `src/rear_multi_p1_pins.h`

The other 157 of 160 production source files, including `rear_multi_p1.h`,
are byte-exact. All 7,123 accepted asset and catalog files are unchanged.
The inherited original-source inverse separately restores 156 files after
removing pre-existing renderer hooks; that is a different comparison from
the 157 baseline-exact files in this P6 patch.

The original allocator, gameplay, RNG, indexed drawing, palette, shadows,
compositor and draw order are unchanged. The birth-identity seal still binds
record, mode, phase, raw ID, generation and physical slot. Allocation ordinal,
cyclic-successor validation, all-prior-slot uniqueness, per-allocation budget
consumption and recycled-slot clearing are preserved. The seal is a
non-cryptographic integrity check, not a memory-security boundary.

P6 mode 2, record 270, remains classic and receives no new admission. Shared
sprites alone grant no permission. Wrong player/bay/port/power/mode, alternative
tables, Christmas, linked/two-player, charged, chain, option, special, enemy,
menu and other excluded contexts remain outside this new route. Generic
163/164 remain observation-only specifically in this rear adapter; their
pre-existing generic HD head and shadow routes remain unchanged.
Existing 182/183 resources remain authored-density-8-only, with the previously
documented indexed fallback at density 4.

## Unchanged artwork and accepted limits

Existing rear-role 131 resources 41, 3 and 77 are reused at authored densities
4 and 8. Every selected PNG, decoded RGBA and packaged HDR1 identity was checked
against the accepted source and frozen candidate. Both default packs contain
the same accepted payloads. There is no new image generation, transformation,
recoloring, resource, catalog entry, drawable/observed index or maximum-budget
expansion.

The logical canvas stays 12 by 14 with anchor 0,0. Triples 41/3 retain their
accepted occupied bounds [0,1,12,13]; single 77 retains [4,3,8,14]. These bounds
do not assert equality between smooth authored alpha and the original indexed
coverage mask.

The previously accepted fixed-canvas tail clipping in 41/3 is unchanged.
Some outer tail samples are absent, and mild flat tips can remain visible at
native 4x, particularly over clouds. Reuse does not establish seamless taper,
whole-lobe alpha/energy preservation or a new visual approval. No clipping
percentage from a different qualification stage is substituted for a P6
measurement.

The bounded same-volley geometry calculation distinguishes coincident,
potentially overlapping age-0 spawn supports from the original first visible
age 1, after movement. Exact accepted supports are disjoint for same-origin,
same-age record-259 heads at native 2x/4x and both authored densities through
255 potential lifetime updates. This calculation does not qualify natural
cross-volley, front/rear, shadow, ship, world or cloud occlusion.

## Controlled source and resource qualification

Ten core suites pass in strict plain and ASan+UBSan builds, for 20 executions.
The new P6 mode-1 suite performs 1,039,162 checks per build; 33 compiled faulty
variants are detected. The synthetic actual-allocator adapter performs 793,072
checks per build and covers 480 malformed-resource variants. The final private
original-data adapter performs 804,170 checks per pack/build across both default
packs in plain and sanitized builds, four executions in total. These are
controlled fixtures, not natural gameplay witnesses.

The independently written core checks additionally pass:

- 8,785,152 seal checks per build, covering 35 canonical record-phase births
  and all 80 slots
- 88,095 period-three checks per build, including 3,840 cyclic prior/current
  capacity cases and 1,440 all-slot duplicate cases
- 400,374 independent original-data adapter checks per build, including all
  physical weapon records from three tables, full-record bit mutations, actual
  allocator parity, exact-density resources and retained birth identity

The qualification covers zero/full/partial capacity, continuation, recycling,
stale calls, reset, invalid birth mutations, wrong scope/source/table, prior
qualified records, exact-density loading, cache locality, missing/corrupt
resources and payload pins. All relevant existing rear-asset suites pass.
Only named executed suites are claimed; inventorying unchanged public tests
does not mean every public test was rerun.

The expanded negative inventory explicitly exercises genuine linked MegaPulse
weapons 22/38, original record 451, the actual `linkGunWeapons`, `linkMult2Gr`
and shot-direction route. The qualifier records 24 cases per pack/build,
96 executions across both packs and builds. They remain rejected without a
rear-resource lookup, preserve allocator/direction state parity and clear stale
birth metadata on recycled slots. This closes a test-enumeration gap; no
pre-existing production guard defect is asserted.

Independent synthetic forced-overlap tests use the unchanged production
compositor and exact accepted art. Each of the plain and sanitized builds
passes 216 cases, 289,004 overlap samples, 104,178 clipped samples and 7,350
checks. Both draw orders and clipping are covered. These are controlled
compositor cases, not natural runtime overlap counts.

Enabled and renderer-disabled strict production builds pass using the
established baseline warning suppressions. This is not an unsuppressed
all-warning qualification. ASan+UBSan use `halt_on_error=1`; leak detection is
disabled and LeakSanitizer is not qualified. The source inverse and
`git diff --check` pass at the source/test checkpoint.

## Acquisition boundary and diagnostic setup

Ordinary P6 acquisition has not been established. The unchanged shop code and
data give a cumulative P6 cost of 27,000 against opening cash of 10,000.
The genuine ordinary P4 purchase costs 8,250 and leaves 1,750. This price
calculation is not a P6 purchase or natural-progression witness.

The P6 diagnostic first performs that genuine P4 purchase, then changes rear
power 4 to 6 before the first gameplay tick in both baseline and candidate.
In every P6 diagnostic pair, exactly one of 784 player bytes changes; the
remaining 783 bytes, cash and all 5,016 canonical RNG bytes are unchanged.
Reversing the power change restores the player bytes. P5 regression cases
use a separately labeled 4-to-5 diagnostic; the eight ordinary P1-P4 regression
cases use genuine affordable purchases and no high-power preset.

## Native diagnostic runtime

The completed matrix contains 30 qualifying baseline/candidate pairs:

| Pairs | Actual coverage |
|---:|---|
| 4 | Normal/Hard, actual native 2x and 4x |
| 8 | Missing 3, corrupt 41, missing 77 and all three missing; both difficulties |
| 10 | Prior P1-P5; both difficulties, with P5 separately labeled diagnostic |
| 4 | Mode switches, retained births and fire-stop clearing at native 2x/4x |
| 2 | Explicit authored-density-4 controls |
| 2 | Repeated/skipped-Present controls |

All 60 qualifying game processes exit 0. They cover 7,680 logic ticks, 856
native game captures and 180 shop captures. Independent review reconstructs
428 candidate native frames against their paired baseline observations and
verifies 4,968 newly admitted head draws. Every pair preserves all 20 original
state/input/drawing streams, actual seed/startup state and exact shop output.
All sampled differences stay inside qualified original-plus-authored support.

Each main case has 292 new record-259 draws and exact live payload identity.
All three reused heads have fully exposed brown-background and cloud-background
witnesses in all four main cases, including original Hard lighting. Independent
review verifies 24 selected full-density witnesses and 48 exact native comparison
tiles. Fractional alpha survives final native sampling.

Missing 3 admits only 41/77; corrupt 41 admits only 3/77; missing 77 admits only
41/3. With all three resources missing, output is baseline-exact. Both
Normal/Hard prior-P1-P5 regressions have zero new admissions and unchanged
original/HD draw commands. P4 also witnesses unchanged generic 163/164 HD head
and shadow behavior.

P6 mode 2 remains classic. The runtime qualifier's focused check records 16
pure record-270 samples. A separate, broader independent check verifies 94
pure record-270 full native/uploaded frame-pair outputs: 32 main, 16 transition,
16 fallback, 14 Present and 16 density-4 samples. Mixed retained-birth samples
are classified separately and do not inflate the pure-mode count.

All four transition cases switch at ticks 60 and 100, then stop firing at
120. At tick 64, three mode-1 draw calls retain their original record-259
ownership. At tick 104, eight retained record-270 classic draw calls receive
no new HD admission. Seven meet the earlier origin filter; the eighth, ID 277,
is wholly off the left edge and is not a visible native witness. At tick 179,
all four cases have no player-shot draw or active-projectile entry and are
native-output-exact to baseline.

The Present controls make 123 calls per process with six skipped ticks and
nine double-Present ticks. RNG and original ownership/allocation streams remain
exact to the regular-Present runs. Independent review reconstructs 52 native
frames across the two pairs. Readback occurs once per scheduled presented tick;
skipped ticks and the second repeated call do not have separate native captures.

The two density-4 cases use all three unchanged density-4 resources and preserve
classic record 270. Independent native reconstruction covers all 56 frame
pairs. For their 112 full-density outputs, the corrected RGB model reconstructs
every pixel of the 1056-by-736 gameplay playfield. A separate comparison proves
all pixels outside that playfield baseline-equal in all 56 pairs. Together
these two checks cover the complete 1280-by-800 uploaded outputs; the playfield
RGB proof alone does not claim to model the outer UI.

Natural authored-support overlap between newly admitted heads is zero at the
sampled main-case points. Each main case separately records 8,785 later ordered
fractional writes, 12,513 fractional points clipped outside the playfield and
1,697 later writes inside original ship-command bounds. Ship bounds provide a
conservative association, not exact per-pixel ship ownership. The 216-case
synthetic forced-overlap proof remains a separate controlled test.

## Observation protocol, retained failures and archival

The candidate waits after original real-time MT seeding and before SDL
initialization. Both programs use the same actual original seed. All 784
startup player bytes and 5,016 canonical RNG bytes are identical before/after
the wait and across each pair, with independently reconstructed MT state.
The baseline exits, validates and is archived before candidate release.
Required measured capacity checks precede launch and release. No seed override,
interposition, normalization or discarded seed-mismatch launch is used.

Capture code, the six frozen observer binaries and replay remain unchanged
across the qualifying matrix. The two completed Normal main pairs retain
storage/controller epoch
`434ff1281d0f833ae84495c3b95cd95b28c3d1904f8284ff77331db715944663`.
The remaining 28 qualifying pairs use the reviewed storage/controller epoch
`e6fb3fc2135317f556d98a063d31536a8298cf86fa2371dede890ed42c864ab0`.
Per-case epoch attribution is retained; changing a storage helper is not an
observation-code or gameplay change.

During the first Hard native-2x attempt, a stale append offset in the private
archive helper caused reconstruction to fail before a manifest was published
or any failed-attempt raw observation was deleted. The baseline game had exited
0; the candidate was terminated with exit -15 while still held before SDL.
All 172,497 previously committed chunks and 1,045 archived files reconstructed
exactly. The 2,979,107-byte unindexed tail and failed evidence remain preserved.
The scoped-handle/EOF-positioning/writer-lock repair passed independent
regression checks without index repair or pack truncation. A new Hard native-2x
attempt reran both programs with an original natural seed and qualified under
the new helper epoch. The incomplete attempt receives no qualification credit.

The Hard density-4 game processes both exited 0 with original-state parity,
but the frozen postprocessing checker failed at tick 8. Independent diagnosis
identified its incorrect green-channel bit shift of 4 instead of 8; spatial
density does not alter RGB packing. The corrected checker and completion outputs
are separately versioned, with postprocessing freeze
`2e326cc6a0820dc38bcb4c8a85dd88fa470a4d830e963c035b14d702e68ef5de`.
The original failed checker/reports remain unchanged. All acquired observations
and 223 pre-existing candidate files reconstruct exactly, with no game rerun
or production, art, observer-binary or acquisition change. Extracted unchanged
production RGB functions pass 1,026 controls per plain and ASan+UBSan build;
512 wrong-shift cases are rejected per build. The initial LeakSanitizer attempt
hit the unsupported ptrace environment; its log is retained and passing
ASan+UBSan controls explicitly disable leak detection.

Total process accounting includes 65 game-executable launches: the 60
qualifying processes, one baseline preparation, two earlier ungated preliminary
processes and the two-process incomplete Hard attempt. There are 64 exit-0
processes and one pre-SDL exit -15. Across all game launches, the retained
record is 8,160 logic ticks, 948 native game captures and 192 shop captures.
Preliminary observations are not reused as fresh qualification. Standalone
gate/compositor/RGB controls are not counted as game launches.

Lossless row-chunk archival verifies both decoded content and exact original
encoded/raw bytes, including original gzip bytes. Every entry records original
and decoded sizes and SHA-256; reconstruction fails closed on any mismatch.
The manifest accounts for 6,082 archived game-process files, including 2,886
gzip recipes, 10,933,846,760 original encoded/raw bytes and 34,902,772,696 decoded
bytes. Reconstruction was byte-compared in the recorded CPython 3.12.14/zlib
1.3.2 environment. Arbitrary future codec versions are not promised to reproduce
identical compressed bytes; exact size/hash checks remain required. Archival
changes storage representation only, not acquisition.

The matrix review confirms all 160 production source files, 7,123 asset/catalog
files, 55 public test files and the Makefile still match the frozen candidate.
Six zero-fuzz observer inverses restore all original source bytes. Independent
quiescent-store review also passes: 658,647 stored objects and 65 retained
manifests reconstruct 6,087 original files, 10,947,434,810 original encoded/raw
bytes and 34,948,340,850 decoded bytes exactly. These global totals include
the five-file storage pilot, unlike the game-only totals above. SQLite integrity,
nonoverlapping indexed ranges, the sole preserved failed-append span, the
original pack prefix and sealed-store hashes all pass without modifying the
store. The sanitized runtime archive also passes an independent exact-byte
persistence roundtrip; this does not establish final source-overlay archive
integrity or remote publication.

## Reproduction and publication limits

Public controlled-test entry points, from the repository root:

    python3 tests/run_rear_multi_p1_core_tests.py
    python3 tests/run_rear_multi_p1_adapter_tests.py
    python3 tests/test_rear_multi_p1_source_inverse.py
    python3 tests/test_rear_multi_p5_mode1_assets.py
    python3 tests/test_rear_multi_p4_mode1_assets.py

The P1-prefixed loader/test names remain for compatibility. P6 adds no art
builder; reuse keeps the previously accepted family outputs unchanged.

Public fixtures are synthetic. Original game data, original-derived masks,
full raw records, private observation code, captures and executables are
excluded. Sanitized record/resource hashes are identifiers, not substitutes
for those private inputs.

Linux SDL dummy/software diagnostic runs cannot establish full-level or
full-campaign completion, ordinary P6 purchase, Windows compatibility,
physical-display/GPU behavior or performance, disk hot reload, natural partial
slot exhaustion, every cyclic start in live play, live power changes, or
LeakSanitizer coverage. Controlled tests and geometry calculations must not be
reported as natural runtime witnesses.

Final committed-tree/source-overlay archive integrity, authorized publication,
exact remote bytes, expected-parent non-force update and CI status remain
separate gates. No publication or CI pass is claimed here.
