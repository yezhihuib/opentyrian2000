/* Shared single-frame dualmissile family: native production allocation/blits.
 * Historical harness helpers are unchanged; original records arrive over stdin. */
#define main historical_newshf_main
#include "newshf_compositor_validation.c"
#undef main
static Uint8 dual_records[2][77];
static void dual_restore(void){for(unsigned p=0;p<2;p++){current_record=newshf_dualmissile_record_ids[p];record_load(dual_records[p]);}}
static void dual_setup(int d){dual_restore();setup(d);}
static void dual_birth(unsigned slot,unsigned p,int x,int y,int filter)
{
 current_slot=slot;current_record=newshf_dualmissile_record_ids[p];
 unsigned avail=JE_makeEnemy(enemy+slot,current_record,0);CHECK(avail==0);enemyAvail[slot]=avail;
 CHECK(newshf_validation_slots[slot].role);CHECK(enemy[slot].eyc==(p?2:5));
 enemy[slot].ex=x;enemy[slot].ey=y;enemy[slot].filter=filter;
 CHECK(enemy[slot].enemycycle==1&&enemy[slot].ani==1&&!enemy[slot].aniactive);
 render_mirror_newshf_validation_observe(slot);
}
static void linked_birth(unsigned slot,unsigned p,unsigned cycle,int x)
{
 current_slot=slot;current_record=171+p;unsigned avail=JE_makeEnemy(enemy+slot,current_record,0);CHECK(avail==0);enemyAvail[slot]=avail;
 CHECK(newshf_validation_slots[slot].role);enemy[slot].ex=x;enemy[slot].ey=80;enemy[slot].enemycycle=cycle;render_mirror_newshf_validation_observe(slot);
}
static void ensure_classic(void)
{
 final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready&&!last_output_valid);
 /* Rejected RGB storage is not a valid output; ordinary indexed presentation
  * remains authoritative. quartet() already checks exact classic INDEX8. */
}
static size_t unproven_soft_sample(unsigned q)
{
 CHECK(global_newshf_group_ready(15));int d=game_probe_density;
 Uint8 tiledata[336];const unsigned parts[]={0,1,19,20};CHECK(decode_tile(global_newshf_bank(),169+parts[q],tiledata,tiledata+168,12,0,0));
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++){
  int sx=(q%2)*96+ax*8/d,sy=(q/2)*112+ay*8/d;
  unsigned alpha=global_newshf_rgba[15][4*(sy*192+sx)+3];
  if(alpha<255&&(alpha||tiledata[168+(ay/d)*12+ax/d])){
   int x=(110-6+(int)(q%2)*12)*d+ax,y=(80-7+(int)(q/2)*14)*d+ay;
   size_t n=(size_t)y*canvas->w+x;hd_owner[n]=1;*pixel(canvas,x,y)=0xff123456u;return n;
  }
 }
 CHECK(false);return 0;
}
int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=argv[1];read_exact(bank_original,sizeof(bank_original));read_exact(original_records,sizeof(original_records));
 for(unsigned p=0;p<3;p++){Uint8 r[77];read_exact(r,77);current_record=171+p;record_load(r);}
 read_exact(dual_records,sizeof(dual_records));dual_restore();
 read_exact(normal_palette,sizeof(normal_palette));Uint32 bank_size;read_exact(&bank_size,4);spriteSheet9.size=bank_size;spriteSheet9.data=malloc(bank_size);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,bank_size);CHECK(fgetc(stdin)==EOF);
 /* Existing fifteen resources still follow their original draw/alpha oracle. */
 for(int d=4;d<=8;d+=4){
  for(unsigned p=0;p<3;p++)for(unsigned pose=1;pose<=3;pose++){dual_setup(d);birth(p,pose,110,80,0);quartet();CHECK(global_newshf_used_resources==0x1ffu);oracle(p,pose);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);}
  for(unsigned p=0;p<3;p++)for(unsigned pose=1;pose<=4;pose++){dual_setup(d);linked_birth(0,p,pose,110);quartet();CHECK(global_newshf_used_resources==0x7e00u);unsigned phase=newshf_profiles[p+3].resources[pose-1];oracle(phase/3,phase%3+1);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);}
 }
 int filters[]={0,0x70,0x80,9};int ys[]={80,-25,-20,-13,-12,-6,0,181,182,195};
 for(int d=4;d<=8;d+=4)for(unsigned p=0;p<2;p++)for(unsigned f=0;f<4;f++){
  dual_setup(d);dual_birth(0,p,110,80,filters[f]);quartet();CHECK(global_newshf_contributed&&!global_newshf_fault);CHECK(global_newshf_used_resources==0x8000u);oracle(5,1);
  /* Unrelated movement after native draw is allowed; render proof is captured. */
  enemy[0].ex+=3;enemy[0].ey+=enemy[0].eyc;enemy[0].filter=0;
  final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready&&last_output_valid);output_oracle(MIRROR_OUTPUT_ORDINARY,0,0);
 }
 for(int d=4;d<=8;d+=4)for(unsigned p=0;p<2;p++)for(unsigned y=0;y<COUNTOF(ys);y++){
  dual_setup(d);dual_birth(0,p,110,ys[y],0);quartet();CHECK(!global_newshf_fault);oracle(5,1);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);
 }
 /* Complete quartet before every late mutation: no incomplete-call shortcut. */
 for(unsigned p=0;p<2;p++)for(unsigned mode=0;mode<17;mode++){
  dual_setup(4);dual_birth(0,p,110,80,0);quartet();CHECK(global_newshf_contributed&&!global_newshf_fault);
  Uint8 saved=bank_original[100];unsigned rec=newshf_dualmissile_record_ids[p];
  if(mode==0)enemyDat[rec].ymove++;
  if(mode==1)enemy[0].enemycycle=2;
  if(mode==2)enemy[0].evalue++;
  if(mode==3)enemy[0].enemytype=rec==2?500:2;
  if(mode==4)enemy[0].enemydatofs=&enemyDat[rec==2?500:2];
  if(mode==5)enemy[0].egr[0]++;
  if(mode==6)enemy[0].ani=2;
  if(mode==7)enemy[0].aniactive=1;
  if(mode==8)enemy[0].edamaged=1;
  if(mode==9)global_newshf_rgba[15][31]^=1;
  if(mode==10)bank_original[100]^=1;
  if(mode==11)rgb_palette[0]^=1;
  if(mode==12)render_mirror_newshf_validation_bank_changed(&enemySpriteSheets[0]);
  if(mode==13)render_mirror_newshf_validation_allocated(enemy,rec,0);
  if(mode==14)enemy[0].sprite2s=&enemySpriteSheets[1];
  if(mode==15)enemy[0].scoreitem=1;
  if(mode==16)enemy[0].animax=1;
  ensure_classic();bank_original[100]=saved;
 }
 /* Cached Present checks must keep new static identity and resources live. */
 for(unsigned p=0;p<2;p++)for(unsigned mode=0;mode<5;mode++){
  dual_setup(4);dual_birth(0,p,110,80,0);quartet();final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);
  if(mode==0)enemy[0].enemycycle=2;
  if(mode==1)enemy[0].evalue++;
  if(mode==2)global_newshf_rgba[15][31]^=1;
  if(mode==3)enemyDat[newshf_dualmissile_record_ids[p]].ymove++;
  if(mode==4)enemy[0].egr[0]++;
  global_newshf_check_cache();CHECK(!ready&&!last_output_valid);
 }
 /* Out-of-order/incomplete quadrants, foreign partial alpha, aliases. */
 dual_setup(4);dual_birth(0,0,110,80,0);tile(1);ensure_classic();
 dual_setup(4);dual_birth(0,0,110,80,0);tile(0);ensure_classic();
 dual_setup(4);talon();dual_birth(0,0,110,80,0);quartet();CHECK(!global_newshf_fault&&!global_newshf_contributed);CHECK(global_newshf_dual_preflight_state[0]==1);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);
 dual_setup(4);dual_birth(0,0,310,80,0);quartet();ensure_classic();
 /* The last quadrant can be the unsupported one: no earlier HD prefix,
  * no poisoned unrelated actor, and a reused slot receives a new decision. */
 for(int d=4;d<=8;d+=4)for(unsigned q=0;q<4;q++){
  dual_setup(d);birth_at(1,0,1,170,80,0);quartet();dual_birth(0,0,110,80,0);
  unproven_soft_sample(q);quartet();CHECK(global_newshf_dual_preflight_state[0]==1&&!global_newshf_fault);
  CHECK(global_newshf_used_resources==0x1ffu);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);
 }
 dual_setup(4);dual_birth(0,0,110,80,0);unproven_soft_sample(3);quartet();CHECK(!global_newshf_contributed);
 enemyAvail[0]=1; /* Native slot retirement precedes any legal reallocation. */
 dual_birth(0,1,170,80,0);quartet();CHECK(global_newshf_dual_preflight_state[0]==2&&global_newshf_contributed&&!global_newshf_fault);
 final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);
 /* An unexpected writer after the preflight still hits the original strict
  * per-pixel guard and revokes the already-contributed frame. */
 dual_setup(4);dual_birth(0,0,110,80,0);tile(0);CHECK(global_newshf_contributed);unproven_soft_sample(3);
 tile(1);tile(19);tile(20);CHECK(global_newshf_fault);ensure_classic();
 /* Mutation after an opaque foreign-owner transfer must revoke stale RGB. */
 dual_setup(4);dual_birth(0,0,110,80,0);quartet();talon();CHECK(global_newshf_contributed);global_newshf_rgba[15][31]^=1;ensure_classic();
 /* Independent resource groups: absence/corruption in optional dual group
  * leaves all fifteen existing resources eligible, both draw orderings. */
 const char *valid=resource_root;const char *modes[]={"missing","corrupt","header","trailing"};
 for(unsigned mode=0;mode<4;mode++)for(unsigned family=0;family<2;family++)for(unsigned order=0;order<2;order++){
  char bad[4096];snprintf(bad,sizeof(bad),"%s/%s-dual",valid,modes[mode]);resource_root=bad;dual_setup(4);
  if(order==0){if(family)linked_birth(1,2,2,170);else birth_at(1,0,1,170,80,0);quartet();}
  dual_birth(0,mode%2,110,80,0);quartet();CHECK(!global_newshf_dualmissile_good&&!global_newshf_fault);
  if(order==1){if(family)linked_birth(1,2,2,170);else birth_at(1,0,1,170,80,0);quartet();}
  final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready&&last_output_valid);
 }
 resource_root=valid;
 /* Conversely missing linked or old art must not prevent dual-only drawing. */
 const char *only[]={"dual-only","no-linked","no-old"};
 for(unsigned mode=0;mode<3;mode++){
  char root[4096];snprintf(root,sizeof(root),"%s/%s",valid,only[mode]);resource_root=root;dual_setup(4);dual_birth(0,0,110,80,0);quartet();CHECK(global_newshf_used_resources==0x8000u&&!global_newshf_fault);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready);
 }
 resource_root=valid;dual_setup(4);dual_birth(0,0,110,80,0);quartet();CHECK(global_newshf_dualmissile_loaded);global_newshf_shutdown();CHECK(!global_newshf_dualmissile_loaded&&!global_newshf_dualmissile_good&&!global_newshf_rgba[15]);
 printf("PASS shared dualmissile NEWSHF: %u cases %u assertions; native allocation/blits and separate resource groups; not natural gameplay\n",cases,checks);return 0;
}
