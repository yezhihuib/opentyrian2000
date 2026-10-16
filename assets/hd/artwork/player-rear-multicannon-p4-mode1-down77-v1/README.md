# Rear Multi-Cannon P4 mode1 downward head77

This bounded package supplies only head77 for actual main-gameplay player1,
rear weapon10, power4, mode1, exact record257, on first-level Normal9/Hard15.
The call owns five emissions. The quartet281/282/301/300 uses the unchanged
accepted R2 resources; only77 adds new density4/8 art. Mode2 record268 remains
unchanged. Shared raw source IDs alone do not admit an emission.
See `docs/rear-multicannon-p4-mode1-reuse-v1/VALIDATION.md` for runtime
qualification and limits.

The downward head is the accepted R2 ID1 rotated clockwise90 degrees and
translated by logical(-2,+2) into the same12×14 canvas, anchor(0,0). Pillow's
integer transpose and unmasked paste preserve every supported straight-RGBA
sample, alpha value and full-density brightness contribution exactly. Only
transparent-black samples fall outside the destination. Native nearest sampling
can change subpixel phase; no brightness correction is applied. Density4 and8
are independently derived from their matching accepted sources. There is no
new drawing, generation, filtering, resampling, normalization or blur.

`inputs.json` pins the published R2 input PNG/RGBA and the approved down77
PNG/RGBA outputs, plus deterministic HDR1 hashes and RGBA FNV values. It also
records the SHA256 of the independently reviewed generated-only export from
which only these77 outputs are selected. This new minimal builder and contract
are separately validated; the original preview package is not copied here.
No original data, masks, palettes, extracted sprites or screenshots are used.

With Python3 and Pillow installed, rebuild to two fresh, separate directories:

    python3 build.py --output NEW_ART_DIRECTORY --hda-output NEW_HDA_DIRECTORY

The default read-only input is the sibling
`../player-rear-multicannon-p1-six-v1/output` directory. An explicit `--source`
may point to a relocated copy of those four pinned accepted PNG/RGBA files.
The builder rejects altered sources, outputs that differ from the approved
hashes, covered clipping, and existing output directories. PNG encoding is
RGBA with compress_level9 and optimizeFalse. All output bytes are pinned, so
an encoder that produces different bytes fails rather than silently updating
an approved resource.

HDR1 uses role131, key1310077, density4/8, logical12×14 and anchor(0,0), followed
by the exact approved straight RGBA bytes. The established loader filenames
`rear-multicannon-p1-bank8-77-{4,8}.hda` are retained. `binding.json` pins the
builder, contract and pack copies. `file-manifest.json` covers every package
file except itself. Existing R2, P3 two-lobe and other art stay byte-exact.
