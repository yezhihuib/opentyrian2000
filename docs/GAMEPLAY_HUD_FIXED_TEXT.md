# Fixed gameplay typography: MODE, SHIELD and ARMOR

This finite HUT1 stage adds twelve opaque canonical 4× tiles: MODE and eleven
vertical letters. It owns exactly 370 logical cells; the one-row vertical gaps
remain original. FRONT/REAR GUN stays in HUC1. No shared font table, dynamic
score/message/level text or gameplay writer changes in this checkpoint.

## Contract and source

HUT1 has an independent single-player PIC3/surface lease using the existing
HUD lifecycle mechanism, with its own palette and source checks.
Each complete label group is checked against original indexed source before
composition. Changed or unsupported input remains original. Source capture
precedes palette installation; compatibility is evaluated when composing.
Missing/corrupt HUT1 leaves other HUD and scene HD active. Canonical density 4
uses nearest sampling at native 2× and repeated subpixels at density 8.

HUT1 is 23,744 bytes: 64-byte header plus 23,680-byte payload. SHA256:
6d096f31085b22fb381761d3c8460bd06956c2bd039a1e0cc97481bc09819745.
Checksums detect corruption; fixed sizes, bounds and source identities are
validated separately. The source contains vector paths, with no original PIC,
palette or font bitmap payload.

Run `python prototype/build-gameplay-hud-fixed-text.py --output /absolute/fresh/path`.
The wrapper rebuilds selected PNGs/HUT1 and rejects existing, in-repository,
ancestor and symlink output paths. `prototype/build-hd-assets.py` verifies both
default packs. Freeze-time artwork metadata describes an earlier trial status;
this document records completed integration. Referenced redundant verification
scratch directories are not imported; compact receipts are pinned separately.

## Bounded validation

Independent sanitizers cover 328 malformed resources, 11 I/O/allocation faults,
370 source mutations and 48 fade-removal comparisons. Prior HUD suites pass.
No-HUT1 classic/HD runs retain exact source/RGB ledgers; collision evidence in
those cases is header-only.

Actual native 2× and true 4× tick 250 match all canonical samples. Same-scale
before/after changes 927 and 3,824 pixels respectively, zero outside 370. All 33
invariant streams and 251 original state/source/RNG observations match. A combined
native 2× frame equals the accepted fixed-text and published corner V2 trials,
with zero changes outside their disjoint 706 cells. Root/author visual gates pass.

One 4× preparation attempt encountered a mutable shared-pack dependency and was
excluded by its integrity gate. The corrected run uses pinned immutable inputs
and passes. Fade/modal behavior is source/unit evidence, not new natural runtime
lifecycle coverage. Private observer hooks are excluded from production.
Latest Windows compile/runtime, CI and whole-game typography are not claimed.
Dynamic protocol documents/models remain design work only; this checkpoint has
no HUF1 loader or dynamic typography production hooks.
