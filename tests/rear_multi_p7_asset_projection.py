"""Validate and remove only the exact additive P7 art from historical oracles."""
from pathlib import Path
import copy
import hashlib
import json
import struct
FAMILY='player_rear_multicannon_p7_mode1_reflections_v1'
PACKAGE='assets/hd/artwork/player-rear-multicannon-p7-mode1-reflections-v1'
BINDING='6fc54deecea4bd11363435f9fcc9ea15d910da9cb142d7ca19cc90fafd19d28a'
FILES='ec2ef69229d8bff9bc05b008367327f2757064d51ba3a632def78f5266f35567'
BASE='6bd3bb4ca9fe7f4a98778aeb938b97c349fe215f09d0aecea9d85d64064f3ed4'
sha=lambda b:hashlib.sha256(b).hexdigest()
def project_p7(root,catalog):
    result=copy.deepcopy(catalog); paths=set()
    if FAMILY not in result:
        return result,paths
    family=result.pop(FAMILY); art=root/PACKAGE
    assert family['source']==PACKAGE and family['ids']==[296,297] and family['role']==131 and family['densities']==[4,8]
    assert sha((art/'binding.json').read_bytes())==family['binding_sha256']==BINDING
    assert sha((art/'file-manifest.json').read_bytes())==family['art_file_manifest_sha256']==FILES
    binding=json.loads((art/'binding.json').read_text()); manifest=json.loads((art/'file-manifest.json').read_text())['files']
    assert len(manifest)==15 and {str(p.relative_to(art))for p in art.rglob('*')if p.is_file()}==set(manifest)|{'file-manifest.json'}
    for name,pin in manifest.items():
        assert not (art/name).is_symlink() and sha((art/name).read_bytes())==pin
        paths.add(PACKAGE+'/'+name)
    paths.add(PACKAGE+'/file-manifest.json')
    packs={catalog['default_preview_pack'],catalog['default_debug_pack']}
    assert [(r['source_id'],r['density'])for r in binding['resources']]==[(296,4),(296,8),(297,4),(297,8)]
    for row in binding['resources']:
        i,d=row['source_id'],row['density'];raw=(art/row['rgba']).read_bytes();png=(art/row['png']).read_bytes()
        assert sha(raw)==row['rgba_sha256'] and sha(png)==row['png_sha256']
        assert row['filename']==f'rear-multicannon-p1-bank8-{i}-{d}.hda'
        assert row['catalog_source_png']==f"assets/hd/source/rear-multicannon-p1-bank8-{i}-{d}-{row['hda_sha256'][:12]}.png"
        assert result['source_pngs'].pop(row['hda_sha256'])=={'path':row['catalog_source_png'],'sha256':row['png_sha256'],'RGBA_sha256':row['rgba_sha256']}
        assert (root/row['catalog_source_png']).read_bytes()==png;paths.add(row['catalog_source_png'])
        assert set(row['pack_paths'])=={f'assets/hd/packs/{p}/{row["filename"]}'for p in packs}
        for pack in packs:
            path=f'assets/hd/packs/{pack}/{row["filename"]}';blob=(root/path).read_bytes()
            assert blob==struct.pack('<4s6I',b'HDR1',1310000+i,d,12,14,0,0)+raw and sha(blob)==row['hda_sha256']
            assert result['packs'][pack]['files'].pop(row['filename'])=={'sha256':row['hda_sha256'],'header_u32':[1310000+i,d,12,14,0,0],'source_png':row['catalog_source_png'],'source_png_sha256':row['png_sha256']}
            result['packs'][pack]['count']-=1;paths.add(path)
        for name,pack in catalog['packs'].items():
            if name not in packs:assert row['filename']not in pack['files'] and not(root/'assets/hd/packs'/name/row['filename']).exists()
    assert len(paths)==28 and sha((json.dumps(result,indent=2)+'\n').encode())==BASE
    return result,paths
