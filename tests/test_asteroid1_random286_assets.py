#!/usr/bin/env python3
"""Explicit-input extracted-production record286 pose and integrity tests.

Reads only named production files, the named ten-family harness and bounded static runner, four HDA
files and external tyrian.hdt/newshd.shp. Never scans other test payloads.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,resource,struct,subprocess
from asteroid1_random_static_harness import _run_bounded
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'assets/hd/packs/asteroid1-ten-v1'
MAIN=r'''
static void actor(Sprite2_array *bank)
{
 struct JE_SingleEnemyType *e=&enemy[0];memset(e,0,sizeof(*e));
 e->enemytype=286;e->enemydatofs=&enemyDat[286];e->sprite2s=bank;e->size=1;e->linknum=0;e->enemydie=0;e->armorleft=3;
 e->ani=12;e->animin=1;e->animax=0;e->aniwhenfire=0;e->enemycycle=1;e->aniactive=1;
 memcpy(e->egr,enemyDat[286].egraphic,sizeof(e->egr));e->xaccel=93;e->eyc=2;e->ex=106;e->ey=87;e->mapoffset=0;
}
static unsigned record_byte_mutations,warm_sibling_checks;
static G101EnemyContext context(unsigned type){return (G101EnemyContext){type,0,0,1,false,false,true,false};}
static void exact_record_guards(Sprite2_array source)
{
 /* Toggle each serialized byte independently, including both bytes of words.
  * The visible actor stays 286 when its sibling's motion/graphic moves. */
 for(unsigned t=286;t<=286;t++) {
#define MUTATE(v) do { \
  for(unsigned bit_=1;bit_<=(sizeof(enemyDat[t].v)==2?256U:1U);bit_*=256U) { \
   enemyDat[t].v^=bit_;assert(!asteroid_random286_source(source)); \
   enemyDat[t].v^=bit_;assert(asteroid_random286_source(source));record_byte_mutations++; \
  } \
 } while(0)
  MUTATE(ani);for(unsigned i=0;i<3;i++)MUTATE(tur[i]);for(unsigned i=0;i<3;i++)MUTATE(freq[i]);
  MUTATE(xmove);MUTATE(ymove);MUTATE(xaccel);MUTATE(yaccel);MUTATE(xcaccel);MUTATE(ycaccel);
  MUTATE(startx);MUTATE(starty);MUTATE(startxc);MUTATE(startyc);MUTATE(armor);MUTATE(esize);
  for(unsigned i=0;i<20;i++)MUTATE(egraphic[i]);
  MUTATE(explosiontype);MUTATE(animate);MUTATE(shapebank);MUTATE(xrev);MUTATE(yrev);MUTATE(dgr);
  MUTATE(dlevel);MUTATE(dani);MUTATE(elaunchfreq);MUTATE(elaunchtype);MUTATE(value);MUTATE(eenemydie);
#undef MUTATE
 }
 assert(record_byte_mutations==1U*77);
 G101EnemyContext c=context(286);
 for(unsigned t=286;t<=286;t++) {
#define WARM_MUTATE(v) do { \
  assert(asteroid_random286_draw(&surface,100,80,source,229,0,0,&c)); \
  unsigned rejected_before_=rejected,accepted_before_=accepted; \
  enemyDat[t].v^=1;assert(!asteroid_random286_draw(&surface,112,80,source,229,1?1:0,0,&c)); \
  assert(rejected==rejected_before_+1&&accepted==accepted_before_); \
  assert(reject_reason&&!strcmp(reject_reason,"asteroid-random286-family-integrity")); \
  enemyDat[t].v^=1;reject_reason=NULL;assert(asteroid_random286_source(source));warm_sibling_checks++; \
 } while(0)
  WARM_MUTATE(ymove);WARM_MUTATE(egraphic[19]);
#undef WARM_MUTATE
 }
 assert(warm_sibling_checks==1U*2);
}
static void source_guards(Sprite2_array source)
{
 Uint8 *bank=source.data,*rebound=malloc(source.size);assert(rebound);
 memcpy(rebound,bank,source.size);
 Sprite2_array alternate={source.size,rebound};
 assert(source.data!=asteroid1_source_snapshot.bytes);
 assert(!asteroid_random286_source((Sprite2_array){source.size,NULL}));
 assert(!asteroid_random286_source((Sprite2_array){source.size-1,bank}));
 assert(!asteroid_random286_source(alternate)); /* A byte-identical ordinary/unbound bank. */
 spriteSheet8=alternate;assert(!asteroid_random286_source(alternate));
 enemySpriteSheets[0]=alternate;assert(!asteroid_random286_source(alternate));
 memset(&spriteSheet8,0,sizeof(spriteSheet8));assert(asteroid_random286_source(alternate));actor(&alternate);
 assert(!asteroid_random286_source(source)); /* Stale binding after the bank was rebound. */
 const unsigned offsets[]={0,200,42011};
 G101EnemyContext c=context(286);
 for(unsigned j=0;j<3;j++) {
  assert(asteroid_random286_draw(&surface,100,80,alternate,229,0,0,&c));
  unsigned before=rejected;
  rebound[offsets[j]]^=1;assert(!asteroid_random286_source(alternate));
  assert(!asteroid_random286_draw(&surface,112,80,alternate,229,1?1:0,0,&c));
  assert(rejected==before+1&&reject_reason&&!strcmp(reject_reason,"asteroid-random286-family-integrity"));
  rebound[offsets[j]]^=1;reject_reason=NULL;assert(asteroid_random286_source(alternate));
 }
 enemySpriteSheets[0]=source;actor(&source);free(rebound);assert(asteroid_random286_source(source));
 for(unsigned slot=0;slot<4;slot++) {
  memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
  enemySpriteSheets[slot]=source;enemySpriteSheetIds[slot]=8;assert(asteroid_random286_source(source));
  enemySpriteSheetIds[slot]=1;assert(!asteroid_random286_source(source));enemySpriteSheetIds[slot]=8;
  enemySpriteSheets[slot].size--;assert(!asteroid_random286_source(source));enemySpriteSheets[slot].size++;
 }
 memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
 enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=8;
 spriteSheet8=source;assert(!asteroid_random286_source(source));memset(&spriteSheet8,0,sizeof(spriteSheet8));
 for(unsigned j=0;j<3;j++) {
  assert(asteroid_random286_draw(&surface,100,80,source,229,0,0,&c));
  unsigned before=rejected;
  bank[offsets[j]]^=1;assert(!asteroid_random286_source(source));
  assert(!asteroid_random286_draw(&surface,112,80,source,229,1?1:0,0,&c));assert(rejected==before+1);
  bank[offsets[j]]^=1;reject_reason=NULL;assert(asteroid_random286_source(source));
 }
 /* With no accepted call this tick, a corrupt source is plain classic fallback. */
 mirror_logic_tick++;unsigned before=rejected;
 bank[200]^=1;assert(!asteroid_random286_draw(&surface,100,80,source,229,0,0,&c));assert(rejected==before&&!reject_reason);
 bank[200]^=1;assert(asteroid_random286_source(source));
}
int main(int argc,char **argv)
{
 assert(argc==5);game_probe_assets=argv[3];records(argv[2]);
 FILE *f=fopen(argv[1],"rb");assert(f);Uint8 *raw=malloc(42012);assert(raw&&fread(raw,1,42012,f)==42012&&fgetc(f)==EOF);fclose(f);
 enemySpriteSheets[0]=(Sprite2_array){42012,raw};enemySpriteSheetIds[0]=8;Sprite2_array source=enemySpriteSheets[0];
 assert(asteroid_random286_source(source)&&asteroid1_scope());actor(&source);
 G101EnemyContext c={286,0,0,1,false,false,true,false};
 if(strcmp(argv[4],"reject")==0){assert(!asteroid_random286_family_ready());assert(!asteroid_random286_draw(&surface,100,80,source,229,0,0,&c));assert(!accepted&&!rejected);asteroid_random286_shutdown();free(raw);return 0;}
 assert(asteroid_random286_family_ready());
 exact_record_guards(source);source_guards(source);mirror_logic_tick++;rejected=0;accepted=logged=0;actor(&source);
 for(unsigned cycle=1;cycle<=12;cycle++) {
  enemy[0].enemycycle=cycle;enemy[0].aniactive=1;enemy[0].filter=17;
  const int parts[]={0,1,19,20};
  for(unsigned p=0;p<4;p++) {
   int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
   assert(asteroid_random286_draw(&surface,100+px,80+py,source,enemy[0].egr[cycle-1],part,17,&c));
   assert(last_x==100&&last_y==80&&last_part_x==px&&last_part_y==py&&last_filter==17);
  }
 }
 assert(accepted==48&&logged==48);actor(&source);assert(asteroid_random286_draw(&surface,100,80,source,229,0,0,&c));
 for(int vx=-4;vx<=4;vx++){enemy[0].exc=vx;assert(asteroid_random286_draw(&surface,100,80,source,229,0,0,&c));}actor(&source);
 const unsigned armor[]={1,4,5,6,9,12,24,255};for(unsigned i=0;i<sizeof(armor)/sizeof(*armor);i++){enemy[0].armorleft=armor[i];assert(asteroid_random286_draw(&surface,100,80,source,229,0,0,&c));}actor(&source);
#define DECLINE assert(!asteroid_random286_draw(&surface,100,80,source,229,0,0,&c))
#define LIVE(field,value) do{struct JE_SingleEnemyType saved=enemy[0];enemy[0].field=value;DECLINE;enemy[0]=saved;}while(0)
#define CTX(field,value) do{G101EnemyContext saved=c;c.field=value;DECLINE;c=saved;}while(0)
 for(unsigned i=0;i<20;i++){unsigned old=enemy[0].egr[i];enemy[0].egr[i]=999;DECLINE;enemy[0].egr[i]=old;}
 LIVE(enemytype,531);LIVE(enemytype,689);LIVE(enemydatofs,NULL);LIVE(sprite2s,NULL);LIVE(linknum,1);LIVE(enemydie,611);
 LIVE(size,0);LIVE(scoreitem,true);LIVE(edamaged,true);LIVE(armorleft,0);LIVE(ani,3);LIVE(animin,0);LIVE(animax,3);LIVE(aniwhenfire,2);
 LIVE(enemycycle,0);LIVE(enemycycle,13);LIVE(enemycycle,2);LIVE(aniactive,0);LIVE(filter,1);LIVE(tur[0],59);LIVE(tur[1],1);LIVE(tur[2],1);
 LIVE(freq[0],1);LIVE(freq[1],1);LIVE(freq[2],1);LIVE(launchfreq,1);LIVE(launchtype,532);LIVE(launchspecial,1);LIVE(edgr,1);LIVE(edlevel,1);LIVE(edani,1);
 LIVE(exc,5);LIVE(exc,-5);LIVE(eyc,4);LIVE(fixedmovey,1);LIVE(excc,1);LIVE(eycc,1);LIVE(xaccel,1);LIVE(yaccel,1);LIVE(ex,107);LIVE(ey,88);LIVE(mapoffset,1);
 CTX(type,531);CTX(type,689);CTX(pool_slot,25);CTX(pool_slot,100);CTX(pool_slot,UINT_MAX);CTX(availability,1);CTX(availability,2);CTX(size,0);CTX(score_item,true);CTX(damaged,true);CTX(independent_motion,false);CTX(static_animation,true);
 enemyAvail[0]=1;DECLINE;enemyAvail[0]=0;
 assert(!asteroid_random286_draw(&surface,100,80,source,231,0,0,&c));assert(!asteroid_random286_draw(&surface,100,80,source,233,0,0,&c));assert(!asteroid_random286_draw(&surface,100,80,source,229,2,0,&c));
 assert(!asteroid_random286_draw(&surface,100,80,source,229,0,256,&c));assert(!asteroid_random286_draw(&surface,100,80,source,229,0,-1,&c));
 const int badx[]={INT_MIN,-1,309,INT_MAX},bady[]={INT_MIN,-14,200,INT_MAX};
 for(unsigned i=0;i<4;i++){assert(!asteroid_random286_draw(&surface,badx[i],80,source,229,0,0,&c));assert(!asteroid_random286_draw(&surface,100,bady[i],source,229,0,0,&c));}
 bool *excluded[]={&xmas,&isNetworkGame,&twoPlayerMode,&galagaMode,&twoPlayerLinked,&record_demo,&onePlayerAction,&superTyrian,&timedBattleMode,&bonusLevel,&normalBonusLevelCurrent,&bonusLevelCurrent,&play_demo};
 for(unsigned i=0;i<sizeof(excluded)/sizeof(*excluded);i++){*excluded[i]=true;DECLINE;*excluded[i]=false;}
 lvlFileNum=2;DECLINE;lvlFileNum=9;DECLINE;lvlFileNum=1;episodeNum=2;DECLINE;episodeNum=1;
 asteroid_hd_enabled=false;DECLINE;asteroid_hd_enabled=true;asteroid_hd_lease=false;DECLINE;asteroid_hd_lease=true;
 superArcadeMode=1;DECLINE;superArcadeMode=0;
 active=false;DECLINE;active=true;game_probe_scene_assets=0;DECLINE;game_probe_scene_assets=1;
 SDL_Surface original_surface=surface;SDL_PixelFormat original_format=format;
 surface.pixels=NULL;DECLINE;surface=original_surface;surface.w=321;DECLINE;surface=original_surface;
 surface.h=201;DECLINE;surface=original_surface;surface.pitch=321;DECLINE;surface=original_surface;
 surface.format=NULL;DECLINE;surface=original_surface;format.format=SDL_PIXELFORMAT_RGBA8888;DECLINE;format=original_format;
 format.BitsPerPixel=32;DECLINE;format=original_format;format.BytesPerPixel=4;DECLINE;format=original_format;
 game_screen=NULL;DECLINE;game_screen=&surface;VGAScreen=NULL;DECLINE;VGAScreen=&surface;
 assert(!asteroid_random286_draw(NULL,100,80,source,229,0,0,&c));
 game_probe_missing=true;assert(!asteroid_random286_family_ready());game_probe_missing=false;
 game_probe_invalid=true;assert(!asteroid_random286_family_ready());game_probe_invalid=false;
 game_probe_original_reference=true;assert(!asteroid_random286_family_ready());game_probe_original_reference=false;
 enemySpriteSheetIds[0]=1;DECLINE;enemySpriteSheetIds[0]=8;spriteSheet8=source;DECLINE;memset(&spriteSheet8,0,sizeof(spriteSheet8));
 enemyDat[286].egraphic[19]=99;assert(!asteroid_random286_source(source));enemyDat[286].egraphic[19]=0;
 raw[200]^=1;DECLINE;assert(rejected==1&&reject_reason);raw[200]^=1;reject_reason=NULL;
 const char *root=game_probe_assets;game_probe_assets="/foreign-asteroid_random286-root";assert(!asteroid_random286_family_ready());game_probe_assets=root;game_probe_density=4;assert(!asteroid_random286_family_ready());game_probe_density=8;
 mirror_logic_tick++;asteroid_random286_resources.member[2].rgba[10]^=1;assert(!asteroid_random286_family_ready());asteroid_random286_resources.member[2].rgba[10]^=1;assert(!asteroid_random286_family_ready());asteroid_random286_shutdown();assert(asteroid_random286_family_ready());
 asteroid_random286_shutdown();free(raw);puts("asteroid_random286 12-slot/48-quadrant geometry, exact live identity, source and coherent integrity passed");return 0;
}
'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--sdl-include',action='append',default=[]);p.add_argument('--sanitize',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 spec=importlib.util.spec_from_file_location('ten_harness',ROOT/'tests/test_asteroid1_ten_assets.py');ten=importlib.util.module_from_spec(spec);spec.loader.exec_module(ten)
 source=(ROOT/'src/render_mirror.c').read_text();family=(ROOT/'src/asteroid1_random286_mirror.inc').read_text();shared=(ROOT/'src/asteroid1_ten_mirror.inc').read_text();v=(ROOT/'src/varz.h').read_text();start=v.index('struct JE_SingleEnemyType\n{');end=v.index('\n};',start)+3
 structcode=v[start:end]+'\nstatic struct JE_SingleEnemyType enemy[100];\nstatic unsigned char enemyAvail[100];\n'
 code=ten.HARNESS.split('int main(int argc')[0].replace('t=444;t<=453','t=286;t<=286')+MAIN
 code=code.replace('@SCOPE@',ten.extract(source,'asteroid1_level_scope')+ten.extract(source,'asteroid1_scope')).replace('@FAMILY@',structcode+ten.extract(shared,'asteroid1_stamp')+'#include "asteroid1_source_snapshot.inc"\n'+ten.extract(shared,'asteroid1_record_stamp')+family)
 harness=a.out/'harness.c';harness.write_text(code);raw=(a.data/'tyrian.hdt').read_bytes();off=struct.unpack_from('<i',raw)[0]+14+1638*80+61*82+55*37+7*37+19*41+38*86+12*37;record=a.out/'original286-record.bin';record.write_bytes(raw[off+286*77:off+287*77])
 files=[PACK/f'enemy-newshd-{b}-8.hda'for b in[229,231,233,235]];fixtures=a.out/'fixtures';fixtures.mkdir(exist_ok=True);variants=[]
 specs=[(f.name,k)for f in files for k in['missing','payload']]+[(files[0].name,k)for k in['magic','role','foreign-base','density','width','height','anchor-x','anchor-y','header-short','short','extra','fifo','directory','broken-symlink']]
 for n,(target,kind)in enumerate(specs):
  d=fixtures/f'{n:02d}-{kind}';d.mkdir(exist_ok=True)
  for f in files:
   dest=d/f.name
   if dest.exists() or dest.is_symlink():continue
   if f.name!=target:dest.symlink_to(f)
   elif kind=='missing':continue
   elif kind=='fifo':os.mkfifo(dest)
   elif kind=='directory':dest.mkdir()
   elif kind=='broken-symlink':dest.symlink_to(d/'absent.hda')
   else:
    b=bytearray(f.read_bytes())
    if kind=='payload':b[40]^=1
    elif kind=='magic':b[:4]=b'NOPE'
    elif kind=='foreign-base':struct.pack_into('<I',b,4,1080231)
    elif kind=='header-short':b=b[:12]
    elif kind in['role','density','width','height','anchor-x','anchor-y']:struct.pack_into('<I',b,dict(role=4,density=8,width=12,height=16,**{'anchor-x':20,'anchor-y':24})[kind],1)
    elif kind=='short':b=b[:-1]
    elif kind=='extra':b+=b'X'
    dest.write_bytes(b)
  variants.append(d)
 flags=['-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I'+str(ROOT/'src')]+['-I'+x for x in a.sdl_include]
 if not a.sdl_include:flags+=subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True).split()
 isolated=fixtures/'isolated-own-family';isolated.mkdir(exist_ok=True)
 for f in files:
  if not (isolated/f.name).is_symlink():(isolated/f.name).symlink_to(f)
 runs=[];compiler_peak=runtime_peak=0
 for mode in['optimized']+(['asan-ubsan']if a.sanitize else[]):
  exe=a.out/mode;compiler=['cc',*flags,'-O2']+(['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']if mode=='asan-ubsan'else[])
  def limits():resource.setrlimit(resource.RLIMIT_AS,(1024*1024**2,)*2)
  compiler_peak=max(compiler_peak,_run_bounded([*compiler,str(harness),'-o',str(exe)],compiler=True))
  for directory,expected in[(PACK,'accept'),(isolated,'accept')]+[(d,'reject')for d in variants]:runtime_peak=max(runtime_peak,_run_bounded([str(exe),str(a.data/'newshd.shp'),str(record),str(directory),expected],sanitize=mode=='asan-ubsan'))
  runs.append(dict(mode=mode,positive=2,negative=len(variants),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
 result=dict(record=286,source_record_byte_mutations=77,warm_record_mutations=2,animation_slots=12,ordered_quadrants=48,fixture_count=len(variants),runtime_peak_rss_bytes=runtime_peak,compiler_peak_rss_bytes=compiler_peak,runtime_memory_limit_bytes=512*1024**2,compiler_address_space_limit_bytes=1024*1024**2,runs=runs,source_sha256=hashlib.sha256(family.encode()).hexdigest(),peak_child_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,leak_sanitizer=False,scope='Extracted production source, exact full actor struct, 12-slot/48-quadrant geometry, live phase/base identity and coherent loader. Separate actual-engine pairs required.')
 (a.out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
