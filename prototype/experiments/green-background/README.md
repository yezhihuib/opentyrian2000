Historical experiment; superseded by the selected immutable pre-draw snapshot implementation documented in docs/GREEN_RENDER_VALIDATION.md. These patches are retained for audit and must not be applied to current source.

# Unapplied green-background interpolation WIP

Only a candidate and private Windows build exist. No runtime A/B, visual acceptance, stability/performance or adoption result. Production remains v2art with original point/blend. The stop request ended work before any candidate run.

The production patch targets renderer A identified in status.json. It samples four original-background pixel centers for the value-average destination term only under mapped green78–84HD smoke when the current HDowner is0. Neighbor HD/outside taps use current value. Existing hue ratios/authored alpha, existing HD destinations, nonblend, missing assets and classic paths stay unchanged. Semantics differ inside smoke: low-resolution scenery brightness gets a continuous transition; partially transparent smoke still reveals the original sharp background. It is not a whole-screen blur or ordinary alpha replacement.

private-renderer-and-halo.patch targets the archived green fixture renderer, not production. It adds only this candidate, a point-baseline environment flag and a read-only1logical-pixel halo observer. Candidate EXE/build products and local transfer credentials are not committed. Review and run a limited A/B before applying either patch.
