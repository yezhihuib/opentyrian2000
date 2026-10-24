#!/usr/bin/env python3
"""Native production-object enemy reuse renderer test; not game-loop acceptance.
Private original data is verified then transferred on stdin, never persisted.
"""
import argparse, hashlib, json, os, re, resource, shutil, struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHA=lambda b:hashlib.sha256(b).hexdigest()
FRAMES=(105,106,124,125,20,21,214,215,216,226,227,244)
def filename(f):return 'enemy-protron-p09-227-8.hda' if f==227 else f'bullet-{f}-8.hda'
HDA_SHA=('d12fde24b67f6b57ede3483e07a155b95cd5f538cf9f96c64e0d80fc2e0eba78','1a47b5701ecbdef673251cd1de7b975e42291cef29ab9a0bfd10f1c48facb2ba','b37e9664609365b53a250c0a711b6ae863ab55299904794051091b206aeef158','11ffdf82296ed985ec9534ba19a555eb22594c14e5fc92414531a47e36383752','328f9831389399fa7c8d623889732bbc1574dac458a30b97511e2d031dd7aed8','a8fbcb2952ec4a4b3f84388f1b410ec70648052cbaff35487d2ed930c9b5dc55','cd2fe29818aa734481be907ba27d764b58cb178f6252ee9f3fa358f8560b8740','917ebcb0f1044b55e025d9cc160546c96192f5e142e950ccf08415f947cfa7bf','f06bd83d10dbab85d50afc0d7946da52d1a4a9bf496cfaba172e6856b772187e')
def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ('original-data','sysroot','base-build','assets','out'):p.add_argument('--'+key,type=Path,required=True)
 p.add_argument('--negative-control',choices=('rgb-store','swapped-mapping'))
 p.add_argument('--current-sonic-art',action='store_true',help='Validate four Sonic inputs by current two-master derivation; other frozen families stay pinned')
 p.add_argument('--observe-session',action='store_true',help='Run independent non-probe session matrix after the unchanged native regression matrix')
 p.add_argument('--min-free-mib',type=int,default=5120,help='Explicit bounded-run disk reserve; minimum 512 MiB')
 p.add_argument('--controlled-session',action='store_true',help='Exact private contract fixture and output-phase owner tests; not original-event acceptance')
 a=p.parse_args();a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=True)
 snapshot={str(p):SHA(p.read_bytes()) for p in list((ROOT/'src').glob('*'))+list((ROOT/'tests').glob('*reuse_validation.*'))+list((ROOT/'tests').glob('enemy_observe_validation.*')) if p.is_file()}
 for key in ('original_data','sysroot','base_build','assets'):setattr(a,key,getattr(a,key).resolve())
 assert a.min_free_mib>=512 and shutil.disk_usage(a.out).free>a.min_free_mib*1024**2
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu'),'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
 cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 flags=['-I'+str(ROOT/'tests'),'-std=c99','-O0','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DENEMY_REUSE_HD_PROTOTYPE=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(ROOT/'src'),'-I'+str(a.out)]
 sanitized=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 # Reuse immutable unchanged baseline objects only; compile every modified TU.
 rebuild={'sprite','tyrian2','entity_draw','enemy_reuse_identity','shots','varz'}
 if a.controlled_session or a.observe_session:rebuild.add('game_probe')
 # Recompile every changed/new translation unit; unchanged objects remain read-only.
 rebuild.update(p.stem for p in (ROOT/'src').glob('*.c') if p.stem not in {'render_mirror','opentyr'} and (not (a.base_build/'src'/p.name).exists() or (a.base_build/'src'/p.name).read_bytes()!=p.read_bytes()))
 objects=[str(x) for x in sorted((a.base_build/'obj').glob('*.o')) if x.stem not in rebuild|{'render_mirror','opentyr'}]
 for obj in objects:
  source=Path(obj).stem+'.c';assert (a.base_build/'src'/source).read_bytes()==(ROOT/'src'/source).read_bytes(), 'Cannot reuse modified production unit '+source
 log=[]
 def run(cmd):
  r=subprocess.run(cmd,env=env,capture_output=True,text=True);log.append(' '.join(cmd)+'\n'+r.stdout+r.stderr);(a.out/'compile.log').write_text('\n'.join(log));
  if r.returncode:raise RuntimeError(r.stderr)
 for unit in sorted(rebuild):
  target=a.out/(unit+'.o');source=ROOT/'src'/(unit+'.c');signature=SHA(source.read_bytes()+b''.join(h.read_bytes() for h in sorted(list((ROOT/'src').glob('*.h'))+list((ROOT/'src').glob('*.inc')))));pin=a.out/(unit+'.build-pin')
  if a.controlled_session and unit=='game_probe':
   source=a.out/'game_probe_contract_fixture.c';source.write_bytes((ROOT/'src/game_probe.c').read_bytes()+(ROOT/'tests/enemy_controlled_probe_fixture.inc').read_bytes());signature=SHA(source.read_bytes()+signature.encode())
  if not target.exists() or not pin.exists() or pin.read_text()!=signature:
   run(['cc',*flags,*sanitized,'-c',str(source),'-o',str(target)]);pin.write_text(signature)
  objects.append(str(target))
 target=a.out/'opentyr.o';run(['cc',*flags,'-Dmain=enemy_reuse_unused_game_main','-c',str(ROOT/'src/opentyr.c'),'-o',str(target)]);objects.append(str(target))
 if a.negative_control:
  mutant=a.out/'mutant';mutant.mkdir(exist_ok=True);code=(ROOT/'src/render_mirror.c').read_text()
  if a.negative_control=='rgb-store':
   store='else *p=blend_rgba(*p,src,talon_blend?(src[3]+1)/2:src[3]);';assert code.count(store)==1;code=code.replace(store,'else *p=*p; /* deliberate compositor-store mutation */')
  else:
   inc=(ROOT/'src/enemy_reuse_mirror.inc').read_text();assert '226,227,244' in inc;inc=inc.replace('226,227,244','244,227,226');(mutant/'enemy_reuse_mirror.inc').write_text(inc)
  (mutant/'render_mirror.c').write_text(code);flags.insert(0,'-I'+str(mutant))
 engine=(ROOT/'src/tyrian2.c').read_text()
 def loop_after(marker,loop):
  start=engine.index(loop,engine.index(marker));opening=engine.index('{',start);end=opening+1;depth=1
  while depth:depth+=(engine[end]=='{')-(engine[end]=='}');end+=1
  return engine[start:end]
 shot_loop=loop_after('/* Draw Enemy Shots */','for (int z = 0; z < ENEMY_SHOT_MAX; z++)')
 for hook in ('enemy_reuse_shot_before_animation','enemy_reuse_shot_after_animation'):assert hook in shot_loop
 explosion_loop=loop_after('/*---------------------------- Draw Explosions','for (int j = 0; j < MAX_EXPLOSIONS; j++)')
 controls='\n#define draw_enemy_reuse_shot_sprite2(s,x,y,b,i,slot,raw) blit_sprite2(s,x,y,b,i)\n'+''.join('#define '+h+'(s) ((void)0)\n' for h in ('enemy_reuse_shot_before_animation','enemy_reuse_shot_after_animation','enemy_reuse_shot_begin_draw','enemy_reuse_shot_retire'))
 control_end='\n#undef draw_enemy_reuse_shot_sprite2\n'+''.join('#undef '+h+'\n' for h in ('enemy_reuse_shot_before_animation','enemy_reuse_shot_after_animation','enemy_reuse_shot_begin_draw','enemy_reuse_shot_retire'))
 (a.out/'native_enemy_green_loops.inc').write_text('static void native_enemy_shots(void){JE_byte temp;'+shot_loop+'}\nstatic void native_explosions(void){'+explosion_loop+'}\n'+controls+'static void native_enemy_shots_classic(void){JE_byte temp;'+shot_loop+'}\n'+control_end)
 (a.out/'native_p05_helpers.inc').write_text((ROOT/'tests/enemy_green_reuse_validation.c').read_text().split('int main(int argc,char **argv)')[0])
 if a.observe_session or a.controlled_session:(a.out/'native_p09_observer_helpers.inc').write_text((ROOT/'tests/enemy_protron_reuse_validation.c').read_text().replace('int main(int argc,char **argv)','static int legacy_p09_main(int argc,char **argv)').replace(' p09_positive();',' if(getenv("ENEMY_OBSERVE_RESOURCE_CASE"))return 0;\n p09_positive();'))
 if a.controlled_session:
  helper=a.out/'native_p09_observer_helpers.inc';helper.write_text(helper.read_text().replace(' if(getenv("ENEMY_OBSERVE_RESOURCE_CASE"))return 0;', ' return 0; /* controlled-only fixture; old matrix run separately */'))
 run(['cc',*flags,*sanitized,'-no-pie',str(ROOT/'tests'/('enemy_controlled_probe_validation.c' if a.controlled_session else 'enemy_observe_validation.c' if a.observe_session else 'enemy_protron_reuse_validation.c')),*objects,*libs,'-lm','-o',str(a.out/'test')])
 raw=(a.original_data/'tyrian.hdt').read_bytes();assert SHA(raw)=='fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b'
 shape=(a.original_data/'tyrian.shp').read_bytes();offsets=struct.unpack_from('<13I',shape,2);bank=shape[offsets[7]:offsets[8]]
 assert len(bank)==32060 and SHA(bank)=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
 pal=(a.original_data/'palette.dat').read_bytes();assert SHA(pal)=='f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0';rgb=bytes((v<<2)|(v>>4) for v in pal[5*768:6*768])
 payload=bank+b''.join(raw[o:o+77] for o in (206365,182495))+b''.join(raw[o:o+80] for o in (27268,32628))+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big')) for n in range(0,768,3))
 payload+=(a.original_data/'newshs.shp').read_bytes()+(a.original_data/'newshc.shp').read_bytes()
 newshn=(a.original_data/'newshn.shp').read_bytes();expbank=(a.original_data/'newsh6.shp').read_bytes();assert len(expbank)==17810 and SHA(expbank)=='49e3d08e122ea71d6a621d2de127da00ce8a26ff73a0fb40d0cdd7ca2909d075'
 registry=json.loads((ROOT/'assets/hd/global-assets-v1/registry.json').read_text());green=next(x for x in registry['families'] if 'green' in x['name'].lower());weapon_offsets=[r['variants'][0]['offset'] for r in green['source_identity']['weapon_records']]
 payload+=raw[193198:193198+77]+raw[33428:33428+80]+b''.join(raw[o:o+80] for o in weapon_offsets)+struct.pack('<II',len(newshn),len(expbank))+newshn+expbank
 # Independent native source fixture, offsets not derived from production allowlist.
 rec_offsets=(174256,173948,174333,180647,180801,181263,181340)
 weapon_offsets=(32468,31908,31988,24228,24148)
 actor=(a.original_data/'newsh7.shp').read_bytes();assert len(actor)==44079 and SHA(actor)=='52c40a2438373f9fc9a7cd2d338ec149f4e81dda56d9c05061ee2264408f0b1a'
 actor6=(a.original_data/'newshb.shp').read_bytes();assert len(actor6)==39025 and SHA(actor6)=='9bae3eccd4e8793d42553c9798581f0ef77d829fe30d16afa29cf45261ed3c08'
 payload+=b''.join(raw[o:o+77] for o in rec_offsets)+b''.join(raw[o:o+80] for o in weapon_offsets)+actor+actor6
 lvl=(a.original_data/'tyrian3.lvl').read_bytes();assert SHA(lvl)=='6a5b94a7d3e4f5a228bc0f702cfe035c8f9f03b20a3f02867d25e95b4249ce86'
 start=struct.unpack_from('<i',lvl,2)[0];pos=start+8;n=struct.unpack_from('<H',lvl,pos)[0];pos+=2+2*n;ne=struct.unpack_from('<H',lvl,pos)[0];pos+=2
 events=[struct.unpack_from('<HBhhbbbB',lvl,pos+i*11) for i in range(ne)]
 for ordinal,time,record in ((37,210,133),(150,960,129)):
  ev=events[ordinal-1];assert ev[:3]==(time,15,record),(ordinal,ev)
  preceding=[v for v in events[:ordinal] if v[1]==5][-1];assert [preceding[2],preceding[3],preceding[4],preceding[7]]==[3,6,15,8],preceding
 fixture=a.out/'fixture';fixture.mkdir(exist_ok=True)
 pins=dict(zip(FRAMES[:9],HDA_SHA));pins.update({226:'231a78b2ebc6a2410da297d05703b4c548f38926e7bd6e6b28c4fe6c4fa7071c',244:'901b61b1da6f538d6aac9bbd06a2f7d34e5e9d1e4d9df50c3f3eb01b1cd7b452'})
 current_sonic = None
 if a.current_sonic_art:
  sys.path.insert(0,str(ROOT/'scripts'))
  import current_sonic_compatibility as sonic
  sonic.load(ROOT) # includes generated-header and canonical-byte validation
  selected,_,derived=sonic.generate(ROOT,sonic.read(ROOT,sonic.SELECTION))
  assert set(derived)=={(80000+i,8) for i in (105,106,124,125)}
  current_sonic={'selection_sha256':SHA(sonic.read(ROOT,sonic.SELECTION)), 'master_sha256':[r['source_sha256'] for r in selected['masters']]}
  for (identity,density),blob in derived.items():pins[identity-80000]=SHA(blob)
 for frame in FRAMES:
  source=a.assets/filename(frame);blob=source.read_bytes()
  if frame==227:
   assert struct.unpack('<4s6I',blob[:28])==(b'HDR1',1470227,8,12,14,0,0)
   assert SHA(blob[28:])=='666074b187670c691f63c718a2cea078b84b1172c8b635d5e0c451e4690a956e'
  else:assert SHA(blob)==pins[frame]
  dest=fixture/source.name
  if not dest.exists():dest.symlink_to(source)
 for i,frame in enumerate(FRAMES):
  for mode in ('missing','corrupt','header','anchor','trailing','short'):
   root=fixture/(mode+str(i));root.mkdir(exist_ok=True)
   for f in FRAMES:
    source=a.assets/filename(f);dest=root/source.name
    if dest.exists() or dest.is_symlink():dest.unlink()
    if f!=frame:dest.symlink_to(source)
    elif mode!='missing':
     b=bytearray(source.read_bytes())
     if mode=='corrupt':b[31]^=1
     if mode=='header':b[4]^=1
     if mode=='anchor':b[20]=1
     if mode=='trailing':b+=b'!'
     if mode=='short':b=b[:-1]
     dest.write_bytes(b)
 content=fixture/'content'
 if not content.exists():content.symlink_to(ROOT/'assets/hd/global-assets-v1/content',target_is_directory=True)
 with (a.out/'harness-progress.log').open('wb') as progress:
  r=subprocess.run([str(a.out/'test'),str(fixture)],input=payload,env=env,cwd=a.out,stdout=subprocess.PIPE,stderr=progress,timeout=1200,preexec_fn=no_core)
 r.stderr=(a.out/'harness-progress.log').read_bytes()
 (a.out/'harness.log').write_bytes(r.stdout+r.stderr);print((r.stdout+r.stderr).decode())
 resource_results=[]
 if a.observe_session and r.returncode==0:
  (fixture/'empty-observe').mkdir(exist_ok=True)
  for case in ('empty-observe','missing9','corrupt9','header9','anchor9','trailing9','short9'):
   rr=subprocess.run([str(a.out/'test'),str(fixture)],input=payload,env={**env,'ENEMY_OBSERVE_RESOURCE_CASE':case},cwd=a.out,capture_output=True,timeout=120,preexec_fn=no_core)
   resource_results.append({'case':case,'returncode':rr.returncode,'stdout':rr.stdout.decode(),'stderr':rr.stderr.decode()})
   (a.out/'observer-resource-results.json').write_text(json.dumps(resource_results,indent=2)+'\n')
 source_stable=all(SHA(Path(p).read_bytes())==h for p,h in snapshot.items())
 accepted=r.returncode==0 and source_stable and all(x['returncode']==0 for x in resource_results)
 if a.negative_control:
  marker=b'draws-n==(p?3:1)' if a.negative_control=='swapped-mapping' else b'*pixel(output,x-24*8,y)==want[(size_t)y*canvas->w+x]'
  accepted=source_stable and r.returncode!=0 and marker in r.stderr and b'AddressSanitizer' not in r.stderr and b'runtime error:' not in r.stderr
 report={'current_sonic_art':current_sonic,'source_stable_during_compile_and_execution':source_stable,'compiled_source_sha256':snapshot,'status':'PASS' if accepted else 'FAIL','observer_resource_cases':resource_results,'observe_session':a.observe_session,'controlled_session':a.controlled_session,'disk_budget_bytes':a.min_free_mib*1024**2,'negative_control':a.negative_control,'returncode':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode(),'scope':'Native JE_drawEnemy with controlled firing timers; exact extracted native projectile/explosion update loops; real player shot creation/movement; not gameplay acceptance','native_enemy_loop_sha256':SHA(shot_loop.encode()),'native_explosion_loop_sha256':SHA(explosion_loop.encode()),'sanitizers':'ASan+UBSan renderer/sprite/tyrian2/entity_draw/identity/shots/varz/harness; remaining baseline production objects native optimized','original_bytes_persisted':False,'harness_sha256':{n:SHA((ROOT/'tests'/n).read_bytes()) for n in ('enemy_protron_reuse_validation.c','enemy_protron_reuse_validation.py','enemy_green_reuse_validation.c','enemy_reuse_validation.c')+ (('enemy_controlled_probe_validation.c','enemy_controlled_probe_fixture.inc') if a.controlled_session else ())},'controlled_fixture_bridge_sha256':SHA((ROOT/'tests/enemy_controlled_probe_fixture.inc').read_bytes()) if a.controlled_session else None,'controlled_fixture_translation_unit_sha256':SHA((a.out/'game_probe_contract_fixture.c').read_bytes()) if a.controlled_session else None,'production_source_sha256':{p.name:SHA(p.read_bytes()) for p in sorted((ROOT/'src').iterdir()) if p.is_file()},'reused_baseline_objects':{Path(p).name:SHA(Path(p).read_bytes()) for p in objects if '/obj/' in p},'free_disk_bytes':shutil.disk_usage(a.out).free}
 (a.out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(not accepted)
if __name__=='__main__':main()
