# Rear Multi-Cannon P9 shadow batch

This presentation-only extension uses the published P10 shadow result
`73c556905a2f6c7266c911f8016cfe9025b6d934` as its file baseline. It adds two
physical birth-owned roles in local single-player Episode 1's first Normal level
(physical level 9), density 8:

- P9 FIRST, physical 262: 277,278,297,296,41,3 (six phases)
- P9 SECOND, physical 273: 277,278,295,294,77,298,299 (seven phases)

FIRST262 retains its original six-allocation budget and six-phase period;
SECOND273 retains seven allocations and its seven-phase period. The selector
power index is 8, and mode indexes are 0 and 1 respectively. Both
complete authentic 80-byte record payloads and all accepted source/asset pins
remain unchanged. P10 FIRST263/SECOND274 and P11 FIRST264/SECOND275 retain their
existing shadow paths. The other sixteen rear routes retain their previous
shadow behavior, including existing generic HD shadows. All 22 head routes and
the thirteen generic shadow entries are unchanged.

## Rendering and gameplay contracts

Every admitted phase uses its own accepted head alpha byte-exactly, without the
head RGB, generated artwork, reflection, resampling or recoloring. Shared bank 8
raw IDs are not globally rebound. The normal shader, ordered alpha compositor,
cloud and green ownership, classic restoration, and original native INDEX8
one-pass darkening are unchanged. The original shadow location remains
`shotX+1, shotY+shadowYDist`; no extra native darken is introduced.

Admission requires the actual renderer-owned slot, qualified sealed birth,
physical record/mode/phase/raw/live-shot identity, generation and birth seal,
complete record and original source-bank pins, captured root/density, validated
accepted resource, and safe disjoint indexed/canvas layouts. The admitted birth
selects its own record-local validation. Existing heads remain qualified across
selection changes; the final drawn counter-zero tick remains eligible.

Aliases 1262/1273, slot 80, malformed layouts, density 4, Hard level 15, unsupported
game modes, negative-x and other previously excluded geometry, and missing or
corrupt artwork retain the original fallback. There are no production changes
to gameplay, allocator, coordinates, motion, damage, lifetime, timing, power,
RNG, palette, wrapper, decoder, blitter, core, resource loader or resource pins.
Only `src/rear_multi_p11_shadow.inc` differs among 161 production source files.

## Focused checks

Use fresh output directories:

```sh
python tests/run_rear_multi_p1_core_tests.py /tmp/rear-core-new
python tests/run_rear_multi_p1_adapter_tests.py /tmp/rear-adapter-new
python tests/run_rear_multi_p11_shadow_tests.py /tmp/rear-adapter-new /tmp/rear-shadow-new
python tests/test_rear_multi_p1_source_inverse.py
```

The last command retains the inherited source-inverse failure caused by the old
published source-projection fixture's incomplete inversion of earlier observer
hooks. That old 21517-byte fixture and the inverse test remain byte-identical to
the baseline. The previously declined replacement fixture is not part of this
batch. No all-green repository claim is made.

The shadow preparation tests extend the existing four roles to all six physical
shadow roles, comprising 6+8+6+8+6+7 phases. They check all 80 owned slots, density 4
fallback,96 negative families and all 80 serialized bytes per phase,16 malformed
resource families, all sixteen earlier head-only roles, physical aliases,
retained births, independent role-local integrity and reset epochs. Synthetic
preparation alone does not establish SDL or gameplay output.

The strict C99/O2/Wall/Wextra/Werror full game build completed. All 21 finite
core suites passed in plain and ASan/UBSan builds,42 runs covering all 22 head
routes. The unchanged adapter/loader/wrapper suite passed 17,080,056 checks per
mode, including 800 malformed-resource variants; pending-art suites passed 983
P10 and 1,123 P11 FIRST checks per mode. Expanded shadow preparation passed
447,420 checks per strict/sanitized run. Independent static review found no
blocking defect and verified all 13 P9 phase references against their accepted
HDA/alpha SHA-256 identities and existing d8 RGBA pins.

Authentic Hdt/SHP checks verify all 22 full 80-byte records and 27 decoded source
pins. Additional P9 checks bind the exact selector cells, physical records,
phase order, original signed offsets and velocities; SECOND273's original
shotrepeat is 6, multi/max are 7, and aim is 0.

## Bounded actual-menu SDL result

Exactly one instrumented 180-tick baseline/candidate pair followed actual NewGame,
FullGame, Episode 1 and Normal menus, then genuinely bought rear-port 10 at P4 in
the shop. Normal manual-HD startup was used; render-test/demo admission was not.
The diagnostic changes exactly one equipment power byte P4→P9 at tick 0, P9→P10
at 60 and P10→P11 at 120. Actual SDL mode keydowns occur at 30/90/150 and are
observed at 31/91/151. The isolated power-byte changes are disclosed and prove
unchanged full RNG state; this is instrumented diagnostic play, not an ordinary
uninstrumented playthrough. Gameplay coordinates, original firing/allocation
fields, RNG, timing, and fades remain intact.

Both processes exited 0. The result is 210/212 runtime checks, with two unchanged
final-attribution gates still failed. All 20 original observation streams and
four mixed original-field projections match exactly. P9 produced four complete
actual calls per mode,24 FIRST births and 28 SECOND births; every original phase,
raw, velocity and unique allocated slot is checked. All normal head accounting
and independent alpha/owner oracles pass. New 262 shadows admit 312/312 eligible
commands and 273 admit 168/168, with zero per-draw RGBA/owner/cloud/green/selection
errors and zero INDEX8 changes during the RGBA stage. Published 263/274/264/275
shadows retain 234/350/385/185 admissions, stable seals and unchanged oracles.

Every one of 1,754 original native shadows per side entered the native darkener
exactly once. Each complete 64,000-byte INDEX8 result equals an independent
one-pass original-RLE model, with zero errors. This includes 336 original 262 and
180 original 273 shadows; negative-x fallbacks remain 24 and 12 respectively.
Fallback is not counted as HD admission.

All 13 native 640x400 SDL readbacks equal the nearest-neighbor projection of their
final uploads. Baseline/candidate differences remain inside actual admitted P9
shadow rectangles. Parent visual review observed cleaner cloud shadow profiles
without apparent head/background displacement; the initial tick 8 fade is dark.
An already captured tick 33 retained 262 pair is clearer but contains new 273
shadows too, so strict other-owner exclusions remain in force. No capture was
added or repeated for visual review.

Finite unique final-native witnesses exist for 262 phases 1/2/5/6 and 273 phases 1/2.
The 262 phase 3/4 oracle checks pass 36 draws each, but nearly all sampled alpha
lies below the gameplay viewport or overlaps other shadow rectangles; the
remaining uncovered samples have no final native difference. The 273 phases 3/4/
5/6/7 have 12/12/4/8/8 admitted zero-error per-draw checks, but no admitted draws
at predetermined capture ticks. Their actual eligibility ages are 1–3,1–3,1,
1–2 and 1–2, which the preselected age 0/4 captures miss. Offline all-phase output
and per-draw checks do not fill these final-native attribution gaps. Gates and
exclusions were not relaxed, and no extra capture or rerun was made.

The pair took 56.14 seconds; raw output was 463,365,747 bytes, below 512 MiB. Peak
sampled game RSS was 145,580,032/142,430,208 bytes and observed free disk remained
above 20.6 GB. Per-game 512 MiB capture/address limits and minimum 4 GiB free-space
guards held. Compiler and sanitizer virtual address spaces were exempt. These
are finite software-SDL results, not whole-campaign, Windows, GPU, interactive
input-device, exhaustive visibility or whole-frame acceptance. Future batches
should derive the frozen capture schedule from each phase's actual eligibility
window before launch; this batch retains its original schedule and limitations.

## Scoped offline output validation

Actual frozen decoder, finite optional loader, wrappers, original indexed
blitters, provenance core and ordered compositor were compared with real SDL
software-renderer readback. Authentic records/source bank and the independently
verified accepted HDA files were used, including each own 41/3/77 alpha from the
accepted common pack. No synthetic adapter artwork was substituted.

All four strict/ASan+UBSan baseline/candidate runs passed 287 scoped scenes and 52
accepted-edge cases each,1,356 scene executions. Each 287-scene candidate run
checks 12,594,460 assertions,1,105 shadow commands,26 restorations,260 negatives
and 44 native readbacks; baseline has 12,539,651 assertions and 228 negatives.
Every new phase is exercised separately on indexed/terrain/cloud backgrounds,
with authentic offset/velocity cohorts, both draw orders, cloud writes,
restoration, low-nibble floor, P9 interleaving, and protected P10/P11/generic 13.
Accepted boundaries x 0/x 308/y-13/y 189 are checked for all 13 phases separately.

To keep coverage bounded, only four representative phase pairs per new route
run both orders at ages 0/2/8 on three backgrounds. The 44 guard mutations and
8 candidate prepared-command invalidations use the first/last phase of each
new role; the all-phase preparation suite supplies broader identity coverage.
This does not repeat the prior 3,477-case Cartesian matrix or claim exhaustive
combinations. The 13 generic routes use accepted frozen loader outputs while
executing actual admission/compositing; their separate file loader is outside
this fixture.

All 50 protected RGBA/owner/cloud/INDEX8 digests match across the four runs.
All 24 native review BMPs match strict/sanitized output, and all eight protected
P10/P11 arrangement pairs remain byte-identical. P9 phase-scene differences are
3,206 pixels for 262 and 3,107 for 273; birth-overlap differences are 2,263/2,591.
Parent accepted these finite offline visuals with unchanged heads/colors.

Every phase has cold missing/corrupt-loader checks in strict and sanitizer
builds:52 phase/fault/build cases,104 executions across two preserved successful
attempts. The second improves resource accounting. Both builds reject all 26
wrong-own-alpha/double-darkening oracle expectations. Production/art remain
unchanged during these sensitivity checks.

Peak recorded offline capture RSS is 122,052,608 bytes; minimum free disk is
20,604,825,600 bytes. Capture 512 MiB RSS and 4 GiB free-space guards held. Final
watchdogs use 10 ms group sampling plus kernel child maximum RSS; the first
strict-baseline/cold attempt retained the earlier 100 ms sampler. Compiler and
ASan virtual address spaces were exempt, and leak detection was disabled.
Initial pack-count and harness compile setup failures are retained separately;
corrected harness builds and every final matrix/edge/cold test passed. These
are constructed offline scenes, not gameplay or GPU output.

## Local-only storage

The local Git history begins with a clearly labeled independent
source/config/test snapshot. Its provenance is the
published `73c5569` file result, not a claim of GitHub commit ancestry. Accepted
artwork and original game data remain external inputs; captures, binaries and
private validation evidence are not included in the publication batch.
