#!/usr/bin/env python3
"""Native production-TU shared91 lifecycle regression; not a game playthrough.

Only this test file is authored here. Builds an immutable local source snapshot;
original bank/palette bytes are streamed to the child, not persisted. The actual
renderer begin/finish, enemy wrapper and native indexed blitter are exercised.
"""
from pathlib import Path
import argparse, hashlib, json, os, resource, shutil, struct, subprocess
from global_talon_reconstruction import extract
ROOT = Path(__file__).resolve().parents[1]
SHA = lambda b: hashlib.sha256(b).hexdigest()
PINS = {
    'mirror_enabled': 'dd0c74003c0a199ddd5c8dcb0aff71a07baead1c6e19c3f09841c6f2615670c1',
    'asteroid1_level_scope': 'a60b685f43e923b061dd6c9c8c75d24256f50c1edb1d92e5a2304198f7b585cd',
    'asteroid1_scope': '13de44e175f7a0ae91e7a0d49fbcba88bbb2897f115bcf3cc9d73465284fa4d1',
}
OLD_OWNER_PINS = {'global_cash25_mirror.inc': '0092bacb866753da033a6d6a54af9fdb787110c74f729bfebf477c0d44e1b64c', 'global_green_mirror.inc': '89d292d6cd7c946579c78dc503287afb75c386aa660238d89042c5b2e9e69c15', 'global_hitflare_mirror.inc': '0fce1f7c51c774338b352ceaa0bfb58073ee378590f8a2793401be074a22dd10', 'global_newshf_mirror.inc': '14089f205fb786ef60d689dece58de4cd370a5a34198f664cece2b583eb3c361', 'global_pulse_mirror.inc': 'c51c264d0c32f757fe9465a3c5b045b9234251914410d788451fef82341cfbd4', 'global_rotor_mirror.inc': '144b85e9ea4469346a1bfd4c8a9f38529920e1192e34161ae8eb56c9ab1ad283', 'global_shield_mirror.inc': 'f0ce8600e2765141cb3af13dfb3241a4ae02102bbb1b30e05df58def16757cb5', 'global_small_explosion_mirror.inc': '08f3a16761c530e3413b686915b0f70b726a1247152f3783a950ee5446fbc8e3', 'global_smoke_mirror.inc': '19c570e67a35e48b22d426c6d3b01192aec453a56fc14eb4c443a069de64e024', 'global_talon_mirror.inc': 'c7456d1ec292faa5e4b895cd7982b1143b6c2b2eaa90a576f0d595f1958a9119', 'global_vulcan_mirror.inc': 'e215b407511cb6f90a01dd1f11d4f86268093178dfa2692bbf3c6316d7dced92'}
HARNESS = r'''
#include "render_mirror.c"
#include "entity_draw.h"
#include "mtrand.h"
static unsigned checks,cases;
#define CHECK(x) do {if(!(x)){fprintf(stderr,"case%u line%d: %s\n",cases,__LINE__,#x);abort();}++checks;} while(0)
static Uint8 original[32060],livebank[32060],mask91[168],source91[168];
static Uint32 palette0[256];
static const char *valid_root,*missing_root;
static Uint32 *at(SDL_Surface *s,int x,int y){return (Uint32*)((Uint8*)s->pixels+y*s->pitch)+x;}
static void read_exact(void *p,size_t n){CHECK(fread(p,1,n,stdin)==n);}
static void setup(unsigned ep,unsigned level)
{
 ++cases;render_mirror_hud_shutdown();
 if(canvas)SDL_FreeSurface(canvas);if(output)SDL_FreeSurface(output);if(game_screen)SDL_FreeSurface(game_screen);if(VGAScreenSeg)SDL_FreeSurface(VGAScreenSeg);if(fade_saved)SDL_FreeSurface(fade_saved);
 canvas=output=fade_saved=NULL;free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);hd_owner=cloud_owner=green_under_owner=NULL;green_first=NULL;green_under=NULL;
 game_screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);VGAScreen=game_screen;VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(game_screen&&VGAScreenSeg);
 memcpy(livebank,original,sizeof(original));spriteSheet8=(Sprite2_array){sizeof(livebank),livebank};spriteSheet12=(Sprite2_array){0,NULL};
 game_probe_density=8;game_probe_enabled=game_probe_missing=game_probe_invalid=game_probe_original_reference=false;
 manual_hd_enabled=asteroid_hd_enabled=manual_hd_lease=asteroid_hd_lease=shared_hud_lease=false;
 xmas=false;episodeNum=ep;lvlFileNum=level;game_probe_assets=NULL;
 memset(enemy,0,sizeof(enemy));memset(enemyAvail,1,sizeof(enemyAvail));memcpy(rgb_palette,palette0,sizeof(palette0));
 SDL_FillRect(game_screen,NULL,0x1b);SDL_FillRect(VGAScreenSeg,NULL,0x1b);
 CHECK(render_mirror_set_global_assets(valid_root));render_mirror_begin();
 CHECK(!game_probe_enabled&&!active&&!mirror_enabled());CHECK(global_projectile91_frame);
 CHECK(decode_tile(spriteSheet8,91,source91,mask91,12,0,0));
}
static void draw(int x,int y)
{
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(classic);memcpy(classic->pixels,game_screen->pixels,64000);
 uint64_t rng=mt_state_fingerprint();JE_MultiEnemyType actors;memcpy(actors,enemy,sizeof(enemy));EnemyShotType shots[ENEMY_SHOT_MAX];memcpy(shots,enemyShot,sizeof(shots));
 blit_sprite2(classic,x,y,spriteSheet8,91);draw_enemy_shot_sprite2(game_screen,x,y,spriteSheet8,91);
 CHECK(!memcmp(classic->pixels,game_screen->pixels,64000));CHECK(rng==mt_state_fingerprint());CHECK(!memcmp(actors,enemy,sizeof(enemy)));CHECK(!memcmp(shots,enemyShot,sizeof(shots)));SDL_FreeSurface(classic);
}
static void final_copy(void){for(int y=0;y<184;y++)memcpy((Uint8*)VGAScreenSeg->pixels+y*320,(Uint8*)game_screen->pixels+y*320+24,264);}
static void finish(void){final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);}
static Uint32 alpha(Uint32 under,const Uint8 *a){unsigned r=(((under>>16)&255)*(255-a[3])+a[0]*a[3]+127)/255,g=(((under>>8)&255)*(255-a[3])+a[1]*a[3]+127)/255,b=((under&255)*(255-a[3])+a[2]*a[3]+127)/255;return 0xff000000u|(r<<16)|(g<<8)|b;}
static void canvas_oracle(int x,int y)
{
 const Uint8 *rgba=projectile91_resources.member.rgba;CHECK(rgba);
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++){
  int px=x*8+ax,py=y*8+ay;if(px<0||px>=2560||py<0||py>=1600)continue;
  CHECK(*at(canvas,px,py)==alpha(palette_rgb(0x1b),rgba+4*(ay*96+ax)));
 }
}
static void output_oracle(void){unsigned n=0;for(int y=0;y<184*8;y++)for(int x=24*8;x<288*8;x++)if(global_projectile91_owner[y*2560+x]){CHECK(*at(output,x-24*8,y)==*at(canvas,x,y));++n;}CHECK(n>0);}
static void positives(void)
{
 unsigned eps[]={1,5,3},levels[]={12,5,10};
 for(unsigned i=0;i<3;i++){setup(eps[i],levels[i]);CHECK(!asteroid1_level_scope());draw(110,80);CHECK(global_projectile91_contributed&&!global_projectile91_fault);canvas_oracle(110,80);finish();CHECK(ready&&last_output_valid&&global_projectile91_cached);output_oracle();}
 int ys[]={-13,-6,0,180,190,199};for(unsigned i=0;i<sizeof(ys)/sizeof(*ys);i++){setup(1,12);draw(110,ys[i]);CHECK(!global_projectile91_fault);canvas_oracle(110,ys[i]);finish();}
 setup(1,12);CHECK(!projectile304_draw(game_screen,110,80,spriteSheet8,304));CHECK(!projectile304_resources.checked);CHECK(!get_asset(spriteSheet8,91,ENTITY_TILE));
}
static void mutations(void)
{
 for(unsigned k=0;k<8;k++){
  setup(1,12);draw(110,80);CHECK(global_projectile91_contributed);Uint8 saved=livebank[100];Uint8 *payload=projectile91_resources.member.rgba;Uint8 pv=payload[100];int pitch=game_screen->pitch;
  switch(k){case 0:livebank[100]^=1;break;case 1:rgb_palette[1]^=1;break;case 2:payload[100]^=1;break;case 3:xmas=true;break;case 4:game_probe_original_reference=true;break;case 5:game_screen->pitch=321;break;case 6:spriteSheet8.size--;break;case 7:projectile91_resources.member.anchor_x=1;break;}
  if(k!=5){finish();CHECK(!ready&&!last_output_valid);}else{global_projectile91_observed_preflight();CHECK(global_projectile91_fault);}
  livebank[100]=saved;payload[100]=pv;game_screen->pitch=pitch;
 }
 /* Cold palette mismatch cannot borrow an otherwise authenticated bank. */
 setup(1,12);rgb_palette[1]^=1;draw(110,80);CHECK(!global_projectile91_contributed);finish();CHECK(!ready);
 /* New logic generation must not carry prior ownership or conceal mutation. */
 setup(1,12);draw(110,80);finish();CHECK(ready);livebank[100]^=1;render_mirror_begin();CHECK(!global_projectile91_contributed&&!active);draw(110,80);finish();CHECK(!ready);livebank[100]^=1;
}
static void witnesses(void)
{
 setup(1,12);CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,91));render_mirror_entity_end();CHECK(global_projectile91_fault);finish();CHECK(!ready);
 setup(1,12);CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,91));CHECK(!render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,91));CHECK(global_projectile91_fault);
 setup(1,12);CHECK(render_mirror_enemy_shot(game_screen,110,80,spriteSheet8,91));unsigned i=0;while(!mask91[i])++i;Uint8 *p=(Uint8*)game_screen->pixels+(80+i/12)*320+110+i%12;*p=source91[i];render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);CHECK(global_projectile91_fault);
}
static void foreign_writes(void)
{
 setup(1,12);draw(110,80);unsigned i=0;while(!mask91[i])++i;int x=110+i%12,y=80+i/12;
 Uint8 *p=(Uint8*)game_screen->pixels+y*320+x;*p=0x3a;render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);finish();CHECK(ready);
 for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)CHECK(*at(output,(x-24)*8+sx,y*8+sy)==palette_rgb(0x3a));
 /* Final-surface writes revoke cached coverage and must win on presentation. */
 p=(Uint8*)VGAScreenSeg->pixels+(y+1)*320+x-24;*p=0x5b;render_mirror_pixel(VGAScreenSeg,p,*p,MIRROR_NORMAL);
 for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)CHECK(!global_projectile91_owner[((y+1)*8+sy)*2560+x*8+sx]);
 setup(1,12);draw(110,80);final_copy();render_mirror_finish(MIRROR_OUTPUT_UNSUPPORTED,0,0);CHECK(!ready);
}
static void talon_tile(void)
{
 global_talon_pose(1,spriteSheet9,233,233,0);
 CHECK(render_mirror_global_player_ship(game_screen,108,78,spriteSheet9,233,MIRROR_NORMAL,1,233)==1);
 blit_sprite2x2(game_screen,108,78,spriteSheet9,233);render_mirror_entity_end();CHECK(global_talon_contributed&&!global_talon_fault);
}
static void independent_absence(void)
{
 const char *saved=valid_root;setup(1,12);blit_sprite2(game_screen,110,80,spriteSheet8,91);render_mirror_entity_end();talon_tile();finish();CHECK(ready);
 size_t n=(size_t)output->pitch*output->h;Uint8 *before=malloc(n);CHECK(before);memcpy(before,output->pixels,n);
 valid_root=missing_root;setup(1,12);draw(110,80);CHECK(!global_projectile91_contributed);talon_tile();finish();CHECK(ready);CHECK(n==(size_t)output->pitch*output->h);CHECK(!memcmp(before,output->pixels,n));free(before);valid_root=saved;
}
static void cross_owner(void)
{
 setup(1,12);draw(110,80);
 global_talon_pose(1,spriteSheet9,233,233,0);
 CHECK(render_mirror_global_player_ship(game_screen,108,78,spriteSheet9,233,MIRROR_NORMAL,1,233)==1);
 blit_sprite2x2(game_screen,108,78,spriteSheet9,233);render_mirror_entity_end();CHECK(global_talon_contributed&&!global_talon_fault);
 finish();CHECK(ready);livebank[100]^=1;global_projectile91_check_cache();CHECK(!ready&&!last_output_valid);
 /* Source proof must survive transfer, including when no91 pixels remain. */
 setup(1,12);draw(110,80);memset(global_projectile91_owner,0,global_projectile91_capacity);
 livebank[100]^=1;finish();CHECK(!ready&&!last_output_valid);
}
static void fades(void)
{
 SDL_Color black={0,0,0,255};
 setup(1,12);draw(110,80);finish();CHECK(ready);
 render_mirror_fade_start(NULL,&black,0,255);
 if(global_projectile91_cached){
  CHECK(have_fade_saved);rgb_palette[1]^=1;
  CHECK(!global_projectile91_fade_step_valid(7));CHECK(!ready&&!last_output_valid&&!have_fade_saved);
 }else CHECK(!ready&&!last_output_valid); /* Explicit fade decline is allowed. */
 setup(1,12);draw(110,80);finish();CHECK(ready);
 render_mirror_fade_start(NULL,&black,0,255);
 if(global_projectile91_cached){CHECK(!global_projectile91_fade_step_valid(0));CHECK(!ready&&!last_output_valid);}
}
static void retained(void)
{
 for(unsigned k=0;k<5;k++){
  setup(1,12);draw(110,80);finish();CHECK(ready&&global_projectile91_cached);
  switch(k){case 0:livebank[100]^=1;break;case 1:rgb_palette[5]^=1;break;case 2:projectile91_resources.member.rgba[101]^=1;break;case 3:((Uint8*)VGAScreenSeg->pixels)[0]^=1;break;case 4:CHECK(render_mirror_set_global_assets(""));break;}
  global_projectile91_check_cache();CHECK(!ready&&!last_output_valid&&!have_fade_saved);
 }
 setup(1,12);draw(110,80);finish();CHECK(ready);CHECK(render_mirror_set_global_assets("/deliberately-missing-91"));render_mirror_begin();draw(110,80);finish();CHECK(!ready&&!projectile91_resources.valid);
}
int main(int argc,char **argv)
{
 CHECK(argc==3);valid_root=argv[1];missing_root=argv[2];read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));Uint32 n;read_exact(&n,4);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);CHECK(fgetc(stdin)==EOF);
 positives();mutations();witnesses();foreign_writes();independent_absence();cross_owner();fades();retained();
 printf("PASS shared91 native lifecycle: %u cases %u assertions; legacy inactive; not full gameplay\n",cases,checks);return 0;
}
'''

def bounded():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (240, 240))

def main():
    test_bytes=Path(__file__).read_bytes()
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,required=True);p.add_argument('--sysroot',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--sanitize',action='store_true')
    p.add_argument('--prepare-only',action='store_true');p.add_argument('--skip-build',action='store_true')
    a=p.parse_args();a.out=a.out.resolve();a.sysroot=a.sysroot.resolve();a.data=a.data.resolve();a.out.mkdir(parents=True,exist_ok=True)
    assert shutil.disk_usage(a.out).free>5*1024**3
    source={str(x.relative_to(ROOT/'src')):x.read_bytes() for x in (ROOT/'src').rglob('*') if x.is_file()}
    for n,h in OLD_OWNER_PINS.items():
        clear=b'  if(global_projectile91_owner)global_projectile91_owner[n]=global_projectile91_foreign[n]=0;\n'
        assert source[n].count(clear)==1 and SHA(source[n].replace(clear,b''))==h,(n,'prior owner changed beyond clearing91')
    for n,h in PINS.items():assert SHA(extract(source['render_mirror.c'].decode(),n).encode())==h,(n,'legacy activation scope changed')
    assert SHA(source['asteroid1_projectile304_mirror.inc'])=='210732124398c21a308309218bc5ce4f98619cc147685fa42b12dd3e22e1b43c'
    build=a.out/'build';build.mkdir(exist_ok=True);(build/'src').mkdir(exist_ok=True)
    for name,b in source.items():
        f=build/'src'/name;f.parent.mkdir(parents=True,exist_ok=True)
        if a.skip_build:assert f.read_bytes()==b,(name,'snapshot stale')
        else:f.write_bytes(b)
    if not a.skip_build:
        shutil.copyfile(ROOT/'Makefile',build/'Makefile')
        for h in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h'):
            src=ROOT/'assets/hd/shared-menu-runs-v1'/h;dst=build/src.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    harness=a.out/'harness.c';harness.write_text(HARNESS)
    if a.prepare_only:print('Prepared immutable source snapshot and native lifecycle harness; not compiled or run.');return
    env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu'),'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1','SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy'}
    def run(cmd,log,**kw):
        r=subprocess.run(cmd,env=env,capture_output=True,timeout=240,preexec_fn=bounded,**kw);(a.out/log).write_bytes(r.stdout+r.stderr)
        if r.returncode:print((r.stdout+r.stderr).decode(errors='replace')[-12000:]);raise SystemExit(r.returncode)
        return r
    if not a.skip_build:run(['make','-j3','VCS_IDREV=printf projectile91-lifecycle','CPPFLAGS=-MMD -DNDEBUG -DNEWSHF_HD_COMPOSITOR=1 -I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),'LDFLAGS=-Wl,-rpath,'+str(a.sysroot/'usr/lib/x86_64-linux-gnu')],'build.log',cwd=build)
    cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
    flags=['-std=c99','-O1','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(build/'src')]
    san=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie'] if a.sanitize else []
    run(['cc',*flags,'-Dmain=unused_game_main','-c',str(build/'src/opentyr.c'),'-o',str(build/'main-test.o')],'main-compile.log')
    objects=[str(x) for x in sorted((build/'obj').glob('*.o')) if x.stem not in ('render_mirror','opentyr','sprite','entity_draw')]
    for name in ('sprite','entity_draw'):
        obj=build/(name+'-test.o');run(['cc',*flags,*san,'-c',str(build/'src'/f'{name}.c'),'-o',str(obj)],name+'-compile.log');objects.append(str(obj))
    exe=a.out/'lifecycle-test';run(['cc',*flags,*san,str(harness),str(build/'main-test.o'),*objects,*libs,'-lm','-o',str(exe)],'harness-compile.log')
    raw=(a.data/'tyrian.shp').read_bytes();offs=struct.unpack_from('<13I',raw,2);bank=raw[offs[7]:offs[8]];assert SHA(bank)=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
    pal=(a.data/'palette.dat').read_bytes()[:768];rgb=bytes((v<<2)|(v>>4)for v in pal);payload=bank+b''.join(struct.pack('<I',int.from_bytes(rgb[i:i+3],'big'))for i in range(0,768,3));talon=raw[offs[8]:offs[9]];payload+=struct.pack('<I',len(talon))+talon
    assets=a.out/'assets';assets.mkdir(exist_ok=True)
    for name,target in [('enemy-projectile91-91-8.hda',ROOT/'assets/hd/current-compat/projectile91/enemy-projectile91-91-8.hda'),('content',ROOT/'assets/hd/global-assets-v1/content')]:
        link=assets/name
        if not link.exists():link.symlink_to(target,target_is_directory=target.is_dir())
    missing=a.out/'missing91';missing.mkdir(exist_ok=True)
    link=missing/'content'
    if not link.exists():link.symlink_to(ROOT/'assets/hd/global-assets-v1/content',target_is_directory=True)
    r=run([str(exe),str(assets),str(missing)],'harness.log',input=payload)
    unchanged=all((ROOT/'src'/n).read_bytes()==b for n,b in source.items());assert Path(__file__).read_bytes()==test_bytes,'test changed during run';assert unchanged,'production changed during snapshot test; rerun against freeze'
    report={'status':'PASS','scope':'Native full production renderer TU and linked sprite/wrapper; legacy active=false ordinary-frame lifecycle, not game-loop/full-game acceptance','sanitizers':'ASan+UBSan renderer,sprite,entity_draw,harness; remaining objects optimized' if a.sanitize else 'none','source_sha256':{n:SHA(b)for n,b in source.items()},'source_unchanged':unchanged,'test_sha256':SHA(test_bytes),'harness_sha256':SHA(harness.read_bytes()),'stdout':r.stdout.decode(),'legacy_activation_and304_scope_pins':PINS,'eleven_prior_owner_clear_only_pins':OLD_OWNER_PINS,'original_bytes_persisted':False,'leak_sanitizer':False}
    (a.out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.decode())
if __name__=='__main__':main()
