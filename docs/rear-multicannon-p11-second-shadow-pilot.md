# Rear Multi-Cannon P11 SECOND shadow pilot

This presentation-only extension starts at published commit
`a0d5e7d8503bf304ac952341461d8b1f609b52b9`. It adds physical weapon record275,
SECOND mode, to the existing finite P11 shadow path in Episode1's first Normal
level (physical level9), density8. Its eight admitted phases are
277,278,295,294,298,299,40,2. Record264 FIRST retains its existing six-phase path.

Each shadow reuses its own accepted head alpha, with no head RGB, new artwork,
resampling or mirror synthesis. In particular, accepted HD40/2 are independent
assets, not exact reflected copies. All head/resource/source/record pins remain
unchanged. The original shadow position, original INDEX8 darken exactly once,
low-nibble rounding and existing ordered command compositor are unchanged.
There are no gameplay, coordinate, allocator, damage, timing, power or RNG edits.

Admission requires the original sealed record275/mode2 birth in its actual
renderer-owned slot, exact phase/live-shot identity, its full80-field record pin,
exact bank/source pin, captured resource root/density, and safe disjoint surface
and canvas layouts. Record264/mode1 is checked against its own admitted record.
Current equipment changes retain earlier births, including the final drawn
lifetime counter0. The existing one-command lease, epoch checks, alpha/cloud
ownership and overlap-expanded restoration remain shared and unchanged.

The other20 rear routes retain their prior shadow paths, including existing
generic HD shadows. Byte-identical physical aliases, slot80, negative x,
density4, Hard level15, excluded game modes, unsafe geometry and missing/corrupt
resources retain the existing fallback behavior. The existing13 generic shadow
entries are untouched; no shared bank8 raw is globally bound.

## Reproducible synthetic checks

Use fresh output directories:

```sh
python tests/run_rear_multi_p1_core_tests.py /tmp/rear-core-new
python tests/run_rear_multi_p1_adapter_tests.py /tmp/rear-adapter-new
python tests/run_rear_multi_p11_shadow_tests.py /tmp/rear-adapter-new /tmp/rear-shadow-new
python tests/test_rear_multi_p1_source_inverse.py
```

The extended existing C shadow guard test passes151,488 checks in each strict
C99 and ASan/UBSan run. It covers all6+8 phases in all80 owned slots, all80
serialized record bytes,96 negative families,16 malformed-resource families,
the other20 routes, aliases, retained births and reset epochs. These synthetic
preparation checks alone do not establish SDL output or gameplay coverage.

The last command has an inherited, explicitly accepted failure in the published
baseline: its retained old source-projection fixture does not invert the earlier
observer hooks. This extension leaves that fixture and the inverse test
byte-identical. It does not claim that every repository test passes.

## Private offline output validation

Actual decoder, loader, wrapper, original blitter and command-compositor excerpts
were paired against the published baseline with authentic records/bank data and
unchanged accepted assets. Independent full-canvas integer oracles passed in
strict C99 and ASan/UBSan on both sides:1,849 cases,3,582 shadow commands,
34 restorations and109 native SDL readbacks per run. The candidate completed
33,084,991 checks, including521 negatives. The separate cold-cache suite passed
32 missing/corrupt-resource cases across all eight phases in plain/sanitized
runs. Twenty-eight preservation digests for264 and the existing13 generic
shadows matched exactly across RGBA, ownership, cloud provenance and INDEX8.

Native640×400 base/new pairs on bright, real-terrain and real-cloud underlays,
including birth overlaps, received limited visual review before gameplay.
These are synthetic scene arrangements using real accepted assets. They do not
change backgrounds or establish gameplay coverage. Full sanitizer processes
completed without diagnostics with monitored RSS below113MB each; their normal
sanitizer virtual address space was allowed.

## Bounded actual-SDL gameplay result and remaining gap

Exactly one180-tick baseline/new pair completed through actual SDL ordinary
New Game / Full Game / Episode1 / Normal menus and a genuine P4 shop purchase.
Two disclosed diagnostic rear-power-byte changes selected P10 and P11; mode
switches used the actual SDL key handler. This does not establish an ordinary
P11 purchase. The natural RNG/start gates, all20 named original observation
streams and four explicit mixed-stream original-field projections were equal.

All560 safe record275 shadow commands were admitted exactly once. The other48
original275 shadows retained negative-x native fallback. Existing264 shadows
remained668/668 on both sides, and all three observed rear normal-head route
admission/identity checks remained exact. Every admitted shadow passed the independent per-draw full
clipped alpha/owner/cloud/green/selection oracle, with unchanged whole INDEX8
before its single original blit. Sixteen sampled native640×400 groups per
process matched the final upload; all new differences stayed inside admitted275
shadow rectangles. The same-tick114 native pair received limited visual review.
The actual pair remained within its512MiB/process and1GiB/pair resource caps.

The original runtime report remains196/197 checks satisfied. Its all-eight-phase
isolated final-pixel gate is INCOMPLETE: phases3/4 have no independently
attributable native sample after excluding every other original shadow's whole
12×14 rectangle and every current head rectangle. The other six phases have
isolated final witnesses. A separate read-only diagnosis found24 correctly
admitted draws for each missing phase,245,760 checked subpixels each and zero
oracle errors. In the two sampled ticks55/56,403/392 authored-alpha samples
fall below the184-logical-pixel gameplay viewport. The remaining141/140 samples
are all covered by excluded head/shadow rectangles. They include42/38 genuinely
changed pixels, with zero independently attributable support. This is an
attribution limit of the retained samples; it is not a claim that both phases
have independent final-frame proof. The original failed gate is unchanged, and
no rerun or extra capture was used to manufacture witnesses.

Eight-phase offline full-canvas results and eight-phase actual per-draw oracles
therefore support only the stated finite scope. Neither offline nor runtime
evidence is campaign, Windows, whole-level or ideal whole-frame compositor
acceptance. The separately inherited source-inverse failure also remains.
