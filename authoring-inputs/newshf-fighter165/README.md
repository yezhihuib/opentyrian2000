# NEWSHF fighter165 V2: simplified metal surfaces

This visual revision responds to feedback that the small aircraft had a grid-like appearance. The built-in image editor independently redrew all three V1 poses, preserving their identity, nose-down orientation, opposite banking, twin upper prongs, red insets and dark cockpit. Dense rectangular surface divisions were replaced with broad continuous bronze/gold planes and restrained highlights. This is a generated surface redraw, not a blur applied to V1. Only a few main structural joins remain. The prompt asks for roughly 80% fewer small seams; this is an artistic instruction, not a measured percentage claim.

All three final masters are 192×224, constrained to the original 24×28 masks. Every original-zero cell is entirely RGBA0. Pixels whose alpha is zero also have RGB zero. Each master is one connected alpha component. Empty original occupied cells: base49 3/274, base47 25/265, base51 32/263. Runtime must restore exact underlay for transparent and partially transparent cells; no black or original body residue is acceptable.

Generated interior alpha is predominantly 253 and is preserved, not normalized. At alpha 253, background contribution is 2/255 (about 0.7843%). Edge pixels have proportionately larger background influence.

`rebuild.py` uses Python 3, Pillow, NumPy and SciPy. It crops each generated alpha bounding box, globally registers it into the original support bounding box with Lanczos sampling, applies a conservative inward-softened native mask, removes disconnected alpha dust and recreates masters, previews and statistics. It does not paint or blur the surface art. Raw PNGs and native masks are included, so rebuilding needs no external original game data. A second rebuild produced identical master bytes.

`comparison-4x.png` and `comparison-8x.png` show V1 and V2 at the same physical size. `straight-comparison-*` retain the early straight-pose review comparison. V1 is preserved unchanged outside this package. This art-only WIP does not establish runtime qualification, Windows acceptance or public approval. V2 must be tested anew against its exact bytes.
