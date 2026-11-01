"""Closed canonical7-to-mirror45 indexed authoring; not runtime qualification.
Namespace156 alone consumes index-coded HDR1; never generic straight RGBA.
"""
from pathlib import Path, PurePosixPath
import hashlib,io,json,re,stat,struct
from PIL import Image,__version__ as PILLOW_VERSION
SELECTORS=(7,45)
IDS=(1560007,1560045)
PAIRS=tuple((i,8)for i in IDS)
INPUT_ROOT='authoring-inputs/projectile-bolts745-current'
ROOT='assets/hd/current-compat/projectile-bolts745'
SELECTION='assets/hd/authoring/projectile-bolts745-current.json'
MAPPING='packaging/current-projectile-bolts745-compatibility.json'
HEADER='src/current_projectile_bolts745_payload_pins.h'
REGISTRATION=INPUT_ROOT+'/registration.json'
COVERAGE=INPUT_ROOT+'/coverage-contract.json'
REFERENCE=INPUT_ROOT+'/source-reference.json'
RAW=INPUT_ROOT+'/raw/generated-7-v1.png'
CANONICAL=INPUT_ROOT+'/canonical-7-registered.png'
SCHEMA='opentyrian-current-projectile-bolts745-authoring-v1'
CANDIDATE_SCHEMA='opentyrian-current-projectile-bolts745-candidate-v1'
MAPPING_SCHEMA='opentyrian-current-projectile-bolts745-compatibility-v1'
REVISION='current-single-source-projectile-bolts745'
# Namespace156 texels are [palette-index,0,0,alpha], NOT generic RGBA.
ENCODING='palette-index-r0-g0-binary-alpha-v1'
SELECTION_SPEC={'schema': 'opentyrian-current-projectile-bolts745-authoring-v1', 'version': 'ordinary-bank8-energy-bolt-7-45-v1', 'canonical_source': 'authoring-inputs/projectile-bolts745-current/canonical-7-registered.png', 'canonical_selector': 7, 'derived_selector': 45, 'transform': 'full-canvas-horizontal-flip', 'encoding': 'palette-index-r0-g0-binary-alpha-v1', 'inputs': {'authoring-inputs/projectile-bolts745-current/raw/generated-7-v1.png': '928fa56d0915122bc7bbc6ae50afba651235977dfc2020cdfa6b2546288619a3', 'authoring-inputs/projectile-bolts745-current/canonical-7-registered.png': 'ae2e1d60b9e48ce1ee2a693d6fa1949d82b5c5daa280e63be252c287cc1302e3', 'authoring-inputs/projectile-bolts745-current/prompt-v1.txt': '6cb27dc56d905402f14efbcfec13fd3ed198a02b01bf9d0d6c3bef773f81bdae', 'authoring-inputs/projectile-bolts745-current/raw/reference-7-16x.png': '2ef3356a16ff111727483ccbb794388edcef566c9bd620385eacd1de60a15a71', 'authoring-inputs/projectile-bolts745-current/source-reference.json': 'e32c07d02e3b03ab86bf6f2c10c1fcd1dd9b822dc8e9e7f4547383564b123d24', 'authoring-inputs/projectile-bolts745-current/provenance.json': '0db6834197c98d533b74b999c2e0d75313233579346c7aa8c8ea41efee07b626', 'authoring-inputs/projectile-bolts745-current/registration.json': 'c1d2700fad563e75541adbc1099c139e7bc9945bfe896308995700660f25c8d8', 'authoring-inputs/projectile-bolts745-current/coverage-contract.json': 'c80f2073e0d66af5f4626afedf7fbaf1ab802bad0b72215122f6cf786b7c4dae'}}
COVERAGE_SPEC={'schema': 'enemy-bolts745-indexed-coverage-v1', 'members': {'7': {'native_mask': '000000000000000000000000000111111100000011111110001111111111011111111111011111111111001111111111000011111110000111111100000000000000000000000000000000000000000000000000', 'native_occupied_cells': 70, 'opaque_hd_pixels': 4029, 'outside_nonzero': 0, 'palette_indices': [112, 113, 114, 115, 116, 117, 119, 120, 122, 123, 125], 'png_sha256': 'ae2e1d60b9e48ce1ee2a693d6fa1949d82b5c5daa280e63be252c287cc1302e3', 'payload_sha256': '1cbd20ae7f9383d1009cb8a73081e5b2cafe0f40e3c3b06767f6d07577fc62f3', 'payload_fnv': 'a9a561e3fab8d9da', 'hda_sha256': 'b41e2dc1e0e4453f2ce764df142e8d92f990d185f57c4c042de3fefbe919df0d'}, '45': {'native_mask': '000000000000000000000000001111111000011111110000111111111100111111111110111111111110111111111100011111110000001111111000000000000000000000000000000000000000000000000000', 'native_occupied_cells': 70, 'opaque_hd_pixels': 4029, 'outside_nonzero': 0, 'palette_indices': [112, 113, 114, 115, 116, 117, 119, 120, 122, 123, 125], 'png_sha256': '7e0501003d10ecc79007c8225048b6ba1caf3622fbd2a65b8170a50b4bf955d1', 'payload_sha256': '78bd2193fb84764c2c868a04add9104be0f7690ecced459889cbee6ad17fb8e3', 'payload_fnv': '78cd699f7811adfa', 'hda_sha256': 'b3137094498d7323a0b7aeaaa93dcd60f00a85129c77edaa0ca97bb29975c3bb'}}}
REGISTRATION_SPEC={'schema': 'enemy-bolts745-registration-v1', 'canonical_selector': 7, 'derived_selector': 45, 'density': 8, 'canvas': [96, 112], 'raw_visible_alpha_threshold': 8, 'raw_visible_bbox': [58, 281, 1116, 1034], 'resize': [88, 64], 'resample': 'Pillow12.3.0/LANCZOS', 'placement': [8, 16], 'registration_alpha_threshold': 8, 'source_support': 'exact native RLE union of 8x8 cells', 'palette_quantization': 'nearest squared RGB among canonical original opaque indices; native encounter order breaks ties', 'alpha': 'binary0/255; transparent texels allzero', 'derived_transform': 'full-canvas horizontal flip', 'payload_encoding': 'palette-index,0,0,alpha; dynamic engine palette; NOT straight RGBA', 'transport': 'HDR1 namespace156 only', 'png_compress_level': 6}
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
    if set(j)!={'7','45'}:fail('Expected exact ordinary source pair')
    for s in SELECTORS:
        r=j[str(s)];src,mask=decode_rle(bytes.fromhex(r['rle_hex']))
        if r['width']!=12 or r['height']!=14 or r['support']!=70 or src!=r['palette_indices_row_major'] or mask!=r['mask_row_major'] or sum(mask)!=70:fail('Changed original source witness')
    for key in ('palette_indices_row_major','mask_row_major'):
        a=j['7'][key];b=j['45'][key]
        if b!=[a[y*12+11-x] for y in range(14) for x in range(12)]:fail('Not exact source mirror')
    if j['7']['observed_palette_rgb768']!=j['45']['observed_palette_rgb768']:fail('Changed observed palette witness')
    return j

def name(identity,density=8):
    if type(identity)is not int or type(density)is not int or (identity,density)not in PAIRS:fail('Unknown bolts745 identity/density')
    return f'enemy-projectile-bolts745-{identity-1560000}-{density}.hda'
def png(identity,density=8):
    name(identity,density);return ROOT+f'/projectile-bolts745-{identity-1560000}-registered.png'
def coverage(root):
    j=parse(single_input(root,COVERAGE,INPUT_PINS[COVERAGE]))
    if not exact(j,COVERAGE_SPEC):fail('Changed complete coverage contract')
    return j
def selection(root,raw,candidate=False):
    if type(candidate)is not bool:fail('Expected boolean candidate')
    j=parse(raw);want=dict(SELECTION_SPEC,schema=CANDIDATE_SCHEMA if candidate else SCHEMA)
    if not exact(j,want):fail('Changed finite one-source selection')
    for p,h in INPUT_PINS.items():single_input(root,p,h)
    source_reference(root);coverage(root)
    if not exact(parse(read(root,REGISTRATION)),REGISTRATION_SPEC):fail('Changed registration recipe')
    return j

def validate_payload(root,selector,payload,contract=None):
    if type(selector)is not int or selector not in SELECTORS or type(payload)not in (bytes,bytearray) or len(payload)!=43008:fail('Invalid complete indexed payload')
    contract=coverage(root)if contract is None else contract
    if not exact(contract,COVERAGE_SPEC):fail('Changed coverage argument')
    m=contract['members'][str(selector)];mask=m['native_mask'];cells=set();indices=set();opaque=0
    for y in range(112):
        for x in range(96):
            q=payload[4*(y*96+x):4*(y*96+x)+4];cell=(y//8)*12+x//8
            if q[3] not in (0,255):fail('Nonbinary alpha')
            if not q[3]:
                if any(q):fail('Nonzero transparent index texel')
            else:
                if mask[cell]!='1' or q[1] or q[2] or q[0] not in m['palette_indices']:fail('Invalid index/encoding/support')
                cells.add(cell);indices.add(q[0]);opaque+=1
    if len(cells)!=70 or opaque!=4029 or sorted(indices)!=m['palette_indices']:fail('Changed exact coverage/index set')
    if sha(payload)!=m['payload_sha256'] or fnv(payload)!=m['payload_fnv']:fail('Changed selected indexed payload')
    return sorted(cells)
def validate_hda(root,identity,blob):
    name(identity);s=identity-1560000;m=COVERAGE_SPEC['members'][str(s)]
    if type(blob)is not bytes or len(blob)!=43036 or blob[:28]!=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0):fail('Changed namespace156 indexed transport')
    validate_payload(root,s,blob[28:])
    if sha(blob)!=m['hda_sha256']:fail('Changed HDA hash')
    return True

def fixed_png(root,name,size):
    with Image.open(io.BytesIO(single_input(root,name,INPUT_PINS[name])))as im:
        if im.format!='PNG' or im.mode!='RGBA' or list(im.size)!=size or getattr(im,'n_frames',1)!=1:fail('Changed approved PNG geometry/mode')
        return im.copy()
def regenerate_canonical(root,reference):
    raw=fixed_png(root,RAW,[1161,1355]);r=reference['7'];palette=r['observed_palette_rgb768']
    # Dict insertion order follows the original source raster, exactly as the
    # accepted registration. No synthetic pixels are inserted for coverage.
    colors={v:tuple(palette[v*3:v*3+3])for v,m in zip(r['palette_indices_row_major'],r['mask_row_major'])if m}
    bbox=raw.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
    if list(bbox or ())!=[58,281,1116,1034]:fail('Changed raw visible bbox')
    preview=Image.new('RGBA',(96,112));preview.paste(raw.crop(bbox).resize((88,64),Image.Resampling.LANCZOS),(8,16))
    registered=Image.new('RGBA',(96,112));inp=preview.load();out=registered.load()
    for y in range(112):
        for x in range(96):
            if not r['mask_row_major'][(y//8)*12+x//8] or inp[x,y][3]<8:continue
            rgb=inp[x,y][:3];v=min(colors,key=lambda v:sum((rgb[k]-colors[v][k])**2 for k in range(3)))
            out[x,y]=colors[v]+(255,)
    approved=fixed_png(root,CANONICAL,[96,112])
    if registered.tobytes()!=approved.tobytes():fail('Raw registration differs from accepted canonical')
    return approved

def generate(root,raw,candidate=False):
    if PILLOW_VERSION!='12.3.0':fail('Fixed Pillow12.3.0 required')
    j=selection(root,raw,candidate);reference=source_reference(root);canonical=regenerate_canonical(root,reference);pngs={};blobs={}
    p=reference['7']['observed_palette_rgb768'];allowed=COVERAGE_SPEC['members']['7']['palette_indices'];lookup={tuple(p[v*3:v*3+3]):v for v in allowed}
    if len(lookup)!=len(allowed):fail('Ambiguous RGB to source index conversion')
    for s,tile in ((7,canonical),(45,canonical.transpose(Image.Transpose.FLIP_LEFT_RIGHT))):
        payload=bytearray();pixels=tile.tobytes()
        for off in range(0,len(pixels),4):
            q=pixels[off:off+4]
            if q[3]==0:
                if any(q):fail('Noncanonical transparent PNG RGB')
                payload.extend(bytes(4))
            else:
                if q[3]!=255 or tuple(q[:3])not in lookup:fail('Unapproved RGB/alpha in canonical')
                payload.extend((lookup[tuple(q[:3])],0,0,255))
        identity=1560000+s;validate_payload(root,s,payload,COVERAGE_SPEC)
        blob=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0)+payload;validate_hda(root,identity,blob)
        buf=io.BytesIO();tile.save(buf,format='PNG',compress_level=6);encoded=buf.getvalue()
        if sha(encoded)!=COVERAGE_SPEC['members'][str(s)]['png_sha256']:fail('Changed selected PNG encoding')
        pngs[png(identity)]=encoded;blobs[(identity,8)]=blob
    a=blobs[(1560007,8)][28:];b=blobs[(1560045,8)][28:]
    if b!=b''.join(a[4*(y*96+95-x):4*(y*96+96-x)]for y in range(112)for x in range(96)):fail('Indexed mirror mismatch')
    return dict(j,schema=SCHEMA),pngs,blobs

def payload_header(pins):
    if type(pins)is not dict or set(pins)!=set(PAIRS) or any(type(k)is not tuple or len(k)!=2 or any(type(x)is not int for x in k)for k in pins):fail('Expected exact finite payload pins')
    lines=['/* SPDX-License-Identifier: GPL-2.0-or-later',' * Namespace156 only: [palette-index,0,0,binary alpha], NOT straight RGBA. */','#ifndef CURRENT_PROJECTILE_BOLTS745_PAYLOAD_PINS_H','#define CURRENT_PROJECTILE_BOLTS745_PAYLOAD_PINS_H']
    for identity,density in PAIRS:
        h=pins[(identity,density)]
        if type(h)is not str or h!=COVERAGE_SPEC['members'][str(identity-1560000)]['payload_fnv']:fail('Changed indexed payload pin')
        lines.append(f'#define CURRENT_PROJECTILE_BOLTS745_{identity}_PAYLOAD_FNV UINT64_C(0x{h})')
    return ('\n'.join(lines+['#endif',''])).encode()
def rows_for(selected,blobs):
    if not exact(selected,SELECTION_SPEC)or type(blobs)is not dict or set(blobs)!=set(PAIRS)or any(type(k)is not tuple or len(k)!=2 or any(type(x)is not int for x in k)for k in blobs):fail('Changed finite output set')
    for i,d in PAIRS:
        b=blobs[(i,d)]
        if type(b)is not bytes or len(b)!=43036 or b[:28]!=struct.pack('<4s6I',b'HDR1',i,8,12,14,0,0) or sha(b)!=COVERAGE_SPEC['members'][str(i-1560000)]['hda_sha256']:fail('Changed indexed rows transport')
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
    if read(root,HEADER)!=payload_header({pair:fnv(b[28:])for pair,b in blobs.items()}):fail('Stale indexed payload header')
    return {r['destination']:r for r in rows}
def validate_runtime_rows(root,manifest,required=False):
    if type(required)is not bool or type(manifest)is not dict or type(manifest.get('files'))is not list:fail('Invalid manifest container')
    rows=[];stem='enemy-projectile-bolts745-'
    for r in manifest['files']:
        if type(r)is not dict or type(r.get('source_path'))is not str or type(r.get('destination'))is not str:fail('Invalid row paths')
        source=r['source_path'].casefold();dest=r['destination'].casefold();revision=r.get('revision')
        if source.startswith(ROOT+'/') or source.rsplit('/',1)[-1].startswith(stem) or dest.rsplit('/',1)[-1].startswith(stem) or (type(revision)is str and revision.casefold()==REVISION):rows.append(r)
    if not required and not rows:return
    expected=load(root)
    if len(rows)!=2 or {r['destination']for r in rows}!=set(expected):fail('Exactly two current bolts745 consumers required')
    for r in rows:
        want=expected[r['destination']]
        if r['source_path']!=want['source_path']or r.get('sha256')!=want['sha256']or r.get('group')!='gameplay'or r.get('revision')!=REVISION or r.get('encoding')!=ENCODING:fail('Stale bolts745 consumer/encoding')
        for k in ('identity','density'):
            if type(r.get(k))is not int or r[k]!=want[k]:fail('Missing or contradictory identity/density')
