# Mint-O-Ship body: three frozen generated resources

The three generated masters in `sources/` are registered using only each frozen
crop, a Lanczos resample to80×104 and an RGBA paste at16,0 onto96×112. The complete
12×14 logical tile uses density8 and anchor0,0. No extracted game pixels, source
masks, recoloring, alpha threshold, repainting or fabricated animation is used.

Resource112 is the dark phase,131 the middle and150 the bright phase. The engine
retains the original sixteen steps112×4→131×4→150×4→131×4 and its pre-draw increment.
This package changes no timer, movement, firing, projectile, RNG or source draw.

`contract.json` pins the generated masters, exact PNG/RGBA/HDA identities and
registration. `rebuild.py --output NEW_DIRECTORY` reconstructs all three byte
exactly with Pillow12.3.0. `prototype/build-mint-body-art.py` also verifies both
default pack extensions and preservation of every prior physical pack file.

Reviewed artwork tradeoffs remain explicit: the dark core is dimmer than the
original112; independently generated shells are not pixel-identical. At native2x,
the dark contour differs by two alpha128 edge pixels from the others; the largest
measured highlight centroid difference is about0.30 logical pixels. No corrective
translation, thresholding or color adjustment has been applied.

The contract records the original offline freeze. Subsequent actual-game review
accepted all three phases at native2x in Normal and Hard, including stationary
non-invulnerable overlap and mixed NIGHT shading. See the batch verification
summary for the bounded technical evidence. This does not establish full-level,
fully-dark-body, Windows, GPU or performance coverage.
