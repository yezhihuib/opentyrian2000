#define main static_hud_legacy_main
#include "../gameplay-hud/test_renderer.c"
#undef main
static Uint8 meter_source[64000];
static const int meter_boxes[4][4]={{289,17,311,20},{289,38,311,41},{269,12,277,104},{307,137,316,195}};
static unsigned meter_count(unsigned mask){unsigned n=0;for(unsigned i=0;i<64000;i++)n+=(component_output_owner[i]&mask)!=0;return n;}
static void activate_meters(const char *path,int d,bool words,bool meters,bool frame_art){
 setup(d,path);expanded_test=false;read_fixture(path,"meter-source.indices",meter_source,64000);memcpy(VGAScreenSeg->pixels,meter_source,64000);
 render_mirror_hud_start(VGAScreenSeg);assert(component_gameplay==(words||meters)&&hud_components_ready()==words&&hud_meters_ready()==meters&&hud_gameplay==frame_art);
}
static void write_meter(unsigned kind,unsigned a,unsigned b){
 render_mirror_hud_meter_begin(VGAScreenSeg,VGAScreenSeg,kind,a,b);unsigned box=kind<2?kind:kind==2?2:3;
 for(int y=meter_boxes[box][1];y<meter_boxes[box][3];y++)for(int x=meter_boxes[box][0];x<meter_boxes[box][2];x++){
  Uint8 *p=(Uint8 *)VGAScreenSeg->pixels+y*320+x;
  if(kind<2)*p=x-289<2*(int)a?116+(x-289)/2:0;
  else if(kind==2){int lo=102-(int)(a>b?a:b),hi=103-(int)(a<b?a:b);if(y>=lo&&y<=hi)*p=b>a?113+b/7:0;}
  else if(kind==3){if(y<=194-2*(int)a)*p=0;}
  else if(y>=193-2*(int)a){int z=(194-y)/2;*p=226+(z<3?0:(z-1)/2);}
 }
 render_mirror_hud_meter_end(VGAScreenSeg,kind);
}
static void fills(void){write_meter(0,1,0);write_meter(1,6,0);write_meter(2,0,90);write_meter(4,10,0);}
static void shield(void){
 for(int y=137;y<195;y++)for(int x=270;x<279;x++){int z=(194-y)/2;((Uint8 *)VGAScreenSeg->pixels)[y*320+x]=z<=10?146+(z<3?0:(z-1)/2):0;}
 render_mirror_hud_shield_drawn(VGAScreenSeg,10,10);
}
static Uint32 packed(const Uint8 *p){assert(p);return 0xff000000u|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];}
static void verify(void){
 int d=game_probe_density;
 for(int y=0;y<200;y++)for(int x=0;x<320;x++)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[320*y+x];Uint32 want=palette_rgb(index);unsigned owner=component_output_owner[320*y+x];
  if(x<264&&y<184)want=palette_rgb(7);
  if(hud_output_owner[y*320+x])want=packed(gameplay_hud_sample(x,y,sx,sy,d,index));
  if(owner==1)want=packed(hud_components_label_sample(x,y,sx,sy,d,index));
  else if(owner==2)want=packed(hud_components_shield_sample(x,y,sx,sy,d,index));
  else if(owner&60)want=packed(hud_meters_sample(x,y,sx,sy,d,index));
  assert(*pixel(output,x*d+sx,y*d+sy)==want);
 }
}
static void suite(const char *path,int d){
 activate_meters(path,d,true,true,true);frame(false,true);assert(!meter_count(60));unsigned alloc=allocations;
 fills();shield();frame(false,true);assert(meter_count(4)==6&&meter_count(8)==36&&meter_count(16)==736&&meter_count(32)==198&&meter_count(1)==350&&meter_count(2)==198);verify();assert(alloc==allocations);
 /* Live values never replace accepted display. End-level is no-write reuse. */
 player[0].armor=0;player[0].items.weapon[0].power=11;power=0;frame(false,true);assert(meter_count(4)==6&&meter_count(32)==198);verify();
 ((Uint8 *)VGAScreenSeg->pixels)[100*320+270]^=1;frame(false,true);assert(!meter_count(16)&&meter_count(32)==198&&meter_count(1)==350);verify();
 ((Uint8 *)VGAScreenSeg->pixels)[100*320+270]^=1;frame(false,true);assert(!meter_count(16));write_meter(2,0,90);frame(false,true);assert(meter_count(16)==736);
 write_meter(4,1,0);frame(false,true);assert(meter_count(32)==198);write_meter(3,0,0);frame(false,true);assert(!meter_count(32));write_meter(4,0,0);frame(false,true);assert(meter_count(32)==18);
 for(int modal=0;modal<3;modal++){uint64_t gen=component_generation;render_mirror_hud_suspend();assert(!meter_count(63)&&component_suspended&&component_generation==gen);frame(false,true);assert(meter_count(16)==736&&meter_count(32)==18);}
 render_mirror_release_texture();assert(component_suspended);frame(false,true);verify();
 write_meter(0,12,0);frame(false,true);assert(!meter_count(4)&&meter_count(8)==36);write_meter(0,1,0);frame(false,true);assert(meter_count(4)==6);
 render_mirror_hud_meter_begin(NULL,VGAScreenSeg,HUD_WRITE_REAR,1,0);frame(false,true);assert(!meter_count(8)&&meter_count(4)==6);
 write_meter(1,6,0);frame(false,true);verify();
}
static void counterfactual(const char *path,int d,unsigned solid,unsigned removal){
 activate_meters(path,d,true,true,true);fills();shield();frame(false,true);
 size_t pixels=(size_t)output->w*output->h;Uint32 *reference=malloc(pixels*4),*target=malloc(pixels*4);assert(reference&&target);
 for(int y=0;y<output->h;y++){memcpy(reference+(size_t)y*output->w,(Uint8 *)output->pixels+y*output->pitch,output->w*4);memcpy(target+(size_t)y*output->w,reference+(size_t)y*output->w,output->w*4);}
 Uint8 owners[64000],static_owners[64000];memcpy(owners,component_output_owner,64000);memcpy(static_owners,hud_output_owner,64000);Uint32 normal[256];memcpy(normal,rgb_palette,sizeof(normal));
 SDL_Color color={solid,solid,solid,255};render_mirror_fade_start(NULL,&color,0,255);
 for(int step=4;step;step--){
  if(step==3){uint64_t gen=component_generation;components_clear_cached(removal);assert(component_generation==gen);for(unsigned i=0;i<64000;i++)if(owners[i]&removal){owners[i]=0;for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){size_t j=((size_t)(i/320)*d+sy)*output->w+(i%320)*d+sx;reference[j]=palette_rgb(last_output_indices[i]);target[j]=0xff000000u|(normal[last_output_indices[i]]&0xffffffu);}}if(removal==3)assert(component_output_generation==gen&&component_saved_generation==gen&&meter_count(60));if(removal==60)assert(component_output_generation==gen&&component_saved_generation==gen&&meter_count(3));}
  palette_step(solid,step,NULL);render_mirror_fade_step(step);
  for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++){unsigned i=(y/d)*320+x/d;size_t j=(size_t)y*output->w+x;reference[j]=(owners[i]||static_owners[i])?channel_step(reference[j],solid?0xffffffffu:0xff000000u,step):palette_rgb(last_output_indices[i]);assert(*pixel(output,x,y)==reference[j]);}
 }
 SDL_Color restore[256];for(unsigned i=0;i<256;i++)restore[i]=(SDL_Color){normal[i]>>16,normal[i]>>8,normal[i],255};render_mirror_fade_start(restore,NULL,0,255);
 for(int step=4;step;step--){palette_step(0,step,normal);render_mirror_fade_step(step);for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++){unsigned i=(y/d)*320+x/d;size_t j=(size_t)y*output->w+x;reference[j]=(owners[i]||static_owners[i])?channel_step(reference[j],target[j],step):palette_rgb(last_output_indices[i]);assert(*pixel(output,x,y)==reference[j]);}}
 free(reference);free(target);
}
static void isolated(const char *path,int d){
 char p[2048];snprintf(p,sizeof(p),"%s/meter-only",path);activate_meters(p,d,false,true,false);fills();frame(false,true);assert(meter_count(60)==976&&last_output_valid);verify();
 /* Every field can be the final current/saved owner. */
 for(unsigned bit=4;bit<=32;bit*=2){activate_meters(p,d,false,true,false);fills();frame(false,true);SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);components_clear_cached(60^bit);assert(meter_count(bit)&&last_output_valid&&component_output_generation==component_generation&&component_saved_generation==component_generation);components_clear_cached(bit);assert(!meter_count(63)&&!component_output_generation&&!component_saved_generation&&!last_output_valid&&!have_fade_saved);}
 snprintf(p,sizeof(p),"%s/no-words",path);activate_meters(p,d,false,true,true);fills();frame(false,true);assert(meter_count(60)==976&&hud_gameplay);verify();
 for(unsigned variant=0;variant<2;variant++){snprintf(p,sizeof(p),"%s/%s",path,variant?"bad-meter":"no-meter");activate_meters(p,d,true,false,true);fills();shield();frame(false,true);assert(!meter_count(60)&&meter_count(3)==548);verify();}
}
static void distrust(const char *path){
 /* Mutate one property at a time after a valid saved frame. Exercise actual
  * fade_start/fade_step/present entry points, not just the private predicate. */
 for(unsigned entry=0;entry<3;entry++)for(unsigned bad=0;bad<18;bad++){
  activate_meters(path,4,true,true,true);fills();frame(false,true);SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
  assert(component_output_generation==component_generation&&component_saved_generation==component_generation&&have_fade_saved);
  unsigned cell=17*320+289;assert(component_output_owner[cell]==4&&component_saved_owner[cell]==4);
  if(bad==0)component_output_generation++;
  if(bad==1)component_saved_generation++;
  if(bad==2)component_output_generation=0;
  if(bad==3)component_saved_generation=0;
  if(bad==4)component_output_owner[cell]=0;
  if(bad==5)component_saved_owner[cell]=0;
  if(bad==6)component_output_owner[cell]=8;
  if(bad==7)component_saved_owner[cell]=8;
  if(bad==8)component_output_owner[cell]=12;
  if(bad==9)component_saved_owner[cell]=132;
  if(bad==10)memset(component_output_owner,0,sizeof(component_output_owner));
  if(bad==11)memset(component_saved_owner,0,sizeof(component_saved_owner));
  if(bad==12){memset(component_output_owner,0,sizeof(component_output_owner));memset(component_saved_owner,0,sizeof(component_saved_owner));}
  if(bad==13)have_fade_saved=false;
  if(bad==14){SDL_FreeSurface(fade_saved);fade_saved=NULL;}
  if(bad==15)component_output_owner[cell]=128;
  if(bad==16)component_saved_owner[cell]=128;
  if(bad==17){memset(component_output_owner,0,sizeof(component_output_owner));memset(component_saved_owner,0,sizeof(component_saved_owner));component_output_generation=component_saved_generation=0;component_saved_owner[cell]=128;}
  if(entry==0)assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));
  else if(entry==1)render_mirror_fade_step(4);
  else render_mirror_fade_start(NULL,&black,0,255);
  assert(!ready&&!last_output_valid&&!have_fade_saved&&!component_output_generation&&!component_saved_generation);
 }
 for(unsigned bad=0;bad<2;bad++){
  activate_meters(path,4,true,true,true);fills();frame(false,true);
  if(bad==0)game_probe_density=2;else component_output_palette[113]^=1;
  assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));assert(!ready&&!last_output_valid&&!have_fade_saved);
 }
 activate_meters(path,4,true,true,true);fills();frame(false,true);twoPlayerMode=true;render_mirror_present(NULL,VGAScreenSeg,NULL);assert(!component_gameplay&&!hud_meters_ready());twoPlayerMode=false;frame(false,true);assert(!meter_count(60));
 activate_meters(path,4,true,true,true);fills();frame(false,true);SDL_Surface *old=VGAScreenSeg;VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,0);memcpy(VGAScreenSeg->pixels,old->pixels,64000);SDL_FreeSurface(old);render_mirror_present(NULL,VGAScreenSeg,NULL);assert(!component_gameplay&&!hud_meters_ready());
}
int main(int argc,char **argv){assert(argc==2);for(int d=4;d<=8;d+=4){suite(argv[1],d);isolated(argv[1],d);for(unsigned solid=0;solid<=255;solid+=255){counterfactual(argv[1],d,solid,3);counterfactual(argv[1],d,solid,60);if(solid==255)break;}}distrust(argv[1]);cleanup();puts("PASS HUM2 production compositor: independent ownership/resources, source lease, current+saved generations, each last-owner, cross-resource removal and whole-output4/8 fade counterfactuals.");return 0;}
