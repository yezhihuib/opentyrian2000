#!/usr/bin/env python3
"""Finite extracted-production enemy-energy test. No game process or capture."""
import argparse, hashlib, json, os, re, struct, subprocess
from pathlib import Path
IDS=[77,58,182,163,1,183,164]
SHA=lambda b:hashlib.sha256(b).hexdigest()

def extract(source,name):
    m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',source,re.M)
    assert m,name
    end=source.index('{',m.start())+1; depth=1
    while depth: depth+=(source[end]=='{')-(source[end]=='}'); end+=1
    return source[m.start():end]+'\n'

def decode(bank,idx):
    pos=struct.unpack_from('<H',bank,2*(idx-1))[0]; cell=0; indices=bytearray(168); mask=bytearray(168)
    while bank[pos]!=15:
        code=bank[pos];pos+=1;cell+=code&15
        for _ in range(code>>4):
            assert 0<=cell<168 and not mask[cell]
            indices[cell]=bank[pos];mask[cell]=255;pos+=1;cell+=1
    return indices+mask

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['out','original-data','baseline']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); repo=Path(__file__).resolve().parents[1];out=a.out.resolve();baseline=a.baseline.resolve()
    assert not out.exists() and repo not in out.parents and out not in repo.parents,'Fresh external output required'
    src={n:(repo/'src'/n).read_bytes() for n in ['render_mirror.c','entity_draw.c','sprite.c','shots.c','tyrian2.c','render_mirror.h']}
    old={n:(baseline/'src'/n).read_bytes() for n in src}
    s=src['render_mirror.c'].decode();entity=src['entity_draw.c'].decode();sprite=src['sprite.c'].decode()
    # Narrow preservation proof, including the complete unchanged old orb branch.
    unchanged=['get_asset','render_mirror_entity','draw_asset_filtered','draw_asset','render_mirror_pixel']
    for n in unchanged:assert extract(s,n)==extract(old['render_mirror.c'].decode(),n),n
    for n in ['sprite.c','shots.c','render_mirror.h']:assert src[n]==old[n],n
    assert extract(entity,'draw_entity_sprite2')==extract(old['entity_draw.c'].decode(),'draw_entity_sprite2')
    prior=extract(old['render_mirror.c'].decode(),'render_mirror_enemy_shot').split('{',1)[1]
    assert extract(s,'render_mirror_enemy_shot').endswith(prior),'Original orb branch changed'
    ty=src['tyrian2.c'].decode();previous=old['tyrian2.c'].decode()
    allow='if (sprite == 112 || sprite == 113 || sprite == 77 || sprite == 58 || sprite == 182 || sprite == 163 || sprite == 1 || sprite == 183 || sprite == 164)'
    assert ty.replace(allow,'if (sprite == 112 || sprite == 113)')==previous,'Unexpected caller/gameplay mutation'
    original=a.original_data.read_bytes();assert SHA(original)=='80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0'
    n=struct.unpack_from('<H',original)[0];offsets=list(struct.unpack_from('<'+str(n)+'I',original,2))+[len(original)]
    bank=original[offsets[7]:offsets[8]];assert SHA(bank)=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
    manifest=json.loads((repo/'assets/hd/manifest.json').read_text());packs=[repo/'assets/hd/packs'/manifest['default_'+kind+'_pack'] for kind in ['preview','debug']]
    art=repo/'assets/hd/artwork/enemy-energy-seven-v1'
    if not art.exists():art=repo.parent/'tyrian-hd-art/formal-enemy-energy-seven-v1'
    inventory=json.loads((art/'inventory.json').read_text());pins={x['id']:x['HDA_SHA256'] for x in inventory['outputs']}
    names=[f'enemy-energy-{i}-8.hda' for i in IDS]+['bullet-112-8.hda','bullet-113-8.hda','bullet-58-8.hda']
    reference=bytearray();asset_pins={}
    for k,name in enumerate(names):
        idx=(IDS+[112,113,58])[k];raw=(packs[0]/name).read_bytes();role=111 if k<7 else 8
        assert raw[:28]==struct.pack('<4s6I',b'HDR1',role*10000+idx,8,12,14,0,0) and len(raw)==43036
        if k<7:assert SHA(raw)==pins[idx]
        for pack in packs:assert (pack/name).read_bytes()==raw
        reference+=decode(bank,idx)+raw[28:];asset_pins[name]=SHA(raw)
    out.mkdir(parents=True);work=out/'fixtures';work.mkdir()
    (work/'bank.bin').write_bytes(bank);(work/'reference.bin').write_bytes(reference)
    variants=[f'missing-{i}' for i in IDS]+[f'changed-{i}' for i in IDS]+['magic','role','id','density','width','height','anchor-x','anchor-y','truncated','extra','alpha','only4']
    for variant in variants:
        directory=work/variant;directory.mkdir()
        for k,name in enumerate(names):
            idx=(IDS+[112,113,58])[k]
            if variant==f'missing-{idx}' and k<7:continue
            raw=bytearray((packs[0]/name).read_bytes())
            if variant==f'changed-{idx}' and k<7:raw[28]^=1
            if k==0:
                if variant=='magic':raw[0]=0
                for label,offset,value in [('role',4,80000+idx),('id',4,1110000+58),('density',8,4),('width',12,11),('height',16,13),('anchor-x',20,1),('anchor-y',24,1)]:
                    if variant==label:struct.pack_into('<I',raw,offset,value)
                if variant=='truncated':raw=raw[:-1]
                if variant=='extra':raw+=b'X'
                if variant=='alpha':raw[31]^=1
            if variant=='only4':
                struct.pack_into('<I',raw,8,4);rgba=raw[28:];raw=raw[:28]+b''.join(rgba[(y*2*96+x*2)*4:(y*2*96+x*2)*4+4] for y in range(56) for x in range(48));name=name.replace('-8.hda','-4.hda')
            (directory/name).write_bytes(raw)
    types=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'static Asset talon_frames\[13\];',r'static bool enemy_energy_checked,enemy_energy_valid;']
    (out/'types.inc').write_text('\n'.join(re.search(q,s,re.S).group() for q in types))
    names_fn=['palette_rgb','blend_rgba','cloud_shadow_rgba','cloud_asset','darken_rgba','decode_tile','read_asset','explosion_asset_slot','get_asset','talon_frame','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset','render_mirror_entity','enemy_energy_slot','enemy_energy_family_ready','render_mirror_enemy_shot','render_mirror_pixel','render_mirror_entity_end']
    helpers={n:extract(s,n) for n in names_fn};helpers.update({n:extract(sprite,n) for n in ['blit_sprite2','blit_sprite2_darken']});helpers.update({n:extract(entity,n) for n in ['draw_enemy_shot_sprite2','draw_entity_sprite2']})
    (out/'functions.inc').write_text('\n'.join(helpers[n] for n in names_fn))
    (out/'blitters.inc').write_text(helpers['blit_sprite2']+helpers['blit_sprite2_darken'])
    (out/'wrappers.inc').write_text(helpers['draw_enemy_shot_sprite2']+helpers['draw_entity_sprite2'])
    (out/'variants.inc').write_text('static const char *variants[]={'+','.join(json.dumps(x) for x in variants)+'};\n')
    command=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(out),str(Path(__file__).with_suffix('.c')),'-o',str(out/'test')]
    r=subprocess.run(command,capture_output=True,text=True);(out/'compile.log').write_text(r.stdout+r.stderr);r.check_returncode()
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');results={}
    for label,pack in zip(['preview','debug'],packs):
        r=subprocess.run([str(out/'test'),str(pack),str(work)],capture_output=True,text=True,env=env,timeout=240)
        (out/(label+'.log')).write_text(r.stdout+r.stderr);print(label+': '+r.stdout+r.stderr,flush=True);r.check_returncode();results[label]=json.loads(r.stdout)
    header=src['render_mirror.h'].decode();macros='\n'.join(re.search(r'^#define '+n+r'\(.*$',header,re.M).group() for n in ['render_mirror_enemy_shot','render_mirror_entity_end'])
    disabled='#include <assert.h>\n#include <stdbool.h>\n#include <stdio.h>\ntypedef int SDL_Surface;typedef int Sprite2_array;static unsigned calls;static void blit_sprite2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){assert(s&&x==3&&y==4&&b==1&&i);calls++;}\n#define RENDER_MIRROR_DISABLED\n'+macros+'\n'+helpers['draw_enemy_shot_sprite2']+'\nint main(void){SDL_Surface s=0;unsigned ids[]={77,58,182,163,1,183,164,112,113};for(unsigned k=0;k<9;k++)draw_enemy_shot_sprite2(&s,3,4,1,ids[k]);assert(calls==9);puts("PASS nine disabled-build original blits");}\n'
    (out/'disabled.c').write_text(disabled);r=subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(out/'disabled.c'),'-o',str(out/'disabled')],capture_output=True,text=True);(out/'disabled-compile.log').write_text(r.stdout+r.stderr);r.check_returncode()
    r=subprocess.run([str(out/'disabled')],capture_output=True,text=True);(out/'disabled.log').write_text(r.stdout+r.stderr);r.check_returncode()
    assert all(v==(repo/'src'/n).read_bytes() for n,v in src.items()),'Production source changed during test'
    report={'status':'PASS','game_runs':0,'captures':0,'sanitizers':['ASan','UBSan'],'results':results,'disabled_build':r.stdout.strip(),'source_sha256':{n:SHA(v) for n,v in src.items()},'function_sha256':{n:SHA(v.encode()) for n,v in helpers.items()},'asset_sha256':asset_pins,'bank_sha256':SHA(bank),'harness_sha256':{q.name:SHA(q.read_bytes()) for q in [Path(__file__),Path(__file__).with_suffix('.c')]},'coverage':{'mutated_packs':variants,'alpha_operator':[0,1,127,128,254,255],'original_index':'Actual source bank8 decoded independently; production RLE remains one blit and one reset per wrapper','pixel_checks':'Every affected ROI after each draw; whole frame every32 transactions and phase boundaries','isolation':'Player58 normal/shadow and orb112/113 work inside each same damaged pack; six other shared player IDs remain classic','legacy_density_fallback':'Old orb/player density8-to4 fallback preserved; seven new IDs reject density1, density4 and source4-only','geometry':'x0/308 and partial vertical clips accepted; physical row wraps fall back; huge coordinates tested before arithmetic','caller_state':'Complete tyrian2 inverse allowlist equality and unchanged sprite.c/shots.c; no gameplay/RNG functions extracted'},'preserved_source':unchanged+['sprite.c','shots.c','render_mirror.h','draw_entity_sprite2','original enemy112/113 hook branch'],'limitations':['Extracted production unit; no gameplay, native presentation or aesthetic acceptance.','Font/material paths are fail-if-entered or no-op stubs; blend/loader/hook/RLE/compositor are exact source.','LeakSanitizer disabled; ASan and UBSan enabled.','Extreme coordinates test the HD hook only; existing original RLE assumptions are not broadened.']}
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('Report:',out/'result.json')

if __name__=='__main__':main()
