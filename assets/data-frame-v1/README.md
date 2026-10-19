# Optional Data static frame

This directory holds the independent DFM1 resource for Data list/reader screens
and its reproducible, bounded source. All 18 portraits remain native.

Rebuild with Python and Pillow 12.3.0:

    python3 scripts/export_data_frame.py

The exporter never modifies `source-v3.png`. The only support clipping happens
inside the exported resource, under an explicit two-logical-cell Chebyshev bound
that applies only to this Data frame. Existing PSP1 projection rules remain at
one logical cell. Exact accepted PMF1 samples survive only where native Data
source writes leave PIC1 visible.

Install only `data-frame-v1.hda` in an optional directory and launch with its
absolute path:

    ./opentyrian2000 --data-frame-assets=/absolute/path/to/assets/data-frame-v1

The frame is independent of the optional `--data-text-assets` translation/font.
The source, exact support mask, prompts and metadata are development inputs.
See [resource and composition contract](../../docs/data-frame-metal.md),
[provenance](DATA-FRAME-PROVENANCE.txt), and
[precise license status](LICENSE-Data-Frame.txt).
