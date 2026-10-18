# Rear Multi-Cannon P10 mode1: four-lobe horizontal pair

Resources 203/222 are newly authored smooth cubic vector forms, frozen after
review of both directions at native 1x/2x/4x sizes on dark, neutral, and bright
backgrounds. They retain the accepted P1 yellow-core/orange/red heat field and
inward 0.30-logical-pixel soft-coverage treatment. The approved bright-background
orange boundary is distinct; actual compositor review must separately check
edge behavior without blurring the lobes or washing out their palette.

The new compact forms are 11x3 for inner lobes and 9x3 for outer lobes. Lower
lobes are full-canvas vertical reflections; 222 is an exact byte reflection
of 203 at each independently rendered density 4/8. Logical canvas 12x14,
anchor (0,0), and occupied bounds [0,1,12,13] remain fixed. No supported lobe
tail is clipped. No original raster boundary is traced or enlarged.

An independent, new local indexed-source check tested 29 accepted original
identities with eight axial rotations/reflections, integer translations, and
whole-canvas clipping. No exact retained component larger than one pixel
matched 203; all compatible pieces covered only 6 of 104 original cells.
This justified new semantic geometry rather than claiming exact component
reuse. Original data, decoded rasters, and comparison captures are excluded.

Only public generated-art semantic constants are required to rebuild.
`inputs.json` pins their original repository blob and SHA256. The reviewed
generator is retained byte-exact. `freeze.json` binds the approved candidate
contract and external local verification digest. The historical candidate
contract retains its pre-approval status verbatim; the freeze record supersedes
that status for art freezing only. This does not grant runtime or publication
approval.

Run `node rebuild.cjs /absolute/fresh/output` using the exact Node/Sharp stack
recorded in `output/candidate-contract.json`. The supported entrypoint refuses
an existing output directory, checks public inputs and renderer versions,
rebuilds all eleven reviewed files byte-exact, and packs four role 131 HDR1
resources. It never reads original game data or captures. Direct standalone
222 SVG rasterization has small boundary rounding differences,documented in
the candidate contract; the canonical payload uses exact byte reflection.

Run `python3 verify.py` from any working directory for frozen package checks,
four exact HDR1 bodies, identical resources in both default packs, source PNG
bindings, and the exact inverse of catalog additions. `--package-only` checks
a relocated package without a repository. Existing family descriptors and
accepted art remain unchanged; all other packs exclude the new resources.

The runtime scope is authenticated normal physical record 263 only: player 1,
rear port 10, bay 1, power index 9, mode index 0, on the already bounded first-level
Normal 9 / Hard 15 route. Its six phases are 277/278/297/296/203/222. The first four
reuse accepted bytes unchanged. Physical alias 1263, opposite-mode 274, other
powers, alternate banks, and generic/shared/linked/shadow consumers remain
excluded. No budget, logical coordinate, collision, or gameplay change is part
of this artwork package. Actual compositor/gameplay, night-palette, Windows,
GPU, and full-level acceptance are separate.
