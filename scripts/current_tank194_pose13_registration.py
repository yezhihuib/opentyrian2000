"""Finite public-only pins for deliberate tank194 native13 / visualHD91 adaptation.

Native13 is NOT source-identical to canonical bank1/91. Its independent source
pins and explicit 12-cell difference proof are retained; HDR1 bytes are unchanged.
The earlier seven poses remain unchanged. No originals or art derivation needed.
"""
import struct
from pathlib import Path
import current_tank194_body_registration as body

PROOF='packaging/tank194-pose13-adaptation-material-proof-v1.json'
PROOF_SHA256='bef57599426a60ca3367beaf352a76d022764aa16453a481a742667516658830'
HEADER='src/global_tank194_pose13_pins.h'
HEADER_SHA256='bfb184c7ad6cad417cfef935f5dca915c644fbdd32ccd870efa6e1a6636442e9'
PREFIX=body.PREFIX
REVISION='canonical-tank194-pose13-adaptation-v1'
ENCODING=body.ENCODING
IDENTITIES=(1010091,)
BASES=(13,)
GAMEPLAY_PREFIX='assets/hd/packs/packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test/'


# Audited scalar authority only; no original native pixels or RLE payload shipped.
NATIVE_INDICES_SHA256='ca17c44e49ff7eba0a2268f944a0caf625a34b99c2a3ed67f37c33b21c015218'
NATIVE_MASK_SHA256='8348944dc5f01035c9dc858c0c64b18a05cd6c0458ca55c23e708f5a9bef90d6'
NATIVE_TILE_FNV=('50f14755d21f9880','a61062619a32d462','2c5d83009761ad6b','744069e028db45e6')
# x,y, old coverage/index, actual13 coverage/index. This is not a full grid.
DIFFERENCES=((10,7,True,1,False,0),(7,8,True,1,False,0),
             (10,8,True,2,True,1),(5,12,False,0,True,1),
             (19,16,False,0,True,1),(8,17,False,0,True,1),
             (15,17,True,64,True,1),(16,17,True,16,True,1),
             (17,17,False,0,True,1),(18,17,False,0,True,1),
             (10,19,False,0,True,1),(14,19,False,0,True,1))


def authority(root,proof_root=None):
    raw=body.regular(proof_root or root,PROOF)
    if body.sha(raw)!=PROOF_SHA256:raise ValueError('Unreviewed finite13 adaptation proof')
    p=body.object_bytes(raw)
    old,_=body.authority(root,proof_root)
    if p['bank20_sha256']!=old['original_source']['bank']['sha256'] or p['bank20_fnv']!=old['original_source']['bank']['fnv64']:raise ValueError('13 bank authority changed')
    if p['record194_sha256']!=old['original_source']['record']['sha256'] or p['record194_fnv']!=old['original_source']['record']['fnv64']:raise ValueError('13 actor authority changed')
    if tuple(p['new_member_order'])!=BASES or tuple(p['retained_member_order'])!=(91,93,51,55,15,17,89) or len(p['members'])!=1:raise ValueError('13 membership changed')
    m=p['members'][0];a=p['adaptation']
    if (m['base'],m['cycle'],m['member'])!=(13,1,7) or m['canonical_material']['header']!=[1010091,8,24,28,6,7]:raise ValueError('13 adaptation identity changed')
    if m['exact_native_alias'] is not False or a['exact_native_alias'] is not False:raise ValueError('Native13 must not claim an exact donor alias')
    if m['indices_sha256']!=NATIVE_INDICES_SHA256 or m['mask_sha256']!=NATIVE_MASK_SHA256:raise ValueError('Actual native13 composite changed')
    tiles=m['source_tiles']
    if [t['index'] for t in tiles]!=[13,14,32,33] or tuple(t['decoded_indices_then_coverage_fnv'] for t in tiles)!=NATIVE_TILE_FNV:raise ValueError('Actual native13 tile pins changed')
    if [(t['raw_offset'],t['raw_end_exclusive']) for t in tiles]!=[(2502,2578),(2578,2631),(4951,4985),(4985,5034)]:raise ValueError('Actual native13 source ranges changed')
    legacy_ref=old['public_sources']['legacy_source_proof']
    if a['canonical_source_proof']!={k:legacy_ref[k] for k in ('path','sha256')}:raise ValueError('Donor authority changed')
    legacy=body.object_bytes(body.regular(root,legacy_ref['path']))
    frame=next(f for f in legacy['frames'] if f['base_id']==91)
    if a['canonical_native_base']!=91 or a['canonical_bank1_sha256']!=legacy['original_sources_sha256']['newsh2.shp']:raise ValueError('Donor bank changed')
    if a['canonical_indices_sha256']!=frame['indices_sha256'] or a['canonical_mask_sha256']!=frame['alpha_sha256']:raise ValueError('Donor composite authority changed')
    if m['indices_sha256']==frame['indices_sha256'] or m['mask_sha256']==frame['alpha_sha256']:raise ValueError('Actual native13 was replaced by donor91')
    # One quadrant is shared; the other three are independently pinned differences.
    cells={c['id']:c for c in frame['cells']}
    if [t['raw_rle_sha256']==cells[91+t['index']-13]['source_record_sha256'] for t in tiles]!=[False,True,False,False]:raise ValueError('Native13/donor quadrant relationship changed')
    d=a['differing_cells']
    fields=('x','y','old_covered','old_index','new_covered','new_index')
    if tuple(tuple(c[k] for k in fields) for c in d)!=DIFFERENCES or any(type(c[k])is not bool for c in d for k in ('old_covered','new_covered')):raise ValueError('Explicit native13 differences changed')
    counts={'added_coverage':sum(not c['old_covered'] and c['new_covered'] for c in d),
            'removed_coverage':sum(c['old_covered'] and not c['new_covered'] for c in d),
            'changed_index':sum(c['old_covered'] and c['new_covered'] and c['old_index']!=c['new_index'] for c in d)}
    if counts!=a['difference_counts'] or counts!={'added_coverage':7,'removed_coverage':2,'changed_index':3}:raise ValueError('Native13 difference counts changed')
    if m['native_covered_cells']!=142 or p['native_covered_cells']!=142 or frame['opaque_pixels']+counts['added_coverage']-counts['removed_coverage']!=142:raise ValueError('Native13 coverage count changed')
    registry_ref=old['public_sources']['legacy_global_registry'];pa=p['palette_authority']
    if pa['path']!=body.PROOF or pa['sha256']!=body.PROOF_SHA256 or pa['additional_color_registry']!={k:registry_ref[k] for k in ('path','sha256')}:raise ValueError('13 palette authority changed')
    registry=body.object_bytes(body.regular(root,registry_ref['path']))
    family=next(f for f in registry['families'] if f['name']==old['palette']['family'])
    pal=family['source_identity']['palette'];ids=pal.get('indices',list(range(pal.get('first_index',0),pal.get('first_index',0)+pal.get('count',0))))
    colors=dict(zip(ids,pal['rgb_hex']))
    if p['additional_palette']!=[{'index':116,'rgb':'860400'}] or colors.get(116)!='860400' or any(i not in old['palette']['indices']+[116] for i in m['used_indices']):raise ValueError('13 independent116 gate changed')
    for cell in d:
        for prefix in ('old','new'):
            if cell[prefix+'_rgb']!=list(bytes.fromhex(colors[cell[prefix+'_index']])):raise ValueError('Adaptation difference RGB changed')
    return p


def canonical(root,p):
    result={}
    for member in p['members']:
        material=member['canonical_material'];identity=material['header'][0]
        raw=body.regular(root,material['path'])
        if len(raw)!=172060 or len(raw)!=material['bytes'] or body.sha(raw)!=material['sha256'] or body.blob(raw)!=material['git_blob']:raise ValueError('Canonical13 material changed')
        if struct.unpack('<4s4I2i',raw[:28])!=(b'HDR1',*material['header']):raise ValueError('13 HDR1 geometry or identity changed')
        if body.sha(raw[28:])!=material['payload_sha256'] or body.fnv(raw[28:])!=material['payload_fnv']:raise ValueError('13 payload changed')
        for cell in p['adaptation']['differing_cells']:
            x,y=cell['x'],cell['y']
            alpha=[raw[28+4*((y*8+dy)*192+x*8+dx)+3] for dy in range(8) for dx in range(8)]
            if sum(v!=0 for v in alpha)!=cell['existing_HD_alpha_nonzero'] or [min(alpha),max(alpha)]!=cell['existing_HD_alpha_range']:raise ValueError('HD91 difference-cell alpha annotation changed')
        result[identity]=raw
    return result


def pins_header(p):
    lines=['/* SPDX-License-Identifier: GPL-2.0-or-later',
           ' * Deliberate body13 adaptation using unchanged existing HDR1 material91.',
           ' * Native13 source is independently pinned, not identical to bank1/91.',
           ' * Source/material proof SHA256: '+PROOF_SHA256+' */',
           '#ifndef GLOBAL_TANK194_POSE13_PINS_H','#define GLOBAL_TANK194_POSE13_PINS_H','#include "global_asset_registry.h"',
           'static const GlobalAssetResource global_tank194_pose13_resources[1] = {']
    for member in p['members']:
        r=member['canonical_material'];identity,d,w,h,x,y=r['header']
        lines.append(f' {{{identity}u,{r["bytes"]}u,{d}u,{w}u,{h}u,{x},{y},"content/{r["sha256"]}.hda",UINT64_C(0x{r["payload_fnv"]})}},')
    lines+=['};','static const GlobalAssetSourceTile global_tank194_pose13_source[4] = {']
    lines += [f' {{{t["index"]}u,UINT64_C(0x{t["decoded_indices_then_coverage_fnv"]})}},' for m in p['members'] for t in m['source_tiles']]
    lines+=['};','static const GlobalAssetPaletteColor global_tank194_pose13_palette[1] = {']
    lines += [f' {{{c["index"]}u,0x{c["rgb"]}u}},' for c in p['additional_palette']]
    lines+=['};','#endif','']
    raw='\n'.join(lines).encode('utf-8')
    if body.sha(raw)!=HEADER_SHA256:raise ValueError('Generated13 header differs from qualified source')
    return raw


def generate(root,proof_root=None):
    p=authority(root,proof_root);data=canonical(root,p)
    result={PREFIX+body.sha(raw)+'.hda':raw for raw in data.values()}
    result[HEADER]=pins_header(p)
    return result


def rows_for(root,proof_root=None):
    p=authority(root,proof_root);data=canonical(root,p);rows=[]
    for member in p['members']:
        r=member['canonical_material'];identity=r['header'][0];raw=data[identity];digest=body.sha(raw)
        rows.append(dict(source_path=PREFIX+digest+'.hda',destination='assets/global/content/'+digest+'.hda',group='global-source-identity',revision=REVISION,identity=identity,density=8,encoding=ENCODING,canonical_source=r['path'],bytes=len(raw),sha256=digest,git_blob=body.blob(raw)))
    return sorted(rows,key=lambda row:row['destination'])


def load(root,proof_root=None):
    for path,expected in generate(root,proof_root).items():
        if body.regular(root,path)!=expected:raise ValueError('Stale13 alias or generated header: '+path)
    return {row['destination']:row for row in rows_for(root,proof_root)}


def gameplay_rows(p):
    rows={}
    for member in p['members']:
        material=member['canonical_material'];name=Path(material['path']).name
        row=dict(source_path=GAMEPLAY_PREFIX+name,destination='assets/gameplay/'+name,group='gameplay',revision='reconstructed-local-unpublished',bytes=material['bytes'],sha256=material['sha256'],git_blob=material['git_blob'])
        rows[row['source_path']]=row
    return rows


def validate_runtime_rows(root,manifest,required=False,proof_root=None):
    rows=manifest.get('files')
    if type(rows)is not list or any(type(row)is not dict for row in rows):raise ValueError('Expected finite runtime rows')
    p=authority(root,proof_root);manual=gameplay_rows(p)
    hashes={m['canonical_material']['sha256'] for m in p['members']}
    sources={PREFIX+h+'.hda' for h in hashes};destinations={'assets/global/content/'+h+'.hda' for h in hashes};selected=[];seen_manual=set()
    for row in rows:
        source=row.get('source_path');dest=row.get('destination');identity=row.get('identity')
        if isinstance(source,str) and source in manual:
            if source in seen_manual or row!=manual[source] or type(row.get('bytes'))is not int:raise ValueError('Changed or duplicate original gameplay13 row')
            seen_manual.add(source);continue
        match=(source in sources if isinstance(source,str) else False) or (dest in destinations if isinstance(dest,str) else False) or (type(identity)is int and identity in IDENTITIES) or row.get('revision')==REVISION or (isinstance(row.get('sha256'),str) and row['sha256'] in hashes)
        if isinstance(source,str) and source.endswith('.hda'):
            body.relative(source);path=Path(root)/source
            if path.exists() or path.is_symlink():
                q,_=body.checked_path(root,source,64*1024*1024)
                with q.open('rb') as stream:head=stream.read(8)
                if len(head)==8 and head[:4]==b'HDR1' and struct.unpack_from('<I',head,4)[0] in IDENTITIES:match=True
        if match:selected.append(row)
    if not selected and not required:return
    expected=load(root,proof_root)
    if len(selected)!=1 or {row.get('destination') for row in selected}!=set(expected):raise ValueError('Expected exactly one pose13 alias')
    for row in selected:
        if type(row.get('identity'))is not int or type(row.get('density'))is not int or type(row.get('bytes'))is not int or row!=expected[row['destination']]:raise ValueError('Changed 13 pose alias metadata')


def input_paths(root):
    p=authority(root);old,_=body.authority(root)
    return sorted({PROOF,body.PROOF,*[r['path'] for r in old['public_sources'].values()],*[m['canonical_material']['path'] for m in p['members']]})
