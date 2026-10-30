"""Three closed generated sources for finite normal-bank8 enemy transports.

The v2 epoch pins exact per-cell alpha matrices, including six selected101
alpha-zero native cells. It does not weaken the native mask/callback contract
or retrospectively qualify the old shared-master/every-cell>=200 epoch.
Package completeness and C runtime missing-member independence are distinct.
"""
import io
import json
import re
import struct
from PIL import Image, __version__ as PILLOW_VERSION
from current_plasma_projectile_compatibility import sha, parse, read, is_hash
from current_craft267_compatibility import path

SELECTORS=(101,120,139)
IDS=(1520101,1520120,1520139)
PAIRS=tuple((i,8) for i in IDS)
SELECTION='assets/hd/authoring/projectile-blue-triplet-current.json'
MAPPING='packaging/current-projectile-blue-triplet-compatibility.json'
HEADER='src/current_projectile_blue_triplet_payload_pins.h'
ROOT='assets/hd/current-compat/projectile-blue-triplet'
# Historical transport tag retained to avoid changing unrelated package rows.
# Each member has one source; v2 SCHEMA (not this tag) closes the three records.
REVISION='current-single-source-projectile-blue-triplet'
INPUT_ROOT='authoring-inputs/projectile-blue-triplet-current'
REGISTRATION=INPUT_ROOT+'/registration.json'
COVERAGE=INPUT_ROOT+'/coverage-contract.json'
SCHEMA='opentyrian-current-projectile-blue-triplet-authoring-v2'
CANDIDATE_SCHEMA='opentyrian-current-projectile-blue-triplet-candidate-v2'
MAPPING_SCHEMA='opentyrian-current-projectile-blue-triplet-compatibility-v2'
MASKS={101:'001111111100'+'111111111111'*13,
       120:'111111111111'*14,
       139:'111111111111'*3+'011111111110'*5+'001111111100'*4+'000111111000'*2}
DISTRIBUTIONS={101:(132,26,6),120:(107,61,0),139:(130,0,0)}
ZERO_CELLS_101=((12,0),(12,11),(13,0),(13,1),(13,10),(13,11))
APPROVED_PNG_SHA256={101:'d93831b3425b6fdef5f33ef11ce56fac9f06c8b6fdaf2c4339f7bd892df98b00',
                    120:'251b5e46688cd6d3da9023a001c8b88e2f8875d48c01f6c171dfe8b650f31bc3',
                    139:'f8e674afbea3148ed6b72f703c68b935e33731f35723da902caa0ff5000d162c'}
SOURCES=({'selector': 101, 'source_png': 'authoring-inputs/projectile-blue-triplet-current/raw/generated-master-101-v6.png', 'source_sha256': '67f727657296f4c9408e310033b4afe7603b4195f3b738115c8cd397a5b29a00', 'source_size': [1160, 1355], 'crop': [0, 0, 1160, 1355], 'png_compress_level': 6}, {'selector': 120, 'source_png': 'authoring-inputs/projectile-blue-triplet-current/raw/generated-master-120-v2.png', 'source_sha256': '1ca347f17ebe894434d0b55698f175bd1dd345b58c87ec3ae0722641b4db3c1b', 'source_size': [1160, 1355], 'crop': [350, 0, 810, 1355], 'png_compress_level': 6}, {'selector': 139, 'source_png': 'authoring-inputs/projectile-blue-triplet-current/raw/generated-master-01.png', 'source_sha256': '0904cafbedf92ca30f3bc132a7f39eb8febc44a69e4cbdac6f85ff00c511ca57', 'source_size': [725, 2168], 'crop': [224, 1550, 502, 1870], 'png_compress_level': 9})
REGISTRATION_SHA256='193e04f50c741211b6bad41229ff3a192679335b620dadbed0cb8878336f7119'
COVERAGE_SHA256='c667b52db7c28fd8d9ee96ffd0531a16b5cb4875c05995c2026bf381ab38d1c9'
CROPS={r["selector"]:tuple(r["crop"]) for r in SOURCES}
def name(identity,density=8):
    if type(identity) is not int or type(density) is not int or (identity,density) not in PAIRS:
        raise ValueError('Unknown blue-triplet identity/density')
    return f'enemy-projectile-blue-triplet-{identity-1520000}-{density}.hda'

def png(identity,density=8):
    name(identity,density)
    return ROOT+f'/projectile-blue-triplet-{identity-1520000}-registered.png'


def single_input(root,name,expected):
    raw=read(root,name)
    if path(root,name).stat().st_nlink!=1 or sha(raw)!=expected:
        raise ValueError('Changed or hardlinked fixed input: '+name)
    return raw

def coverage(root):
    return parse(single_input(root,COVERAGE,COVERAGE_SHA256))

def selection(root,raw,candidate=False):
    if type(candidate) is not bool:raise ValueError('Expected candidate flag boolean')
    j=parse(raw)
    if not isinstance(j,dict) or set(j)!={'schema','version','sources'} or j['schema']!=(CANDIDATE_SCHEMA if candidate else SCHEMA):
        raise ValueError('Invalid v2 blue-triplet selection')
    if not isinstance(j['version'],str) or not 1<=len(j['version'])<=128:raise ValueError('Invalid version')
    if not isinstance(j['sources'],list) or len(j['sources'])!=3:raise ValueError('Expected exactly three finite source records')
    for r,expected in zip(j['sources'],SOURCES):
        if not isinstance(r,dict) or set(r)!=set(expected):raise ValueError('Invalid source fields')
        if (type(r['selector']) is not int or type(r['png_compress_level']) is not int or
                not isinstance(r['source_png'],str) or not is_hash(r['source_sha256']) or
                not isinstance(r['source_size'],list) or len(r['source_size'])!=2 or
                not isinstance(r['crop'],list) or len(r['crop'])!=4 or
                any(type(v) is not int for v in r['source_size']+r['crop']) or r!=expected):
            raise ValueError('Changed finite source selector/path/hash/size/crop/encoding')
        single_input(root,r['source_png'],r['source_sha256'])
    single_input(root,REGISTRATION,REGISTRATION_SHA256)
    coverage(root)
    return j

def validate_payload(root,selector,payload,contract=None):
    if type(selector) is not int or selector not in SELECTORS or len(payload)!=43008:
        raise ValueError('Invalid finite payload')
    m=(coverage(root) if contract is None else contract)['members'][str(selector)]
    mask=MASKS[selector];maximum=[];zero=[]
    for y in range(112):
        for x in range(96):
            p=(y*96+x)*4;pixel=payload[p:p+4]
            if (mask[(y//8)*12+x//8]=='0' or pixel[3]==0) and any(pixel):
                raise ValueError('Noncanonical alpha-zero or outside-native RGBA')
    for y in range(14):
        row=[]
        for x in range(12):
            a=max(payload[((y*8+dy)*96+x*8+dx)*4+3] for dy in range(8) for dx in range(8));row.append(a)
            if mask[y*12+x]=='1' and a==0:zero.append([y,x])
        maximum.append(row)
    used=[maximum[y][x] for y in range(14) for x in range(12) if mask[y*12+x]=='1']
    dist=(sum(a>=200 for a in used),sum(0<a<200 for a in used),used.count(0))
    expected_zero=[list(v) for v in ZERO_CELLS_101] if selector==101 else []
    if (m['native_mask']!=mask or m['native_occupied_cells']!=len(used) or
            maximum!=m['max_alpha_per_native_cell'] or dist!=DISTRIBUTIONS[selector] or
            zero!=expected_zero or zero!=m['fully_transparent_native_cells'] or
            sha(payload)!=m['payload_sha256'] or list(payload[3:384:4])!=m['first_row_alpha'] or
            list(payload[-381::4])!=m['last_row_alpha']):
        raise ValueError('Changed exact selected alpha matrix/distribution/payload/endpoints')
    return maximum

def generate(root,raw,candidate=False):
    j=selection(root,raw,candidate);pngs={};blobs={};contract=coverage(root)
    if PILLOW_VERSION!='12.3.0':raise ValueError('Fixed Pillow12.3.0 registration required')
    for r in j['sources']:
        selector=r['selector'];identity=1520000+selector
        with Image.open(io.BytesIO(single_input(root,r['source_png'],r['source_sha256']))) as im:
            if im.format!='PNG' or im.mode!='RGBA' or list(im.size)!=r['source_size'] or getattr(im,'n_frames',1)!=1:
                raise ValueError('Changed approved RGBA source dimensions')
            # Generated RGB/alpha only; exact fixed crop, no fitting, fill,
            # alpha promotion, edge copying, or original-color sampling.
            tile=im.crop(tuple(r['crop'])).resize((96,112),Image.Resampling.LANCZOS)
            payload=bytearray(tile.tobytes());mask=MASKS[selector]
            for y in range(112):
                for x in range(96):
                    p=(y*96+x)*4
                    if mask[(y//8)*12+x//8]=='0' or not payload[p+3]:payload[p:p+4]=b'\0'*4
            validate_payload(root,selector,payload,contract)
            out=Image.frombytes('RGBA',(96,112),bytes(payload));buf=io.BytesIO();out.save(buf,format='PNG',compress_level=r['png_compress_level'])
            encoded=buf.getvalue()
            if sha(encoded)!=APPROVED_PNG_SHA256[selector]:raise ValueError('Changed selected generated derivative')
            blob=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0)+payload
            if sha(blob)!=contract['members'][str(selector)]['hda_sha256']:raise ValueError('Changed selected HDA')
            pngs[png(identity)]=encoded;blobs[(identity,8)]=blob
    return dict(j,schema=SCHEMA),pngs,blobs

def payload_header(pins):
    if not isinstance(pins,dict) or set(pins)!=set(PAIRS):raise ValueError('Expected three independent payload pins')
    lines=['/* Generated payload-only pins; fixed role/source/geometry stay separate. */',
           '#ifndef CURRENT_PROJECTILE_BLUE_TRIPLET_PAYLOAD_PINS_H',
           '#define CURRENT_PROJECTILE_BLUE_TRIPLET_PAYLOAD_PINS_H']
    for identity,density in PAIRS:
        pin=pins[(identity,density)]
        if not isinstance(pin,str) or not re.fullmatch('[0-9a-f]{16}',pin):raise ValueError('Invalid blue-triplet pin')
        lines.append(f'#define CURRENT_PROJECTILE_BLUE_TRIPLET_{identity}_PAYLOAD_FNV UINT64_C(0x{pin})')
    return ('\n'.join(lines+['#endif',''])).encode()

def rows_for(selected,blobs):
    return [dict(identity=identity,density=density,source_path=ROOT+'/'+name(identity,density),
                 destination='assets/gameplay/'+name(identity,density),sha256=sha(blobs[(identity,density)]))
            for identity,density in PAIRS]

def input_paths(root):
    selection(root,read(root,SELECTION))
    return {SELECTION,MAPPING,HEADER,REGISTRATION,COVERAGE}|{r['source_png'] for r in SOURCES}|{png(i,d) for i,d in PAIRS}|{ROOT+'/'+name(i,d) for i,d in PAIRS}

def load(root):
    from build_current_art import fnv
    selected,pngs,blobs=generate(root,read(root,SELECTION));rows=rows_for(selected,blobs)
    outputs={**pngs,**{r['source_path']:blobs[(r['identity'],r['density'])] for r in rows}}
    for p,b in outputs.items():
        if read(root,p)!=b:raise ValueError('Stale blue-triplet derivative: '+p)
    expected=dict(schema=MAPPING_SCHEMA,selection=SELECTION,version=selected['version'],files=rows)
    if parse(read(root,MAPPING))!=expected:raise ValueError('Stale blue-triplet mapping')
    if read(root,HEADER)!=payload_header({pair:fnv(blob[28:]) for pair,blob in blobs.items()}):
        raise ValueError('Stale blue-triplet independent pins')
    return {r['destination']:r for r in rows}

def validate_runtime_rows(root,manifest,required=False):
    """Closed alias-aware three-piece package selection, not C runtime readiness."""
    if type(required) is not bool or not isinstance(manifest,dict) or not isinstance(manifest.get('files'),list):
        raise ValueError('Invalid blue-triplet manifest container')
    rows=[];stem='enemy-projectile-blue-triplet-'
    for r in manifest['files']:
        if not isinstance(r,dict) or not isinstance(r.get('source_path'),str) or not isinstance(r.get('destination'),str):
            raise ValueError('Invalid runtime row paths')
        source=r['source_path'].casefold();dest=r['destination'].casefold();revision=r.get('revision')
        if (source.startswith(ROOT+'/') or source.rsplit('/',1)[-1].startswith(stem) or
                dest.rsplit('/',1)[-1].startswith(stem) or
                (isinstance(revision,str) and revision.casefold()==REVISION)):
            rows.append(r)
    if not required and not rows:return
    expected=load(root)
    if len(rows)!=3 or {r['destination'] for r in rows}!=set(expected):
        raise ValueError('Blue-triplet requires exactly three current consumers')
    for r in rows:
        current=expected[r['destination']]
        if (r['source_path']!=current['source_path'] or r.get('sha256')!=current['sha256'] or
                r.get('group')!='gameplay' or r.get('revision')!=REVISION):
            raise ValueError('Stale blue-triplet runtime selection')
