/* Synthetic parser/history/material oracle. Includes production implementation
 * only to probe I/O and inject sampler-only states, never original game data. */
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
static uint64_t test_pins[7];
static void *meter_malloc(size_t);static void meter_free(void *);
static int meter_open(const char *,int,...);static ssize_t meter_read(int,void *,size_t);
static int meter_fstat(int,struct stat *);static int meter_close(int);
#define HUD_METERS_PIC_FNV test_pins[0]
#define HUD_METERS_PALETTE_FNV test_pins[1]
#define HUD_METERS_FIRE_FNV test_pins[2]
#define HUD_METERS_ARMOR_FNV test_pins[3]
#define HUD_METERS_ROWS_FNV test_pins[4]
#define HUD_METERS_LOOKUP_FNV test_pins[5]
#define HUD_METERS_PAYLOAD_FNV test_pins[6]
#define malloc meter_malloc
#define free meter_free
#define open meter_open
#define read meter_read
#define fstat meter_fstat
#define close meter_close
#include "gameplay_hud_meters.c"
#undef malloc
#undef free
#undef open
#undef read
#undef fstat
#undef close
static unsigned allocations,frees,opens,reads,closes,stats,cases,mutations,pairs;
static int descriptor=-1,fail_alloc,fail_stat,fail_close,fail_read,size_override=-1;
static void *allocation;
static uint8_t raw[FILE_BYTES],pristine[64000],screen[64000],padded[337*200];
static uint32_t test_palette[256];
static char filename[2048];static const char *directory;
static void *meter_malloc(size_t n){allocations++;assert(n==PAYLOAD&&!allocation);if(fail_alloc)return NULL;return allocation=malloc(n);}
static void meter_free(void *p){if(p){assert(p==allocation);allocation=NULL;frees++;}free(p);}
static int meter_open(const char *p,int flags,...){assert(descriptor==-1);assert(flags&O_NONBLOCK);opens++;return descriptor=open(p,flags);}
static ssize_t meter_read(int fd,void *p,size_t n){assert(fd==descriptor&&n<=PAYLOAD);reads++;if(fail_read&&!--fail_read){errno=EIO;return -1;}return read(fd,p,n);}
static int meter_fstat(int fd,struct stat *s){assert(fd==descriptor);stats++;if(fail_stat)return -1;int r=fstat(fd,s);if(!r&&size_override>=0)s->st_size=size_override;return r;}
static int meter_close(int fd){assert(fd==descriptor);descriptor=-1;closes++;int r=close(fd);return fail_close?-1:r;}
static uint64_t reference_hash(const uint8_t *p,size_t n){uint64_t h=UINT64_C(0xcbf29ce484222325);while(n--){h^=*p++;h*=UINT64_C(0x100000001b3);}return h;}
static void put32(unsigned o,uint32_t v){for(unsigned j=0;j<4;j++)raw[o+j]=(uint8_t)(v>>(8*j));}
static void put64(unsigned o,uint64_t v){for(unsigned j=0;j<8;j++)raw[o+j]=(uint8_t)(v>>(8*j));}
static void rehash(void){
 uint8_t rgb[768];for(unsigned i=0;i<256;i++){rgb[3*i]=test_palette[i]>>16;rgb[3*i+1]=test_palette[i]>>8;rgb[3*i+2]=test_palette[i];}
 test_pins[0]=reference_hash(pristine,64000);test_pins[1]=reference_hash(rgb,768);
 test_pins[2]=reference_hash(raw+112,4224);test_pins[3]=reference_hash(raw+4336,51840);
 test_pins[4]=reference_hash(raw+56176,120832);test_pins[5]=reference_hash(raw+177008,444912);
 test_pins[6]=reference_hash(raw+112,621808);for(unsigned i=0;i<7;i++)put64(48+8*i,test_pins[i]);
}
static void fixture(void){
 memset(raw,0,sizeof(raw));memcpy(raw,"HUM2",4);unsigned values[]={2,112,4,320,200,4224,51840,120832,444912,944,222456};
 for(unsigned i=0;i<11;i++)put32(4+4*i,values[i]);
 for(unsigned i=0;i<176896;i+=4){raw[112+i]=(i/4)*7%251;raw[113+i]=(i/4)*11%253;raw[114+i]=(i/4)*17%255;raw[115+i]=255;}
 for(unsigned i=0;i<222456;i++){unsigned v=(i*17+11)%944;raw[177008+2*i]=v;raw[177009+2*i]=v>>8;}
 memset(pristine,7,sizeof(pristine));for(unsigned k=0;k<4;k++)for(int y=boxes[k][1];y<boxes[k][3];y++)memset(pristine+y*320+boxes[k][0],0,boxes[k][2]-boxes[k][0]);
 for(unsigned i=0;i<256;i++)test_palette[i]=(i*5%256)<<16|(i*11%256)<<8|(i*17%256);rehash();
}
static void write_file(size_t n){FILE *f=fopen(filename,"wb");assert(f);assert(fwrite(raw,1,n,f)==n);assert(!fclose(f));}
static void failed(void){hud_meters_shutdown();assert(!allocation&&descriptor==-1);assert(!hud_meters_load(directory));assert(!allocation&&descriptor==-1);unsigned o=opens;assert(!hud_meters_load(directory)&&opens==o);cases++;}
static void load(void){hud_meters_shutdown();write_file(FILE_BYTES);assert(hud_meters_load(directory));assert(allocation&&descriptor==-1);assert(!hud_meters_ready());}
static void reset_screen(void){memcpy(screen,pristine,sizeof(screen));assert(hud_meters_capture(screen,320));assert(hud_meters_prepare(screen,320)==60);}
static void parser(void){
 hud_meters_shutdown();assert(!hud_meters_load(NULL));assert(!hud_meters_load(directory));hud_meters_shutdown();assert(!hud_meters_load(""));
 char long_path[1200];memset(long_path,'x',1199);long_path[1199]=0;hud_meters_shutdown();assert(!hud_meters_load(long_path));
 unlink(filename);failed();assert(!mkdir(filename,0700));failed();assert(!rmdir(filename));assert(!mkfifo(filename,0600));failed();assert(!unlink(filename));
 write_file(FILE_BYTES);load();unsigned a=allocations,o=opens,r=reads;assert(hud_meters_load(NULL)&&allocations==a&&opens==o&&reads==r);hud_meters_shutdown();
 for(unsigned j=0;j<112;j++){raw[j]^=1;write_file(FILE_BYTES);failed();raw[j]^=1;}
 for(unsigned j=0;j<4;j++){unsigned offsets[]={112,4336,56176,177008};raw[offsets[j]]^=1;write_file(FILE_BYTES);failed();raw[offsets[j]]^=1;}
 for(unsigned section=0;section<3;section++)for(unsigned alpha=0;alpha<255;alpha++){
  unsigned offsets[]={115,4339,56179},off=offsets[section];raw[off]=alpha;rehash();write_file(FILE_BYTES);failed();raw[off]=255;
 }
 rehash();for(unsigned endpoint=0;endpoint<2;endpoint++)for(unsigned value=944;value<=65535;value+=64591){
  unsigned o=177008+2*(endpoint?222455:0);uint8_t lo=raw[o],hi=raw[o+1];raw[o]=value;raw[o+1]=value>>8;rehash();write_file(FILE_BYTES);failed();raw[o]=lo;raw[o+1]=hi;
 }
 rehash();write_file(FILE_BYTES-1);failed();size_override=FILE_BYTES;failed();size_override=-1;
 write_file(FILE_BYTES);FILE *f=fopen(filename,"ab");assert(f&&fputc(0,f)==0&&!fclose(f));failed();size_override=FILE_BYTES;failed();size_override=-1;
 write_file(FILE_BYTES);fail_alloc=1;failed();fail_alloc=0;fail_stat=1;failed();fail_stat=0;fail_close=1;failed();fail_close=0;
 for(int j=1;j<=3;j++){fail_read=j;failed();}fail_read=0;load();
}
static void paint(unsigned kind,unsigned a,unsigned b){
 unsigned box=kind<2?kind:kind==2?2:3;
 for(int y=boxes[box][1];y<boxes[box][3];y++)for(int x=boxes[box][0];x<boxes[box][2];x++){
  if(kind<2)screen[y*320+x]=x-289<2*(int)a?116+(x-289)/2:0;
  else if(kind==2){int lo=102-(int)(a>b?a:b),hi=103-(int)(a<b?a:b);if(y>=lo&&y<=hi)screen[y*320+x]=b>a?113+b/7:0;}
  else if(kind==3){if(y<=194-2*(int)a)screen[y*320+x]=0;}
  else if(y>=193-2*(int)a){int z=(194-y)/2;screen[y*320+x]=226+(z<3?0:(z-1)/2);}
 }
}
static void event(unsigned kind,unsigned a,unsigned b){hud_meters_write_begin(kind,a,b);paint(kind,a,b);assert(hud_meters_write_end(kind,screen,320));}
static void history(void){
 reset_screen();assert(hud_meters_palette_matches(test_palette));
 for(unsigned i=0;i<256;i++){test_palette[i]^=1;assert(!hud_meters_palette_matches(test_palette));test_palette[i]^=1;test_palette[i]^=0xff000000;assert(hud_meters_palette_matches(test_palette));}assert(!hud_meters_palette_matches(NULL));
 for(unsigned field=0;field<2;field++)for(unsigned p=0;p<12;p++)for(unsigned q=0;q<12;q++){reset_screen();event(field,p,0);event(field,q,0);assert(hud_meters_prepare(screen,320)==60);pairs++;}
 for(unsigned p=0;p<=90;p++)for(unsigned q=0;q<=90;q++){reset_screen();if(p)event(2,0,p);if(p!=q)event(2,p,q);assert(hud_meters_prepare(screen,320)==60);pairs++;}
 for(unsigned p=0;p<=28;p++)for(unsigned q=0;q<=28;q++){
  reset_screen();event(4,p,0);event(4,q,0);assert(hud_meters_prepare(screen,320)==60);unsigned top=193-2*(p>q?p:q);assert(screen[top*320+307]);
  event(3,q,0);assert(hud_meters_prepare(screen,320)==60);event(4,q,0);assert(hud_meters_prepare(screen,320)==60);pairs++;
 }
 reset_screen();event(2,0,45);unsigned occupied=0;for(unsigned y=12;y<104;y++)occupied+=screen[y*320+269]!=0;assert(occupied==47&&generator[45]==119);
 reset_screen();event(2,0,90);event(2,90,45);occupied=0;for(unsigned y=12;y<104;y++)occupied+=screen[y*320+269]!=0;assert(occupied==45&&screen[59*320+269]==125);
 reset_screen();event(0,11,0);hud_meters_write_begin(0,12,0);paint(0,11,0);assert(!hud_meters_write_end(0,screen,320));assert(!(hud_meters_prepare(screen,320)&4));event(0,1,0);assert(hud_meters_prepare(screen,320)==60);
 hud_meters_write_begin(2,91,45);assert(!hud_meters_write_end(2,screen,320));hud_meters_write_begin(2,45,46);paint(2,45,46);assert(!hud_meters_write_end(2,screen,320));event(2,0,90);assert(hud_meters_prepare(screen,320)==60);
 hud_meters_write_begin(3,UINT_MAX,0);assert(!hud_meters_write_end(3,screen,320));event(4,28,0);event(3,0,0);assert(hud_meters_prepare(screen,320)==60);for(int y=137;y<195;y++)assert(!screen[y*320+307]);
 event(4,0,0);assert(screen[193*320+307]==226);event(4,20,0);event(4,1,0);assert(screen[153*320+307]);
 hud_meters_write_begin(0,1,0);hud_meters_write_begin(1,2,0);assert(!hud_meters_write_end(1,screen,320));assert(!(hud_meters_prepare(screen,320)&12));
 reset_screen();hud_meters_write_begin(0,1,0);assert(!hud_meters_write_end(1,screen,320));assert(!(hud_meters_prepare(screen,320)&12));
}
static void mismatch(void){
 for(unsigned k=0;k<4;k++)for(int y=boxes[k][1];y<boxes[k][3];y++)for(int x=boxes[k][0];x<boxes[k][2];x++){
  reset_screen();event(0,6,0);event(1,6,0);event(2,0,45);event(4,10,0);
  screen[y*320+x]^=1;assert(hud_meters_prepare(screen,320)==(60u&~(4u<<k)));screen[y*320+x]^=1;assert(!(hud_meters_prepare(screen,320)&(4u<<k)));
  if(k<2)event(k,6,0);else if(k==2)event(2,0,90);else event(4,28,0);assert(hud_meters_prepare(screen,320)==60);mutations++;
 }
 reset_screen();event(0,2,0);paint(0,3,0);assert(!(hud_meters_prepare(screen,320)&4));
 reset_screen();event(2,0,90);screen[100*320+269]=0;hud_meters_write_begin(2,90,89);paint(2,90,89);assert(!hud_meters_write_end(2,screen,320));
 reset_screen();memset(padded,99,sizeof(padded));for(int y=0;y<200;y++)memcpy(padded+y*337,pristine+y*320,320);assert(hud_meters_capture(padded,337));
 assert(!hud_meters_capture(NULL,320));assert(!hud_meters_ready());assert(!hud_meters_capture(pristine,319));reset_screen();
 for(unsigned k=0;k<4;k++)for(int y=boxes[k][1];y<boxes[k][3];y++)for(int x=boxes[k][0];x<boxes[k][2];x++){
  pristine[y*320+x]=1;test_pins[0]=reference_hash(pristine,64000);assert(!hud_meters_capture(pristine,320));pristine[y*320+x]=0;
 }test_pins[0]=reference_hash(pristine,64000);reset_screen();
}
static unsigned ref_lookup[13][93],ref_armor[14][7];
static void check_samples(unsigned k){
 size_t offset[92][4];unsigned limit=boxes[k][3]-boxes[k][1];
 if(k>=2){uint8_t *rows=k==2?generator:armor;for(unsigned top=0;top<limit;){unsigned end=top+1;while(end<limit&&rows[end]==rows[top])end++;unsigned h=end-top,i=rows[top];
  for(unsigned y=top;i&&y<end;y++)for(unsigned cy=0;cy<4;cy++){
   if(k==2){unsigned entry=ref_lookup[i-113][h]+4*(y-top)+cy;unsigned id=raw[177008+2*entry]|raw[177009+2*entry]<<8;offset[y][cy]=56064+id*128;}
   else offset[y][cy]=4224+ref_armor[i-226][h]+((y-top)*4+cy)*144;
  }top=end;}}
 for(int d=4;d<=8;d+=4)for(int y=boxes[k][1];y<boxes[k][3];y++)for(int x=boxes[k][0];x<boxes[k][2];x++)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){
  uint8_t index=screen[y*320+x];const uint8_t *p=hud_meters_sample(x,y,sx,sy,d,index);if(!index){assert(!p);continue;}
  unsigned dx=x-boxes[k][0],dy=y-boxes[k][1],cx=sx/(d/4),cy=sy/(d/4);
  size_t o=k<2?(dx/2)*384+4*((dy*4+cy)*8+(dx%2)*4+cx):offset[dy][cy]+4*(dx*4+cx);assert(p&&!memcmp(p,raw+112+o,4));
 }
}
static void sampling(void){
 unsigned offset=0;for(unsigned role=0;role<13;role++)for(unsigned h=1;h<=92;h++){ref_lookup[role][h]=offset;offset+=4*h;}assert(offset==222456);
 offset=0;for(unsigned role=0;role<14;role++)for(unsigned h=2;h<=(role?4:6);h+=2){ref_armor[role][h]=offset;offset+=h*576;}assert(offset==51840);
 for(unsigned p=0;p<12;p++){reset_screen();event(0,p,0);event(1,p,0);hud_meters_prepare(screen,320);check_samples(0);check_samples(1);}
 for(unsigned a=0;a<=28;a++){reset_screen();event(4,a,0);hud_meters_prepare(screen,320);check_samples(3);}
 /* Sampler-only direct synthetic states: not claims about writer provenance. */
 for(unsigned i=113;i<=125;i++)for(unsigned h=1;h<=92;h++){
  reset_screen();for(unsigned y=0;y<92;y++){generator[y]=y<h?i:0;memset(screen+(y+12)*320+269,generator[y],8);}stamped|=16;
  assert(hud_meters_prepare(screen,320)&16);check_samples(2);
 }
 reset_screen();event(0,1,0);hud_meters_prepare(screen,320);
 for(int d=-1;d<=9;d++)if(d!=4&&d!=8)assert(!hud_meters_sample(289,17,0,0,d,116));
 assert(!hud_meters_sample(289,17,-1,0,4,116)&&!hud_meters_sample(289,17,0,4,4,116)&&!hud_meters_sample(289,17,0,0,4,117));
 for(int y=-1;y<=200;y++)for(int x=-1;x<=320;x++)if(x<289||x>=291||y<17||y>=20)assert(!hud_meters_sample(x,y,0,0,4,116));
}
int main(int argc,char **argv){assert(argc==2);directory=argv[1];assert(snprintf(filename,sizeof(filename),"%s/gameplay-hud-meters-v2.hda",directory)>0);fixture();parser();
 unsigned a=allocations,o=opens,r=reads,s=stats,c=closes;history();mismatch();sampling();assert(a==allocations&&o==opens&&r==reads&&s==stats&&c==closes);
 hud_meters_shutdown();assert(!allocation&&descriptor==-1&&frees<=allocations);assert(!hud_meters_prepare(screen,320));
 printf("PASS HUM2 parser=%u, transitions=%u, whole-field mutations=%u, all1196 materials/density4+8; no runtime allocation/I/O.\n",cases,pairs,mutations);return 0;}
