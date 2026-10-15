#!/usr/bin/env python3
"""Rebuild five frozen generated Plasma body imports; never paint or animate."""
from pathlib import Path
from PIL import Image, __version__ as pillow_version
import argparse, hashlib, json, struct
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parent
    c = json.loads((root / 'contract.json').read_text())
    out = a.output.resolve()
    assert not out.exists() and not any(x.is_symlink() for x in [out, *out.parents])
    assert root not in out.parents and out not in root.parents
    r = c['reconstruction']
    assert pillow_version == r['version']
    out.mkdir(parents=True)
    for e in c['entries']:
        source = root / e['source']
        assert root in source.resolve().parents and sha(source.read_bytes()) == e['source_sha256']
        im = Image.open(source).convert('RGBA')
        piece = im.crop(e['crop']).resize(r['resize'], Image.Resampling.LANCZOS)
        result = Image.new('RGBA', tuple(r['canvas']))
        result.paste(piece, tuple(r['paste']))
        raw = result.tobytes()
        hda = struct.pack('<4s6I', b'HDR1', *e['header_u32']) + raw
        assert sha(raw) == e['RGBA_sha256'] and sha(hda) == e['HDA_sha256']
        stem = f"option-plasma-bank9-{e['id']}-8"
        result.save(out / (stem + '.png'))
        (out / (stem + '.hda')).write_bytes(hda)
        assert sha((out / (stem + '.png')).read_bytes()) == e['PNG_sha256']
    print('PASS the fixed generated-master crop/resample/paste imports: exact PNG, RGBA and HDA')

if __name__ == '__main__':
    main()
