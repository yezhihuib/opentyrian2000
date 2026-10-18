# Rear Multi-Cannon P10 mode 2: exact eight-shot route

Baseline commit `6203ef0fbc49aa73121ee5f68053eb9bd0264032`, tree
`16235dbc60f018a0d2ceeb8a1a05f4401406cf2a`.

## Exact scope

Adds ordinary player 1, rear port 10 / bay 1, power index 9, mode index 1,
physical normal record 274. The full 80-byte record has FNV 1a64
`8680b14f3eaffcf6` and SHA256
`7b29db63423a30c98587c8d66e7f725ea66f397e78e342b90e2e50b1d881c4b7`.
All eight entries are active. Original multi/max are 8; repeat is 6,
normally giving seven eligible updates between successful held-fire calls.

Ordered heads: 277, 278, 295, 294, 298, 299, 39, 1. Velocities:
(-9, -2), (9, -2), (6, 6), (-6, 6), (-2, 9), (2, 9), (-10, 0), (10, 0).
Birth dx is -2, 2, 4, -4, -4, 4, 0, 0; birth dy is zero. Damage is
2, 2, 2, 2, 2, 2, 1, 1. Placement stays (current shotX+1, current shotY),
with HDA anchor (0, 0). Admission requires `op[1][9] == 274`, the full
record pin and all existing ordinary scope/source/shot guards. Byte-identical
alias 1274, wrong contexts, linked/generic/shadow consumers and later powers
remain excluded. Normal physical level 9 / Hard physical level 15 scope
is unchanged.

Only four production files change. The renderer-owned per-call slot list
expands 7 to 8; original gameplay remains an 81-slot allocator (0..80).
Renderer ownership remains 0..79; slot 80 stays native. No gameplay arrays,
allocator, phase, energy, damage, cooldown, movement, RNG or collision changes.
Other 156 source-tree files are byte-exact, with an exact production inverse.
All old budgets and 163/164 pass-through remain intact. There are now
20 routes/91 canonical phases, still 23 drawable and 25 observed identities.

All eight heads reuse their accepted individually pinned d4/d8 HDA files.
All 16 relevant headers/payloads match role 131, 12x14, anchor (0, 0) and the
existing RGBA pins. Source/RGBA index order and pins are unchanged. No art,
asset file, catalog or density fallback is added, regenerated or transformed.
The candidate checkout has unmaterialized assets: no asset change is a
tracked-tree/diff statement, not a full disk-tree comparison. Runtime uses
the same existing hash-verified local selected pack. No remote recovery.

## Public tests and build

- 19 core suites, plain and ASan/UBSan: all 38 executions pass. New 274
  ownership: 4,355,212 checks per configuration, 648 cyclic capacity designs,
  all 20 routes/91 phases across bounded old/new cohorts.
- Actual-source allocator/adapter/decoder/loader/wrapper: 12,438,172 checks
  per configuration. All 640 record bits at each new phase; exact aliases,
  wrong contexts, partial capacities, shared/warm resources, seals and reuse.
- Eight tail slots 72..79 qualify at both densities / all starts while free
  native slot 80 stays untouched. Ninth capacity and duplicate ordinals
  fail closed. Every phase has independent missing/corrupt resource cases.
- All 736 malformed variants retained. Separate zero 203/222-pin regressions
  pass 979 checks per configuration: 263 fails closed while 274 stays available.
- Authentic inputs pass 20 full 80-byte record and 25 decoded-source pins. Source
  inverse passes 156 files. Public fixture bytes are synthetic; the new
  fixture differs from original 274. No original payload enters public tests.
- Uninstrumented strict C99 build passes -Wall -Wextra -Werror using local
  official SDL2 headers. Suppressions: misleading-indentation,
  format-truncation, missing-field-initializers. This is not unsuppressed-all-
  warnings or LeakSanitizer qualification.

## Offline ordered compositor

Actual candidate ownership/adapter/decoder/loader/compositor and actual SDL
pass 743 main synthetic scenes, 69,344,647 checks, 2,228 admitted draws and 267
native 640x400 outputs. All 28 phase pairs run both orders, both densities,
ages 0/1/2/4/8/16: 672 cases. All 56 pair/density tuples have disjoint original
rectangles at age 16; some far-travelled heads are then off-screen. Thirty-two
mixed 263/274 cases cover retained seals, overlap restoration and redraw.
Independent ordered integer-alpha, full ownership/canvas and native sampling
oracles agree. Alpha, ownership and restoration mutants fail as expected.

Another 56 cold-cache cases cover each 274 eight-head and protected 263
six-head resource missing/corrupt at d4/d8. Actual classic dispatch/blit/pixel
output matches direct original blit and independent decoded classic oracle.
Generic HD admission is stubbed false and unrelated font/shadow families
are no-ops in these fallback scenes; no full-stack claim is made for them.
All diagnostic runtimes have kernel 512 MiB address-space caps and guarded
evidence/free space. Native offline bright, overlap and mixed-separation
frames were reviewed. These are synthetic fixtures, not gameplay.

## One bounded actual-game pair

One pair completes 180 ticks of the first Normal level at native 640x400,
density 8 and actual SDL software readback; both exit 0. Ordinary SDL handlers
select New Game, Full Game, episode 1, Normal and genuinely buy rear port 10 P4.
No render-test/demo bootstrap. Natural time seed/full RNG and post-purchase
canonical Player/full RNG equality gates pass before play.

The only direct private gameplay diagnostic writes rear power 4 to 10 at
tick 0, verifying every other Player byte and complete RNG unchanged. This
is not ordinary P10 acquisition evidence. Real SDL mode-key handlers switch
1→2 at 50 and 2→1 at 110, observed at 51/111; no direct mode write. Private
instrumentation patches are identical; none enters production source.

All 20 named telemetry streams match byte-for-byte, including original
state/allocator/RNG and shot requests/emissions/results/draws, plus existing
visual diagnostics. Private births/input also match. 12 genuine power-rejected
calls stay rejected. Protected 263: 1,334/1,334 eligible draws; new 274: 608/608,
none missing/unexpected. Exact original birth/call/slot/phase and stable
nonzero seals agree; per-draw alpha/owner errors are zero. 113 old 263 draws
remain after 50; 73 old 274 draws after 110. Baseline 274 stays classic fallback.

Each process retains 16 capture groups at 4, 5, 6, 8, 11, 54, 55, 56, 58, 61, 114, 115,
116, 118, 121, 179; each contains classic, upload and native BMPs. Every SDL
readback equals nearest samples of its final upload. All 8 new phases have
final opaque authored-pixel witnesses, all 8 in tick 55. Phase 5 has only 9
unoccluded opaque native support pixels there and only that sampled witness;
this is not all 8 full-bounds/separated visibility. Mixed old/new visibility
occurs 55/56/58/61 and 115/116/118/121. All 6 protected 263 phases have final
witnesses before/after, with complete upload/native frame equality. Under
startup fade, protected visibility uses native-vs-classic differences inside
uncovered opaque support, not unfaded source RGB equality.

The sealed analyzer stops on a read-only parsing error: production represents
no rejections by an explicitly empty string, not integer zero. Original
analyzer/trace remain untouched. A separately reviewed one-expression
correction requires that exact empty string; textual 0 and unknown nonempty
values fail. No other test change. Same-pair analysis passes 122/122. No game
rerun, color normalization or replacement capture. Mixed renderer streams
also have exact original-field projections, excluding only documented
HD-substitution/count/RGB fields.

Raw native frames 55/61/118/121/179 and faded 8 pass limited direct visual
review: warm compact heads, soft energy edges, inherited four-lobe shapes and
trajectories remain readable, with no observed black matte/square bright core.
This applies only to those frames.

Each gameplay child has soft=hard 512 MiB address-space caps, pair at most 1 GiB.
Outputs: 284,263,921 and 284,301,897 bytes, within 512 MiB/process and 1 GiB/pair.
Runtime 46.21 seconds; free space 27,936,935,936 bytes at completion. One pair.

Acceptance combines offline exact ordered/restoration checks, runtime full
draw/omission accounting, state parity, sampled final visibility, SDL sampling,
protected 263 equality and limited native review. It does not independently
reconstruct an ideal whole final frame. Actual Hard/native 4x, full level or
campaign, ordinary P10 purchase, every ship/resolution and Windows/GPU remain
outside this batch. Private inputs, captures, builds and probes are excluded.

## Reproduce and evidence seals

```
python3 tests/run_rear_multi_p1_core_tests.py
python3 tests/run_rear_multi_p1_adapter_tests.py
python3 tests/test_rear_multi_p1_source_inverse.py
python3 tests/test_rear_multi_p10_mode2_inputs.py /path/to/tyrian2000
```

Private evidence SHA256:

- Input audit: `b6c9dc0095b06adca5430cbd606472e98097f38d908dad97e0633ce20a6987ce`
- Production review: `cc42bdb6df44efcacdc2e7f344cfca2e08c5aab101c632190800a504e53baeca`
- Public tests: `ee3f9fea3be1aab62896a5b665faf6e9f2b3c3fb303dd12d407a9a64eeb35ee1`
- Uninstrumented binary: `f0044946687f0fcbeb980ae4ed26d9119f9440b0bcd980c3a3f61229c8aaeb64`
- Offline coverage: `3d3977551b12d686d094b63a2dc3fffe649c6221973dfb81e5c80993d8d5238d`
- Launch manifest: `da9625a340368abce6e9c366c1d3da7833237061bae99b69fae9bb111d8e5377`
- Pair receipt: `29470f71f4ac566091b51eb735e63682b8b2306b3cfe8538d50d3b1e84dd856d`
- Corrected analyzer: `cf365125c2a3cbe533b748ed839137cb0eaf6588f78629ca3add34412ca4c2ed`
- Same-pair 122/122: `e2c177662ead77f596b5ceba98d46262a75770d00e46050c756d9ef3ef034c0a`
