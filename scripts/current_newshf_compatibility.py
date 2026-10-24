"""Two fixed three-pose masters for current NEWSHF163/167; frozen168 unchanged.

Physical source columns, not inferred velocity directions or automatic animation.
The legacy nine-pose contract remains independently validated and immutable.
"""
import io
import json
import struct
from PIL import Image
import build_newshf_hd as legacy
from current_guided_compatibility import read, parse, sha, image, is_hash

IDS = legacy.IDS
EDIT_IDS = IDS[:6]
PAIRS = tuple((i, 8) for i in EDIT_IDS)
SELECTORS = (163,167)
# Exact public fca48c7 legacy evidence; current edits never rewrite these.
LEGACY_SHA256 = {'assets/hd/newshf-v1/manifest.json': '64a8df170669c18b24b1ecc9c518e3e7adbea31842c9b75eb72fac6e0bc627f4', 'assets/hd/newshf-v1/newshf-role2100000-8.hda': 'bccab3ffa0e2743cd8e12b45101ab18ecc5ca22745fcd430701da2c2fda43420', 'assets/hd/newshf-v1/newshf-role2100001-8.hda': 'fb326361a33883f7374732c3b4cea3be0f4e7cdfa298daefeed3a13b815f0807', 'assets/hd/newshf-v1/newshf-role2100002-8.hda': '6c311946d3d92ff2bca8ed6aa3874eb3acbcc694d2db6baa6b82b86c3e25c684', 'assets/hd/newshf-v1/newshf-role2100003-8.hda': '36f3e6eb60084635ecd38f29b437a9eedf014a8e7a19e8bcfed38f00bc052f23', 'assets/hd/newshf-v1/newshf-role2100004-8.hda': '9a39daa716d85a5fb55534692a61cb09649cb59f24b2ad4a50b1dbb01d1b480c', 'assets/hd/newshf-v1/newshf-role2100005-8.hda': '8e3cff75572bbac1f830a8c50e060473cea14a170b5d10afea8567c92f2917ed', 'assets/hd/newshf-v1/newshf-role2100006-8.hda': '1954ceba77e72e099d3b92b8f6bc78c14c061ee28dfdd0cec037ca43e62b2c49', 'assets/hd/newshf-v1/newshf-role2100007-8.hda': '1bc2d7b6f83a438ae167a0776481d60ac04fa19b181945499585fbb08ccc13c5', 'assets/hd/newshf-v1/newshf-role2100008-8.hda': '35a17d97f319ae97dcbfcf8c1545f66048c9c27a5545c2f6a9ac05f2ba4c97dd', 'authoring-inputs/enemies/newshf-phase-a/enemy-163-v1-bbox-fit-base123.png': 'f5fb995632edde27643bd462ffce52a76639c427d0229aeb97d176913878754d', 'authoring-inputs/enemies/newshf-phase-a/enemy-163-v1-bbox-fit-base125.png': '8231cf3832460c679dfef3743b0f17604579e0f7df400f7deece96cdb64e684d', 'authoring-inputs/enemies/newshf-phase-a/enemy-163-v1-bbox-fit-base127.png': '2a286657eaf91e7404bb3c3ccab77974c8d2c5060ab8a6961c4ab1ef7601b33a', 'authoring-inputs/enemies/newshf-phase-a/enemy-167-v1-bbox-fit-base1.png': '076b9106aebc39c1c28349abae95fc014d3c2e8dff3813077912a27bc761a25e', 'authoring-inputs/enemies/newshf-phase-a/enemy-167-v1-bbox-fit-base3.png': '931556bcf925637217e1039f063b043836abd568469a736aa5542fbb358e277f', 'authoring-inputs/enemies/newshf-phase-a/enemy-167-v1-bbox-fit-base5.png': '74dbf41d55eccdc35f50d913efd9871ab26e5d0b57f81e2a9cc985607154c7c7', 'authoring-inputs/enemies/newshf-phase-a/enemy-168-v1-bbox-fit-base17.png': 'e02d8f0b3c622aa7fd846406f5df30dc6ac0a4af1eed70a1103fec19dac1955b', 'authoring-inputs/enemies/newshf-phase-a/enemy-168-v1-bbox-fit-base55.png': '9cfc7d7b8c2b20917bd58898cf21fbb76ad2841e371158f37316aab3f8818e70', 'authoring-inputs/enemies/newshf-phase-a/enemy-168-v1-bbox-fit-base93.png': 'c0f68d1715b31fa314f9ba65dbb910bc7c7edc3f6ad4bb4f2958da032e6f61b5', 'authoring-inputs/enemies/newshf-phase-a/manifest.json': '474c884e6f007c3270e2d05c52b9bafc76cff29e393775ae8b7d14fa284e7bb3', 'authoring-inputs/enemies/newshf-phase-a/provenance.json': '13c607ee442593bdcd9c2f9752526c3692429419568348218e1b6ca3ef64c024', 'authoring-inputs/enemies/newshf-phase-a/report.json': 'a711013892967aef697eed61536621ecfd836a394ac6be2615d741ce96ef1936', 'src/newshf_hd_assets.h': 'c9552ffee0610c7ece607dce0e20a414818f143911d2a5e42bd21b5fd4a8d129'}
SELECTION = 'assets/hd/authoring/newshf-current.json'
MAPPING = 'packaging/current-newshf-compatibility.json'
HEADER = 'src/current_newshf_hd_assets.h'
ROOT = 'assets/hd/current-compat/newshf'
INPUT_ROOT = 'authoring-inputs/newshf-current'
SCHEMA = 'opentyrian-current-newshf-authoring-v1'
CANDIDATE_SCHEMA = 'opentyrian-current-newshf-candidate-v1'
RECIPE = {'schema':'newshf-fixed-two-master-recipe-v1','canvas':[192,224],
 'logical_size':[24,28],'density':8,'anchor':[6,7],
 'resample':'Pillow-LANCZOS-straight-RGBA-paste-without-mask',
 'alpha':'binary-threshold-128-before-and-after-resize-zero-transparent-rgb',
 'relationship':'two-independent-three-physical-column-masters-no-direction-inference',
 'masters':[{'selector':163,'source_size':[2011,782]}, {'selector':167,'source_size':[2012,782]}],
 'pieces':[
 {'selector':163,'identity':2100000,'base':125,'crop':[65,8,640,773],'size':[168,224],'xy':[16,0]},
 {'selector':163,'identity':2100001,'base':123,'crop':[755,8,1295,773],'size':[152,224],'xy':[24,0]},
 {'selector':163,'identity':2100002,'base':127,'crop':[1457,8,1994,773],'size':[152,224],'xy':[24,0]},
 {'selector':167,'identity':2100003,'base':3,'crop':[181,43,614,696],'size':[136,200],'xy':[40,8]},
 {'selector':167,'identity':2100004,'base':1,'crop':[814,44,1208,695],'size':[120,200],'xy':[48,8]},
 {'selector':167,'identity':2100005,'base':5,'crop':[1421,44,1823,695],'size':[120,200],'xy':[48,8]}]}


def name(identity):
    return legacy.name(identity)


def png(identity):
    if type(identity) is not int or identity not in EDIT_IDS:
        raise ValueError('Unknown current aircraft role')
    return INPUT_ROOT + '/derived/' + name(identity).removesuffix('.hda') + '.png'


def generated_paths():
    return {png(i) for i in EDIT_IDS}


def selection(root, raw, candidate=False):
    selected=parse(raw)
    keys={'schema','version','masters','recipe'} | (set() if candidate else {'resources'})
    if not isinstance(selected,dict) or set(selected)!=keys or selected['schema']!=(CANDIDATE_SCHEMA if candidate else SCHEMA):
        raise ValueError('Invalid current aircraft selection schema/fields')
    if not isinstance(selected['version'],str) or not 1<=len(selected['version'])<=128:
        raise ValueError('Invalid current aircraft version')
    if not isinstance(selected['masters'],list) or len(selected['masters'])!=2:
        raise ValueError('Expected two aircraft masters')
    for selector,row in zip(SELECTORS,selected['masters']):
        if (not isinstance(row,dict) or set(row)!={'selector','source_png','source_sha256'} or
            type(row['selector']) is not int or row['selector']!=selector or
            row['source_png']!=INPUT_ROOT+f'/master-{selector}.png' or not is_hash(row['source_sha256']) or
            sha(read(root,row['source_png']))!=row['source_sha256']):
            raise ValueError('Invalid/changed aircraft master identity/path/hash/order')
    row=selected['recipe']
    if (not isinstance(row,dict) or set(row)!={'path','sha256'} or row['path']!=INPUT_ROOT+'/recipe.json' or
        not is_hash(row['sha256']) or sha(read(root,row['path'],128*1024))!=row['sha256']):
        raise ValueError('Invalid/changed aircraft recipe record')
    if not candidate:
        if not isinstance(selected['resources'],list) or len(selected['resources'])!=6:
            raise ValueError('Expected six derived aircraft poses')
        for identity,row in zip(EDIT_IDS,selected['resources']):
            if (not isinstance(row,dict) or set(row)!={'identity','density','source_png','source_sha256'} or
                type(row['identity']) is not int or row['identity']!=identity or type(row['density']) is not int or
                row['density']!=8 or row['source_png']!=png(identity) or not is_hash(row['source_sha256'])):
                raise ValueError('Invalid derived aircraft role/density/path/order/hash')
    return selected


def threshold(im):
    raw=bytearray(im.tobytes())
    for offset in range(0,len(raw),4):
        if raw[offset+3]<128:
            raw[offset:offset+4]=b'\0\0\0\0'
        else:
            raw[offset+3]=255
    return Image.frombytes('RGBA',im.size,bytes(raw))


def generate(root,raw,candidate=False):
    selected=selection(root,raw,candidate)
    if json.dumps(parse(read(root,selected['recipe']['path'],128*1024)),sort_keys=True)!=json.dumps(RECIPE,sort_keys=True):
        raise ValueError('Fixed aircraft recipe identity/geometry/alpha changed')
    masters={row['selector']:threshold(image(read(root,row['source_png']),tuple(spec['source_size'])))
        for row,spec in zip(selected['masters'],RECIPE['masters'])}
    pngs,blobs,rows={},{},[]
    for ordinal,spec in enumerate(RECIPE['pieces']):
        piece=Image.new('RGBA',(192,224))
        crop=masters[spec['selector']].crop(tuple(spec['crop'])).resize(tuple(spec['size']),Image.Resampling.LANCZOS)
        piece.paste(threshold(crop),tuple(spec['xy']))
        alpha=set(piece.getchannel('A').tobytes())
        if alpha!={0,255}:
            raise ValueError('Aircraft pose must have binary nonempty foreground/background')
        stream=io.BytesIO();piece.save(stream,format='PNG',optimize=False)
        encoded=stream.getvalue();identity=spec['identity'];source=png(identity)
        if not candidate:
            current=read(root,source)
            if sha(current)!=selected['resources'][ordinal]['source_sha256'] or current!=encoded:
                raise ValueError('Derived aircraft PNG differs from master and fixed recipe: '+source)
        pngs[source]=encoded
        rows.append(dict(identity=identity,density=8,source_png=source,source_sha256=sha(encoded)))
        blobs[identity]=struct.pack('<4s6I',b'HDR1',identity,8,24,28,6,7)+piece.tobytes()
    if len({blob[28:] for blob in blobs.values()})!=6:
        raise ValueError('Duplicate current aircraft pose pixels')
    return dict(selected,schema=SCHEMA,resources=rows),pngs,blobs


def resource_rows(root,selected,blobs):
    for relative,digest in LEGACY_SHA256.items():
        if sha(read(root,relative))!=digest:
            raise ValueError('Frozen NEWSHF legacy evidence changed: '+relative)
    old=legacy.load(root)
    rows=[]
    for identity,(record,base) in zip(IDS,legacy.PAIRS):
        destination='assets/global/newshf/'+name(identity)
        if identity in EDIT_IDS:
            raw=blobs[identity]
            row=dict(identity=identity,record=record,base=base,source_path=ROOT+'/'+name(identity),
                destination=destination,source_png=png(identity),source_png_sha256=selected['resources'][identity-EDIT_IDS[0]]['source_sha256'],
                bytes=len(raw),sha256=sha(raw),payload_fnv=f'{legacy.fnv(raw[28:]):016x}')
        else:
            row=old[destination]
        rows.append(row)
    return rows


def payload_header(rows):
    if len(rows)!=9 or tuple(row['identity'] for row in rows)!=IDS:
        raise ValueError('Expected nine aircraft header rows')
    declarations=[f' {{{r["identity"]}u,{r["bytes"]}u,8u,24u,28u,6,7,"newshf/{name(r["identity"])}",UINT64_C(0x{r["payload_fnv"]})}},' for r in rows]
    return ('/* Generated by scripts/build_current_newshf.py; six current poses and three frozen168 poses. */\n'
        '#ifndef CURRENT_NEWSHF_HD_ASSETS_H\n#define CURRENT_NEWSHF_HD_ASSETS_H\n'
        '#include "global_asset_registry.h"\n'
        'enum { NEWSHF_HD_RESOURCE_COUNT = 9 };\n'
        'static const GlobalAssetResource newshf_hd_resources[NEWSHF_HD_RESOURCE_COUNT] = {\n'
        +'\n'.join(declarations)+'\n};\n#endif\n').encode()


def input_paths(root):
    selected=selection(root,read(root,SELECTION,128*1024))
    return legacy.input_paths(root) | {SELECTION,MAPPING,HEADER,selected['recipe']['path']} | generated_paths() | {
        row['source_png'] for row in selected['masters']} | {ROOT+'/'+name(i) for i in EDIT_IDS}


def load(root):
    selected,_,blobs=generate(root,read(root,SELECTION,128*1024))
    rows=resource_rows(root,selected,blobs)
    for identity,blob in blobs.items():
        if read(root,ROOT+'/'+name(identity))!=blob:
            raise ValueError('Current aircraft HDA differs from master and recipe')
    expected=dict(schema='opentyrian-current-newshf-compatibility-v1',selection=SELECTION,version=selected['version'],files=rows)
    if json.dumps(parse(read(root,MAPPING,128*1024)),sort_keys=True)!=json.dumps(expected,sort_keys=True):
        raise ValueError('Stale current aircraft mapping')
    if read(root,HEADER)!=payload_header(rows):
        raise ValueError('Stale current aircraft header')
    for relative,expected_names in ((ROOT,{name(i) for i in EDIT_IDS}),(INPUT_ROOT+'/derived',{png(i).split('/')[-1] for i in EDIT_IDS})):
        folder=root/relative
        if {p.name for p in folder.iterdir()}!=expected_names:
            raise ValueError('Unexpected current aircraft output member')
    return {row['destination']:row for row in rows}
