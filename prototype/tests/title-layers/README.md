# Title-only compositor source and synthetic unit gates

These tests include the actual `src/title_layers.c` production module. They do not
run the game, invoke its entrypoint, copy original game artwork, publish assets,
or accelerate or change game timing. SDL uses an in-memory software renderer.

Run from the repository root with SDL2 development dependencies available:

```sh
. /workspace/scratch/f67dd347fa0a/recovery-dependencies-20261012/env.sh
python3 prototype/tests/title-layers/test_source.py
python3 prototype/tests/title-layers/test_runtime.py
python3 prototype/tests/title-layers/test_runtime.py --sanitize
```

The sanitizer build enables ASan and UBSan with immediate failure. LeakSanitizer
is explicitly disabled because it is unsupported under ptrace in this environment.
Every production heap allocation and free, and nominal texture lifetime, are also
tracked independently by the harness. Fixture/oracle allocations are outside that
production ledger. No original source identities are weakened in production:
compile-time guarded identity constants alone are replaced by independently
calculated hashes of generated fixtures. Source dimensions and all protocol,
state, coverage, palette, source, and resource checks remain production code.

Coverage:

- Exact 80-byte little-endian TLV1 resources and all 80 header bytes; missing files,
  nonregular files and FIFOs, short/long payloads, hash corruption, opacity, support
  bounds and transparent RGB; all seven missing-resource combinations.
- Original source dimensions/identity, palette and RLE source registration;
  same-index version shadow coverage, exact current palette roles, opaque-index
  zero, arbitrary authored alpha, overlap and transparent holes against a separate
  full-frame integer source-over oracle.
- Initial pose and all 29 original motion poses, settled restart, indexed
  background/menu checkpoints, highlight reset, cursor right-row/bottom locations,
  full 64,000-byte erase verification and off-cursor tampering.
- Art-only 10-step and UI-only 20-step fades, full-black 10/15-step outgoing fades,
  independent channel recurrence, palette tamper and malformed sequence rejection.
- Whole-epoch allocator/SDL failures, independent I/O fallback, no retries inside
  failed epochs, texture recreation, exact 2x nearest output, no per-presentation
  heap allocations or resource I/O, and exact peak dynamic/fixed storage ledgers.
- Source comparison against `93de0fe4cb935f1d7cf7d737c86e0ff3f3f8c218` after
  removing explicit title hook statements and reversing the sole approved CLI help
  literal. Original indexed writes and
  manufacturer/title control flow retain identical code tokens. Input, timing,
  manufacturer module bytes, and the manufacturer intro function are unchanged.
  Checkpoint hook counts/order, foreign-screen retirement and Windows registration
  are checked separately.

The runtime module is driven by synthetic original write callbacks. The source
suite verifies callbacks reside after the real original sprite writes. This is
source/unit coverage, not actual-engine visual validation or physical GPU,
fullscreen, Windows, joystick, or demo-return coverage. Final artist alpha assets
and bounded actual-engine evidence are recorded separately in docs/STARTUP_TITLE.md.

After independent review, 18 malformed checkpoint enum/no-before regressions were
added, including negative sentinel collisions. They add no presentations; the full
normal/sanitized suite retains 736 presentation checks.
Extreme address, null, below-base and past-end callbacks are rejected using defined
unsigned arithmetic before any pixel dereference; sanitizer cases cover those guards.
