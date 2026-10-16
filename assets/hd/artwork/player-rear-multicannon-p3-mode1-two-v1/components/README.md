# P3 mode1 two-lobe component-reuse proposal

Preview-only generated artwork. No production binding, HDA resource, game code,
runtime acceptance, or publication is included.

## Exact construction

Full logical canvas is 12×14; anchor is (0,0). The accepted R2 component source
identities 1 and39 are independently authored. They are never replaced with a
mirror of the opposite-direction component.

- Proposal2: component1 translated (0,−2), plus whole-canvas flipY(component1)
  translated (0,+2).
- Proposal40: whole-canvas flipY(component39) translated (0,−4), plus component39
  translated (0,+4).

At density d, flipY maps row y to 14d−1−y, then translation changes y by d×dy.
Every occupied RGBA sample is copied unchanged. The supports are disjoint, so
assembly performs no overlapping blend. No supported sample is clipped.

Both proposals retain two distinct lobes and an exactly transparent central
strip y∈[6,8), meaning logical rows6 and7. Bounds are [1,2,12,12) for2 and
[0,2,11,12) for40. No halo, blur, recoloring, edge sharpening, brightness
normalization, recentering, or redraw is applied.

Each lobe has exactly the accepted component's full-density alpha values,
straight RGB values, alpha-weighted RGB totals and peak brightness. Two-lobe
totals are exactly twice the component. This is not a claim of equality to the
original indexed art's brightness. Nearest-center native sampling after a
reflection can select a different subpixel phase; display-level lobe sums may
differ slightly without changing any source byte.

## Rebuild

Requirements: Python3 standard library and the pinned accepted generated R2
artwork package. No original game data, original masks, palettes, screenshots,
or private review material is read by the builder.

From this directory:

    python3 build_composites.py /path/to/player-rear-multicannon-p1-six-v1 /path/to/new-output

The output directory must not exist. `accepted-component-pins.json` verifies
the accepted inputs before writing. `output/transform-contract.json` records
the exact transformations, source pins, per-lobe metrics, and output SHA256
and FNV1a64 hashes. The four proposal pairs and eight layer pairs use straight
row-major RGBA with zeros under alpha0.

The source package is the accepted R2 art in the published baseline tree
f17193939bc71d99f80f66af55186a9427d51ec1, commit
8c996513ef83a53cd0384046a32e5701307a3d11. Pinned RGBA is authoritative; the
accepted source SVGs and their metadata are pinned for provenance. Density4
and8 each use their independently rasterized accepted component, never a
downsample of the other density.

PNG generation is deterministic RGBA8 with filter0 rows and explicitly
constructed stored DEFLATE blocks. It does not depend on an image renderer,
color management, or a compression-version heuristic. PNG decoding has been
checked against each raw RGBA payload. The individual full-canvas lobe files
are retained for independent inverse-transform checks.

All original references and comparisons remain outside this generated-only
directory. Keep that separation when archiving or exporting the proposal.
