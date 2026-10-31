"""Closed selected166/94 authoring and transport validation; not runtime qualification.
Only two fixed generated sources; historical prompts are records, never executed.
"""
from pathlib import Path, PurePosixPath
import hashlib,io,json,re,stat,struct
from PIL import Image,__version__ as PILLOW_VERSION
SELECTORS=(166, 94)
IDS=(1550166, 1550094)
PAIRS=tuple((i,8) for i in IDS)
INPUT_ROOT='authoring-inputs/projectile-pulses16694-current'
ROOT='assets/hd/current-compat/projectile-pulses16694'
SELECTION='assets/hd/authoring/projectile-pulses16694-current.json'
MAPPING='packaging/current-projectile-pulses16694-compatibility.json'
HEADER='src/current_projectile_pulses16694_payload_pins.h'
REGISTRATION=INPUT_ROOT+'/registration.json'
COVERAGE=INPUT_ROOT+'/coverage-contract.json'
SCHEMA='opentyrian-current-projectile-pulses16694-authoring-v1'
CANDIDATE_SCHEMA='opentyrian-current-projectile-pulses16694-candidate-v1'
MAPPING_SCHEMA='opentyrian-current-projectile-pulses16694-compatibility-v1'
REVISION='current-projectile-pulses16694-166-94-generated-v1'
SELECTION_SPEC={'schema': 'opentyrian-current-projectile-pulses16694-authoring-v1', 'version': 'selected-pulses16694-registered02-standard-fnv', 'sources': [{'selector': 166, 'source_png': 'authoring-inputs/projectile-pulses16694-current/raw/generated-166-01.png', 'source_sha256': 'c49e46b754d1e00aec1d684129d57dd830bb0274758ecf4d8cf22547d124aad9', 'source_size': [1254, 1254], 'prompt_path': 'authoring-inputs/projectile-pulses16694-current/prompt-166-01.txt', 'prompt_sha256': 'a41e97e3164e7a0d830086be18abcb10681395096f4205c02c160b1073c978d0'}, {'selector': 94, 'source_png': 'authoring-inputs/projectile-pulses16694-current/raw/generated-94-corrected-02.png', 'source_sha256': 'f16260aa15e46d3cff124447017b138047bc9e26af59629d0eb8879b848f742f', 'source_size': [1060, 1484], 'prompt_path': 'authoring-inputs/projectile-pulses16694-current/prompt-94-correction-02.txt', 'prompt_sha256': '6a092173c67a607f61c974ccbac5b2fe8e262d09980f783b6c2b5375dbc20c0d'}], 'historical_prompts': [{'path': 'authoring-inputs/projectile-pulses16694-current/prompt-166-01.txt', 'sha256': 'a41e97e3164e7a0d830086be18abcb10681395096f4205c02c160b1073c978d0'}, {'path': 'authoring-inputs/projectile-pulses16694-current/prompt-94-01.txt', 'sha256': '6a35d673500238bc4a8d04c5413efdd6188feeacdd69192487e8301b3701e285'}, {'path': 'authoring-inputs/projectile-pulses16694-current/prompt-94-correction-02.txt', 'sha256': '6a092173c67a607f61c974ccbac5b2fe8e262d09980f783b6c2b5375dbc20c0d'}], 'members': [{'selector': 166, 'crop': [0, 0, 1254, 1254], 'placements': [[8, 8]], 'resize': [88, 88], 'png_compress_level': 6}, {'selector': 94, 'crop': [0, 0, 1060, 1484], 'placements': [[8, 0]], 'resize': [80, 112], 'png_compress_level': 6}]}
COVERAGE_SPEC={'schema': 'enemy-pulses16694-selected-coverage-v1', 'members': {'166': {'native_mask': '000000000000000011111000000111111100001111111110011111111111011111111111011111111111011111111111011111111111001111111110000111111100000011111000000000000000000000000000', 'native_occupied_cells': 97, 'max_alpha_matrix': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 76, 122, 141, 128, 76, 0, 0, 0], [0, 0, 0, 169, 237, 252, 252, 252, 249, 196, 0, 0], [0, 0, 174, 252, 253, 253, 253, 252, 252, 252, 187, 0], [0, 82, 245, 252, 253, 252, 252, 252, 252, 252, 250, 77], [0, 114, 251, 252, 252, 252, 252, 252, 252, 252, 252, 132], [0, 128, 252, 252, 252, 252, 252, 252, 252, 253, 252, 157], [0, 120, 252, 252, 252, 252, 252, 252, 252, 252, 252, 139], [0, 67, 240, 252, 252, 252, 252, 252, 252, 252, 247, 63], [0, 0, 171, 251, 252, 252, 253, 252, 252, 252, 161, 0], [0, 0, 0, 183, 244, 252, 252, 252, 251, 154, 0, 0], [0, 0, 0, 0, 73, 129, 147, 133, 66, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 'cell_distribution': {'high_ge200': 69, 'low_1_199': 28, 'zero': 0}, 'pixels': {'alpha0_rgb_nonzero': 0, 'max_alpha': 253, 'native_alpha0': 420, 'nonzero': 5788, 'opaque255': 0, 'outside_nonzero': 0, 'soft': 5788}, 'png_sha256': 'af41c280b551a3c2e0b440a3f114145dc7e6bf206fd61039411f6807cd7e2750', 'hda_sha256': 'e14f6cc59d8f0773fa20b840c4ea453bb6c2afebcc4e27806c927c2f9751fb89', 'payload_sha256': '8850072a95b19fdd57acd6c432c2a4ee65f65b5c6d359547a9cd62411ebb8703', 'payload_fnv': '80c10783a6cabbe2', 'palette_indices': [33, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159]}, '94': {'native_mask': '000001100000000001100000000011110000001111111100001111111100011111111110011111111110011111111110011111111110011111111110011111111110011111111110001111111100000111111000', 'native_occupied_cells': 108, 'max_alpha_matrix': [[0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 254, 255, 0, 0, 0, 0, 0], [0, 0, 0, 0, 252, 253, 253, 252, 0, 0, 0, 0], [0, 0, 56, 253, 253, 253, 253, 253, 253, 68, 0, 0], [0, 0, 252, 253, 253, 253, 253, 253, 253, 253, 0, 0], [0, 252, 253, 253, 253, 253, 253, 253, 253, 253, 251, 0], [0, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 0], [0, 255, 253, 253, 253, 253, 253, 253, 253, 253, 255, 0], [0, 255, 253, 253, 253, 253, 253, 253, 253, 253, 255, 0], [0, 255, 253, 253, 253, 253, 253, 253, 253, 253, 255, 0], [0, 255, 253, 253, 253, 253, 252, 253, 253, 253, 255, 0], [0, 179, 253, 253, 253, 253, 253, 253, 253, 254, 216, 0], [0, 0, 247, 253, 253, 253, 253, 253, 253, 251, 0, 0], [0, 0, 0, 115, 252, 253, 252, 252, 119, 0, 0, 0]], 'cell_distribution': {'high_ge200': 103, 'low_1_199': 5, 'zero': 0}, 'pixels': {'alpha0_rgb_nonzero': 0, 'max_alpha': 255, 'native_alpha0': 424, 'nonzero': 6488, 'opaque255': 40, 'outside_nonzero': 0, 'soft': 6448}, 'png_sha256': '2e229012e33f26d6104ca746d83c35e3eb3f9108d2f2690073387c1d19eccacc', 'hda_sha256': 'cf6f70641746a3b8eb91d61d5c414af7545e748f6583351972aa76c46f813f93', 'payload_sha256': '207b4f8a9890486490345820de0c0d589a7e7532f6aeb4687294e85e8aa6485e', 'payload_fnv': '131a3be7ed56665d', 'palette_indices': [114, 115, 116, 117, 119, 120, 121, 122, 123, 124, 125, 126, 127]}}}
REGISTRATION_SHA256='8691c3dcb55964da6af2c3fca58e53d257c5b04266d55d04d1dfa3bbaa07ef27'
COVERAGE_SHA256='6dac9390092d62f44e36497a9b0336ba23158b5ce84951f3e5b5677653bbada5'
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
    if type(identity)is not int or type(density)is not int or (identity,density)not in PAIRS:fail('Unknown pulses16694 identity/density')
    return f'enemy-projectile-pulses16694-{identity-1550000}-{density}.hda'
def png(identity,density=8):
    name(identity,density);return ROOT+f'/projectile-pulses16694-{identity-1550000}-registered.png'

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
    if type(selector)is not int or selector not in SELECTORS or type(payload)not in (bytes,bytearray) or len(payload)!=43008:fail('Invalid complete pulses16694 payload')
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
    name(identity);s=identity-1550000;m=COVERAGE_SPEC['members'][str(s)]
    if type(blob)is not bytes or len(blob)!=43036 or blob[:28]!=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0):fail('Changed exact HDR1 transport')
    validate_payload(root,s,blob[28:])
    if sha(blob)!=m['hda_sha256']:fail('Changed HDA hash')
    return True

def generate(root,raw,candidate=False):
    if PILLOW_VERSION!='12.3.0':fail('Fixed Pillow12.3.0 required')
    j=selection(root,raw,candidate);pngs={};blobs={};contract=coverage(root)
    for source,r in zip(SOURCES,j['members']):
        selector=r['selector'];identity=1550000+selector
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
        if type(pin)is not str or not re.fullmatch('[0-9a-f]{16}',pin) or pin!=COVERAGE_SPEC['members'][str(identity-1550000)]['payload_fnv']:fail('Changed standard payload pin')
    lines=['/* SPDX-License-Identifier: GPL-2.0-or-later',' * Fixed registered166/94 complete straight-RGBA payloads; separate identities. */','#ifndef CURRENT_PROJECTILE_PULSES16694_PAYLOAD_PINS_H','#define CURRENT_PROJECTILE_PULSES16694_PAYLOAD_PINS_H']
    for identity,density in PAIRS:lines.append(f'#define CURRENT_PROJECTILE_PULSES16694_{identity}_PAYLOAD_FNV UINT64_C(0x{pins[(identity,density)]})')
    return ('\n'.join(lines+['#endif',''])).encode()

def rows_for(selected,blobs):
    if not exact(selected,SELECTION_SPEC)or type(blobs)is not dict or set(blobs)!=set(PAIRS)or any(type(k)is not tuple or len(k)!=2 or any(type(x)is not int for x in k)for k in blobs):fail('Changed finite output set')
    for i,d in PAIRS:
        b=blobs[(i,d)]
        if type(b)is not bytes or len(b)!=43036 or b[:28]!=struct.pack('<4s6I',b'HDR1',i,8,12,14,0,0) or sha(b)!=COVERAGE_SPEC['members'][str(i-1550000)]['hda_sha256']:fail('Changed rows_for transport')
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
    rows=[];stem='enemy-projectile-pulses16694-'
    for r in manifest['files']:
        if type(r)is not dict or type(r.get('source_path'))is not str or type(r.get('destination'))is not str:fail('Invalid row paths')
        source=r['source_path'].casefold();dest=r['destination'].casefold();revision=r.get('revision')
        if source.startswith(ROOT+'/') or source.rsplit('/',1)[-1].startswith(stem) or dest.rsplit('/',1)[-1].startswith(stem) or (type(revision)is str and revision.casefold()==REVISION):rows.append(r)
    if not required and not rows:return
    expected=load(root)
    if len(rows)!=2 or {r['destination']for r in rows}!=set(expected):fail('Exactly two current pulses16694 consumers required')
    for r in rows:
        want=expected[r['destination']]
        if r['source_path']!=want['source_path']or r.get('sha256')!=want['sha256']or r.get('group')!='gameplay'or r.get('revision')!=REVISION:fail('Stale pulses16694 consumer')
        for k in ('identity','density'):
            if k in r and (type(r[k])is not int or r[k]!=want[k]):fail('Contradictory identity/density')
