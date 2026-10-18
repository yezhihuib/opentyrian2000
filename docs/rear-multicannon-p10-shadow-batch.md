# Rear Multi-Cannon P10 shadow batch

This presentation-only extension starts at published commit
`a59f4aa73a5acd965b0c2c4805a974049cd82d26`. In local single-player Episode 1's
first Normal level (physical level 9), density 8, it admits these two original
birth-owned shadow roles into the existing finite shadow path:

- P10 FIRST, physical 263: 277,278,297,296,203,222
- P10 SECOND, physical 274: 277,278,295,294,298,299,39,1

P11 FIRST 264 and SECOND 275 retain their existing six/eight-phase paths. The other
18 rear routes retain their prior shadow paths, including generic HD shadows.
The existing 13 generic entries and every head route are untouched. No shared
bank 8 raw is globally bound to the rear role.

## Unchanged rendering and gameplay contracts

Each admitted shadow reuses its own accepted head alpha byte-exactly, without
head RGB, new art, resampling or mirror synthesis. The original INDEX8 darken
still executes exactly once at original `shotX+1`, `shotY+shadowYDist`. Original
low-nibble rounding, ordered command compositing, cloud ownership and restoration
are unchanged. There are no production gameplay, coordinates, allocator, damage,
lifetime, timing, power, RNG, art, resource-pin, wrapper or core edits.

Admission still requires the original sealed birth in its actual renderer-owned
slot, exact physical record/mode/phase/raw/live-shot identity, generation and
birth seal, full 80-byte record pin, exact source-bank pin, captured resource
root/density, accepted alpha pin and safe disjoint surface/canvas layouts. The
admitted birth selects its own existing full-record check. Equipment switches
retain earlier births, including their final drawn lifetime-counter 0 tick.

Aliases 1263/1274, slot 80, negative x, density 4, Hard level 15, excluded game modes,
unsafe geometry and missing/corrupt assets retain their previous fallback.
There is no second native-darken path or new compositor framework.

## Reproducible focused checks

Use fresh output directories:

```sh
python tests/run_rear_multi_p1_core_tests.py /tmp/rear-core-new
python tests/run_rear_multi_p1_adapter_tests.py /tmp/rear-adapter-new
python tests/run_rear_multi_p11_shadow_tests.py /tmp/rear-adapter-new /tmp/rear-shadow-new
python tests/test_rear_multi_p1_source_inverse.py
```

The last command retains its inherited, explicitly user-accepted failure: the
old published source-projection fixture does not invert earlier observer hooks.
Both fixture and inverse test remain byte-identical to the baseline. No denied
replacement fixture is included or repackaged. This batch does not claim that
all repository tests pass.

The expanded shadow test passed 303,864 checks in each strict C99 and ASan/UBSan
run. Synthetic preparation checks cover all 6+8+6+8 shadow phases in all 80 owned slots,
all 80 serialized bytes of each role, all existing 96 negative families and 16
malformed-resource families, the other 18 routes, aliases, retained births,
independent supported-role table integrity and reset epochs. Preparation tests
alone do not establish SDL output or gameplay coverage.

The full strict C99 game build also passed. The 21 existing finite core suites
completed 42 plain/sanitized runs, covering all 22 rear routes. The existing
adapter/loader/wrapper suite passed 17,080,056 checks per normal mode with 800
malformed-resource variants; pending-art guard suites passed 983 P10 and 1,123
P11 FIRST checks per mode. Authentic-input checks verified all 22 original
full 80-byte record pins and 27 decoded source pins, including both P10 tuples.
Only the shadow include changes among 161 production source files; the other 160
remain byte-identical to the published baseline.

## Bounded actual-SDL gameplay result and remaining gaps

Exactly one instrumented 180-tick baseline/candidate pair ran through the actual
New Game / Full Game / Episode 1 / Normal menus and shop purchase, using normal
manual-HD startup rather than render-test/demo admission. The diagnostic changes
rear power from purchased P4 to P10 at tick 0 and P10 to P11 at tick 80, with
actual SDL mode-key events at ticks 40/130 and confirmation at 41/131. Those two
power-byte writes are isolated and disclosed; the instrumented run is not an
uninstrumented ordinary playthrough. The diagnostic wrote no coordinate or RNG state.

Both processes exited 0. The final analysis reports **216/218 checks
passed**. New safe shadows admitted 390/390 for 263 and 420/420 for 274; existing
P11 shadows retained 434/434 for 264 and 490/490 for 275. All 20 original streams
and four mixed original-field projections matched. Every original native shadow
was observed entering the darken exactly once, and its full 64,000-byte INDEX8
result matched an independent one-pass original-RLE model: 420 draws for 263,
456 for 274, 532 for 275 and 458 for 264 per side, with zero oracle errors. The
per-draw alpha, owner, cloud, green-selection and untouched INDEX8 checks passed.

All 13 native 640x400 captures per side matched the nearest-neighbor projection
of their corresponding final uploads. Baseline/candidate differences were
confined to new P10 shadow rectangles. Retained births continued across mode and
power changes. Native pairs received limited visual review: tick 8's intro fade
is dark; later retained-birth views at ticks 40/82 show cleaner cloud/terrain
shadow contours without observed head or background displacement.

The two failed gates remain failed: not every phase has an isolated final native
pixel witness. Phases 3/4 have none for either new role after unchanged exclusions
of every head and every other full shadow rectangle. For 263 each phase has 45
admitted, zero-error per-draw oracle checks; most sampled alpha is below the
viewport or overlaps, and six uncovered samples per phase have no final native
difference. For 274 each phase has 18 admitted, zero-error per-draw checks; all
in-view samples overlap other owners, so changed pixels are ambiguous. Correct
per-draw output and offline evidence do not fill these final-attribution gaps.
No gate was relaxed, and there was no extra capture or rerun.

The pair took 93.91 seconds. Peak RSS stayed below 142 MB per process, combined
raw outputs were 463,367,654 bytes, and observed free space stayed above 20 GiB.
The 512 MiB process/output limits and minimum 4 GiB free-space guard held. These
are finite local software-SDL results, not whole-level, campaign, Windows, GPU,
interactive-device or ideal-whole-frame acceptance.

## Private offline output validation

Actual decoder, loader, wrapper, original blitter and command-compositor excerpts
were paired against the exact published baseline with authentic records/bank data
and unchanged accepted assets. Independent full-canvas integer oracles passed
all four strict C99 and ASan/UBSan runs: 3,477 cases, 7,322 shadow commands, 62 restorations and 143
native SDL readbacks per run. The candidate passed 47,046,343 checks including
1,305 negatives; the baseline passed 46,854,155 checks including 1,193 negatives.
These are finite offline scene arrangements, not gameplay.

Thirty preservation digests for 264, 275 and the existing 13 generic shadows
match byte-for-byte across RGBA, ownership, cloud provenance and INDEX8, including
the frozen predecessor output. Both P11 native image arrangements are unchanged;
all 784 original-coordinate/birth-identity receipt rows match across all four
runs. All 16 side/record/arrangement BMPs match strict, sanitized and review output. Native 640x400 base/new scenes use real frozen terrain/cloud underlays and
include original birth/overlap examples. Each accepted alpha is used independently,
including the existing asymmetry in 39/1; no reflected replacement was synthesized.

The cold-cache suite passed all 56 missing/corrupt-resource cases across all six
263 phases and eight 274 phases in strict and ASan/UBSan runs. Every case includes
native SDL readback, retained-birth checks and exactly-once INDEX8 verification.

The 13 generic preservation fixtures use prefrozen accepted loader outputs while
exercising the actual admission, lifecycle, compositor and original blitter.
They add no new generic-shadow loader-file coverage. The new 263/274 accepted
HDA loading and their 56 cold variants exercise the actual loader separately.

The full sanitized runs completed without diagnostics, with sampled peak RSS
below 114 MB each. Their normal sanitizer virtual address space was allowed;
the 512 MiB RSS ceiling and minimum 4 GiB free-disk guards held. No extra matrix,
game capture or rerun was added.
