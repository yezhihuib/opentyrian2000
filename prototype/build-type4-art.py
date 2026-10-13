#!/usr/bin/env python3
"""Reproduce and verify the exact approved type4 fractional-contour v2 art.
Original data is optional read-only identity/registration evidence, never an art input.
"""
from pathlib import Path
import argparse, hashlib, json, re, struct, subprocess, sys
from PIL import Image, ImageChops
IDS = [159,161,163,165,167]
ORDER = [159,159,161,161,163,163,165,165,167,167,165,165,163,163,161,161,159,159,159,159]
sha = lambda data: hashlib.sha256(data).hexdigest()
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--original-data',type=Path)
p.add_argument('--enemy-data',type=Path)
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
source = repo / 'assets/hd/artwork/type4-fivepose-smooth-contour-v2'
given = a.output.absolute(); out = given.resolve()
if any(q.is_symlink() for q in [given,*given.parents]) or out.exists() or out == repo or repo in out.parents or out in repo.parents:
    p.error('Choose a fresh directory outside the repository, without symlink path components')
assert all(not q.is_symlink() for q in source.rglob('*'))
manifest = json.loads((repo/'assets/hd/manifest.json').read_text())
family = manifest['enemy_type4_fivepose_v1']
assert family['ids']==IDS and family['slots']==list(range(369,374))
assert family['bank']=='newsh2.shp' and family['bank_role']==101 and family['enemy_type']==4
assert family['style']=='NORMAL' and family['logical_size']==[24,28] and family['anchor']==[6,7]
assert family['density']==8 and family['runtime_components']==[0,1,19,20] and family['order']==ORDER
assert family['source']==str(source.relative_to(repo)) and family['art_revision']=='smooth-contour-v2'
assert family['source_inventory']=='SHA256SUMS.json'
assert sha((source/'SHA256SUMS.json').read_bytes())==family['source_inventory_sha256']
imported=json.loads((source/'IMPORT.json').read_text())
assert imported['source_inventory_sha256']==family['source_inventory_sha256']
assert len(imported['files'])==len({e['path'] for e in imported['files']})
assert {e['path'] for e in imported['files']}=={str(f.relative_to(source)) for f in source.rglob('*') if f.is_file() and f.name!='IMPORT.json'}
for e in imported['files']:
    path=source/e['path']; assert source in path.resolve().parents
    assert sha(path.read_bytes())==e['sha256'],e['path']
for name,digest in json.loads((source/'SHA256SUMS.json').read_text()).items():
    path=source/name; assert source in path.resolve().parents
    assert sha(path.read_bytes())==digest,name
contract=json.loads((source/'contract.json').read_text())
proof=json.loads((repo/'assets/hd/artwork/type4-fivepose-v1/proof/type4-source-proof.json').read_text())
assert contract['ids']==IDS and contract['order']==ORDER==proof['record4']['egraphic']==proof['animation']['order']
assert contract['bank']=='newsh2.shp' and contract['namespace']==101 and contract['enemy_type']==4
assert contract['logical_size']==[24,28] and contract['anchor']==[6,7] and contract['density']==8
assert contract['quadrant_offsets']==[0,1,19,20]
assert proof['record4']['shapebank']==1 and proof['record4']['ani']==20
assert [proof['record4'][k] for k in ('dgr','dani','dlevel','eenemydie')]==[0]*4
assert [e['id'] for e in contract['entries']]==IDS
if a.enemy_data:
    data = a.enemy_data.read_bytes()
    assert sha(data) == proof['original_sources_sha256']['tyrian.hdt']
    source_reader = (repo / 'src/episodes.c').read_text()
    formats = {'u8': 'B', 's8': 'b', 'u16': 'H', 's16': 'h'}
    def schema(variable):
        return [(m[2], formats[m[1]], int(m[3])) for m in re.finditer(
            r'fread_(u8|s8|u16|s16)_die\(\s*&?' + variable + r'\[i\]\.(\w+),\s*(\d+),\s*f\)', source_reader)]
    weapon_schema, enemy_schema = schema('weapons'), schema('enemyDat')
    assert len(enemy_schema) == 28 and weapon_schema
    position = struct.unpack_from('<i', data)[0] + 14
    position += 1638 * sum(n * struct.calcsize(fmt) for _, fmt, n in weapon_schema)
    position += 61 * 82 + sum(n * size for n, size in [(55, 37), (7, 37), (19, 41), (38, 86), (12, 37)])
    users = []
    record_ids = list(range(851)) + list(range(1001, 1851))
    assert len(record_ids) == 1701
    for record_id in record_ids:
        record = {'id': record_id}
        for name, fmt, count in enemy_schema:
            values = list(struct.unpack_from('<' + str(count) + fmt, data, position))
            position += count * struct.calcsize(fmt)
            record[name] = values[0] if count == 1 else values
        if record_id == 4:
            assert record == proof['record4']
        if record['shapebank'] == 1 and (set(record['egraphic']) & set(IDS)
                or (not record['dani'] and record['dgr'] in IDS)):
            users.append(record_id)
    assert position <= len(data) and users == [4]
subprocess.run([sys.executable,str(source/'rebuild.py'),'--output',str(out)],check=True)
original=a.original_data.read_bytes() if a.original_data else None
if original: assert sha(original)==proof['original_sources_sha256']['newsh2.shp']
for e in contract['entries']:
    sprite_id=e['id']; name=f'enemy-newsh2-{sprite_id}-8'
    expected_header=[1010000+sprite_id,8,24,28,6,7]
    raw=(out/(name+'.hda')).read_bytes(); png=out/(name+'.png')
    assert e['header_u32']==expected_header
    assert raw[:28]==b'HDR1'+struct.pack('<6I',*expected_header) and len(raw)==28+192*224*4
    assert sha(raw)==e['HDA_sha256'] and sha(raw[28:])==e['RGBA_sha256']
    assert sha(png.read_bytes())==e['PNG_sha256']
    image=Image.open(png); assert image.mode=='RGBA' and image.size==(192,224)
    alpha=image.getchannel('A'); assert any(0<v<255 for v in alpha.tobytes())
    assert alpha.tobytes()==Image.open(source/'masks'/f'authored-alpha-{sprite_id}-8.png').tobytes()
    strong=alpha.point(lambda value:255 if value>=128 else 0)
    assert list(strong.getbbox())==e['registered_bbox8_alpha128']
    assert list(strong.getbbox())==[v*8 for v in e['original_bbox_logical']]
    original_alpha=Image.open(source/'masks'/f'original-alpha-{sprite_id}-24x28.png')
    original8=original_alpha.resize((192,224),Image.Resampling.NEAREST)
    assert ImageChops.subtract(alpha,original8).tobytes()==Image.open(source/'masks'/f'support-additions-{sprite_id}.png').tobytes()
    assert ImageChops.subtract(original8,alpha).tobytes()==Image.open(source/'masks'/f'support-removals-{sprite_id}.png').tobytes()
    frame=next(f for f in proof['frames'] if f['base_id']==sprite_id)
    assert sha(original_alpha.tobytes())==frame['alpha_sha256']
    assert [c['id'] for c in frame['cells']]==[sprite_id+d for d in (0,1,19,20)]
    if original:
        mask=bytearray(24*28)
        for cell,(delta,x,y) in zip(frame['cells'],[(0,0,0),(1,12,0),(19,0,14),(20,12,14)]):
            pos=struct.unpack_from('<H',original,(sprite_id+delta-1)*2)[0];start=pos;linear=0
            while original[pos]!=15:
                command=original[pos];pos+=1;linear+=command&15;count=command>>4
                assert 0<=linear<=168 and linear+count<=168
                for n in range(linear,linear+count):mask[(y+n//12)*24+x+n%12]=255
                linear+=count;pos+=count
            assert sha(original[start:pos+1])==cell['source_record_sha256']
        assert bytes(mask)==original_alpha.tobytes()
    for key in ('default_preview_pack','default_debug_pack'):
        pack=manifest['packs'][manifest[key]]; assert pack['count']==len(pack['files'])
        entry=pack['files'][name+'.hda'];assert entry['header_u32']==expected_header
        actual=(repo/'assets/hd/packs'/manifest[key]/(name+'.hda')).read_bytes()
        assert actual==raw and sha(actual)==entry['sha256']
        canonical=repo/entry['source_png'];assert canonical.read_bytes()==png.read_bytes()
        assert sha(canonical.read_bytes())==entry['source_png_sha256']
        indexed=manifest['source_pngs'][sha(raw)]
        assert indexed['path']==entry['source_png'] and indexed['sha256']==entry['source_png_sha256'] and indexed['RGBA_sha256']==sha(raw[28:])
    for pack_name,pack in manifest['packs'].items():
        for density in (4,8):
            assert (f'enemy-newsh2-{sprite_id}-{density}.hda' in pack['files'])==(density==8 and pack_name in (manifest['default_preview_pack'],manifest['default_debug_pack']))
print('PASS five frozen generated-only fractional-contour PNG/RGBA/HDR1 assets; two-default scope; exact registration, original-size support bbox, source records, order and namespace. No game run.')
