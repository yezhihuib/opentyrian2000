# Gameplay HUD meter materials V2: portable source package

Frozen coarse armor V2, unchanged firepower and generator materials. This is a
source/resource package only. It makes no game-capture, runtime-lifecycle or
publication claim. The recovered original package remains unchanged.

## Source and canonical identities

`materials.py` is byte-exact, SHA-256
`967f9d54b043b8e6cfcc209c3630485eee51f2e69cdeec1e003bf75bf4af3b22`.
It renders continuous scalar luminance profiles at32 subpixels per logical
pixel, then BOX samples to canonical4x. `selected-rgb.json` is unchanged,
SHA-256 `98eb282953779812db0a1f2461e2a8c9701e57138638cabc550a4492c5b49e2e`.
These RGB annotations preserve original palette roles; no original game bitmap
or full palette is bundled.

Canonical HUM2 is621920 bytes, SHA-256
`3f8d9c35a3a9791d554a3c46f3431289c8ecd68b57419747ce3a40c225dafa4c`,
FNV-1a64 `52667536bbd9a9a8`. The exact1390-cell ownership mask is64000 bytes,
SHA-256 `38f313fc060ee5195071e6b5d2ed2727541e243038808147710b5575bf24d95f`.
Only the canonical resource and mask are retained; redundant canonical section
copies and PNG tile sheets are unnecessary for source reconstruction.

## Exact finite scope and displayed-state semantics

Half-open logical boxes: front `[289,17,311,20)`, rear `[289,38,311,41)`,
generator `[269,12,277,104)`, armor `[307,137,316,195)`. Their union is1390 cells.
Baked red prefix pads, shield, labels, lamps and the frame are outside scope.
Zero/blank original cells carry no generated material.

Firepower is P0..11, adjacent2x3 units j1..P, palette role115+j. It has no
extra baseline segment. Eleven opaque8x12 RGBA tiles occupy4224 bytes;
role i starts at `384*(i-116)`.

Armor A0..28 uses A+1 original two-row units, index
`226 + max(0, floor((z-1)/2))` for z0..A. Group adjacent units of the same
original palette color, then shade that coarse group once. Do not add a seam at
every two logical rows, change fill height, normalize against ship capacity,
add a capacity marker or recolor low armor. Colors stay bronze/brown through
cream. Blank wipe-only state is different from A0's baseline. Role226 has group
heights2/4/6; roles227..239 have heights2/4, totaling29 opaque tiles.
Their RGBA width is36, with576 bytes per logical row. Role226 offsets are
0/1152/3456; higher roles use `6912+3456*(i-227)+(0 if h==2 else1152)`.
The final tile ends at51840 bytes.

Generator rendering follows the original painted raster and write history,
never a synthesized current-energy gradient. For displayed q=floor(power/10):

- Increase q>last paints logical rows `[102-q,104-last)` at role113+floor(q/7).
- Decrease q<last clears `[102-last,104-q)` to black.
- q==last makes no write. Arcade power900 can still have a blank display.

Equal current q can have different occupied rows and colors. Preserve those
exact rows, their original contiguous palette runs and their positions. Accept
only verified uniform rows of index0 or113..125; reject/fall back for an unknown
or nonuniform source. Source-write provenance and the currently displayed
indexed raster must both be honored. Event-driven armor/firepower can lag live
state; do not redraw merely because live values changed.

The generator dictionary has944 opaque32x1 RGBA rows,128 bytes per row,
120832 bytes total. Lookup has222456 uint16LE IDs,444912 bytes total, bounded
0..943. For role i113..125 and contiguous height h1..92, the first lookup entry
is `(i-113)*17112 + 2*h*(h-1)` and the run reads4*h entries. All1196 materials
are directly rerendered, reconstructed from dictionary rows, and compared with
the complete frozen material-hash list digest
`e1bc71e41501f6f1b06a0eff421090086f8738e9e332fe31a20b512e855834d6`.

Native2x uses the accepted nearest sampling from canonical4x. Density8 repeats
each canonical texel2x2. These rules preserve the authored materials; lifecycle,
source checks, writer validity, fades, independently removable components and
field-local fallback are separate runtime obligations.

## Protocol and exact section identities

`contract.json` gives every header field, dimension, checksum, offset formula,
source identity and scope. Header112 bytes, `<4s11I8Q>`, magicHUM2/version2;
payload621808 bytes in firepower, armor, generatorRGBA rows, generator lookup
order. Section file ranges are `[112,4336)`, `[4336,56176)`, `[56176,177008)`,
`[177008,621920)`; exact EOF is required.

| Section | Bytes | SHA-256 | FNV-1a64 |
|---|---:|---|---|
| Firepower |4224|`ac0cc47c2c5586b20ab4000be6af9ee93f787af8e9454b3176cd96a0f5e1d4a5`|`92ce2a65c65f67db`|
| Coarse armor |51840|`bace2bdf649ab7703bc6c30d10523b559edc36fce4bf066ea2fd2620b3bdbbe1`|`33f13810daec0125`|
| Generator rows |120832|`fec8194ec5015585b41c54aa41f396b971fa51e1e8d9b88602946c663415cb6c`|`c4231771a5413868`|
| Generator lookup |444912|`c5b08bee80b40b4099c4a02a2896f900eb9c92e7480892576cfb40e69eae221f`|`1d129d23c2edc134`|

Combined payload SHA-256 is
`c7a03b1a2f546fa1ffff4fbc9b0d0bf1fdc6f9fdc0461457b7152d693fefb989`,
FNV `fcc77c108870c9db`. Full PIC3 FNV `14c1441f3d5dc0e2` and normal paletteRGB
FNV `5e80e83992be2927` are compatibility stamps supplied to the builder; no
original game-data extraction runs here.

## Rebuild and output guards

Use CPython3.12.14, Pillow12.3.0 and NumPy2.3.5. Keep materials.py,
selected-rgb.json, contract.json and build_resource.py adjacent. The builder
resolves inputs relative to its own file, independent of the current directory.

```sh
python3 '/path with spaces/gameplay-hud-meters-v2/build_resource.py' \
  --output '/separate path/new output directory'
```

The output directory must not exist, be within/contain the source package, or
have any symlink in its path. Guards run before rendering and again before
creating output. All material/section/resource checks must pass before any
output file is written. Use argument-list subprocess calls in repository
wrappers, quote shell paths, and do not interpolate shell command strings.
Canonical files are never read by the builder. It emits the HDA, four rebuilt
sections, scope mask, tile-layout metadata and build proof into the new external
directory. Legacy `png` names in tile-layout metadata are descriptive labels;
PNG tile files are not emitted or required.

## Proof and inventory

`proof/relocated-build.json` is a fresh source-only reconstruction proof, with
all section/resource hashes,1196 material checks and lookup bounds. Its input
was relocated to a path with spaces, run from a foreign working directory,
with neither canonical resource nor original game assets available. Resource
and scope bytes matched canonical output exactly. `proof/portable-path-checks.json`
records five rejected-output cases and unchanged sources after them.

`FILES.txt` explicitly lists the formal package; `manifest.json` pins source,
contract, canonical and proof files; `SHA256SUMS` checks every file except itself.
No caches, recovery extraction helpers, machine-specific paths, old captures or
unavailable runtime-QA claims are included. No artwork change was made.
