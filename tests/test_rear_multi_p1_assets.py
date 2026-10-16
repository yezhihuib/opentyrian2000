#!/usr/bin/env python3
"""Verify the six generated-only sources, exact d4/d8 payloads and role131 binds."""
from pathlib import Path
import hashlib,json,re,struct
from PIL import Image
root=Path(__file__).resolve().parents[1]
art=root/'assets/hd/artwork/player-rear-multicannon-p1-six-v1'
binding=json.loads((art/'binding.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert binding['role']==131 and binding['logical_size']==[12,14] and binding['anchor']==[0,0]
for path_key,hash_key in [('art_inventory','art_inventory_sha256'),('binding_map','binding_map_sha256'),('wrapper_receipt','wrapper_receipt_sha256'),('art_file_manifest','art_file_manifest_sha256')]:
    assert sha(art/binding[path_key])==binding[hash_key]
inv=json.loads((art/binding['art_inventory']).read_text())
for name,pin in inv['inputs'].items():assert sha(art/name)==pin,name
for a in json.loads((art/binding['art_file_manifest']).read_text())['files']:
    assert (art/a['path']).stat().st_size==a['bytes'] and sha(art/a['path'])==a['sha256']
seen=set();stamps={}
for a in binding['resources']:
    sid,d=a['source_id'],a['density'];assert (sid,d) not in seen;seen.add((sid,d))
    assert sid in [1,39,281,282,300,301] and d in [4,8] and a['key']==1310000+sid
    assert a['logical_size']==[12,14] and a['anchor']==[0,0] and a['role']==131
    raw=(art/a['rgba']).read_bytes();assert len(raw)==168*d*d*4
    assert sha(art/a['rgba'])==a['rgba_sha256'] and sha(art/a['png'])==a['png_sha256'] and sha(art/a['svg'])==a['svg_sha256']
    image=Image.open(art/a['png']).convert('RGBA');assert image.size==(12*d,14*d) and image.tobytes()==raw
    h=14695981039346656037
    for v in raw:h=((h^v)*1099511628211)&((1<<64)-1)
    assert f'0x{h:016x}'==a['rgba_fnv1a64'];stamps[sid,d]=h
    assert any(0<v<255 for v in raw[3::4]),'fractional alpha was lost'
    assert len(a['pack_paths'])==2
    for name in a['pack_paths']:
        path=root/name;b=path.read_bytes();assert sha(path)==a['hda_sha256'] and len(b)==a['hda_bytes']
        assert struct.unpack('<4s6I',b[:28])==(b'HDR1',1310000+sid,d,12,14,0,0) and b[28:]==raw
assert len(seen)==12
pins=(root/'src/rear_multi_p1_pins.h').read_text().split('#define REAR_P1_RGBA_PINS ',1)[1].split('\n',1)[0]
assert [int(x,16) for x in re.findall(r'UINT64_C\(0x([0-9a-f]+)\)',pins)][:12]==[stamps[sid,d] for sid in [39,1,281,282,301,300] for d in [4,8]]
print('Rear P1 R2: 6 pinned SVG masters,12 exact PNG/RGBA variants,24 byte-exact default-pack HDR1 files; fractional alpha and runtime pins verified')
