# Finite Layer1 grass/sand tests

CPU-only tests for the private nine-ID candidate. They execute extracted
production functions with independent literal membership/pixel oracles and
synthetic HDA inputs. They do not run the game, create or evaluate artwork,
capture screenshots, modify production source, or publish. Temporary fixtures
and fault diagnostics are retained.

## Run

Requirements: Python3.9+, a C99 compiler, ASan/UBSan; licensed original game files
for the binder. Run from the repository root after applying the finite renderer
candidate and this test-only patch. `OUT` must be an external report directory.

```sh
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$OUT"
python prototype/fixtures/test-grass-sand-source-scope.py \
  --report "$OUT/source-scope.json"
python prototype/fixtures/test-grass-sand-binder.py --sanitize \
  --data "$TYRIAN_DATA_DIR" --report "$OUT/binder.json"
python prototype/fixtures/test-grass-sand-alpha.py \
  --report "$OUT/alpha.json"
python prototype/fixtures/test-grass-sand-mutations.py \
  --binder-report "$OUT/binder.json" --alpha-report "$OUT/alpha.json" \
  --report "$OUT/mutations.json"
```

The first three accept `--source OTHER_REPOSITORY`; all defaults are relative
to the fixture location. No private checkout path is embedded in the patch.
Original data are not bundled. `TYRIAN_DATA_DIR` can replace `--data`.
LeakSanitizer is disabled under ptrace; address and undefined-behavior checks
are enabled. A failing mutant counts only with an actual oracle or sanitizer
diagnostic, never because of a random process failure or compiler error.

## Baseline and source scope

`grass-sand-baseline-sha256.json` freezes all107 source/header files at commit
`7c7aee388e384840915bd2532bbcc038c3d5047e`. The source-scope test requires106 to
remain byte-identical. Reversing exactly eight finite edits in render_mirror.c
must recover its full baseline SHA256. This proves no generic draw, blend,
shadow, filter, pixel, ownership, entity, loader, timing or gameplay code changed.
It is deliberately strict; a later unrelated source change requires explicit
review and a new baseline, not relaxed comparisons.

The binder independently verifies the original Layer1 callsite uses
blit_background_row/NORMAL and14-column advancement. Unlike Layer3, Layer1's
existing row API forwards supplied styles; tests preserve that established API
while exercising NORMAL from the original caller. No generic style policy was
added. The new exact IDs are66/67/69/76/78/79/80/89/90 in slots312..320, with
321 assets and162 source registrations. All nine original tiles are fully
opaque, as verified against SHA256-checked shapesz.dat. Alpha-hole controls
are synthetic compatibility cases, not artwork requirements.

The exact excluded forest10 are211/212/213/215/221/223/231/232/233/234. No
forest binding is added. Original neighbors47/49/50 retain their prior slots.

## Coverage

- Exact finite helper values for0..1000 andUINT_MAX, all layers and byte-valued
  bank names, null and equal-byte/different-pointer negatives, unknown IDs,
  first-binding precedence and cross-family aliases, map resets and overflow.
- The unmodified original loader registers100 real pointers:54 Layer1,
 15 Layer2 and31 Layer3, including the existing duplicate351. All99 distinct
  terrain assets retain separate caches. A synthetic213-pointer load preserves
  the first162 pointers without overwriting or aliasing later sources.
- Missing-all/each,38 malformed file classes for every new member, invalid
  member isolation, persistent cached rejection,4x fallback, all seven disabled
  guards, exact row bit masks/order/coordinates/traces and draw-failure fallback.
- Prior64 cloud NORMAL/blend behavior,131 gray NORMAL/shadow behavior, purple169
  separation, all90 prior terrain slots and unmodified entity reserves. Every
  old asset slot0..311 is also filled with distinct cached sentinels while all
  nine new assets load; prior metadata, payload pointers and bytes must remain
  byte-identical.
- Actual NORMAL compositor, original indexed blitter and pixel callbacks for
  all40 new grass/sand9 plus purple13/gray18 IDs at2x/4x/8x. Exact RGBA, indexed
  bytes, selected flags, ownership, clipping and guard bytes. Original63 mixed
  gray/purple rows are retained and63 mixed grass/sand/gray/purple rows added.
-35 deliberately introduced faults must compile and then fail the independent
  oracles, including12 grass-specific faults and23 prior terrain/pixel faults.

## Existing fixture compatibility

The patch also updates the prior fixtures' extracted-helper lists, strict
capacity assertions, literal accepted Layer1 sets, original loader counts and
capacity-boundary probes. Existing negative guards remain. Terrain asset
inventory permits exactly77,90 or99 complete IDs; no arbitrary supersets.
Existing gray/purple alpha and entity source/pixel oracles are retained.

Focused prior suites checked with ASan/UBSan: cloud-shadow, green-background,
green-head-layer, ground, road, plateau, underlay, holes, next-seven, gray binder,
purple binder and purple alpha. Full unrelated entity Cartesian products are
not rerun; exact source-scope proof covers their unchanged production functions.
The current entity extraction/capacity compatibility changes are included.

## Frozen v3 artifact and rebuild checks

The selected-art gate now pins runtime manifest SHA256
`01cab117a442828ecf499c5c8955bba29d64658afe5b6dd2f35f9019945083a4`
and corrected formal source inventory revision 2, SHA256
`e875ecd3fe33b0867ab5dd18ff664035c62b2276a48e4d75a6e31bb2df67edf6`.
Pillow and a C++17 compiler are additionally needed for these artifact checks.
After importing the frozen source package and nine assets:

```sh
python prototype/fixtures/test-purple-selected-pack.py --grass-extension \
  --baseline 7c7aee388e384840915bd2532bbcc038c3d5047e \
  --report "$OUT/selected-packs.json"
python prototype/fixtures/test-grass-sand-art.py \
  --package assets/hd/artwork/grass-sand9-v3 \
  --pack assets/hd/packs/packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test \
  --rebuild --report "$OUT/art-and-rebuild.json"
python prototype/fixtures/test-grass-sand-alpha.py \
  --actual-package assets/hd/artwork/grass-sand9-v3 \
  --report "$OUT/actual-compositor.json"
git show 7c7aee388e384840915bd2532bbcc038c3d5047e:assets/hd/manifest.json > "$OUT/baseline7c7.json"
python prototype/fixtures/test-grass-sand-art-mutations.py \
  --baseline-manifest "$OUT/baseline7c7.json" \
  --package assets/hd/artwork/grass-sand9-v3 \
  --report "$OUT/art-mutations.json"
```

For an archive without Git, the selected-pack and art fixtures accept
`--baseline-manifest "$OUT/baseline7c7.json"`; its complete SHA256 is pinned to
7c7, so an arbitrary supplied manifest cannot weaken the baseline. Do not pass
both `--baseline` and `--baseline-manifest` to the selected-pack fixture.

The strict grass-extension mode requires:
- Exactly nine additions per default pack, with counts325/329
- Every prior manifest and canonical source record unchanged; all nondefault
  packs and the two default pack identities unchanged
- Exactly nine new canonical source catalog records, matching frozen PNG file,
  decoded RGBA and full HDA hashes; all nine alpha channels are255
- All frozen purple13/entity9 metadata, PNG/HDA payloads and alpha checks retained
- Current cloud64 HDA SHA256
  `1f9378615e16157f59113a47066dd28a52433c28e5a36d8845491b355e64a3b8`
  and PNG SHA256
  `5a7b79fac3399d87cde0fb2d855e92e2121ed127a5112f7afcb5216e70deead3`

The independent formal-source audit hashes all37 listed package files, all
seven canonical inputs and every selected output. Rebuilding from an unrelated
path containing spaces reproduces all nine decoded RGBA and full HDA hashes.
PNG encoder variation is disclosed for rebuilt files; selected canonical PNG
files remain frozen byte-for-byte. The rebuilder's same-package, ancestor,
nested-package and occupied-output guards are exercised on private test paths.
A wrapper only retains temporary compiler products; it does not change the
frozen rebuilder source. No original game data or generative rerun is involved.

The actual-art alpha option independently decodes each frozen PNG for its pixel
oracle and loads its HDA through the production loader. All81 combinations of
nine cells, three placements and2x/4x/8x scales check exact RGB, indexed bytes,
ownership and clipping in the original NORMAL path.27 in-memory artifact/delta
mutations must be rejected with their intended assertions.

The old selected-pack mode remains available for the historical purple import,
including its strict22-addition comparison. Baseline0044 must not be used to
claim current peers are unchanged: cloud64 was intentionally revised after
805304f. Its old unchanged-peer claim is verified to fail at cloud64; the guard
was retained rather than exempting arbitrary changes.

## Runtime and visual scope

These fixtures establish source, artifact, reconstruction and pixel behavior.
They do not run the game, take captures, or establish runtime visibility or
aesthetic acceptance. The known80 entering fragment at3099–3131 alone does not
establish a grass motif. Any independently approved whole-motif runtime review
remains separate evidence and must not be inferred from these test passes.
