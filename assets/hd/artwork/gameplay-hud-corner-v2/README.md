# Corner V2: continuity-preserving trial package

Root reviewed the native2×/4× wider-context proof and authorized a reversible
actual trial. User feedback and runtime review remain pending. V1 is rejected
and must not be adopted. This package changes no runtime or repository files.

## Exact art and ownership

The opaque84×64 RGBA tile occupies logical `[248,184,269,200)` (336 cells).
It preserves all150 previously owned V5 frame cells byte-exact and restores10
verified source-black seam cells exactly. Only176 interior cells receive new
rendered metal. The full top five rows and right housing continuation retain
their prior profiles; the first authored grille rib continues the original
two-cell cadence. The diagonal brace keeps the original narrow topology.

The ownership exception remains336 cells, including150 existing and186 new
cells. Forty-six of the186 had original index0. The whole-frame union is6853.
No playfield, labels, lamps, meter or message-eraser expansion is included.

Before any corner composition, all336 original indexed source cells must still
equal captured PIC3. A mismatch from long message text or persistent tails
suppresses the entire corner and restores even its150 formerly HD frame cells.
Do not erase those original tails. Permit source-zero only within the validated
rectangle. Retain original PIC3/mode/surface lease, lifecycle and fade gates.

## Reproduce

`python reproduce.py --baseline-hda PATH --output NEW_DIRECTORY`

PATH must be the immutable generated V5 HUD1 resource, SHA256
`4ff6cd95d4c3ec5b7e4825e38a5242fc96c1cd305987a873bea4a55fa5a04482`.
The baseline master is deliberately not duplicated. The imagegen master is
resized to120×72 using Lanczos, cropped at `[16,8,100,72)`, then composited with
the150 exact generated V5 cells and10 explicitly black seam cells. Native2×
uses nearest sampling from canonical4×; density8 repeats each texel2×.

The script reconstructs the existing HUD1 format with the6853 union. It adds
no extra resource header or runtime overlay layer. `rebuilt-a` and `rebuilt-b`
retain two matching generated outputs and reports. `verification.json` also
independently checks every old6667 owned cell and the reviewed tile byte-exact.

No original PIC/glyph/sprite/palette/capture pixel payloads are bundled. Source
compatibility metadata is retained separately from generated artwork. Offline
proof typography is another candidate and is not part of this patch.
