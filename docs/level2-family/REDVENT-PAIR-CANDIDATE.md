# Private static red-vent pair (339 / 348)

This is newly recreated artwork, not recovered November 7 material. It rebuilds
two small, opaque industrial ground tiles: the three horizontal recesses in 339
and the single vertical recess in 348. Previously rejected high-frequency rock
walls and the paused four-tile pit group are not changed.

**Stage: opt-in integration candidate, not gameplay-qualified.** The private
art has a separately disabled loader in the optional level-2 build. The public
52-asset manifest and default 24-terrain selection remain unchanged.
No gameplay, entity occlusion, animation, map-neighbor closure, frame rate or
Windows display acceptance is claimed. Only use the explicit private-candidate option for subsequent validation; do not
promote it to default coverage before visible scene and occlusion checks.

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

## Map identity and optional integration

The targeted map is **episode 1, physical level 2, ASTEROID2**, map character D,
shape set Z. It is a branch after TYRIAN, not the mandatory second campaign stage.
Its layer 1 has 133 stored occurrences of 339 (loader slot 37), and 23 of 348
(slot 45); neither is used on layer 2/3. There are 44/22 distinct eight-neighbor
patterns respectively. Eight sampled 4x neighborhoods had no obvious new edge
displacement; this is not exhaustive neighbor or runtime acceptance. Both IDs
are reused in other maps, so the existing episode/physical-level family guard
remains mandatory. No target-specific tile-byte animation or event-64 filter
switch was found in this map; unsupported global contexts retain existing guards.

The optional family build accepts `--redvent-pair` only together with `--hd`:

```sh
python3 scripts/launch_level2_family.py --data /path/to/game-data --hd \
  --redvent-pair /path/to/private-candidate --check-only
```

This read-only command verifies both exact HDA hashes in addition to the unchanged
52 public assets. Omit the option to leave the pair off, even if inherited
environment variables request it. A later `--launch` is a separate gameplay step.
The source-only `experimental/late-level` package is not changed by this update.

The loader requires exact `BUILDING313_REDVENT_PAIR_ENABLE=1`, the parent family
and ground prerequisites, matching native source/payload identities, exact
headers/file length and full opacity. It keeps its own two-file cache. Toggle or
directory changes during a frame invalidate the shared terrain transaction and
pure support snapshots. Normal native stores, map/event data and draw order are
unchanged. Optional cells use the existing ground ownership/retirement pathway,
which remains unverified in real red-vent gameplay. Bad or missing enabled assets
reject the shared frame instead of partially presenting the pair.

Loader tests cover default-off, compilation-disabled behavior, prerequisites,
malformed/missing data, explicit launcher selection, callback and snapshot guards.
A private isolated C run also loads both real assets against real source pins,
then verifies mid-frame directory/toggle rejection and cache release. These are
not a rendered frame or input/save/performance test.
