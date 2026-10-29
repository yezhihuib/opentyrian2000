# Shared enemy projectile145 — lavender metal

This finite addition targets **ordinary sprite-sheet bank8, selector145** only.
It shares the existing projectile91 owner lifecycle, not that projectile's art,
optional-resource eligibility or palette subset. It does not add a provider
architecture or alter firing, movement, collision, native coordinates or RNG.

## Authored asset and registration

The generated master is
`authoring-inputs/projectile145-current/projectile145-lavender-v2-concept.png`
(SHA256 `e485f853ae8e4efab03adb852224a58453e20c9629115609c41193cd0fe3e274`).
The retained prompt and provenance describe a newly generated metal projectile,
not an enlarged original sprite. No original image was passed to image generation;
original colored pixels were inspected privately and are not packaged here.
The second generation corrects the rejected first candidate's heading.

`scripts/current_projectile145_compatibility.py` deterministically crops
`[114,349,854,1163)` from the 1161×1355 generated RGBA master, resizes to70×70
with LANCZOS, and places it at `(0,25)` on the96×112 canvas. It clips only to the
original39 occupied native cells and canonicalizes transparent RGB to zero.
The generated RGB is never derived from original game colors. All39 occupied
cells retain authored coverage:1920 nonzero-alpha subpixels, including1790 soft
and130 opaque. The full12×14 logical canvas and zero anchors are retained.

The single HDR1 transport has role150/identity1500145, internal density8,
12×14 native dimensions, anchor0,0. Its payload SHA256 is
`d5ac9ea2737a93926744581bdd78d80ec6340d8890b961686be0eacdfed0e204`.
The runtime uses the generated payload FNV pin `1e1ff56840c2746b` and fixed
role/geometry checks. The build script and mapping pin the entire transport.

```sh
python scripts/build_current_projectile145.py stage --selection <candidate.json> --stage <new-external-directory>
python scripts/build_current_projectile145.py apply --stage <staged-directory>
python scripts/build_current_projectile145.py check
```

Stage is non-mutating; apply uses the existing current-family transaction checks.
The generation-time provenance's `runtime_qualification: false` is historical
creation metadata, not a replacement for subsequent validation receipts.

## Runtime boundaries

The complete ordinary bank is authenticated through the unchanged bank8 source
witness. The145-specific palette subset contains indices49,84–89,91,93,95.
Missing or corrupt145 must not disable an otherwise eligible91, and vice versa.
Only actual visible contributions set the finite owner's used-member bits.
An already-consumed member remains a final/cache dependency even if a real
Talon draw subsequently takes pixel ownership. Native-underlay colors and the
cached complete palette retain their existing checks; unused-member independence
is not a blanket exemption from palette validation.

The original indexed native blit still executes exactly once at its original
coordinates. Unknown/Christmas banks, a foreign source/palette, unsupported
geometry, missing/corrupt resources or internal density other than8 decline to
classic. Display/window2× or4× is distinct from internal density. The observed
normal E1–E3 weapon4/8 identities do not grant eligibility by episode number;
E4/E5 embedded tables differ and are not claimed to share those identities.
Potential map placements are not evidence of a shot having fired.

## Completed bounded evidence

-13 authoring/package checks cover deterministic generation, pins and the finite
  runtime mapping, not native lifecycle behavior.
- The unchanged37-case projectile91 harness plus70 new145 cases pass107 cases
  and223,603 assertions. The new cases include both draw orders, independent
  resource/palette failures, native callback and wrap boundaries, final/cache
  dependency rejection and two **real**145→Talon transfers (`copied=376` each).
  The first local run instrumented4 fresh TUs with ASan/UBSan and reused82
  bound native objects; it was not a fully fresh or fully instrumented game.
- A source-bound ordinary game derivative observed E1 physical level2, original
  actor194/link3 using weapon4, naturally emitting selector145 at tick1162.
  The shot starts at242,79 and is actually drawn at239,82 after its normal update.
  Twenty-four observed frames1162–1185 each provide130 visible opaque authored
  pixel witnesses. The test uses fixed debug input/seed; no actor, shot or pose is
  injected. Output-only log filtering does not alter game control flow.
- A separate single-tick1162 present/missing145/qualified-baseline comparison uses
  internal density8 and physical window2×. Eleven native/state artifacts agree
  byte-for-byte, including INDEX8,768-byte palette and RNG/state records.
  Missing145 equals the baseline HD output. The present delta is2496 internal
  pixels/156 physical pixels, exactly within the39-cell native support;
  outside-support delta and classic delta are both zero. There are130 exact
  opaque authored witnesses, and582,550 other HD pixels outside this support
  remain different from classic. All9 captured BMPs are retained losslessly in
  verified ZIPs with exact recovery maps and equivalent PNGs.

The natural comparison has **zero blend writes, collision events and player-fire
activity**. It does not claim those paths, old91/145 natural same-frame overlap,
interactive campaign launch, other levels, platforms, GPU drivers or a full gate.
The lifecycle harness supplies separate non-vacuous overlap/alpha checks.

## Qualification records

Four independent fresh builds completed for default-off, HD-on, mirror-disabled
and HD-on ASan/UBSan:86 fresh production translation units per configuration,
344 fresh objects, with no prior project-object reuse. The unchanged107-case
harness also passed using84 fresh sanitized objects plus a fresh renamed main
and renderer/harness translation unit. All project TUs in that sanitizer
configuration are instrumented; external SDL/system libraries remain native and
LSan is disabled. The sampled output peak was218,468,352 bytes under the256MiB
budget; the sampled minimum free space was436,703,232 bytes, above250MiB.

The original fresh wrapper receipt is **FAIL_BINDING_RETAINED**, not an overall
PASS: a raw Git-index hash changed during the run. Independent exact reconstruction
of the pre-run index proved that only the7958 newly hydrated entries had their
zero stat caches populated from unchanged files. Path/blob/mode/stage/flags and
the TREE extension were identical; every consumed source/script/asset/producer
and all four source copies remained byte-exact. The writer is unknown. A separate
accepted-disposition record accepts the functional four-build/107-case results
with this explicitly retained deviation; the failed receipt and assertions were
not rewritten and the builds were not repeated. The later raw index is only a new
freeze baseline, never a replacement for the original pre-run binding.

Historical receipts are not silently rebound to later documentation/projection
files. Hydration of a formerly sparse checkout is a completeness prerequisite,
not qualification.

A new145 inverse/ledger and explicit deployment profile must preserve all earlier
qualified sources, historical ledgers and the original255-method ordered suite.
The full gate is not claimed by this preparation document; its terminal receipt
and independent review determine that status.
