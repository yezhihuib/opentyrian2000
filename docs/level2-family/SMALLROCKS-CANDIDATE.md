# Random smallrocks candidate

The existing `--hd --public-candidates` preset now requests the bounded
smallrocks adapter for records317–324. Plain `--hd` does not enable it; the
launcher removes inherited `SMALLROCKS_` controls before setting the preset's
`SMALLROCKS_ENABLE=1` and verified asset directory. There is no new CLI option.
No game state, random number, original data or authored asset is modified.

Four existing public files are reused from `assets/hd/packs/asteroid1-ten-v1`:
`enemy-newshd-{95,114,133,152}-8.hda`. Each is 43,036 bytes, HDR1 12x14 at density8.
The launcher checks exact size and SHA-256; the runtime additionally checks the
HDR1 fields and pinned RGBA hash. These four checks are additional to the base
52-file manifest, not a change to those base asset requirements.

## Exact native births, not arbitrary matching images

The source adapter and decoded native callback tables come from the public
archive `experimental/late-level/sources/03c5968bda89ae17/`; central integration
was compared with `sources/9a69cfe175a0bbc0/b313_family_canvas_mirror.inc`.
They were selectively connected to the current family implementation without
replacing its newer adapters or display admission rules.

The adapter requires ordinary E1 physical-level2 ASTEROID2, mapD/shapeZ, the
exact 33-entry random enemy table, record/source-bank/palette pins and its
existing family parent mode. Its table has records317–324 repeated three times;
this suggests useful coverage but is not a measured live spawn count.

A begin/commit pair surrounds only the real random `JE_newEnemy(0,tempW,0)`
call after the engine has made its existing RNG choices. Allocation and
initialization hooks bind the actual pool0–24 object to record, token, epoch,
generation and bank. Failed allocations close the call; reused slots retire
old witnesses. There is no event replay, forced spawn or new random draw.
The source table and source/record pins are archived assumptions checked
against actual runtime data, not independently decoded original data in this
cloud batch. Unsupported data remains native.

## Rendering and retirement

Only complete single tiles at x24..276/y0..170, part0, normal unfiltered writes
are admitted. The exact original sparse callback order is checked against both
the native destination and expected buffer: 145/137/113/153 callbacks for the
four materials. Native holes issue no callback. A native index of zero would
still be a write, not a reason to skip; the current four pinned tables happen
to contain no such zero-index callbacks.

The artwork has real partial alpha, unlike binary-mask longface art. Each
verified native callback blends all64 HD subpixels using the actual asset
alpha and assigns ownership even when alpha0 preserves underlying RGB.
All other sparse family owners are retired before any family pixel handler
can return early. A later normal/blend write clears smallrock ownership;
validated native shadows darken the live canvas and retain ownership with a
shadow receipt. Failed or incomplete callbacks invalidate the provisional frame.
The central finish/output gates check smallrocks too, and reset/tick/shutdown,
offscreen removal, slot reuse and bank changes retain lifecycle handling.

Smallrocks cannot admit a display frame by itself. It writes only inside the
already permitted actor or surviving-terrain family frame. No new frame lease,
geometry relaxation, pause/cache behavior or broad scene acceptance was added.

## Offline evidence and limits

- `tests/test_smallrocks_family.py` extracts actual birth/witness and
  pixel/end/retirement functions plus the real alpha blender. It checks eight
  record births, failed allocation and stale token/reuse rejection, all548
  pinned callback writes against the four real materials, partial/zero-alpha
  behavior, missing writes, malformed callbacks and shadow retirement.
  Scope, shape, writer-ready and other-family clears are explicit stubs;
  this is not live constructor/RLE/event/Present execution.
- `scripts/check_family_writer_interleave.py` uses the actual central writer
  and retirement functions for49 pairwise family transitions, normal/blend/
  shadow and no-callback holes. Acquisition itself remains modeled.
- Launcher tests check preset-only selection, inherited-control removal and
  fail-closed asset corruption; the existing package tests still apply.

No original game data, actual smallrock scene, GUI, final visible pixels or
normal gameplay has been verified by this batch. The adapter remains an
experimental public-preset candidate, not a complete second-level remaster.
