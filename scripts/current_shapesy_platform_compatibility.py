"""Finite shapesY platform resource contract; original water remains native.

Only the generated component master supplies creative pixels. Original material
geometry is immutable. Rebuilds require no original game data or Git history.
"""
import importlib.util
import io
import json
import struct
from pathlib import Path
from current_guided_compatibility import read, parse, sha
from build_newshf_hd import fnv

INPUT_ROOT = 'authoring-inputs/shapesy-platform-current'
RECIPE_MODULE = 'prototype/build-shapesy-platform-art.py'
HEADER = 'src/current_shapesy_platform_hd_assets.h'
SELECTION = 'assets/hd/authoring/shapesy-platform-current.json'
MAPPING = 'packaging/current-shapesy-platform-compatibility.json'
SCHEMA = 'opentyrian-shapesy-platform-authoring-v1'
REVISION = 'current-single-source-shapesy-platform-28'
ROLE = 202
IDS = (321, 322, 323, 324, 325, 326, 331, 332, 333, 334, 336, 341, 342, 343, 346, 351, 352, 353, 354, 361, 362, 363, 364, 365, 374, 375, 384, 385)
# SHA256 of672 binary source-water semantic cells, not palette/RGB data.
WATER_MASK_SHA256 = {321: '3ebfe9f63c8703ad9bf664972625f6228d486d33cc06df9a1745cabd5e7f154c', 322: '6ba2114245a865374ace77bf738adc33b38affa58744346f722fe537216caa5e', 323: '7cdd48d4cf6e6b033a2fe784ef45a62d8e3945635954117917449f96b1faddcd', 324: 'f792b7f860bb94e55760c0daa727d58d13ba96276a2b52f29a645c8e08e73ec1', 325: 'f792b7f860bb94e55760c0daa727d58d13ba96276a2b52f29a645c8e08e73ec1', 326: 'f792b7f860bb94e55760c0daa727d58d13ba96276a2b52f29a645c8e08e73ec1', 331: '083c199d3a8b4b05e455af03fa2c79756c83fb0106b3aeaa563efe615f370471', 332: 'f792b7f860bb94e55760c0daa727d58d13ba96276a2b52f29a645c8e08e73ec1', 333: '9c54344c6fd67a7b490e6190359c42e2dd8c56adc7a47c57bd0a044bb56864c9', 334: 'f792b7f860bb94e55760c0daa727d58d13ba96276a2b52f29a645c8e08e73ec1', 336: 'f792b7f860bb94e55760c0daa727d58d13ba96276a2b52f29a645c8e08e73ec1', 341: '5e0d2f98bab02ce77d53ea4b66f7d7affd2c549e61bb7c3a5504824f1876a621', 342: 'f792b7f860bb94e55760c0daa727d58d13ba96276a2b52f29a645c8e08e73ec1', 343: '8f96a835f8b22155e4faa3727d8ee549fc85b9f9de5e904607ae4a21c5e4f9e1', 346: '87827da861efd66510043dc2d08f77f5e03170aff54708259bb9c048f097b305', 351: '98d305e41241487103ca468bf1a8e3c0f91599134779298fec5ff8ff5fb5e907', 352: 'f792b7f860bb94e55760c0daa727d58d13ba96276a2b52f29a645c8e08e73ec1', 353: '3d0925a9e4034df927c36ee26d4e55420ed7530434710fc2261b78692b4aa81f', 354: '8617d7286994e007ec76cd3bae2648e70a64d7543c050040ff565fd40f0482a0', 361: 'cfa620f35ca488fc8814ecda58ee4ec9676a8ee8c78cb79876fac0e521e455fb', 362: '87827da861efd66510043dc2d08f77f5e03170aff54708259bb9c048f097b305', 363: 'f6c57a854985a0d7868f4675e6d61db043c5339d104749001feb358f70f928f8', 364: 'e3db9a1a8ab4520238ece286e43132d3543d83e73969292b14ea82d7501f78c7', 365: '0bb78d3232d1b99f25da28337e3a4fd3fa3abd334b450af0fbff19db2d3aaa86', 374: 'f792b7f860bb94e55760c0daa727d58d13ba96276a2b52f29a645c8e08e73ec1', 375: '5cac7e669ff7f49fa8dc2242b022478cf5fd128dd351a72f067bdac864eb2f04', 384: '8617d7286994e007ec76cd3bae2648e70a64d7543c050040ff565fd40f0482a0', 385: 'ea1d9e24e7f9388f133c45fd6b0b679f05d507dac4e330d99be4f92f46c8026e'}
PACKS = ('packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test',
         'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test')
ROOT = 'assets/hd/packs/' + PACKS[0]

def name(i): return f'terrain-shapesy-{i}-8.hda'
def png(i): return f'assets/hd/source/terrain-shapesy-{i}-8.png'
def generated_paths(): return {png(i) for i in IDS}
def recipe(root):
    path=Path(root)/RECIPE_MODULE
    read(root, RECIPE_MODULE) # regular/contained path check before execution
    spec=importlib.util.spec_from_file_location('shapesy_platform_art',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def input_paths(root):
    result=set()
    for p in recipe(root).input_paths(Path(root)):
        p=Path(p)
        result.add(p.relative_to(root).as_posix() if p.is_absolute() else p.as_posix())
    assert result and all(p.startswith(INPUT_ROOT+'/') for p in result)
    return result | {RECIPE_MODULE, SELECTION}

def encode_png(im):
    out=io.BytesIO();im.save(out,format='PNG',optimize=False);return out.getvalue()

def check_pixels(i,im):
    if im.mode!='RGBA' or im.size!=(192,224):raise ValueError('Incorrect Y format/density')
    pixels=im.load();mask=bytearray()
    for y in range(28):
        for x in range(24):
            alpha=pixels[x*8,y*8][3]
            if alpha not in (0,255):raise ValueError('Nonbinary Y alpha')
            mask.append(255 if alpha==0 else 0)
            for sy in range(y*8,y*8+8):
                for sx in range(x*8,x*8+8):
                    value=pixels[sx,sy]
                    if value[3]!=alpha or (alpha==0 and value!=(0,0,0,0)):
                        raise ValueError('Water geometry or transparent RGB changed')
                    if i==333 and x==9 and y==9 and value!=(0,0,0,255):
                        raise ValueError('Original zero333 black-cell semantics changed')
    if sha(bytes(mask))!=WATER_MASK_SHA256[i]:raise ValueError('Immutable source-water mask changed')

def generate(root,raw):
    selected=parse(raw)
    if set(selected)!={'schema','version','inputs'} or selected['schema']!=SCHEMA:
        raise ValueError('Invalid Y selection schema')
    if not isinstance(selected['version'],str) or not 1<=len(selected['version'])<=128:
        raise ValueError('Invalid Y version')
    expected=input_paths(root)-{SELECTION}
    if set(selected['inputs'])!=expected:raise ValueError('Y input closure changed')
    for p,digest in selected['inputs'].items():
        if sha(read(root,p))!=digest:raise ValueError('Changed Y input: '+p)
    images=recipe(root).generate(Path(root))
    if set(images)!=set(IDS):raise ValueError('Y family must be exact28')
    pngs,blobs,rows={},{},[]
    for i in IDS:
        im=images[i];check_pixels(i,im);data=encode_png(im);pngs[png(i)]=data
        raw=struct.pack('<4s6I',b'HDR1',ROLE*10000+i,8,24,28,0,0)+im.tobytes()
        blobs[i]=raw
        rows.append(dict(identity=ROLE*10000+i,base=i,source_bank='shapesy.dat',
          source_path=ROOT+'/'+name(i),destination='assets/gameplay/'+name(i),
          source_png=png(i),source_png_sha256=sha(data),bytes=len(raw),sha256=sha(raw),
          payload_fnv=f'{fnv(raw[28:]):016x}'))
    return selected,pngs,blobs,rows

def payload_header(rows):
    if tuple(r['base'] for r in rows)!=IDS:raise ValueError('Invalid Y header order')
    entries='\n'.join(f' UINT64_C(0x{r["payload_fnv"]}), /* {r["base"]} */' for r in rows)
    return ('/* Generated by build_current_shapesy_platform.py. */\n'
      '#ifndef CURRENT_SHAPESY_PLATFORM_HD_ASSETS_H\n#define CURRENT_SHAPESY_PLATFORM_HD_ASSETS_H\n'
      '#include <stdint.h>\nstatic const uint64_t shapesy_rgba_pins[28] = {\n'+entries+
      '\n};\n#endif\n').encode()

def load(root):
    selected,pngs,blobs,rows=generate(root,read(root,SELECTION))
    if parse(read(root,MAPPING))!=dict(schema='opentyrian-shapesy-platform-compatibility-v1',selection=SELECTION,files=rows):
        raise ValueError('Y mapping differs from independently derived resources')
    for p,b in pngs.items():
        if read(root,p)!=b:raise ValueError('Changed Y PNG: '+p)
    for pack in PACKS:
        for i,b in blobs.items():
            if read(root,'assets/hd/packs/'+pack+'/'+name(i))!=b:raise ValueError('Changed Y transport')
    if read(root,HEADER)!=payload_header(rows):raise ValueError('Changed Y payload header')
    catalog=json.loads(read(root,'assets/hd/manifest.json'))
    for pack in PACKS:
        for row in rows:
            i=row['base'];expected=dict(sha256=row['sha256'],header_u32=[ROLE*10000+i,8,24,28,0,0],source_png=png(i),source_png_sha256=row['source_png_sha256'])
            if catalog['packs'][pack]['files'].get(name(i))!=expected:raise ValueError('Y catalog entry changed')
    return {r['destination']:r for r in rows}
