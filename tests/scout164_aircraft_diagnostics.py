#!/usr/bin/env python3
"""Separate instrumented record164 pose and typed-underlay diagnostics.

Pose-only uses the original E1L8 actor with a controlled source-cycle selection.
Controlled-chain replaces NEWSHI allocations with original record164 and places
one real cyan tile at a sealed platform/actor intersection. Neither is natural
banking or normal gameplay equality evidence. Production sources are untouched.
"""
import argparse,concurrent.futures,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
INJECT=r'''
static unsigned diagnostic_slot=100;
static void diagnostic_assert(bool okay,const char *why)
{if(!okay){fprintf(stderr,"DIAGNOSTIC FAIL %s tick=%u dep=%llu\n",why,game_probe_tick,(unsigned long long)global_newshf_cyan_dependency);fflush(stderr);_Exit(91);}}
static void diagnostic_mutate(const char *which)
{
 if(!strcmp(which,"rgba"))cyan_secondary_resources.members[0].rgba[0]^=1;
 else if(!strcmp(which,"source")){unsigned i;for(i=0;i<71;i++)if(cyan_member(cyan_registry.ids[i])>=4){megaData2.shapes[i].sh[0]^=1;break;}diagnostic_assert(i<71,"source slot");}
 else if(!strcmp(which,"palette"))rgb_palette[0]^=1;
 else if(!strcmp(which,"generation"))++cyan_secondary_resources.generation;
 else if(!strcmp(which,"serial"))++cyan_borrow.serial;
 else if(!strcmp(which,"tick"))++cyan_borrow.tick;
 else if(!strcmp(which,"reset"))cyan_frame_reset();
 else if(!strcmp(which,"root"))game_probe_assets="diagnostic-unqualified-root";
 else if(!strcmp(which,"geometry"))++cyan_borrow.geometry.output_w;
 else if(!strcmp(which,"canvas"))canvas->pitch+=4;
 else if(!strcmp(which,"indexed"))game_screen->pitch+=1;
 else if(!strcmp(which,"layer1-rgba")){diagnostic_assert(cyan_layer1_dependency!=0,"recursive layer1 dependency occurred");shapesy_resources.members[0].rgba[0]^=1;}
 else if(!strcmp(which,"layer1-source")){diagnostic_assert(cyan_layer1_dependency!=0,"recursive layer1 dependency occurred");unsigned i;for(i=0;i<72;i++)if(shapesy_member(shapesy_registry.ids[i])>=0){megaData1.shapes[i].sh[0]^=1;break;}diagnostic_assert(i<72,"layer1 source slot");}
 else if(!strcmp(which,"layer1-serial")){diagnostic_assert(cyan_layer1_dependency!=0,"recursive layer1 dependency occurred");++shapesy_borrow.serial;}
 else diagnostic_assert(false,"unknown mutation");
}
static void diagnostic_transfer(void)
{
 unsigned slot;for(slot=0;slot<100;slot++)if(global_newshf_generations[slot]&&newshf_validation_slots[slot].profile==17&&global_newshf_cyan_pixels[slot])break;
 diagnostic_assert(slot<100,"transfer source");
 Uint8 *prior=malloc(global_newshf_capacity);diagnostic_assert(prior!=NULL,"transfer allocation");memcpy(prior,global_newshf_owner,global_newshf_capacity);
 int x=newshf_validation_slots[slot].x-6,y=newshf_validation_slots[slot].y-7;
 global_talon_pose(1,spriteSheet9,233,233,0);
 fprintf(stderr,"TRANSFER_GUARDS xy=%d,%d requested=%d frame=%d fault=%d surface=%d source=%d palette=%d underlay=%d family=%d live=%d pose=%d\n",x,y,global_talon_requested(),global_talon_frame,global_talon_fault,global_talon_surface_matches(),global_talon_source_matches(spriteSheet9),global_talon_palette_matches(),global_talon_underlay_matches(),global_talon_family_ready(),global_talon_call.live,global_talon_poses[0].valid);
 diagnostic_assert(render_mirror_global_player_ship(game_screen,x,y,spriteSheet9,233,MIRROR_NORMAL,1,233)==1,"actual Talon transfer draw");
 blit_sprite2x2(game_screen,x,y,spriteSheet9,233);render_mirror_entity_end();
 unsigned copied=0;for(size_t i=0;i<global_newshf_capacity;i++)if(prior[i]&&global_talon_owner[i]&&global_talon_foreign[i]&&!global_newshf_owner[i])copied++;
 free(prior);diagnostic_assert(copied>0,"actual copied ownership");
 for(int yy=0;yy<184;yy++)memcpy((Uint8*)VGAScreenSeg->pixels+yy*VGAScreenSeg->pitch,(Uint8*)game_screen->pixels+yy*320+24,264);
 diagnostic_assert(global_newshf_cyan_dependency!=0,"dependency survives transfer");
}
static void diagnostic_wrap_write(bool copied)
{
 int d=game_probe_density;size_t n;
 for(n=0;n<global_newshf_capacity;n++)if(diagnostic_chain_mask[n]&&(copied?(global_talon_owner[n]&&global_talon_foreign[n]):global_newshf_owner[n]))break;
 diagnostic_assert(n<global_newshf_capacity,"actual chain RGB selected before native wrap write");
 Uint8 source[168]={0},mask[168]={0};diagnostic_assert(decode_tile(spriteSheet9,233,source,mask,12,0,0),"raw writer original source");
 unsigned m;for(m=0;m<168&&!mask[m];m++);diagnostic_assert(m<168,"raw writer occupied source");
 int tx=(int)(n%canvas->w)/d,ty=(int)(n/canvas->w)/d;
 /* Deliberately raw native writer, NOT an eligible wrapped record164 actor. */
 int x=tx-(int)(m%12)-320,y=ty-(int)(m/12)+1;
 diagnostic_assert(x<0&&y>=0,"physical row wrapping fixture");
 blit_sprite2(game_screen,x,y,spriteSheet9,233);
 diagnostic_assert(!(copied?global_talon_owner[n]:global_newshf_owner[n]),"normalized native write retired borrowed/copied owner");
 diagnostic_assert(global_newshf_cyan_dependency&&!global_newshf_fault,"dependency survives actual native owner retirement");
 for(int yy=0;yy<184;yy++)memcpy((Uint8*)VGAScreenSeg->pixels+yy*VGAScreenSeg->pitch,(Uint8*)game_screen->pixels+yy*320+24,264);
 fprintf(stderr,"ACTUAL_NATIVE_WRAP copied=%d origin=%d,%d normalized=%d,%d chain_pixel=%zu\n",copied,x,y,tx,ty,n);
}
void render_mirror_finish(MirrorOutputKind kind,int lightx,int lighty)
{
 const char *mode=getenv("CYAN_AIRCRAFT_DIAGNOSTIC");
 if(getenv("SCOUT164_POSE_ONLY")){
  bool visible=false;for(unsigned i=0;i<100;i++)if(global_newshf_generations[i]&&newshf_validation_slots[i].profile==17){
   diagnostic_assert(newshf_validation_slots[i].pose==(unsigned)atoi(getenv("SCOUT164_CONTROLLED_POSE")),"controlled pose selected");visible=true;
  }
  diagnostic_inner_finish(kind,lightx,lighty);
  if(game_probe_tick>=DIAGNOSTIC_START&&visible){
   diagnostic_assert(ready&&last_output_valid&&!global_newshf_fault,"controlled pose actual HD");
   diagnostic_assert(SDL_SaveBMP(output,"controlled-pose-output.bmp")==0,"pose screenshot saved");
   fprintf(stderr,"PASS DIAGNOSTIC baseline tick%u controlled-pose=%s\n",game_probe_tick,getenv("SCOUT164_CONTROLLED_POSE"));fflush(stderr);_Exit(0);
  }
  diagnostic_assert(game_probe_tick<=DIAGNOSTIC_END,"controlled pose visible in window");return;
 }
 bool actual=false;for(unsigned i=0;i<100;i++)if(global_newshf_generations[i]&&newshf_validation_slots[i].profile==17&&global_newshf_cyan_pixels[i])actual=true;
 bool injected=mode&&!strncmp(mode,"preflight-",10)&&diagnostic_slot;
 if(!(cyan_frame.used&2u)||!diagnostic_secondary_pixels)actual=false;
 if(getenv("CYAN_CONTROLLED_CHAIN")&&(!cyan_layer1_dependency||!diagnostic_chain_pixels))actual=false;
 if(!mode){diagnostic_inner_finish(kind,lightx,lighty);return;}
 diagnostic_assert(game_probe_tick<=DIAGNOSTIC_END,"actual secondary soft-aircraft overlap required inside selected window");
 if(game_probe_tick<DIAGNOSTIC_START||(!actual&&!injected)||((strstr(mode,"layer1-")!=NULL)&&!cyan_layer1_dependency)){
  diagnostic_inner_finish(kind,lightx,lighty);return;
 }
 bool preflight=!strncmp(mode,"preflight-",10),cached=!strncmp(mode,"cached-",7),transfer=strstr(mode,"transfer-")!=NULL;
 if(preflight){
  diagnostic_assert(diagnostic_slot<100,"preflight injected");
  diagnostic_assert(global_newshf_dual_preflight_state[diagnostic_slot]==1&&!global_newshf_fault,"whole actor fallback without frame fault");
  diagnostic_assert(!global_newshf_cyan_pixels[diagnostic_slot-1]&&!global_newshf_generations[diagnostic_slot-1],"no actor HD prefix before whole actor fallback");
  diagnostic_inner_finish(kind,lightx,lighty);diagnostic_assert(ready&&last_output_valid,"unrelated scene stays HD");
 }else{
  unsigned soft_borrowers=0;for(unsigned i=0;i<100;i++)if(global_newshf_generations[i]&&newshf_validation_slots[i].profile==17&&global_newshf_dual_cyan_serial[i]&&global_newshf_cyan_pixels[i])++soft_borrowers;
  diagnostic_assert(soft_borrowers>0&&diagnostic_secondary_pixels>0,"actual secondary soft-aircraft typed borrowers");
  diagnostic_assert(global_newshf_cyan_dependency&&global_newshf_contributed&&!global_newshf_fault,"genuine typed borrow occurred");
  diagnostic_assert(cyan_borrow_check(global_newshf_cyan_dependency),"genuine sealed cyan source before mutation");
  if(transfer)diagnostic_transfer();
  if(strstr(mode,"wrap-")!=NULL)diagnostic_wrap_write(transfer);
  if(strstr(mode,"occluded-")!=NULL){memset(global_newshf_owner,0,global_newshf_capacity);diagnostic_assert(global_newshf_cyan_dependency!=0,"dependency survives full ownership occlusion");}
  const char *which=cached?mode+7:mode+6;if(transfer||strstr(mode,"occluded-")!=NULL||strstr(mode,"wrap-")!=NULL)which="rgba";
  if(!strncmp(mode,"baseline",8)){
   diagnostic_inner_finish(kind,lightx,lighty);diagnostic_assert(ready&&last_output_valid,"baseline valid HD");
  }else if(cached){
   diagnostic_inner_finish(kind,lightx,lighty);diagnostic_assert(ready&&last_output_valid&&global_newshf_cached,"valid cached HD before mutation");
   diagnostic_mutate(which);global_newshf_check_cache();diagnostic_assert(!ready&&!last_output_valid,"cached mutation rejected");
  }else{
   diagnostic_mutate(which);diagnostic_inner_finish(kind,lightx,lighty);diagnostic_assert(!ready&&!last_output_valid,"final mutation rejected");
  }
 }
 fprintf(stderr,"PASS DIAGNOSTIC %s%s tick%u typed-cyan-underlay guard chain_pixels=%u\n",getenv("CYAN_CONTROLLED_CHAIN")?"controlled-":"",mode,game_probe_tick,diagnostic_chain_pixels);fflush(stderr);_Exit(0);
}
'''

CONTROLLED=r"""
/* Test-only deterministic placement. One bound cyan tile per frame, chosen at
 * a real sealed layer1/aircraft intersection; no source payload is modified. */
static void diagnostic_controlled_place(const void *first,int x,int y)
{
 memset(diagnostic_chain_mask,0,sizeof(diagnostic_chain_mask));diagnostic_chain_pixels=0;
 memset(diagnostic_secondary_mask,0,sizeof(diagnostic_secondary_mask));diagnostic_secondary_pixels=0;
 if(!getenv("CYAN_CONTROLLED_CHAIN")||game_probe_tick<DIAGNOSTIC_START||game_probe_tick>DIAGNOSTIC_END||!cyan_group_ready(1))return;
 uint64_t serial=shapesy_borrow_ready();if(!serial)return;
 Uint8 **map=(Uint8 **)first;unsigned best=0,br=0,bt=0,bk=0;
 for(unsigned r=0;r<8;r++)for(unsigned t=0;t<12;t++)for(unsigned k=4;k<9;k++){
  unsigned score=0;
  for(unsigned iy=0;iy<28;iy++)for(unsigned ix=0;ix<24;ix++){
   if(!cyan_registry.source[k][iy*24+ix])continue;
   int gx=x+t*24+ix,gy=y+r*28+iy;if(gx<0||gx>=320||gy<0||gy>=200)continue;
   bool plane=false;for(unsigned a=0;a<100;a++)if(enemyAvail[a]==0&&enemy[a].enemytype==164){
    int ex=newshf_validation_slots[a].x,ey=enemy[a].ey;
    if(gx>=ex-10&&gx<ex+22&&gy>=ey-11&&gy<ey+25){plane=true;break;}
   }
   if(!plane)continue;
   size_t n=(size_t)(gy*8+4)*canvas->w+gx*8+4;
   Uint32 color=((Uint32 *)((Uint8 *)canvas->pixels+(gy*8+4)*canvas->pitch))[gx*8+4];
   if(shapesy_borrow_sample(serial,n,color))++score;
  }
  if(score>best){best=score;br=r;bt=t;bk=k;}
 }
 if(!best)return;
 Uint8 *source=NULL;for(unsigned i=0;i<71;i++)if(cyan_registry.ids[i]==cyan_id_at(bk)){source=megaData2.shapes[i].sh;break;}
 if(!source)return;
 map[br*14+bt]=source;
 for(unsigned iy=0;iy<224;iy++)for(unsigned ix=0;ix<192;ix++){
  if(!source[(iy/8)*24+ix/8]||(*cyan_asset(bk)).rgba[(iy*192+ix)*4+3]==255)continue;
  int gx=(x+bt*24)*8+ix,gy=(y+br*28)*8+iy;if(gx<0||gx>=2560||gy<0||gy>=1600)continue;
  size_t n=(size_t)gy*canvas->w+gx;Uint32 color=((Uint32 *)((Uint8 *)canvas->pixels+gy*canvas->pitch))[gx];
  if(shapesy_borrow_sample(serial,n,color))diagnostic_chain_mask[n]=1;
 }
 fprintf(stderr,"CONTROLLED_CYAN_PLACEMENT tick=%u row=%u tile=%u id=%u platform_cells=%u\n",game_probe_tick,br,bt,cyan_id_at(bk),best);
}
"""

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('original-data','sysroot','native-build','pack','out'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--density',type=int,choices=(4,8),default=8)
 p.add_argument('--start',type=int,default=180);p.add_argument('--end',type=int,default=381)
 p.add_argument('--level',type=int,default=8)
 p.add_argument('--pose',type=int,choices=(1,2,3),default=1)
 p.add_argument('--pose-only',action='store_true',help='Controlled source-cycle on natural E1L8 record164; no borrow assertion')
 p.add_argument('--controlled-actor',action='store_true',help='Test-only NEWSHI allocation replacement with original record164')
 p.add_argument('--controlled-chain',action='store_true',help='Test-only one-tile map placement for real platform→cyan→aircraft chain')
 p.add_argument('--modes',help='Comma-separated bounded subset; baseline always runs first')
 p.add_argument('--jobs',type=int,choices=(1,2),default=2)
 a=p.parse_args();a=argparse.Namespace(**{k:(v.resolve() if isinstance(v,Path) else v) for k,v in vars(a).items()});a.out.mkdir(exist_ok=False)
 # Global Talon uses content-addressed paths, not legacy pack filenames.
 if a.controlled_chain:
  pack=a.out/'controlled-pack';pack.mkdir()
  for f in a.pack.rglob('*'):
   if f.is_file():
    dst=pack/f.relative_to(a.pack);dst.parent.mkdir(parents=True,exist_ok=True);dst.symlink_to(f.resolve())
  talon=sorted((ROOT/'assets/hd/current-compat/talon').glob('*.hda'));assert len(talon)==13
  for f in talon:
   dst=pack/'content'/(SHA(f)+'.hda');dst.parent.mkdir(exist_ok=True)
   if dst.exists():assert SHA(dst)==SHA(f)
   else:dst.symlink_to(f.resolve())
  a.pack=pack
 source_hash={str(p.relative_to(ROOT)):SHA(p) for p in (ROOT/'src').rglob('*') if p.is_file()}
 driver_hash=SHA(Path(__file__))
 native_hash={str(p.relative_to(a.native_build)):SHA(p) for p in (a.native_build/'obj').rglob('*') if p.is_file()}
 dependencies={}
 for dep in (a.native_build/'obj').glob('*.d'):
  if dep.stem=='render_mirror':continue
  for name in dep.read_text().replace('\\\n',' ').split()[1:]:
   if name.startswith('src/') and (a.native_build/name).is_file():dependencies[name]={'build':SHA(a.native_build/name),'current':SHA(ROOT/name)}
 mismatches={n:h for n,h in dependencies.items() if h['build']!=h['current']}
 if mismatches:
  (a.out/'receipt.json').write_text(json.dumps({'status':'FAIL','reason':'native object source dependency mismatch','mismatches':mismatches},indent=2)+'\n');raise SystemExit(1)
 stage=a.out/'instrumented';shutil.copytree(ROOT/'src',stage/'src');(stage/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
 source=(ROOT/'src/render_mirror.c').read_text();marker='void render_mirror_finish(MirrorOutputKind kind,int lightx,int lighty)\n{';assert source.count(marker)==1
 source=source.replace(marker,'static void diagnostic_inner_finish(MirrorOutputKind kind,int lightx,int lighty)\n{')
 # Preflight injections refer to a declaration visible before included code.
 source=source.replace('#include "global_newshf_mirror.inc"','static unsigned diagnostic_slot;\nstatic Uint8 diagnostic_chain_mask[320u*200u*8u*8u];\nstatic unsigned diagnostic_chain_pixels;\nstatic Uint8 diagnostic_secondary_mask[320u*200u*8u*8u];\nstatic unsigned diagnostic_secondary_pixels;\n#include "global_newshf_mirror.inc"')
 wrapper=INJECT.replace('static unsigned diagnostic_slot=100;','')
 wrapper=wrapper.replace('DIAGNOSTIC_START',str(a.start)).replace('DIAGNOSTIC_END',str(a.end))
 needle='\n#else\ntypedef int render_mirror_disabled_translation_unit;';assert source.count(needle)==1;source=source.replace(needle,'\n'+wrapper+needle)
 source=source.replace('#include "shapesy_cyan_layer2_mirror.inc"','#include "shapesy_cyan_layer2_mirror.inc"\n'+CONTROLLED.replace('DIAGNOSTIC_START',str(a.start)).replace('DIAGNOSTIC_END',str(a.end)))
 source=source.replace('static unsigned diagnostic_slot;', 'static void diagnostic_controlled_place(const void *,int,int);\nstatic unsigned diagnostic_slot;')
 cyan=(ROOT/'src/shapesy_cyan_layer2_mirror.inc').read_text();needle='void render_mirror_cyan_layer2(SDL_Surface *surface,const void *first,int x,int y)\n{';assert cyan.count(needle)==1
 cyan=cyan.replace(needle,needle+'\n diagnostic_controlled_place(first,x,y);')
 assert cyan.count('   cyan_borrow_mark(n,*dst);')==1
 cyan=cyan.replace('   cyan_borrow_mark(n,*dst);','   cyan_borrow_mark(n,*dst);if(k>=4)diagnostic_secondary_mask[n]=1;')
 (stage/'src/shapesy_cyan_layer2_mirror.inc').write_text(cyan)
 (stage/'src/render_mirror.c').write_text(source)
 identity=(ROOT/'src/newshf_identity_validation.inc').read_text()
 needle='void render_mirror_newshf_validation_observe(unsigned s)\n{';assert identity.count(needle)==1
 identity=identity.replace(needle,needle+'\n if(s<100&&enemy[s].enemytype==164&&getenv("SCOUT164_CONTROLLED_POSE"))enemy[s].enemycycle=(unsigned)atoi(getenv("SCOUT164_CONTROLLED_POSE"));')
 (stage/'src/newshf_identity_validation.inc').write_text(identity)
 allocation=(ROOT/'src/tyrian2.c').read_text()
 needle='uint JE_makeEnemy(struct JE_SingleEnemyType *enemy, Uint16 eDatI, Sint16 uniqueShapeTableI)\n{';assert allocation.count(needle)==1
 allocation=allocation.replace(needle,needle+'\n if(getenv("SCOUT164_CONTROLLED_ACTOR")&&eDatI>=302&&eDatI<=308)eDatI=164;')
 (stage/'src/tyrian2.c').write_text(allocation)
 inc=(ROOT/'src/global_newshf_mirror.inc').read_text();needle='  if(foreign){Uint32 color=*((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch)+x);';assert inc.count(needle)==1
 injection=r'''  if(foreign){Uint32 color=*((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch)+x);
   const char *mode=getenv("CYAN_AIRCRAFT_DIAGNOSTIC");
   if(mode&&(phase>=28&&phase<=30)&&game_probe_tick>=DIAGNOSTIC_START&&game_probe_tick<=DIAGNOSTIC_END&&!strncmp(mode,"preflight-",10)&&diagnostic_slot==0&&diagnostic_secondary_active(n)&&cyan_borrow_sample(cyan_serial,n,color)&&!shapesy_borrow_sample(shapesy_serial,n,color)){
    diagnostic_slot=slot+1;
    if(!strcmp(mode,"preflight-mismatch")){*((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch)+x)^=1;color^=1;}
    else if(!strcmp(mode,"preflight-untyped"))diagnostic_untyped_pixel=n;
   }
   if(mode&&!strcmp(mode,"preflight-untyped")&&diagnostic_slot&&n==diagnostic_untyped_pixel)cyan_borrow.values[n]=0;
'''
 # The global include precedes ShapesY type definitions. Use a helper hook
 # defined after ShapesY for the test-only removal of one typed value.
 injection=injection.replace('else if(!strcmp(mode,"preflight-untyped"))diagnostic_untyped_pixel=n;','else if(!strcmp(mode,"preflight-untyped"))diagnostic_untype(n);').replace('   if(mode&&!strcmp(mode,"preflight-untyped")&&diagnostic_slot&&n==diagnostic_untyped_pixel)cyan_borrow.values[n]=0;','')
 inc=inc.replace('global_newshf_cyan_dependency=cyan_serial;++cyan_pixels;', 'global_newshf_cyan_dependency=cyan_serial;++cyan_pixels;if(n<sizeof(diagnostic_chain_mask)&&diagnostic_chain_mask[n])++diagnostic_chain_pixels;if(n<sizeof(diagnostic_secondary_mask)&&diagnostic_secondary_mask[n])++diagnostic_secondary_pixels;')
 injection=injection.replace('DIAGNOSTIC_START',str(a.start)).replace('DIAGNOSTIC_END',str(a.end))
 inc=inc.replace(needle,injection);(stage/'src/global_newshf_mirror.inc').write_text(inc)
 source=(stage/'src/render_mirror.c').read_text().replace('static unsigned diagnostic_slot;','static unsigned diagnostic_slot;\nstatic bool diagnostic_secondary_active(size_t);\nstatic void diagnostic_untype(size_t);')
 source=source.replace('static void diagnostic_mutate(const char *which)','static bool diagnostic_secondary_active(size_t n){return (cyan_frame.used&2u)&&n<sizeof(diagnostic_secondary_mask)&&diagnostic_secondary_mask[n];}\nstatic void diagnostic_untype(size_t n){cyan_borrow.values[n]=0;}\nstatic void diagnostic_mutate(const char *which)')
 # Stored slot+1 distinguishes actor slot0 from not injected.
 source=source.replace('diagnostic_slot<100,"preflight injected"','diagnostic_slot>0&&diagnostic_slot<=100,"preflight injected"').replace('global_newshf_dual_preflight_state[diagnostic_slot]==1','global_newshf_dual_preflight_state[diagnostic_slot-1]==1')
 (stage/'src/render_mirror.c').write_text(source)
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu')}
 cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 obj=stage/'render_mirror.o';cmd=['cc','-std=c99','-O2','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(stage/'src'),'-c',str(stage/'src/render_mirror.c'),'-o',str(obj)]
 z=subprocess.run(cmd,env=env,capture_output=True);(a.out/'compile.log').write_bytes(z.stdout+z.stderr);assert z.returncode==0,z.stderr.decode()
 allocation_obj=stage/'tyrian2.o';allocation_cmd=cmd[:-4]+['-c',str(stage/'src/tyrian2.c'),'-o',str(allocation_obj)]
 z=subprocess.run(allocation_cmd,env=env,capture_output=True);(a.out/'compile-allocation.log').write_bytes(z.stdout+z.stderr);assert z.returncode==0,z.stderr.decode()
 exe=stage/'opentyrian-diagnostic';objects=[str(x) for x in sorted((a.native_build/'obj').glob('*.o')) if x.stem not in ('render_mirror','tyrian2')];z=subprocess.run(['cc',str(obj),str(allocation_obj),*objects,*libs,'-lm','-o',str(exe)],env=env,capture_output=True);assert z.returncode==0,z.stderr.decode()
 mutations=['rgba','source','palette','generation','serial','tick','reset','root','geometry','canvas','indexed']
 if a.controlled_chain:mutations+=['layer1-rgba','layer1-source','layer1-serial']
 modes=['baseline']+[when+'-'+m for when in ('final','cached') for m in mutations]+['preflight-mismatch','preflight-untyped','final-transfer-rgba','cached-transfer-rgba','final-occluded-rgba','cached-occluded-rgba','baseline-wrap-rgba','final-wrap-rgba','cached-wrap-rgba','baseline-transfer-wrap-rgba','final-transfer-wrap-rgba','cached-transfer-wrap-rgba']
 if a.modes:
  selected=a.modes.split(',');assert all(m in modes for m in selected),selected
  modes=['baseline']+[m for m in modes[1:] if m in selected]
 if a.pose_only:modes=['baseline']
 def tree_inputs(root):return {str(f):dict(sha256=SHA(f),resolved=str(f.resolve()),symlink=f.is_symlink()) for f in sorted(root.rglob('*')) if f.is_file()}
 result=[]
 def run(mode):
  label=('controlled-' if a.controlled_chain else '')+mode
  out=a.out/label;out.mkdir();cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text('section video\nitem scaler 4x\nitem fullscreen -1\n')
  e={**env,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','HOME':str(out),'XDG_CONFIG_HOME':str(out/'config'),'CYAN_AIRCRAFT_DIAGNOSTIC':mode,'SCOUT164_CONTROLLED_POSE':str(a.pose)}
  if a.pose_only:e['SCOUT164_POSE_ONLY']='1'
  if a.controlled_actor:e['SCOUT164_CONTROLLED_ACTOR']='1'
  if a.controlled_chain:e['CYAN_CONTROLLED_CHAIN']='1'
  cmd=[str(exe),f'--data={a.original_data}','--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=1',f'--asset-debug-level={a.level}',f'--asset-debug-tick={a.start}','--asset-debug-running',f'--render-ticks={a.end+2}',f'--render-assets={a.pack}',f'--global-assets={a.pack}',f'--render-test={a.density}']
  before=dict(binary=SHA(exe),pack=tree_inputs(a.pack),game_data=tree_inputs(a.original_data));(out/'inputs-before.json').write_text(json.dumps(before,indent=2)+'\n')
  start=time.monotonic();z=subprocess.run(cmd,cwd=out,env=e,capture_output=True,timeout=180);(out/'stdout.log').write_bytes(z.stdout);(out/'stderr.log').write_bytes(z.stderr)
  after_inputs=dict(binary=SHA(exe),pack=tree_inputs(a.pack),game_data=tree_inputs(a.original_data));(out/'inputs-after.json').write_text(json.dumps(after_inputs,indent=2)+'\n')
  okay=z.returncode==0 and f'PASS DIAGNOSTIC {label} tick'.encode() in z.stderr and before==after_inputs
  capture={}
  for f in out.glob('*.bmp'):
   import zipfile
   from PIL import Image
   h=SHA(f);Image.open(f).save(f.with_suffix('.png'));archive=f.with_suffix('.zip')
   with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as zz:zz.write(f,f.name)
   with zipfile.ZipFile(archive) as zz:assert zz.namelist()==[f.name] and hashlib.sha256(zz.read(f.name)).hexdigest()==h
   capture[f.name]=dict(sha256=h,archive_sha256=SHA(archive));f.unlink()
  print(label,'PASS' if okay else 'FAIL',flush=True)
  return dict(mode=label,inputs_before=before,inputs_after=after_inputs,inputs_unchanged=before==after_inputs,captures=capture,passed=okay,exit_code=z.returncode,seconds=round(time.monotonic()-start,3),argv=cmd,stderr_sha256=SHA(out/'stderr.log'))
 result.append(run('baseline'))
 if result[0]['passed']:
  with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:result.extend(pool.map(run,modes[1:]))
 after={str(p.relative_to(ROOT)):SHA(p) for p in (ROOT/'src').rglob('*') if p.is_file()}
 native_after={str(p.relative_to(a.native_build)):SHA(p) for p in (a.native_build/'obj').rglob('*') if p.is_file()}
 passed=all(x['passed'] for x in result) and len(result)==len(modes) and after==source_hash and native_after==native_hash and SHA(Path(__file__))==driver_hash
 receipt={'status':'PASS' if passed else 'FAIL','scope':__doc__,'secondary_group_required':not a.pose_only,'record':164,'controlled_pose':a.pose,'pose_only':a.pose_only,'controlled_actor':a.controlled_actor,'physical_level':a.level,'window':[a.start,a.end],'controlled_placement':a.controlled_chain,'natural_state_equality_claimed':False,'canonical_before':source_hash,'canonical_after':after,'injected_sources':{str(p.relative_to(stage)):SHA(p) for p in (stage/'src').rglob('*') if p.is_file()},'diagnostic_binary_sha256':SHA(exe),'driver_sha256':driver_hash,'driver_after_sha256':SHA(Path(__file__)),'native_dependencies':dependencies,'native_objects_before':native_hash,'native_objects_after':native_after,'results':result}
 (a.out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');raise SystemExit(not passed)
if __name__=='__main__':main()
