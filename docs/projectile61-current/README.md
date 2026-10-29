# Shared enemy projectile61 — paired red-orange energy trails

This finite addition targets ordinary sprite-sheet bank8, selector61 only.
It adds a third independently eligible member to the existing91/145 owner,
not a new provider architecture. Firing, movement, collision, timing, native
coordinates, indexed drawing and RNG are unchanged. Christmas stays classic.

## Generated artwork and registration

The transparent generated master is
`authoring-inputs/projectile61-current/raw/generated-master-01.png`
(SHA256 `5940b0956dfb10907632fef4416e13bffcadf2fb38524791a4577cfa5bca53a2`).
The original normal/Christmas sprites were viewed privately for shape and
direction; original colored images are not packaged and were not inputs to
image generation. This is newly drawn artwork, not a nearest-neighbor enlargement.
The master retains its generation-platform C2PA provenance metadata. Historical
creation-time `NOT_RUN`/candidate labels remain creation records, not claims
about the later runtime checks below.

The fixed registration crops two generated-master rectangles, resizes each to
32×88 with LANCZOS and places them at (0,8) and (64,8) on a96×112 canvas.
`registration.json` records the exact rectangles and Pillow version. Alpha is
not promoted; unsupported cells and alpha-zero RGB are canonicalized to zero.
All74 native cells (37 per side) contain generated alpha. The middle four native
columns remain entirely transparent. The result has3499 soft and246 opaque
subpixels, with no change to the12×14 native canvas or zero anchor.

The HDR1 transport is role151, identity1510061, internal density8,12×14,
anchor0,0. Whole-file SHA256:
`3530c27302a2cb3d26830711cd4b94a01aacbfad748c91aea219bbc81b0c5c29`.
RGBA SHA256:
`8f4d0ebc154383ece77d49e9818ce60c4e7f0239765c1b02e26e09028a7435a1`.
Runtime payload FNV1a64 is `b01c832398fd6e16`.

The actual authoring CLI supports only `--root` and `--write`:

```sh
# Check deterministic products without writing them:
python3 scripts/build_current_projectile61.py --root .
# Regenerate products only in an explicitly writable development checkout:
python3 scripts/build_current_projectile61.py --root . --write
```

There are no stage/apply/check subcommands. The check is authoring-only;
neither command establishes native behavior or full qualification.

## Runtime boundaries

The ordinary bank is authenticated by its complete existing source witness.
Selector61 checks its actual palette subset113–124 independently. A requested
Christmas bank or a nonmatching source cannot admit this artwork. Missing or
corrupt61 must not disable eligible91/145, and unused bad old members must not
disable61. This independence does not exempt a color actually sampled as native
or foreign underlay, nor weaken the cached complete-palette guard.

Member bits91=1,145=2,61=4 are set only by actual visible contributions. A member
already consumed remains a final/cache dependency even after a real Talon draw
takes pixel ownership. The existing native blit still executes exactly once at
the original coordinates. Unsupported geometry/density, bad source/palette,
missing resources or invalid callback sequences decline to classic.
Physical window2×/4× is distinct from internal density8; no internal4 HD support
is claimed for this family. Weapon identities observed in original E1–E3 data
do not grant eligibility by episode number or imply E4/E5 identity equivalence.

## Bounded native and natural evidence

-15 authoring/static checks cover the finite asset and integration contracts,
  not runtime behavior.
- The original107-case91/145 harness is byte-identical. A separate157-case61
  companion checks straight-alpha output, native mask and transparent middle
  slot, both draw orders with each old member, actual three-member overlap
  (`used=7`), two-way missing/corrupt isolation, palette/source/geometry/Christmas
  rejection, callback/wrap/reset boundaries and final/cache dependencies.
  Total264 cases pass1,045,894 assertions. Two real61→Talon draws copy267 owner
  pixels each, including231 soft61 pixels, with an exact RGB witness. This is
  **61 soft RGB retained through native-covered transparent Talon pixels**,
  not a claim that the Talon HDA has soft alpha.
- A source-bound ordinary game derivative observes original E2 physical level9.
  At actual tick150/curLoc151, actor795/link10/weapon131, actor slot50, emits
  shot slot43 at112,23; the same tick draws it at112,29, admits role151 and has
 246 final opaque authored pixels different from classic. The bounded window
  records20 emits,492 draws/admissions and452 visible candidates. This first
  witness uses same-tick records, not an inference from later slot reuse.
  The run uses deterministic debug input/seed, no actor/shot/pose injection;
  output-only log filtering does not change game behavior.
- A separate present/missing61/qualified145 comparison captures actual tick150
  with internal density8 and physical window2×. Eleven native/state artifacts
  are byte-equal, including two indexed buffers,768-byte palette and state/RNG.
  Missing61 matches the qualified baseline in all three captures. The nonzero
  present delta is4736 internal pixels /296 physical pixels, entirely within
  the74-cell native support; classic and outside-support deltas are zero.
  There are246 opaque authored witnesses and554,816 other HD pixels outside
  that support which remain different from classic.
- All nine BMP captures are retained losslessly in verified ZIPs with exact
  recovery maps and pixel-equivalent PNGs. Only those verified duplicate BMP
  files were removed. Three game processes retain identical first-use warnings
  about missing config/save files; those warnings are not hidden as empty logs.

The comparison contains383 real blend writes, whose protocol/formula/results
are identical in all variants. **None is selector61 or overlaps its footprint**:
these are other resources at y149–180, while61 occupies y29–42. This does not
claim native61 blend coverage. Retained tick0/150 diagnostics contain zero
collision/player-fire rows; this is not coverage of those paths or proof that
no such event occurred at any unretained tick. The fixed debug input is
stationary with no player fire. The evidence is one bounded natural scene,
not a complete actor lifecycle,
interactive campaign, cross-platform/GPU test or natural three-member overlap.

## Fresh build and evidence epochs

Four independent empty build directories compile all86 project translation
units each: default-off, HD-on, mirror-disabled and HD-on ASan/UBSan. There is
no reuse of old project objects. The264-case executable uses84 fresh sanitizer
objects, a fresh renamed main and a fresh renderer/harness TU. All86 project
TUs in this sanitizer configuration are instrumented; external SDL/system
libraries remain native and leak sanitizer is disabled.

The unique fresh run passes all eight commands and its final source/index/input
and budget checks. Its receipt SHA256 is
`b684d867d511c43e12e9fe5f4e0d73757403881d20cb07701661bd2341479930`.
Sampled peak232,886,272 bytes is below256MiB; minimum free space380,690,432 bytes
exceeds250MiB. The three ordinary builds retain compiler warning logs;
the sanitizer build, supplementary compile/link and both native stderr logs
are empty. These are build/native results, not a new game-loop run or full gate.

Earlier attempts are retained separately: nativev1 stopped during linking on
its smaller budget and ran neither harness; nativev2 passed the old107 but
failed the nonempty-transfer assertion at the original fixed Talon position.
Independent geometry analysis proved zero eligible overlap there. The approved
test-onlyv3 shifts that Talon x coordinate108→107, retains `copied>0` and adds
exact267/231/RGB assertions. Production and the original107 oracle are unchanged.
Failed receipts are not rewritten or counted as complete passes.

Hydration restored7958 missing tracked paths without overwriting existing files.
After its saved terminal index, an unknown writer populated exactly those
entries' zero stat caches; independent byte-level comparison proved unchanged
path/blob/mode/stage/flags/TREE and source bytes. This occurred **before** fresh
builds, not during them. The original hydration receipt remains immutable.
The subsequent explicitly authorized QA import and own-index refresh saved
actual raw/semantic before-and-after bytes. The fresh run starts from that
new epoch and preserves its raw index and complete9730-file input inventory.

Later documentation/projection/aggregate metadata is a separate epoch, not a
retroactive change to consumed native inputs. The new61 inverse/ledger/profile
must retain the earlier293-method ordered suffix and historical ledgers. Its
separate terminal qualification receipt determines the full result; this
preparation document does not claim a completed full gate or public release.
