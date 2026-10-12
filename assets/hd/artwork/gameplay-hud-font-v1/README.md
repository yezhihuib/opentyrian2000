# Gameplay HUD dynamic font V1: portable source package

This package reproduces the reviewed, frozen HUF1 font artwork without original
game data, canonical-image inputs, a repository checkout, or recovery-location
helpers. It is a source/resource handoff; it does not install a renderer or
assert any game-capture or runtime QA result.

## Canonical outputs

| Output | Bytes | SHA-256 |
|---|---:|---|
| `canonical/tiny-coverage-atlas-4x.png` | 20474 | `f81c31f85ec8646e5fd5e29e9cb9e6f03b8f51988e3dfc945bc2fa6821dfed92` |
| `canonical/tiny-coverage-atlas-4x.alpha.bin` | 163840 | `e4f245519b2922b3f3575ae499f0419bfc85742d059a07680f3693e68ddbaeb7` |
| `canonical/tiny-vector-atlas.svg` | 58612 | `eced60613272f6553626d28391e96b919d73a5ee3868b7d978edac64b9e2592b` |
| `canonical/gameplay-hud-font-v1.hda` | 163952 | `3c328c1537cf1e09529ae8805e98a8deb57a859ea80ba269cfea0b55cfae539e` |

The vector geometry, two standalone builders, compatibility contract and all
four output files are byte-identical to the exact recovery. No artwork was
redrawn, regenerated to a new style, or inferred from a preview.

## Portable metadata normalization

Only two JSON string values were normalized in
`sources/source-font-metrics.json`:

- `source_files["tyrian.shp"].path` is now `tyrian.shp`.
- `source_files["fonthand.c"].path` is now `src/fonthand.c`.

These are provenance labels, not paths opened by either builder. Source SHA-256
values, every metric, character mapping, opaque bound and vector record are
unchanged. The new metadata-file SHA-256 is
`46d34fabd3014be2ef53282ffb2162fc16c75f0196054794cad500b57819f41a`.
The only dependent edit is `metrics_source_sha256` in
`sources/original-atlas-manifest.json`. `proof/metadata-normalization.json`
records both before/after hashes and an exact JSON-field diff. The immutable
recovery directory/archive was not modified.

The `original-atlas-manifest.json` filename is retained for builder
compatibility. It is a recovered metadata serialization, not a claim that a
vanished historical JSON file was byte-recovered. The unchanged vector-only
reproducer has an older `PENDING_HOOK_ENGINEER_NOT_DEFINED_HERE` report field;
that field describes its stage, not the final protocol. The HUF1 contract,
resource packer and fresh resource proof are authoritative here.

## Scope and rendering semantics

- 127 geometric glyphs exist; exactly 86 mapped ASCII glyph IDs 0 through 85
  are runtime-eligible. IDs 86 through 126 are unreviewed extended geometry.
  An unsupported extended/accented text run remains wholly classic.
- Coverage is alpha-only. Foreground uses authored palette role 7 and the
  original caller hue, brightness and highlight/tilde arithmetic. Source edge
  shading is replaced by authored coverage, not copied as pixel geometry.
- Preserve original byte mappings, glyph widths/heights, `width + 1` advances,
  space advance 6, unmapped-byte behavior and control-byte semantics.
- FULL_SHADE renders four complete black strings at (-1,0), (1,0), (0,-1),
  (0,1), then the complete foreground string. Do not interleave by glyph.
- Green score/level roles remain green; bottom messages retain original
  white/gray. No opaque background plate is introduced behind scene text.
- Canonical density is 4. Native 2x uses the reviewed nearest sampling;
  density 8 repeats each canonical texel in a 2x2 block.
- Runtime context, history, source equality, fades, fallback and lifetime are
  separate integration responsibilities. Do not replace shared menu fonts.

## Standalone build and safe wrapper guidance

Canonical toolchain: CPython 3.12.14, Pillow 12.3.0, zlib 1.3.2. Pillow is the
only non-standard-library dependency. PNG byte identity depends on its encoder;
alpha, SVG and HUF1 must also retain their exact hashes.

Copy this whole directory wherever the repository's art sources belong. Keep
`sources/` adjacent to `reproduce.py` and `build_resource.py`. Inputs are resolved
from each script's `__file__`, not the caller's working directory. Do not carry
`recover_exact_dependencies.py`, extraction paths, old captures or recovery
workspace helpers into the repository.

Pass explicit, separate output locations so a build cannot overwrite the
canonical assets or fill the source package with generated proof files:

```sh
python3 '/path with spaces/gameplay-hud-font-v1/build_resource.py' \
  --output '/separate output/gameplay-hud-font-v1.hda' \
  --proof-output '/separate output/vector-proof'
```

For a repository wrapper, use `Path(__file__).resolve()` to locate the package
and `subprocess.run([sys.executable, str(builder), "--output", str(resource),
"--proof-output", str(proof)], check=True)`. Resolve the two output paths first,
reject overlap with the source/canonical directories, and pass arguments as a
list. Avoid shell-concatenated commands and assumptions about current working
directory. The wrapper should install only the successfully verified HUF1 into
the runtime data staging tree; installation is not performed by this package.

`build_resource.py` invokes the standalone vector rasterizer. It validates all
127 canvases, zero coverage outside exact glyph canvases, empty slot 127,
86-glyph eligibility, all computable mapping/metric/payload signatures, header
layout, EOF and the final resource SHA. Compatibility signatures for PIC3,
palette and original encoded font are supplied stamps, not recomputed from
original assets by this package.

## Fresh relocation proof and inventory

A fresh build was run from a foreign working directory with spaces in both
relocated source and output paths. Only the seven builder/source/dependency
files were copied; no canonical PNG, SVG, alpha or HUF1 was available in the
relocated input. All four generated outputs matched the approved hashes and
canonical bytes. See `proof/relocated-build.json` and the fresh resource and
vector reproduction reports. These are build proofs, not runtime evidence.

`FILES.txt` is the exact file inventory. `SHA256SUMS` checks all files except
itself; `manifest.json` records every source, canonical output and proof file
(excluding the two hash/inventory bookkeeping files and itself). From this
directory, `sha256sum -c SHA256SUMS` verifies the complete package.
