# STORM heading artwork pilot

This bounded pilot redraws only the five-row STORM heading within option icon37.
It leaves the lower green streak, its two-row spacer, and the ammo gauge to the
original renderer. It is a private candidate, not a published or runtime-approved
replacement.

## Authoring and provenance

The label extends the repository's independently authored geometric HUD lettering
at the existing 0.72-logical-unit stem width. S, O, R, and M use the same path
vocabulary as MODE/SHIELD/ARMOR; T uses the FRONT label's path vocabulary. The final
M occupies its five-unit slot. No installed font is required. The recipe computes
segment distances analytically and integrates coverage at density4 and density8.
It does not upscale the original bitmap or trace its pixel mask.

Green palette roles197–201 retain the established green ramp. The runtime must
resolve these roles through its active palette. No original palette RGB array,
decoded game mask, sprite payload, screenshot, or lower-motif reconstruction is
included here. A small flat-green geometry PNG/SVG is supplied only for structural
review; palette-index and coverage planes are authoritative.

## Reproduce

Use Python3, NumPy2.3.5, Pillow12.3.0, and zlib1.3.2:

    python build_assets.py --output /fresh/output/directory

Only adjacent geometry.json is read. Game files and reference captures are not
required. Rebuild outputs include the contract and hashes. Existing outputs with
different bytes are refused.

## Integration contract

- Original icon: bank5, zero-based index37, 25×13 logical units.
- Owned heading: local half-open [0,0,25,5].
- Original rows5–12 remain untouched. The ammo gauge begins at row13.
- Density4 planes: 100×20, 2,000 bytes each.
- Density8 planes: 200×40, 8,000 bytes each.
- Each plane is uint8, row-major, no stride. Index is an absolute palette role;
  coverage is vector-ink alpha0–255. Index0 occurs exactly where coverage is0.
- Replace the whole top25×5 with palette0 background plus authored ink. Do not
  alpha-blend the new label on top of the old letter pixels.
- Composite each RGB channel with integer rounding:
  (palette[index]×coverage + palette[0]×(255−coverage) +127) //255.
- Offline native2× art previews average composited density4 pixels. Production
  preserves the existing SDL nearest sampler of selected density4/8. Density8 is
  independently integrated vector coverage, not replicated density4 pixels.
- The runtime resource/parser and source fingerprint guard belong to the
  integrator. Artwork files alone do not prove the runtime is safe.

See generated/contract.json for machine-readable details and artifact hashes.
The only directory suitable for later public review is this public-artwork
directory. Sibling private previews and comparisons must not be published.

Production sampling note: any averaging mentioned above describes only the offline art preview. The game keeps its existing SDL nearest sampler for selected density4/8 artwork; actual native readback is the acceptance authority.
