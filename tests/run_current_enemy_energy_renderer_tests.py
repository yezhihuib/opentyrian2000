#!/usr/bin/env python3
"""Current-source enemy-energy loader/role proof. Draw is a strict spy; native matrix proves compositor."""
import argparse, hashlib, json, os, re, struct, subprocess
from pathlib import Path
SHA=lambda b:hashlib.sha256(b).hexdigest()
def extract(s,name):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',s,re.M);assert m,name
 end=s.index('{',m.start())+1;depth=1
 while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[m.start():end]+'\n'
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=a.root.resolve();d=a.out.resolve();d.mkdir(parents=True,exist_ok=False)
s=(r/'src/render_mirror.c').read_text();entity=(r/'src/entity_draw.c').read_text();manifest=json.loads((r/'packaging/runtime-assets-v1.json').read_text());rows={x['destination']:x for x in manifest['files']};raw={i:(r/rows[f'assets/gameplay/enemy-energy-{i}-8.hda']['source_path']).read_bytes() for i in (77,58,182,163,1,183,164)}
for i,b in raw.items():assert b[:4]==b'HDR1' and struct.unpack('<6I',b[4:28])==(1110000+i,8,12,14,0,0) and len(b)==43036
variants={}
for i in raw:
 b=raw[i];changes={'missing':None,'magic':b'BAD!'+b[4:],'header':b[:27],'short':b[:-1],'extra':b+b'X','rgb':b[:28]+bytes([b[28]^1])+b[29:],'alpha':b[:31]+bytes([b[31]^1])+b[32:]}
 for n,off,val in [('role',4,80000+i),('identity',4,1110000+999),('density',8,4),('width',12,11),('height',16,13),('anchor-x',20,1),('anchor-y',24,1)]:
  q=bytearray(b);struct.pack_into('<I',q,off,val);changes[n]=bytes(q)
 for n,v in changes.items():variants[f'{n}-{i}']={j:v if j==i else raw[j] for j in raw}
variants['full']=raw;variants['missing-all']={i:None for i in raw}
for name,values in variants.items():
 dst=d/name;dst.mkdir()
 for i,b in values.items():
  if b is not None:(dst/f'enemy-energy-{i}-8.hda').write_bytes(b)
for i,b in raw.items():(d/f'golden-{i}.rgba').write_bytes(b[28:])
header=r/'src/current_enemy_energy_payload_pins.h'
if header.exists():(d/header.name).write_bytes(header.read_bytes())
types=re.search(r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',s,re.S).group()+'\n'+re.search(r'enum \{ ASSET_NEWSH2=.*?\};',s).group()+'\n'+re.search(r'static Asset assets\[\d+\];',s).group()
funcs=['read_asset','enemy_energy_slot','enemy_energy_family_ready','render_mirror_enemy_shot','blend_rgba']
(d/'extracted.inc').write_text('\n'.join(extract(s,n) for n in funcs)+'\n'+extract(entity,'draw_enemy_shot_sprite2'))
(d/'types.inc').write_text(types)
c=r'''#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;typedef uint32_t Uint32;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;SDL_PixelFormat *format;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef struct {int x,y,w,h;} SDL_Rect;
enum {MIRROR_NORMAL,ENTITY_NORMAL};
#include "types.inc"
HEADER
static bool enemy_energy_checked,enemy_energy_valid,game_probe_missing,game_probe_invalid,game_probe_original_reference,asteroid_hd_enabled,xmas,active=true;
static int game_probe_density=8;static const char *game_probe_assets,*reject_reason;
static SDL_PixelFormat format={8,1};static SDL_Surface screen={320,200,320,&format},*game_screen=&screen,*VGAScreen=&screen;
static Uint8 token,other;static Sprite2_array spriteSheet8={&token,1};
static struct {Uint8*rgba;char path[1024];} vulcan_shadow_resource[20],vulcan_shadow_coverage_resource[20];
static int vulcan_shadow_member(unsigned i){(void)i;return -1;}
static unsigned draws,originals,ends,scenes,shadow_ends,tests;static int ex,ey;static unsigned ei;static Uint8 golden[7][43008];
static void render_mirror_shadow_end(void){shadow_ends++;}
static bool projectile304_draw(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){(void)s;(void)x;(void)y;(void)b;(void)i;assert(0);return false;}
static bool enemy_orb112113_draw(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){(void)s;(void)x;(void)y;(void)b;(void)i;assert(0);return false;}
static bool enemy_tank_shell_family_ready(void){assert(0);return false;}
static const unsigned ids[7]={77,58,182,163,1,183,164};
static int slot(unsigned id){for(int i=0;i<7;i++)if(id==ids[i])return i;return -1;}
static bool draw_asset(int x,int y,Asset*a,int style,const SDL_Rect*p){assert(x==ex&&y==ey&&a==assets+462+slot(ei)&&style==MIRROR_NORMAL&&!p);assert(a->valid&&a->bank==111&&a->index==(int)ei&&a->density==8&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y);assert(!memcmp(a->rgba,golden[slot(ei)],43008));draws++;return true;}
static void game_probe_scene_draw(int role,unsigned i,int x,int y,int part,int style,bool mirrored){assert(role==111&&i==ei&&x==ex&&y==ey&&!part&&style==ENTITY_NORMAL);(void)mirrored;scenes++;}
static void blit_sprite2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){assert(s==&screen&&x==ex&&y==ey&&b.data==spriteSheet8.data&&i==ei);originals++;}
static void render_mirror_entity_end(void){ends++;}
#include "extracted.inc"
static void clear(void){for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(assets+i,0,sizeof(*assets));}enemy_energy_checked=enemy_energy_valid=false;}
static void pair(bool accepted){for(unsigned z=0;z<7;z++){ei=ids[z];unsigned a=draws,b=originals,c=ends,e=scenes;ex=94;ey=73;draw_enemy_shot_sprite2(&screen,ex,ey,spriteSheet8,ei);assert(draws==a+accepted&&originals==b+1&&ends==c+1&&scenes==e+1);tests++;}}
static void declined(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned id){unsigned n=draws;assert(!render_mirror_enemy_shot(s,x,y,b,id)&&draws==n);tests++;}
static void guards(void){clear();for(int j=0;j<7;j++){unsigned id=ids[j];SDL_Surface alt=screen;Sprite2_array wrong={&other,1},null={0};declined(NULL,94,73,spriteSheet8,id);declined(&alt,94,73,spriteSheet8,id);declined(&screen,94,73,wrong,id);declined(&screen,94,73,null,id);active=false;declined(&screen,94,73,spriteSheet8,id);active=true;reject_reason="x";declined(&screen,94,73,spriteSheet8,id);reject_reason=NULL;for(int k=0;k<4;k++){int x=k<2?(k==0?-1:309):94,y=k>=2?(k==2?-14:200):73;declined(&screen,x,y,spriteSheet8,id);}screen.w=319;declined(&screen,94,73,spriteSheet8,id);screen.w=320;screen.h=199;declined(&screen,94,73,spriteSheet8,id);screen.h=200;screen.pitch=319;declined(&screen,94,73,spriteSheet8,id);screen.pitch=320;screen.format=NULL;declined(&screen,94,73,spriteSheet8,id);screen.format=&format;format.BitsPerPixel=32;declined(&screen,94,73,spriteSheet8,id);format.BitsPerPixel=8;format.BytesPerPixel=4;declined(&screen,94,73,spriteSheet8,id);format.BytesPerPixel=1;}
assert(!enemy_energy_checked);for(int n=1;n<=4;n+=3){game_probe_density=n;pair(false);assert(!enemy_energy_checked);}game_probe_density=8;
bool *flags[]={&game_probe_missing,&game_probe_invalid,&game_probe_original_reference};for(unsigned i=0;i<3;i++){*flags[i]=true;pair(false);assert(!enemy_energy_checked);*flags[i]=false;}const char *save=game_probe_assets;game_probe_assets=NULL;pair(false);assert(!enemy_energy_checked);game_probe_assets=save;
for(unsigned z=0;z<7;z++)for(int x=0;x<=308;x+=308)for(int y=-13;y<=199;y+=212){ei=ids[z];ex=x;ey=y;assert(render_mirror_enemy_shot(&screen,x,y,spriteSheet8,ei));tests++;}clear();}
int main(int argc,char **argv){assert(argc==3);bool want_xmas=!strcmp(argv[2],"xmas");xmas=false;char full[2048],path[2048];snprintf(full,sizeof(full),"%s/full",argv[1]);for(int j=0;j<7;j++){snprintf(path,sizeof(path),"%s/golden-%u.rgba",argv[1],ids[j]);FILE*f=fopen(path,"rb");assert(f&&fread(golden[j],1,43008,f)==43008&&fgetc(f)==EOF);fclose(f);}game_probe_assets=full;pair(true);xmas=true;pair(false);assert(enemy_energy_checked&&enemy_energy_valid);xmas=false;pair(true);clear();xmas=true;pair(false);assert(!enemy_energy_checked);xmas=false;pair(true);guards();
VARIANTS
for(unsigned k=0;k<sizeof(variants)/sizeof(*variants);k++){clear();snprintf(path,sizeof(path),"%s/%s",argv[1],variants[k]);game_probe_assets=path;pair(false);assert(enemy_energy_checked&&!enemy_energy_valid);game_probe_assets=full;pair(false);clear();pair(true);game_probe_assets=path;pair(true);}clear();game_probe_assets=full;pair(true);
uint64_t checks=0;for(unsigned j=0;j<7;j++)for(unsigned p=0;p<43008;p+=4)for(unsigned alpha=0;alpha<256;alpha++){Uint32 dst=0xff000000u|((p*2654435761u+j*971)&0xffffffu);Uint8 *src=golden[j]+p;Uint32 expected=0xff000000u;for(unsigned c=0;c<3;c++){unsigned sh=(2-c)*8,dc=(dst>>sh)&255;expected|=((dc*(255-alpha)+src[c]*alpha+127)/255)<<sh;}assert(blend_rgba(dst,src,(int)alpha)==expected);checks++;}if(want_xmas){xmas=true;pair(false);assert(enemy_energy_checked);clear();pair(false);assert(!enemy_energy_checked);}clear();printf("{\"status\":\"PASS\",\"tests\":%u,\"draws\":%u,\"originals\":%u,\"alpha_checks\":%llu}\n",tests,draws,originals,(unsigned long long)checks);return 0;}
'''
c=c.replace('HEADER','#include "current_enemy_energy_payload_pins.h"' if header.exists() else '').replace('VARIANTS','static const char *variants[]={'+','.join(json.dumps(n) for n in variants if n!='full')+'};')
(d/'driver.c').write_text(c)
cmd=['cc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(d),str(d/'driver.c'),'-o',str(d/'driver')];result=subprocess.run(cmd,capture_output=True,text=True);(d/'compile.log').write_text(result.stdout+result.stderr);result.check_returncode()
results={}
for mode in ('normal','xmas'):
 q=subprocess.run([str(d/'driver'),str(d),mode],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'));(d/(mode+'.log')).write_text(q.stdout+q.stderr);q.check_returncode();results[mode]=json.loads(q.stdout)
report={'status':'PASS','results':results,'variants':list(variants),'production_functions_sha256':{n:SHA(extract(s,n).encode()) for n in funcs},'wrapper_sha256':SHA(extract(entity,'draw_enemy_shot_sprite2').encode()),'hda_sha256':{i:SHA(b) for i,b in raw.items()},'limitations':['Extracted real loader/role hook/wrapper and blend primitive; draw compositor is a strict spy and verified independently by native matrix.','Tank/orb/global optional branches are excluded fail-if-entered stubs, not evidence of their own behavior.','Synthetic fixture exercises roles, not natural campaign gameplay.','LeakSanitizer unavailable under executor ptrace; ASan/UBSan active.']};(d/'summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
