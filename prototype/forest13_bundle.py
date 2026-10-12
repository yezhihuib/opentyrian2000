"""Finite forest canopy: selected bases remain separate from the world atlas."""
from pathlib import Path
import hashlib,json,struct
from PIL import Image
from world_material_bundle import checked_path,fnv64

IDS=[211,212,213,215,221,222,223,224,225,231,232,233,234]
INVENTORY='e734d037291c47d9b47ffddc42a0b1079d9918aaf3297187cb0236dbbe6ce6ea'
COMPOSITION='69b44242c9bcb001a46dc6ccc25d6a5fcbcd43824874217149dd8a3575f22015'
ATLAS='e71a1b179c85b177cb8e094703f7376c88e4aacc99f2cae5837d6757cd4b57f7'
PIXELS=192*224
ATLAS_BYTES=768*896*4
PAYLOAD_BYTES=ATLAS_BYTES+13*PIXELS
FILENAME='forest13-world-material.fcan'
POLICY=b'forest13-coupled-original-v1\n'
def sha(x):return hashlib.sha256(x).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)

def build_bundle(package):
    package=Path(package).resolve()
    inv=checked_path(package,'inventory.json').read_bytes()
    require(sha(inv)==INVENTORY,'Frozen forest inventory mismatch')
    files=json.loads(inv)['files']
    require({str(p.relative_to(package)) for p in package.rglob('*') if p.is_file() or p.is_symlink()}==set(files)|{'inventory.json'},'Unexpected source files')
    for name,digest in files.items():require(sha(checked_path(package,name).read_bytes())==digest,'Frozen file mismatch: '+name)
    raw=checked_path(package,'contracts/composition.json').read_bytes()
    require(sha(raw)==COMPOSITION,'Composition mismatch')
    contract=json.loads(raw)
    require(contract['ids']==IDS and contract['layer']==1 and contract['mode']=='NORMAL' and contract['anchors']==[0,0] and contract['density']==8 and contract['logical_size']==[24,28],'Finite binding contract')
    def decode(name,mode,size):
        with Image.open(checked_path(package,name)) as im:
            require(im.size==size,'Wrong dimensions: '+name)
            return im.convert(mode).tobytes()
    atlas=decode('selected/atlas.png','RGBA',(768,896))
    require(sha(atlas)==ATLAS and all(a==255 for a in atlas[3::4]),'Opaque atlas mismatch')
    require([r['source_id'] for r in contract['selected']]==IDS,'Finite record order')
    parts=[atlas];records=[];source=[]
    for i,row in enumerate(contract['selected']):
        ident=IDS[i];slot=336+i
        require(row['proposed_slot']==slot,'Finite slot mismatch')
        base=decode(row['base_path'],'RGBA',(192,224));mask=decode(row['mask_path'],'L',(192,224))
        require(sha(base)==row['base_rgba_sha256'] and all(a==255 for a in base[3::4]),'Opaque base mismatch')
        require(sha(mask)==row['mask_l8_sha256'] and any(mask),'Mask mismatch')
        header=b'HDR1'+struct.pack('<6I',2010000+ident,8,24,28,0,0)
        require(row['header_u32']==[2010000+ident,8,24,28,0,0],'HDA geometry mismatch')
        require(checked_path(package,row['hda_path']).read_bytes()==header+base and sha(header+base)==row['hda_sha256'],'Selected HDA mismatch')
        records.append({'index':ident,'slot':slot,'mask_offset':ATLAS_BYTES+i*PIXELS,'source_fnv64':fnv64(base)})
        parts.append(mask);source.append({'id':ident,'hda_sha256':sha(header+base),'rgba_sha256':sha(base),'mask_sha256':sha(mask)})
    header=b'FCANAT1\0'+struct.pack('<6I',1,13,768,896,8,PAYLOAD_BYTES)
    header+=b''.join(struct.pack('<3I',201,r['index'],r['mask_offset']) for r in records)
    blob=header+b''.join(parts)
    require(len(header)==188 and len(blob)==3311804,'Finite bundle size')
    receipt={'filename':FILENAME,'bytes':len(blob),'header_bytes':len(header),'payload_bytes':PAYLOAD_BYTES,'sha256':sha(blob),'fnv64':f'{fnv64(blob):016x}','inventory_sha256':INVENTORY,'composition_sha256':COMPOSITION,'atlas_rgba_sha256':ATLAS,'sources':source,'checksum_purpose':'accidental corruption only; not authentication','policy':'absent declaration retains selected-pack art; present invalid declaration or required input disables only forest13 to indexed original'}
    return blob,records,receipt

def render_header(records,receipt):
    return '\n'.join(['/* Generated finite forest contract; FNV is not authentication. */',
      '#define FOREST13_BUNDLE_RECORD_COUNT 13u',
      '#define FOREST13_BUNDLE_HEADER_BYTES 188u',
      f'#define FOREST13_BUNDLE_PAYLOAD_BYTES {PAYLOAD_BYTES}u',
      f'#define FOREST13_BUNDLE_FILE_BYTES {receipt["bytes"]}u',
      '#define FOREST13_BUNDLE_FNV64 UINT64_C(0x'+receipt['fnv64']+')',
      'static const Forest13Record forest13_records[13]={',
      *[' {'+','.join(str(r[k])+'u' for k in ('index','slot','mask_offset'))+',UINT64_C(0x'+f'{r["source_fnv64"]:016x}' +')},' for r in records],'};',''])
