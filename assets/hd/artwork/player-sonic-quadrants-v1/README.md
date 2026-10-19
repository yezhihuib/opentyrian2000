# Sonic Wave rear quadrants

Four smooth green-energy heads: normal bank8 IDs 105, 106, 124, 125. The two saved
generated masters are independent; only the exact horizontal counterparts are
derived. These are simultaneous directional pieces, not animation frames or the
joined 143/144 wave seam.

The frozen contract records the exact image-generation prompts, conservative
observed time bounds, source fingerprints, proportional registration, Pillow
version and all output hashes. The exact model ID was not supplied. Original game
rasters, indices and masks are not distributed here and are never reconstruction
inputs. No nearest-upscaled original stairs, repainting, recoloring, alpha
thresholding, source-mask clipping or non-proportional stretching is used.

Run from the repository root:

```sh
python3 prototype/build-sonic-quadrant-art.py
python3 tests/test_sonic_quadrant_art.py
python3 tests/run_sonic_quadrant_tests.py --data ORIGINAL_DATA_DIR \
  --out NEW_EXTERNAL_RESULTS --sanitize --mutants
```

`rebuild.py --output NEW_DIRECTORY` reconstructs exact PNG/RGBA/HDR1 outputs from
the saved generated sources. It refuses existing and symlinked output paths.
`build-sonic-quadrant-art.py` verifies this finite family, both default-pack
entries and the exact inverse of the additive manifest change. It needs no Git
history or unrelated original game data.

Registration preserves 12x14 logical tiles, density 8 and anchor 0. 105/106 retain
two transparent top rows; 124/125 retain three transparent bottom rows. All prior
17 Sonic resource entries remain unchanged. The four frozen head alphas also
supply guarded smooth shadows, with original indexed writes and classic fallback
in excluded contexts. See [technical and controlled-scene validation](../../../../docs/sonic-quadrants.md).
