# Optional manufacturer startup cards

Historical checkpoint: the commands, subset directories and file counts below
record the original bounded acceptance. Those subset runtime directories have
since been retired. For current use, select
`--startup-assets=assets/hd/packs/startup-title-settings-v1`, which also enables
the complete supported startup/UI family. See [retired pack recovery and
rebuilds](RETIRED_HD_PACKS.md) to reproduce the historical subsets.

The approved artwork covers PIC10/XSIV GAMES and PIC12/ECLIPSE only.
Source/package and synthetic production-function tests pass. Twelve bounded
actual-engine executions pass, including native 640×400 and 1280×800 readbacks,
original fades, input skipping, independent fallback and classic title handoff.
They used SDL dummy/software, not a physical desktop/GPU/fullscreen environment.
Windows runtime, physical joystick, whole-game HD and performance acceptance
remain outside this result. Exact results are in
[the validation record](STARTUP_MANUFACTURER_VALIDATION.json).

This document describes the unchanged two-file manufacturer directory. The separate
[combined title pack](STARTUP_TITLE.md) uses the same selector but additionally opts
into layered title artwork; its source/runtime acceptance is documented separately.

## Explicit opt-in

From the repository root, with a release/NDEBUG build:

```sh
./opentyrian2000 --data=/absolute/path/to/tyrian2000 \
  --startup-assets=assets/hd/packs/startup-manufacturer-v1
```

The directory may instead be absolute. An empty argument is rejected. A missing
or unreadable directory is ordinary per-card classic fallback, not a fatal
startup error. No option means no resource open/allocation and classic startup.
Network, `--render-test` and `--asset-debug` combinations are rejected before
loading game data. Debug builds reject the selector because their existing entry
path omits the manufacturer sequence. The selector never enables `game_probe`.

Only the two manufacturer cards can be HD. Title PIC4, PLANET sprites146/151,
menu/version/cursor text and subsequent ordinary manual gameplay stay classic.
This does not turn controlled gameplay previews into a manual-HD release.

## Original sequence and ownership

`intro_logos()` retains all its original calls and their order:

- Set `moveTyrianLogoUp`; clear indexed VGAScreen; white fade25.
- Load PIC10; show under white; palette fade25; delay200/input wait; black fade10.
- Load PIC12; show under black; palette fade10; delay200/input wait; black fade10.

There are82 original `JE_showVGA` calls and two original waits. The renderer does
not add presentation calls or alter the timer, input service or RNG. Keyboard
`newkey` is consumed by the wait; held mouse/joystick states may skip both waits.
Events processed during a fade can skip the following wait; fades still finish.

A separate module gets a context only on explicit `intro_logos` entry. Each card
is registered immediately after that function's actual `JE_loadPic` and before
its first show. PIC coincidence elsewhere never grants ownership. Generic PIC
loads/clears revoke the current card; explicit registration advances through the
fixed10/12 sequence even when a card fails. The final black fade is followed by
explicit context release, before the original title starts.

Activation requires the actual VGA surface/pixels/format, exactly320×200×8 with
pitch320, the pinned decoded source hash, the pinned target palette, and the
expected initial all-white/all-black current palette. Unsupported surface
layouts fall back. Every live presentation/fade checks source identity and all
64000 indexed bytes. Current palette RGB must match the independently predicted
original palette. No authored RGB is quantized or written to the original
indexed surface or original palette.

## Exact MFG1 resource contract

The two independent files are `startup-pic10-v1.hda` and
`startup-pic12-v1.hda`. Each is exactly4096064 bytes. Its64-byte little-endian
header is Python `struct.Struct('<4s7I4Q')`:

| Offset | Type | Fixed value / role |
| --- | --- | --- |
| 0 | 4 bytes | `MFG1` |
| 4 | u32 | version1 |
| 8 | u32 | density4 |
| 12 | u32 | PIC10 or PIC12 |
| 16 | u32 | palette20 or palette22 |
| 20,24 | u32,u32 | logical width320,height200 |
| 28 | u32 | payload4096000 bytes |
| 32 | u64 | pinned decoded-index FNV-1a64 |
| 40 | u64 | pinned expanded RGB palette FNV-1a64 |
| 48 | u64 | payload FNV-1a64 |
| 56 | u64 | reserved0 |

The payload is1280×800 row-major RGBA; every alpha is255. FNV-1a uses offset
14695981039346656037 and prime1099511628211 with unsigned64-bit wrapping.
These are compatibility/corruption checks, not authentication. Repository
packaging also pins source/artwork and complete resource SHA-256 values.

| Card | Source indices FNV | Palette RGB FNV | Payload FNV |
| --- | --- | --- | --- |
| PIC10 | 720d8ce9dda3f5f4 | b50ac0b9e5f1a73d | 46944845146f2d39 |
| PIC12 | 98d7341da720b7ab | 20261a06b61711d5 | 3d97f250a0cae51a |

The runtime loader checks the opened object is a regular file and exact size,
then checks all fixed fields before allocation. It validates exact reads, EOF,
close, checksum and every alpha. POSIX opens are nonblocking so a FIFO cannot
stall startup. Short/interrupted reads fail closed without retry. File-declared
sizes never control allocation products or dimensions.

Original-data files and original/reference-comparison PNGs are excluded from
the repository import. Frozen generated masters, canonical PNGs, prompts,
source-compatibility metadata and omission provenance are retained. Runtime
resources form a separate manifest family/pack; gameplay pack defaults and
HDR1 counts do not change. The standalone builder can reproduce both resources
from canonical PNGs or frozen generated masters without original game data.

## Presentation, fades, fallback and lifetime

Full-card output uses one nearest-sampled opaque ARGB8888 texture with the
existing destination rectangle. It does not use the gameplay scene crop or HD
HUD ownership. Synthetic SDL software-renderer tests check exact4× pixels and
2× center-nearest sampling against the canonical4× grid; these are not native
window captures.

PIC10 starts from white; PIC12 starts from black. Only the explicit full-range
fade-in25/10 and fade-out10 sequences are accepted. Each authored channel follows
`current + (target-current)/remaining_steps` with C integer division, matching
the original incremental palette recurrence. Endpoints are exact authored RGB
or black. The independently predicted256-entry palette must match the palette
that the original engine actually advanced. Unexpected targets, ranges, step
counts or palette/source mutations revoke the card.

Missing/invalid/incompatible cards fall back independently to the indexed
originals. Presentation/SDL errors revoke only the current card and return to
the caller's existing classic draw. The already-computed classic texture is
available, so failure does not leave an old HD texture in place. The next card
can activate independently. No per-frame reload or unbounded retry is used.

Renderer recreation frees only the card texture; valid CPU fade state survives.
Full video teardown revokes the context and frees CPU/GPU ownership before the
indexed surfaces are freed. Repeated reset/shutdown are safe. Normal completion
frees both card buffers and its texture before title/menu presentation.

At most one current card is loaded. Peak explicit CPU backing buffers are:

- RGBA target:4096000 bytes
- ARGB current output:4096000 bytes
- Source index lease:64000 bytes
- Two256-entry SDL_Color palettes:2048 bytes

Total8258048 bytes (about7.88MiB), plus small fixed metadata and stack locals.
The one texture is nominally4096000 bytes (about3.91MiB); SDL/driver backing or
staging overhead is implementation-dependent and not measured here. The tests
track exactly8192000 peak heap bytes and zero retained production heap bytes
at shutdown. There is no CPU allocation or file I/O per presentation; texture
allocation happens only at the first presentation or after renderer recreation.
This memory accounting is separate from source/resource disk size.

## Reproducible source gates

With SDL2 development headers available through pkg-config:

```sh
python3 prototype/tests/startup-logos/test_source.py
python3 prototype/tests/startup-logos/test_runtime.py
python3 prototype/tests/startup-logos/test_runtime.py --sanitize
python3 prototype/tests/startup-manufacturer/test_package.py
python3 prototype/build-hd-assets.py
python3 prototype/test-windows-project.py
make
```

The source gate removes only the explicit startup display hooks and compares
original source hashes against8227aff for the full palette/video/PIC/tyrian2
files, and unchanged timer/keyboard/joystick files. A tiny extracted sequence
oracle checks82 presentations/two waits; it does not run the game.

Synthetic runtime tests include fixed-header corruption, exact/short/trailing
reads, every header byte, opacity rejection, checksum errors, missing/directory/
FIFO/path-overflow cases, allocation/I/O/close and SDL failures, independent-card
fallback, rejected source layouts/identities/palettes, stale surface state,
unsupported fade ranges/counts, exact endpoints, repeat presentation, renderer
texture recreation, native-grid2×/4× sampling and shutdown allocation ledgers.
ASan/UBSan pass. LeakSanitizer cannot run under this executor's tracing; the
explicit production-allocation ledger covers these finite allocations instead.

## Bounded actual-engine acceptance, 2026-10-12

The source audit is pinned to `4640fbb8153ecf05e58e6f71b492933bd2f3ff3a`.
Candidate `8837edd11b8b828979ac1a9a803e02a82c128ff1` adds only the exact published
mechanical 190/200 checkpoint to that source; all startup production bytes remain
identical to the audited commit. The classic baseline is published
`eec06f5c6fa2f57917ed8f30dfb38a1c23c660be`. A later documentation-only commit does
not change the tested production source or resources.

The private A/B builds execute the actual release intro/main and title paths.
Both use seed `0x4d464731`, version text `startup-qa-20261012`, identical original
data and isolated matching configuration. The common private seed/version are
necessary to compare title RNG and rendered version text; ordinary production
seed/version behavior is unchanged. Observer, queued-input and exit hooks exist
only in private source archives. They do not enable `game_probe`, shorten delays,
assign engine input state, or replace indexed/palette state. Each readback is
immediately before the single original `SDL_RenderPresent`.

| Case | Executions | Result |
| --- | ---: | --- |
| Native 2×, no input (640×400) | classic + HD | PASS |
| Native 4×, no input (1280×800) | classic + HD | PASS |
| Key queued at first wait | classic + HD | PASS; first wait skipped, second retained |
| Held mouse across waits | classic + HD | PASS; both waits skipped |
| Missing PIC10 resource | HD candidate | PASS; only PIC10 falls back |
| Missing PIC12 resource | HD candidate | PASS; only PIC12 falls back |
| Key queued during PIC10 fade | classic + HD | PASS; latches until first wait |

Every execution retains 82 intro and 60 classic title presentations, 80 original
intro delay-1 calls, two delay-200 calls, five fades and 80 palette steps. The full
indexed/palette/RNG/input records match across each A/B pair. All 60 classic title
readbacks match, including settled title/menu output. Every authored fade output
from intro presentation 25 through 82 matches an independent canonical RGB integer
recurrence oracle. Missing-card runs match the corresponding original card and
the intact HD card independently. Keys are consumed by the original wait; held
mouse remains held through both waits and is released privately before title.
Physical device delivery and joystick behavior are not established by queued
SDL key/mouse events; joystick preservation also has source/synthetic coverage.

All 82 intro and 60 title hashes are retained per execution. Selected native
endpoint/transition PNGs and four compact chronological clips are retained only
for the two no-input A/B pairs. Retained run outputs total 9,979,893 bytes,
excluding hardlinked resource files. Private fixture source, binaries, full
traces and media are outside Git; the validation JSON records their hashes.
The artwork author directly reviewed retained chronological PNGs: all nine core2
candidate stills, both classic logo endpoints, and selected core4 transitions,
endpoints and title. All four 2×/4× endpoint PNGs equal the frozen generated PNG
files byte-for-byte. Input/fallback findings were reviewed through the numeric
receipts; there is no claim of continuous video playback. The complete author
report and receipt SHA256 are retained in the validation JSON. Title PIC4,
PLANET 146/151 and title/menu lettering remain original artwork.

The formal generated-only import remains exactly 22 paths, including six generated
master/preview PNGs. No original, comparison or reference raster from the pilot,
and no private runtime fixture/code/media, was added to Git.

Paired intro wall times were 7.441/7.468 s at 2× and 10.289/9.775 s at 4×
(classic/HD). Summed palette-step costs were 0.280/452.134 ms at 2× and
0.330/516.549 ms at 4×; the HD maximum observed step was 18.409/69.141 ms.
Both no-input waits remain about 2.875 s. These are single instrumented samples:
readback, hashing, PNG export and FIFO encoding/backpressure can extend observed
intervals. They are diagnostic wall/step costs, not original-speed, FPS or
performance proof. Original delay counts and input control flow were unchanged.

Windows runtime, physical desktop/GPU/fullscreen, physical joystick and a full
manual-gameplay HD release still require their own acceptance. No startup title
art replacement is included. Source/unit tests cover malformed files and failures
more exhaustively than this deliberately finite actual-engine matrix.
