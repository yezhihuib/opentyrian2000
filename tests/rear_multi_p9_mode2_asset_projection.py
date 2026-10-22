"""Validate and remove only the exact additive P9 mode2 art from historical oracles."""
from pathlib import Path
import copy
import hashlib
import json
import struct
FAMILY='player_rear_multicannon_p9_mode2_rotations_v1'
PACKAGE='assets/hd/artwork/player-rear-multicannon-p9-mode2-rotations-v1'
BINDING='4ac08526cf1df97b7f6a51c38bd53f2d56547f84bd6cf3cf1f138fc591feae3f'
FILES='dfebf6b1162d38beed48ea5805c9dd5b29274e7b0084bdb5e3dd26ceadb469fb'
BASE='b0ff398229a2a6ab64abadf778b1003a576af38b0ca4d3d829c5c5c6b4d9eb39'
FAMILY_SHA='50e532b44b372bc5182d255844f44f558e460cf10d524018988e195f6a3b824f'
sha=lambda b:hashlib.sha256(b).hexdigest()
def project_p9_mode2(root,catalog):
    from accepted_later_changes import project_p9_catalog
    catalog=project_p9_catalog(catalog)
    result=copy.deepcopy(catalog); paths=set()
    if FAMILY not in result:
        return result,paths
    family=result.pop(FAMILY); art=root/PACKAGE
    assert not art.is_symlink() and not any(p.is_symlink() for p in art.rglob("*"))
    assert sha(json.dumps(family,sort_keys=True,separators=(',',':')).encode())==FAMILY_SHA
    assert family['source']==PACKAGE and family['ids']==[298,299] and family['role']==131 and family['densities']==[4,8]
    assert sha((art/'binding.json').read_bytes())==family['binding_sha256']==BINDING
    assert sha((art/'file-manifest.json').read_bytes())==family['art_file_manifest_sha256']==FILES
    binding=json.loads((art/'binding.json').read_text()); manifest=json.loads((art/'file-manifest.json').read_text())['files']
    assert len(manifest)==25 and {str(p.relative_to(art))for p in art.rglob('*')if p.is_file()}==set(manifest)|{'file-manifest.json'}
    for name,pin in manifest.items():
        assert not (art/name).is_symlink() and sha((art/name).read_bytes())==pin
        paths.add(PACKAGE+'/'+name)
    paths.add(PACKAGE+'/file-manifest.json')
    packs={catalog['default_preview_pack'],catalog['default_debug_pack']}
    assert [(r['source_id'],r['density'])for r in binding['resources']]==[(298,4),(298,8),(299,4),(299,8)]
    for row in binding['resources']:
        i,d=row['source_id'],row['density'];raw=(art/row['rgba']).read_bytes();png=(art/row['png']).read_bytes()
        assert sha(raw)==row['rgba_sha256'] and sha(png)==row['png_sha256']
        assert (art/row['package_hda']).read_bytes()==struct.pack('<4s6I',b'HDR1',1310000+i,d,12,14,0,0)+raw
        assert row['filename']==f'rear-multicannon-p1-bank8-{i}-{d}.hda'
        assert row['catalog_source_png']==f"assets/hd/source/rear-multicannon-p1-bank8-{i}-{d}-{row['hda_sha256'][:12]}.png"
        assert result['source_pngs'].pop(row['hda_sha256'])=={'path':row['catalog_source_png'],'sha256':row['png_sha256'],'RGBA_sha256':row['rgba_sha256']}
        assert not(root/row['catalog_source_png']).is_symlink()
        assert (root/row['catalog_source_png']).read_bytes()==png;paths.add(row['catalog_source_png'])
        assert set(row['pack_paths'])=={f'assets/hd/packs/{p}/{row["filename"]}'for p in packs}
        for pack in packs:
            path=f'assets/hd/packs/{pack}/{row["filename"]}';assert not(root/path).is_symlink();blob=(root/path).read_bytes()
            assert blob==struct.pack('<4s6I',b'HDR1',1310000+i,d,12,14,0,0)+raw and sha(blob)==row['hda_sha256']
            assert result['packs'][pack]['files'].pop(row['filename'])=={'sha256':row['hda_sha256'],'header_u32':[1310000+i,d,12,14,0,0],'source_png':row['catalog_source_png'],'source_png_sha256':row['png_sha256']}
            result['packs'][pack]['count']-=1;paths.add(path)
        for name,pack in catalog['packs'].items():
            if name not in packs:assert row['filename']not in pack['files'] and not(root/'assets/hd/packs'/name/row['filename']).exists()
    assert len(paths)==38 and sha((json.dumps(result,indent=2)+'\n').encode())==BASE
    return result,paths
