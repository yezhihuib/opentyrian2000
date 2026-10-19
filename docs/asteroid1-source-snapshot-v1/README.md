# Strict ASTEROID1 source-bank comparison

The five opt-in families share one renderer-owned 42,012-byte private reference
of the original NEWshd bank. The first eligible source check copies the bytes
and validates that copy against the existing FNV pin. Every eligible draw then
compares all current bank bytes to that reference, including the initial check.
The reference is immutable while trusted. Renderer shutdown revokes trust; its
static storage needs no allocation or release.

This is a byte comparison on every draw. Loaded role, pointer, size and ordinary
spriteSheet8 exclusions stay ahead of it. Full serialized record checks still
run every call. Scope, lease, selected-root cache, once-per-frame RGBA preflight,
sticky art failure and family-local rejected-frame behavior are unchanged.
A moved or reloaded canonical bank is eligible; changed bytes at the same
address fail. Invalid cold bytes never become trusted. Art and gameplay are
unchanged, and the separate global manual-HD registry remains 629 assets.

## Bounded verification

- All five existing asset suites passed optimized and ASan/UBSan, with each
  positive geometry/identity case and 99 negative resource cases per mode.
- The focused production-source regression passed 247 checks per mode. It covers
  all 22 family record dependencies, cold exclusions and invalid bytes, warm
  first/middle/last-byte corruption, bank slots/roles/sizes, unloaded pointers,
  distinct reload, in-place address reuse, live-bank release and shutdown epochs.
- Two actual-engine baseline/candidate pairs preserve final RGBA, gameplay, RNG,
  classic INDEX8 signatures and HD/record/RGBA-preflight call counts exactly.
  Both use 120 original-event physical1 ticks and no captures.
- Source-check CPU time fell 0.4906 to 0.0146 seconds for seed 0x5eed and 0.6690 to
  0.0106 seconds for seed 4. These are isolated guard measurements. Whole-process
  timing varied, including a slower candidate run; no stable whole-game
  percentage or FPS improvement is claimed.

See validation.json for signatures, counts, limits and evidence scope. This
finite software-rendered scene does not certify natural campaign progression,
level completion, Windows, a real GPU or fullscreen operation. Leak sanitizer
is disabled under this executor; address and undefined-behavior checks passed.

Run the focused regression with:

```
python3 tests/test_asteroid1_source_snapshot.py --data ORIGINAL --out OUTPUT --sanitize
```

Run each existing test_asteroid1_{ten,four,common4,random5,goldwing}_assets.py
suite with the same arguments. Supply explicit --sdl-include directories for
those suites when SDL pkg-config metadata is unavailable.
