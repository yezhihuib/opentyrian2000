"""Finite title-only TMF1 V3.1 artwork and the explicit six-file startup pack."""
from pathlib import Path
import argparse,hashlib,json,shutil,struct,subprocess,sys,tempfile
from PIL import Image
from title_layer_bundle import checked_file,require,require_inventory,sha,fnv64,build_bundles as title_bundles

PACK='startup-title-menu-v1'
SOURCE='assets/hd/artwork/title-menu-font-v3-1'
FILENAME='title-menu-font-v1.hda'
SCHEMA='finite-title-menu-tmf1-v3-1'
SOURCE_MANIFEST_SHA256='ab89e4bff91beab301ba334ed6cf202d656a21d48f12e94cbe0abbe4102c385c'
RESOURCE_SHA256='26e4f9eabed4f90bfe74896e04ee59e647e445ffd44a9feaf003c91444275a4d'
SOURCE_FILES=frozenset(('README.md','manifest.json','contract.json','rebuild.py','sources/menu-normal-vectors.json','sources/source-metrics.json','proof/initial-build.json','proof/j-only-correction.json','proof/offline-preview-validation.json','proof/reproduction-validation.json','proof/sampling-contract.json','canonical/menu-normal-coverage-4x.alpha.bin','canonical/menu-normal-coverage-4x.png','canonical/menu-normal-roles-4x.bin','canonical/menu-normal-roles-4x.png','canonical/menu-normal-vector-atlas.svg','canonical/title-menu-font-v1.hda'))
PINS=('845b16939661b466','f0dec0f37828f1c4','96f0e4e668876f23','a3861b64f710cb1f','8f64628a08533287')
HEADER=struct.Struct('<4s15I8Q')
FIELDS=(1,4,896,384,85,76,56,64,4,1,344064,344064,12,15,0)

def source_receipts(source):
    require_inventory(source,SOURCE_FILES,'Frozen TMF1 source')
    raw=checked_file(source,'manifest.json').read_bytes()
    require(sha(raw)==SOURCE_MANIFEST_SHA256,'TMF1 frozen manifest changed')
    manifest=json.loads(raw)
    receipts={name:{'bytes':len(data),'sha256':sha(data)} for name in sorted(SOURCE_FILES) for data in [checked_file(source,name).read_bytes()]}
    require(manifest['files']=={name:receipt for name,receipt in receipts.items() if name!='manifest.json'},'TMF1 source file identity changed')
    return receipts

def build_resource(source):
    source=Path(source);source_receipts(source)
    contract=json.loads(checked_file(source,'contract.json').read_text())
    vectors=json.loads(checked_file(source,'sources/menu-normal-vectors.json').read_text())
    require(vectors['font']==1 and vectors['density']==4 and vectors['atlas_size']==[896,384] and vectors['cell_size']==[56,64] and vectors['inset']==4,'TMF1 geometry registration changed')
    alpha=checked_file(source,'canonical/menu-normal-coverage-4x.alpha.bin').read_bytes()
    roles=checked_file(source,'canonical/menu-normal-roles-4x.bin').read_bytes()
    require(len(alpha)==len(roles)==344064,'TMF1 plane size changed')
    with Image.open(checked_file(source,'canonical/menu-normal-coverage-4x.png')) as image:
        require(image.mode=='RGBA' and image.size==(896,384) and image.getchannel('A').tobytes()==alpha,'TMF1 coverage PNG mismatch')
    with Image.open(checked_file(source,'canonical/menu-normal-roles-4x.png')) as image:
        require(image.mode=='L' and image.size==(896,384) and image.tobytes()==roles,'TMF1 role PNG mismatch')
    glyphs=vectors['glyphs'];require([g['sprite_id'] for g in glyphs]==list(range(85)),'TMF1 glyph inventory changed')
    require(all(g['stroke_width_logical']==1.90 for g in glyphs),'TMF1 unapproved stroke variant')
    require(fnv64(b''.join(struct.pack('<3H',g['width'],g['height'],g['advance']) for g in glyphs))==PINS[1],'TMF1 metrics changed')
    require(fnv64(bytes(0 if g['blank_original'] else 255 for g in glyphs))==PINS[3],'TMF1 blank slots changed')
    for gid in range(96):
        g=glyphs[gid] if gid<85 else None;visible=False
        for y in range(64):
            for x in range(56):
                p=((gid//16)*64+y)*896+(gid%16)*56+x;a,r=alpha[p],roles[p]
                allowed=g and not g['blank_original'] and 4<=x<4+g['width']*4 and 4<=y<4+g['height']*4
                require((allowed or (not a and not r)) and ((not a and not r) or (a and 12<=r<=15)),'TMF1 support, blank, padding or role mismatch')
                visible|=bool(a)
        require(visible==bool(g and not g['blank_original']),'TMF1 visible glyph missing')
    payload=alpha+roles
    raw=HEADER.pack(b'TMF1',*FIELDS,*[int(v,16) for v in PINS],int(fnv64(payload),16),0,0)+payload
    require(fnv64(payload)=='08f9609583417c89' and sha(raw)==RESOURCE_SHA256,'TMF1 approved V3.1 payload changed')
    require(raw==checked_file(source,'canonical/'+FILENAME).read_bytes(),'TMF1 canonical resource differs')
    require(contract['resource']['header_format']=='<4s15I8Q' and contract['resource']['total_bytes']==len(raw),'TMF1 source contract changed')
    return raw,{'bytes':len(raw),'sha256':sha(raw)}

def build_family(repo):
    repo=Path(repo);manifest=json.loads(checked_file(repo,'assets/hd/manifest.json').read_text())
    require(PACK not in manifest['packs'],'TMF1 must stay outside HDR1 defaults')
    bundles=title_bundles(repo)
    require(len(bundles)==5,'Expected five exact prior startup resources')
    raw,receipt=build_resource(repo/SOURCE);bundles[FILENAME]=(raw,receipt)
    family={'schema':SCHEMA,'pack':PACK,'source':SOURCE,'source_manifest_sha256':SOURCE_MANIFEST_SHA256,'source_files':source_receipts(repo/SOURCE),'count':6,'menu_font_count':1,'startup_compatibility_count':5,'compatibility_source_pack':'startup-title-v1','files':{name:stamp for name,(_,stamp) in sorted(bundles.items())},'runtime_bytes':sum(len(data) for data,_ in bundles.values())}
    return bundles,family

def build_bundles(repo):
    repo=Path(repo);bundles,family=build_family(repo)
    manifest=json.loads(checked_file(repo,'assets/hd/manifest.json').read_text())
    require(manifest['startup_title_menu_v1']==family,'TMF1 family receipt changed')
    pack=repo/'assets/hd/packs'/PACK;require_inventory(pack,bundles,'Title menu runtime pack')
    for name,(raw,_) in bundles.items():require(checked_file(pack,name).read_bytes()==raw,'TMF1 runtime differs: '+name)
    return bundles

def verify_source_rebuild(repo):
    source=Path(repo)/SOURCE;source_receipts(source)
    with tempfile.TemporaryDirectory(prefix='tmf1-vector-rebuild-') as temporary:
        root=Path(temporary);relocated=root/'source';(relocated/'sources').mkdir(parents=True)
        for name in ('rebuild.py','contract.json','sources/menu-normal-vectors.json'):shutil.copyfile(checked_file(source,name),relocated/name)
        subprocess.run([sys.executable,str(relocated/'rebuild.py'),'--output',str(root/'rebuilt')],check=True,capture_output=True,text=True)
        outputs=json.loads(checked_file(source,'contract.json').read_text())['expected_outputs']
        require_inventory(root/'rebuilt',outputs,'TMF1 relocated outputs')
        for name,stamp in outputs.items():
            data=checked_file(root/'rebuilt',name).read_bytes()
            require({'bytes':len(data),'sha256':sha(data),'fnv64':fnv64(data)}==stamp,'TMF1 vector-only rebuild differs')
    return True

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify-rebuild',action='store_true');args=parser.parse_args()
    repo=Path(__file__).resolve().parent.parent;bundles=build_bundles(repo)
    if args.verify_rebuild:verify_source_rebuild(repo)
    print(json.dumps({'pack':PACK,'source_files':len(SOURCE_FILES),'runtime_files':len(bundles),'unchanged_compatibility_files':5,'menu_font_sha256':RESOURCE_SHA256,'runtime_bytes':sum(len(raw) for raw,_ in bundles.values()),'vector_only_rebuild':args.verify_rebuild},indent=2))
if __name__=='__main__':main()
