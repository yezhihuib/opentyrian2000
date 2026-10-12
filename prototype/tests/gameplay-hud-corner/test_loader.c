/* Synthetic source and authored RGBA only. Exact coordinate mask is pinned. */
#include "gameplay_hud.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static uint8_t source[64000], current[64000], padded[337 * 200], mask[64000];
static bool inside(int x, int y) { return x >= 248 && x < 269 && y >= 184 && y < 200; }
static void path_for(char *out, size_t size, const char *root, const char *name)
{ assert(snprintf(out, size, "%s/%s", root, name) < (int)size); }
static void read_file(const char *directory, const char *name, uint8_t *data)
{
 char path[2048];path_for(path,sizeof(path),directory,name);
 FILE *file=fopen(path,"rb");assert(file);assert(fread(data,1,64000,file)==64000);
 assert(fgetc(file)==EOF);assert(!fclose(file));
}
static void expect_corner(bool ready, int density)
{
 for(int y=184;y<200;y++)for(int x=248;x<269;x++)
  assert((gameplay_hud_sample(x,y,density-1,density-1,density,current[y*320+x])!=NULL)==ready);
}
int main(int argc,char **argv)
{
 if(argc==3) {
  assert(!strcmp(argv[2],"reject-capture"));read_file(argv[1],"source.indices",source);
  assert(gameplay_hud_load(argv[1]));assert(!gameplay_hud_capture(source,320));
  assert(!gameplay_hud_ready()&&!gameplay_hud_prepare_corner(source,320));
  gameplay_hud_shutdown();puts("PASS: independently pinned source-zero/region-identity rejection.");return 0;
 }
 assert(argc==2);char directory[2048];path_for(directory,sizeof(directory),argv[1],"corner");
 read_file(directory,"source.indices",source);read_file(directory,"synthetic.mask",mask);
 memcpy(current,source,sizeof(source));
 assert(gameplay_hud_load(directory));assert(gameplay_hud_capture(source,320));
 expect_corner(false,4); /* A capture never substitutes for per-composition proof. */
 assert(gameplay_hud_prepare_corner(current,320));expect_corner(true,4);expect_corner(true,8);
 unsigned black=0;for(int y=184;y<200;y++)for(int x=248;x<269;x++)black+=!source[y*320+x];
 assert(black==46);
 for(int y=184;y<200;y++)for(int x=248;x<269;x++) {
  current[y*320+x]^=1;
  assert(!gameplay_hud_prepare_corner(current,320));expect_corner(false,4);
  assert(gameplay_hud_sample(264,0,0,0,4,current[264]));
  current[y*320+x]^=1;assert(gameplay_hud_prepare_corner(current,320));expect_corner(true,4);
 }
 /* Changes outside the rectangle do not revoke unrelated corner ownership. */
 const int boundaries[][2]={{247,190},{269,190},{248,183},{243,197},{270,184},{0,0}};
 for(unsigned k=0;k<sizeof(boundaries)/sizeof(boundaries[0]);k++) {
  int at=boundaries[k][1]*320+boundaries[k][0];current[at]^=1;
  assert(gameplay_hud_prepare_corner(current,320));expect_corner(true,4);current[at]^=1;
 }
 for(int y=0;y<200;y++) {memcpy(padded+y*337,source+y*320,320);memset(padded+y*337+320,123,17);}
 assert(gameplay_hud_capture(padded,337));expect_corner(false,4);
 assert(gameplay_hud_prepare_corner(padded,337));expect_corner(true,4);
 padded[190*337+268]^=1;assert(!gameplay_hud_prepare_corner(padded,337));expect_corner(false,4);
 assert(!gameplay_hud_prepare_corner(NULL,320));assert(!gameplay_hud_prepare_corner(current,319));
 for(int i=0;i<64000;i++)if(mask[i]&&!inside(i%320,i/320)) {
  current[i]=0;assert(!gameplay_hud_capture(current,320));assert(!gameplay_hud_ready());
  assert(!gameplay_hud_prepare_corner(source,320));current[i]=source[i];break;
 }
 assert(gameplay_hud_capture(source,320));assert(gameplay_hud_prepare_corner(source,320));
 assert(!gameplay_hud_capture(NULL,320));assert(!gameplay_hud_prepare_corner(source,320));
 assert(gameplay_hud_capture(source,320));assert(gameplay_hud_prepare_corner(source,320));
 gameplay_hud_forget_source();expect_corner(false,4);assert(!gameplay_hud_prepare_corner(source,320));
 gameplay_hud_shutdown();assert(!gameplay_hud_ready());
 const char *invalid[]={"partial","wrong-mask","rgba-corrupt","mask-corrupt","source-pin","mask-header","alpha","nonbinary"};
 for(unsigned i=0;i<sizeof(invalid)/sizeof(invalid[0]);i++) {
  path_for(directory,sizeof(directory),argv[1],invalid[i]);assert(!gameplay_hud_load(directory));
  assert(!gameplay_hud_capture(source,320));assert(!gameplay_hud_prepare_corner(source,320));gameplay_hud_shutdown();
 }
 path_for(directory,sizeof(directory),argv[1],"legacy");assert(gameplay_hud_load(directory));
 assert(gameplay_hud_capture(source,320));assert(!gameplay_hud_prepare_corner(source,320));
 assert(gameplay_hud_sample(248,184,0,0,4,source[184*320+248]));
 assert(!gameplay_hud_sample(248,190,0,0,4,source[190*320+248]));
 gameplay_hud_shutdown();puts("PASS: exact6853 mask; every336 mismatch is atomic; source-zero scope; padding/lifetime; 8 corrupt/partial/wrong-mask inputs.");
 return 0;
}
