# Private static red-vent pair (339 / 348)

This is newly recreated artwork, not recovered November 7 material. It rebuilds
two small, opaque industrial ground tiles: the three horizontal recesses in 339
and the single vertical recess in 348. Previously rejected high-frequency rock
walls and the paused four-tile pit group are not changed.

**Stage: static art candidate only.** Neither runtime source nor the public
52-asset manifest is changed. The public integrated terrain count stays at 24.
No gameplay, entity occlusion, animation, map-neighbor closure, frame rate or
Windows display acceptance is claimed. The files must not be put into an enabled
runtime pack until their identity, loader, neighbors and visible scene are checked.

## Private inputs and deterministic registration

Two image-generated masters were made with the corresponding original tile as
geometry reference and the accepted 340 / newly generated 339 as material
references. The prompts preserve top-down projection, subdued maroon glow and
charcoal masonry. The masters and derived images stay in a private checkpoint;
this source commit does not publish those images or original game data.

```sh
python3 scripts/build_redvent_pair.py \
  --data /path/to/legal-original-data \
  --raw-art /path/to/private-masters \
  --output /path/to/fresh-external-output
```

Requires Pillow 13.0.0 and Python 3.9+. Inputs are exact-hash pinned in the script:
`shapesz.dat`, `palette.dat`, `tile339-raw-v1.png`, `tile348-raw-v2.png`.
It does not download anything. Output must be fresh, outside the repository and
input directories. Inputs are validated before an output directory is created.

Registration downsamples the master to 192 x 224, clamps per-channel global
brightness correction to 0.75–1.25, and preserves the exact one-native-pixel
perimeter. The next two logical pixels feather inward to the generated artwork.
The 6,400 perimeter HD pixels are explicitly original-derived RGB, not newly
created art. All 43,008 pixels remain fully opaque. Each HDA is 172,060 bytes,
with an HDR1 / 8x / 24x28 / zero-offset header and RGBA payload.

A static 2x/4x contact review checks the three-recess versus single-recess layout
and overall silhouette. A second revision of 348 restores its small upper-left yellow-orange hotspot
without globally brightening the recess. Overall brightness still needs scene review.
Exact perimeter preservation is a local edge constraint, not proof of seamless
joining to every neighboring HD asset.

## Checks and promotion boundary

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_redvent_pair_authoring.py -v
```

Unit checks cover malformed inputs, hash/size and symlink rejection, no-overwrite,
no partial output on bad inputs, full opacity and the exact border count. A second
independent output directory can verify byte-for-byte reproduction against the
private checkpoint's hashes. Neither check runs the game or promotes the art.
