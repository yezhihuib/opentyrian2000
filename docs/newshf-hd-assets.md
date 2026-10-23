# NEWSHF finite HD resource build

> Latest selected artwork policy: [168 V4 finite soft-alpha revision](newshf168-v4-soft-alpha/README.md). The previous binary-alpha revision and its receipts remain historical, not overwritten.

> Current art/pose revision: [corrected physical selection](newshf-fine-v2-corrected-poses/README.md). Earlier unchanged-art/pose claims below describe historical integration only; the first-two167/168 artwork assignments were subsequently found mislabeled and corrected.

The independent compositor consumes exactly nine role IDs **2100000–2100008**,
in record/pose order 163:125/123/127, 167:3/1/5, 168:55/17/93. These IDs are
material roles, not generic bank/base eligibility. The existing accepted
120-resource global registry is unchanged.

`python scripts/build_newshf_hd.py build` validates the Phase A source contract
and writes nine deterministic HDR1 files, `assets/hd/newshf-v1/manifest.json`,
and `src/newshf_hd_assets.h`. `check` performs the same derivation without writes.
Every HDA is its unique 28-byte header followed by the selected PNG's unchanged
192×224 RGBA bytes: density 8, logical 24×28, anchor (6,7). No original game
pixels or binaries are generated or packaged.

The additive package extension contains exactly nine
`assets/global/newshf/newshf-role<ID>-8.hda` destinations. The root supplied to
the renderer is the package's `assets/global` directory. Header payload FNV pins
protect runtime content; the build manifest binds complete HDA SHA-256 and PNG
revision hashes. These are integrity checks, not cryptographic authentication.

Intentional art edits update the existing Phase A manifest/provenance art pins
and source report, then regenerate these consumers. Immutable identity,
geometry, records and source bank hashes do not change. Each pose has one source,
shared across levels. The selected pixels were not edited in this integration.

The exact-nine package extension is separate from historical current-art
replacement maps. Unknown historical consumers remain rejected. Legacy authoring
workflows retain these finite inputs in their isolated build roots and plans.
Resource compilation and packaging alone do not prove compositor/game acceptance;
see the separate native validation receipt for that scope.
