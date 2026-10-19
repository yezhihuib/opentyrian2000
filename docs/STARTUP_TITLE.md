# Optional layered title artwork

Historical checkpoint: the commands, subset directories and file counts below
record the original bounded acceptance. Those subset runtime directories have
since been retired. For current use, select
`--startup-assets=assets/hd/packs/startup-title-settings-v1`, which also enables
the complete supported startup/UI family. See [retired pack recovery and
rebuilds](RETIRED_HD_PACKS.md) to reproduce the historical subsets.

The title family contains three separate generated assets: opaque PIC4 background,
PLANET_SHAPES146 Tyrian logo, and PLANET_SHAPES151 2000™ companion. Version text,
its indexed shadow, menu text/highlights and mouse cursor remain classic live draws.
The corrected Tyrian alpha channels were reviewed and frozen with the artwork.
Source/unit, package and bounded actual-engine gates pass. Eight cases / 13 executions
cover native 2×/4× output, input/cursor/restart and real idle demo handoff; one later
media-free merged regression also passes. Physical Windows/GPU/fullscreen/joystick
acceptance remains separate. Exact checkpoints and limits are recorded below.

## Explicit selection and compatibility

From the repository root, using a release/NDEBUG build and separately supplied
original game data:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-title-v1
```

An absolute asset-directory path also works. This combined directory contains the
three title resources and byte-identical copies of the existing two manufacturer
cards. The old `startup-manufacturer-v1` directory remains exactly two files and
continues to show a classic title. No option keeps ordinary startup classic.
The existing selector rejects debug, network, render-test and asset-debug combinations;
it does not enable `game_probe`, change gameplay/default packs or provide manual-
gameplay HD coverage. Original game data and private runtime fixtures are not included.

The title files add 7,113,968 unique runtime bytes. The combined directory also
contains 8,192,128 bytes of existing MFG1 resources for finite compatibility;
Git reuses the same two blob identities. This disk duplication is distinct from
the module's CPU/texture allocation budget.

## Original sequence and layered ownership

Only the actual PIC4 load inside `titleScreen()` binds a title lease. A PIC4 load
elsewhere, or a coincidentally matching sprite number, never activates it.
Composition follows the original order:

1. PIC4 at (0,0).
2. Original version shadow at (3,193), then version glyphs at (2,192).
3. PLANET146 Tyrian at the current original position.
4. PLANET151 2000™ at the current original position.
5. Original menu items, then the current selection highlight.
6. Original cursor, only for its original draw/present/erase interval.

The initial positions are (11,62)/(155,41). The 29 movement pairs are exactly
(11,60−2k)/(155,45+k), k=0…28, including the original first companion jump.
Each original movement retains its delay of two units. A settled restart directly
draws (11,4)/(155,73), with no invented interpolation or replay. There is no original
animation-skip branch. The original event clearing before the first live menu is
preserved, as are keyboard wrap, mouse hitboxes, sounds, special names and idle demo.

Both settled logos extend into the menu band. Therefore no final whole-screen
card overlay, hue mask, rectangular menu exclusion or before/after difference mask
is used. Four existing sprite pixel writers notify a title-only observer after
their original indexed write. Classic planes retain coverage and exact post-write
indices, including writes that did not change the index value. Every pixel uses
its own current palette entry. In particular the version shadow can use indices
0–239 while version glyphs use 240–255; it is not treated as one fade-class plane.

The original VGAScreen2 copies remain in place. Before each copy, the module checks
source identity and the known full indexed checkpoint. Afterward, private expected
state comes from that known checkpoint, never an unvalidated destination. A menu
restore also resets the private highlight plane. Cursor start saves all 64,000
pre-cursor indices; after `JE_mouseReplace`, the complete screen must equal that
checkpoint before transient coverage is removed. This includes the original direct
24×28 restore's bottom clipping/right-row behavior without changing it.

## Source and alpha guards

A lease requires VGAScreen==VGAScreenSeg, fixed 320×200×8 layout with pitch320,
separate compatible VGAScreen2 storage, pinned PIC4 decoded indices, palette8,
and both original sprite RLE/decoded-index/encoded-opacity identities. Pointer,
format and checkpoint identity remain guarded. Every presentation checks all
64,000 expected indexed bytes, the original sprite buffers and the original RGB
palette. Unknown writes during a live epoch revoke ownership even if the index
value is unchanged. Outside an epoch, the callbacks are inert.

Original sprite opacity comes from RLE skip instructions, not index0 or an RGB key.
Decoded transparent index slots are zero; opacity hashes use row-major bytes0/255.
These identities validate the original engine input. The approved new logo alpha
is independent high-resolution straight coverage, not a repeated low-resolution
mask. Both logical canvases retain their original registration padding and anchors.
The module never writes authored RGB into original indexed screens or palettes.

## TLV1 resource contract

Three independent files have an 80-byte little-endian `struct.Struct('<4s11I4Q')`
header, followed by canonical packed straight RGBA:

| Offset | Type | Meaning |
| --- | --- | --- |
| 0 | 4 bytes | `TLV1` |
| 4,8 | u32,u32 | version1, density4 |
| 12 | u32 | asset ID4,146 or151 |
| 16,20 | u32,u32 | logical width/height |
| 24 | u32 | palette8 |
| 28 | u32 | alpha mode0 opaque,1 straight |
| 32 | u32 | exact RGBA payload bytes |
| 36,40,44 | u32×3 | zero reserved |
| 48 | u64 | original decoded-index FNV1a64 |
| 56 | u64 | original opacity FNV1a64 |
| 64 | u64 | palette RGB FNV1a64 |
| 72 | u64 | payload FNV1a64 |

FNV1a64 uses offset14695981039346656037 and prime1099511628211. Checksums are
compatibility/corruption checks, not authentication. Dimensions and sizes are fixed:

| File | Logical canvas | Canonical canvas | File bytes |
| --- | --- | --- | ---: |
| title-pic4-v1.hda | 320×200 | 1280×800 | 4,096,080 |
| title-planet146-v1.hda | 304×121 | 1216×484 | 2,354,256 |
| title-planet151-v1.hda | 162×64 | 648×256 | 663,632 |

PIC4 alpha is255 everywhere, including original index0 space. Logo alpha may range
from0 to255, with zero support outside [4,4,1216,484) for146 and [8,8,644,252) for151.
RGB is zero wherever alpha is zero. Soft coverage is retained. The runtime validates
opened-handle regular-file type, all fixed fields, exact size/read/EOF, hashes, alpha
and bounds. Nonblocking open keeps FIFO inputs bounded. Files are read only at a new
explicit epoch; there is no per-presentation resource I/O or unbounded retry.

## Palette phases, fallback and retirement

The original art fade affects indices0–239 over10 steps; the late UI fade affects
240–255 over20 steps. Authored RGB channels use a 256-entry lookup advanced by the
same signed integer recurrence. Logo alpha stays fixed. UI-only fading leaves the
art lookup unchanged. Each classic pixel continues to use its original current
palette entry. Layer source-over is `(src*a + dst*(255-a) +127)/255`, in original
order, over opaque output. Canonical4× output uses the existing destination rectangle
and nearest sampling. No extra presentation, input service, delay or RNG call is added.

Fresh binding requires the art palette bank to start black. Unsupported entry colors
fall back for that title epoch. The module independently predicts and validates all
original palette entries during supported art/UI and outgoing black10/15 fades.
A missing or malformed resource falls back only for its own layer. Invalid source,
stage, checkpoint, palette, allocation or SDL state revokes the entire title epoch,
using the already-computed classic frame. There is no stale partial cache or mid-
epoch reactivation; a fresh explicit restart may bind again.

Outgoing full-black completion releases the lease. Explicit retirement also precedes
all foreign screens and title returns, including the ENGAGE/JE_whoa pixel-bleed effect,
which remains classic. Generic PIC load/clear, sprite-table reset and final video
teardown are backstops. Renderer recreation discards the texture while retaining
CPU state only if the lease still validates. Repeated retirement is safe.

## Bounded storage and verification

At maximum, the three immutable RGBA assets and one output buffer occupy11,209,728
heap bytes. Fixed state occupies865,824 bytes:862,304 indexed/mask/checkpoint/plane
bytes,3,328 palette/LUT bytes, and192 metadata/padding bytes. Specs/directory add200
bytes. Total explicit persistent CPU storage is12,075,752 bytes, plus small stack
locals. One nominal4,096,000-byte SDL texture is separate; SDL/driver overhead is
implementation-dependent. All dynamic CPU/texture ownership is released at retirement;
there is no CPU allocation per presentation. Manufacturer buffers are already released
before title entry. The budget is independent of source/media/resource disk size.

```sh
python3 prototype/tests/title-layers/test_source.py
python3 prototype/tests/title-layers/test_runtime.py
python3 prototype/tests/title-layers/test_runtime.py --sanitize
python3 prototype/tests/title-package/test_package.py
python3 prototype/tests/startup-logos/test_source.py
python3 prototype/tests/startup-logos/test_runtime.py
python3 prototype/test-windows-project.py
```

The initial source checkpoint is654005bed13e7334d7109b50c669b7c1257f1c6d, with
bounded hardening at38e8a046c6389f06f79684c8bf062143f3b66e93, based on
published1df1d87. Invalid checkpoint enums/no-before calls and extreme callback
addresses have explicit fail-closed regression tests. Removing explicit title hooks
and reversing the single approved CLI help literal restores original source tokens;
input/timer and manufacturer source bytes remain exact. The synthetic actual-module
suite covers736 presentations, all29 positions, settled restart, exact per-pixel
source-over, same-index/shadow writes, both palette groups, full-screen cursor erase,
checkpoint tampering, all missing-resource combinations, malformed inputs, allocator/
SDL failures and explicit lifetimes. ASan/UBSan pass with LeakSanitizer disabled
because it is unsupported under this executor's tracing; a finite allocation ledger
checks this module's ownership instead. The independent reviewer repeated all736
normal and736 sanitizer presentations and an additional806-presentation adversarial
sanitizer suite. The final source receipt SHA-256 is
`486a8849d7de719e9db6368d0ff8d4a0193d3580afb350cd97570f45db8c93d2`.

All19 generated-only source files match the corrected frozen art package. Its
source-only relocated rebuild is byte-exact, and all13 package tests pass. The full
central asset verifier also passes after the published linked31 merge with 18 packs,
3,012 HDA entries, 402 exact source PNGs, default counts 386/390, eight linked31 members,
and the separate three title resources plus two MFG1 compatibility copies.
It ran in a private read-only hardlink view to avoid another full asset copy; no
original comparison images or game data were added to Git.

## Bounded actual-engine acceptance

The eight-case matrix compares candidate `b62a99b7f48909d653a8d46c0ca709e10bfd8eba`
with published baseline `1df1d87b49b478d0e8b2eb5c5a4778c3f20866a8`. Both sides use the
same HD manufacturer cards, original external data, clean configuration, private seed
`0x4d464731` and version label `startup-qa-20261012`; only the candidate enables title
layers. Normal production seed/version behavior is unchanged. The private observer,
SDL event injection, readback and exit gates are absent from production and Git.

All 13 executions pass, retaining 2,058 presentation records: 1,066 intro, 940 title
and 52 foreign-screen records. Readback occurs immediately before the original
`SDL_RenderPresent`. Original indexed pixels, all palette bytes, RNG fingerprints,
input states, write coverage (including same-index writes), delay/fade/wait counts and
supported branch results agree. An independent ordered compositor reconstructs every
title output from original data, actual indexed post-writes and frozen straight RGBA.

| Case | Executions | Presentations per execution | Bounded proof |
| --- | ---: | ---: | --- |
| Native 2× | 2 | 82 intro + 60 title | 640×400, all 29 positions, art/UI fades, seven retained stages per side |
| Native 4× | 2 | 82 + 60 | 1280×800, exact canonical sampling, initial/settled spots |
| Missing PIC4 / 146 / 151 | 3 total | 82 + 60 | Each candidate omits one layer; independent classic fallback; frozen 2× baseline reused |
| Interactive | 2 | 82 + 125 title + 26 foreign | Keyboard wrap, hover/cursor, Instructions/Escape, settled restart, Quit |
| Fade-time key | 2 | 82 + 60 | UP down after frame 5 / up after 8; held 6–8, released 9; original latch/clear, no animation skip |
| Real 30-second idle | 2 | 82 + 75 | Original idle branch, 15 outgoing fade frames, true/play_demo handoff |

The interactive schedule checks all six complete cursor erases, visible Instructions
and Quit cursor/highlight states, zero title ownership throughout all 26 foreign
frames, retained selection after settled restart, original false/Quit return and
zero ownership at cleanup. The idle branch fires after 30,004 / 30,007 real SDL ms
(baseline / candidate); private observation stops after the original true/play_demo
return and before gameplay. It does not establish completed demo playback or return.
The fade-key fixture's preliminary simultaneous and adjacent-frame edges were rejected
in isolated SDL polling tests before any actual run; the final fixed 5/8 edges preserve
original polling and delays. No input-state assignment or timing shortcut is used.

The later source merge includes exact published `aba8650c` render-mirror changes and
one approved help-text clarification. Candidate `49c4e0363ae526527c5ab3e11713ff7b09d61308`
then passes one additional native-2× execution, with no new media: all 142 indexed,
palette, RGB, RNG and input fingerprints, original writes, palette bytes and non-time
wait/fade/delay/event fields equal the independently verified b62 core2 candidate.
The title module, 19 generated-only source files and all five runtime resources are
byte-exact. Totals including this mechanical regression are 14 executions and 2,200
presentations. This is a regression against the frozen candidate, not a second full
matrix against a new baseline. The final documentation-only commit adds no runtime change.

The artist directly reviewed 14 retained candidate PNGs and two core2 baseline PNGs:
seven core2 stages, two core4 spots and five interactive transitions. Their review
passes gold identities, corrected channels/counters, registration, ordered alpha,
menu/version/shadow, cursor, foreign takeover, settled restart and black exit. The
remaining input/fallback/idle claims are numerical receipt review. Twenty-eight PNGs
and two compact core2 clips are retained privately; no additional captures are needed.
The complete author report and all eight oracle hashes are preserved in
[the validation receipt](STARTUP_TITLE_VALIDATION.json).

### Diagnostic timing and remaining limits

Observed title first-presentation begin to final readback spans were 1,239,512 /
1,249,678 microseconds at 2× and 1,246,900 / 1,254,675 microseconds at 4× (baseline /
candidate). Across the 30 palette steps, measured sums were 59 / 892 microseconds at
2× and 57 / 834 at 4×; maximum candidate steps were 49 / 45 microseconds. Full-frame
render/readback totals were 38,231 / 284,778 microseconds at 2× and 126,870 / 350,118
at 4×. These are observer-instrumented diagnostic samples, including readback and
logging overhead; core2 FIFO encoding/backpressure can extend intervals. They are
neither FPS nor original-speed or GPU performance evidence. Original delay counts
are unchanged; palette-step timing alone excludes the full-frame compositor cost.

Actual-engine scope is SDL dummy/software at native output sizes. Physical desktop,
GPU, fullscreen, physical joystick, Windows build/runtime, audio quality, Christmas
title, corrupt-resource actual runs and complete demo playback/return remain untested.
Malformed inputs and unsupported paths have the documented source/unit checks rather
than actual-run acceptance. Author review covers retained chronological stills, not
continuous video playback. MP4 is lossy and instrumented; PNG/hash evidence supplies
exact pixels. Gameplay/default pack selection and ordinary classic startup are unchanged.
