/* SPDX-License-Identifier: GPL-2.0-or-later
 * Reconstructed RFR3 resource loader. Original NFR1 numeric bytes remain exact.
 * A family is atomic and independent; files cannot widen compiled contracts. */
#include "common_menu_runs.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <fcntl.h>
#include <sys/stat.h>
#if defined(_WIN32)
#include <io.h>
#define CR_OPEN(p) _open(p,_O_RDONLY|_O_BINARY|_O_NOINHERIT)
#define CR_READ _read
#define CR_CLOSE _close
#define CR_FSTAT _fstat
#define CR_STAT struct _stat
#define CR_REGULAR(m) (((m)&_S_IFMT)==_S_IFREG)
#else
#include <unistd.h>
#define CR_OPEN(p) open(p,O_RDONLY|O_NONBLOCK)
#define CR_READ read
#define CR_CLOSE close
#define CR_FSTAT fstat
#define CR_STAT struct stat
#define CR_REGULAR(m) S_ISREG(m)
#endif
#include "../assets/hd/shared-menu-runs-v1/reconstructed_run_specs.h"
#include "../assets/hd/shared-menu-runs-v1/reconstructed_numeric_specs.h"
#define CR_FNV UINT64_C(14695981039346656037)
enum { CR_COUNT=171,CR_FAMILY_MAX=113,CR_PAYLOAD_CAP=6*1024*1024 };
static char directory[1024];
static Uint8 *payload[CR_COUNT],*numeric_payload;
static struct {bool attempted,ready;uint64_t generation;} family[COMMON_MENU_FAMILY_COUNT],numeric;
static uint64_t generation_counter;
static uint64_t next_generation(void){if(++generation_counter==0)++generation_counter;return generation_counter;}
static uint64_t hash_more(uint64_t h,const void *v,size_t n){const Uint8 *p=v;while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
static uint32_t u32(const Uint8 *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t u64(const Uint8 *p){return u32(p)|((uint64_t)u32(p+4)<<32);}
static bool valid_family(enum CommonMenuFamily f){return (unsigned)f<COMMON_MENU_FAMILY_COUNT;}
static Uint8 *read_exact(const char *name,size_t length)
{
 char path[1200];CR_STAT st;Uint8 *b=NULL,extra;bool ok=false;
 if(!directory[0]||!name||strchr(name,'/')||strchr(name,'\\')||length>CR_PAYLOAD_CAP)return NULL;
 int n=snprintf(path,sizeof(path),"%s/%s",directory,name);if(n<0||(size_t)n>=sizeof(path))return NULL;
 int fd=CR_OPEN(path);if(fd<0)return NULL;
 if(CR_FSTAT(fd,&st)||!CR_REGULAR(st.st_mode)||st.st_size<0||(uint64_t)st.st_size!=length)goto done;
 b=malloc(length);if(!b)goto done;
 size_t at=0;while(at<length){long got=CR_READ(fd,b+at,length-at);if(got<=0)goto done;at+=(size_t)got;}
 if(CR_READ(fd,&extra,1)!=0)goto done;ok=true;
 done:if(CR_CLOSE(fd))ok=false;if(!ok){free(b);b=NULL;}return b;
}
void common_menu_runs_shutdown(enum CommonMenuFamily f)
{
 if(!valid_family(f))return;
 unsigned first=cmr3_family_first[f],count=cmr3_family_count[f];
 for(unsigned i=0;i<count;i++){free(payload[first+i]);payload[first+i]=NULL;}
 family[f].ready=family[f].attempted=false;family[f].generation=next_generation();
}
void common_menu_numeric_runs_shutdown(void)
{free(numeric_payload);numeric_payload=NULL;numeric.ready=numeric.attempted=false;numeric.generation=next_generation();}
void common_menu_runs_shutdown_all(void)
{for(unsigned i=0;i<COMMON_MENU_FAMILY_COUNT;i++)common_menu_runs_shutdown((enum CommonMenuFamily)i);common_menu_numeric_runs_shutdown();}
bool common_menu_runs_set_directory(const char *root)
{
 size_t n=root?strlen(root):0;
 if(n<sizeof(directory)&&((!n&&!directory[0])||(n&&!strcmp(root,directory))))return true;
 common_menu_runs_shutdown_all();directory[0]=0;
 if(n>=sizeof(directory))return false;if(n)memcpy(directory,root,n+1);return true;
}
static bool validate_run(const struct Cmr3Spec *s,const Uint8 *b,size_t length)
{
 size_t plane=(size_t)s->width*s->height;
 if(memcmp(b,"RFR3",4)||u32(b+4)!=3||u32(b+8)!=64||u32(b+12)!=s->width||u32(b+16)!=s->height||
    u32(b+20)!=(uint32_t)s->dx||u32(b+24)!=(uint32_t)s->dy||u32(b+28)!=s->advance256||
    u32(b+32)!=s->planes||u32(b+36)!=s->role_profile||u64(b+40)!=s->text_fnv64||
    u64(b+48)!=s->payload_fnv64||u64(b+56)!=s->font_prefix64||
    hash_more(CR_FNV,b,64)!=s->header_fnv64||hash_more(CR_FNV,b,length)!=s->file_fnv64||
    hash_more(CR_FNV,b+64,length-64)!=s->payload_fnv64)return false;
 const Uint8 *a=b+64,*r=a+plane,*stroke=s->planes==3?r+plane:NULL;bool ink=false;
 for(size_t n=0;n<plane;n++){
  if((!a[n]&&r[n])||(a[n]&&(r[n]<s->role_min||r[n]>s->role_max))||(stroke&&stroke[n]<a[n]))return false;
  ink|=a[n]!=0;
 }
 return ink;
}
bool common_menu_runs_load(enum CommonMenuFamily f)
{
 if(!valid_family(f)||!directory[0])return false;if(family[f].attempted)return family[f].ready;
 family[f].attempted=true;unsigned first=cmr3_family_first[f],count=cmr3_family_count[f];
 Uint8 *pending[CR_FAMILY_MAX]={0};size_t total=0;bool ok=false;
 if(count>CR_FAMILY_MAX||first>CR_COUNT||count>CR_COUNT-first)goto done;
 for(unsigned i=0;i<count;i++){
  const struct Cmr3Spec *s=&cmr3_specs[first+i];
  uint64_t bytes=(uint64_t)s->width*s->height*s->planes+64;
  if(s->family!=(unsigned)f||s->id!=i||!s->width||!s->height||(s->planes!=2&&s->planes!=3)||
     bytes>CR_PAYLOAD_CAP||total>CR_PAYLOAD_CAP-(size_t)bytes)goto done;
  total+=(size_t)bytes;pending[i]=read_exact(s->filename,(size_t)bytes);
  if(!pending[i]||!validate_run(s,pending[i],(size_t)bytes))goto done;
 }
 for(unsigned i=0;i<count;i++){payload[first+i]=pending[i];pending[i]=NULL;}ok=true;
 done:for(unsigned i=0;i<CR_FAMILY_MAX;i++)free(pending[i]);family[f].ready=ok;family[f].generation=next_generation();return ok;
}
bool common_menu_runs_ready(enum CommonMenuFamily f){return valid_family(f)&&family[f].ready;}
unsigned common_menu_runs_count(enum CommonMenuFamily f){return valid_family(f)?cmr3_family_count[f]:0;}
uint64_t common_menu_runs_generation(enum CommonMenuFamily f){return valid_family(f)?family[f].generation:0;}
bool common_menu_runs_get(enum CommonMenuFamily f,unsigned id,CommonMenuRun *out)
{
 if(!out||!common_menu_runs_ready(f)||id>=cmr3_family_count[f])return false;
 unsigned n=cmr3_family_first[f]+id;const struct Cmr3Spec *s=&cmr3_specs[n];size_t plane=(size_t)s->width*s->height;
 memset(out,0,sizeof(*out));out->dx=s->dx;out->dy=s->dy;out->width=out->pitch=s->width;out->height=s->height;
 out->advance256=s->advance256;out->text=s->text;out->role_min=s->role_min;out->role_max=s->role_max;
 out->alpha=payload[n]+64;out->roles=out->alpha+plane;out->stroke=s->planes==3?out->roles+plane:NULL;return true;
}
int common_menu_runs_find(enum CommonMenuFamily f,const char *text)
{
 if(!valid_family(f)||!text)return -1;
 for(unsigned i=0;i<cmr3_family_count[f];i++)if(!strcmp(cmr3_specs[cmr3_family_first[f]+i].text,text))return (int)i;
 return -1;
}
size_t common_menu_runs_retained_bytes(void)
{
 size_t n=sizeof(payload)+sizeof(family)+sizeof(directory)+sizeof(cmr3_specs)+sizeof(cmr3_family_first)+sizeof(cmr3_family_count);
 for(unsigned i=0;i<CR_COUNT;i++)if(payload[i])n+=64+(size_t)cmr3_specs[i].width*cmr3_specs[i].height*cmr3_specs[i].planes;
 return n;
}
/* Numeric implementation follows generated exact descriptor admission below. */
typedef char resource_sum_bound[(CMR3_TOTAL_FILE_BYTES+CMR_NUMERIC_FILE_BYTES+sizeof(cmr3_specs)+sizeof(cmr_numeric_masks)+sizeof(cmr_numeric_phases)<CR_PAYLOAD_CAP)?1:-1];
bool common_menu_numeric_runs_load(void)
{
 if(!directory[0])return false;if(numeric.attempted)return numeric.ready;numeric.attempted=true;
 Uint8 *b=read_exact("numeric-runs-v1.nfr",CMR_NUMERIC_FILE_BYTES);bool ok=false;
 if(!b)goto done;
 if(memcmp(b,"NFR1",4)||u32(b+4)!=1||u32(b+8)!=64||u32(b+12)!=12||u32(b+16)!=64||u32(b+20)!=64||
    u32(b+24)!=CMR_NUMERIC_PAYLOAD_BYTES||u32(b+28)||u64(b+32)!=CMR_NUMERIC_FONT_PREFIX64||
    u64(b+40)!=CMR_NUMERIC_PAYLOAD_FNV64||u64(b+48)||u64(b+56)||
    hash_more(CR_FNV,b,64)!=CMR_NUMERIC_HEADER_FNV64||
    hash_more(CR_FNV,b,CMR_NUMERIC_FILE_BYTES)!=CMR_NUMERIC_FILE_FNV64||
    hash_more(CR_FNV,b+64,CMR_NUMERIC_PAYLOAD_BYTES)!=CMR_NUMERIC_PAYLOAD_FNV64)goto done;
 size_t end=0;
 for(unsigned i=0;i<CMR_NUMERIC_MASK_COUNT;i++){
  const struct CmrNumericMask *m=&cmr_numeric_masks[i];size_t n=(size_t)m->width*m->height;
  if(!m->width||!m->height||m->offset!=end||n>CMR_NUMERIC_PAYLOAD_BYTES-end)goto done;
  end+=n;
 }
 if(end!=CMR_NUMERIC_PAYLOAD_BYTES)goto done;
 for(unsigned t=0;t<CMR_NUMERIC_TOKEN_COUNT;t++)for(unsigned phase=0;phase<64;phase++)
  if(cmr_numeric_phases[t][phase].mask>=CMR_NUMERIC_MASK_COUNT||cmr_numeric_advances64[t]<=0)goto done;
 numeric_payload=b;b=NULL;ok=true;
 done:free(b);numeric.ready=ok;numeric.generation=next_generation();return ok;
}
bool common_menu_numeric_runs_ready(void){return numeric.ready;}
uint64_t common_menu_numeric_runs_generation(void){return numeric.generation;}
static bool numeric_add(CommonMenuNumericRun *out,unsigned token,int *pen,int *minx,int *miny,int *maxx,int *maxy)
{
 if(out->count>=COMMON_MENU_NUMERIC_MAX_TOKENS||token>=CMR_NUMERIC_TOKEN_COUNT||*pen<0)return false;
 const struct CmrNumericPhase *p=&cmr_numeric_phases[token][(unsigned)*pen%64];
 const struct CmrNumericMask *m=&cmr_numeric_masks[p->mask];int x=*pen/64+p->x,y=p->y;
 CommonMenuNumericPlacement *place=&out->token[out->count++];place->mask=p->mask;place->x=x;place->y=y;
 if(x<*minx)*minx=x;if(y<*miny)*miny=y;
 if(x+(int)m->width>*maxx)*maxx=x+m->width;if(y+(int)m->height>*maxy)*maxy=y+m->height;
 if(*pen>INT_MAX-cmr_numeric_advances64[token])return false;*pen+=cmr_numeric_advances64[token];return true;
}
bool common_menu_numeric_runs_layout(const char *text,CommonMenuNumericRun *out)
{
 if(!out)return false;memset(out,0,sizeof(*out));if(!numeric.ready||!text)return false;
 size_t length=0;while(length<=20&&text[length])++length;if(!length||length>20)return false;
 unsigned at=0;int pen=0,minx=INT_MAX,miny=INT_MAX,maxx=INT_MIN,maxy=INT_MIN;bool prefix=false,negative=false;
 if(length>=6&&!memcmp(text,cmr_numeric_tokens[11],6)){
  if(!numeric_add(out,11,&pen,&minx,&miny,&maxx,&maxy))goto fail;at=6;prefix=true;
 }
 if(at<length&&text[at]=='-'){
  if(prefix||!numeric_add(out,10,&pen,&minx,&miny,&maxx,&maxy))goto fail;negative=true;++at;
 }
 if(at>=length||text[at]<'0'||text[at]>'9'||(text[at]=='0'&&(negative||at+1!=length)))goto fail;
 for(;at<length;at++)if(text[at]<'0'||text[at]>'9'||!numeric_add(out,(unsigned)(text[at]-'0'),&pen,&minx,&miny,&maxx,&maxy))goto fail;
 if(!out->count||maxx<=minx||maxy<=miny||pen>INT_MAX/4)goto fail;
 out->dx=minx;out->dy=miny;out->width=(unsigned)(maxx-minx);out->height=(unsigned)(maxy-miny);out->advance256=(unsigned)pen*4;return true;
 fail:memset(out,0,sizeof(*out));return false;
}
bool common_menu_numeric_runs_sample(const CommonMenuNumericRun *run,int x,int y,Uint8 *alpha,Uint8 *role)
{
 if(!alpha||!role)return false;*alpha=*role=0;
 if(!numeric.ready||!run||!run->count||run->count>COMMON_MENU_NUMERIC_MAX_TOKENS)return false;
 for(unsigned i=0;i<run->count;i++){
  const CommonMenuNumericPlacement *p=&run->token[i];if(p->mask>=CMR_NUMERIC_MASK_COUNT)return false;
  const struct CmrNumericMask *m=&cmr_numeric_masks[p->mask];
  int64_t sx=(int64_t)x-p->x,sy=(int64_t)y-p->y;
  if(sx<0||sy<0||sx>=m->width||sy>=m->height)continue;
  Uint8 a=numeric_payload[64+m->offset+(size_t)sy*m->width+(size_t)sx];
  /* Exact whole-string oracle proves disjoint nonzero token support. A forged
   * placement that violates that condition never invents a blending rule. */
  if(a&&*alpha){*alpha=*role=0;return false;}if(a){*alpha=a;*role=7;}
 }
 return true;
}
size_t common_menu_numeric_runs_retained_bytes(void)
{return sizeof(numeric)+sizeof(numeric_payload)+sizeof(cmr_numeric_masks)+sizeof(cmr_numeric_phases)+sizeof(cmr_numeric_tokens)+sizeof(cmr_numeric_advances64)+(numeric_payload?CMR_NUMERIC_FILE_BYTES:0);}
