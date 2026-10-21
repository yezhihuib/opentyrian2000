/* SPDX-License-Identifier: GPL-2.0-or-later
 * Differential IO test. Frozen legacy adapters are extracted by the runner
 * from the pre-refactor commit, not reimplemented to match the new helper.
 * Mock IO checks error/short-read/close behavior, never grants rendering roles.
 */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <limits.h>
#include "global_asset_registry.h"
typedef uint8_t Uint8; typedef uint32_t Uint32;
static unsigned checks,cases;
#define CHECK(x) do { ++checks; if(!(x)){fprintf(stderr,"assertion failed at %d: %s\n",__LINE__,#x);abort();} } while(0)
static uint64_t independent_hash(const void *pv,size_t n)
{const unsigned char *p=pv;uint64_t h=UINT64_C(14695981039346656037);while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
static uint32_t old_u32(const unsigned char *p)
{return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
struct Mock {
 unsigned char *bytes; size_t size,at; long stated_size;
 int open_fail,stat_fail,regular,header_short,tail_error,close_error,malloc_fail;
 size_t chunk; int payload_fail;
 unsigned opens,stats,reads,closes,allocations; uint64_t events;
};
static struct Mock io;
static void event(unsigned op,size_t n){io.events=(io.events^op)*UINT64_C(1099511628211);io.events=(io.events^n)*UINT64_C(1099511628211);}
static int mock_open(const char *p){(void)p;++io.opens;event(1,0);return io.open_fail?-1:7;}
static FILE *mock_fopen(const char *p,const char *mode){(void)mode;return mock_open(p)<0?NULL:(FILE*)&io;}
struct FakeStat {unsigned st_mode;long st_size;};
static int mock_stat(int fd,struct FakeStat *s){CHECK(fd==7);++io.stats;event(2,0);s->st_mode=io.regular;s->st_size=io.stated_size;return io.stat_fail;}
static int mock_read(int fd,void *out,size_t n)
{
 CHECK(fd==7);++io.reads;event(3,n);
 if(io.at==0&&n==28&&io.header_short)n=(size_t)io.header_short-1;
 else if(io.at>=28&&n>1){if(io.payload_fail)return io.payload_fail==1?-1:0;if(io.chunk&&n>io.chunk)n=io.chunk;}
 if(io.at>=io.size)return n==1&&io.tail_error?-1:0;
 if(n>io.size-io.at)n=io.size-io.at;
 memcpy(out,io.bytes+io.at,n);io.at+=n;return (int)n;
}
static size_t mock_fread(void *out,size_t size,size_t n,FILE *f)
{CHECK(f==(FILE*)&io);CHECK(size==1);int got=mock_read(7,out,n);return got<0?0:(size_t)got;}
static int mock_fgetc(FILE *f){unsigned char b;CHECK(f==(FILE*)&io);int n=mock_read(7,&b,1);return n==1?b:EOF;}
static int mock_close(int fd){CHECK(fd==7);++io.closes;event(4,0);return io.close_error;}
static int mock_fclose(FILE *f){CHECK(f==(FILE*)&io);return mock_close(7);}
static void *mock_malloc(size_t n){++io.allocations;event(5,n);return io.malloc_fail?NULL:malloc(n);}
#define fopen mock_fopen
#define fread mock_fread
#define fgetc mock_fgetc
#define fclose mock_fclose
#define malloc mock_malloc
#define SF_OPEN mock_open
#define SF_FSTAT mock_stat
#define SF_STAT struct FakeStat
#define SF_REGULAR(m) ((m)==1)
#define SF_READ mock_read
#define SF_CLOSE mock_close
#include "shared_asset_reader.h"
#include "shared_asset_fd_reader.inc"
#include "shared_asset_reader_legacy.inc"
#undef fopen
#undef fread
#undef fgetc
#undef fclose
#undef malloc
struct Outcome {bool accepted;uint64_t hash,events;unsigned opens,stats,reads,closes,allocations;size_t at;};
static struct Outcome run(const GlobalAssetResource *r,struct Mock initial,int mode,bool old)
{
 io=initial;io.at=0;io.opens=io.stats=io.reads=io.closes=io.allocations=0;io.events=0;
 Uint8 *p;
 if(mode==0)p=old?legacy_stdio(r):shared_asset_load_stdio("mock",r);
 else if(mode==1)p=old?legacy_ship(r):shared_asset_load_fd("mock",r,true);
 else p=old?legacy_projectile(r):shared_asset_load_fd("mock",r,false);
 struct Outcome out={0};out.accepted=p!=NULL;out.hash=p?independent_hash(p,r->bytes-28u):0;out.events=io.events;out.opens=io.opens;out.stats=io.stats;out.reads=io.reads;out.closes=io.closes;out.allocations=io.allocations;out.at=io.at;
 free(p);return out;
}
static void compare(const GlobalAssetResource *r,struct Mock in,int mode,int expected)
{
 ++cases;struct Outcome a=run(r,in,mode,true),b=run(r,in,mode,false);
 CHECK(a.accepted==b.accepted);CHECK(a.hash==b.hash);CHECK(a.events==b.events);CHECK(a.opens==b.opens);CHECK(a.stats==b.stats);CHECK(a.reads==b.reads);CHECK(a.closes==b.closes);CHECK(a.allocations==b.allocations);CHECK(a.at==b.at);
 if(expected>=0)CHECK(b.accepted==(expected!=0));
}
static void exercise(const GlobalAssetResource *r,unsigned char *data,int mode)
{
 struct Mock m={0};m.bytes=data;m.size=r->bytes;m.stated_size=r->bytes;m.regular=1;
 compare(r,m,mode,1);
 struct Mock x=m;x.open_fail=1;compare(r,x,mode,0);
 x=m;x.stat_fail=1;compare(r,x,mode,mode==0);
 x=m;x.regular=0;compare(r,x,mode,mode==0);
 x=m;x.stated_size--;compare(r,x,mode,mode==0);
 x=m;x.stated_size++;compare(r,x,mode,mode==0);
 x=m;x.close_error=-1;compare(r,x,mode,mode!=1);
 x=m;x.tail_error=1;compare(r,x,mode,mode==0);
 x=m;x.malloc_fail=1;compare(r,x,mode,0);
 for(int shortn=1;shortn<=28;shortn++){x=m;x.header_short=shortn;compare(r,x,mode,0);}
 for(unsigned i=0;i<28;i++){data[i]^=0x01;compare(r,m,mode,0);data[i]^=0x01;}
 const unsigned truncate[]={0,1,3,4,12,27,28,29,100};
 for(unsigned i=0;i<sizeof(truncate)/sizeof(*truncate);i++){x=m;x.size=truncate[i];compare(r,x,mode,0);}
 x=m;x.size--;compare(r,x,mode,0);
 x=m;x.size++;data[r->bytes]=0xa5;compare(r,x,mode,0);
 const size_t chunks[]={1,17,1024,43007};
 for(unsigned i=0;i<sizeof(chunks)/sizeof(*chunks);i++){x=m;x.chunk=chunks[i];compare(r,x,mode,mode!=0||chunks[i]>=r->bytes-28u);}
 for(int e=1;e<=2;e++){x=m;x.payload_fail=e;compare(r,x,mode,0);}
 data[28]^=0xff;compare(r,m,mode,0);data[28]^=0xff;
 data[r->bytes-1]^=0xff;compare(r,m,mode,0);data[r->bytes-1]^=0xff;
 GlobalAssetResource bad=*r;bad.payload_fnv^=1;compare(&bad,m,mode,0);
}
int main(int argc,char **argv)
{
 CHECK(argc==2);unsigned assets=0;
 for(unsigned i=0;i<GLOBAL_ASSET_RESOURCE_COUNT;i++){
  const GlobalAssetResource *r=&global_asset_resources[i];char path[2048];int n=snprintf(path,sizeof(path),"%s/%s",argv[1],r->path);CHECK(n>0&&n<(int)sizeof(path));
  FILE *f=fopen(path,"rb");CHECK(f);unsigned char *data=malloc((size_t)r->bytes+1);CHECK(data);CHECK(fread(data,1,r->bytes,f)==r->bytes);CHECK(fgetc(f)==EOF);CHECK(fclose(f)==0);
  exercise(r,data,0);assets++;
  if(r->identity==90233)exercise(r,data,1);
  if(r->identity==80058||r->identity==80059||r->identity==80060||r->identity==80062||r->identity==80165||r->identity==80067||r->identity==80070)exercise(r,data,2);
  free(data);
 }
 printf("PASS shared reader differential: %u assets, %u cases, %u checks\n",assets,cases,checks);return 0;
}
