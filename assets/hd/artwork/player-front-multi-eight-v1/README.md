# Frozen normal-player front Multi eight-head art

This generated-only package freezes the parent-approved v3 offline art. It does not constitute actual gameplay author acceptance.

Eight standalone semantic SVGs produce straight RGBA PNG and HDR1 resources for player role8 IDs121,122,163,164,201,202,279,280. HDR1 keys are80000+sprite, density8, logical12×14, anchor0,0; proposed slots524–531. Every PNG/RGBA byte matches the approved v3 candidate.

The drawing is a continuous yellow/orange/red luminous heat field in an authored smooth cap/taper silhouette. No gray casing, dark outline, inner highlight boundary, blur/halo, pixel-mask staircase trace, bitmap source input or added animation exists. v3 changes only shading: every alpha byte equals v2. Twins retain a visible central gap at direct native2×/4×; their density8 antialias supports share one very faint sample, never a luminous core.

## Rebuild

With Node and the Sharp version recorded in `proof/renderer-versions.json`, run:

    node rebuild.cjs /absolute/new/output-directory

The output directory must not already exist. The renderer verifies frozen input hashes, builds solely from standalone SVGs, and checks every generated output against `inventory.json`. It neither locates nor reads original game data, masks or screenshots. `author-geometry.cjs` records the semantic construction and can reproduce all SVG sources; its additional semantic-contract JSON is explanatory, not a raster input.

## Gate and sampling

The offline gate directly sampled authored density8 to native2×/4× without a native1× intermediate. The source-alpha operator matches `render_mirror.c`: round `(destination*(255-alpha)+source*alpha)/255`. SDL2 software-renderer proof checks nearest-center presentation at every target pixel. See `proof/verify-nearest.c` and its log. This is a small standalone sampler test, not a game run.

The exact center sample is `floor((destination_coordinate+0.5)*8/display_density)`. No smoothing or intermediate source-scale enlargement is used. The package includes no original reference images or original pixel-index arrays.

## Integration boundaries

Require normal-only admission for all eight IDs; Christmas differs for six members. Existing58/59 remain byte-exact. Existing enemy-only163/164 are separate and untouched. Original indexed shadows remain unchanged. This package does not claim complete rear Multi, linked, charge, Hyper Pulse, option, shop-preview, Windows, acquisition, collision or live-render coverage. Those require their own scoped tests. No additional art revision is authorized by this freeze.
