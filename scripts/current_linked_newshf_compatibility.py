"""Fixed whole-master registration for linked NEWSHF171–173; no creative drawing.

Hot overlays contain only deliberate alternate-state changes. Transparent overlay
pixels inherit the cold whole master, so common material edits propagate.
"""
import io
import struct
from PIL import Image
from current_guided_compatibility import read, parse, sha, image
from build_newshf_hd import fnv

INPUT_ROOT = 'authoring-inputs/newshf-linked'
ROOT = 'assets/hd/current-compat/newshf-linked'
HEADER = 'src/current_linked_newshf_hd_assets.h'
SELECTION = 'assets/hd/authoring/newshf-linked.json'
MAPPING = 'packaging/current-linked-newshf-compatibility.json'
IDS = tuple(range(2100009,2100015))
PAIRS = ((171,43),(171,45),(172,81),(172,83),(173,119),(173,121))
INPUTS = ('cold-whole.png','alternate-middle-overlay.png','hot-bottom-overlay.png')
CHANGE_MASKS = ('change-83.png','change-121.png')
CHANGE_SHA256 = {83: '1319d0cabe5bff024706a0b4e010b7f51b6988b4497f433d3569248ccbe5cb87', 121: 'aee48f2bf0af75a69272815a951d25c91d90a5a61d41ff5ed8196936017ee436'}
MASKS = tuple(f'mask-{base}.png' for _,base in PAIRS)
MASK_SHA256 = {43: '655aaa9efdf90fbebc84abc602fc31635453d4f389e456d566c8b5048cd7a3dc', 45: '655aaa9efdf90fbebc84abc602fc31635453d4f389e456d566c8b5048cd7a3dc', 81: '806b5a64666580a7cc9708ed0327e7ff468f097ab80da5374193886e56da9f84', 83: '806b5a64666580a7cc9708ed0327e7ff468f097ab80da5374193886e56da9f84', 119: 'c8ef6c1b536d37604b21f169b2c8572ea04e55252f19c12121a4799314cffe89', 121: 'fa4fb2f9257d0d4af0e3a24a30d824bb96e7f19c97ebb5c32d99a8f50c71b775'}
SCHEMA = 'opentyrian-linked-newshf-authoring-v1'

def name(i): return f'newshf-role{i}-8.hda'
def png(i): return INPUT_ROOT+'/derived/'+name(i).replace('.hda','.png')
def generated_paths(): return {png(i) for i in IDS}
def input_paths(root): return {INPUT_ROOT+'/'+n for n in INPUTS+MASKS+CHANGE_MASKS}|{SELECTION}
def encode_png(im):
    out=io.BytesIO(); im.save(out,format='PNG',optimize=False); return out.getvalue()

def generate(root,raw,candidate=False):
    selected=parse(raw)
    if set(selected)!={'schema','version','inputs'} or selected['schema']!=SCHEMA:
        raise ValueError('Invalid linked selection')
    if not isinstance(selected['version'],str) or not 1<=len(selected['version'])<=128:
        raise ValueError('Invalid linked version')
    expected={INPUT_ROOT+'/'+n for n in INPUTS+MASKS+CHANGE_MASKS}
    if not isinstance(selected['inputs'],dict) or set(selected['inputs'])!=expected:
        raise ValueError('Invalid linked fixed input closure')
    for p,h in selected['inputs'].items():
        if sha(read(root,p))!=h: raise ValueError('Changed linked input: '+p)
    for base,digest in MASK_SHA256.items():
        if sha(read(root,INPUT_ROOT+f'/mask-{base}.png'))!=digest:
            raise ValueError('Immutable native mask changed')
    cold=image(read(root,INPUT_ROOT+'/'+INPUTS[0]),(192,672))
    overlays=[image(read(root,INPUT_ROOT+'/'+n),(192,224)) for n in INPUTS[1:]]
    for im in [cold]+overlays:
        if not set(im.getchannel('A').tobytes()) <= {0,255}:
            raise ValueError('Registered inputs must use binary alpha')
    for overlay,base in zip(overlays,(83,121)):
        raw_mask=read(root,INPUT_ROOT+f'/change-{base}.png')
        if sha(raw_mask)!=CHANGE_SHA256[base]: raise ValueError('Immutable state-change mask changed')
        change=Image.open(io.BytesIO(raw_mask)).convert('L').resize((192,224),Image.Resampling.NEAREST)
        if any(a and not m for a,m in zip(overlay.getchannel('A').tobytes(),change.tobytes())):
            raise ValueError('Alternate overlay changes shared housing outside native state difference')
    pieces=[]
    for level in range(3):
        piece=cold.crop((0,224*level,192,224*(level+1)))
        pieces.append(piece)
        hot=piece.copy()
        if level: hot.paste(overlays[level-1],(0,0),overlays[level-1].getchannel('A'))
        pieces.append(hot)
    pngs,blobs,rows={},{},[]
    for i,((record,base),piece) in enumerate(zip(PAIRS,pieces)):
        mask=Image.open(io.BytesIO(read(root,INPUT_ROOT+f'/mask-{base}.png'))).convert('L')
        if mask.size!=(24,28) or not set(mask.tobytes()) <= {0,255}:
            raise ValueError('Invalid native mask')
        mask=mask.resize((192,224),Image.Resampling.NEAREST)
        # Source-mask registration is exact, not a bounding-box approximation.
        if any(m and not a for m,a in zip(mask.tobytes(),piece.getchannel('A').tobytes())):
            raise ValueError('Registered artwork does not cover native foreground')
        piece.putalpha(mask)
        clean=Image.new('RGBA',piece.size); clean.paste(piece,(0,0),mask); piece=clean
        identity=IDS[i]; data=encode_png(piece); pngs[png(identity)]=data
        blob=struct.pack('<4s6I',b'HDR1',identity,8,24,28,6,7)+piece.tobytes()
        blobs[identity]=blob
        rows.append(dict(identity=identity,record=record,base=base,source_path=ROOT+'/'+name(identity),destination='assets/global/newshf-linked/'+name(identity),source_png=png(identity),source_png_sha256=sha(data),bytes=len(blob),sha256=sha(blob),payload_fnv=f'{fnv(blob[28:]):016x}'))
    if blobs[IDS[0]][28:]!=blobs[IDS[1]][28:]: raise ValueError('Top states must be identical')
    return selected,pngs,blobs,rows

def payload_header(rows):
    if tuple(r['identity'] for r in rows)!=IDS: raise ValueError('Invalid linked rows')
    lines=[f' {{{r["identity"]}u,{r["bytes"]}u,8u,24u,28u,6,7,"newshf-linked/{name(r["identity"])}",UINT64_C(0x{r["payload_fnv"]})}},' for r in rows]
    return ('/* Generated by build_current_linked_newshf.py. */\n#ifndef CURRENT_LINKED_NEWSHF_HD_ASSETS_H\n#define CURRENT_LINKED_NEWSHF_HD_ASSETS_H\n#include "global_asset_registry.h"\nenum { LINKED_NEWSHF_HD_RESOURCE_COUNT = 6 };\nstatic const GlobalAssetResource linked_newshf_hd_resources[6] = {\n'+'\n'.join(lines)+'\n};\n#endif\n').encode()


def load(root):
    """Independently regenerate and verify every installed byte; no receipt trust."""
    raw=read(root,SELECTION)
    selected,pngs,blobs,rows=generate(root,raw)
    expected=dict(schema='opentyrian-linked-newshf-compatibility-v1',selection=SELECTION,files=rows)
    if parse(read(root,MAPPING))!=expected:
        raise ValueError('Linked mapping differs from independently derived rows')
    for p,data in pngs.items():
        if read(root,p)!=data: raise ValueError('Changed derived linked PNG: '+p)
    for identity,data in blobs.items():
        if read(root,ROOT+'/'+name(identity))!=data: raise ValueError('Changed linked transport')
    if read(root,HEADER)!=payload_header(rows): raise ValueError('Changed linked header')
    return {row['destination']:row for row in rows}
