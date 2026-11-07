/* Private-art red-vent pair. Default off; no native stores, gameplay or asset promotion.
 * Included by the ordinary family ground bridge, not a separate translation unit. */
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

enum { RP_BYTES = 172032, RP_SOURCE_BYTES = 672 };
static const unsigned rp_ids[2] = {339, 348};
static const uint64_t rp_source_pins[2] = {UINT64_C(0x2b4a2358518f8aba), UINT64_C(0xd949e56642afdd92)};
static const uint64_t rp_payload_pins[2] = {UINT64_C(0xacc3d72355ec1d20), UINT64_C(0x56565553a52915eb)};
static struct {
 bool enabled, ready, failed, source_fault;
 unsigned setting;
 uint8_t *rgba[2];
 char root[1024];
} rp;
static int rp_member(unsigned id)
{ for (int i=0;i<2;i++) if (id==rp_ids[i]) return i; return -1; }
static uint64_t rp_hash(const uint8_t *p,size_t n)
{ uint64_t h=UINT64_C(0xcbf29ce484222325);while(n--){h^=*p++;h*=UINT64_C(0x100000001b3);}return h; }
static unsigned rp_setting(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("BUILDING313_REDVENT_PAIR_ENABLE");
 return !e||!strcmp(e,"0")?0:!strcmp(e,"1")?1:2;
#else
 return 0;
#endif
}
static const char *rp_directory(void)
{ const char *e=getenv("BUILDING313_REDVENT_PAIR_ASSET_DIR");return e?e:""; }
static void rp_free(void)
{
 rp.enabled=rp.ready=rp.failed=false;
 for(unsigned i=0;i<2;i++){free(rp.rgba[i]);rp.rgba[i]=NULL;}
 rp.root[0]=0;
}
static void rp_map_begin(void){rp.enabled=false;rp.source_fault=false;}
static void rp_bind(unsigned id,const uint8_t *data)
{
 int i=rp_member(id);if(i<0)return;
 if(!data||rp_hash(data,RP_SOURCE_BYTES)!=rp_source_pins[i]){rp.source_fault=true;return;}
 for(unsigned n=0;n<RP_SOURCE_BYTES;n++)if(!data[n])rp.source_fault=true;
}
static uint32_t rp_le32(const uint8_t *p)
{ return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24; }
static bool rp_load(void)
{
 if(rp.ready)return true;
 if(rp.failed)return false;
 for(unsigned i=0;i<2;i++) {
  char name[1200];int len=snprintf(name,sizeof name,"%s/terrain-shapesz-%u-8.hda",rp.root,rp_ids[i]);
  FILE *f=(len>0&&(size_t)len<sizeof name)?fopen(name,"rb"):NULL;
  uint8_t head[28],*p=NULL;bool ok=f!=NULL;
  if(ok)ok=fread(head,1,sizeof head,f)==sizeof head;
  if(ok)ok=!memcmp(head,"HDR1",4)&&rp_le32(head+4)==2010000+rp_ids[i]&&rp_le32(head+8)==8&&rp_le32(head+12)==24&&rp_le32(head+16)==28&&!rp_le32(head+20)&&!rp_le32(head+24);
  if(ok){p=malloc(RP_BYTES);ok=p!=NULL;}
  if(ok)ok=fread(p,1,RP_BYTES,f)==RP_BYTES&&fgetc(f)==EOF&&!ferror(f);
  if(f&&fclose(f))ok=false;
  if(ok)ok=rp_hash(p,RP_BYTES)==rp_payload_pins[i];
  if(ok)for(unsigned n=3;n<RP_BYTES;n+=4)if(p[n]!=255){ok=false;break;}
  if(!ok){free(p);for(unsigned j=0;j<2;j++){free(rp.rgba[j]);rp.rgba[j]=NULL;}rp.ready=rp.enabled=false;rp.failed=true;return false;}
  rp.rgba[i]=p;
 }
 rp.ready=true;return true;
}
/* Only a new frame can select the optional pair. Root/toggle changes are
 * refused during that frame; a later frame may establish a new snapshot. */
static bool rp_begin(bool parent_requested,bool ground_requested)
{
 rp.enabled=false;
 rp.setting=parent_requested?rp_setting():0;
 if(!rp.setting){rp_free();return true;}
 if(rp.setting!=1||!ground_requested||rp.source_fault)return false;
 const char *root=rp_directory();size_t n=strlen(root);
 if(!n||n>=sizeof rp.root)return false;
 if(strcmp(root,rp.root)){rp_free();memcpy(rp.root,root,n+1);}
 if(!rp_load())return false;
 rp.enabled=true;return true;
}
static bool rp_current(void)
{
 if(rp.setting!=rp_setting())return false;
 return rp.setting==0||(rp.setting==1&&rp.enabled&&rp.ready&&!rp.failed&&!rp.source_fault&&!strcmp(rp.root,rp_directory()));
}
