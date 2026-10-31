"""Closed selected162/260 authoring and transport validation; not runtime qualification.
Only two fixed generated sources; historical prompts are records, never executed.
"""
from pathlib import Path, PurePosixPath
import hashlib,io,json,re,stat,struct
from PIL import Image,__version__ as PILLOW_VERSION
SELECTORS=(162,260)
IDS=(1540162,1540260)
PAIRS=tuple((i,8) for i in IDS)
INPUT_ROOT='authoring-inputs/projectile-statics-current'
ROOT='assets/hd/current-compat/projectile-statics'
SELECTION='assets/hd/authoring/projectile-statics-current.json'
MAPPING='packaging/current-projectile-statics-compatibility.json'
HEADER='src/current_projectile_statics_payload_pins.h'
REGISTRATION=INPUT_ROOT+'/registration.json'
COVERAGE=INPUT_ROOT+'/coverage-contract.json'
SCHEMA='opentyrian-current-projectile-statics-authoring-v1'
CANDIDATE_SCHEMA='opentyrian-current-projectile-statics-candidate-v1'
MAPPING_SCHEMA='opentyrian-current-projectile-statics-compatibility-v1'
REVISION='current-projectile-statics-162-260-generated-v1'
SELECTION_SPEC={'schema': 'opentyrian-current-projectile-statics-authoring-v1', 'version': 'selected-statics-registered02-standard-fnv', 'sources': [{'selector': 162, 'source_png': 'authoring-inputs/projectile-statics-current/raw/generated-162-01.png', 'source_sha256': '27dcdfedd7e8c3ec4ad21be7e4d62befc27b6cfe618bb0c259679a40c8164d44', 'source_size': [1254, 1254], 'prompt_path': 'authoring-inputs/projectile-statics-current/prompt-162-01.txt', 'prompt_sha256': '909083d64c1af9800544f3c09dc8b5b2644a6ac1cdde3e80b51c7dd7b8df0e1e'}, {'selector': 260, 'source_png': 'authoring-inputs/projectile-statics-current/raw/generated-260-corrected-02.png', 'source_sha256': '86e024a8535a22b5229b98c140559ff741db03768f217bdc21113fd7ed200130', 'source_size': [887, 1774], 'prompt_path': 'authoring-inputs/projectile-statics-current/prompt-260-correction-02.txt', 'prompt_sha256': 'e2c9d3285046d6a135a804e63591eb31eecb6430d8cc52845bacb079191701f4'}], 'historical_prompts': [{'path': 'authoring-inputs/projectile-statics-current/prompt-162-01.txt', 'sha256': '909083d64c1af9800544f3c09dc8b5b2644a6ac1cdde3e80b51c7dd7b8df0e1e'}, {'path': 'authoring-inputs/projectile-statics-current/prompt-260-01.txt', 'sha256': '0297199b612d2792e9855086a6db64f5f2226cbab4ab1170e17747f398c862b1'}, {'path': 'authoring-inputs/projectile-statics-current/prompt-260-correction-02.txt', 'sha256': 'e2c9d3285046d6a135a804e63591eb31eecb6430d8cc52845bacb079191701f4'}], 'members': [{'selector': 162, 'crop': [0, 0, 1254, 1254], 'placements': [[32, 16], [32, 56]], 'resize': [32, 32], 'png_compress_level': 6}, {'selector': 260, 'crop': [0, 0, 887, 1774], 'placements': [[16, 0]], 'resize': [56, 112], 'png_compress_level': 6}]}
COVERAGE_SPEC={'schema': 'enemy-statics-selected-coverage-v1', 'members': {'162': {'native_mask': '000000000000000000000000000001100000000011110000000011110000000001100000000000000000000001100000000011110000000011110000000001100000000000000000000000000000000000000000', 'native_occupied_cells': 24, 'max_alpha_matrix': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 254, 254, 0, 0, 0, 0, 0], [0, 0, 0, 0, 254, 253, 253, 255, 0, 0, 0, 0], [0, 0, 0, 0, 255, 253, 253, 255, 0, 0, 0, 0], [0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 254, 254, 0, 0, 0, 0, 0], [0, 0, 0, 0, 254, 253, 253, 255, 0, 0, 0, 0], [0, 0, 0, 0, 255, 253, 253, 255, 0, 0, 0, 0], [0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 'cell_distribution': {'high_ge200': 24, 'low_1_199': 0, 'zero': 0}, 'pixels': {'alpha0_rgb_nonzero': 0, 'max_alpha': 255, 'native_alpha0': 144, 'nonzero': 1392, 'opaque255': 12, 'outside_nonzero': 0, 'soft': 1380}, 'png_sha256': 'bbccd58bd75664e17391498f40355fe31215373da684f5259178b01b80b763e1', 'hda_sha256': '2d045f7fc472ed6e2f33f9d742072f3b7ea1c3a606d8f1909bbcd33b57ae0119', 'payload_sha256': '76f9b1ec5130119e20d11a64530dfcc3308be1df64f159ee32ba9f18b64845a4', 'payload_fnv': '97621110c318d6a5', 'palette_indices': [122, 123, 125, 126, 127]}, '260': {'native_mask': '000011100000000111110000001111111000001111111000001111111000001111111000001111111000001111111000001111111000001111111000001111111000001111111000000111110000000011100000', 'native_occupied_cells': 86, 'max_alpha_matrix': [[0, 0, 0, 0, 254, 255, 254, 0, 0, 0, 0, 0], [0, 0, 0, 252, 253, 253, 253, 252, 0, 0, 0, 0], [0, 0, 188, 252, 253, 253, 253, 253, 203, 0, 0, 0], [0, 0, 247, 253, 252, 253, 253, 253, 247, 0, 0, 0], [0, 0, 250, 253, 252, 253, 253, 253, 251, 0, 0, 0], [0, 0, 252, 253, 253, 253, 253, 253, 252, 0, 0, 0], [0, 0, 252, 253, 253, 253, 253, 253, 252, 0, 0, 0], [0, 0, 252, 253, 253, 253, 252, 253, 253, 0, 0, 0], [0, 0, 252, 253, 253, 253, 253, 253, 252, 0, 0, 0], [0, 0, 248, 253, 253, 253, 252, 253, 249, 0, 0, 0], [0, 0, 245, 253, 253, 253, 252, 253, 246, 0, 0, 0], [0, 0, 195, 253, 253, 253, 252, 253, 190, 0, 0, 0], [0, 0, 0, 252, 253, 253, 253, 253, 0, 0, 0, 0], [0, 0, 0, 0, 253, 253, 253, 0, 0, 0, 0, 0]], 'cell_distribution': {'high_ge200': 83, 'low_1_199': 3, 'zero': 0}, 'pixels': {'alpha0_rgb_nonzero': 0, 'max_alpha': 255, 'native_alpha0': 287, 'nonzero': 5217, 'opaque255': 1, 'outside_nonzero': 0, 'soft': 5216}, 'png_sha256': 'caaa44da1ee336a17b2959e94c17719d3fce929c34711bdbfae510995ebf6909', 'hda_sha256': '5545ee065fcf879eb306a6c25dc0b9be8ecf8dcaa5154cdbb69ae907e75adf8e', 'payload_sha256': 'fe9fd61f0ef6c71769390f07ed1cfc2798482b2a1c1c98ddafc8b1aa2b162bb6', 'payload_fnv': 'fa2ac27b3212b610', 'palette_indices': [113, 116, 117, 119, 120, 121, 122, 123, 124, 125, 126]}}}
REGISTRATION_SHA256='57935422e6fa5e91582dfd71b420c11c1715d4cb5969dfe93531152d4ec6c5a4'
COVERAGE_SHA256='ae3a53f15f38e27714d8ccb7a6b79c517a69a85814acfd6d4337f205506bc5e9'
SOURCES=SELECTION_SPEC["sources"]
MEMBERS=SELECTION_SPEC["members"]
PROMPTS=SELECTION_SPEC["historical_prompts"]
MASKS={int(s):r["native_mask"]for s,r in COVERAGE_SPEC["members"].items()}
APPROVED_PNG_SHA256={int(s):r["png_sha256"]for s,r in COVERAGE_SPEC["members"].items()}

def fail(message):raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def fnv(raw):
    h=0xcbf29ce484222325
    for b in raw:h=((h^b)*0x100000001b3)&0xffffffffffffffff
    return f'{h:016x}'
def exact(value,wanted):
    if type(value)is not type(wanted):return False
    if type(wanted)is dict:return set(value)==set(wanted) and all(exact(value[k],v)for k,v in wanted.items())
    if type(wanted)is list:return len(value)==len(wanted) and all(exact(a,b)for a,b in zip(value,wanted))
    return value==wanted

def parse(raw):
    if type(raw)is not bytes or len(raw)>128*1024:fail('Expected bounded JSON bytes')
    def pairs(rows):
        out={}
        for k,v in rows:
            if k in out:fail('Duplicate JSON key')
            out[k]=v
        return out
    def nonfinite(value):fail('Non-finite JSON value')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=nonfinite)

def relative_name(name):
    if type(name)is not str or not name or '\\' in name or ':' in name or any(ord(c)<32 for c in name):fail('Invalid relative path')
    p=PurePosixPath(name)
    if p.is_absolute() or any(x in ('','.','..')for x in name.split('/')) or p.as_posix()!=name:fail('Noncanonical relative path')
    return p

def path(root,name):
    rel=relative_name(name);root=Path(root).absolute();target=root/rel
    for p in (root,*root.parents,*[root.joinpath(*rel.parts[:i])for i in range(1,len(rel.parts)+1)]):
        try:s=p.lstat()
        except FileNotFoundError:continue
        if stat.S_ISLNK(s.st_mode) or getattr(s,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0):fail('Linked/reparse path')
    return target

def read(root,name,limit=16*1024*1024):
    p=path(root,name);s=p.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_size>limit:fail('Not independent bounded regular input')
    b=p.read_bytes();a=p.lstat()
    if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_nlink)!=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_nlink) or len(b)!=s.st_size:fail('Input changed while reading')
    return b

def single_input(root,name,pin):
    raw=read(root,name)
    if sha(raw)!=pin:fail('Changed fixed input: '+name)
    return raw

def name(identity,density=8):
    if type(identity)is not int or type(density)is not int or (identity,density)not in PAIRS:fail('Unknown statics identity/density')
    return f'enemy-projectile-statics-{identity-1540000}-{density}.hda'
def png(identity,density=8):
    name(identity,density);return ROOT+f'/projectile-statics-{identity-1540000}-registered.png'

def coverage(root):
    j=parse(single_input(root,COVERAGE,COVERAGE_SHA256))
    if not exact(j,COVERAGE_SPEC):fail('Changed complete coverage contract')
    return j

def selection(root,raw,candidate=False):
    if type(candidate)is not bool:fail('Expected boolean candidate')
    j=parse(raw);want=dict(SELECTION_SPEC,schema=CANDIDATE_SCHEMA if candidate else SCHEMA)
    if not exact(j,want):fail('Changed finite two-source selection')
    for s in SOURCES:single_input(root,s['source_png'],s['source_sha256'])
    for p in PROMPTS:single_input(root,p['path'],p['sha256'])
    single_input(root,REGISTRATION,REGISTRATION_SHA256);coverage(root)
    return j

def validate_payload(root,selector,payload,contract=None):
    if type(selector)is not int or selector not in SELECTORS or type(payload)not in (bytes,bytearray) or len(payload)!=43008:fail('Invalid complete statics payload')
    contract=coverage(root)if contract is None else contract
    if not exact(contract,COVERAGE_SPEC):fail('Changed coverage argument')
    m=contract['members'][str(selector)];mask=MASKS[selector]
    for y in range(112):
        for x in range(96):
            q=payload[4*(y*96+x):4*(y*96+x)+4]
            if (mask[(y//8)*12+x//8]=='0' or q[3]==0) and any(q):fail('Noncanonical outside/zero RGBA')
    matrix=[[max(payload[4*((y*8+dy)*96+x*8+dx)+3]for dy in range(8)for dx in range(8))for x in range(12)]for y in range(14)]
    used=[matrix[y][x]for y in range(14)for x in range(12)if mask[y*12+x]=='1'];alpha=payload[3::4]
    dist=dict(high_ge200=sum(a>=200 for a in used),low_1_199=sum(0<a<200 for a in used),zero=used.count(0))
    pix=dict(nonzero=sum(a>0 for a in alpha),soft=sum(0<a<255 for a in alpha),opaque255=alpha.count(255),max_alpha=max(alpha),native_alpha0=sum(alpha[y*96+x]==0 for y in range(112)for x in range(96)if mask[(y//8)*12+x//8]=='1'),outside_nonzero=0,alpha0_rgb_nonzero=0)
    if len(used)!=m['native_occupied_cells'] or matrix!=m['max_alpha_matrix'] or dist!=m['cell_distribution'] or pix!=m['pixels'] or sha(payload)!=m['payload_sha256'] or fnv(payload)!=m['payload_fnv']:fail('Changed selected matrix/distribution/payload')
    return matrix

def validate_hda(root,identity,blob):
    name(identity);s=identity-1540000;m=COVERAGE_SPEC['members'][str(s)]
    if type(blob)is not bytes or len(blob)!=43036 or blob[:28]!=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0):fail('Changed exact HDR1 transport')
    validate_payload(root,s,blob[28:])
    if sha(blob)!=m['hda_sha256']:fail('Changed HDA hash')
    return True

def generate(root,raw,candidate=False):
    if PILLOW_VERSION!='12.3.0':fail('Fixed Pillow12.3.0 required')
    j=selection(root,raw,candidate);pngs={};blobs={};contract=coverage(root)
    for source,r in zip(SOURCES,j['members']):
        selector=r['selector'];identity=1540000+selector
        with Image.open(io.BytesIO(single_input(root,source['source_png'],source['source_sha256'])))as im:
            if im.format!='PNG' or im.mode!='RGBA' or list(im.size)!=source['source_size'] or getattr(im,'n_frames',1)!=1:fail('Changed approved raw PNG')
            component=im.crop(tuple(r['crop'])).resize(tuple(r['resize']),Image.Resampling.LANCZOS)
            tile=Image.new('RGBA',(96,112),(0,0,0,0))
            for xy in r['placements']:tile.paste(component,tuple(xy))
            payload=bytearray(tile.tobytes());mask=MASKS[selector]
            for y in range(112):
                for x in range(96):
                    p=4*(y*96+x)
                    if mask[(y//8)*12+x//8]=='0' or payload[p+3]==0:payload[p:p+4]=b'\0'*4
            validate_payload(root,selector,payload,contract)
            out=Image.frombytes('RGBA',(96,112),bytes(payload));buf=io.BytesIO();out.save(buf,format='PNG',compress_level=r['png_compress_level']);encoded=buf.getvalue()
            blob=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0)+payload
            if sha(encoded)!=APPROVED_PNG_SHA256[selector]:fail('Changed selected PNG encoding')
            validate_hda(root,identity,blob);pngs[png(identity)]=encoded;blobs[(identity,8)]=blob
    return dict(j,schema=SCHEMA),pngs,blobs

def payload_header(pins):
    if type(pins)is not dict or set(pins)!=set(PAIRS) or any(type(k)is not tuple or len(k)!=2 or any(type(x)is not int for x in k)for k in pins):fail('Expected exact finite payload pins')
    for identity,density in PAIRS:
        pin=pins[(identity,density)]
        if type(pin)is not str or not re.fullmatch('[0-9a-f]{16}',pin) or pin!=COVERAGE_SPEC['members'][str(identity-1540000)]['payload_fnv']:fail('Changed standard payload pin')
    lines=['/* SPDX-License-Identifier: GPL-2.0-or-later',' * Fixed registered162/260 complete straight-RGBA payloads; separate identities. */','#ifndef CURRENT_PROJECTILE_STATICS_PAYLOAD_PINS_H','#define CURRENT_PROJECTILE_STATICS_PAYLOAD_PINS_H']
    for identity,density in PAIRS:lines.append(f'#define CURRENT_PROJECTILE_STATICS_{identity}_PAYLOAD_FNV UINT64_C(0x{pins[(identity,density)]})')
    return ('\n'.join(lines+['#endif',''])).encode()

def rows_for(selected,blobs):
    if not exact(selected,SELECTION_SPEC)or type(blobs)is not dict or set(blobs)!=set(PAIRS)or any(type(k)is not tuple or len(k)!=2 or any(type(x)is not int for x in k)for k in blobs):fail('Changed finite output set')
    for i,d in PAIRS:
        b=blobs[(i,d)]
        if type(b)is not bytes or len(b)!=43036 or b[:28]!=struct.pack('<4s6I',b'HDR1',i,8,12,14,0,0) or sha(b)!=COVERAGE_SPEC['members'][str(i-1540000)]['hda_sha256']:fail('Changed rows_for transport')
    return [dict(identity=i,density=d,source_path=ROOT+'/'+name(i,d),destination='assets/gameplay/'+name(i,d),sha256=sha(blobs[(i,d)]))for i,d in PAIRS]

def input_paths(root):
    selection(root,read(root,SELECTION))
    return {SELECTION,MAPPING,HEADER,REGISTRATION,COVERAGE}|{s['source_png']for s in SOURCES}|{p['path']for p in PROMPTS}|{png(i,d)for i,d in PAIRS}|{ROOT+'/'+name(i,d)for i,d in PAIRS}

def load(root):
    selected,pngs,blobs=generate(root,read(root,SELECTION));rows=rows_for(selected,blobs)
    for p,b in {**pngs,**{r['source_path']:blobs[(r['identity'],r['density'])]for r in rows}}.items():
        if read(root,p)!=b:fail('Stale derivative: '+p)
    expected=dict(schema=MAPPING_SCHEMA,selection=SELECTION,version=selected['version'],files=rows)
    if not exact(parse(read(root,MAPPING)),expected):fail('Stale mapping')
    if read(root,HEADER)!=payload_header({pair:fnv(b[28:])for pair,b in blobs.items()}):fail('Stale independent payload header')
    return {r['destination']:r for r in rows}

def validate_runtime_rows(root,manifest,required=False):
    if type(required)is not bool or type(manifest)is not dict or type(manifest.get('files'))is not list:fail('Invalid manifest container')
    rows=[];stem='enemy-projectile-statics-'
    for r in manifest['files']:
        if type(r)is not dict or type(r.get('source_path'))is not str or type(r.get('destination'))is not str:fail('Invalid row paths')
        source=r['source_path'].casefold();dest=r['destination'].casefold();revision=r.get('revision')
        if source.startswith(ROOT+'/') or source.rsplit('/',1)[-1].startswith(stem) or dest.rsplit('/',1)[-1].startswith(stem) or (type(revision)is str and revision.casefold()==REVISION):rows.append(r)
    if not required and not rows:return
    expected=load(root)
    if len(rows)!=2 or {r['destination']for r in rows}!=set(expected):fail('Exactly two current statics consumers required')
    for r in rows:
        want=expected[r['destination']]
        if r['source_path']!=want['source_path']or r.get('sha256')!=want['sha256']or r.get('group')!='gameplay'or r.get('revision')!=REVISION:fail('Stale statics consumer')
        for k in ('identity','density'):
            if k in r and (type(r[k])is not int or r[k]!=want[k]):fail('Contradictory identity/density')
