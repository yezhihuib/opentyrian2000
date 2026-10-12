# Manufacturer startup source/unit tests

No original game data is used and no game binary is launched by these tests.
Run from repository root, with SDL2 development headers/library discoverable:

```
python3 prototype/tests/startup-logos/test_source.py
python3 prototype/tests/startup-logos/test_runtime.py
python3 prototype/tests/startup-logos/test_runtime.py --sanitize
python3 prototype/tests/startup-manufacturer/test_package.py
```

`test_runtime.c` includes actual production `startup_logos.c`, replacing only
I/O/allocation and selected SDL calls with failure-injection wrappers. Synthetic
source identity guards are explicitly overridden for this test build; the Python
runner separately asserts all four immutable production guard definitions.
The production binary has no test flags, input injection, exit gates or readback.

The synthetic software renderer validates nearest center sampling at2× and exact
canonical sampling at4×. This is not actual-window or real-startup acceptance.
The finite allocation ledger asserts the two-buffer8192000-byte heap maximum,
no allocations/I/O on repeated presentation, and zero live buffers at shutdown.

`--sanitize` enables ASan/UBSan. Optional `--leak-check` requests LeakSanitizer;
it is unavailable under this executor's tracing and must not be reported passed.
The ordinary sanitizer run uses the finite allocation ledger without LSan.

The preservation source test pins normalized8227aff source hashes after removing
only new explicit startup hooks, and compiles a small actual-intro-function call
sequence oracle. It verifies82 original presentation calls, two original waits,
and unchanged timer/input/title source. Full private actual-startup capture and
input observation remain a later gate, outside production.
