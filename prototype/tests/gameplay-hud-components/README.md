# Bounded HUC1 component loader oracle

Run with Python 3 and a POSIX C99 compiler:

```
python3 prototype/tests/gameplay-hud-components/run_tests.py
python3 prototype/tests/gameplay-hud-components/run_tests.py --sanitize
```

`--cc` selects a compiler; `--leak-check` additionally enables LeakSanitizer when
the environment supports it. Allocation, descriptor and I/O instrumentation is
always enabled. All indexed sources, palettes and RGBA are generated patterns.
No original game data, art or screenshots are read, copied or distributed.
Temporary fixtures and executables are removed automatically.

The tests exercise absent/NULL/empty/overlong paths, directories and nonblocking
FIFO rejection, immutable failed and successful attempts, descriptor inspection,
allocation/read/close failures, truncated/extra bytes both before and after size
inspection, every fixed header byte and checksum byte, payload corruption and
all 255 nonopaque alpha values in both payload sections. Capture tests cover
full 320x200 hashes, padding exclusion, failed-capture invalidation, independently
corrupt all 522 pristine shield pixels with honestly recomputed hashes, and
compare all 256 RGB entries with high-byte independence. Sampling tests enumerate
all 350 word pixels and all other frame coordinates, allow captured zero only
inside those word boxes, reject occlusion and invalid coordinates/subpixels, and
prove exact authored-4x to repeated-8x mapping.

An independent iterative reproduction of the original bar drawing validates all
435 `0 <= S <= M <= 28` pairs, including the zero-shield baseline. Every one of
the 522 expected ROI indices is individually mutated for every pair to prove
whole-region matching. Every shield subpixel is checked at both densities;
black and marker pixels never return artwork. Wipes, invalid draws and source
capture reset shield ownership, while label validity survives shield-only
revocations. Runtime API loops make no allocation or I/O. One live allocation
must be exactly 38528 bytes and all allocations and descriptors are released.

## Resource format

`gameplay-hud-components-v1.hda` is exactly 38592 bytes: a 64-byte little-endian
header, 22400 bytes of label RGBA, then 16128 bytes of band RGBA. All pixels must
be fully opaque. Header fields are:

- Offset 0: ASCII `HUC1`
- Offsets 4,8,12,16,20,24,28: u32 values `1,4,4,22400,14,36,8`
- Offset 32: u64 hash of all 64000 pristine PIC3 indices, excluding row padding
- Offset 40: u64 label-payload hash
- Offset 48: u64 band-payload hash
- Offset 56: u64 normal-palette hash of 256 sequential RGB triples, no alpha

Every hash is standard FNV-1a64 with offset basis 14695981039346656037 and prime
1099511628211. Checksums detect corruption; they do not authenticate artwork.
Label tiles are sequential FRONT 96x20, front GUN 56x20, REAR 72x20, rear GUN
56x20, placed at logical origins (285,5), (285,11), (285,26), (285,32). Fourteen
36x8 tiles follow in index order 146 through 159. Shield row pairs start on odd
logical y, so authored tile row zero maps to rows 137,139,...,193. The header
documents the complete finite ownership and the caller's rendering gates.

## Renderer integration and source writer oracle

This candidate is based on published d2f0a36b3529b94418404a374e06333d734ca13b.
The existing HUD1 loader/mask/resource and circuit renderer are unchanged.
Only the four word boxes (350 logical pixels) and the shield's 9x58 channel
can use HUC1 samples. MODE, lamps, digits, power bars and armor stay independent.
Empty shield pixels and the original index 68 capacity marker are never owned
or painted by this component compositor. There is no additional track artwork.

`render_mirror_hud_start` independently grants HUC1 after the explicit pristine
single-player PIC3 load. Its separate lease binds the persistent VGAScreenSeg,
pixels, format, pitch, 320x200 geometry and 8-bit layout. Missing/corrupt HUC1
cannot revoke the existing static frame. Component failure and frame failure
have separate ownership and cache-removal paths. A component-only pack can work
without HUD1. Generic PIC loads, level transitions, modes and teardown revoke
both using the existing lifecycle entry points.

`JE_wipeShieldArmorBars` notifies immediately before its original indexed clear;
this strips only baked shield samples from verified pending/fade caches and
invalidates the shield stamp. `JE_drawShield` notifies only after its original
indexed drawing completes. It records S/M only for a valid single-player leased
surface and 0<=S<=M<=28. No gameplay value, input, RNG, timer or drawing logic is
changed. A displayed stamp survives ordinary frames without a redraw, including
endLevel. ConstantDie's wipe-only path therefore stays blank rather than gaining
an invented zero baseline. Source indices remain authoritative.

Only an accepted ordinary finish composes new component RGB, after scene crop
and static HUD composition. The normal-palette checksum must match. Every one of
the 522 shield channel indices must equal the last actual draw's scalar raster;
a mismatch invalidates that stamp until a new original draw. Label samples
require captured PIC3 index equality, including explicitly bounded source-zero
background within the four word boxes. Labels can remain HD after a shield-only
failure. No per-frame allocation or file I/O occurs.

Component output ownership uses independent whole-logical-pixel values (1 for
labels, 2 for shield), with separate saved ownership, generation and palette.
Fade uses already composed RGB; present never rebuilds artwork. Wipe removes
only shield-owned output/saved pixels. Modal suspension removes both component
kinds, preserving verified scene/static-frame caches. Repeated suspension and
reset are idempotent. The same generation can resume at the next begin after
original modal restoration; the whole shield channel is verified again. Benign
renderer recreation suspends, while true video teardown revokes before freeing
the persistent source. Stale snapshots reject presentation safely.

Run the additional source-only oracles:

```
python3 prototype/tests/gameplay-hud-components/test_shield_writer.py
python3 prototype/tests/gameplay-hud-components/test_shield_writer.py --sanitize
python3 prototype/tests/gameplay-hud-components/test_renderer.py
python3 prototype/tests/gameplay-hud-components/test_renderer.py --sanitize
```

The writer oracle extracts the original JE_dBar3 / JE_drawShield / wipe helpers
and compares all 435 S/M pairs to an independent scalar raster. It checks the
whole unchanged surface, 5858 rectangle calls, regeneration/depletion, wipe-only
blank, displayed-stamp semantics and source lifecycle callsites. The compositor
oracle extracts actual production renderer functions, links the real loaders,
and verifies complete synthetic output at densities 4/8, source-zero label
backgrounds, every fill value, partial foreign label writes, whole-channel bar
rejection, independently retained frame/labels/scene, no extra frame allocation,
black/white/restore fades, mid-fade repeated shield clearing, modal resume,
missing/corrupt resources, nine source identity/layout losses (including freed
old allocations), mode/PIC changes, special output and palette rejection.

The previous static-HUD tests still run. Their writer-source hashes for the two
modified functions were updated only for these reviewed display notifications;
the new oracle independently checks their placement and unchanged indexed output.

For bounded real-executable baseline checking without HUC1:

```
python3 prototype/tests/gameplay-hud-components/test_no_components_runtime.py \
  --baseline /path/to/published/opentyrian2000 \
  --candidate /path/to/candidate/opentyrian2000 \
  --pack /path/to/existing/full-pack-with-static-HUD-but-no-HUC1 \
  --data /path/to/existing/tyrian2000-data \
  --output /path/to/new/proof-directory
```

This uses four 120-tick runs, classic/density8, native default 640x400 dummy/software,
FIFO hashes and compact logs, no game-data/art copies or captures. All original
state/RNG/indexed-output and rendered-RGB TSV hashes must match the published
baseline. Collision-header-only streams do not establish eventful collision
coverage. Parent-owned natural-damage/respawn/modal and real 2x/4x display trials
remain separate. The Visual C project lists both new module files; no Windows
build is claimed.
