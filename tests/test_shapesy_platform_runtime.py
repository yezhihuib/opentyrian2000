#!/usr/bin/env python3
"""Bounded shapesY runtime harness. Actual finite include, actual indexed blitter,
actual HD compositor and normal indexed-write compositor suffix. Font/entity hooks
are unrelated stubs. Synthetic art is explicitly diagnostic, never authored output.
Use --pack for final pinned art instead. Original game data stays outside checkout.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, struct, subprocess
ROOT=Path(__file__).resolve().parents[1]
IDS=(321,322,323,324,325,326,331,332,333,334,336,341,342,343,346,351,352,353,354,361,362,363,364,365,374,375,384,385)
def module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fnv(b):
 h=0xcbf29ce484222325
 for v in b:h=((h^v)*0x100000001b3)&((1<<64)-1)
 return h
EXTRA=r'''
static char terrain_file='Y';
static const Asset *shapesy_draw_lease,*projectile91_draw_lease;
static bool shapesy_clear_proof,filterActive=true,filterFade,smoothies[9];
static int levelFilter=-99,levelBrightness=-99;
static Uint8 expected[64000];static unsigned occlusions;
static struct {Uint8 *mainmap[300][14];struct {Uint8 sh[672];} shapes[72];} megaData1;
static unsigned short lookup[72];static Uint8 original_sources[72][672],map_indices[4200];
static Uint8 **mapYPos;static intptr_t mapXbpPos;static int mapXPos,backPos;
static void render_mirror_shapesy_end(void);
/* This standalone harness deliberately exercises only the original layer1.
 * New layer2 entry fails closed; inactive callbacks cannot claim cyan pixels.
 * The role202-only scene assertion below also rejects any cyan draw claim.
 * Active mixed paths are covered by the real cyan include and game tests. */
static void render_mirror_cyan_layer2(SDL_Surface *surface,const void *first,int x,int y)
{(void)surface;(void)first;(void)x;(void)y;assert(!"cyan layer2 outside layer1 harness");}
static void render_mirror_cyan_row_end(void){}
static bool cyan_native_pixel(SDL_Surface *s,Uint8 *address,Uint8 source,int style,bool replaced,bool *qualified)
{(void)s;(void)address;(void)source;(void)style;(void)replaced;*qualified=false;return false;}
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored)
{(void)id;(void)x;(void)y;(void)mirrored;assert(role==202&&!part&&style==MIRROR_NORMAL);}
static void asset_debug_terrain_row(int x,int y,Uint8 **map){(void)x;(void)y;(void)map;}
static void render_mirror_ground101_layer1(SDL_Surface *s,const void *p,int x,int y){(void)s;(void)p;(void)x;(void)y;}
static void render_mirror_asteroid_terrain_layer1(SDL_Surface *s,const void *p,int x,int y){(void)s;(void)p;(void)x;(void)y;}
static void render_mirror_asteroid_terrain_end(void){}
static Uint32 cloud_shadow_rgba(Uint32 c,Uint8 a,Uint8 b){(void)c;(void)a;(void)b;assert(0);return 0;}
static void render_mirror_pixel(SDL_Surface *,Uint8 *,Uint8,int);
int SDL_FillRect(SDL_Surface *s,const SDL_Rect *r,Uint32 c)
{assert(s==&surface&&!r&&!c);memset(pixels,0,64000);return 0;}
'''
CHECKS=r'''
static void registry(void)
{
 shapesy_map_reset();terrain_file='Y';
 for(unsigned i=0;i<72;i++){memcpy(megaData1.shapes[i].sh,original_sources[i],672);shapesy_bind(1,lookup[i],megaData1.shapes[i].sh);}
 for(unsigned y=0;y<300;y++)for(unsigned x=0;x<14;x++)megaData1.mainmap[y][x]=megaData1.shapes[map_indices[y*14+x]].sh;
 assert(shapesy_sources_valid());for(unsigned k=0;k<28;k++)assert(shapesy_registry.seen[k]);
}
static void clear(void)
{
 reject_reason=NULL;suppress=suppress_cloud=suppress_green_smoke=false;region_count=0;
 memset(selected,0,sizeof(selected));memset(green_first,0,sizeof(green_first));
 SDL_FillRect(&surface,NULL,0);render_mirror_rect(&surface,NULL);assert(shapesy_clear_proof);
}
static void frame(unsigned row,int scroll)
{
 shapesy_frame_reset();mapXPos=0;backPos=scroll;mapXbpPos=1;mapYPos=&megaData1.mainmap[row][0]+11;
 clear();render_mirror_shapesy_layer1(&surface,&megaData1.mainmap[row][0],0,scroll-28);
}
static void verify_row(unsigned row,int y)
{
 for(unsigned t=0;t<12;t++){
  Uint8 *s=megaData1.mainmap[row][t];int k=shapesy_member(shapesy_id(s));
  for(unsigned i=0;i<672;i++){
   int x=t*24+i%24,dy=y+i/24;if(dy<0||dy>=200)continue;
   unsigned v=s[i];assert(pixels[dy*320+x]==v);bool water=v>=48&&v<=63;
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    unsigned at=(dy*8+sy)*2560+x*8+sx;
    if(k<0||water){assert(canvas_pixels[at]==palette_rgb(v));assert(!hd_owner[at]);}
    else {
     const Uint8 *p=shapesy_resources.members[k].rgba+((i/24*8+sy)*192+(i%24*8+sx))*4;
     assert(canvas_pixels[at]==(0xff000000u|p[0]<<16|p[1]<<8|p[2]));assert(hd_owner[at]==1);
    }
   }
  }
 }
}
static void checks(void)
{
 assert(rgb_palette[0]==0&&palette_rgb(0)==0xff000000u); /* Actual RGB888 source palette, ARGB mirror. */
 /* Active flag alone is not an effect: production leaves it true forever
  * after opening fade. Both sentinels stay -99; toggles are no-op equivalents. */
 for(unsigned flag=0;flag<2;flag++){
  registry();filterActive=flag;frame(280,27);assert(shapesy_pass.live);
  blit_background_row(&surface,0,-1,&megaData1.mainmap[280][0]);filterActive=!flag;
  render_mirror_shapesy_end();assert(!reject_reason&&shapesy_frame_check());
 }
 filterActive=true;
 registry();frame(280,1);assert(filterActive&&shapesy_pass.live);
 /* Water must replace a deliberately wrong older scene and older HD owner. */
 for(unsigned n=0;n<2560*1600;n++){canvas_pixels[n]=0xffb522c1;hd_owner[n]=1;}
 /* No333 in this first top row; restore its zero when any source zero exists. */
 for(unsigned t=0;t<12;t++){Uint8 *s=megaData1.mainmap[280][t];for(unsigned i=0;i<672;i++)if(!s[i]){
  int y=-27+i/24;if(y>=0)for(int yy=0;yy<8;yy++)for(int xx=0;xx<8;xx++){int at=(y*8+yy)*2560+(t*24+i%24)*8+xx;canvas_pixels[at]=palette_rgb(0);hd_owner[at]=0;}}}
 blit_background_row(&surface,0,-27,&megaData1.mainmap[280][0]);verify_row(280,-27);assert(!shapesy_row_lease.live);
 /* All actual placements/IDs, clipping28 phases; compare original INDEX8. */
 unsigned seen[28]={0};
 for(unsigned row=0;row<=292;row+=4)for(int phase=0;phase<28;phase+=9){
  frame(row,phase);assert(shapesy_pass.live);
  for(unsigned r=0;r<8;r++){
   blit_background_row(&surface,0,(int)r*28+phase-28,&megaData1.mainmap[row+r][0]);verify_row(row+r,(int)r*28+phase-28);
   for(unsigned t=0;t<12;t++){int k=shapesy_member(shapesy_id(megaData1.mainmap[row+r][t]));if(k>=0)seen[k]++;}
  }render_mirror_shapesy_end();
 }
 for(unsigned k=0;k<28;k++)assert(seen[k]);
 for(int phase=0;phase<28;phase++){
  frame(284,phase);assert(shapesy_pass.live);
  for(unsigned r=0;r<8;r++){blit_background_row(&surface,0,(int)r*28+phase-28,&megaData1.mainmap[284+r][0]);verify_row(284+r,(int)r*28+phase-28);}
 }

 /* Same-pointer source and unused duplicate aliases cannot be trusted. */
 unsigned slot=0;while(lookup[slot]!=333)slot++;
 frame(280,1);megaData1.shapes[slot].sh[2]^=1;assert(!shapesy_sources_valid());
 assert(!shapesy_row(&surface,0,-27,&megaData1.mainmap[280][0],MIRROR_NORMAL));registry();
 Uint8 clone[672];memcpy(clone,megaData1.shapes[slot].sh,672);assert(!shapesy_id(clone)&&!shapesy_id(megaData1.shapes[slot].sh+1));
 shapesy_bind(1,333,clone);assert(!shapesy_sources_valid());registry();
 /* Repeated rows do not inherit leases. */
 frame(280,1);assert(shapesy_pass.live);blit_background_row(&surface,0,-27,&megaData1.mainmap[280][0]);
 assert(!shapesy_row(&surface,0,-27,&megaData1.mainmap[280][0],MIRROR_NORMAL)&&!shapesy_pass.live);
 for(unsigned n=0;n<4;n++){
  clear();if(n==0)game_probe_density=4;if(n==1)rgb_palette[5]^=1;if(n==2)smoothies[1]=true;if(n==3)filterFade=true;
  render_mirror_shapesy_layer1(&surface,&megaData1.mainmap[280][0],0,-27);assert(!shapesy_pass.live);
  game_probe_density=8;if(n==1)rgb_palette[5]^=1;smoothies[1]=false;filterFade=false;
 }
 /* Current cache bytes are revalidated even within the same logic tick. */
 frame(280,1);assert(shapesy_pass.live);shapesy_resources.members[0].rgba[0]^=1;
 frame(280,1);assert(!shapesy_pass.live);registry();
 /*333's sole0 has no indexed callback: prove black/current-clear ownership,
  * and reject a distinct previous RGBA underlay without changing the index. */
 registry();unsigned zslot=0;while(lookup[zslot]!=333)zslot++;
 megaData1.mainmap[280][0]=megaData1.shapes[zslot].sh;
 int zx=225%24,zy=225/24-1,za=zy*8*2560+zx*8;
 for(unsigned kind=0;kind<5;kind++){
  frame(280,27);assert(shapesy_pass.live);assert(!pixels[zy*320+zx]);
  if(kind==0)canvas_pixels[za]=0xffac1291;
  if(kind==1)hd_owner[za]=1;
  if(kind==2)cloud_owner[za]=1;
  if(kind==3)expected[zy*320+zx]=4;
  if(kind==4)pixels[zy*320+zx]=4;
  assert(!shapesy_row(&surface,0,-1,&megaData1.mainmap[280][0],MIRROR_NORMAL));assert(!shapesy_pass.live);
  assert(pixels[zy*320+zx]==(kind==4?4:0));
 }registry();
 /* A stale replaced bit after row_end cannot suppress ANY Y cell. */
 registry();frame(280,27);unsigned stale=shapesy_row(&surface,0,-1,&megaData1.mainmap[280][0],MIRROR_NORMAL);
 render_mirror_shapesy_row_end();pixels[0]=54;canvas_pixels[0]=0xffac1291;hd_owner[0]=1;
 render_mirror_terrain_pixel(&surface,pixels,54,MIRROR_NORMAL,true);assert(canvas_pixels[0]==palette_rgb(54)&&!hd_owner[0]);(void)stale;
 registry();
 /* Mutation between row draw and callback is checked against immutable source,
  * not merely against the now-mutated pointer. */
 megaData1.mainmap[280][0]=megaData1.shapes[zslot].sh;frame(280,27);
 unsigned bits=shapesy_row(&surface,0,-1,&megaData1.mainmap[280][0],MIRROR_NORMAL);assert(bits&1);
 Uint8 original=megaData1.shapes[zslot].sh[24];megaData1.shapes[zslot].sh[24]^=1;
 assert(!shapesy_native_water(&surface,pixels,megaData1.shapes[zslot].sh[24],MIRROR_NORMAL,true,NULL));
 assert(reject_reason&&!shapesy_pass.live);megaData1.shapes[zslot].sh[24]=original;registry();
 /* Palette/resource generation mutations between draw and callbacks fail
  * immediately. RGBA mutation is caught at pass end, before presentation. */
 for(unsigned kind=0;kind<3;kind++){
  registry();megaData1.mainmap[280][0]=megaData1.shapes[zslot].sh;frame(280,27);
  unsigned mask=shapesy_row(&surface,0,-1,&megaData1.mainmap[280][0],MIRROR_NORMAL);assert(mask&1);
  if(kind==0)rgb_palette[5]^=1;
  if(kind==1)shapesy_resources.generation++;
  if(kind==2)shapesy_resources.members[0].rgba[10]^=1;
  if(kind<2){assert(!shapesy_native_water(&surface,pixels,megaData1.shapes[zslot].sh[24],MIRROR_NORMAL,true,NULL));assert(reject_reason&&!shapesy_pass.live);}
  else {render_mirror_shapesy_end();assert(reject_reason&&!shapesy_pass.live);}
  if(kind==0)rgb_palette[5]^=1;
 }registry();
 /* An offscreen duplicate slot is checked even when its original ID is absent
  * from the current window. Layer2 rebinding never grants Layer1 identity. */
 shapesy_map_reset();for(unsigned i=0;i<72;i++){
  unsigned id=lookup[i];if(i==71){id=333;memcpy(megaData1.shapes[i].sh,original_sources[zslot],672);}
  shapesy_bind(1,id,megaData1.shapes[i].sh);
 }
 assert(shapesy_sources_valid());megaData1.shapes[71].sh[671]^=1;assert(!shapesy_sources_valid());registry();
 shapesy_map_reset();shapesy_bind(2,333,megaData1.shapes[zslot].sh);assert(!shapesy_id(megaData1.shapes[zslot].sh));registry();
 /* Full clear is mandatory; black zero never paints over an arbitrary underlay. */
 clear();shapesy_clear_proof=false;render_mirror_shapesy_layer1(&surface,&megaData1.mainmap[280][0],0,-27);assert(!shapesy_pass.live);
 frame(280,1);assert(shapesy_pass.live);render_mirror_unsupported("test");assert(!shapesy_pass.live&&!shapesy_row_lease.live);
 /* Postpass source/palette/brightness/filter/epoch drift is rejected by the
  * exact witness called at finish and Present, not by a live pass lease. */
 for(unsigned kind=0;kind<6;kind++){
  registry();frame(280,27);blit_background_row(&surface,0,-1,&megaData1.mainmap[280][0]);render_mirror_shapesy_end();
  assert(shapesy_frame.live&&shapesy_frame_check());
  if(kind==0)rgb_palette[5]^=1;if(kind==1)levelFilter=4;if(kind==2)levelBrightness=-3;
  if(kind==3)megaData1.shapes[zslot].sh[20]^=1;if(kind==4)shapesy_resources.generation++;if(kind==5)smoothies[1]=true;
  assert(!shapesy_frame_check());shapesy_frame_reset();assert(shapesy_frame_check());
  if(kind==0)rgb_palette[5]^=1;filterActive=true;levelFilter=-99;levelBrightness=-99;smoothies[1]=false;
 }registry();
 puts("shapesY finite runtime, native water/classic owners, all28 static windows and guards PASS");
}
int main(int argc,char **argv)
{
 assert(argc==4);game_probe_assets=argv[2];surface.clip_rect=(SDL_Rect){0,0,320,200};asteroid_hd_enabled=false;
 FILE *f=fopen(argv[1],"rb");assert(f);assert(fread(lookup,2,72,f)==72);assert(fread(original_sources,672,72,f)==72);assert(fread(map_indices,1,4200,f)==4200);
 for(unsigned i=0;i<256;i++){Uint8 p[3];assert(fread(p,1,3,f)==3);rgb_palette[i]=p[0]<<16|p[1]<<8|p[2];}assert(fgetc(f)==EOF);fclose(f);
 if(!strcmp(argv[3],"reject")){registry();frame(280,1);assert(!shapesy_pass.live);puts("atomic reject PASS");}
 else checks();shapesy_shutdown();return 0;
}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--pack',type=Path);p.add_argument('--sanitize',action='store_true');p.add_argument('--positive-only',action='store_true');p.add_argument('--sdl-include',action='append',default=[]);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 r=(ROOT/'src/render_mirror.c').read_text();b=(ROOT/'src/backgrnd.c').read_text();inc=(ROOT/'src/shapesy_platform_mirror.inc').read_text()
 ext=module(ROOT/'tests/test_asteroid1_ten_assets.py','y_extract').extract
 assert 'if(!shapesy_frame_check())' in ext(r,'render_mirror_finish')
 assert 'if(!shapesy_frame_check()||!shapesy_present_geometry(renderer,dst)||' in ext(r,'render_mirror_present')
 assert '||!cyan_frame_check()||!cyan_present_geometry(renderer,dst))' in ext(r,'render_mirror_present')
 assert 'shapesy_frame_reset();' in ext(r,'render_mirror_begin')
 assert 'shapesy_frame_reset();' in ext(r,'render_mirror_unsupported')
 assert '!qualified_y&&!qualified_cyan)replaced=false;' in ext(r,'render_mirror_terrain_pixel')
 assert 'cyan_native_pixel(surface,address,source,style,replaced,&qualified_cyan);' in ext(r,'render_mirror_terrain_pixel')
 orb=module(ROOT/'tests/test_asteroid1_enemy_orb112113_runtime.py','y_prefix')
 raw=(a.data/'shapesy.dat').read_bytes();assert hashlib.sha256(raw).hexdigest()=='1faf60f8804c4ca52ea41ece94e3d2fd3cdaecb437b63ecb61adc58907c7b869';tiles={};pos=0
 for i in range(1,601):
  blank=raw[pos];pos+=1;tiles[i]=bytes(672) if blank else raw[pos:pos+672];pos+=0 if blank else 672
 raw=(a.data/'tyrian1.lvl').read_bytes();pos=316541;mc,sc,x1,x2,x3,ne=struct.unpack_from('<ccHHHH',raw,pos);assert (mc,sc)==(b'3',b'Y');pos+=10+2*ne
 n=struct.unpack_from('<H',raw,pos)[0];pos+=2+11*n;lookup=struct.unpack_from('>128H',raw,pos)[:72];pos+=768;grid=raw[pos:pos+4200]
 pal=(a.data/'palette.dat').read_bytes()[5*768:6*768];pal=bytes((v<<2)|(v>>4) for v in pal)
 data=a.out/'original-sources.bin';data.write_bytes(struct.pack('<72H',*lookup)+b''.join(tiles[i] for i in lookup)+grid+pal)
 pack=a.pack or a.out/'synthetic-pack';pack.mkdir(exist_ok=True)
 if not a.pack:
  pins=[]
  for i in IDS:
   rgba=bytes(c for y in range(224) for x in range(192) for c in ((0,0,0,0) if 48<=tiles[i][y//8*24+x//8]<=63 else (0,0,0,255) if not tiles[i][y//8*24+x//8] else (73,91,109,255)))
   pins.append(fnv(rgba));(pack/f'terrain-shapesy-{i}-8.hda').write_bytes(struct.pack('<4s6I',b'HDR1',2020000+i,8,24,28,0,0)+rgba)
  inc=inc.replace('#include "current_shapesy_platform_hd_assets.h"','static const uint64_t shapesy_rgba_pins[28]={'+','.join(f'UINT64_C(0x{v:016x})' for v in pins)+'};')
 enum=re.search(r'enum \{ ASSET_NEWSH2=.*?\};',r).group(0)
 prefix=orb.PREFIX[:orb.PREFIX.index('static void game_probe_scene_draw')].replace('@ENUM@',enum).replace('@READ_GATES@','(void)a;').replace('game_probe_scene_assets=1','game_probe_scene_assets=2')
 prefix=prefix.replace('static void render_mirror_unsupported(const char *reason){reject_reason=reason;rejected++;}','static void shapesy_frame_reset(void);\nstatic void render_mirror_unsupported(const char *reason){shapesy_frame_reset();reject_reason=reason;rejected++;}')
 prefix=prefix.replace('8192','32768')
 geometry_type=re.search(r'typedef struct VideoOutputGeometry \{.*?\} VideoOutputGeometry;', (ROOT/'src/video.h').read_text(),re.S).group(0)
 prefix+='typedef int ScalingMode;\n'+geometry_type+'\n'
 prefix+=r'''static VideoOutputGeometry mock_geometry={(SDL_Window *)1,(SDL_Renderer *)2,1,{0,0,1280,800},1280,800,1280,800,4,2,0};
static bool mock_geometry_available=true;
static bool video_output_geometry(VideoOutputGeometry *out){if(!mock_geometry_available)return false;*out=mock_geometry;return true;}
'''
 prefix+=ext((ROOT/'src/video.c').read_text(),'video_output_geometry_equal')
 prefix+=EXTRA
 # Match the production declaration before extracted draw_asset_filtered.
 prefix+='static void shapesy_borrow_mark(size_t n,Uint32 color);\n'
 helpers=''.join(ext(r,n) for n in ('palette_rgb','blend_rgba','darken_rgba','cloud_asset','draw_asset_filtered'))
 helpers+=ext((ROOT/'src/asteroid1_ten_mirror.inc').read_text(),'asteroid1_stamp')+inc
 pixel=ext(r,'render_mirror_pixel');suffix=pixel[pixel.index(' if(suppress)'):]
 helpers+='static void render_mirror_pixel(SDL_Surface *surface,Uint8 *address,Uint8 source,int style){\n shapesy_clear_proof=false;assert(surface==game_screen&&style==MIRROR_NORMAL);int n=(int)(address-(Uint8 *)surface->pixels),x=n%320,y=n/320;Uint8 before=expected[n];expected[n]=*address;\n'+suffix
 rect=ext(r,'render_mirror_rect');rect=rect[rect.index(' int x0='):];helpers+='static void render_mirror_rect(SDL_Surface *s,const SDL_Rect *rect){\n'+rect
 helpers+='static unsigned render_mirror_terrain_row(SDL_Surface *s,int x,int y,Uint8 **map,int style){return shapesy_row(s,x,y,map,style);}\n'+ext(r,'render_mirror_terrain_pixel')+ext(b,'blit_background_row')+ext(b,'draw_background_1')
 harness=a.out/'harness.c';harness.write_text(prefix+helpers+CHECKS)
 flags=['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-misleading-indentation','-O2','-I'+str(ROOT/'src')]+['-I'+x for x in a.sdl_include]
 if a.sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
 exe=a.out/'runtime';res=subprocess.run(flags+[str(harness),'-lm','-o',str(exe)],capture_output=True,text=True);(a.out/'compile.log').write_text(res.stdout+res.stderr);assert res.returncode==0,res.stderr
 res=subprocess.run([str(exe),str(data),str(pack),'accept'],capture_output=True,text=True);(a.out/'positive.log').write_text(res.stdout+res.stderr);assert res.returncode==0,res.stderr
 print(res.stdout)
 if a.positive_only:
  (a.out/'receipt.json').write_text(json.dumps(dict(synthetic_art=not bool(a.pack),atomic_negative_fixtures=0,sanitize=a.sanitize,source_sha256=hashlib.sha256(inc.encode()).hexdigest(),harness_sha256=hashlib.sha256(harness.read_bytes()).hexdigest(),positive_only=True,passed=True),indent=2))
  return
 # Whole family is atomic: every member missing/corrupt, then malformed
 # representative headers/length/alpha. Original packs are never edited.
 fixtures=a.out/'negative';fixtures.mkdir(exist_ok=True);negative_count=0
 kinds=['missing','payload']
 for index in IDS:
   for kind in kinds+(['magic','role','density','width','height','anchor','short','trailing','alpha'] if index==321 else []):
     d=fixtures/f'{index}-{kind}';d.mkdir(exist_ok=True)
     for other in IDS:
       target=d/f'terrain-shapesy-{other}-8.hda'
       if target.exists() or target.is_symlink():target.unlink()
       if other!=index:target.symlink_to((pack/f'terrain-shapesy-{other}-8.hda').resolve())
     blob=bytearray((pack/f'terrain-shapesy-{index}-8.hda').read_bytes())
     if kind!='missing':
       if kind=='payload':blob[40]^=1
       elif kind=='magic':blob[:4]=b'NOPE'
       elif kind=='short':blob=blob[:-1]
       elif kind=='trailing':blob+=b'x'
       elif kind=='alpha':blob[31]=127
       else:struct.pack_into('<I',blob,dict(role=4,density=8,width=12,height=16,anchor=20)[kind],1)
       (d/f'terrain-shapesy-{index}-8.hda').write_bytes(blob)
     res=subprocess.run([str(exe),str(data),str(d),'reject'],capture_output=True,text=True)
     (d/'result.log').write_text(res.stdout+res.stderr);assert res.returncode==0,(index,kind,res.stderr)
     negative_count+=1
 (a.out/'receipt.json').write_text(json.dumps(dict(synthetic_art=not bool(a.pack),atomic_negative_fixtures=negative_count,sanitize=a.sanitize,source_sha256=hashlib.sha256(inc.encode()).hexdigest(),harness_sha256=hashlib.sha256(harness.read_bytes()).hexdigest(),passed=True),indent=2))
if __name__=='__main__':main()
