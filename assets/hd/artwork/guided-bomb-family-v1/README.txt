Guided-bomb family: four finite HD player-projectile candidates.

STATUS: Root approved all four designs offline on2026-10-12 for a bounded runtime trial. Runtime visual acceptance is not claimed. No production repository edits or gameplay runs/captures were made by the artist.

Exactly four spriteSheet8 identities:19,171 physical blue-metal bombs;20,21 warm luminous short-lived collision-child heads also shared with other projectile users. These are four distinct static forms, NOT an animation and NOT directional views. Frame22 belongs to Widget Beam and is deliberately outside this work. No other artwork is replaced.

All four use logical12x14, anchor(0,0), density8, exported96x112 straight RGBA. Runtime headers are HDR1+[80019/80171/80020/80021,8,12,14,0,0]. Each .hda payload exactly matches the corresponding exported PNG RGBA bytes. Original draw remains logicalX+1/logicalY; no frame59 anchor exception applies. Original conditional shadows, gameplay, RNG, motion, damage, collisions and shot tables remain untouched.

Original19 and171 both occupy[1,2,11,12]; selected HD alpha>128 bounds are exactly[8,16,88,96].19 is broad/rounded;171 has narrower sloping shoulders. Both retain the blue-gray metal casing and recessed warm center. Original20 occupies[4,4,9,11],21[4,3,9,12]; selected HD alpha>16 bounds match those bounds at8x. Their original visual center(6.5,7.5) is intentionally different from the full tile center(6,7). Soft shoulders fade slightly beyond the old occupied footprint; no opaque rectangular backgrounds or dark mattes remain. The energy bodies stay distinct compact and elongated warm forms.

Artwork was made with the built-in image_gen tool. Selected generated masters are saved unchanged.19 received a darker-blue material refinement.20/21 received broad-core, true-alpha matte-removal and rounded-original-shape passes. The selected20 is a broad oval;21 has full-height parallel shoulders and rounded caps. Retained prompts describe every pass. Production export only performs whole-object crop, Lanczos resampling and placement. No procedural recoloring, painting, alpha remapping, component warping, fabricated animation, or legacy pixel tracing.

Reproduce with: python export_final.py
Requires Pillow. All transforms and hashes are recorded in candidate-manifest.json and validation-metrics.json. No original game data is needed to regenerate the four runtime files and generated-only review sheets.

Original source PNGs, decoded palette/index evidence, local source comparison sheets and the decoder are local-only review material. They are excluded from both distributable ZIP packages. The source package includes selected generated masters, prompts, exporter, technical contract, manifest, metrics and generated-only review sheets. The runtime package includes four PNGs and four HDR1 resources plus technical metadata and generated-only review sheets.

Offline review is precisely an alpha-over/nearest sample of the8x assets at actual4x(48x56) and2x(24x28), over black, light gray and olive. It is not a screenshot or proof of dynamic rendering. Root offline review is complete; runtime integration should now use the existing legal-loadout fixture, real enemy collisions and missing-art fallback. Broader shared weapon users have not received complete runtime acceptance.

Specific pending runtime visual gate: on actual cloud/terrain backgrounds, the red/orange shoulder of20/21 must read as fading warm light, not a painted red outline or capsule border. Source alpha is genuinely partial; runtime perception is the final gate. No22 change.
