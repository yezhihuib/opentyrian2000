/* Linked-family extension of unchanged historical native helpers. */
#define main historical_newshf_main
#include "newshf_compositor_validation.c"
#undef main
static void linked_birth(unsigned p,unsigned cycle,int filter)
{
 current_slot=0;current_record=171+p;
 unsigned avail=JE_makeEnemy(enemy,current_record,0);CHECK(avail==0);enemyAvail[0]=avail;
 CHECK(newshf_validation_slots[0].role);
 enemy[0].ex=110;enemy[0].ey=80;enemy[0].enemycycle=cycle;enemy[0].filter=filter;
 render_mirror_newshf_validation_observe(0);
}
int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=argv[1];read_exact(bank_original,sizeof(bank_original));read_exact(original_records,sizeof(original_records));
 for(unsigned p=0;p<3;p++){Uint8 r[77];read_exact(r,77);current_record=171+p;record_load(r);}
 read_exact(normal_palette,sizeof(normal_palette));Uint32 bank_size;read_exact(&bank_size,4);spriteSheet9.size=bank_size;spriteSheet9.data=malloc(bank_size);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,bank_size);CHECK(fgetc(stdin)==EOF);
 if(!getenv("LINKED_FALLBACK_ONLY")){
 /* All old cases are retained: optional linked group need not load for them. */
 positives();fprintf(stderr,"historical positives passed\n");negatives();additional();fprintf(stderr,"historical negatives passed\n");soft_alpha();fprintf(stderr,"historical alpha passed\n");
 for(int d=4;d<=8;d+=4)for(unsigned p=0;p<3;p++)for(unsigned c=1;c<=4;c++)for(unsigned f=0;f<2;f++){
  setup(d);linked_birth(p,c,f?0x70:0);quartet();CHECK(global_newshf_contributed&&!global_newshf_fault);
  CHECK(global_newshf_used_resources==0x7e00u);
  const unsigned phases[3][4]={{9,10,10,9},{11,12,12,11},{13,14,14,13}};unsigned phase=phases[p][c-1];
  oracle(phase/3,phase%3+1);
  /* Native fire changes active after draw; this is not identity corruption. */
  enemy[0].aniactive=1;final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready&&last_output_valid);
 }
 for(unsigned mode=0;mode<11;mode++){
  setup(4);linked_birth(2,2,0);
  if(mode==0)enemy[0].ani=3;
  if(mode==1)enemy[0].aniactive=0;
  if(mode==2)enemy[0].enemycycle=0;
  if(mode==3)enemyDat[173].freq[0]^=1;
  if(mode==4)bank_original[sizeof(bank_original)-1]^=1;
  if(mode==5)rgb_palette[5]^=1;
  if(mode==6){tile(1);}else if(mode!=2)quartet();else render_mirror_newshf_validation_observe(0);
  if(mode==7){global_newshf_rgba[14][0]^=1;}
  if(mode==8)enemyDat[173].freq[0]^=1;
  if(mode==9)bank_original[sizeof(bank_original)-1]^=1;
  if(mode==10)enemy[0].enemycycle=3;
  final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready);
  if(mode==3||mode==8)enemyDat[173].freq[0]^=1;
  if(mode==4||mode==9)bank_original[sizeof(bank_original)-1]^=1;
 }
 }
 /* Both ordering directions: missing optional six must not kill old nine. */
 const char *valid=resource_root;char oldonly[4096];snprintf(oldonly,sizeof(oldonly),"%s/old-only",valid);resource_root=oldonly;
 const int old_x[]={170,100,110};
 for(unsigned pos=0;pos<3;pos++)for(unsigned order=0;order<2;order++){
  setup(4);
  if(order==0){birth_at(1,0,1,old_x[pos],80,0);quartet();CHECK(global_newshf_contributed);}
  linked_birth(0,1,0);quartet();CHECK(!global_newshf_linked_good&&!global_newshf_fault);
  if(order==1){birth_at(1,0,1,old_x[pos],80,0);quartet();}
  unsigned owned=0;for(size_t n=0;n<global_newshf_capacity;n++)owned+=global_newshf_owner[n]!=0;
  bool fully_occluded=pos==2&&order==0;
  CHECK(global_newshf_identity_complete()&&global_newshf_assets_match()&&!global_newshf_fault);
  CHECK(fully_occluded?owned==0:owned>0);
  final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);
  if(fully_occluded){
   CHECK(!ready&&!last_output_valid);
   for(int y=0;y<184*4;y++)for(int x=0;x<264*4;x++)
    CHECK(*pixel(output,x,y)==palette_rgb(((Uint8*)VGAScreenSeg->pixels)[(y/4)*VGAScreenSeg->pitch+x/4]));
  }else {
   CHECK(ready&&last_output_valid);output_oracle(MIRROR_OUTPUT_ORDINARY,0,0);
   for(int y=0;y<184*4;y++)for(int x=0;x<264*4;x++){
    size_t n=(size_t)y*canvas->w+x+24*4;
    Uint32 want=global_newshf_owner[n]?*pixel(canvas,x+24*4,y):palette_rgb(((Uint8*)VGAScreenSeg->pixels)[(y/4)*VGAScreenSeg->pitch+x/4]);
    CHECK(*pixel(output,x,y)==want);
   }
  }

 }
 for(unsigned mode=0;mode<2;mode++)for(unsigned i=0;i<6;i++){
  char bad[4096];snprintf(bad,sizeof(bad),"%s/%s-linked%u",valid,mode?"corrupt":"missing",i);resource_root=bad;
  setup(4);birth_at(1,0,1,100,80,0);quartet();linked_birth(i/2,i%2+1,0);quartet();
  CHECK(!global_newshf_linked_good&&!global_newshf_fault);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);
 }
 resource_root=valid;
 printf("PASS linked NEWSHF: %u cases %u assertions; scope=%s; not natural gameplay\n",cases,checks,getenv("LINKED_FALLBACK_ONLY")?"fallback-only":"full historical plus linked matrix");return 0;
}
