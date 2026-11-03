"""Finite public-only aliases and exact C pins for tank194 poses51/55.

Reuses existing HDR1 materials39/43. The original91/93 proof, header and pair
remain unchanged. No artwork derivation or original game data is required.
"""
import struct
from pathlib import Path
import current_tank194_body_registration as body

PROOF='packaging/tank194-extra-pose-material-proof-v1.json'
PROOF_SHA256='0a882328e1bbffb50f51a1d157f24c80cd77019e80e190b7eb9997d210b5357a'
HEADER='src/global_tank194_extra_pins.h'
HEADER_SHA256='3568d0b6162c121b7153920d7cd94df47bee227a1c945ac161823af7353d82c6'
PREFIX=body.PREFIX
REVISION='canonical-tank194-extra-poses-reuse-v1'
ENCODING=body.ENCODING
IDENTITIES=(1010039,1010043)
BASES=(51,55)
GAMEPLAY_PREFIX='assets/hd/packs/packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test/'


def authority(root,proof_root=None):
    raw=body.regular(proof_root or root,PROOF)
    if body.sha(raw)!=PROOF_SHA256:raise ValueError('Unreviewed finite extra-pose proof')
    p=body.object_bytes(raw)
    old,_=body.authority(root,proof_root)
    if p['bank20_sha256']!=old['original_source']['bank']['sha256'] or p['bank20_fnv']!=old['original_source']['bank']['fnv64']:raise ValueError('Extra bank authority changed')
    if p['record194_sha256']!=old['original_source']['record']['sha256'] or p['record194_fnv']!=old['original_source']['record']['fnv64']:raise ValueError('Extra actor authority changed')
    if tuple(p['new_member_order'])!=BASES or tuple(p['retained_member_order'])!=body.BASES:raise ValueError('Extra pose membership changed')
    legacy=body.object_bytes(body.regular(root,old['public_sources']['legacy_source_proof']['path']))
    registry=body.object_bytes(body.regular(root,old['public_sources']['legacy_global_registry']['path']))
    frames={f['base_id']:f for f in legacy['frames']}
    for member,base,identity in zip(p['members'],BASES,IDENTITIES):
        if member['base']!=base or member['canonical_material']['header']!=[identity,8,24,28,6,7]:raise ValueError('Extra HDR1 contract changed')
        frame=frames[base-12]
        if member['indices_sha256']!=frame['indices_sha256'] or member['mask_sha256']!=frame['alpha_sha256']:raise ValueError('Extra composite differs from public proof')
        cells={c['id']:c for c in frame['cells']}
        if [t['index'] for t in member['source_tiles']]!=[base+d for d in (0,1,19,20)]:raise ValueError('Extra tile membership changed')
        for tile in member['source_tiles']:
            cell=cells[tile['index']-12]
            if tile['raw_rle_sha256']!=cell['source_record_sha256'] or tile['raw_end_exclusive']-tile['raw_offset']!=cell['bytes']:raise ValueError('Extra tile differs from public proof')
    family=next(f for f in registry['families'] if f['name']==old['palette']['family'])
    pal=family['source_identity']['palette']
    ids=pal.get('indices',list(range(pal.get('first_index',0),pal.get('first_index',0)+pal.get('count',0))))
    colors=dict(zip(ids,pal['rgb_hex']))
    if [c['index'] for c in p['additional_palette']]!=[10,16,116] or any(colors.get(c['index'])!=c['rgb'] for c in p['additional_palette']):raise ValueError('Extra palette differs from public registry')
    return p


def canonical(root,p):
    result={}
    for member in p['members']:
        material=member['canonical_material'];identity=material['header'][0]
        raw=body.regular(root,material['path'])
        if len(raw)!=172060 or len(raw)!=material['bytes'] or body.sha(raw)!=material['sha256'] or body.blob(raw)!=material['git_blob']:raise ValueError('Canonical extra material changed')
        if struct.unpack('<4s4I2i',raw[:28])!=(b'HDR1',*material['header']):raise ValueError('Extra HDR1 geometry or identity changed')
        if body.sha(raw[28:])!=material['payload_sha256'] or body.fnv(raw[28:])!=material['payload_fnv']:raise ValueError('Extra payload changed')
        result[identity]=raw
    return result


def pins_header(p):
    lines=['/* SPDX-License-Identifier: GPL-2.0-or-later',
           ' * Finite extra body51/55 pins from unchanged existing HDR1 materials39/43.',
           ' * Source/material proof SHA256: '+PROOF_SHA256+' */',
           '#ifndef GLOBAL_TANK194_EXTRA_PINS_H','#define GLOBAL_TANK194_EXTRA_PINS_H','#include "global_asset_registry.h"',
           'static const GlobalAssetResource global_tank194_extra_resources[2] = {']
    for member in p['members']:
        r=member['canonical_material'];identity,d,w,h,x,y=r['header']
        lines.append(f' {{{identity}u,{r["bytes"]}u,{d}u,{w}u,{h}u,{x},{y},"content/{r["sha256"]}.hda",UINT64_C(0x{r["payload_fnv"]})}},')
    lines+=['};','static const GlobalAssetSourceTile global_tank194_extra_source[8] = {']
    lines += [f' {{{t["index"]}u,UINT64_C(0x{t["decoded_indices_then_coverage_fnv"]})}},' for m in p['members'] for t in m['source_tiles']]
    lines+=['};','static const GlobalAssetPaletteColor global_tank194_extra_palette[3] = {']
    lines += [f' {{{c["index"]}u,0x{c["rgb"]}u}},' for c in p['additional_palette']]
    lines+=['};','#endif','']
    raw='\n'.join(lines).encode('utf-8')
    if body.sha(raw)!=HEADER_SHA256:raise ValueError('Generated extra header differs from qualified source')
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
        if body.regular(root,path)!=expected:raise ValueError('Stale extra alias or generated header: '+path)
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
            if source in seen_manual or row!=manual[source] or type(row.get('bytes'))is not int:raise ValueError('Changed or duplicate original gameplay extra row')
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
    if len(selected)!=2 or {row.get('destination') for row in selected}!=set(expected):raise ValueError('Expected exactly two extra-pose aliases')
    for row in selected:
        if type(row.get('identity'))is not int or type(row.get('density'))is not int or type(row.get('bytes'))is not int or row!=expected[row['destination']]:raise ValueError('Changed extra-pose alias metadata')


def input_paths(root):
    p=authority(root);old,_=body.authority(root)
    return sorted({PROOF,body.PROOF,*[r['path'] for r in old['public_sources'].values()],*[m['canonical_material']['path'] for m in p['members']]})
