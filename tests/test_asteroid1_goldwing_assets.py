#!/usr/bin/env python3
"""Explicit-input extracted-production record282 pose and integrity tests.

Reads only named production files, the named ten-family harness, three HDA
files and external tyrian.hdt/newshd.shp. Never scans other test payloads.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,resource,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'assets/hd/packs/asteroid1-ten-v1'
MAIN=r'''
static void actor(Sprite2_array *bank)
{
 struct JE_SingleEnemyType *e=&enemy[0];memset(e,0,sizeof(*e));
 e->enemytype=282;e->enemydatofs=&enemyDat[282];e->sprite2s=bank;e->size=1;e->linknum=40;e->enemydie=535;e->armorleft=3;
 e->ani=6;e->animin=1;e->animax=6;e->aniwhenfire=2;e->enemycycle=1;e->aniactive=2;
 memcpy(e->egr,enemyDat[282].egraphic,sizeof(e->egr));e->tur[0]=59;e->freq[0]=50;e->eyc=2;e->ex=106;e->ey=87;e->mapoffset=0;
}
int main(int argc,char **argv)
{
 assert(argc==5);game_probe_assets=argv[3];records(argv[2]);
 FILE *f=fopen(argv[1],"rb");assert(f);Uint8 *raw=malloc(42012);assert(raw&&fread(raw,1,42012,f)==42012&&fgetc(f)==EOF);fclose(f);
 enemySpriteSheets[0]=(Sprite2_array){42012,raw};enemySpriteSheetIds[0]=8;Sprite2_array source=enemySpriteSheets[0];
 assert(goldwing_source(source)&&asteroid1_scope());actor(&source);
 G101EnemyContext c={282,0,0,1,false,false,true,false};
 if(strcmp(argv[4],"reject")==0){assert(!goldwing_family_ready());assert(!goldwing_draw(&surface,100,80,source,79,0,0,&c));assert(!accepted&&!rejected);goldwing_shutdown();free(raw);return 0;}
 assert(goldwing_family_ready());
 for(unsigned cycle=1;cycle<=6;cycle++) {
  enemy[0].enemycycle=cycle;enemy[0].aniactive=cycle==6?2:1;enemy[0].filter=17;
  const int parts[]={0,1,19,20};
  for(unsigned p=0;p<4;p++) {
   int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
   assert(goldwing_draw(&surface,100+px,80+py,source,enemy[0].egr[cycle-1],part,17,&c));
   assert(last_x==100&&last_y==80&&last_part_x==px&&last_part_y==py&&last_filter==17);
  }
 }
 assert(accepted==24&&logged==24);actor(&source);assert(goldwing_draw(&surface,100,80,source,79,0,0,&c));
 const unsigned armor[]={1,4,5,6,9,12,24,255};for(unsigned i=0;i<sizeof(armor)/sizeof(*armor);i++){enemy[0].armorleft=armor[i];assert(goldwing_draw(&surface,100,80,source,79,0,0,&c));}actor(&source);
#define DECLINE assert(!goldwing_draw(&surface,100,80,source,79,0,0,&c))
#define LIVE(field,value) do{struct JE_SingleEnemyType saved=enemy[0];enemy[0].field=value;DECLINE;enemy[0]=saved;}while(0)
#define CTX(field,value) do{G101EnemyContext saved=c;c.field=value;DECLINE;c=saved;}while(0)
 for(unsigned i=0;i<20;i++){unsigned old=enemy[0].egr[i];enemy[0].egr[i]=999;DECLINE;enemy[0].egr[i]=old;}
 LIVE(enemytype,531);LIVE(enemytype,689);LIVE(enemydatofs,NULL);LIVE(sprite2s,NULL);LIVE(linknum,0);LIVE(enemydie,611);
 LIVE(size,0);LIVE(scoreitem,true);LIVE(edamaged,true);LIVE(armorleft,0);LIVE(ani,3);LIVE(animin,0);LIVE(animax,3);LIVE(aniwhenfire,0);
 LIVE(enemycycle,0);LIVE(enemycycle,7);LIVE(enemycycle,2);LIVE(aniactive,0);LIVE(filter,1);LIVE(tur[0],0);LIVE(tur[1],1);LIVE(tur[2],1);
 LIVE(freq[0],1);LIVE(freq[1],1);LIVE(freq[2],1);LIVE(launchfreq,1);LIVE(launchtype,532);LIVE(launchspecial,1);LIVE(edgr,1);LIVE(edlevel,1);LIVE(edani,1);
 LIVE(exc,1);LIVE(eyc,4);LIVE(fixedmovey,1);LIVE(excc,1);LIVE(eycc,1);LIVE(xaccel,1);LIVE(yaccel,1);LIVE(ex,107);LIVE(ey,88);LIVE(mapoffset,1);
 CTX(type,531);CTX(type,689);CTX(pool_slot,25);CTX(pool_slot,100);CTX(pool_slot,UINT_MAX);CTX(availability,1);CTX(availability,2);CTX(size,0);CTX(score_item,true);CTX(damaged,true);CTX(independent_motion,false);CTX(static_animation,true);
 enemyAvail[0]=1;DECLINE;enemyAvail[0]=0;
 assert(!goldwing_draw(&surface,100,80,source,81,0,0,&c));assert(!goldwing_draw(&surface,100,80,source,83,0,0,&c));assert(!goldwing_draw(&surface,100,80,source,79,2,0,&c));
 assert(!goldwing_draw(&surface,100,80,source,79,0,256,&c));assert(!goldwing_draw(&surface,100,80,source,79,0,-1,&c));
 const int badx[]={INT_MIN,-1,309,INT_MAX},bady[]={INT_MIN,-14,200,INT_MAX};
 for(unsigned i=0;i<4;i++){assert(!goldwing_draw(&surface,badx[i],80,source,79,0,0,&c));assert(!goldwing_draw(&surface,100,bady[i],source,79,0,0,&c));}
 bool *excluded[]={&xmas,&isNetworkGame,&twoPlayerMode,&galagaMode,&twoPlayerLinked,&record_demo,&onePlayerAction,&superTyrian,&timedBattleMode,&bonusLevel,&normalBonusLevelCurrent,&bonusLevelCurrent,&play_demo};
 for(unsigned i=0;i<sizeof(excluded)/sizeof(*excluded);i++){*excluded[i]=true;DECLINE;*excluded[i]=false;}
 lvlFileNum=2;DECLINE;lvlFileNum=9;DECLINE;lvlFileNum=1;episodeNum=2;DECLINE;episodeNum=1;
 asteroid_hd_enabled=false;DECLINE;asteroid_hd_enabled=true;asteroid_hd_lease=false;DECLINE;asteroid_hd_lease=true;
 enemySpriteSheetIds[0]=1;DECLINE;enemySpriteSheetIds[0]=8;spriteSheet8=source;DECLINE;memset(&spriteSheet8,0,sizeof(spriteSheet8));
 enemyDat[282].egraphic[19]=99;assert(!goldwing_source(source));enemyDat[282].egraphic[19]=0;
 raw[200]^=1;DECLINE;assert(rejected==1&&reject_reason);raw[200]^=1;reject_reason=NULL;
 const char *root=game_probe_assets;game_probe_assets="/foreign-goldwing-root";assert(!goldwing_family_ready());game_probe_assets=root;game_probe_density=4;assert(!goldwing_family_ready());game_probe_density=8;
 mirror_logic_tick++;goldwing_resources.member[2].rgba[10]^=1;assert(!goldwing_family_ready());goldwing_resources.member[2].rgba[10]^=1;assert(!goldwing_family_ready());goldwing_shutdown();assert(goldwing_family_ready());
 goldwing_shutdown();free(raw);puts("goldwing six-slot/24-quadrant geometry, exact live identity, source and coherent integrity passed");return 0;
}
'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--sdl-include',action='append',default=[]);p.add_argument('--sanitize',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 spec=importlib.util.spec_from_file_location('ten_harness',ROOT/'tests/test_asteroid1_ten_assets.py');ten=importlib.util.module_from_spec(spec);spec.loader.exec_module(ten)
 source=(ROOT/'src/render_mirror.c').read_text();family=(ROOT/'src/asteroid1_goldwing_mirror.inc').read_text();shared=(ROOT/'src/asteroid1_ten_mirror.inc').read_text();v=(ROOT/'src/varz.h').read_text();start=v.index('struct JE_SingleEnemyType\n{');end=v.index('\n};',start)+3
 structcode=v[start:end]+'\nstatic struct JE_SingleEnemyType enemy[100];\nstatic unsigned char enemyAvail[100];\n'
 code=ten.HARNESS.split('int main(int argc')[0].replace('t=444;t<=453','t=282;t<=282')+MAIN
 code=code.replace('@SCOPE@',ten.extract(source,'asteroid1_level_scope')+ten.extract(source,'asteroid1_scope')).replace('@FAMILY@',structcode+ten.extract(shared,'asteroid1_stamp')+'#include "asteroid1_source_snapshot.inc"\n'+ten.extract(shared,'asteroid1_record_stamp')+family)
 harness=a.out/'harness.c';harness.write_text(code);raw=(a.data/'tyrian.hdt').read_bytes();off=struct.unpack_from('<i',raw)[0]+14+1638*80+61*82+55*37+7*37+19*41+38*86+12*37;record=a.out/'original282-record.bin';record.write_bytes(raw[off+282*77:off+283*77])
 files=[PACK/f'enemy-newshd-{b}-8.hda'for b in[79,81,83]];fixtures=a.out/'fixtures';fixtures.mkdir();variants=[]
 specs=[(f.name,k)for f in files for k in['missing','payload']]+[(files[0].name,k)for k in['magic','role','density','width','height','anchor-x','anchor-y','short','extra','fifo','directory']]
 for n,(target,kind)in enumerate(specs):
  d=fixtures/f'{n:02d}-{kind}';d.mkdir()
  for f in files:
   dest=d/f.name
   if f.name!=target:dest.symlink_to(f)
   elif kind=='missing':continue
   elif kind=='fifo':os.mkfifo(dest)
   elif kind=='directory':dest.mkdir()
   else:
    b=bytearray(f.read_bytes())
    if kind=='payload':b[40]^=1
    elif kind=='magic':b[:4]=b'NOPE'
    elif kind in['role','density','width','height','anchor-x','anchor-y']:struct.pack_into('<I',b,dict(role=4,density=8,width=12,height=16,**{'anchor-x':20,'anchor-y':24})[kind],1)
    elif kind=='short':b=b[:-1]
    elif kind=='extra':b+=b'X'
    dest.write_bytes(b)
  variants.append(d)
 flags=['-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I'+str(ROOT/'src')]+['-I'+x for x in a.sdl_include]
 if not a.sdl_include:flags+=subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True).split()
 runs=[]
 for mode in['optimized']+(['asan-ubsan']if a.sanitize else[]):
  exe=a.out/mode;compiler=['cc',*flags,'-O2']+(['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']if mode=='asan-ubsan'else[])
  def limits():resource.setrlimit(resource.RLIMIT_AS,(1024*1024**2,)*2)
  subprocess.run([*compiler,str(harness),'-o',str(exe)],check=True,preexec_fn=limits)
  for directory,expected in[(PACK,'accept')]+[(d,'reject')for d in variants]:subprocess.run([str(exe),str(a.data/'newshd.shp'),str(record),str(directory),expected],check=True,timeout=10,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
  runs.append(dict(mode=mode,positive=1,negative=len(variants),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
 result=dict(runs=runs,source_sha256=hashlib.sha256(family.encode()).hexdigest(),peak_child_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024,leak_sanitizer=False,scope='Extracted production source, exact full actor struct, six-slot24-quadrant geometry, live phase/base identity and coherent loader. Separate actual-engine pairs required.')
 (a.out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
