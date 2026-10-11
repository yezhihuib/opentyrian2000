# Nine-tile brown plateau artwork

Generated shapesz layer1 IDs99,100,106,107,109,110,118,119,120. Each is24×28 logical,8×192×224 RGBA, anchor0,0, fully opaque. Only the first522-tick brown plateau family is covered; this is not a whole-level terrain replacement.

Two saved imagegen sources and prompts define the artwork. Extraction registers actual plateau and diagonal occurrences. GEGL makes109 periodic; the edge-registration helper reconciles22 internal edge types and nine connectors to the unchanged accepted HD101. The107 planar connectors use periodic109 texture, avoiding a false fence-like stripe. No original game pixels, maps or legal data files are included.

Run `python prototype/build-ground-art.py --output NEW_EXTERNAL_DIRECTORY`. Requires ImageMagick7, C++17, Python3/Pillow and GEGL0.4 introspection for /usr/bin/python3. The wrapper supplies the current accepted pack; the frozen101 helper verifies its exact SHA256. Fresh output must match all nine HDA and decodedRGBA bytes. PNG metadata may vary; committed PNG file hashes are verified separately.

Existing dark101 ground, sandy path, terrain props and cloud-v2 are unchanged. Later IDs96/97/98/108 remain out-of-sample adjacency risks. The original-to-HD style change at120→36 remains visible. All new tiles are opaque; these are not alpha holes. Original generic shadows are retained after a bounded dark-floor audit: a tiny single ship-shadow sample on118 is darker than original, without repeated stacking. See docs/GROUND_NINE_VALIDATION.md for exact coverage and limitations.
