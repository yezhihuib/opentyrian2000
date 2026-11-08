/* Test harness only: actual current public HDR1 readers; no game or scene authority. */
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
typedef uint8_t Uint8;
#define SF_OPEN(p) open((p),O_RDONLY)
#define SF_FSTAT fstat
#define SF_STAT struct stat
#define SF_REGULAR S_ISREG
#define SF_READ read
#define SF_CLOSE close
#include "shared_asset_reader.h"
#include "shared_asset_fd_reader.inc"
static unsigned checks,failures;
static void check(int ok,const char *what,unsigned i){checks++;if(!ok){failures++;fprintf(stderr,"FAIL row=%u %s\n",i,what);}}
static void expect(const char *path,const GlobalAssetResource *r,int accepted,const char *kind,unsigned i){
 uint8_t *a=shared_asset_load_stdio(path,r),*b=shared_asset_load_fd(path,r,true);
 check((a!=NULL)==accepted,kind,i);check((b!=NULL)==accepted,kind,i);
 if(a&&b)check(!memcmp(a,b,r->bytes-28),"stdio-fd-payload-equivalence",i);
 printf("%u\t%u\t%s\t%d\t%d\t%s\n",i,r->identity,kind,a!=NULL,b!=NULL,r->path);free(a);free(b);
}
static void write_fixture(const char *path,const uint8_t *raw,size_t n){FILE *f=fopen(path,"wb");if(!f||fwrite(raw,1,n,f)!=n||fclose(f)){perror("fixture");exit(2);}}
int main(int argc,char **argv){
 if(argc!=3)return 2;char path[4096],fixture[4096],missing[4096];snprintf(fixture,sizeof fixture,"%s/negative.hda",argv[2]);snprintf(missing,sizeof missing,"%s/absent.hda",argv[2]);
 printf("row\tidentity\tcase\tstdio_accepted\tfd_accepted\tresource\n");
 for(unsigned i=0;i<GLOBAL_ASSET_RESOURCE_COUNT;i++){
  const GlobalAssetResource *r=&global_asset_resources[i];snprintf(path,sizeof path,"%s/%s",argv[1],r->path);
  expect(path,r,1,"actual-public",i);expect(missing,r,0,"missing",i);
  FILE *f=fopen(path,"rb");if(!f)return 2;uint8_t *raw=malloc(r->bytes+1);if(!raw)return 2;
  if(fread(raw,1,r->bytes,f)!=r->bytes||fclose(f))return 2;
  raw[4]^=1;write_fixture(fixture,raw,r->bytes);expect(fixture,r,0,"wrong-identity",i);raw[4]^=1;
  write_fixture(fixture,raw,r->bytes-1);expect(fixture,r,0,"truncated",i);
  raw[r->bytes]=0x5a;write_fixture(fixture,raw,r->bytes+1);expect(fixture,r,0,"trailing-byte",i);
  raw[28]^=1;write_fixture(fixture,raw,r->bytes);expect(fixture,r,0,"payload-corruption",i);raw[28]^=1;
  if(i==0){char ppm[4096];snprintf(ppm,sizeof ppm,"%s/first-asset-decoded-preview.ppm",argv[2]);FILE *g=fopen(ppm,"wb");unsigned w=r->width*r->density,h=r->height*r->density;if(!g)return 2;fprintf(g,"P6\n%u %u\n255\n",w,h);for(unsigned p=0;p<w*h;p++){uint8_t rgb[3];unsigned alpha=raw[28+p*4+3];for(int c=0;c<3;c++)rgb[c]=(uint8_t)((raw[28+p*4+c]*alpha+96*(255-alpha))/255);fwrite(rgb,1,3,g);}fclose(g);}
  free(raw);
 }
 fprintf(stderr,"SUMMARY assets=%u cases=%u checks=%u failures=%u\n",GLOBAL_ASSET_RESOURCE_COUNT,GLOBAL_ASSET_RESOURCE_COUNT*6u,checks,failures);return failures?1:0;
}
