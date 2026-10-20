#!/usr/bin/env python3
"""Bounded extracted-production map-E fixture144 source, pass and compositor tests.

Reads the named original shapesz.dat/tyrian1.lvl only. Executes the actual
background1 pass, indexed row blitter, stars, private helper and normal RGBA
compositor. Unrelated legacy terrain selection and font/HUD effects are stubs.
No gameplay mutation, original-data edits, game launch or publication.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
IDS=(429,430,439,440)

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

EXTRA=r'''
static const Asset *terrain144_draw_lease;
static char terrain_file='z';
static struct {Uint8 *mainmap[300][14];struct {Uint8 sh[672];} shapes[72];} megaData1;
static unsigned short lookup[72];static Uint8 original_sources[72][672],map_indices[4200];
static Uint8 **mapYPos;static intptr_t mapXbpPos;static int mapXPos,backPos;
static unsigned traced,accepted_rows,original_writes;
static bool observe=true;
static FILE *trace_file;
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored)
{assert(role==144&&(id==429||id==430||id==439||id==440)&&!part&&style==MIRROR_NORMAL);traced++;if(trace_file)fprintf(trace_file,"%llu,%u,%d,%d,%d\n",(unsigned long long)mirror_logic_tick,id,x,y,mirrored);}
static void asset_debug_terrain_row(int x,int y,Uint8 **map){(void)x;(void)y;(void)map;}
static void render_mirror_ground101_layer1(SDL_Surface *s,const void *p,int x,int y){(void)s;(void)p;(void)x;(void)y;}
int SDL_FillRect(SDL_Surface *s,const SDL_Rect *r,Uint32 c)
{assert(!r&&!c&&s==&surface);memset(pixels,0,64000);return 0;}
static void render_mirror_rect(SDL_Surface *s,const SDL_Rect *r)
{assert(s==&surface&&!r);for(unsigned i=0;i<2560*1600;i++)canvas_pixels[i]=rgb_palette[0];memset(hd_owner,0,sizeof(hd_owner));memset(cloud_owner,0,sizeof(cloud_owner));}
static void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,int style)
{
 assert(s==&surface&&p>=pixels&&p<pixels+64000&&*p==v&&style==MIRROR_NORMAL);original_writes++;
 if(!observe||suppress)return;
 size_t n=(size_t)(p-pixels);unsigned x=n%320,y=n/320;
 for(unsigned yy=0;yy<8;yy++)for(unsigned xx=0;xx<8;xx++) {unsigned at=(y*8+yy)*2560+x*8+xx;canvas_pixels[at]=rgb_palette[v];hd_owner[at]=0;}
}
'''

CHECKS=r'''
static void registry(void)
{
 terrain_file='z';render_mirror_asteroid_terrain_map('E','Z');
 for(unsigned i=0;i<72;i++){memcpy(megaData1.shapes[i].sh,original_sources[i],672);terrain144_bind(1,lookup[i],megaData1.shapes[i].sh);}
 for(unsigned y=0;y<300;y++)for(unsigned x=0;x<14;x++)megaData1.mainmap[y][x]=megaData1.shapes[map_indices[y*14+x]].sh;
 assert(terrain144_sources_valid()&&terrain144_map_valid());
}
static void frame(unsigned row,unsigned col,int x,int scroll)
{
 mirror_logic_tick++;reject_reason=NULL;region_count=0;suppress=false;suppress_cloud=false;suppress_green_smoke=false;
 mapXPos=x;backPos=scroll;mapXbpPos=1;mapYPos=&megaData1.mainmap[0][0]+row*14+col+11;
 render_mirror_asteroid_terrain_end();
}
static void begin(unsigned row,unsigned col,int x,int scroll)
{frame(row,col,x,scroll);render_mirror_asteroid_terrain_layer1(&surface,&megaData1.mainmap[row][col],x,scroll-28);}
static void source_guards(void)
{
 for(unsigned k=0;k<4;k++) {
  unsigned slot=0;while(lookup[slot]!=terrain144_ids[k])slot++;
  for(unsigned n=0;n<672;n++) {
   registry();megaData1.shapes[slot].sh[n]^=1;
   assert(!terrain144_sources_valid());begin(107,0,0,0);assert(!terrain144_pass.live);
   registry();render_mirror_asteroid_terrain_map('E','Z');megaData1.shapes[slot].sh[n]^=1;
   for(unsigned i=0;i<72;i++)terrain144_bind(1,lookup[i],megaData1.shapes[i].sh);
   assert(!terrain144_sources_valid());
  }
 }
 registry();begin(107,0,0,1);assert(terrain144_pass.live);
 unsigned bits=terrain144_row(&surface,0,-27,&megaData1.mainmap[107][0],MIRROR_NORMAL);assert(bits==(3u<<6));
 megaData1.shapes[58].sh[0]^=1;assert(!terrain144_row(&surface,0,1,&megaData1.mainmap[108][0],MIRROR_NORMAL)&&reject_reason);registry();
 /* Unused duplicate loader slots are still validated, including warm bytes. */
 render_mirror_asteroid_terrain_map('E','Z');
 for(unsigned i=0;i<72;i++){unsigned id=lookup[i];if(i==8){id=429;memcpy(megaData1.shapes[i].sh,original_sources[58],672);}terrain144_bind(1,id,megaData1.shapes[i].sh);}
 assert(terrain144_sources_valid()&&terrain144_map_valid());megaData1.shapes[8].sh[671]^=1;assert(!terrain144_sources_valid());registry();
 Uint8 clone[672];memcpy(clone,original_sources[58],672);assert(!terrain144_id(clone)&&!terrain144_id(megaData1.shapes[58].sh+1));
 terrain144_bind(1,429,clone);assert(!terrain144_sources_valid());registry();
 terrain144_bind(2,429,megaData1.shapes[58].sh);assert(terrain144_sources_valid());
 for(unsigned i=0;i<4200;i++){Uint8 **p=&megaData1.mainmap[i/14][i%14],*old=*p;*p=old==megaData1.shapes[58].sh?megaData1.shapes[63].sh:megaData1.shapes[58].sh;assert(!terrain144_map_valid());*p=old;}
 registry();
}
static void context_guards(void)
{
 bool *flags[]={&xmas,&isNetworkGame,&twoPlayerMode,&galagaMode,&twoPlayerLinked,&record_demo,&onePlayerAction,&superTyrian,&timedBattleMode,&bonusLevel,&normalBonusLevelCurrent,&bonusLevelCurrent,&play_demo};
 for(unsigned i=0;i<sizeof(flags)/sizeof(*flags);i++){*flags[i]=true;begin(107,0,0,1);assert(!terrain144_pass.live);*flags[i]=false;}
 int *off[]={&episodeNum,&lvlFileNum};for(unsigned k=0;k<2;k++)for(int n=0;n<20;n++)if(n!=1){*off[k]=n;begin(107,0,0,1);assert(!terrain144_pass.live);*off[k]=1;}
 superArcadeMode=1;begin(107,0,0,1);assert(!terrain144_pass.live);superArcadeMode=0;
 bool *disable[]={&active,&asteroid_hd_enabled,&asteroid_hd_lease};for(unsigned i=0;i<3;i++){*disable[i]=false;begin(107,0,0,1);assert(!terrain144_pass.live);*disable[i]=true;}
 game_probe_enabled=true;asteroid_hd_lease=false;begin(107,0,0,1);assert(terrain144_pass.live);game_probe_enabled=false;asteroid_hd_lease=true;
 game_probe_scene_assets=1;begin(107,0,0,1);assert(!terrain144_pass.live);game_probe_scene_assets=2;
 bool *bad[]={&game_probe_missing,&game_probe_invalid,&game_probe_original_reference};for(unsigned i=0;i<3;i++){*bad[i]=true;begin(107,0,0,1);assert(!terrain144_pass.live);*bad[i]=false;}
 for(int d=0;d<10;d++)if(d!=8){game_probe_density=d;begin(107,0,0,1);assert(!terrain144_pass.live);}game_probe_density=8;
 const char *root=game_probe_assets;game_probe_assets=NULL;begin(107,0,0,1);assert(!terrain144_pass.live);game_probe_assets="";begin(107,0,0,1);assert(!terrain144_pass.live);game_probe_assets="unselected";begin(107,0,0,1);assert(!terrain144_pass.live);game_probe_assets=root;
 SDL_Surface old=surface,other=surface;SDL_PixelFormat f=format;
#define BAD_SURFACE(k,v) do{surface.k=v;begin(107,0,0,1);assert(!terrain144_pass.live);surface=old;}while(0)
 BAD_SURFACE(pixels,NULL);BAD_SURFACE(w,319);BAD_SURFACE(h,199);BAD_SURFACE(pitch,319);BAD_SURFACE(pitch,321);BAD_SURFACE(format,NULL);
#define BAD_FORMAT(k,v) do{format.k=v;begin(107,0,0,1);assert(!terrain144_pass.live);format=f;}while(0)
 BAD_FORMAT(format,SDL_PIXELFORMAT_ARGB8888);BAD_FORMAT(BitsPerPixel,32);BAD_FORMAT(BytesPerPixel,4);
 frame(107,0,0,1);render_mirror_asteroid_terrain_layer1(&other,&megaData1.mainmap[107][0],0,-27);assert(!terrain144_pass.live);
 render_mirror_asteroid_terrain_layer1(NULL,&megaData1.mainmap[107][0],0,-27);assert(!terrain144_pass.live);
 VGAScreen=&other;begin(107,0,0,1);assert(!terrain144_pass.live);VGAScreen=&surface;
 game_screen=&other;begin(107,0,0,1);assert(!terrain144_pass.live);game_screen=&surface;
 for(int x=-1;x<=33;x++)if(x<0||x>32){begin(107,0,x,1);assert(!terrain144_pass.live);}
 begin(107,0,0,-1);assert(!terrain144_pass.live);begin(107,0,0,28);assert(!terrain144_pass.live);
 begin(107,3,0,1);assert(!terrain144_pass.live);begin(293,0,0,1);assert(!terrain144_pass.live);
 frame(107,0,0,1);mapYPos++;render_mirror_asteroid_terrain_layer1(&surface,&megaData1.mainmap[107][0],0,-27);assert(!terrain144_pass.live);
 for(unsigned k=0;k<3;k++){registry();if(k==0)terrain144_registry.map='A';if(k==1)terrain144_registry.shape='A';if(k==2)terrain_file='a';begin(107,0,0,1);assert(!terrain144_pass.live);}registry();
 begin(107,0,0,1);assert(terrain144_pass.live);assert(!terrain144_row(&surface,0,-27,&megaData1.mainmap[107][0],MIRROR_BLEND));
 begin(107,0,0,1);assert(!terrain144_row(&surface,1,-27,&megaData1.mainmap[107][0],MIRROR_NORMAL));
 begin(107,0,0,1);assert(!terrain144_row(&surface,0,-26,&megaData1.mainmap[107][0],MIRROR_NORMAL));
 begin(107,0,0,1);assert(!terrain144_row(&surface,0,-27,&megaData1.mainmap[108][0],MIRROR_NORMAL));
 Uint8 *copymap[12];memcpy(copymap,&megaData1.mainmap[107][0],sizeof(copymap));begin(107,0,0,1);assert(!terrain144_row(&surface,0,-27,copymap,MIRROR_NORMAL));
 begin(107,0,0,1);render_mirror_asteroid_terrain_end();assert(!terrain144_row(&surface,0,-27,&megaData1.mainmap[107][0],MIRROR_NORMAL));
 begin(107,0,0,1);assert(terrain144_row(&surface,0,-27,&megaData1.mainmap[107][0],MIRROR_NORMAL)==(3u<<6));assert(!terrain144_row(&surface,0,-27,&megaData1.mainmap[107][0],MIRROR_NORMAL)&&reject_reason);
 registry();
}
static void asset_guards(void)
{
 /* Warm source/map guards never cache; optional RGBA buffers intentionally
  * follow the existing immutable-per-tick resource convention. */
 begin(107,0,0,1);assert(terrain144_pass.live);Asset *cached=&terrain144_resources.members[0];
 cached->rgba[0]^=1;assert(terrain144_family_ready());
 begin(107,0,0,1);assert(!terrain144_pass.live);cached->rgba[0]^=1;terrain144_resources.valid=true;

 for(unsigned k=0;k<4;k++) {
  Asset *a=&terrain144_resources.members[k],old=*a;frame(107,0,0,1);
  assert(!draw_asset_filtered(144,60,a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL));
  enemy_orb112113_draw_lease=a;firing285_draw_lease=a;assert(!draw_asset_filtered(144,60,a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL));enemy_orb112113_draw_lease=firing285_draw_lease=NULL;
  terrain144_draw_lease=a;assert(!draw_asset_filtered(144,60,a,MIRROR_BLEND,NULL,0,NULL,NULL,NULL));SDL_Rect part={0,0,24,28};assert(!draw_asset_filtered(144,60,a,MIRROR_NORMAL,&part,0,NULL,NULL,NULL));assert(!draw_asset_filtered(144,60,a,MIRROR_NORMAL,NULL,1,NULL,NULL,NULL));terrain144_draw_lease=NULL;
  int *fields[]={&a->bank,&a->index,&a->density,&a->w,&a->h,&a->anchor_x,&a->anchor_y};
  for(unsigned f=0;f<7;f++){(*fields[f])++;begin(107,0,0,1);assert(!terrain144_pass.live);*a=old;terrain144_resources.valid=true;}
  a->rgba[0]^=1;begin(107,0,0,1);assert(!terrain144_pass.live);a->rgba[0]^=1;terrain144_resources.valid=true;
  a->rgba=NULL;begin(107,0,0,1);assert(!terrain144_pass.live);*a=old;terrain144_resources.valid=true;
  Asset generic=*a;generic.bank=201;assert(!read_asset(&generic,8));generic.bank=144;assert(!read_asset(&generic,8));
 }
}
static uint64_t stamp_canvas(void){return asteroid1_stamp((Uint8*)canvas_pixels,sizeof(canvas_pixels));}
static void verify_fixture_pixels(unsigned row,unsigned col,int x,int scroll)
{
 for(unsigned r=0;r<8;r++)for(unsigned tile=0;tile<12;tile++) {
  int k=terrain144_member(terrain144_id(megaData1.mainmap[row+r][col+tile]));if(k<0)continue;
  const Asset *a=&terrain144_resources.members[k];int ox=x+(int)tile*24,oy=scroll-28+(int)r*28;
  for(int sy=0;sy<28*8;sy++)for(int sx=0;sx<24*8;sx++) {
   int px=ox*8+sx,py=oy*8+sy;if(px<0||px>=2560||py<0||py>=1600)continue;
   const Uint8 *c=a->rgba+(sy*192+sx)*4;Uint32 expected=0xff000000u|(Uint32)c[0]<<16|(Uint32)c[1]<<8|c[2];
   assert(canvas_pixels[py*2560+px]==expected&&hd_owner[py*2560+px]==1);
  }
 }
}
static void trace_frames(void)
{
 Uint8 indexed[64000];StarfieldStar stars[MAX_STARS],after[MAX_STARS];unsigned count=0;
 for(unsigned p=0;p<5;p++)for(unsigned col=0;col<3;col++)for(unsigned scroll=0;scroll<28;scroll+=3) {
  unsigned row=terrain144_placements[p][1]-4;int x=(int)(scroll%24);
  frame(row,col,x,scroll);mt_srand(1234);initialize_starfield();memcpy(stars,starfield_stars,sizeof(stars));uint64_t rng=mt_state_fingerprint();
  asteroid_hd_enabled=false;observe=false;draw_background_1(&surface);update_and_draw_starfield(&surface,1);memcpy(indexed,pixels,64000);memcpy(after,starfield_stars,sizeof(after));assert(rng==mt_state_fingerprint());
  asteroid_hd_enabled=true;observe=true;frame(row,col,x,scroll);memcpy(starfield_stars,stars,sizeof(stars));unsigned prior=draws;draw_background_1(&surface);assert(!terrain144_pass.live&&!reject_reason&&draws>prior);verify_fixture_pixels(row,col,x,scroll);update_and_draw_starfield(&surface,1);
  assert(!memcmp(indexed,pixels,64000)&&!memcmp(after,starfield_stars,sizeof(after))&&rng==mt_state_fingerprint());
  /* Compare every selected source cell to original indexed bytes. */
  for(unsigned n=0;n<64000;n++)if(hd_owner[(n/320*8)*2560+n%320*8])assert(indexed[n]!=0);
  count++;
 }
 /* Top and bottom clipping, all28 phases, horizontal limits and row wrap. */
 for(unsigned scroll=0;scroll<28;scroll++)for(unsigned edge=0;edge<2;edge++) {
  unsigned row=edge?101:107;frame(row,0,32,scroll);asteroid_hd_enabled=false;observe=false;draw_background_1(&surface);memcpy(indexed,pixels,64000);
  asteroid_hd_enabled=true;observe=true;frame(row,0,32,scroll);draw_background_1(&surface);assert(!reject_reason&&!memcmp(indexed,pixels,64000));verify_fixture_pixels(row,0,32,scroll);
 }
 frame(150,0,0,1);draw_background_1(&surface);uint64_t nofixture=stamp_canvas();assert(!terrain144_pass.live);
 frame(103,0,0,1);draw_background_1(&surface);assert(stamp_canvas()!=nofixture);
 /* Ordered foreground HD draw stays above terrain; later classic pixel
  * overwrites both rather than inheriting a stale row suppression lease. */
 Asset foreground={true,true,108,31,1,1,0,0,8,NULL};Uint8 rgba[256];for(unsigned i=0;i<256;i+=4){rgba[i]=251;rgba[i+1]=13;rgba[i+2]=29;rgba[i+3]=255;}foreground.rgba=rgba;
 int x=145,y=90;assert(draw_asset_filtered(x,y,&foreground,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL));assert(canvas_pixels[y*8*2560+x*8]==0xfffb0d1d);suppress=false;pixels[y*320+x]=7;render_mirror_pixel(&surface,pixels+y*320+x,7,MIRROR_NORMAL);assert(canvas_pixels[y*8*2560+x*8]==rgb_palette[7]);
 printf("actual_background_and_star_traces=%u indexed_equal=1 star_state_equal=1 rng_equal=1 clipping_phases=28 foreground_order=1\n",count);
}
static void load_file(const char *path,void *p,size_t n){FILE *f=fopen(path,"rb");assert(f&&fread(p,1,n,f)==n&&fgetc(f)==EOF);fclose(f);}
int main(int argc,char **argv)
{
 assert(argc==5);game_probe_assets=argv[2];for(unsigned i=0;i<256;i++)rgb_palette[i]=0xff000000u|i*0x010101u;
 FILE *f=fopen(argv[1],"rb");assert(f);assert(fread(lookup,2,72,f)==72&&fread(original_sources,672,72,f)==72&&fread(map_indices,1,4200,f)==4200&&fgetc(f)==EOF);fclose(f);registry();
 begin(107,0,0,1);
 if(!strcmp(argv[3],"reject")){assert(!terrain144_pass.live);unsigned prior=draws;draw_background_1(&surface);assert(draws==prior&&!reject_reason);terrain144_shutdown();puts("atomic_optional_rejection=1");return 0;}
 assert(terrain144_pass.live);source_guards();context_guards();asset_guards();trace_file=fopen(argv[4],"w");assert(trace_file);fputs("tick,tile,x,y,mirrored\n",trace_file);trace_frames();fclose(trace_file);trace_file=NULL;
 assert(!unrelated_loads&&!terrain144_draw_lease);
 terrain144_shutdown();registry();begin(220,0,0,1);assert(!terrain144_pass.live&&!terrain144_resources.checked);draw_background_1(&surface);assert(!terrain144_resources.checked);
 terrain144_shutdown();puts("terrain144 source_map_context_resource_guards=PASS");return 0;
}
'''
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--sdl-include',action='append',default=[]);p.add_argument('--sanitize',action='store_true');a=p.parse_args();root=a.repo.resolve();a.out=a.out.resolve()
    a.out.mkdir(parents=True,exist_ok=True)
    if any(a.out.iterdir()):raise RuntimeError('Select a new empty output directory')
    if shutil.disk_usage(a.out).free<5_000_000_000:raise RuntimeError('At least5GB free required')
    ten=module(root/'tests/test_asteroid1_ten_assets.py','terrain144_ten');linked=module(root/'tests/test_asteroid1_linked338_runtime.py','terrain144_linked');orb=module(root/'tests/test_asteroid1_enemy_orb112113_runtime.py','terrain144_orb');extract=ten.extract
    names=('render_mirror.c','render_mirror.h','asteroid1_terrain144_mirror.inc','asteroid1_ten_mirror.inc','backgrnd.c','tyrian2.c','mtrand.c')
    source={n:(root/'src'/n).read_text() for n in names};r=source['render_mirror.c'];b=source['backgrnd.c']
    assert 'terrain144_shutdown();' in extract(r,'render_mirror_hud_shutdown')
    assert 'terrain144_map_reset(0,shape_file);' in extract(r,'render_mirror_map_begin')
    assert 'terrain144_bind(layer,id,data);' in extract(r,'render_mirror_bind_terrain')
    assert 'render_mirror_asteroid_terrain_map(char_mapFile,char_shapeFile);' in source['tyrian2.c']
    row=extract(r,'render_mirror_terrain_row');assert row.startswith('unsigned int render_mirror_terrain_row(SDL_Surface *surface,int x,int y,Uint8 **map,int style)\n{\n if(asteroid_hd_enabled)return terrain144_row(surface,x,y,map,style);')
    # Exact new production early dispatch. Legacy terrain selector is not exercised.
    row=row[:row.index(' if(!active')]+ ' return 0;\n}\n'
    enum=re.search(r'enum \{ ASSET_NEWSH2=.*?\};',r).group(0)
    reader=extract(r,'read_asset');gates=reader[reader.index(' if(a->bank==ASSET_ASTEROID1_NEWSHP'):reader.index(' char name[1024];')]
    prefix=orb.PREFIX[:orb.PREFIX.index('static void game_probe_scene_draw')].replace('@ENUM@',enum).replace('@READ_GATES@',gates).replace('static unsigned game_probe_scene_assets=1;','static unsigned game_probe_scene_assets=2;')
    helpers=''.join(extract(r,n) for n in ('asteroid1_level_scope','asteroid1_scope','palette_rgb','blend_rgba','darken_rgba','cloud_asset','draw_asset_filtered'))
    helpers+=extract(source['asteroid1_ten_mirror.inc'],'asteroid1_stamp')+source['asteroid1_terrain144_mirror.inc']+row
    helpers+=extract(r,'render_mirror_terrain_pixel')+extract(b,'blit_background_row')+extract(b,'draw_background_1')
    star_start=b.index('typedef struct',b.index('/* Background Starfield */'));helpers+=b[star_start:]
    harness=a.out/'harness.c';harness.write_text(prefix+EXTRA+helpers+source['mtrand.c']+CHECKS)
    assert not re.search(r'@[A-Z_]+@',harness.read_text())
    raw=(a.data/'shapesz.dat').read_bytes();assert hashlib.sha256(raw).hexdigest()=='3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248'
    tiles={};pos=0
    for i in range(1,601):
        blank=raw[pos];pos+=1;tiles[i]=bytes(672) if blank else raw[pos:pos+672]
        if not blank:pos+=672
    assert pos<=len(raw)  # The original loader reads exactly600 entries.
    raw=(a.data/'tyrian1.lvl').read_bytes();pos=struct.unpack_from('<I',raw,2)[0];mc,sc,x1,x2,x3,ne=struct.unpack_from('<ccHHHH',raw,pos);assert (mc,sc)==(b'E',b'Z');pos+=10+2*ne
    n=struct.unpack_from('<H',raw,pos)[0];pos+=2+11*n;lookup=struct.unpack_from('>128H',raw,pos)[:72];pos+=768;grid=raw[pos:pos+4200];assert max(grid)<72
    data=a.out/'original-map-sources.bin';data.write_bytes(struct.pack('<72H',*lookup)+b''.join(tiles[i] for i in lookup)+grid)
    pack=root/'assets/hd/packs/asteroid1-ten-v1';payloads=[(pack/f'terrain-shapesz-{i}-8.hda').read_bytes() for i in IDS]
    for i,blob in zip(IDS,payloads):assert len(blob)==172060 and struct.unpack_from('<4s6I',blob)==(b'HDR1',1440000+i,8,24,28,0,0)
    kinds=['missing','payload','magic','role201','role108','role143','wrong-tile','density','width','height','anchor-x','anchor-y','header-short','short','extra','fifo','directory','broken-symlink']
    fixtures=a.out/'fixtures';fixtures.mkdir();variants=[]
    for k,index in enumerate(IDS):
      for kind in kinds:
        d=fixtures/f'{index}-{kind}';d.mkdir();dest=d/f'terrain-shapesz-{index}-8.hda'
        for j,other in enumerate(IDS):
            if j!=k:(d/f'terrain-shapesz-{other}-8.hda').symlink_to(pack/f'terrain-shapesz-{other}-8.hda')
        if kind=='missing':pass
        elif kind=='fifo':os.mkfifo(dest)
        elif kind=='directory':dest.mkdir()
        elif kind=='broken-symlink':dest.symlink_to(d/'absent.hda')
        else:
            blob=bytearray(payloads[k])
            if kind=='payload':blob[100]^=1
            elif kind=='magic':blob[:4]=b'NOPE'
            elif kind.startswith('role'):struct.pack_into('<I',blob,4,int(kind[4:])*10000+index)
            elif kind=='wrong-tile':blob=bytearray(payloads[(k+1)%4])
            elif kind=='header-short':blob=blob[:12]
            elif kind=='short':blob=blob[:-1]
            elif kind=='extra':blob+=b'X'
            else:struct.pack_into('<I',blob,dict(density=8,width=12,height=16,**{'anchor-x':20,'anchor-y':24})[kind],1)
            dest.write_bytes(blob)
        variants.append(d)
    flags=['-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-function','-Wno-unused-variable','-I'+str(root/'src')]+['-I'+x for x in a.sdl_include]
    if not a.sdl_include:flags+=subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True).split()
    compiler_peak=runtime_peak=0;runs=[]
    for mode in ['optimized']+(['asan-ubsan'] if a.sanitize else []):
        exe=a.out/mode;compiler=['cc',*flags,'-O2']+(['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'] if mode=='asan-ubsan' else [])
        compiler_peak=max(compiler_peak,linked.run_bounded([*compiler,str(harness),'-lm','-o',str(exe)],a.out/(mode+'-compile.log'),compiler=True))
        for i,(directory,expected) in enumerate([(pack,'accept')]+[(d,'reject') for d in variants]):
            log=a.out/f'{mode}-{i:03d}.log';runtime_peak=max(runtime_peak,linked.run_bounded([str(exe),str(data),str(directory),expected,str(a.out/(mode+'-terrain-trace.csv'))],log,sanitize=mode=='asan-ubsan'))
        runs.append(dict(mode=mode,positive=1,negative=len(variants),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    output_bytes=sum(p.stat().st_size for p in a.out.rglob('*') if p.is_file() and not p.is_symlink())
    assert output_bytes<64*1024**2
    receipt=dict(material=144,source_indices=list(IDS),map='E',shape='Z',map_placements=[[6,107],[7,139],[8,158],[9,161],[6,163]],cold_source_byte_mutations=2688,warm_source_byte_mutations=2688,fullmap_cell_mutations=4200,all4_atomic_resources=True,actual_background_pass=True,actual_indexed_row_blitter=True,actual_normal_compositor=True,actual_procedural_stars=True,background_and_star_traces=150,INDEX8_equal=True,star_positions_colors_speeds_equal=True,RNG_equal=True,RGBA_hash_once_per_tick=True,same_tick_RGBA_mutation_limit='Payload byte revalidation occurs on the next logic tick; metadata and original source/map are checked each row.',source_pointer_alias_and_duplicate_checks=True,foreground_overlap_order=True,clipping_phases=28,clipping_INDEX8_comparisons=56,all_visible_RGBA_subpixels_exact=True,empty_window_skips_resource_IO=True,negative_optional_fixtures=len(variants),compiler_peak_rss_bytes=compiler_peak,runtime_peak_rss_bytes=runtime_peak,output_bytes=output_bytes,runs=runs,source_sha256={n:hashlib.sha256(s.encode()).hexdigest() for n,s in source.items()},harness_sha256=hashlib.sha256(harness.read_bytes()).hexdigest())
    (a.out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
