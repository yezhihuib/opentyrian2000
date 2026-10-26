#!/usr/bin/env python3
"""Finite cyan runtime include + original indexed row blitter. Typed layer1 donor
is a diagnostic stub; recursive real layer1/aircraft evidence is a separate actual
scene diagnostic. --out must be a new directory so failure receipts survive."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, struct, subprocess
ROOT=Path(__file__).resolve().parents[1]
def module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
PREFIX=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include "SDL.h"
#define REAR_OPEN(p) open(p,O_RDONLY|O_NONBLOCK)
#define REAR_READ read
#define REAR_CLOSE close
#define REAR_FSTAT fstat
#define REAR_STAT struct stat
#define REAR_REGULAR(m) S_ISREG(m)
#define ASSET_SHAPESY_CYAN 203
#define CYAN_CHECK(c) do { checks++;assert(c); }while(0)
enum {MIRROR_NORMAL,MIRROR_BLEND};
static unsigned checks,cases,draws;
typedef Uint8 JE_byte;
typedef struct {bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y,density;Uint8 *rgba;} Asset;
static struct {Uint8 *mainmap[600][14];struct {Uint8 nothing[3],fill,sh[672];} shapes[71];} megaData2;
static Uint8 originals[4][672],expected[64000],pixels[64000];
static SDL_PixelFormat format={.format=SDL_PIXELFORMAT_INDEX8,.BitsPerPixel=8,.BytesPerPixel=1};
static SDL_PixelFormat rgba_format={.format=SDL_PIXELFORMAT_ARGB8888,.BitsPerPixel=32,.BytesPerPixel=4};
static Uint32 canvas_pixels[2560*1600];
static SDL_Surface surface={.format=&format,.w=320,.h=200,.pitch=320,.pixels=pixels,.clip_rect={0,0,320,200}};
static SDL_Surface canvas_surface={.format=&rgba_format,.w=2560,.h=1600,.pitch=2560*4,.pixels=canvas_pixels};
static SDL_Surface *canvas=&canvas_surface,*game_screen=&surface,*VGAScreen=&surface;
static Uint8 hd_owner[2560*1600],cloud_owner[2560*1600],selected[64000];
static Uint16 green_first[2560*1600];
static Uint32 rgb_palette[256];
static char terrain_file='Y';
static bool asteroid_hd_enabled,active=true,game_probe_missing,game_probe_invalid,game_probe_original_reference,filterFade,smoothies[9];
static int game_probe_density=8,levelFilter=-99,levelBrightness=-99,background2=1;
static unsigned game_probe_scene_assets=2;
static const char *game_probe_assets,*reject_reason;
static uint64_t mirror_logic_tick=1;static unsigned game_probe_tick;
static Uint8 **mapY2Pos;static intptr_t mapX2bpPos;static int mapX2Pos,backPos2;
static void cyan_frame_reset(void);
static void render_mirror_unsupported(const char *reason){reject_reason=reason;cyan_frame_reset();}
static void render_mirror_shadow_end(void){}
static void font_before_effect(SDL_Rect r){(void)r;}
static void asset_debug_terrain_row(int x,int y,Uint8 **map){(void)x;(void)y;(void)map;}
static void render_mirror_shapesy_row_end(void){}
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored)
{(void)id;(void)x;(void)y;(void)mirrored;assert(role==203&&!part&&style==MIRROR_NORMAL);}
/* Deliberately finite diagnostic donor. Production donor tested separately. */
static bool donor_live=true;static uint64_t donor_serial=55;static Uint32 donor_value=0xff123456;
static uint64_t shapesy_borrow_ready(void){return donor_live?donor_serial:0;}
static bool shapesy_borrow_sample(uint64_t serial,size_t n,Uint32 c){(void)n;return donor_live&&serial==donor_serial&&c==donor_value;}
static bool shapesy_borrow_check(uint64_t serial){return donor_live&&serial==donor_serial;}
static bool allocation_fail;
static void *cyan_test_calloc(size_t n,size_t z){return allocation_fail?NULL:calloc(n,z);}
'''
CHECKS=r'''
static void registry(void)
{
 cyan_map_reset();reject_reason=NULL;terrain_file='Y';donor_live=true;donor_serial=55;
 for(unsigned i=0;i<71;i++){
  unsigned k=i%4;memcpy(megaData2.shapes[i].sh,originals[k],672);
  cyan_bind(2,cyan_ids[k],megaData2.shapes[i].sh);
 }
 for(unsigned y=0;y<600;y++)for(unsigned x=0;x<14;x++)megaData2.mainmap[y][x]=megaData2.shapes[x%4].sh;
 CYAN_CHECK(cyan_sources_valid());for(unsigned k=0;k<4;k++)CYAN_CHECK(cyan_registry.seen[k]);
}
static void frame(void)
{
 cyan_frame_reset();reject_reason=NULL;mirror_logic_tick++;
 memset(pixels,7,sizeof(pixels));memset(expected,7,sizeof(expected));
 memset(hd_owner,0,sizeof(hd_owner));memset(cloud_owner,0,sizeof(cloud_owner));memset(selected,0,sizeof(selected));
 for(unsigned n=0;n<2560*1600;n++)canvas_pixels[n]=palette_rgb(7);
 mapX2Pos=0;backPos2=27;mapX2bpPos=1;mapY2Pos=&megaData2.mainmap[280][0]+11;
}
static void begin(void){render_mirror_cyan_layer2(&surface,&megaData2.mainmap[280][0],0,-1);}
static void complete(void)
{
 begin();CYAN_CHECK(cyan_pass.live);
 for(unsigned r=0;r<8;r++)blit_background_row(&surface,0,(int)r*28-1,&megaData2.mainmap[280+r][0]);
 render_mirror_cyan_end();CYAN_CHECK(!reject_reason&&cyan_frame.live&&cyan_borrow.sealed&&cyan_frame_check());
}
static void positive(void)
{
 cases++;registry();frame();Uint8 before[64000];memcpy(before,pixels,sizeof(before));complete();
 for(unsigned y=0;y<200;y++)for(unsigned x=0;x<320;x++){
  unsigned r=(y+1)/28,t=x/24,i=((y+1)%28)*24+x%24;
  Uint8 source=x<288?originals[t%4][i]:0;
  CYAN_CHECK(pixels[y*320+x]==(source?source:before[y*320+x]));
  for(unsigned py=0;py<8;py++)for(unsigned px=0;px<8;px++){
   size_t n=(size_t)(y*8+py)*2560+x*8+px;
   if(!source){CYAN_CHECK(canvas_pixels[n]==palette_rgb(7)&&!hd_owner[n]&&!cyan_borrow.values[n]);}
   else{
    const Uint8 *a=cyan_resources.members[t%4].rgba+4*(((y+1)%28*8+py)*192+x%24*8+px);
    CYAN_CHECK(canvas_pixels[n]==blend_rgba(palette_rgb(7),a,a[3])&&hd_owner[n]==1&&cyan_borrow_sample(cyan_borrow.serial,n,canvas_pixels[n]));
   }
  }
  (void)r;
 }
 /* Postpass scrolling is legal; snapshots bind actual used map, not globals. */
 backPos2=0;mapY2Pos-=14;CYAN_CHECK(cyan_frame_check());
}
static unsigned visible_nonzero(unsigned k){for(unsigned i=24;i<672;i++)if(originals[k][i])return i;assert(0);return 0;}
static void guarded(void)
{
 for(unsigned mode=0;mode<11;mode++){
  cases++;registry();frame();
  if(mode==0)game_probe_density=4;if(mode==1)rgb_palette[4]^=1;if(mode==2)filterFade=true;
  if(mode==3)levelFilter=1;if(mode==4)levelBrightness=1;if(mode==5)smoothies[1]=true;
  if(mode==6)terrain_file='Z';if(mode==7)surface.pitch=321;if(mode==8)mock_geometry_available=false;
  if(mode==9){free(cyan_borrow.values);cyan_borrow.values=NULL;cyan_borrow.capacity=0;allocation_fail=true;}
  if(mode==10)canvas_surface.w=2559;
  begin();CYAN_CHECK(!cyan_pass.live);
  game_probe_density=8;if(mode==1)rgb_palette[4]^=1;filterFade=false;levelFilter=levelBrightness=-99;smoothies[1]=false;
  terrain_file='Y';surface.pitch=320;mock_geometry_available=true;allocation_fail=false;canvas_surface.w=2560;
 }
 cases++;registry();frame();begin();CYAN_CHECK(cyan_pass.live);begin();CYAN_CHECK(!cyan_pass.live&&!cyan_borrow.sealed);
 cases++;registry();frame();begin();blit_background_row(&surface,0,-1,&megaData2.mainmap[280][0]);begin();CYAN_CHECK(reject_reason&&!cyan_borrow.sealed);
 for(unsigned mode=0;mode<8;mode++){
  cases++;registry();frame();begin();CYAN_CHECK(cyan_pass.live);
  Uint8 clone[672];memcpy(clone,originals[0],672);
  if(mode==0)megaData2.mainmap[280][0]=clone;
  if(mode==1)megaData2.mainmap[280][0]++;
  if(mode==2)megaData2.shapes[70].sh[671]^=1;
  if(mode==3)cyan_registry.ids[0]=112;
  if(mode==4)cyan_registry.valid=false;
  if(mode==5)cyan_pass.generation++;
  if(mode==6)cyan_resources.members[0].rgba[0]^=1;
  if(mode==7)megaData2.mainmap[287][11]=NULL;
  unsigned bits=cyan_row(&surface,0,-1,&megaData2.mainmap[280][0],MIRROR_NORMAL);
  if(mode==5||mode==6||mode==7){render_mirror_cyan_end();CYAN_CHECK(!cyan_borrow.sealed);}else CYAN_CHECK(!bits);
 }
 cases++;registry();Uint8 clone[672];memcpy(clone,originals[0],672);CYAN_CHECK(cyan_source_slot(clone)<0&&cyan_source_slot(megaData2.shapes[0].sh+1)<0&&cyan_source_slot(megaData2.shapes[0].nothing)<0);
 cyan_bind(2,111,clone);CYAN_CHECK(!cyan_sources_valid());
 cases++;registry();cyan_map_reset();cyan_bind(1,111,megaData2.shapes[0].sh);CYAN_CHECK(!cyan_id(megaData2.shapes[0].sh));
}
static void alpha_and_underlays(void)
{
 for(unsigned mode=0;mode<5;mode++){
  cases++;registry();frame();begin();CYAN_CHECK(cyan_pass.live);
  unsigned i=visible_nonzero(0);int x=i%24,y=i/24-1;size_t n=(size_t)y*8*2560+x*8;
  Uint8 *a=cyan_resources.members[0].rgba+4*(i/24*8*192+i%24*8);Uint8 save[4];memcpy(save,a,4);
  /* Direct low-level diagnostic bypasses pinned resource check solely to test
   * mathematical alpha endpoints; never presented as authored art admission. */
  const unsigned alphas[5]={0,1,254,255,0};a[0]=60;a[1]=90;a[2]=120;a[3]=alphas[mode];
  if(mode==4){a[0]=a[1]=a[2]=0;canvas_pixels[n]=donor_value;hd_owner[n]=1;}
  bool borrowed=false;CYAN_CHECK(cyan_tile_preflight(0,0,-1,donor_serial,&borrowed));
  Uint32 bg=canvas_pixels[n];CYAN_CHECK(cyan_tile_draw(0,0,-1));
  CYAN_CHECK(canvas_pixels[n]==blend_rgba(bg,a,a[3])&&cyan_borrow.values[n]==canvas_pixels[n]);
  if(mode==4)CYAN_CHECK(cyan_layer1_dependency==donor_serial);
  memcpy(a,save,4);cyan_pass.live=false;cyan_row_lease.live=false;
 }
 /* One unsafe last sample prevents an earlier HD prefix. */
 cases++;registry();frame();begin();unsigned i=visible_nonzero(0);size_t n=(size_t)(i/24-1)*8*2560+i%24*8;
 hd_owner[n]=1;canvas_pixels[n]=0xffabcdef;uint64_t before=asteroid1_stamp((const Uint8 *)canvas_pixels,sizeof(canvas_pixels));
 CYAN_CHECK(!cyan_tile_draw(0,0,-1));CYAN_CHECK(asteroid1_stamp((const Uint8 *)canvas_pixels,sizeof(canvas_pixels))==before);
 for(size_t q=0;q<cyan_borrow.capacity;q++)CYAN_CHECK(!cyan_borrow.values[q]);
 cases++;registry();frame();begin();hd_owner[n]=1;canvas_pixels[n]=donor_value;
 CYAN_CHECK(cyan_tile_draw(0,0,-1)&&cyan_layer1_dependency==55);donor_live=false;CYAN_CHECK(!shapesy_borrow_check(cyan_layer1_dependency));
 cyan_pass.live=false;
}
static void final_guards(void)
{
 for(unsigned mode=0;mode<25;mode++){
  cases++;registry();frame();complete();uint64_t serial=cyan_borrow.serial;CYAN_CHECK(cyan_borrow_check(serial));
  if(mode==0)cyan_resources.members[0].rgba[1]^=1;if(mode==1)megaData2.shapes[70].sh[0]^=1;
  if(mode==2)megaData2.mainmap[287][11]=NULL;if(mode==3)cyan_borrow.serial++;
  if(mode==4)cyan_resources.generation++;if(mode==5)mirror_logic_tick++;
  if(mode==6)canvas_surface.pitch+=4;if(mode==7)surface.pitch++;
  if(mode==8)canvas_surface.pixels=(Uint8 *)canvas_pixels+4;if(mode==9)surface.pixels=pixels+1;
  if(mode==10)cyan_resources.root[0]^=1;if(mode==11)mock_geometry.dst.w++;
  if(mode==12)rgb_palette[7]^=1;if(mode==13)filterFade=true;
  if(mode==14){cyan_layer1_dependency=55;donor_live=false;}
  if(mode==15)cyan_borrow.failed=true;
  if(mode==16)surface.w=319;if(mode==17)surface.h=199;if(mode==18)format.format=SDL_PIXELFORMAT_RGB332;
  if(mode==19)format.BitsPerPixel=7;if(mode==20)format.BytesPerPixel=2;if(mode==21)surface.clip_rect.x=1;
  if(mode==22)rgba_format.BitsPerPixel=24;if(mode==23)rgba_format.BytesPerPixel=3;if(mode==24)canvas_surface.pixels=(Uint8 *)canvas_pixels+1;
  fprintf(stderr,"final-mutant=%u\n",mode);
  CYAN_CHECK(!cyan_borrow_check(serial)&&!cyan_frame_check());
  surface.w=320;surface.h=200;format.format=SDL_PIXELFORMAT_INDEX8;format.BitsPerPixel=8;format.BytesPerPixel=1;surface.clip_rect.x=0;rgba_format.BitsPerPixel=32;rgba_format.BytesPerPixel=4;
  canvas_surface.pitch=2560*4;surface.pitch=320;canvas_surface.pixels=canvas_pixels;surface.pixels=pixels;
  if(mode==11)mock_geometry.dst.w--;if(mode==12)rgb_palette[7]^=1;filterFade=false;
 }
 cases++;registry();frame();begin();unsigned bits=cyan_row(&surface,0,-1,&megaData2.mainmap[280][0],MIRROR_NORMAL);CYAN_CHECK(bits);
 render_mirror_cyan_row_end();CYAN_CHECK(reject_reason&&!cyan_borrow.sealed);
}

static void callbacks(void)
{
 for(unsigned mode=0;mode<5;mode++){
  cases++;registry();frame();begin();unsigned bits=cyan_row(&surface,0,-1,&megaData2.mainmap[280][0],MIRROR_NORMAL);CYAN_CHECK(bits);
  unsigned i=visible_nonzero(0),x=i%24,y=i/24-1;Uint8 v=originals[0][i];Uint8 *p=pixels+y*320+x;bool qualified=false;
  *p=v;
  if(mode==0){cyan_native_pixel(&surface,p,v^1,MIRROR_NORMAL,true,&qualified);CYAN_CHECK(!qualified&&reject_reason);}
  if(mode==1){cyan_native_pixel(&surface,p,v,MIRROR_NORMAL,true,&qualified);CYAN_CHECK(qualified);qualified=false;cyan_native_pixel(&surface,p,v,MIRROR_NORMAL,true,&qualified);CYAN_CHECK(!qualified&&reject_reason);}
  if(mode==2){megaData2.shapes[0].sh[i]^=1;cyan_native_pixel(&surface,p,v,MIRROR_NORMAL,true,&qualified);CYAN_CHECK(!qualified&&reject_reason);}
  if(mode==3){rgb_palette[5]^=1;cyan_native_pixel(&surface,p,v,MIRROR_NORMAL,true,&qualified);CYAN_CHECK(!qualified&&reject_reason);rgb_palette[5]^=1;}
  if(mode==4){render_mirror_cyan_row_end();cyan_native_pixel(&surface,p,v,MIRROR_NORMAL,true,&qualified);CYAN_CHECK(!qualified&&reject_reason);}
 }
}

int main(int argc,char **argv)
{
 assert(argc==4);game_probe_assets=argv[2];FILE *f=fopen(argv[1],"rb");assert(f);
 assert(fread(originals,672,4,f)==4);for(unsigned i=0;i<256;i++){Uint8 p[3];assert(fread(p,1,3,f)==3);rgb_palette[i]=p[0]<<16|p[1]<<8|p[2];}assert(fgetc(f)==EOF);fclose(f);
 registry();frame();
 if(!strcmp(argv[3],"reject")){begin();CYAN_CHECK(!cyan_pass.live);}
 else{positive();guarded();alpha_and_underlays();final_guards();callbacks();}
 cyan_shutdown();printf("cyan runtime PASS cases=%u checks=%u\n",cases,checks);return 0;
}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--pack',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--sdl-include',action='append',default=[]);p.add_argument('--sanitize',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 ext=module(ROOT/'tests/test_asteroid1_ten_assets.py','extract').extract;r=(ROOT/'src/render_mirror.c').read_text();b=(ROOT/'src/backgrnd.c').read_text();inc=(ROOT/'src/shapesy_cyan_layer2_mirror.inc').read_text()
 raw=(a.data/'shapesy.dat').read_bytes();assert hashlib.sha256(raw).hexdigest()=='1faf60f8804c4ca52ea41ece94e3d2fd3cdaecb437b63ecb61adc58907c7b869';tiles={};pos=0
 for i in range(1,601):
  blank=raw[pos];pos+=1;tiles[i]=bytes(672) if blank else raw[pos:pos+672];pos+=0 if blank else 672
 pal=(a.data/'palette.dat').read_bytes()[5*768:6*768];pal=bytes((v<<2)|(v>>4) for v in pal)
 data=a.out/'sources.bin';data.write_bytes(b''.join(tiles[i] for i in (111,112,121,122))+pal)
 geometry=re.search(r'typedef struct VideoOutputGeometry \{.*?\} VideoOutputGeometry;', (ROOT/'src/video.h').read_text(),re.S).group(0)
 code=PREFIX+'typedef int ScalingMode;\n'+geometry+r'''
static VideoOutputGeometry mock_geometry={(SDL_Window *)1,(SDL_Renderer *)2,1,{0,0,1280,800},1280,800,1280,800,4,2,0};
static bool mock_geometry_available=true;
static bool video_output_geometry(VideoOutputGeometry *o){if(!mock_geometry_available)return false;*o=mock_geometry;return true;}
'''+ext((ROOT/'src/video.c').read_text(),'video_output_geometry_equal')+ext(r,'palette_rgb')+ext(r,'blend_rgba')+ext((ROOT/'src/asteroid1_ten_mirror.inc').read_text(),'asteroid1_stamp')+'\n#define calloc cyan_test_calloc\n'+inc+'\n#undef calloc\n'
 code+=r'''
static unsigned render_mirror_terrain_row(SDL_Surface *s,int x,int y,Uint8 **m,int style){return cyan_row(s,x,y,m,style);}
static void render_mirror_terrain_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,int style,bool replaced){
 bool qualified=false;cyan_native_pixel(s,p,v,style,replaced,&qualified);
 size_t n=(size_t)(p-pixels);expected[n]=*p;
 if(!qualified)for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++){
  size_t at=(n/320*8+y)*2560+n%320*8+x;canvas_pixels[at]=palette_rgb(v);hd_owner[at]=cloud_owner[at]=0;
 }
}
'''+ext(b,'blit_background_row')+CHECKS
 harness=a.out/'harness.c';harness.write_text(code)
 flags=['cc','-std=c99','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-misleading-indentation','-I'+str(ROOT/'src')]+['-I'+x for x in a.sdl_include]
 if a.sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
 exe=a.out/'runtime';res=subprocess.run(flags+[str(harness),'-o',str(exe)],capture_output=True,text=True);(a.out/'compile.log').write_text(res.stdout+res.stderr)
 receipt=dict(source_sha256=hashlib.sha256(inc.encode()).hexdigest(),harness_sha256=hashlib.sha256(code.encode()).hexdigest(),sanitized=a.sanitize,asan_options=os.environ.get("ASAN_OPTIONS",""),donor="controlled stub; real recursive donor tested separately",pack_sha256={v.name:hashlib.sha256(v.read_bytes()).hexdigest() for v in sorted(a.pack.glob("terrain-shapesy-cyan-*-8.hda"))},passed=False)
 (a.out/'receipt.json').write_text(json.dumps(receipt,indent=2));assert res.returncode==0,res.stderr
 res=subprocess.run([str(exe),str(data),str(a.pack),'accept'],capture_output=True,text=True);(a.out/'positive.log').write_text(res.stdout+res.stderr);assert res.returncode==0,res.stderr
 receipt['positive']=res.stdout.strip();count=0
 for i in (111,112,121,122):
  for kind in ('missing','payload','magic','density','role','width','height','anchor','short','trailing'):
   out=a.out/'negative'/f'{i}-{kind}';out.mkdir(parents=True)
   for other in (111,112,121,122):
    dest=out/f'terrain-shapesy-cyan-{other}-8.hda';source=a.pack/dest.name
    if other!=i:dest.symlink_to(source.resolve());continue
    blob=bytearray(source.read_bytes())
    if kind=='missing':continue
    if kind=='payload':blob[40]^=1
    elif kind=='magic':blob[:4]=b'NOPE'
    elif kind=='short':blob=blob[:-1]
    elif kind=='trailing':blob+=b'x'
    else:struct.pack_into('<I',blob,dict(role=4,density=8,width=12,height=16,anchor=20)[kind],1)
    dest.write_bytes(blob)
   res=subprocess.run([str(exe),str(data),str(out),'reject'],capture_output=True,text=True);(out/'result.log').write_text(res.stdout+res.stderr);assert res.returncode==0,(i,kind,res.stderr);count+=1
 receipt.update(passed=True,atomic_rejections=count);(a.out/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
if __name__=='__main__':main()
