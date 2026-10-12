/* Bounded HUM2 V2 coarse materials. Indexed original display remains authority. */
#include "gameplay_hud_meters.h"
#include <fcntl.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#if defined(TARGET_WIN32) || defined(_WIN32)
#include <io.h>
#define HUM_OPEN(p) _open(p,_O_RDONLY|_O_BINARY|_O_NOINHERIT)
#define HUM_READ _read
#define HUM_CLOSE _close
#define HUM_FSTAT _fstat
#define HUM_STAT struct _stat
#define HUM_REGULAR(m) (((m)&_S_IFMT)==_S_IFREG)
#else
#include <unistd.h>
#define HUM_OPEN(p) open(p,O_RDONLY|O_NONBLOCK)
#define HUM_READ read
#define HUM_CLOSE close
#define HUM_FSTAT fstat
#define HUM_STAT struct stat
#define HUM_REGULAR(m) S_ISREG(m)
#endif
#ifndef HUD_METERS_PIC_FNV
#define HUD_METERS_PIC_FNV UINT64_C(0x14c1441f3d5dc0e2)
#endif
#ifndef HUD_METERS_PALETTE_FNV
#define HUD_METERS_PALETTE_FNV UINT64_C(0x5e80e83992be2927)
#endif
#ifndef HUD_METERS_FIRE_FNV
#define HUD_METERS_FIRE_FNV UINT64_C(0x92ce2a65c65f67db)
#endif
#ifndef HUD_METERS_ARMOR_FNV
#define HUD_METERS_ARMOR_FNV UINT64_C(0x33f13810daec0125)
#endif
#ifndef HUD_METERS_ROWS_FNV
#define HUD_METERS_ROWS_FNV UINT64_C(0xc4231771a5413868)
#endif
#ifndef HUD_METERS_LOOKUP_FNV
#define HUD_METERS_LOOKUP_FNV UINT64_C(0x1d129d23c2edc134)
#endif
#ifndef HUD_METERS_PAYLOAD_FNV
#define HUD_METERS_PAYLOAD_FNV UINT64_C(0xfcc77c108870c9db)
#endif
enum { HEADER=112,FIRE_BYTES=4224,ARMOR_BYTES=51840,ROW_BYTES=120832,
       LOOKUP_BYTES=444912,ARMOR_OFFSET=4224,ROW_OFFSET=56064,
       LOOKUP_OFFSET=176896,PAYLOAD=621808,FILE_BYTES=621920 };
static uint8_t *payload;
static bool attempted,captured;
static unsigned stamped,prepared;
static uint8_t fire[2],generator[92],armor[58];
static uint32_t generator_rows[92],armor_rows[58];
static struct { bool active,eligible; unsigned kind,a,b; } pending;
static const int boxes[4][4]={{289,17,311,20},{289,38,311,41},
                            {269,12,277,104},{307,137,316,195}};
static uint32_t u32(const uint8_t *p)
{return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t u64(const uint8_t *p)
{return (uint64_t)u32(p)|((uint64_t)u32(p+4)<<32);}
static uint64_t update(uint64_t h,const uint8_t *p,size_t n)
{for(size_t i=0;i<n;i++)h=(h^p[i])*UINT64_C(1099511628211);return h;}
static uint64_t hash(const uint8_t *p,size_t n)
{return update(UINT64_C(14695981039346656037),p,n);}
static bool source_valid(const uint8_t *p,int pitch)
{return p&&pitch>=320&&(size_t)pitch<=(SIZE_MAX-320)/199;}
static bool header_valid(const uint8_t *h)
{
 static const uint32_t fixed[]={2,112,4,320,200,4224,51840,120832,444912,944,222456};
 const uint64_t pins[]={HUD_METERS_PIC_FNV,HUD_METERS_PALETTE_FNV,
  HUD_METERS_FIRE_FNV,HUD_METERS_ARMOR_FNV,HUD_METERS_ROWS_FNV,
  HUD_METERS_LOOKUP_FNV,HUD_METERS_PAYLOAD_FNV,0};
 if(memcmp(h,"HUM2",4))return false;
 for(unsigned i=0;i<11;i++)if(u32(h+4+4*i)!=fixed[i])return false;
 for(unsigned i=0;i<8;i++)if(u64(h+48+8*i)!=pins[i])return false;
 return true;
}
static bool payload_valid(const uint8_t *p)
{
 if(hash(p,FIRE_BYTES)!=HUD_METERS_FIRE_FNV||
    hash(p+ARMOR_OFFSET,ARMOR_BYTES)!=HUD_METERS_ARMOR_FNV||
    hash(p+ROW_OFFSET,ROW_BYTES)!=HUD_METERS_ROWS_FNV||
    hash(p+LOOKUP_OFFSET,LOOKUP_BYTES)!=HUD_METERS_LOOKUP_FNV||
    hash(p,PAYLOAD)!=HUD_METERS_PAYLOAD_FNV)return false;
 for(size_t i=3;i<LOOKUP_OFFSET;i+=4)if(p[i]!=255)return false;
 for(size_t i=LOOKUP_OFFSET;i<PAYLOAD;i+=2)
  if(((unsigned)p[i]|((unsigned)p[i+1]<<8))>=944)return false;
 return true;
}
bool hud_meters_load(const char *directory)
{
 char path[1024];uint8_t h[HEADER],extra,*data=NULL;HUM_STAT st;
 bool valid=false;int length,fd;
 if(attempted)return payload!=NULL;
 attempted=true;
 if(!directory||!*directory)return false;
 length=snprintf(path,sizeof(path),"%s/gameplay-hud-meters-v2.hda",directory);
 if(length<0||(size_t)length>=sizeof(path))return false;
 fd=HUM_OPEN(path);if(fd<0)return false;
 if(HUM_FSTAT(fd,&st)||!HUM_REGULAR(st.st_mode)||st.st_size!=FILE_BYTES||
    HUM_READ(fd,h,HEADER)!=HEADER||!header_valid(h))goto done;
 data=malloc(PAYLOAD);
 if(!data||HUM_READ(fd,data,PAYLOAD)!=PAYLOAD||HUM_READ(fd,&extra,1)!=0)goto done;
 valid=payload_valid(data);
 done:
 if(HUM_CLOSE(fd))valid=false;
 if(!valid){free(data);return false;}
 payload=data;return true;
}
void hud_meters_forget_source(void)
{
 captured=false;stamped=prepared=0;memset(&pending,0,sizeof(pending));
 memset(fire,0,sizeof(fire));memset(generator,0,sizeof(generator));memset(armor,0,sizeof(armor));
 memset(generator_rows,0,sizeof(generator_rows));memset(armor_rows,0,sizeof(armor_rows));
}
void hud_meters_shutdown(void)
{hud_meters_forget_source();free(payload);payload=NULL;attempted=false;}
bool hud_meters_ready(void){return payload&&captured;}
bool hud_meters_capture(const uint8_t *p,int pitch)
{
 uint64_t h=UINT64_C(14695981039346656037);
 hud_meters_forget_source();if(!payload||!source_valid(p,pitch))return false;
 for(int y=0;y<200;y++)h=update(h,p+(size_t)y*pitch,320);
 if(h!=HUD_METERS_PIC_FNV)return false;
 for(unsigned k=0;k<4;k++)for(int y=boxes[k][1];y<boxes[k][3];y++)
  for(int x=boxes[k][0];x<boxes[k][2];x++)if(p[(size_t)y*pitch+x])return false;
 captured=true;stamped=HUD_METERS_ALL;return true;
}
bool hud_meters_palette_matches(const uint32_t palette[256])
{
 uint64_t h=UINT64_C(14695981039346656037);
 if(!payload||!palette)return false;
 for(unsigned i=0;i<256;i++){
  uint8_t rgb[3]={(uint8_t)(palette[i]>>16),(uint8_t)(palette[i]>>8),(uint8_t)palette[i]};
  h=update(h,rgb,3);
 }
 return h==HUD_METERS_PALETTE_FNV;
}
unsigned hud_meters_event_bits(unsigned kind)
{
 switch(kind){case HUD_WRITE_FRONT:return HUD_METER_FRONT;case HUD_WRITE_REAR:return HUD_METER_REAR;
 case HUD_WRITE_GENERATOR:return HUD_METER_GENERATOR;
 case HUD_WRITE_ARMOR_WIPE:case HUD_WRITE_ARMOR_DRAW:return HUD_METER_ARMOR;default:return 0;}
}
void hud_meters_revoke(unsigned bits)
{
 stamped&=~bits;prepared&=~bits;
 if(pending.active&&(hud_meters_event_bits(pending.kind)&bits))pending.active=false;
}
void hud_meters_write_begin(unsigned kind,unsigned a,unsigned b)
{
 unsigned bits=hud_meters_event_bits(kind);bool valid=false,full=false;
 if(pending.active){unsigned previous=hud_meters_event_bits(pending.kind);pending.active=false;hud_meters_revoke(bits|previous);return;}
 if(!bits){hud_meters_revoke(HUD_METERS_ALL);return;}
 if(kind==HUD_WRITE_FRONT||kind==HUD_WRITE_REAR){valid=a<=11;full=valid;}
 else if(kind==HUD_WRITE_GENERATOR){valid=a<=90&&b<=90&&a!=b;full=valid&&((a==0&&b==90)||(a==90&&b==0));}
 else {valid=a<=28;full=valid&&((kind==HUD_WRITE_ARMOR_WIPE&&a==0)||(kind==HUD_WRITE_ARMOR_DRAW&&a==28));}
 pending.kind=kind;pending.a=a;pending.b=b;
 pending.eligible=hud_meters_ready()&&valid&&(full||(stamped&bits)!=0);
 pending.active=true;stamped&=~bits;prepared&=~bits;
}
static uint8_t armor_value(int y)
{int z=(194-y)/2;return (uint8_t)(226+(z>1?(z-1)/2:0));}
static uint8_t fire_value(unsigned p,int x)
{return x/2<(int)p?(uint8_t)(116+x/2):0;}
bool hud_meters_write_end(unsigned kind,const uint8_t *p,int pitch)
{
 unsigned bits=hud_meters_event_bits(kind),a=pending.a,b=pending.b;
 if(!pending.active||pending.kind!=kind){unsigned other=pending.active?hud_meters_event_bits(pending.kind):0;pending.active=false;hud_meters_revoke(bits|other);return false;}
 pending.active=false;
 if(!pending.eligible||!hud_meters_ready()||!source_valid(p,pitch))return false;
 unsigned box=(kind<=HUD_WRITE_REAR)?kind:kind==HUD_WRITE_GENERATOR?2:3;
 int start=0,end=0;uint8_t color=0;
 if(kind==HUD_WRITE_GENERATOR){start=102-(int)(a>b?a:b);end=104-(int)(a<b?a:b);color=b>a?(uint8_t)(113+b/7):0;}
 for(int y=boxes[box][1];y<boxes[box][3];y++){
  uint8_t expected=0;
  if(kind==HUD_WRITE_GENERATOR)expected=y>=start&&y<end?color:generator[y-12];
  else if(kind==HUD_WRITE_ARMOR_WIPE)expected=y<195-2*(int)a?0:armor[y-137];
  else if(kind==HUD_WRITE_ARMOR_DRAW)expected=y>=193-2*(int)a?armor_value(y):armor[y-137];
  for(int x=boxes[box][0];x<boxes[box][2];x++)
   if(p[(size_t)y*pitch+x]!=(box<2?fire_value(a,x-289):expected))return false;
 }
 if(box<2)fire[box]=(uint8_t)a;
 else for(int y=boxes[box][1];y<boxes[box][3];y++)
  (box==2?generator:armor)[y-boxes[box][1]]=p[(size_t)y*pitch+boxes[box][0]];
 stamped|=bits;return true;
}
static bool armor_shape(void)
{
 int top=0;while(top<58&&!armor[top])top++;
 if(top==58)return true;
 if((58-top)%2)return false;
 for(int y=top;y<58;y++)if(armor[y]!=armor_value(y+137))return false;
 return true;
}
unsigned hud_meters_prepare(const uint8_t *p,int pitch)
{
 prepared=0;if(!hud_meters_ready()||!source_valid(p,pitch)){hud_meters_revoke(HUD_METERS_ALL);return 0;}
 for(unsigned box=0;box<4;box++){
  unsigned bits=4u<<box;bool valid=(stamped&bits)!=0;
  if(!valid)continue;
  if(box==3&&!armor_shape())valid=false;
  for(int y=boxes[box][1];valid&&y<boxes[box][3];y++){
   uint8_t value=box==2?generator[y-12]:box==3?armor[y-137]:0;
   if(box==2&&value&&(value<113||value>125)){valid=false;break;}
   for(int x=boxes[box][0];x<boxes[box][2];x++)
    if(p[(size_t)y*pitch+x]!=(box<2?fire_value(fire[box],x-289):value)){valid=false;break;}
  }
  if(!valid){hud_meters_revoke(bits);continue;}
  if(box>=2){
   const uint8_t *rows=box==2?generator:armor;unsigned n=box==2?92:58;
   for(unsigned y=0;y<n;){
    unsigned end=y+1;while(end<n&&rows[end]==rows[y])end++;
    unsigned h=end-y,i=rows[y];uint32_t base=0;
    if(i){
     if(box==2)base=(i-113)*17112+2*h*(h-1);
     else if(i==226&&(h==2||h==4||h==6))base=h==2?0:h==4?1152:3456;
     else if(i>=227&&i<=239&&(h==2||h==4))base=6912+3456*(i-227)+(h==4?1152:0);
     else {valid=false;break;}
    }
    for(unsigned r=y;r<end;r++)if(box==2)generator_rows[r]=base+4*(r-y);else armor_rows[r]=base+576*(r-y);
    y=end;
   }
  }
  if(valid)prepared|=bits;else hud_meters_revoke(bits);
 }
 return prepared;
}
const uint8_t *hud_meters_sample(int x,int y,int sx,int sy,int density,uint8_t index)
{
 if(!hud_meters_ready()||!index||(density!=4&&density!=8)||sx<0||sy<0||sx>=density||sy>=density)return NULL;
 unsigned box;for(box=0;box<4;box++)if(x>=boxes[box][0]&&x<boxes[box][2]&&y>=boxes[box][1]&&y<boxes[box][3])break;
 if(box==4||!(prepared&(4u<<box)))return NULL;
 unsigned dx=(unsigned)(x-boxes[box][0]),dy=(unsigned)(y-boxes[box][1]);
 unsigned cx=(unsigned)sx/(unsigned)(density/4),cy=(unsigned)sy/(unsigned)(density/4);
 size_t offset;
 if(box<2){
  if(index!=fire_value(fire[box],(int)dx))return NULL;
  offset=(dx/2)*384+4*((dy*4+cy)*8+(dx%2)*4+cx);if(offset+4>FIRE_BYTES)return NULL;
 }else if(box==2){
  if(index!=generator[dy])return NULL;
  size_t entry=(size_t)generator_rows[dy]+cy;if(entry>=222456)return NULL;
  const uint8_t *id=payload+LOOKUP_OFFSET+2*entry;
  unsigned row=(unsigned)id[0]|((unsigned)id[1]<<8);if(row>=944)return NULL;
  offset=ROW_OFFSET+(size_t)row*128+4*(dx*4+cx);
 }else{
  if(index!=armor[dy])return NULL;
  offset=ARMOR_OFFSET+(size_t)armor_rows[dy]+cy*144+4*(dx*4+cx);if(offset+4>ROW_OFFSET)return NULL;
 }
 return payload+offset;
}
