# NEWSHF record166 three-pose authoring draft

Straight base87, opposite banks base85 and base89. Each PNG is 192×224 for an unchanged 24×28 native quartet. The smooth tan/bronze-gold single-stalk design is distinct from record165’s broad twin-prong craft. Dense rectangular panel grids were intentionally avoided.

Built-in image_gen produced each pose independently. Raw files, prompts and deterministic registration recipe are retained. Run `python3 rebuild.py` with Pillow, NumPy and SciPy to regenerate masters, previews and statistics. No original proprietary game bank is included; the supplied native masks were derived from the separately verified original source.

Native source-zero cells must remain RGBA zero. Originally occupied cells can become empty or partially transparent; the runtime must restore the verified underlay instead of painting black or retaining the native body. Visible interior alpha is generally253, contributing about0.7843% underlay. See stats.json for per-pose coverage and alpha data.

This draft is artwork only, not a runtime qualification or a public release. Opposite banks are separate generated poses, not flipped/skewed copies. Native source positions, collision and game logic are unchanged.
