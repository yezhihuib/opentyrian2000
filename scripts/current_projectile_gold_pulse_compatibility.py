"""Closed single-generated-master enemy gold transports; no game data or external fallback.
Authoring/package validation is separate from runtime admission and qualification.
"""
import io,json,re,struct
from PIL import Image, __version__ as PILLOW_VERSION
from current_plasma_projectile_compatibility import sha,parse,read,is_hash
from current_craft267_compatibility import path
SELECTORS=(168,169)
IDS=(1530168,1530169)
PAIRS=tuple((i,8) for i in IDS)
INPUT_ROOT='authoring-inputs/projectile-gold-pulse-current'
ROOT='assets/hd/current-compat/projectile-gold-pulse'
SELECTION='assets/hd/authoring/projectile-gold-pulse-current.json'
MAPPING='packaging/current-projectile-gold-pulse-compatibility.json'
HEADER='src/current_projectile_gold_pulse_payload_pins.h'
REGISTRATION=INPUT_ROOT+'/registration.json'
COVERAGE=INPUT_ROOT+'/coverage-contract.json'
SCHEMA='opentyrian-current-projectile-gold-pulse-authoring-v1'
CANDIDATE_SCHEMA='opentyrian-current-projectile-gold-pulse-candidate-v1'
MAPPING_SCHEMA='opentyrian-current-projectile-gold-pulse-compatibility-v1'
REVISION='current-single-source-projectile-gold-pulse'
MASTER={'source_png': 'authoring-inputs/projectile-gold-pulse-current/raw/generated-master-epoch2-01.png', 'source_sha256': '3c26709606ce7c673fe33799c2480951b2041b829a5123bdacf5c9fb20b3ef75', 'source_size': [1774, 887], 'prompt_path': 'authoring-inputs/projectile-gold-pulse-current/prompt-01.txt', 'prompt_sha256': '2c683103adc625695f5d957d6933af9a28a11d143cfaedc4edd00c2f5dbc883f'}
MEMBERS=[{'selector': 168, 'crop': [0, 0, 887, 887], 'resize': [88, 88], 'paste': [0, 8], 'png_compress_level': 6}, {'selector': 169, 'crop': [887, 0, 1774, 887], 'resize': [72, 72], 'paste': [8, 16], 'png_compress_level': 6}]
MASKS={168: '000000000000000111110000001111111000011111111100111111111110111111111110111111111110111111111110111111111110011111111100001111111000000111110000000000000000000000000000', 169: '000000000000000000000000000111110000001111111000011111111100011111111100011111111100011111111100011111111100001111111000000111110000000000000000000000000000000000000000'}
DISTRIBUTIONS={168: (72, 25, 0), 169: (45, 24, 0)}
APPROVED_PNG_SHA256={168: '624ff64f2029fdea00e63420419ad2faefe575d574f99307795f2842283862ec', 169: 'b9740e8a2c257b3ae261aca027427fdac0c66b53353391febe0e92378c3f9cb5'}
REGISTRATION_SHA256='3075f05d501ca179f9ad042da9d2d76d17f6a3ccfa1d41b5323c8d66cc78ee4f'
COVERAGE_SHA256='ed516cc835d7858d27999c837160bd4a04d0f782e3affc9e803f87e1d83cd3cf'

def name(identity,density=8):
    if type(identity) is not int or type(density) is not int or (identity,density) not in PAIRS:raise ValueError('Unknown gold identity/density')
    return f'enemy-projectile-gold-pulse-{identity-1530000}-{density}.hda'
def png(identity,density=8):
    name(identity,density);return ROOT+f'/projectile-gold-pulse-{identity-1530000}-registered.png'
def single_input(root,name,expected):
    raw=read(root,name)
    if path(root,name).stat().st_nlink!=1 or sha(raw)!=expected:raise ValueError('Changed/hardlinked fixed gold input: '+name)
    return raw
def coverage(root):return parse(single_input(root,COVERAGE,COVERAGE_SHA256))
def selection(root,raw,candidate=False):
    if type(candidate) is not bool:raise ValueError('Expected boolean candidate')
    j=parse(raw)
    if not isinstance(j,dict) or set(j)!={'schema','version','master','members'} or j['schema']!=(CANDIDATE_SCHEMA if candidate else SCHEMA):raise ValueError('Invalid closed gold schema')
    if not isinstance(j['version'],str) or not 1<=len(j['version'])<=128:raise ValueError('Invalid gold version')
    m=j['master']
    if not isinstance(m,dict) or set(m)!=set(MASTER) or any(not isinstance(m[k],str) for k in ('source_png','source_sha256','prompt_path','prompt_sha256')) or not isinstance(m['source_size'],list) or len(m['source_size'])!=2 or any(type(v) is not int for v in m['source_size']) or m!=MASTER:raise ValueError('Changed fixed master/prompt/dimensions')
    rows=j['members']
    if not isinstance(rows,list) or len(rows)!=2:raise ValueError('Expected exactly two members')
    for row,expected in zip(rows,MEMBERS):
        if not isinstance(row,dict) or set(row)!=set(expected):raise ValueError('Invalid member fields')
        if type(row['selector']) is not int or type(row['png_compress_level']) is not int or any(not isinstance(row[k],list) or len(row[k])!=len(expected[k]) or any(type(v) is not int for v in row[k]) for k in ('crop','resize','paste')) or row!=expected:raise ValueError('Changed finite registration')
    single_input(root,m['source_png'],m['source_sha256']);single_input(root,m['prompt_path'],m['prompt_sha256'])
    single_input(root,REGISTRATION,REGISTRATION_SHA256);coverage(root);return j

def validate_payload(root,selector,payload,contract=None):
    if type(selector) is not int or selector not in SELECTORS or len(payload)!=43008:raise ValueError('Invalid gold payload')
    m=(coverage(root) if contract is None else contract)['members'][str(selector)];mask=MASKS[selector]
    for y in range(112):
        for x in range(96):
            q=payload[(y*96+x)*4:(y*96+x)*4+4]
            if (mask[(y//8)*12+x//8]=='0' or q[3]==0) and any(q):raise ValueError('Noncanonical transparent/outside-native RGBA')
    matrix=[[max(payload[((y*8+dy)*96+x*8+dx)*4+3] for dy in range(8) for dx in range(8)) for x in range(12)] for y in range(14)]
    used=[matrix[y][x] for y in range(14) for x in range(12) if mask[y*12+x]=='1'];alpha=payload[3::4]
    dist=(sum(a>=200 for a in used),sum(0<a<200 for a in used),used.count(0))
    nativezero=sum(alpha[y*96+x]==0 for y in range(112) for x in range(96) if mask[(y//8)*12+x//8]=='1')
    pix={'nonzero':sum(a>0 for a in alpha),'soft':sum(0<a<255 for a in alpha),'opaque255':alpha.count(255),'native_alpha0':nativezero,'max_alpha':max(alpha)}
    from build_current_art import fnv
    if m['native_mask']!=mask or m['native_occupied_cells']!=len(used) or matrix!=m['max_alpha_matrix'] or dist!=DISTRIBUTIONS[selector] or pix!=m['pixels'] or sha(payload)!=m['payload_sha256'] or fnv(payload)!=m['payload_fnv']:raise ValueError('Changed selected gold matrix/distribution/payload')
    return matrix

def generate(root,raw,candidate=False):
    j=selection(root,raw,candidate);pngs={};blobs={};contract=coverage(root)
    if PILLOW_VERSION!='12.3.0':raise ValueError('Fixed Pillow12.3.0 required')
    with Image.open(io.BytesIO(single_input(root,MASTER['source_png'],MASTER['source_sha256']))) as im:
        if im.format!='PNG' or im.mode!='RGBA' or list(im.size)!=MASTER['source_size'] or getattr(im,'n_frames',1)!=1:raise ValueError('Changed approved RGBA master')
        for r in j['members']:
            selector=r['selector'];identity=1530000+selector
            tile=Image.new('RGBA',(96,112));tile.paste(im.crop(tuple(r['crop'])).resize(tuple(r['resize']),Image.Resampling.LANCZOS),tuple(r['paste']))
            payload=bytearray(tile.tobytes());mask=MASKS[selector]
            for y in range(112):
                for x in range(96):
                    p=(y*96+x)*4
                    if mask[(y//8)*12+x//8]=='0' or payload[p+3]==0:payload[p:p+4]=b'\0'*4
            validate_payload(root,selector,payload,contract)
            out=Image.frombytes('RGBA',(96,112),bytes(payload));buf=io.BytesIO();out.save(buf,format='PNG',compress_level=r['png_compress_level']);encoded=buf.getvalue()
            blob=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0)+payload
            if sha(encoded)!=APPROVED_PNG_SHA256[selector] or sha(blob)!=contract['members'][str(selector)]['hda_sha256']:raise ValueError('Changed gold derivative')
            pngs[png(identity)]=encoded;blobs[(identity,8)]=blob
    return dict(j,schema=SCHEMA),pngs,blobs

def payload_header(pins):
    if not isinstance(pins,dict) or set(pins)!=set(PAIRS):raise ValueError('Expected two exact pins')
    lines=['/* SPDX-License-Identifier: GPL-2.0-or-later',' * New epoch2 generated payload identities; no old-gold identity claim. */','#ifndef CURRENT_PROJECTILE_GOLD_PULSE_PAYLOAD_PINS_H','#define CURRENT_PROJECTILE_GOLD_PULSE_PAYLOAD_PINS_H']
    for identity,density in PAIRS:
        pin=pins[(identity,density)]
        if not isinstance(pin,str) or not re.fullmatch('[0-9a-f]{16}',pin):raise ValueError('Invalid gold pin')
        lines.append(f'#define CURRENT_PROJECTILE_GOLD_PULSE_{identity}_PAYLOAD_FNV UINT64_C(0x{pin})')
    return ('\n'.join(lines+['#endif',''])).encode()
def rows_for(selected,blobs):
    return [dict(identity=i,density=d,source_path=ROOT+'/'+name(i,d),destination='assets/gameplay/'+name(i,d),sha256=sha(blobs[(i,d)])) for i,d in PAIRS]

def input_paths(root):
    selection(root,read(root,SELECTION))
    return {SELECTION,MAPPING,HEADER,REGISTRATION,COVERAGE}|{MASTER['source_png'],MASTER['prompt_path']}|{png(i,d) for i,d in PAIRS}|{ROOT+'/'+name(i,d) for i,d in PAIRS}

def load(root):
    from build_current_art import fnv
    selected,pngs,blobs=generate(root,read(root,SELECTION));rows=rows_for(selected,blobs)
    outputs={**pngs,**{r['source_path']:blobs[(r['identity'],r['density'])] for r in rows}}
    for p,b in outputs.items():
        if read(root,p)!=b:raise ValueError('Stale gold-pulse derivative: '+p)
    expected=dict(schema=MAPPING_SCHEMA,selection=SELECTION,version=selected['version'],files=rows)
    if parse(read(root,MAPPING))!=expected:raise ValueError('Stale gold-pulse mapping')
    if read(root,HEADER)!=payload_header({pair:fnv(blob[28:]) for pair,blob in blobs.items()}):
        raise ValueError('Stale gold-pulse independent pins')
    return {r['destination']:r for r in rows}

def validate_runtime_rows(root,manifest,required=False):
    """Closed alias-aware two-piece package selection, not C runtime readiness."""
    if type(required) is not bool or not isinstance(manifest,dict) or not isinstance(manifest.get('files'),list):
        raise ValueError('Invalid gold-pulse manifest container')
    rows=[];stem='enemy-projectile-gold-pulse-'
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
    if len(rows)!=2 or {r['destination'] for r in rows}!=set(expected):
        raise ValueError('Gold-pulse requires exactly two current consumers')
    for r in rows:
        current=expected[r['destination']]
        if (r['source_path']!=current['source_path'] or r.get('sha256')!=current['sha256'] or
                r.get('group')!='gameplay' or r.get('revision')!=REVISION):
            raise ValueError('Stale gold-pulse runtime selection')
