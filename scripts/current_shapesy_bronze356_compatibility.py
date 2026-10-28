"""One independent opaque ShapesY356 tile from one generated RGB master.

No source pixels, palette, native masks, neighbor repaint or alpha passthrough.
The immutable old28 contour family is not part of this authoring closure.
"""
import io,json,struct,zlib
from PIL import Image
from current_guided_compatibility import read,parse,sha
from build_newshf_hd import fnv
INPUT_ROOT='authoring-inputs/shapesy-bronze356'
ROOT='assets/hd/current-compat/shapesy-bronze356'
HEADER='src/current_shapesy_bronze356_hd_assets.h'
SELECTION='assets/hd/authoring/shapesy-bronze356.json'
MAPPING='packaging/current-shapesy-bronze356-compatibility.json'
SCHEMA='opentyrian-shapesy-bronze356-authoring-v1'
MAPPING_SCHEMA='opentyrian-shapesy-bronze356-compatibility-v1'
REVISION='current-single-source-shapesy-bronze356-opaque'
IDS=(356,)
ROLE=202
INPUTS=('raw/generated-master-03.png','registration-runtime.json')
RECIPE=dict(schema='opentyrian-shapesy-bronze356-registration-v1',master_size=[1161,1354],target_size=[192,224],crop=[0,0,1161,1354],anchor=[0,0],density=8,role=202,identity=2020356,resample='Pillow-LANCZOS',alpha='all255',native_data_needed=False)
def name(i):
    if type(i) is not int or i not in IDS:raise ValueError('Unknown bronze356 identity')
    return 'terrain-shapesy-356-8.hda'
def png(i):return INPUT_ROOT+'/derived/'+name(i).replace('.hda','.png')
def generated_paths():return {png(356)}
def input_paths(root):return {INPUT_ROOT+'/'+n for n in INPUTS}|{SELECTION}
def encode_png(im):
    out=io.BytesIO();im.save(out,format='PNG',optimize=False);return out.getvalue()

def master_image(raw):
    """Bounded, complete, single-frame CRC-valid RGB8 master, never alpha art."""
    if len(raw)>16*1024*1024 or raw[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Expected bounded bronze356 PNG')
    offset=8;kinds=[]
    while offset<len(raw):
        if offset+12>len(raw):raise ValueError('Truncated bronze356 PNG chunk')
        length=struct.unpack('>I',raw[offset:offset+4])[0];end=offset+12+length
        if end>len(raw):raise ValueError('Truncated bronze356 PNG data')
        kind=raw[offset+4:offset+8];body=raw[offset+8:end-4]
        if zlib.crc32(kind+body)&0xffffffff!=struct.unpack('>I',raw[end-4:end])[0]:raise ValueError('Bronze356 PNG CRC mismatch')
        if not kinds and (kind!=b'IHDR' or body!=struct.pack('>IIBBBBB',1161,1354,8,2,0,0,0)):raise ValueError('Unexpected bronze356 RGB8 dimensions')
        if kind in (b'acTL',b'fcTL',b'fdAT',b'tRNS') or (kind not in (b'IHDR',b'PLTE',b'IDAT',b'IEND') and not kind[0]&32):raise ValueError('Animated/transparent/unknown critical bronze356 PNG')
        kinds.append(kind);offset=end
        if kind==b'IEND':
            if length or offset!=len(raw):raise ValueError('Trailing bronze356 PNG data')
            break
    if kinds.count(b'IHDR')!=1 or kinds.count(b'IEND')!=1 or b'IDAT' not in kinds:raise ValueError('Incomplete bronze356 PNG')
    try:
        with Image.open(io.BytesIO(raw)) as im:im.verify()
        with Image.open(io.BytesIO(raw)) as im:
            if im.format!='PNG' or im.mode!='RGB' or im.size!=(1161,1354) or getattr(im,'n_frames',1)!=1:raise ValueError('Invalid bronze356 master')
            return im.copy()
    except (OSError,SyntaxError) as error:raise ValueError('Malformed bronze356 PNG') from error

def generate(root,raw):
    selected=parse(raw)
    if not isinstance(selected,dict) or set(selected)!={'schema','version','inputs'} or selected['schema']!=SCHEMA:raise ValueError('Invalid bronze356 selection')
    if not isinstance(selected['version'],str) or not 1<=len(selected['version'])<=128:raise ValueError('Invalid bronze356 version')
    if not isinstance(selected['inputs'],dict) or set(selected['inputs'])!={INPUT_ROOT+'/'+n for n in INPUTS}:raise ValueError('Invalid bronze356 input closure')
    for p,h in selected['inputs'].items():
        if not isinstance(h,str) or len(h)!=64 or sha(read(root,p))!=h:raise ValueError('Changed bronze356 input: '+p)
    recipe=parse(read(root,INPUT_ROOT+'/registration-runtime.json'))
    if json.dumps(recipe,sort_keys=True)!=json.dumps(RECIPE,sort_keys=True):raise ValueError('Fixed bronze356 registration changed')
    tile=master_image(read(root,INPUT_ROOT+'/raw/generated-master-03.png')).convert('RGBA').resize((192,224),Image.Resampling.LANCZOS)
    pixels=tile.tobytes()
    if any(a!=255 for a in pixels[3::4]):raise ValueError('Bronze356 must be fully opaque')
    data=encode_png(tile);blob=struct.pack('<4s6I',b'HDR1',2020356,8,24,28,0,0)+pixels
    row=dict(identity=2020356,base=356,source_bank='shapesy.dat',source_layer=1,source_path=ROOT+'/'+name(356),destination='assets/gameplay/'+name(356),source_png=png(356),source_png_sha256=sha(data),bytes=len(blob),sha256=sha(blob),payload_fnv=f'{fnv(pixels):016x}')
    return selected,{png(356):data},{356:blob},[row]

def payload_header(rows):
    if len(rows)!=1 or rows[0]['identity']!=2020356 or rows[0]['base']!=356:raise ValueError('Invalid bronze356 header rows')
    return ('/* Generated by build_current_shapesy_bronze356.py. */\n#ifndef CURRENT_SHAPESY_BRONZE356_HD_ASSETS_H\n#define CURRENT_SHAPESY_BRONZE356_HD_ASSETS_H\n#include <stdint.h>\n#define SHAPESY_BRONZE356_RGBA_FNV UINT64_C(0x'+rows[0]['payload_fnv']+')\n#endif\n').encode()

def load(root):
    selected,pngs,blobs,rows=generate(root,read(root,SELECTION))
    if parse(read(root,MAPPING))!=dict(schema=MAPPING_SCHEMA,selection=SELECTION,files=rows):raise ValueError('Bronze356 mapping differs')
    for p,b in pngs.items():
        if read(root,p)!=b:raise ValueError('Changed bronze356 derived PNG')
    if read(root,ROOT+'/'+name(356))!=blobs[356]:raise ValueError('Changed bronze356 transport')
    if read(root,HEADER)!=payload_header(rows):raise ValueError('Changed bronze356 payload header')
    return {r['destination']:r for r in rows}
