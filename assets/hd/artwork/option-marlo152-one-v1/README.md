# Satellite Marlo: one independently generated normal body

This is one new orange/red energy-orb image with a lower hot yellow core, not an enlarged or retouched original sprite. The fresh generated master is stored under `sources/`; it does not reuse the previously lost unpublished candidate. No original game data or original-sprite screenshots are included.

The standard import is fixed in `contract.json`: crop[148,132,1130,1114], Pillow12.3.0 LANCZOS resize64×64, paste16,16 on transparent96×112. There is no painting, recoloring, alpha threshold or shape edit. Run `python rebuild.py --output /new/external/output` to reproduce exact PNG/RGBA/HDA hashes.

The resource is density8 on the original full12×14 logical tile, anchor0,0, independent role126/index152/slot536. The original support bbox[2,2,10,10] maps to physical[16,16,80,80], center48,48 (logical6,6), with the original larger bottom margin. This is not the Talon role9 anchor5,7.

The native2x offline preview was accepted before integration: core and width remain legible. The new alpha-weighted area38.397 native pixels,73.84% of original52, is an explicitly reviewed soft-edge/irregular-outline tradeoff; alpha was not thickened. This artwork freeze precedes actual-engine validation. Completed checks and bounded coverage must be documented separately before publication.

Only normal option30/style4/charge0/body152 is in scope. All source identity checks must precede cold and warm resource lookup, including same-address bank reload. Christmas bank9/152 is empty and must retain its original invisible indexed fallback. Original indexed drawing executes once at the original position. Orbit/gameplay, Talon/Mint, other sidekicks, projectile67, HUD and shop previews remain separate.
