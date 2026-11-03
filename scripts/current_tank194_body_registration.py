"""Finite public-source tank194 aliases and C pins. No artwork derivation.

The two aliases preserve complete existing HDR1 bytes and identities1010041/
1010131. They are outside the unchanged legacy120 global registry. Original
bank/HDT bytes are optional verification inputs, never generation dependencies.
"""
from pathlib import Path, PurePosixPath
import hashlib, json, stat, struct

PROOF='packaging/tank194-body-source-proof-v1.json'
PROOF_SHA256='0b3b69662e1bb820d1a5e0d07a16c91417d88ed1885d673fac2b79de0a6742c8'
HEADER='src/global_tank194_pins.h'
PREFIX='assets/hd/global-assets-v1/content/'
REVISION='canonical-tank194-body-reuse-v1'
ENCODING='rgba-straight-alpha-v1'
IDENTITIES=(1010041,1010131)
BASES=(91,93)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def fnv(raw):
    value=14695981039346656037
    for byte in raw:value=((value^byte)*1099511628211)&((1<<64)-1)
    return f'{value:016x}'
def relative(name):
    if not isinstance(name,str):raise ValueError('Expected relative path')
    path=PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or str(path)!=name or not name:raise ValueError('Unsafe source path')
    return path

def checked_path(root,name,limit=1024*1024):
    root=Path(root).absolute();path=relative(name);cursor=root
    if root.is_symlink() or not root.is_dir():raise ValueError('Expected regular source root')
    for part in path.parts:
        cursor=cursor/part
        if cursor.is_symlink():raise ValueError('Symlink source rejected')
    info=cursor.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size>limit:raise ValueError('Nonregular or oversized source')
    return cursor,info.st_size

def regular(root,name,limit=1024*1024):
    cursor,size=checked_path(root,name,limit);raw=cursor.read_bytes()
    if len(raw)!=size:raise ValueError('Source changed while reading')
    return raw

def object_bytes(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('Duplicate JSON key')
            result[key]=value
        return result
    def nonfinite(value):raise ValueError('Nonfinite JSON value')
    value=json.loads(raw,object_pairs_hook=pairs,parse_constant=nonfinite)
    if type(value)is not dict:raise ValueError('Expected JSON object')
    return value

def authority(root,proof_root=None):
    raw=regular(proof_root or root,PROOF)
    if sha(raw)!=PROOF_SHA256:raise ValueError('Unreviewed finite tank194 proof')
    p=object_bytes(raw)
    if p['schema']!='opentyrian-tank194-body-source-proof-v1':raise ValueError('Wrong proof schema')
    refs={}
    for name,row in p['public_sources'].items():
        data=regular(root,row['path'])
        if len(data)!=row['bytes'] or sha(data)!=row['sha256'] or blob(data)!=row['git_blob']:raise ValueError('Public authority reference changed: '+name)
        refs[name]=object_bytes(data)
    legacy=refs['legacy_source_proof'];registry=refs['legacy_global_registry']
    if len(registry['resources'])!=120 or len(registry['families'])!=14:raise ValueError('Legacy registry membership changed')
    if tuple(r['identity'] for r in p['resources'])!=IDENTITIES or tuple(r['base'] for r in p['resources'])!=BASES:raise ValueError('Wrong finite body identities')
    frames={f['base_id']:f for f in legacy['frames']}
    raw_cells={c['id']:c['source_record_sha256'] for f in legacy['frames'] for c in f['cells']}
    for tile in p['original_source']['tiles']:
        if tile['raw_sha256']!=raw_cells[tile['legacy_index']]:raise ValueError('Original tile reuse proof differs from public legacy proof')
    for c in p['original_source']['composites']:
        old=frames[c['legacy_base']]
        if c['indices_sha256']!=old['indices_sha256'] or c['mask_sha256']!=old['alpha_sha256']:raise ValueError('Composite reuse proof differs from public legacy proof')
    family=next(f for f in registry['families'] if f['name']==p['palette']['family'])
    pal=family['source_identity']['palette'];ids=pal.get('indices',list(range(pal.get('first_index',0),pal.get('first_index',0)+pal.get('count',0))))
    colors=dict(zip(ids,pal['rgb_hex']))
    if len(p['palette']['indices'])!=18 or any(i not in colors for i in p['palette']['indices']):raise ValueError('Finite palette selection changed')
    return p,{i:colors[i] for i in p['palette']['indices']}

def canonical(root,p):
    result={}
    for r in p['resources']:
        row=r['manual_row'];raw=regular(root,row['source_path'])
        if len(raw)!=172060 or len(raw)!=row['bytes'] or sha(raw)!=row['sha256'] or blob(raw)!=row['git_blob']:raise ValueError('Canonical body material changed')
        if struct.unpack('<4s4I2i',raw[:28])!=(b'HDR1',r['identity'],*r['header']):raise ValueError('Body HDR1 geometry/identity changed')
        if fnv(raw[28:])!=r['payload_fnv64']:raise ValueError('Body payload changed')
        result[r['identity']]=raw
    return result

def pins_header(p,colors):
    lines=['/* SPDX-License-Identifier: GPL-2.0-or-later',
           ' * Generated from '+PROOF+'.',
           ' * Rebuild with scripts/build_tank194_body_registration.py.',
           ' * Source proof SHA256: '+PROOF_SHA256+' */',
           '#ifndef GLOBAL_TANK194_PINS_H','#define GLOBAL_TANK194_PINS_H','#include "global_asset_registry.h"',
           f"#define GLOBAL_TANK194_BANK_BYTES {p['original_source']['bank']['bytes']}u",
           f"#define GLOBAL_TANK194_BANK_FNV UINT64_C(0x{p['original_source']['bank']['fnv64']})",
           'static const GlobalAssetResource global_tank194_resources[2] = {']
    for r in p['resources']:
        d,w,h,x,y=r['header'];row=r['manual_row']
        lines.append(f' {{{r["identity"]}u,{row["bytes"]}u,{d}u,{w}u,{h}u,{x},{y},"content/{row["sha256"]}.hda",UINT64_C(0x{r["payload_fnv64"]})}},')
    lines+=['};','static const GlobalAssetSourceTile global_tank194_source[8] = {']
    lines += [f' {{{t["index"]}u,UINT64_C(0x{t["decoded_fnv64"]})}},' for t in p['original_source']['tiles']]
    lines+=['};','static const GlobalAssetPaletteColor global_tank194_palette[] = {']
    lines += [f' {{{i}u,0x{colors[i]}u}},' for i in p['palette']['indices']]
    lines+=['};',f'static const uint64_t global_tank194_record_fnv[] = {{UINT64_C(0x{p["original_source"]["record"]["fnv64"]})}};','#endif','']
    return '\n'.join(lines).encode('utf-8')

def generate(root,proof_root=None):
    p,colors=authority(root,proof_root);data=canonical(root,p)
    result={PREFIX+sha(raw)+'.hda':raw for raw in data.values()}
    result[HEADER]=pins_header(p,colors)
    return result

def rows_for(root,proof_root=None):
    p,_=authority(root,proof_root);data=canonical(root,p);rows=[]
    for r in p['resources']:
        raw=data[r['identity']];digest=sha(raw)
        rows.append(dict(source_path=PREFIX+digest+'.hda',destination='assets/global/content/'+digest+'.hda',group='global-source-identity',revision=REVISION,identity=r['identity'],density=8,encoding=ENCODING,canonical_source=r['manual_row']['source_path'],bytes=len(raw),sha256=digest,git_blob=blob(raw)))
    return sorted(rows,key=lambda row:row['destination'])

def load(root,proof_root=None):
    for path,expected in generate(root,proof_root).items():
        if regular(root,path)!=expected:raise ValueError('Stale body alias or generated header: '+path)
    return {row['destination']:row for row in rows_for(root,proof_root)}

def validate_runtime_rows(root,manifest,required=False,proof_root=None):
    rows=manifest.get('files')
    if type(rows)is not list or any(type(row)is not dict for row in rows):raise ValueError('Expected finite runtime rows')
    p,_=authority(root,proof_root);manual={r['manual_row']['source_path']:r['manual_row'] for r in p['resources']}
    hashes={r['manual_row']['sha256'] for r in p['resources']};sources={PREFIX+h+'.hda' for h in hashes};destinations={'assets/global/content/'+h+'.hda' for h in hashes};selected=[];seen_manual=set()
    for row in rows:
        source=row.get('source_path');dest=row.get('destination');identity=row.get('identity')
        if isinstance(source,str) and source in manual:
            if source in seen_manual or row!=manual[source] or type(row.get('bytes'))is not int:raise ValueError('Changed or duplicate original gameplay body row')
            seen_manual.add(source);continue
        match=(source in sources if isinstance(source,str) else False) or (dest in destinations if isinstance(dest,str) else False) or (type(identity)is int and identity in IDENTITIES) or row.get('revision')==REVISION or (isinstance(row.get('sha256'),str) and row['sha256']in hashes)
        if isinstance(source,str) and source.endswith('.hda'):
            relative(source);path=Path(root)/source
            if path.exists() or path.is_symlink():
                q,_=checked_path(root,source,64*1024*1024)
                with q.open('rb') as stream:head=stream.read(8)
                if len(head)==8 and head[:4]==b'HDR1' and struct.unpack_from('<I',head,4)[0]in IDENTITIES:match=True
        if match:selected.append(row)
    if not selected and not required:return
    expected=load(root,proof_root)
    if len(selected)!=2 or {row.get('destination') for row in selected}!=set(expected):raise ValueError('Expected exactly two tank194 body aliases')
    for row in selected:
        if type(row.get('identity'))is not int or type(row.get('density'))is not int or type(row.get('bytes'))is not int or row!=expected[row['destination']]:raise ValueError('Changed body alias metadata')

def verify_original_data(root,data_root,proof_root=None):
    """Optional audit of caller-owned originals. No copies or original bytes returned."""
    p,_=authority(root,proof_root);spec=p['original_source'];bs=spec['bank'];rs=spec['record']
    bank=regular(data_root,bs['name']);hdt=regular(data_root,rs['file'],4*1024*1024)
    if len(bank)!=bs['bytes'] or sha(bank)!=bs['sha256'] or fnv(bank)!=bs['fnv64'] or sha(hdt)!=rs['file_sha256']:raise ValueError('Original data authority mismatch')
    record=hdt[rs['offset']:rs['offset']+rs['bytes']]
    if len(record)!=77 or sha(record)!=rs['sha256'] or fnv(record)!=rs['fnv64']:raise ValueError('Original actor194 record mismatch')
    decoded={}
    for tile in spec['tiles']:
        pos=struct.unpack_from('<H',bank,(tile['index']-1)*2)[0];start=pos;x=y=0;idx=bytearray(168);mask=bytearray(168)
        while True:
            if pos>=len(bank):raise ValueError('Truncated source tile')
            code=bank[pos];pos+=1
            if code==15:break
            x+=code&15;count=code>>4
            if not count:y+=1;x-=12
            for _ in range(count):
                if not(0<=x<12 and 0<=y<14 and pos<len(bank)):raise ValueError('Invalid source tile')
                idx[y*12+x]=bank[pos];mask[y*12+x]=255;pos+=1;x+=1
        if sha(bank[start:pos])!=tile['raw_sha256'] or sha(idx)!=tile['indices_sha256'] or sha(mask)!=tile['mask_sha256'] or fnv(idx+mask)!=tile['decoded_fnv64']:raise ValueError('Original source tile mismatch')
        decoded[tile['index']]=(idx,mask)
    for comp in spec['composites']:
        idx=bytearray(672);mask=bytearray(672)
        for part,ox,oy in [(0,0,0),(1,12,0),(19,0,14),(20,12,14)]:
            a,b=decoded[comp['base']+part]
            for y in range(14):
                for x in range(12):idx[(oy+y)*24+ox+x]=a[y*12+x];mask[(oy+y)*24+ox+x]=b[y*12+x]
        if sha(idx)!=comp['indices_sha256'] or sha(mask)!=comp['mask_sha256']:raise ValueError('Original composite mismatch')
    return {'status':'PASS','scope':'optional original bank/record/tile/composite fingerprints only','tiles':8,'poses':2}
