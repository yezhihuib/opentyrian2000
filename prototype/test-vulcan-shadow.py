#!/usr/bin/env python3
"""Focused source-only proof of the local two-ID Vulcan shadow compositor.
Extracts production C without changing it. No game, art generation, or capture.
"""
import argparse, hashlib, json, os, re, shutil, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
PIN='4e75dbda875922303fda92d514fe6d9755e40696'
SHA=lambda b:hashlib.sha256(b).hexdigest()
FUNCTIONS=['complete_turret_group','restore_classic_rect','palette_rgb','blend_rgba','cloud_shadow_rgba','cloud_asset','darken_rgba','decode_tile','read_asset','explosion_asset_slot','get_asset','talon_frame','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset','render_mirror_entity','enemy_energy_slot','enemy_energy_family_ready','render_mirror_enemy_shot','render_mirror_pixel','render_mirror_entity_end','render_mirror_unsupported','upscale','render_mirror_begin','render_mirror_finish','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_shadow_begin','render_mirror_shadow_end']

def extract(source,name):
    m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',source,re.M)
    assert m,name
    end=source.index('{',m.start())+1;depth=1
    while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[m.start():end]+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['candidate','baseline','fixtures','out']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()})
    assert not a.out.exists(),'Use a fresh output directory'
    harness={q.name:q.read_bytes() for q in [Path(__file__),Path(__file__).with_suffix('.c')]}
    assert subprocess.check_output(['git','-C',str(a.baseline),'rev-parse','HEAD'],text=True).strip()==PIN
    names=subprocess.check_output(['git','-C',str(a.baseline),'ls-tree','-r','--name-only',PIN,'--','src'],text=True).splitlines()
    names=[n for n in names if Path(n).suffix in {'.c','.h','.inc'}]
    assert {str(q.relative_to(a.candidate)) for q in (a.candidate/'src').rglob('*') if q.is_file() and q.suffix in {'.c','.h','.inc'}}==set(names)
    sources={n:(a.candidate/n).read_bytes() for n in names}
    altered=[]
    for n in names:
        old=subprocess.check_output(['git','-C',str(a.baseline),'show',PIN+':'+n])
        assert (a.baseline/n).read_bytes()==old,'Unpinned baseline '+n
        if sources[n]!=old:altered.append(n)
    assert altered==['src/render_mirror.c','src/render_mirror.h','src/sprite.c'],altered
    sprite_restore=sources['src/sprite.c'].decode().replace('\trender_mirror_shadow_begin(surface,x,y,sprite2s,index);\n','').replace('{ render_mirror_shadow_end(); return; }','return;').replace('\trender_mirror_shadow_end();\n','')
    assert sprite_restore.encode()==(a.baseline/'src/sprite.c').read_bytes(),'Original sprite blitters changed beyond entry/end hooks'
    header_restore=''.join(line for line in sources['src/render_mirror.h'].decode().splitlines(True) if 'render_mirror_shadow_begin' not in line and 'render_mirror_shadow_end' not in line)
    assert header_restore.encode()==(a.baseline/'src/render_mirror.h').read_bytes(),'Unexpected public API change'
    manifest=json.loads((a.baseline/'assets/hd/manifest.json').read_text())
    assert subprocess.check_output(['git','-C',str(a.candidate),'show',PIN+':assets/hd/manifest.json'])==(a.baseline/'assets/hd/manifest.json').read_bytes()
    packs=[a.baseline/'assets/hd/packs'/manifest['default_'+kind+'_pack'] for kind in ['preview','debug']]
    art={}
    for idx in [67,70]:
        name=f'bullet-{idx}-8.hda';raw=(packs[0]/name).read_bytes();assert (packs[1]/name).read_bytes()==raw
        assert SHA(raw)==manifest['packs'][manifest['default_preview_pack']]['files'][name]['sha256']
        art[name]=SHA(raw)
    fixture_files={str(q.relative_to(a.fixtures)):SHA(q.read_bytes()) for q in a.fixtures.rglob('*') if q.is_file()}
    for name,pin in {'bank.bin':'9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68','xmas-bank.bin':'26eb4fe91672bcef4bc88d7162d5f531144ad98eba64f5c0314e35fec85241e4','reference.bin':'6635ca4f7e16ced0a647e4009510627429466006d1acc91cb77ff985488d47e4'}.items():assert fixture_files[name]==pin
    a.out.mkdir();work=a.out/'fixtures';shutil.copytree(a.fixtures,work)
    # Runtime mutations remain in isolated fixtures and never alter frozen art.
    for name,idx in [('payload-67',67),('payload-70',70)]:
        (work/name).mkdir()
        for k in [67,70]:
            raw=bytearray((packs[0]/f'bullet-{k}-8.hda').read_bytes())
            if k==idx:raw[28+3]^=1
            (work/name/f'bullet-{k}-8.hda').write_bytes(raw)
    variants=sorted(q.name for q in work.iterdir() if q.is_dir())
    validity=[]
    for variant in variants:
        row=[]
        for idx in [67,70]:
            q=work/variant/f'bullet-{idx}-8.hda'
            row.append(int(q.is_file() and SHA(q.read_bytes())==art[f'bullet-{idx}-8.hda']))
        validity.append(row)
    s=sources['src/render_mirror.c'].decode();sprite=sources['src/sprite.c'].decode();entity=sources['src/entity_draw.c'].decode()
    types=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'static Asset talon_frames\[13\];',r'static bool enemy_energy_checked,enemy_energy_valid;',r'enum \{ ASSET_NEWSH2=.*?\};']
    (a.out/'types.inc').write_text('\n'.join(re.search(q,s,re.S).group() for q in types))
    # Bounded production declarations are emitted by exact named markers.
    patterns=[r'typedef struct \{\s*bool live,entered;\s*SDL_Surface \*surface;.*?\} VulcanShadowCall;',r'static VulcanShadowCall vulcan_shadow;',r'static struct \{const Uint8 \*rgba;char path\[1024\];\} vulcan_shadow_resource\[2\];']
    (a.out/'shadow-types.inc').write_text('\n'.join(re.search(q,s,re.S).group() for q in patterns))
    extras=re.findall(r'^static [^\n;{}]*\b(vulcan_shadow_[a-z_]+)\([^;{}]*\)\s*\{',s,re.M)
    functions=FUNCTIONS[:]+['draw_vulcan_shadow']
    helpers={n:extract(s,n) for n in functions+extras}
    # Forward declarations retain original signatures and let production order vary.
    prototypes='\n'.join(v[:v.index('{')].strip()+';' for v in helpers.values())
    (a.out/'functions.inc').write_text(prototypes+'\n'+'\n'.join(helpers.values()))
    blitters=''.join(extract(sprite,n) for n in ['blit_sprite2','blit_sprite2_darken'])
    wrappers=''.join(extract(entity,n) for n in ['draw_entity_sprite2','draw_enemy_shot_sprite2'])
    (a.out/'blitters.inc').write_text(blitters);(a.out/'wrappers.inc').write_text(wrappers)
    (a.out/'variants.inc').write_text('static const char *variants[]={'+','.join(json.dumps(v) for v in variants)+'};\nstatic const int variant_valid[][2]={'+','.join('{'+','.join(map(str,q))+'}' for q in validity)+'};\n')
    command=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(a.out),str(HERE/'test-vulcan-shadow.c'),'-o',str(a.out/'test')]
    r=subprocess.run(command,capture_output=True,text=True);(a.out/'compile.log').write_text(r.stdout+r.stderr)
    if r.returncode:print(r.stderr)
    r.check_returncode();runs={};env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    for kind,pack in zip(['preview','debug'],packs):
        r=subprocess.run([str(a.out/'test'),str(pack),str(work)],env=env,capture_output=True,text=True,timeout=240)
        (a.out/(kind+'.log')).write_text(r.stdout+r.stderr);print(kind+': '+r.stdout+r.stderr,flush=True);r.check_returncode();runs[kind]=json.loads(r.stdout)
    assert all((a.candidate/n).read_bytes()==raw for n,raw in sources.items()),'Production source changed during test'
    assert fixture_files=={str(q.relative_to(a.fixtures)):SHA(q.read_bytes()) for q in a.fixtures.rglob('*') if q.is_file()},'Retained fixture mutated'
    assert all(SHA((pack/name).read_bytes())==stamp for pack in packs for name,stamp in art.items()),'Frozen art changed during test'
    assert all((HERE/name).read_bytes()==raw for name,raw in harness.items()),'Harness changed during test'
    report={'status':'PASS','game_runs':0,'captures':0,'sanitizers':['ASan','UBSan'],'leak_detection':False,'baseline_commit':PIN,'production_files_checked':len(names),'changed_production_files':altered,'sprite_and_header_inverse_exact':True,'production_sha256':{n:SHA(v) for n,v in sources.items()},'art_sha256':art,'retained_fixtures_sha256':fixture_files,'variant_acceptance':dict(zip(variants,validity)),'runs':runs,'compile_command':command,'extracted_function_sha256':{n:SHA(v.encode()) for n,v in helpers.items()},'harness_sha256':{name:SHA(raw) for name,raw in harness.items()},'coverage':['All indexed writes exactly once in independently decoded source-support order; full indexed buffers and padding exact','Frozen full contour includes exactly78/110 extra-support samples; alpha0 indexed divergence and cloud provenance','All256 palette indices, ramp-floor repeated writes, exact0/1/254/255 blend and HD half-before-blend math','Current indexed,HD-owned,cloud transfer mappings; original-reference ownership covered in mixed scenes','Own-head overlaps and fixed-position different-ID and each same-ID projectile pair in both command orders','Normal/original/enemy intervening writes; pending wrong bank,index,origin and source/storage/root/payload/ledger epoch failures','Entered duplicate,premature end,nested entity,finish,partial command and source/indexed/RGBA metadata mismatches','Cold/warm Christmas,source allocation reload and address reuse,missing/invalid/only4/invalid8-valid4 and mutated payload fallbacks','Top/bottom clip,Cartesian wrap rejection retaining old physical writes,padded indexed and RGBA pitch','Exact extracted frame begin,finish,crop,repeated Present,black/white/restoration fades and local region restoration'],'limitations':['Extracted-source units only; no game, screenshot, or aesthetic acceptance.','HUD/font/material integrations use no-op or fail-if-entered stubs; original loaders, mirror, RLE and local restoration are extracted unchanged.','LeakSanitizer disabled in ptrace executor; ASan and UBSan remain enabled.']}
    (a.out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('Report:',a.out/'result.json')
if __name__=='__main__':main()
