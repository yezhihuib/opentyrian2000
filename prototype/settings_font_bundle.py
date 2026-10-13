"""Validate/rebuild the finite nine-file optional startup/title/settings pack."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,tempfile
from title_menu_font_bundle import build_bundles as title_bundles
PACK='startup-title-settings-v1'
SOURCE='assets/hd/artwork/settings-font-v1'
LARGE='assets/hd/artwork/formal-menu-large-font-v2'
SETTINGS_NAMES=('settings-font-large-v1.hda','settings-font-medium-v1.hda','settings-font-tiny-v1.hda')
EXPECTED={'settings-font-large-v1.hda':(934016,'7827555a736375ff45bd78dc2c05c5651e65d3b024527e8dba525d3beff721e5'),'settings-font-medium-v1.hda':(688256,'51852f5d54516de70a5729e991fb14104871b9ad58991f0352899ab4502bd484'),'settings-font-tiny-v1.hda':(163968,'888b635af0c123dc77fecf2f50a2e603f85a0fb6ad74a1c4215b29affc28a35c')}
sha=lambda b:hashlib.sha256(b).hexdigest()
def regular(p):
    assert p.is_file() and not any(x.is_symlink() for x in [p,*p.parents]),p
    return p.read_bytes()
def build_bundles(repo,check_manifest=True):
    pin_bytes=regular(repo/SOURCE/'large-source-pins.json')
    assert sha(pin_bytes)=='962be4b2fa26cbb64f4777e488dcd378377e49ab196ad1cc4d25e26f61318b51'
    pins=json.loads(pin_bytes)
    assert {str(p.relative_to(repo/LARGE)) for p in (repo/LARGE).rglob('*') if p.is_file()}==set(pins)
    for name,stamp in pins.items():
        raw=regular(repo/LARGE/name);assert stamp=={'bytes':len(raw),'sha256':sha(raw)},name
    bundles=title_bundles(repo);assert len(bundles)==6
    with tempfile.TemporaryDirectory(prefix='settings-source-export-') as temporary:
        output=Path(temporary)/'canonical'
        subprocess.run([sys.executable,str(repo/'tools/export_settings_fonts.py'),'--large',str(repo/LARGE),'--repo',str(repo),'--out',str(output)],check=True,capture_output=True)
        for name,(size,digest) in EXPECTED.items():
            raw=regular(repo/SOURCE/'canonical'/name)
            assert len(raw)==size and sha(raw)==digest and raw==regular(output/name),name
            bundles[name]=(raw,{'bytes':len(raw),'sha256':sha(raw)})
    family={'schema':'finite-settings-font-sfn1-v1','pack':PACK,'source':SOURCE,'large_source':LARGE,'large_source_pins_sha256':sha(regular(repo/SOURCE/'large-source-pins.json')),'count':9,'settings_font_count':3,'compatibility_source_pack':'startup-title-menu-v1','compatibility_count':6,'files':{name:stamp for name,(_,stamp) in sorted(bundles.items())},'runtime_bytes':sum(len(raw) for raw,_ in bundles.values())}
    if check_manifest:assert json.loads(regular(repo/'assets/hd/manifest.json'))['startup_settings_font_v1']==family
    directory=repo/'assets/hd/packs'/PACK
    assert {p.name for p in directory.iterdir()}==set(bundles)
    for name,(raw,_) in bundles.items():assert regular(directory/name)==raw,name
    return bundles,family
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();repo=Path(__file__).resolve().parents[1];bundles,family=build_bundles(repo)
    if a.output:
        assert a.output.is_absolute() and not a.output.exists() and not any(q.is_symlink() for q in a.output.parents)
        a.output.mkdir()
        for name,(raw,_) in bundles.items():(a.output/name).write_bytes(raw)
    print(json.dumps(family,indent=2))
