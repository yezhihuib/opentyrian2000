"""Reconstruct finite HUC1/HUL1 resources; FNV checks accidental corruption only."""
from pathlib import Path
import hashlib, json, struct
from PIL import Image

def sha(data): return hashlib.sha256(data).hexdigest()
def fnv(data):
    h=14695981039346656037
    for c in data: h=((h^c)*1099511628211)&0xffffffffffffffff
    return h

def checked_file(root, name):
    q=root/name
    assert not q.is_symlink() and q.is_file() and q.resolve().is_relative_to(root.resolve())
    assert not any(p.is_symlink() for p in q.parents if p != root.parent)
    return q

def build_bundles(repo):
    repo=Path(repo)
    family=json.loads((repo/'assets/hd/manifest.json').read_text())['gameplay_hud_extensions_v1']
    assert family['schema']=='finite-pic3-huc1-hul1-v1'
    result={}
    for kind, entry in family['resources'].items():
        assert kind in ('components','indicators')
        source=repo/entry['source']
        assert source.resolve().is_relative_to(repo.resolve())
        actual={str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}
        assert actual==set(entry['source_files'])
        for name, spec in entry['source_files'].items():
            raw=checked_file(source,name).read_bytes()
            assert len(raw)==spec['bytes'] and sha(raw)==spec['sha256']
        pieces=[]
        for tile in entry['tiles']:
            authored=checked_file(source,tile['authored'])
            canonical=checked_file(repo,tile['source_png'])
            assert authored.read_bytes()==canonical.read_bytes()
            assert sha(canonical.read_bytes())==tile['png_sha256']
            with Image.open(canonical) as im:
                assert im.mode=='RGBA' and list(im.size)==tile['size']
                raw=im.tobytes()
            assert sha(raw)==tile['rgba_sha256'] and set(raw[3::4])=={255}
            pieces.append(raw)
        if kind=='components':
            assert len(pieces)==18
            labels=b''.join(pieces[:4]);bands=b''.join(pieces[4:])
            assert len(labels)==22400 and len(bands)==16128
            header=struct.pack('<4s7I4Q',b'HUC1',1,4,4,22400,14,36,8,
                0x14c1441f3d5dc0e2,fnv(labels),fnv(bands),0x5e80e83992be2927)
            raw=header+labels+bands
            assert entry['filename']=='gameplay-hud-components-v1.hda' and len(raw)==38592
        else:
            assert len(pieces)==3 and list(map(len,pieces))==[1344,13824,13824]
            payload=b''.join(pieces)
            header=struct.pack('<4s7I6Q',b'HUL1',1,4,28,12,108,32,28992,
                0x14c1441f3d5dc0e2,0x5e80e83992be2927,0x328ef0a75cce2260,
                0x55f78c15a1ce495a,0xf7a97c521d045d18,fnv(payload))
            raw=header+payload
            assert entry['filename']=='gameplay-hud-indicators-v1.hda' and len(raw)==29072
        assert raw==checked_file(source,entry['filename']).read_bytes()
        receipt={'bytes':len(raw),'sha256':sha(raw)}
        assert receipt==entry['bundle']
        result[entry['filename']]=(raw,receipt)
    assert set(family['resources'])=={'components','indicators'}
    return result
