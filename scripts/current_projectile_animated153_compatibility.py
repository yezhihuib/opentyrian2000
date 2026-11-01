"""Finite Banana Blast3phase authoring; source invariant qualification, scene review pending."""
from pathlib import Path,PurePosixPath
import hashlib,io,json,re,stat,struct
from PIL import Image,__version__ as PILLOW_VERSION
SELECTORS=(153,154,155)
IDS=(1570153,1570154,1570155)
PAIRS=tuple((i,8)for i in IDS)
INPUT_ROOT='authoring-inputs/projectile-animated153-current'
ROOT='assets/hd/current-compat/projectile-animated153'
SELECTION='assets/hd/authoring/projectile-animated153-current.json'
MAPPING='packaging/current-projectile-animated153-compatibility.json'
HEADER='src/current_projectile_animated153_payload_pins.h'
REGISTRATION=INPUT_ROOT+'/registration.json'
COVERAGE=INPUT_ROOT+'/coverage-contract.json'
REFERENCE=INPUT_ROOT+'/source-reference.json'
SCHEMA='opentyrian-current-projectile-animated153-authoring-v1'
CANDIDATE_SCHEMA='opentyrian-current-projectile-animated153-candidate-v1'
MAPPING_SCHEMA='opentyrian-current-projectile-animated153-compatibility-v1'
REVISION='current-single-source-projectile-animated153'
ENCODING='palette-index-r0-g0-binary-alpha-v1'
SELECTION_SPEC={'schema': 'opentyrian-current-projectile-animated153-authoring-v1', 'version': 'ordinary-bank8-banana-153-154-155-v1', 'encoding': 'palette-index-r0-g0-binary-alpha-v1', 'inputs': {'authoring-inputs/projectile-animated153-current/coverage-contract.json': '2128f5a762b5115bf1b8cc9c6d9ba2d7daadc9ad40f0569299bc436604b34c1d', 'authoring-inputs/projectile-animated153-current/prompt-v1.txt': '4bb2b32185e85f9074f1c453d293233768a6aed136b62874bb298d5b76ab277a', 'authoring-inputs/projectile-animated153-current/prompt-v2.txt': '1655673fc2796071da63fc96f04fc39a69b0cf2af0ad7162ac3b4ff8d904deeb', 'authoring-inputs/projectile-animated153-current/prompt-v3-banana.txt': '58814ecae39e357d76ef5a631cff5b346990828e44b3821d6aba73d92e560936', 'authoring-inputs/projectile-animated153-current/prompt-v4-153-only.txt': 'ace0383b55ad4af899fd3c36174191629a42f7371bd2f835bbd58aa33194663a', 'authoring-inputs/projectile-animated153-current/provenance.json': '31a7b8d2f5cd9708c1adb72d01f0084925c0d35982cfdeb91bfd6960ba6b8eee', 'authoring-inputs/projectile-animated153-current/raw-153-v4.png': '8b3ea9838879b0cc356fb8238410bc0779c202b1b5e8c9af42378d0b4020ecfc', 'authoring-inputs/projectile-animated153-current/raw-three-phases-v1.png': '02ab3c47fae4f1fdc0a9d3ef093e715281b96378dd5da287587599f4eac02fae', 'authoring-inputs/projectile-animated153-current/raw-three-phases-v2.png': '1ff09d1fd1a7a6ffb5d61f7eb5b49ffd3a41126835e70ec1de40502727519bb1', 'authoring-inputs/projectile-animated153-current/raw-three-phases-v3.png': 'f3be24dc0e15af313faf150a92614d9af2498a151ca3a2d46fbf9eae9f45325e', 'authoring-inputs/projectile-animated153-current/registration.json': 'fae3a1cf3185471d683d2d4a8f380c5771378e1e2d66de59151c8ddc3bf2b91c', 'authoring-inputs/projectile-animated153-current/source-reference.json': '104198517f5173bfd7fef14e2b321e478bbede2d269c48efde2ed2965d54c887', 'authoring-inputs/projectile-animated153-current/source-reference.png': 'dbf49acde66313b0d1dc2a9726d0526dcca3878888f016b9a7e386afaff9222a', 'authoring-inputs/projectile-animated153-current/source153-target-reference.png': 'a7f7270e053ac3d0e592484568823c25e523f3baf0557803ccd8adc72ec12a7a'}}
COVERAGE_SPEC={'schema': 'enemy-animated153-indexed-coverage-v1', 'members': {'154': {'opaque_hd_pixels': 4944, 'source_cells': 88, 'covered_source_cells': 88, 'empty_native_cells_yx': [], 'palette_allowed': [112, 119, 120, 121, 122, 123, 124, 125], 'payload_sha256': 'd4dbcaef03b1479ddb372a4df4d3ac775eeaf8f9b449c2a2b5e496f6f936954d', 'payload_fnv1a64': 11026697380802109782, 'sha256': '7b5894d8389c3319f52aa8141f70aa2523e590b6ff97bdeca3541a1f36988caf'}, '155': {'opaque_hd_pixels': 3777, 'source_cells': 76, 'covered_source_cells': 76, 'empty_native_cells_yx': [], 'palette_allowed': [112, 119, 120, 121, 122, 123, 124, 125], 'payload_sha256': '381fbfe3787b807a8a844c32157dd6d0a80b851aaa1918d1467ecc3c06b54f28', 'payload_fnv1a64': 12311739024840853719, 'sha256': 'e17729835f0b4fc5ea5ff59a52d1369034f22bc24911042f26888898ded9db0e'}, '153': {'opaque_hd_pixels': 3424, 'source_cells': 76, 'covered_source_cells': 73, 'empty_native_cells_yx': [[5, 0], [5, 1], [5, 2]], 'palette_allowed': [112, 120, 121, 122, 123, 124, 125], 'payload_sha256': '2f737c274a5ebee589b96173930dd345508ecf1bfb0fae82195bbb3619972dd4', 'payload_fnv1a64': 10328367883016278006, 'sha256': '457d330314b37e7dd12d927256c0db56f2f66fd017f410f56540d1bd00ff1884'}}, 'authoring_exception': '153 empty y5x0..2 provisionally accepted; no source-mask/collision/safety relaxation; scenevisualpending'}
REGISTRATION_SPEC={'schema': 'enemy-animated153-registration-v1', 'pillow': '12.3.0', 'alpha_bbox_threshold': 8, 'alpha_final_threshold': 128, 'resample': 'LANCZOS', 'palette_tie_order': 'ascending allowed original indices', 'canvas': [96, 112], 'members': {'154': {'raw': 'raw-three-phases-v3.png', 'raw_size': [2014, 781], 'panel': [0, 0, 671, 781], 'bbox': [80, 82, 565, 701], 'resize': [96, 115], 'paste': [0, -4]}, '155': {'raw': 'raw-three-phases-v3.png', 'raw_size': [2014, 781], 'panel': [671, 0, 1343, 781], 'bbox': [36, 148, 663, 701], 'resize': [96, 103], 'paste': [3, 6]}, '153': {'raw': 'raw-153-v4.png', 'raw_size': [1199, 1312], 'panel': [0, 0, 1199, 1312], 'bbox': [24, 57, 1199, 1272], 'resize': [96, 96], 'paste': [-3, 8]}}}
INPUT_PINS=SELECTION_SPEC["inputs"]

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

def decode_rle(raw):
    if type(raw)is not bytes or len(raw)>512:fail('Invalid bounded RLE')
    src=[0]*168;mask=[0]*168;x=y=p=0
    while p<len(raw):
        code=raw[p];p+=1
        if code==15:
            if p!=len(raw):fail('Trailing RLE')
            return src,mask
        x+=code&15;n=code>>4
        if not n:y+=1;x-=12
        else:
            for _ in range(n):
                if p>=len(raw) or not 0<=x<12 or not 0<=y<14:fail('Invalid RLE geometry')
                src[y*12+x]=raw[p];mask[y*12+x]=1;x+=1;p+=1
    fail('Unterminated RLE')

def source_reference(root):
    j=parse(single_input(root,REFERENCE,INPUT_PINS[REFERENCE]))
    if set(j)!={'153','154','155'}:fail('Expected exact original banana family')
    for s in SELECTORS:
        r=j[str(s)];src,mask=decode_rle(bytes.fromhex(r['rle_hex']))
        if r['width']!=12 or r['height']!=14 or src!=r['palette_indices_row_major'] or mask!=r['mask_row_major'] or sum(mask)!=COVERAGE_SPEC['members'][str(s)]['source_cells']:fail('Changed source RLE witness')
        if sha(bytes.fromhex(r['rle_hex']))!=r['rle_sha256']:fail('Changed RLE hash')
        if sha(bytes(r['observed_palette_rgb768']))!='d4c24a49efb588abd6dc1ffd0f0d1279a498c422cdd26fba4fc921b07f8c159f':fail('Changed observed palette')
    return j

def name(identity,density=8):
    if type(identity)is not int or type(density)is not int or (identity,density)not in PAIRS:fail('Unknown banana identity/density')
    return f'enemy-projectile-animated153-{identity-1570000}-{density}.hda'
def png(identity,density=8):
    name(identity,density);return ROOT+f'/projectile-animated153-{identity-1570000}-registered.png'
def coverage(root):
    j=parse(single_input(root,COVERAGE,INPUT_PINS[COVERAGE]))
    if not exact(j,COVERAGE_SPEC):fail('Changed finite coverage exception contract')
    return j
def selection(root,raw,candidate=False):
    if type(candidate)is not bool:fail('Expected boolean candidate')
    j=parse(raw);want=dict(SELECTION_SPEC,schema=CANDIDATE_SCHEMA if candidate else SCHEMA)
    if not exact(j,want):fail('Changed finite banana selection')
    for p,h in INPUT_PINS.items():single_input(root,p,h)
    source_reference(root);coverage(root)
    if not exact(parse(read(root,REGISTRATION)),REGISTRATION_SPEC):fail('Changed registration')
    return j

def validate_payload(root,selector,payload,contract=None):
    if type(selector)is not int or selector not in SELECTORS or type(payload)not in(bytes,bytearray)or len(payload)!=43008:fail('Invalid complete indexed payload')
    contract=coverage(root)if contract is None else contract
    if not exact(contract,COVERAGE_SPEC):fail('Changed coverage argument')
    m=contract['members'][str(selector)];ref=source_reference(root)[str(selector)];mask=ref['mask_row_major'];cells=set();indices=set();opaque=0
    for y in range(112):
        for x in range(96):
            q=payload[4*(y*96+x):4*(y*96+x)+4];cell=(y//8)*12+x//8
            if q[3]not in(0,255):fail('Nonbinary alpha')
            if not q[3]:
                if any(q):fail('Nonzero transparent texel')
            else:
                if not mask[cell]or q[1]or q[2]or q[0]not in m['palette_allowed']:fail('Invalid encoding/palette/support')
                cells.add(cell);indices.add(q[0]);opaque+=1
    missing=[[c//12,c%12]for c,v in enumerate(mask)if v and c not in cells]
    if missing!=m['empty_native_cells_yx']or len(cells)!=m['covered_source_cells']or opaque!=m['opaque_hd_pixels']or sorted(indices)!=m['palette_allowed']:fail('Changed explicit coverage/opacity/palette')
    if sha(payload)!=m['payload_sha256']or int(fnv(payload),16)!=m['payload_fnv1a64']:fail('Changed selected payload')
    return sorted(cells)
def validate_hda(root,identity,blob):
    name(identity);s=identity-1570000;m=COVERAGE_SPEC['members'][str(s)]
    if type(blob)is not bytes or len(blob)!=43036 or blob[:28]!=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0):fail('Changed indexed transport')
    validate_payload(root,s,blob[28:])
    if sha(blob)!=m['sha256']:fail('Changed HDA hash')
    return True

def generate(root,raw,candidate=False):
    if PILLOW_VERSION!='12.3.0':fail('Fixed Pillow12.3.0 required')
    j=selection(root,raw,candidate);reference=source_reference(root);pngs={};blobs={}
    for s in SELECTORS:
        reg=REGISTRATION_SPEC['members'][str(s)];r=reference[str(s)];p=r['observed_palette_rgb768'];allowed=r['allowed_indices'];colors={v:tuple(p[v*3:v*3+3])for v in allowed}
        with Image.open(io.BytesIO(single_input(root,INPUT_ROOT+'/'+reg['raw'],INPUT_PINS[INPUT_ROOT+'/'+reg['raw']])))as rawim:
            if rawim.format!='PNG'or rawim.mode!='RGBA'or list(rawim.size)!=reg['raw_size']or getattr(rawim,'n_frames',1)!=1:fail('Changed raw PNG geometry/mode')
            panel=rawim.crop(reg['panel']);bbox=panel.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
            if list(bbox or())!=reg['bbox']:fail('Changed raw alpha bbox')
            tile=Image.new('RGBA',(96,112));tile.paste(panel.crop(bbox).resize(reg['resize'],Image.Resampling.LANCZOS),tuple(reg['paste']))
        registered=Image.new('RGBA',(96,112));inp=tile.load();out=registered.load();payload=bytearray()
        for y in range(112):
            for x in range(96):
                q=inp[x,y]
                if not r['mask_row_major'][(y//8)*12+x//8]or q[3]<128:payload.extend(bytes(4));continue
                v=min(allowed,key=lambda v:sum((q[k]-colors[v][k])**2 for k in range(3)))
                out[x,y]=colors[v]+(255,);payload.extend((v,0,0,255))
        identity=1570000+s;validate_payload(root,s,payload,COVERAGE_SPEC);blob=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0)+payload;validate_hda(root,identity,blob)
        buf=io.BytesIO();registered.save(buf,format='PNG',compress_level=6);pngs[png(identity)]=buf.getvalue();blobs[(identity,8)]=blob
    return dict(j,schema=SCHEMA),pngs,blobs

def payload_header(pins):
    if type(pins)is not dict or set(pins)!=set(PAIRS):fail('Expected finite payload pins')
    lines=['/* Namespace157 indexed banana art; 153 has explicit73/76coverage exception. Scene review pending. */','#ifndef CURRENT_PROJECTILE_ANIMATED153_PAYLOAD_PINS_H','#define CURRENT_PROJECTILE_ANIMATED153_PAYLOAD_PINS_H','#include <stdint.h>','#define CURRENT_PROJECTILE_ANIMATED153_ART_QUALIFIED 1']
    for i,d in PAIRS:
        if pins[(i,d)]!=f"{COVERAGE_SPEC['members'][str(i-1570000)]['payload_fnv1a64']:016x}":fail('Changed pin')
        lines.append(f'#define CURRENT_PROJECTILE_ANIMATED153_{i}_PAYLOAD_FNV UINT64_C(0x{pins[(i,d)]})')
    return ('\n'.join(lines+['#endif',''])).encode()
def rows_for(selected,blobs):
    if not exact(selected,SELECTION_SPEC)or type(blobs)is not dict or set(blobs)!=set(PAIRS):fail('Changed finite output set')
    for i,d in PAIRS:
        b=blobs[(i,d)]
        if type(b)is not bytes or len(b)!=43036 or b[:28]!=struct.pack('<4s6I',b'HDR1',i,8,12,14,0,0)or sha(b)!=COVERAGE_SPEC['members'][str(i-1570000)]['sha256']:fail('Changed rows transport')
    return [dict(identity=i,density=d,encoding=ENCODING,source_path=ROOT+'/'+name(i,d),destination='assets/gameplay/'+name(i,d),sha256=sha(blobs[(i,d)]))for i,d in PAIRS]
def input_paths(root):
    selection(root,read(root,SELECTION))
    return {SELECTION,MAPPING,HEADER}|set(INPUT_PINS)|{png(i,d)for i,d in PAIRS}|{ROOT+'/'+name(i,d)for i,d in PAIRS}
def load(root):
    selected,pngs,blobs=generate(root,read(root,SELECTION));rows=rows_for(selected,blobs)
    for p,b in {**pngs,**{r['source_path']:blobs[(r['identity'],r['density'])]for r in rows}}.items():
        if read(root,p)!=b:fail('Stale derivative: '+p)
    expected=dict(schema=MAPPING_SCHEMA,selection=SELECTION,version=selected['version'],files=rows)
    if not exact(parse(read(root,MAPPING)),expected):fail('Stale mapping')
    if read(root,HEADER)!=payload_header({pair:fnv(b[28:])for pair,b in blobs.items()}):fail('Stale payload header')
    return {r['destination']:r for r in rows}
def validate_runtime_rows(root,manifest,required=False):
    if type(required)is not bool or type(manifest)is not dict or type(manifest.get('files'))is not list:fail('Invalid manifest container')
    rows=[];stem='enemy-projectile-animated153-'
    for r in manifest['files']:
        if type(r)is not dict or type(r.get('source_path'))is not str or type(r.get('destination'))is not str:fail('Invalid row paths')
        source=r['source_path'].casefold();dest=r['destination'].casefold();revision=r.get('revision')
        if (type(r.get('identity'))is int and 1570000<=r['identity']<1580000)or source.startswith(ROOT+'/')or source.rsplit('/',1)[-1].startswith(stem)or dest.rsplit('/',1)[-1].startswith(stem)or(type(revision)is str and revision.casefold()==REVISION):rows.append(r)
    if not required and not rows:return
    expected=load(root)
    if len(rows)!=3 or {r['destination']for r in rows}!=set(expected):fail('Exactly3current banana consumers required')
    for r in rows:
        want=expected[r['destination']]
        if r['source_path']!=want['source_path']or r.get('sha256')!=want['sha256']or r.get('group')!='gameplay'or r.get('revision')!=REVISION or r.get('encoding')!=ENCODING:fail('Stale banana consumer/encoding')
        for k in ('identity','density'):
            if type(r.get(k))is not int or r[k]!=want[k]:fail('Missing/contradictory identity/density')
