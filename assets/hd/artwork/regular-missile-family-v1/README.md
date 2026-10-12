# Regular Missile Launcher HD pilot v1

Frozen after root art review on 2026-10-12. Approved for a bounded runtime trial only. This art task made no repository changes and ran no game or captures.

## Exact scope

Three static physical-missile upgrade designs for regular front weapon port 17, bank 8 IDs 31, 32 and 33. These are not animation phases. ID 31 is narrow gunmetal; ID 32 is wider silver/white with broader fins; ID 33 is copper/red-brown.

All exports are true-transparent RGBA PNG, 96×112 for a 12×14 logical cell, density 8, anchor (0,0). Occupied half-open bounds match the original cells times eight:

- 31: (24,8)–(80,112), logical horizontal axis 6.5
- 32: (16,0)–(88,112), logical horizontal axis 6.5
- 33: (8,0)–(80,112), logical horizontal axis 5.5

ID 33 retains its original one-logical-pixel left shift. The actual runtime shot placement must stay unchanged.

Accepted shared collision sprites 20/21, smoke 135–141 and warm effects 122–133 are outside the edits. ID 22 is not reachable in the regular source closure. ID 30 remains latent/unmapped. Shared special 19 and latent records 120/1120 are source-only caveats, with no full-coverage claim.

## Artwork provenance and processing

All three selected source masters were generated with the built-in imagegen tool from inspected original references. Full prompts and original generated RGBA sources are retained. Only whole-object rectangle crop, whole-image Lanczos resampling and placement on a transparent canvas were applied. There was no painting, recoloring, silhouette reconstruction, alpha repaint, sharpen pass or part-specific deformation.

The generated sources contain scattered remote alpha=1 speckles. The recorded crops preserve the visible object and all source alpha >=2, with a two-source-pixel margin; only remote alpha=1 speckles fall outside. Alpha within each crop is preserved through resampling. Generated proportions were fit nonuniformly to the original occupied-cell bounds. Every crop and placement is recorded in candidate-manifest.json.

## Contents and reproduction

- frames/: three frozen 96×112 RGBA PNGs
- runtime/: three HDR1 raw RGBA HDA files; exact PNG pixel bytes, 43,036 bytes each
- sources/: three selected unchanged generated masters and complete generation prompts
- candidate-manifest.json: bindings, registration, transforms, hashes and limits
- generation-provenance.json: generation records and source hashes
- validation.json / reproduction-verification.json: offline checks
- review/hd-pixels-1to1-dark-light.png: generated-only HD pixel review

Run `bash export_pilot.sh` to reproduce the frozen PNGs with ImageMagick 7 and `python encode_runtime.py` to reproduce HDA payloads with Pillow. Verify against CHECKSUMS.sha256. No engine source or manifest is modified by these scripts.

The formal source ZIP deliberately excludes original pixel references, source-containing comparison contacts, and any unselected masters. Original comparison contacts remain local for review only. The native1x/2x/4x contacts are offline source-over composites, not runtime captures.

Runtime acceptance still needs actual renderer review on moving cloud/terrain at native Integer2x and targeted4x, all three static identities, registration, alpha edges and shared-effect distinction. Do not claim integrated or published status from this pilot.
