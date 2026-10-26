"""One approved bitmap master; deterministic, fixed-geometry shared enemy91."""
import io, json, struct
from PIL import Image
from current_plasma_projectile_compatibility import sha, parse, read, is_hash
from current_craft267_compatibility import path
IDS=(1490091,)
PAIRS=((1490091,8),)
SELECTION='assets/hd/authoring/projectile91-current.json'
MAPPING='packaging/current-projectile91-compatibility.json'
HEADER='src/current_projectile91_payload_pins.h'
ROOT='assets/hd/current-compat/projectile91'
INPUT_ROOT='authoring-inputs/projectile91-current'
SCHEMA='opentyrian-current-projectile91-authoring-v1'
CANDIDATE_SCHEMA='opentyrian-current-projectile91-candidate-v1'
PREVIEW=ROOT+'/projectile91-registered.png'
MASK='000000000000000000000000000011110000000111111000000111111000000111111000000111111000000111111000000111111000000111111000000111111000000011110000000011110000000001100000'
def name(identity,density=8):
    if type(identity) is not int or type(density) is not int or (identity,density) not in PAIRS:raise ValueError('Unknown projectile91 identity/density')
    return 'enemy-projectile91-91-8.hda'
def selection(root,raw,candidate=False):
    j=parse(raw)
    if not isinstance(j,dict) or set(j)!={'schema','version','masters'} or j['schema']!=(CANDIDATE_SCHEMA if candidate else SCHEMA):raise ValueError('Invalid projectile91 selection')
    if not isinstance(j['version'],str) or not 1<=len(j['version'])<=128:raise ValueError('Invalid version')
    if not isinstance(j['masters'],list) or len(j['masters'])!=1:raise ValueError('Expected one shared master')
    r=j['masters'][0]
    if set(r)!={'selector','source_png','source_sha256'} or type(r['selector']) is not int or r['selector']!=91 or r['source_png']!=INPUT_ROOT+'/projectile91-silver-v2-concept.png' or not is_hash(r['source_sha256']):raise ValueError('Invalid master identity')
    if path(root,r['source_png']).stat().st_nlink!=1 or sha(read(root,r['source_png']))!=r['source_sha256']:raise ValueError('Changed or hardlinked master')
    return j

def generate(root,raw,candidate=False):
    j=selection(root,raw,candidate)
    with Image.open(io.BytesIO(read(root,j['masters'][0]['source_png']))) as im:
        if im.format!='PNG' or im.mode!='RGBA' or im.size!=(1161,1354) or getattr(im,'n_frames',1)!=1:raise ValueError('Expected approved RGBA master dimensions')
        # Alpha-only dust cleanup; no painted/redrawn pixels. Resample in Pillow's
        # premultiplied-alpha RGBA path, preserving smooth inward support edges.
        box=im.getchannel('A').point(lambda v:255 if v>127 else 0).getbbox()
        if box!=(311,121,850,1305):raise ValueError('Master visible bounds changed; registration review required')
        crop=im.crop(box)
        crop.putalpha(crop.getchannel('A').point(lambda v:0 if v<=127 else v))
        scaled=crop.resize((44,96),Image.Resampling.BICUBIC)
    canvas=Image.new('RGBA',(96,112));canvas.alpha_composite(scaled,(26,16))
    payload=bytearray(canvas.tobytes())
    for y in range(112):
        for x in range(96):
            p=(y*96+x)*4
            if MASK[(y//8)*12+x//8]=='0' or not payload[p+3]:payload[p:p+4]=b'\0'*4
    preview=Image.frombytes('RGBA',(96,112),bytes(payload));buf=io.BytesIO();preview.save(buf,format='PNG',compress_level=9)
    blob=struct.pack('<4s6I',b'HDR1',IDS[0],8,12,14,0,0)+payload
    return dict(j,schema=SCHEMA),{PREVIEW:buf.getvalue()},{PAIRS[0]:blob}

def payload_header(pins):
    if set(pins)!=set(PAIRS):raise ValueError('Expected one payload pin')
    import re
    pin=pins[PAIRS[0]]
    if not isinstance(pin,str) or not re.fullmatch('[0-9a-f]{16}',pin):raise ValueError('Invalid pin')
    return ('/* Generated payload-only pin; geometry/role/source stay fixed. */\n#ifndef CURRENT_PROJECTILE91_PAYLOAD_PINS_H\n#define CURRENT_PROJECTILE91_PAYLOAD_PINS_H\n#define CURRENT_PROJECTILE91_PAYLOAD_FNV UINT64_C(0x'+pin+')\n#endif\n').encode()
def input_paths(root):
    j=selection(root,read(root,SELECTION))
    return {SELECTION,MAPPING,HEADER,PREVIEW,ROOT+'/'+name(IDS[0]),j['masters'][0]['source_png']}
def load(root):
    from build_current_art import fnv
    j,pngs,blobs=generate(root,read(root,SELECTION))
    blob=blobs[PAIRS[0]];source=ROOT+'/'+name(IDS[0]);dest='assets/gameplay/'+name(IDS[0])
    for p,b in {source:blob,**pngs}.items():
        if read(root,p)!=b:raise ValueError('Stale projectile91 derivative: '+p)
    row=dict(identity=IDS[0],density=8,source_path=source,destination=dest,sha256=sha(blob))
    expected=dict(schema='opentyrian-current-projectile91-compatibility-v1',selection=SELECTION,version=j['version'],files=[row])
    if parse(read(root,MAPPING))!=expected:raise ValueError('Stale projectile91 mapping')
    if read(root,HEADER)!=payload_header({PAIRS[0]:fnv(blob[28:])}):raise ValueError('Stale projectile91 pin')
    return {dest:row}
