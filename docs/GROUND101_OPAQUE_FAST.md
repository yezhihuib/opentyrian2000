# Exact fully replaced material fast path

This follow-up changes no artwork, bundle, material phase, gameplay or selected-pack
fallback. After every existing eligibility, pointer, bounds and alpha check, a
pixel with primary weight255 and both secondary weights0 copies the atlas RGB
directly. The selected-pack alpha is retained. Fractional weights and the ordered
119/120 footer stages continue through the original integer compositor.

The unchanged scalar implementation remains the reference. Tests compare both
return values and all four output bytes, including independent nonzero-alpha
cases that the earlier weight-coupled loop did not exercise. Formal ASan/UBSan
checks cover49,152,000 scalar/fast samples,16,777,216 independent alpha/color cases,
1,638,400 secondary-weight cases, clipping/invalid guards and35 split-loader cases.
The earlier complete61-recipe plus111-guard/footer reconstruction also passes.

The source-pixel eligibility census is973,931 of2,623,488 pixels (37.1235%); this
is neither draw-weighted frequency nor an estimate of speedup. The full terrain101
source qualifies, while decorated boundaries often keep fractional weights.

Actual output and paired diagnostic timings are recorded in
`GROUND101_OPAQUE_FAST_VALIDATION.json`. Timings include loading, auditing and
FIFO logging on the cloud software renderer. They are not a gameplay FPS result
or a Windows guarantee. Do not subtract the improvement from the earlier33%
feature-on overhead: that earlier comparison used a different bounded window.
No visual recapture is necessary when the exact reviewed outputs are retained.

With the shipped two-part loader, all three paired road500–559 comparisons
improved. Median elapsed fell from9.093118s to8.091775s (11.012%); median child
CPU fell from9.086874s to8.090906s (10.961%). All348 reviewed-window audits and
the360 additional timing-frame audits remained exact.
