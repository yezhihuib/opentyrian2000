#!/usr/bin/env python3
"""Verify exact accepted-component reuse and the four finite role131 resources.

Only generated assets are read. No original data, masks or capture is required.
"""
from pathlib import Path
import hashlib,json,re,struct,subprocess,sys,tempfile
from PIL import Image

root=Path(__file__).resolve().parents[1]
art=root/'assets/hd/artwork/player-rear-multicannon-p3-mode1-two-v1'
old=root/'assets/hd/artwork/player-rear-multicannon-p1-six-v1'
component=art/'components'
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((component/'file-manifest.json').read_text())
assert sha((component/'file-manifest.json').read_bytes())=='c1ece694062816a0296d1d45969cd1666b9d4864b704f766c4be1e3cd72de5bd'
assert len(manifest['files'])==28
assert {str(p.relative_to(component)) for p in component.rglob('*') if p.is_file()}==set(manifest['files'])|{'file-manifest.json'}
for n,h in manifest['files'].items():
    p=component/n;assert not p.is_symlink() and sha(p.read_bytes())==h,n
contract=json.loads((component/'output/transform-contract.json').read_text())
for n,h in contract['accepted_component_file_pins'].items():assert sha((old/n).read_bytes())==h,n

binding=json.loads((art/'binding.json').read_text())
assert binding['role']==131 and binding['logical_size']==[12,14] and binding['anchor']==[0,0]
assert sha((component/'file-manifest.json').read_bytes())==binding['approved_component_manifest_sha256']
assert sha((component/'build_composites.py').read_bytes())==binding['component_builder_sha256']
assert sha((art/'pack-hda.py').read_bytes())==binding['wrapper_sha256']
assert sha((art/'binding-map.json').read_bytes())==binding['binding_map_sha256']
catalog=json.loads((root/'assets/hd/manifest.json').read_text())
entry=catalog['player_rear_multicannon_p3_mode1_two_v1']
assert entry['binding_sha256']==sha((art/'binding.json').read_bytes())
assert entry['ids']==[2,40] and entry['densities']==[4,8] and entry['role']==131
default_packs={catalog['default_preview_pack'],catalog['default_debug_pack']}
seen=set();stamps={}
for a in binding['resources']:
    sid,d=a['source_id'],a['density'];assert (sid,d) not in seen;seen.add((sid,d))
    assert sid in [2,40] and d in [4,8] and a['key']==1310000+sid
    assert a['logical_size']==[12,14] and a['anchor']==[0,0] and a['role']==131
    raw=(art/a['rgba']).read_bytes();assert len(raw)==168*d*d*4 and sha(raw)==a['rgba_sha256']
    assert sha((art/a['png']).read_bytes())==a['png_sha256']
    with Image.open(art/a['png']) as image:
        assert image.mode=='RGBA' and image.size==(12*d,14*d) and image.tobytes()==raw
    source=1 if sid==2 else 39
    source_raw=(old/f'output/rear-multi-{source}-{d}.rgba').read_bytes()
    specs=[(False,-2),(True,2)] if sid==2 else [(True,-4),(False,4)]
    expected=bytearray(len(raw));w,h=12*d,14*d
    for n,(flip,dy) in enumerate(specs,1):
        layer=bytearray(len(raw))
        # Independent destination-to-source construction, not the builder loop.
        for y in range(h):
            pre=y-dy*d;sy=h-1-pre if flip else pre
            if 0<=sy<h:
                for x in range(w):
                    q=(sy*w+x)*4;p=(y*w+x)*4
                    layer[p:p+4]=source_raw[q:q+4]
        recorded=(component/f'output/rear-multi-{sid}-{d}-lobe-{n}.rgba').read_bytes()
        assert bytes(layer)==recorded
        assert sum(layer[3::4])==sum(source_raw[3::4])
        for c in range(3):
            assert sum(layer[p+c]*layer[p+3] for p in range(0,len(layer),4))==sum(source_raw[p+c]*source_raw[p+3] for p in range(0,len(source_raw),4))
        for p in range(0,len(raw),4):
            if layer[p+3]:
                assert not expected[p+3],'Lobes must not overlap'
                expected[p:p+4]=layer[p:p+4]
    assert bytes(expected)==raw
    assert not any(raw[(6*d*w)*4+3:(8*d*w)*4:4]),'Central two-row gap changed'
    assert any(0<v<255 for v in raw[3::4]),'Fractional alpha was lost'
    assert all(raw[p:p+3]==b'\0\0\0' for p in range(0,len(raw),4) if not raw[p+3])
    stamp=14695981039346656037
    for v in raw:stamp=((stamp^v)*1099511628211)&((1<<64)-1)
    assert a['rgba_fnv1a64']==f'0x{stamp:016x}';stamps[sid,d]=stamp
    assert len(a['pack_paths'])==2
    assert {Path(n).parent.name for n in a['pack_paths']}==default_packs
    for n in a['pack_paths']:
        p=root/n;data=p.read_bytes();assert sha(data)==a['hda_sha256'] and len(data)==a['hda_bytes']
        assert struct.unpack('<4s6I',data[:28])==(b'HDR1',1310000+sid,d,12,14,0,0) and data[28:]==raw
        row=catalog['packs'][p.parent.name]['files'][p.name]
        assert row['sha256']==sha(data) and row['header_u32']==[1310000+sid,d,12,14,0,0]
        assert row['source_png']==a['catalog_source_png'] and row['source_png_sha256']==a['png_sha256']
        assert (root/row['source_png']).read_bytes()==(art/a['png']).read_bytes()
    assert catalog['source_pngs'][a['hda_sha256']]=={'path':a['catalog_source_png'],'sha256':a['png_sha256'],'RGBA_sha256':a['rgba_sha256']}
    for pack,items in catalog['packs'].items():
        if pack not in default_packs:
            assert a['filename'] not in items['files']
            assert not (root/'assets/hd/packs'/pack/a['filename']).exists()
assert seen=={(sid,d) for sid in [2,40] for d in [4,8]}
assert entry['entries']==[{'id':a['source_id'],'density':a['density'],'HDA_sha256':a['hda_sha256']} for a in binding['resources']]
pins=(root/'src/rear_multi_p1_pins.h').read_text().split('#define REAR_P1_RGBA_PINS ',1)[1].split('\n',1)[0]
pin_values=[int(x,16) for x in re.findall(r'UINT64_C\(0x([0-9a-f]+)\)',pins)]
assert len(pin_values)==16 and pin_values[12:]==[stamps[sid,d] for sid in [40,2] for d in [4,8]]
for pack in default_packs:
    assert catalog['packs'][pack]['count']==len(catalog['packs'][pack]['files'])
with tempfile.TemporaryDirectory(prefix='rear-p3-mode1-art-') as t:
    out=Path(t)/'art';hda=Path(t)/'hda'
    subprocess.run([sys.executable,str(component/'build_composites.py'),str(old),str(out)],check=True)
    expected_files={p.name for p in (component/'output').iterdir()}
    assert {p.name for p in out.iterdir()}==expected_files
    for p in out.iterdir():assert p.read_bytes()==(component/'output'/p.name).read_bytes()
    subprocess.run([sys.executable,str(art/'pack-hda.py'),str(hda)],check=True)
    assert {p.name for p in hda.iterdir()}=={a['filename'] for a in binding['resources']}
    for a in binding['resources']:assert (hda/a['filename']).read_bytes()==(root/a['pack_paths'][0]).read_bytes()
print('Rear P3 mode1: four exact component composites, eight layers, two-row gaps, fractional alpha, eight default-pack HDR1 copies, catalog/pins and deterministic rebuild PASS')
