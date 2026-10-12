# Reusable terrain repair method

The rejected reconstruction inherited two kinds of low-resolution artifacts: pixel-stepped silhouette masks and stone/highlight cuts at independently chosen crop boundaries. A high-resolution texture alone did not repair either.

1. Use original pixels to identify palette, motif locations, approximate scale, tile topology and transparency. Do not treat staircase pixels or square highlight clusters as literal stone geometry.
2. Describe the intended forms first: broad gray/warm-brown rock plates, natural joints, and recessed dark-red impact pits. Check that the drawing still has the original stone scale at native 2×.
3. Author a continuous material and explicitly repaint its wrapped opposite-edge joins. Use that common interface for interchangeable fill variants; preserve their distinct centers.
4. Fit side/rim transitions in assembled family context. Keep original world bounds and anchors, but allow small natural contour corrections rather than forcing obsolete opaque stairs.
5. Inspect both actual repeated rows and alternate neighbor classes. A single handsome assembled master does not prove its independently reusable crops will join.
6. Validate nearest-sampled 2×/4× and actual scrolling, including crater reveal and old/new neighbor reuse. Numeric edge equality is a diagnostic, not a reason to blur the whole family.

Current scope: eighteen gray terrain IDs and the necessary purple/turret stone backings. Purple geometry, lens, damage details and turret body/core geometry remain unchanged; terrain150 and entity169 are unchanged guards. The six-rim checkpoint is retained. No publication until combined family and actual-frame review.
