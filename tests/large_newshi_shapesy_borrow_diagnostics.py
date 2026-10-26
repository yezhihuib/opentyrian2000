#!/usr/bin/env python3
"""Actual E1L12 typed-underlay guard probes in a separate instrumented binary.

Production sources are never edited. This intentionally exits at tick397 after
asserting NEWSHI final/cached guard outcomes; it is not a normal playthrough/Present.
The uninstrumented run remains a separately required positive visual proof.
"""
import argparse,concurrent.futures,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
INJECT=r'''
static unsigned diagnostic_slot=100;
static void diagnostic_assert(bool okay,const char *why)
{if(!okay){fprintf(stderr,"DIAGNOSTIC FAIL %s tick=%u dep=%llu\n",why,game_probe_tick,(unsigned long long)global_newshf_shapesy_dependency);fflush(stderr);_Exit(91);}}
static void diagnostic_mutate(const char *which)
{
 if(!strcmp(which,"rgba"))shapesy_resources.members[0].rgba[0]^=1;
 else if(!strcmp(which,"source")){unsigned i;for(i=0;i<72;i++)if(shapesy_member(shapesy_registry.ids[i])>=0){megaData1.shapes[i].sh[0]^=1;break;}diagnostic_assert(i<72,"source slot");}
 else if(!strcmp(which,"palette"))rgb_palette[0]^=1;
 else if(!strcmp(which,"generation"))++shapesy_resources.generation;
 else if(!strcmp(which,"serial"))++shapesy_borrow.serial;
 else if(!strcmp(which,"tick"))++shapesy_borrow.tick;
 else if(!strcmp(which,"reset"))shapesy_frame_reset();
 else if(!strcmp(which,"root"))game_probe_assets="diagnostic-unqualified-root";
 else if(!strcmp(which,"geometry"))++shapesy_borrow.geometry.output_w;
 else if(!strcmp(which,"canvas"))canvas->pitch+=4;
 else if(!strcmp(which,"indexed"))game_screen->pitch+=1;
 else diagnostic_assert(false,"unknown mutation");
}
static void diagnostic_transfer(void)
{
 unsigned slot;for(slot=0;slot<100;slot++)if(global_newshf_generations[slot]&&newshf_validation_slots[slot].profile>=10)break;
 diagnostic_assert(slot<100,"transfer source");
 Uint8 *prior=malloc(global_newshf_capacity);diagnostic_assert(prior!=NULL,"transfer allocation");memcpy(prior,global_newshf_owner,global_newshf_capacity);
 int x=newshf_validation_slots[slot].x-6,y=newshf_validation_slots[slot].y-7;
 global_talon_pose(1,spriteSheet9,233,233,0);
 diagnostic_assert(render_mirror_global_player_ship(game_screen,x,y,spriteSheet9,233,MIRROR_NORMAL,1,233)==1,"actual Talon transfer draw");
 blit_sprite2x2(game_screen,x,y,spriteSheet9,233);render_mirror_entity_end();
 unsigned copied=0;for(size_t i=0;i<global_newshf_capacity;i++)if(prior[i]&&global_talon_owner[i]&&global_talon_foreign[i]&&!global_newshf_owner[i])copied++;
 free(prior);diagnostic_assert(copied>0,"actual copied ownership");
 for(int yy=0;yy<184;yy++)memcpy((Uint8*)VGAScreenSeg->pixels+yy*VGAScreenSeg->pitch,(Uint8*)game_screen->pixels+yy*320+24,264);
 diagnostic_assert(global_newshf_shapesy_dependency!=0,"dependency survives transfer");
}
void render_mirror_finish(MirrorOutputKind kind,int lightx,int lighty)
{
 const char *mode=getenv("NEWSHI_BORROW_DIAGNOSTIC");
 if(!mode||game_probe_tick!=397){diagnostic_inner_finish(kind,lightx,lighty);return;}
 bool preflight=!strncmp(mode,"preflight-",10),cached=!strncmp(mode,"cached-",7),transfer=strstr(mode,"transfer-")!=NULL;
 if(preflight){
  diagnostic_assert(diagnostic_slot<100,"preflight injected");
  diagnostic_assert(global_newshf_dual_preflight_state[diagnostic_slot]==1&&!global_newshf_fault,"whole actor fallback without frame fault");
  diagnostic_inner_finish(kind,lightx,lighty);diagnostic_assert(ready&&last_output_valid,"unrelated scene stays HD");
 }else{
  unsigned large_borrowers=0;for(unsigned i=0;i<100;i++)if(global_newshf_generations[i]&&newshf_validation_slots[i].profile>=10&&global_newshf_dual_shapesy_serial[i])++large_borrowers;
  diagnostic_assert(large_borrowers>0,"actual NEWSHI typed borrowers");
  diagnostic_assert(global_newshf_shapesy_dependency&&global_newshf_contributed&&!global_newshf_fault,"genuine typed borrow occurred");
  diagnostic_assert(shapesy_borrow_check(global_newshf_shapesy_dependency),"genuine sealed source before mutation");
  if(transfer)diagnostic_transfer();
  const char *which=cached?mode+7:mode+6;if(transfer)which="rgba";
  if(!strcmp(mode,"baseline")){
   diagnostic_inner_finish(kind,lightx,lighty);diagnostic_assert(ready&&last_output_valid,"baseline valid HD");
  }else if(cached){
   diagnostic_inner_finish(kind,lightx,lighty);diagnostic_assert(ready&&last_output_valid&&global_newshf_cached,"valid cached HD before mutation");
   diagnostic_mutate(which);global_newshf_check_cache();diagnostic_assert(!ready&&!last_output_valid,"cached mutation rejected");
  }else{
   diagnostic_mutate(which);diagnostic_inner_finish(kind,lightx,lighty);diagnostic_assert(!ready&&!last_output_valid,"final mutation rejected");
  }
 }
 fprintf(stderr,"PASS DIAGNOSTIC %s tick397 typed-underlay guard\n",mode);fflush(stderr);_Exit(0);
}
'''
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('original-data','sysroot','native-build','pack','out'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--density',type=int,choices=(4,8),default=8)
 a=p.parse_args();a=argparse.Namespace(**{k:(v.resolve() if isinstance(v,Path) else v) for k,v in vars(a).items()});a.out.mkdir(exist_ok=False)
 source_hash={str(p.relative_to(ROOT)):SHA(p) for p in (ROOT/'src').rglob('*') if p.is_file()}
 stage=a.out/'instrumented';shutil.copytree(a.native_build/'src',stage/'src');(stage/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
 source=(ROOT/'src/render_mirror.c').read_text();marker='void render_mirror_finish(MirrorOutputKind kind,int lightx,int lighty)\n{';assert source.count(marker)==1
 source=source.replace(marker,'static void diagnostic_inner_finish(MirrorOutputKind kind,int lightx,int lighty)\n{')
 # Preflight injections refer to a declaration visible before included code.
 source=source.replace('#include "global_newshf_mirror.inc"','static unsigned diagnostic_slot;\n#include "global_newshf_mirror.inc"')
 wrapper=INJECT.replace('static unsigned diagnostic_slot=100;','')
 needle='\n#else\ntypedef int render_mirror_disabled_translation_unit;';assert source.count(needle)==1;source=source.replace(needle,'\n'+wrapper+needle)
 (stage/'src/render_mirror.c').write_text(source)
 inc=(ROOT/'src/global_newshf_mirror.inc').read_text();needle='  if(foreign){Uint32 color=*((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch)+x);';assert inc.count(needle)==1
 injection=r'''  if(foreign){Uint32 color=*((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch)+x);
   const char *mode=getenv("NEWSHI_BORROW_DIAGNOSTIC");
   if(mode&&phase>=18&&phase<=27&&game_probe_tick==397&&!strncmp(mode,"preflight-",10)&&diagnostic_slot==0&&shapesy_borrow_sample(shapesy_serial,n,color)){
    diagnostic_slot=slot+1;
    if(!strcmp(mode,"preflight-mismatch")){*((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch)+x)^=1;color^=1;}
    else if(!strcmp(mode,"preflight-untyped"))diagnostic_untyped_pixel=n;
   }
   if(mode&&!strcmp(mode,"preflight-untyped")&&diagnostic_slot&&n==diagnostic_untyped_pixel)shapesy_borrow.values[n]=0;
'''
 # The global include precedes ShapesY type definitions. Use a helper hook
 # defined after ShapesY for the test-only removal of one typed value.
 injection=injection.replace('else if(!strcmp(mode,"preflight-untyped"))diagnostic_untyped_pixel=n;','else if(!strcmp(mode,"preflight-untyped"))diagnostic_untype(n);').replace('   if(mode&&!strcmp(mode,"preflight-untyped")&&diagnostic_slot&&n==diagnostic_untyped_pixel)shapesy_borrow.values[n]=0;','')
 inc=inc.replace(needle,injection);(stage/'src/global_newshf_mirror.inc').write_text(inc)
 source=(stage/'src/render_mirror.c').read_text().replace('static unsigned diagnostic_slot;','static unsigned diagnostic_slot;\nstatic void diagnostic_untype(size_t);')
 source=source.replace('static void diagnostic_mutate(const char *which)','static void diagnostic_untype(size_t n){shapesy_borrow.values[n]=0;}\nstatic void diagnostic_mutate(const char *which)')
 # Stored slot+1 distinguishes actor slot0 from not injected.
 source=source.replace('diagnostic_slot<100,"preflight injected"','diagnostic_slot>0&&diagnostic_slot<=100,"preflight injected"').replace('global_newshf_dual_preflight_state[diagnostic_slot]==1','global_newshf_dual_preflight_state[diagnostic_slot-1]==1')
 (stage/'src/render_mirror.c').write_text(source)
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu')}
 cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 obj=stage/'render_mirror.o';cmd=['cc','-std=c99','-O2','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(stage/'src'),'-c',str(stage/'src/render_mirror.c'),'-o',str(obj)]
 z=subprocess.run(cmd,env=env,capture_output=True);(a.out/'compile.log').write_bytes(z.stdout+z.stderr);assert z.returncode==0,z.stderr.decode()
 exe=stage/'opentyrian-diagnostic';objects=[str(x) for x in sorted((a.native_build/'obj').glob('*.o')) if x.stem!='render_mirror'];z=subprocess.run(['cc',str(obj),*objects,*libs,'-lm','-o',str(exe)],env=env,capture_output=True);assert z.returncode==0,z.stderr.decode()
 mutations=['rgba','source','palette','generation','serial','tick','reset','root','geometry','canvas','indexed']
 modes=['baseline']+[when+'-'+m for when in ('final','cached') for m in mutations]+['preflight-mismatch','preflight-untyped','final-transfer-rgba','cached-transfer-rgba']
 result=[]
 def run(mode):
  out=a.out/mode;out.mkdir();cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text('section video\nitem scaler 4x\nitem fullscreen -1\n')
  e={**env,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','HOME':str(out),'XDG_CONFIG_HOME':str(out/'config'),'NEWSHI_BORROW_DIAGNOSTIC':mode}
  cmd=[str(exe),f'--data={a.original_data}','--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=1','--asset-debug-level=12','--asset-debug-tick=340','--asset-debug-running','--render-ticks=400',f'--render-assets={a.pack}',f'--global-assets={a.pack}',f'--render-test={a.density}']
  start=time.monotonic();z=subprocess.run(cmd,cwd=out,env=e,capture_output=True,timeout=180);(out/'stdout.log').write_bytes(z.stdout);(out/'stderr.log').write_bytes(z.stderr)
  okay=z.returncode==0 and f'PASS DIAGNOSTIC {mode} tick397'.encode() in z.stderr
  print(mode,'PASS' if okay else 'FAIL',flush=True)
  return dict(mode=mode,passed=okay,exit_code=z.returncode,seconds=round(time.monotonic()-start,3),argv=cmd,stderr_sha256=SHA(out/'stderr.log'))
 result.append(run('baseline'))
 if result[0]['passed']:
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:result.extend(pool.map(run,modes[1:]))
 after={n:SHA(ROOT/n) for n in source_hash};passed=all(x['passed'] for x in result) and len(result)==len(modes) and after==source_hash
 receipt={'status':'PASS' if passed else 'FAIL','scope':__doc__,'canonical_before':source_hash,'canonical_after':after,'injected_sources':{str(p.relative_to(stage)):SHA(p) for p in (stage/'src').glob('*') if p.is_file()},'diagnostic_binary_sha256':SHA(exe),'driver_sha256':SHA(Path(__file__)),'results':result}
 (a.out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');raise SystemExit(not passed)
if __name__=='__main__':main()
