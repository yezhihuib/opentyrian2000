# Forest13 continuous canopy, v1

Selected offline forest family: 211/212/213/215/221/222/223/224/225/231/232/233/234. One opaque 768×896 canopy field repeats every96×112 logical pixels. Thirteen opaque192×224 bases retain fixed geometry, shaded front wood, roots and local grass; thirteen L8 weights select canopy only. All resources use24×28 logical bounds, density8 and anchor0,0.

## Rebuild

Run `python rebuild.py --output-dir /new/external/output`. Requires Python3, Pillow and a C++17 compiler. The destination must not already exist. Source PNGs are authoritative registered generated art and authored masks; no original game data is needed. The tool verifies every source, reproduces27 selected decoded image outputs and13 exact HDA byte streams, and writes a receipt. PNG file encodings may vary; decoded pixels and HDA bytes must not.

The imagegen masters and prompts are recorded in contracts/provenance.json. Selected registration inputs are bundled. Original game extracts, reference comparison images, captures and raw map pixels are excluded.

## Runtime contract

Use the existing saved Layer1 world transform and positive modulo. RGB is `(base*(255-w)+atlas*w+127)//255`; alpha is255. No per-ID phase offset, RNG, map change, extra actor offset, or per-frame material allocation. Every fully eligible connector uses consecutive atlas texels. Zero-weight pixels stay byte-exact. The accepted69/66 files are unchanged.

A versioned engineering-owned marker couples default forest13: if any required base/mask/bundle is invalid, all13 use original indexed forest. A custom selected pack without the marker retains its selected artwork. Lower-ground/cap materials are independent.

## Geometry and evidence

The outer-frame authoring primitive has source-valid pairs and2×2 vertices, but is not a literal whole3×3 map occurrence. 215's north connector is source-correct rather than copied from its exceptional exposed-top occurrence. 221 uses consistent vertical side connectors. Narrow front connectors support232/234 reuse; corner endcaps retain diagonal envelopes. The narrow ground notch225/224 over233/231 remains open. The small2×2 grove has a shallower visible wood band than the original; it remains readable in the selected offline review.

Root accepted native2× first17, small2×2 and inward-corner contexts. The static audit checks all208 tile phases and1,040 original pair/phase cases for positive-modulo registration, alpha, protected pixels and exact full-weight sampling. These checks do not claim that every phase has received a separate human visual review.

Actual runtime acceptance is pending. Natural full-scene visibility is heavily occluded by original Layer2/Layer3 and actors. A separate explicitly layer-isolated authoring view and the normal full-scene composition/state proof are required. No natural unobscured gameplay claim is made.
