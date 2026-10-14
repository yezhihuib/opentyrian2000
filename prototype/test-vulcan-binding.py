#!/usr/bin/env python3
"""Compact isolated Vulcan proof, adapted from existing Missile/Energy tests.
No game execution, capture, production-source mutation or publication.
"""
import argparse, hashlib, json, os, re, struct, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
PIN='ee2b90cfaf9f227ca394ecd01f2403e55dbf2ea0'
IDS=[67,70]
PACKET_SHA='802a5611b97dbd63b27dd79eae728c9f19b07eea6ac6474dad237f8c09c55e60'
INVENTORY_SHA='2099589202e779b0b41c7fed9f50bb71a5f99f84c8eabd79c580f3214ee2e460'
SHA=lambda b:hashlib.sha256(b).hexdigest()
CHANGES=[
 ('/* Slots 507..521 are reserved for the separately staged rear and Data families. */\nstatic Asset assets[524];','static Asset assets[507];'),
 (' /* Normal Vulcan: two static player tracer heads; Christmas art stays original. */\n'
  ' if(!xmas&&bank.data==spriteSheet8.data&&layout==ENTITY_TILE) {\n'
  '  static const unsigned int vulcan_ids[2]={67,70};\n'
  '  for(int i=0;i<2;i++)if(index==vulcan_ids[i]){slot=522+i;role=8;break;}\n }\n',''),
 (' /* Vulcan shadows retain their original indexed silhouettes and origin. */\n'
  ' if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&(index==67||index==70)&&style==MIRROR_SHADOW)return false;\n','')]

FUNCTIONS=['complete_turret_group','restore_classic_rect','palette_rgb','blend_rgba','cloud_shadow_rgba','cloud_asset','darken_rgba','decode_tile','read_asset','explosion_asset_slot','get_asset','talon_frame','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset','render_mirror_entity','enemy_energy_slot','enemy_energy_family_ready','render_mirror_enemy_shot','render_mirror_pixel','render_mirror_entity_end']

def extract(source,name):
    m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',source,re.M)
    assert m,name
    end=source.index('{',m.start())+1;depth=1
    while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[m.start():end]+'\n'

def decode(bank,idx):
    pos=struct.unpack_from('<H',bank,2*(idx-1))[0];cell=0;indices=bytearray(168);mask=bytearray(168)
    while bank[pos]!=15:
        code=bank[pos];pos+=1;cell+=code&15
        for _ in range(code>>4):
            assert 0<=cell<168 and not mask[cell]
            indices[cell]=bank[pos];mask[cell]=255;pos+=1;cell+=1
    return indices+mask

def scope(candidate,baseline):
    assert subprocess.check_output(['git','-C',str(baseline),'rev-parse','HEAD'],text=True).strip()==PIN
    names=subprocess.check_output(['git','-C',str(baseline),'ls-tree','-r','--name-only',PIN,'--','src'],text=True).splitlines()
    names=[n for n in names if Path(n).suffix in {'.c','.h','.inc'}]
    current={str(p.relative_to(candidate)) for p in (candidate/'src').rglob('*') if p.is_file() and p.suffix in {'.c','.h','.inc'}}
    assert current==set(names),'Added or removed production source'
    data={label:{n:(root/n).read_bytes() for n in names} for label,root in [('candidate',candidate),('baseline',baseline)]}
    for name in names:
        pinned=subprocess.check_output(['git','-C',str(baseline),'show',PIN+':'+name])
        assert data['baseline'][name]==pinned,'Baseline no longer pinned: '+name
        restored=data['candidate'][name]
        if name=='src/render_mirror.c':
            text=restored.decode()
            for before,after in CHANGES:assert text.count(before)==1; text=text.replace(before,after)
            restored=text.encode()
        assert restored==pinned,'Unexpected production delta: '+name
    manifest=json.loads((candidate/'assets/hd/manifest.json').read_bytes());original=json.loads(subprocess.check_output(['git','-C',str(baseline),'show',PIN+':assets/hd/manifest.json']))
    restored=json.loads(json.dumps(manifest));family=restored.pop('player_vulcan_two_v1')
    for row in family['entries']:
        del restored['source_pngs'][row['HDA_sha256']]
        for kind in ['preview','debug']:
            pack=restored['default_'+kind+'_pack'];del restored['packs'][pack]['files'][f"bullet-{row['id']}-8.hda"];restored['packs'][pack]['count']-=1
    assert restored==original,'Unexpected manifest delta'
    for kind in ['preview','debug']:
        pack=manifest['default_'+kind+'_pack']
        for name,item in original['packs'][pack]['files'].items():
            raw=(baseline/'assets/hd/packs'/pack/name).read_bytes();assert SHA(raw)==item['sha256']
            materialized=candidate/'assets/hd/packs'/pack/name
            if materialized.exists():assert materialized.read_bytes()==raw
    return data,{'baseline_commit':PIN,'production_file_count':len(names),'exact_renderer_changes':3,'inverse_renderer':'byte-identical to pinned baseline','other_production_files':'byte-identical to pinned baseline','manifest_inverse_exact':True,'prior_default_manifest_resources_hash_verified':1030,'production_sha256':{n:SHA(v) for n,v in data['candidate'].items()}}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['candidate','baseline','art','original-data','xmas-data','source-packet','out']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});out=a.out
    assert not out.exists() and all(out!=root and root not in out.parents for root in [a.candidate,a.baseline,a.art]),'Use a fresh output outside the supplied source and asset directories'
    sources,proof=scope(a.candidate,a.baseline)
    packet_raw=a.source_packet.read_bytes();assert SHA(packet_raw)==PACKET_SHA
    packet=json.loads(packet_raw);inv_raw=(a.art/'inventory.json').read_bytes();assert SHA(inv_raw)==INVENTORY_SHA
    pins={q['id']:q['HDA_SHA256'] for q in json.loads(inv_raw)['outputs']}
    banks=[]
    for path,expected in [(a.original_data,'80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0'),(a.xmas_data,'e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d')]:
        raw=path.read_bytes();assert SHA(raw)==expected;n=struct.unpack_from('<H',raw)[0];off=list(struct.unpack_from('<'+str(n)+'I',raw,2))+[len(raw)];banks.append(raw[off[7]:off[8]])
    for k,idx in enumerate(IDS):
        q=decode(banks[0],idx);s=packet['shapes'][k]['normal'];assert SHA(q[:168])==s['index_sha256'] and SHA(q[168:])==s['mask_sha256']
        q=decode(banks[1],idx);s=packet['shapes'][k]['christmas'];assert SHA(q[:168])==s['index_sha256'] and SHA(q[168:])==s['mask_sha256']
    manifest=json.loads((a.candidate/'assets/hd/manifest.json').read_text());packs=[a.candidate/'assets/hd/packs'/manifest['default_'+kind+'_pack'] for kind in ['preview','debug']]
    raws={}
    for idx in IDS+[58,31]:
        name=f'bullet-{idx}-8.hda';raw=(packs[0]/name).read_bytes();assert raw[:28]==struct.pack('<4s6I',b'HDR1',80000+idx,8,12,14,0,0) and len(raw)==43036
        assert (packs[1]/name).read_bytes()==raw
        if idx in IDS:
            assert SHA(raw)==pins[idx] and (a.art/'output'/name).read_bytes()==raw
            assert all(not (pack/f'bullet-{idx}-4.hda').exists() for pack in packs)
        raws[idx]=raw
    out.mkdir();work=out/'fixtures';work.mkdir();(work/'bank.bin').write_bytes(banks[0]);(work/'xmas-bank.bin').write_bytes(banks[1])
    reference=b''.join(bytes(decode(banks[0],idx))+raws[idx][28:] for idx in IDS+[58,31])+b''.join(bytes(decode(banks[1],idx))+raws[idx][28:] for idx in IDS)
    (work/'reference.bin').write_bytes(reference)
    variants=[];valid=[];densities=[]
    def add(name,missing=(),mutate=None,density4=False):
        folder=work/name;folder.mkdir();variants.append(name);valid.append([int(idx not in missing and not(mutate and idx==mutate[0])) for idx in IDS]);densities.append(4 if density4 else 8)
        for idx in IDS+[58,31]:
            if idx in missing:continue
            raw=raws[idx];filename=f'bullet-{idx}-8.hda'
            if density4 and idx in IDS:
                rgba=raw[28:];raw=struct.pack('<4s6I',b'HDR1',80000+idx,4,12,14,0,0)+b''.join(rgba[(2*y*96+2*x)*4:(2*y*96+2*x)*4+4] for y in range(56) for x in range(48));filename=filename.replace('-8.','-4.')
            if mutate and idx==mutate[0]:
                raw=bytearray(raw);kind=mutate[1]
                if kind=='magic':raw[0]=0
                fields={'role':(4,1110000+idx),'id':(4,80000+IDS[(IDS.index(idx)+1)%2]),'density':(8,4),'width':(12,11),'height':(16,13),'anchor-x':(20,1),'anchor-y':(24,1)}
                if kind in fields:offset,value=fields[kind];struct.pack_into('<I',raw,offset,value)
                if kind=='short-header':raw=raw[:27]
                if kind=='truncated':raw=raw[:-1]
                if kind=='extra':raw+=b'X'
            (folder/filename).write_bytes(raw)
    for idx in IDS:add(f'missing-{idx}',missing=[idx])
    add('missing-all',missing=IDS)
    for idx in IDS:
        for kind in ['magic','role','id','density','width','height','anchor-x','anchor-y','short-header','truncated','extra']:add(f'{kind}-{idx}',mutate=(idx,kind))
    add('only4',density4=True)
    # Invalid 8x plus a valid 4x is still the existing per-head density fallback.
    add('invalid8-valid4',density4=True)
    for idx in IDS:(work/'invalid8-valid4'/f'bullet-{idx}-8.hda').write_bytes(b'invalid')
    variants_inc='static const char *variants[]={'+','.join(json.dumps(v) for v in variants)+'};\nstatic const int variant_valid[][2]={'+','.join('{'+','.join(map(str,q))+'}' for q in valid)+'};\nstatic const int variant_density[]={'+','.join(map(str,densities))+'};\n'
    types=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'static Asset talon_frames\[13\];',r'static bool enemy_energy_checked,enemy_energy_valid;',r'enum \{ ASSET_NEWSH2=.*?\};']
    reports={}
    for label,baseline in [('candidate',False),('baseline',True)]:
        directory=out/label;directory.mkdir();src=sources[label];s=src['src/render_mirror.c'].decode();sprite=src['src/sprite.c'].decode();entity=src['src/entity_draw.c'].decode()
        helpers={n:extract(s,n) for n in FUNCTIONS};helpers.update({n:extract(sprite,n) for n in ['blit_sprite2','blit_sprite2_darken']});helpers.update({n:extract(entity,n) for n in ['draw_entity_sprite2','draw_enemy_shot_sprite2']})
        (directory/'types.inc').write_text('\n'.join(re.search(q,s,re.S).group() for q in types))
        (directory/'functions.inc').write_text('\n'.join(helpers[n] for n in FUNCTIONS))
        (directory/'blitters.inc').write_text(helpers['blit_sprite2']+helpers['blit_sprite2_darken'])
        (directory/'wrappers.inc').write_text(helpers['draw_entity_sprite2']+helpers['draw_enemy_shot_sprite2'])
        (directory/'variants.inc').write_text(variants_inc)
        command=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-DBASELINE='+str(int(baseline)),'-I'+str(directory),str(HERE/'test-vulcan-binding.c'),'-o',str(directory/'test')]
        r=subprocess.run(command,capture_output=True,text=True);(directory/'compile.log').write_text(r.stdout+r.stderr)
        if r.returncode:print(r.stderr)
        r.check_returncode();runs={}
        env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        for kind,pack in zip(['preview','debug'],packs):
            r=subprocess.run([str(directory/'test'),str(pack),str(work)],env=env,capture_output=True,text=True,timeout=240);(directory/(kind+'.log')).write_text(r.stdout+r.stderr);print(label+'/'+kind+': '+r.stdout+r.stderr,flush=True);r.check_returncode();runs[kind]=json.loads(r.stdout)
        reports[label]={'runs':runs,'compile_command':command,'extracted_function_sha256':{n:SHA(v.encode()) for n,v in helpers.items()}}
    for label,root in [('candidate',a.candidate),('baseline',a.baseline)]:assert all((root/n).read_bytes()==raw for n,raw in sources[label].items()),'Source changed during test'
    report={'status':'PASS','game_runs':0,'captures':0,'sanitizers':['ASan','UBSan'],'leak_detection':False,'source_scope':proof,'art_inventory_sha256':SHA(inv_raw),'source_packet_sha256':SHA(packet_raw),'asset_sha256':{str(k):SHA(v) for k,v in raws.items()},'bank_sha256':[SHA(v) for v in banks],'variants':variants,'results':reports,'coverage':['Finite bank/layout/ID enumeration in both xmas modes; cache slots and neighbors','Cold and warmed xmas guard before cache with actual alternative Christmas67/70 indexed pixels','Prior player metadata; Pulse58 HD normal/shadow; Missile31 HD normal/indexed shadow','All heads: straight alpha, transparent preservation, ordered overlaps, original indexed writes and silhouettes, clipping, 320/328 indexed pitch, RGBA row padding, ownership','Each missing member, all missing; all header fields, short header, short/trailing payload per head; valid4 and invalid8-to4 fallback; current 8-only pack falls back to indexed at density4','Actual unchanged generic compositor blend rejection and local restoration','All production source pinned; direct enemy/shop/Christmas call sites remain unchanged; direct indexed blits and explicit enemy hook/wrapper negatives tested'], 'limitations':['Extracted-source unit; no game execution, screenshot, presentation or aesthetic acceptance.','Font/material inputs are no-op or fail-if-entered stubs; loader, routing, RLE, pixel compositor and local restoration are extracted unchanged.','Generic blend rejection signal is recorded by a stub; actual draw_asset_filtered and restore_classic_rect execute unchanged.','LeakSanitizer disabled for ptrace-based executor; address and undefined sanitizers enabled.']}
    report['harness_sha256']={q.name:SHA(q.read_bytes()) for q in [Path(__file__),Path(__file__).with_suffix('.c')]}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('Report:',out/'result.json')

if __name__=='__main__':main()
