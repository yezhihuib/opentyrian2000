# Accepted canonical shop icons

These three PNG files are the **exact user-approved normalized bytes**, accepted
2026-10-21 06:55:18 UTC after the static original/new shop comparison. They are
not gameplay art and are not bound to a single equipment ID. NEWSH1 quad 235 and
199 are shared source identities; every item using the authenticated canonical
quad may use the same icon in the authenticated shop context.

`manifest.json` pins PNG, original master, decoded RGBA, encoded HDA and original
bank fingerprints. `scripts/export_shop_static.py` accepts only these exact PNG
hashes and the exact original NEWSH1 fingerprint. It copies each PNG unchanged
and encodes its straight RGBA bytes unchanged: no cropping, resampling, threshold,
color edits, alpha edits, or repainting. Original game bytes are never embedded.

## SQC1

128-byte little-endian header followed by exactly 172032 straight RGBA8 bytes
(192 × 224). Header bytes 0–3 are `SQC1`; fifteen u32 fields start at offset 4:
version=1, canonical quad, logical width=24, height=28, density=8, pixel width=192,
height=224, anchor x=0, y=0, payload bytes=172032, channels=4,
straight RGBA=1, source identity version=1, reserved=0, reserved=0.
Eight u64 fields begin at offset 64: PIC1 base FNV, canonical palette FNV,
NEWSH1 bank FNV, decoded quad index FNV, decoded quad mask FNV, RGBA payload FNV,
reserved=0, reserved=0. FNV is FNV-1a 64-bit. The quad comprises tiles q, q+1,
q+19, q+20 at offsets (0,0), (12,0), (0,14), (12,14). Decoded indices and mask
are each 672 row-major bytes, mask 255 on original written samples, zero elsewhere.

The runtime derives display samples from the immutable 8× payload; display
sampling does not change the accepted source asset. Runtime/context validation
is documented and tested separately; resource encoding is not runtime evidence.
