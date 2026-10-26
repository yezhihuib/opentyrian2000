/* Seven-slot shared turret family: production allocation and sprite blits.
 * Private originals enter stdin only. No gameplay/event timers are replaced. */
#define main historical_newshf_main
#include "newshf_compositor_validation.c"
#undef main
static Uint8 linked_records[3][77],dual_records[2][77],turret_records[2][77];
static void t_restore(void)
{
 for(unsigned p=0;p<3;p++){current_record=171+p;record_load(linked_records[p]);}
 for(unsigned p=0;p<2;p++){current_record=newshf_dualmissile_record_ids[p];record_load(dual_records[p]);current_record=newshf_turret_record_ids[p];record_load(turret_records[p]);}
}
static void t_setup(int d){t_restore();setup(d);}
static void t_allocate(unsigned slot,unsigned p,int x,int y,int filter)
{
 current_slot=slot;current_record=newshf_turret_record_ids[p];
 unsigned avail=JE_makeEnemy(enemy+slot,current_record,0);CHECK(avail==0);enemyAvail[slot]=avail;
 CHECK(newshf_validation_slots[slot].role);CHECK(enemy[slot].ani==7&&enemy[slot].animax==7&&enemy[slot].aniactive==2&&enemy[slot].enemycycle==1);
 enemy[slot].ex=x;enemy[slot].ey=y;enemy[slot].filter=filter;
}
static void t_birth(unsigned slot,unsigned p,unsigned cycle,int x,int y,int filter)
{t_allocate(slot,p,x,y,filter);enemy[slot].enemycycle=cycle;render_mirror_newshf_validation_observe(slot);}
static void other_birth(unsigned slot,unsigned family,unsigned pose,int x,int y)
{
 if(family==0){birth_at(slot,0,pose,x,y,0);return;}
 current_slot=slot;current_record=family==1?173:500;
 unsigned avail=JE_makeEnemy(enemy+slot,current_record,0);CHECK(avail==0);enemyAvail[slot]=avail;CHECK(newshf_validation_slots[slot].role);
 enemy[slot].ex=x;enemy[slot].ey=y;enemy[slot].enemycycle=pose;render_mirror_newshf_validation_observe(slot);
}
static void finish_valid(void){final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready&&last_output_valid);}
static void finish_invalid(void){final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready&&!last_output_valid);}
static unsigned t_phase(unsigned cycle){return cycle>=2&&cycle<=4?17:16;}
static void t_oracle(unsigned cycle){unsigned phase=t_phase(cycle);oracle(phase/3,phase%3+1);}
int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=argv[1];read_exact(bank_original,sizeof(bank_original));read_exact(original_records,sizeof(original_records));
 read_exact(linked_records,sizeof(linked_records));read_exact(dual_records,sizeof(dual_records));read_exact(turret_records,sizeof(turret_records));t_restore();
 read_exact(normal_palette,sizeof(normal_palette));Uint32 bank_size;read_exact(&bank_size,4);spriteSheet9.size=bank_size;spriteSheet9.data=malloc(bank_size);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,bank_size);CHECK(fgetc(stdin)==EOF);
 /* Existing sixteen resources retain their exact draw oracle. */
 for(int d=4;d<=8;d+=4){
  for(unsigned p=0;p<3;p++)for(unsigned pose=1;pose<=3;pose++){t_setup(d);birth(p,pose,110,80,0);quartet();oracle(p,pose);CHECK(global_newshf_used_resources==0x1ffu);finish_valid();}
  for(unsigned p=0;p<3;p++)for(unsigned pose=1;pose<=4;pose++){
   t_setup(d);current_slot=0;current_record=171+p;unsigned avail=JE_makeEnemy(enemy,current_record,0);CHECK(avail==0);enemyAvail[0]=avail;enemy[0].ex=110;enemy[0].ey=80;enemy[0].enemycycle=pose;render_mirror_newshf_validation_observe(0);quartet();
   unsigned phase=newshf_profiles[p+3].resources[pose-1];oracle(phase/3,phase%3+1);CHECK(global_newshf_used_resources==0x7e00u);finish_valid();
  }
  for(unsigned p=0;p<2;p++){t_setup(d);current_slot=0;current_record=newshf_dualmissile_record_ids[p];unsigned avail=JE_makeEnemy(enemy,current_record,0);CHECK(avail==0);enemyAvail[0]=avail;enemy[0].ex=110;enemy[0].ey=80;render_mirror_newshf_validation_observe(0);quartet();oracle(5,1);CHECK(global_newshf_used_resources==0x8000u);finish_valid();}
 }
 int filters[]={0,0x70,0x80,9};
 for(int d=4;d<=8;d+=4)for(unsigned p=0;p<2;p++)for(unsigned cycle=1;cycle<=7;cycle++)for(unsigned f=0;f<4;f++){
  t_setup(d);t_birth(0,p,cycle,110,80,filters[f]);CHECK(newshf_validation_slots[0].role);quartet();
  CHECK(global_newshf_contributed&&!global_newshf_fault&&global_newshf_used_resources==UINT32_C(0x30000));
  CHECK(global_newshf_dual_preflight_state[0]==0&&!global_newshf_shapesy_dependency);t_oracle(cycle);
  /* Legitimate fire/launch activity transitions and movement occur after draw. */
  enemy[0].aniactive=1;enemy[0].ey+=2;enemy[0].filter=0;finish_valid();output_oracle(MIRROR_OUTPUT_ORDINARY,0,0);
 }
 /* Native resting cycle7 is valid in both activity states; no forced cycle1. */
 for(unsigned p=0;p<2;p++)for(unsigned state=1;state<=2;state++){
  t_setup(4);t_allocate(0,p,110,80,0);enemy[0].enemycycle=7;enemy[0].aniactive=state;render_mirror_newshf_validation_observe(0);quartet();t_oracle(7);enemy[0].aniactive=3-state;finish_valid();
 }
 const int ys[]={-25,-20,-13,-12,-6,0,181,182,195};
 for(int d=4;d<=8;d+=4)for(unsigned y=0;y<COUNTOF(ys);y++){
  t_setup(d);t_birth(0,y%2,y%7+1,110,ys[y],0);quartet();CHECK(!global_newshf_fault);t_oracle(y%7+1);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);
 }
 /* Reject wrong animation or identity before first visible quadrant. */
 for(unsigned p=0;p<2;p++)for(unsigned mode=0;mode<10;mode++){
  t_setup(4);t_allocate(0,p,110,80,0);
  if(mode==0)enemy[0].enemycycle=0;if(mode==1)enemy[0].enemycycle=8;if(mode==2)enemy[0].ani=4;if(mode==3)enemy[0].animax=4;
  if(mode==4)enemy[0].aniactive=0;if(mode==5)enemy[0].aniactive=3;if(mode==6)enemy[0].aniwhenfire=0;
  if(mode==7)enemy[0].egr[6]++;if(mode==8)enemy[0].animin=0;if(mode==9)enemy[0].sprite2s=&enemySpriteSheets[1];
  render_mirror_newshf_validation_observe(0);CHECK(!newshf_validation_slots[0].role&&!global_newshf_contributed);finish_invalid();
 }
 /* Completed contribution before final/cache mutations; no vacuous rejection. */
 for(unsigned p=0;p<2;p++)for(unsigned cached=0;cached<2;cached++)for(unsigned mode=0;mode<17;mode++){
  t_setup(4);t_birth(0,p,7,110,80,0);quartet();CHECK(global_newshf_contributed&&!global_newshf_fault);if(cached)finish_valid();
  Uint8 saved=bank_original[100];unsigned rec=newshf_turret_record_ids[p];
  if(mode==0)enemyDat[rec].animate++;if(mode==1)enemy[0].enemycycle=6;if(mode==2)enemy[0].evalue++;
  if(mode==3)enemy[0].enemytype=rec==162?840:162;if(mode==4)enemy[0].enemydatofs=&enemyDat[rec==162?840:162];
  if(mode==5)enemy[0].egr[6]++;if(mode==6)enemy[0].ani=4;if(mode==7)enemy[0].aniactive=0;if(mode==8)enemy[0].edamaged=1;
  if(mode==9)global_newshf_rgba[16][31]^=1;if(mode==10)global_newshf_rgba[17][31]^=1;
  if(mode==11)bank_original[100]^=1;if(mode==12)rgb_palette[0]^=1;
  if(mode==13)render_mirror_newshf_validation_bank_changed(&enemySpriteSheets[0]);
  if(mode==14)render_mirror_newshf_validation_allocated(enemy,rec,0);
  if(mode==15)enemy[0].scoreitem=1;if(mode==16)enemy[0].animax=4;
  if(cached){global_newshf_check_cache();CHECK(!ready&&!last_output_valid);}else finish_invalid();bank_original[100]=saved;
 }
 t_setup(4);t_birth(0,0,2,110,80,0);tile(1);finish_invalid();
 t_setup(4);t_birth(0,1,4,110,80,0);tile(0);finish_invalid();
 /* Full-opacity turret can cover foreign terrain/smoke/ship-owned pixels;
  * it never acquires the dualmissile partial-alpha borrowing authority. */
 for(int d=4;d<=8;d+=4){
  t_setup(d);talon();t_birth(0,0,2,110,80,0);quartet();CHECK(!global_newshf_fault);t_oracle(2);CHECK(global_newshf_dual_preflight_state[0]==0&&!global_newshf_shapesy_dependency);finish_valid();
  t_setup(d);other_birth(1,2,1,110,80);quartet();t_birth(0,1,5,110,80,0);quartet();t_oracle(5);CHECK(global_newshf_used_resources==UINT32_C(0x38000));finish_valid();
  t_setup(d);t_birth(0,0,2,110,80,0);quartet();other_birth(1,2,1,110,80);quartet();CHECK(!global_newshf_fault);finish_valid();
 }
 /* Later native smoke-like blended write must retire only covered HD pixels. */
 t_setup(4);t_birth(0,0,2,110,80,0);quartet();Uint8 *pixelindex=(Uint8*)game_screen->pixels+80*320+110;Uint8 before=*pixelindex;*pixelindex=(before&240)|((before&15)/2);render_mirror_pixel(game_screen,pixelindex,*pixelindex,MIRROR_SHADOW);finish_valid();
 /* Full and partial later occlusion cannot erase retained source dependency. */
 for(unsigned family=0;family<3;family++){
  t_setup(4);t_birth(0,0,2,110,80,0);quartet();if(family==0)talon();else other_birth(1,family,1,family==1?115:110,80),quartet();
  global_newshf_rgba[17][31]^=1;finish_invalid();
 }
 /* Slot retirement/reallocation never reuses a stale turret witness. */
 for(unsigned p=0;p<2;p++){
  t_setup(4);t_birth(0,p,2,110,80,0);quartet();uint64_t generation=newshf_validation_slots[0].generation;
  render_mirror_newshf_validation_allocated(enemy,5,0);CHECK(!newshf_validation_slots[0].role&&newshf_validation_slots[0].generation!=generation);finish_invalid();
  t_setup(4);t_birth(0,p,1,110,80,0);generation=newshf_validation_slots[0].generation;
  /* No pixels have contributed: native retirement can safely reuse the slot. */
  enemyAvail[0]=1;current_slot=0;current_record=163;unsigned avail=JE_makeEnemy(enemy,current_record,0);CHECK(avail==0);enemyAvail[0]=avail;
  CHECK(newshf_validation_slots[0].role&&newshf_validation_slots[0].profile==0&&newshf_validation_slots[0].generation!=generation);
  render_mirror_newshf_validation_allocated(enemy,5,0);CHECK(!newshf_validation_slots[0].role);enemyAvail[0]=1;
  t_birth(0,1-p,7,110,80,0);quartet();t_oracle(7);finish_valid();
 }
 const char *valid=resource_root,*modes[]={"missing","corrupt","header","trailing"};
 for(unsigned state=0;state<2;state++)for(unsigned mode=0;mode<4;mode++)for(unsigned family=0;family<3;family++)for(unsigned order=0;order<2;order++){
  char bad[4096];snprintf(bad,sizeof(bad),"%s/%s-turret%u",valid,modes[mode],state);resource_root=bad;t_setup(4);
  if(order==0){other_birth(1,family,family==1?4:1,170,80);quartet();}
  t_birth(0,state,state?2:1,110,80,0);quartet();CHECK(!global_newshf_turret_good&&!global_newshf_fault);
  if(order==1){other_birth(1,family,family==1?4:1,170,80);quartet();}
  CHECK(!(global_newshf_used_resources&UINT32_C(0x30000)));finish_valid();
 }
 const char *only[]={"turret-only","no-linked","no-old","no-dual"};
 for(unsigned mode=0;mode<4;mode++){
  char path[4096];snprintf(path,sizeof(path),"%s/%s",valid,only[mode]);resource_root=path;t_setup(4);t_birth(0,mode%2,mode+1,110,80,0);quartet();CHECK(global_newshf_used_resources==UINT32_C(0x30000)&&!global_newshf_fault);finish_valid();
 }
 resource_root=valid;t_setup(4);t_birth(0,0,1,110,80,0);quartet();CHECK(global_newshf_turret_loaded);global_newshf_shutdown();
 CHECK(!global_newshf_turret_loaded&&!global_newshf_turret_good);for(unsigned i=0;i<18;i++)CHECK(!global_newshf_rgba[i]);
 printf("PASS shared turret NEWSHF: %u cases %u assertions; two records/seven slots, native allocation/blits, independent group; no game-loop or Windows claim\n",cases,checks);return 0;
}
