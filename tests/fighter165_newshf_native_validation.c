/* Finite record165 three-pose controlled native matrix. No game-loop claim.
 * Real production allocation/blits; original game bytes enter stdin only. */
#include <limits.h>
#define main historical_newshf_main
#include "newshf_compositor_validation.c"
#undef main
static Uint8 fighter_record[77],large_record[77],large_bank[NEWSHI_LARGE_BANK_BYTES];
static void s_setup(int d)
{
 current_record=165;record_load(fighter_record);current_record=302;record_load(large_record);setup(d);
 enemySpriteSheetIds[1]=13;enemySpriteSheets[1]=(Sprite2_array){NEWSHI_LARGE_BANK_BYTES,large_bank};
}
static void s_allocate(unsigned slot,int x,int y,int filter)
{
 current_slot=slot;current_record=165;unsigned avail=JE_makeEnemy(enemy+slot,165,0);CHECK(avail==0);enemyAvail[slot]=avail;
 CHECK(newshf_validation_slots[slot].role&&newshf_validation_slots[slot].profile==18);
 CHECK(enemy[slot].enemycycle==1&&enemy[slot].ani==1&&!enemy[slot].aniactive&&!enemy[slot].edamaged);
 enemy[slot].ex=x;enemy[slot].ey=y;enemy[slot].filter=filter;
}
static void s_birth(unsigned slot,unsigned pose,int x,int y,int filter)
{s_allocate(slot,x,y,filter);enemy[slot].enemycycle=pose;render_mirror_newshf_validation_observe(slot);}
static void old_birth(unsigned family,unsigned slot,int x)
{
 if(family==0){birth_at(slot,0,1,x,80,0);return;}
 current_slot=slot;current_record=302;unsigned avail=JE_makeEnemy(enemy+slot,302,0);CHECK(avail==0);enemyAvail[slot]=avail;
 CHECK(newshf_validation_slots[slot].role);enemy[slot].ex=x;enemy[slot].ey=80;render_mirror_newshf_validation_observe(slot);
}
static void s_oracle(unsigned pose){unsigned phase=30+pose;oracle(phase/3,phase%3+1);}
static void finish_valid(void){final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready&&last_output_valid);}
static void finish_invalid(void){final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready&&!last_output_valid);}
static bool s_unproven(unsigned pose,unsigned q,size_t *at)
{
 unsigned phase=30+pose;CHECK(global_newshf_group_ready(phase));int d=game_probe_density;
 Uint8 data[336]={0};const unsigned parts[]={0,1,19,20};unsigned base=newshf_profiles[18].bases[pose-1];
 CHECK(decode_tile(global_newshf_bank(),base+parts[q],data,data+168,12,0,0));
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++){
  int sx=(q%2)*96+ax*8/d,sy=(q/2)*112+ay*8/d;
  unsigned alpha=global_newshf_rgba[phase][4*(sy*192+sx)+3];
  if(alpha<255&&(alpha||data[168+(ay/d)*12+ax/d])){
   int x=(110-6+(int)(q%2)*12)*d+ax,y=(80-7+(int)(q/2)*14)*d+ay;
   *at=(size_t)y*canvas->w+x;hd_owner[*at]=1;*pixel(canvas,x,y)=0xff123456u;return true;
  }
 }
 return false;
}
/* Enumerate original native writes independently, including row wrapping.
 * No synthetic HD ownership is introduced; these are actual decoded masks. */
static void s_native_writes(unsigned pose,int x,int y,Uint8 touched[64000])
{
 memset(touched,0,64000);const unsigned parts[]={0,1,19,20};
 for(unsigned q=0;q<4;q++){
  if(q<2?y<=-13:y<=-26||y>=182)continue;
  Uint8 data[336]={0};CHECK(decode_tile(enemySpriteSheets[0],newshf_profiles[18].bases[pose-1]+parts[q],data,data+168,12,0,0));
  for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(data[168+yy*12+xx]){
   int n=(y-7+(q/2)*14+yy)*320+x-6+(q%2)*12+xx;if(n>=0&&n<64000)touched[n]=1;
  }
 }
}
static unsigned s_wrapping_matrix(void)
{
 const int xs[]={-28,-5,0,5},ys[]={-20,-12,80,182},filters[]={0,0x70};unsigned overlap_subpixels=0;
 for(int d=4;d<=8;d+=4)for(unsigned x=0;x<COUNTOF(xs);x++)for(unsigned y=0;y<COUNTOF(ys);y++)for(unsigned f=0;f<COUNTOF(filters);f++)for(unsigned order=0;order<2;order++){
  s_setup(d);if(!order){s_birth(75,2,110,80,0);quartet();}
  s_birth(0,1,xs[x],ys[y],filters[f]);CHECK(newshf_validation_slots[0].role);quartet();
  CHECK(!global_newshf_fault&&global_newshf_generations[0]==0&&!newshf_validation_slots[0].remaining);
  if(order){s_birth(75,2,110,80,0);quartet();}finish_valid();
 }
 /* A permitted left-wrap writer really overlaps existing RGB near the right
  * native buffer edge. Every normalized touched address retires that owner. */
 for(int d=4;d<=8;d+=4)for(unsigned f=0;f<COUNTOF(filters);f++)for(unsigned mutate=0;mutate<2;mutate++){
  s_setup(d);s_birth(99,1,110,80,0);quartet();s_birth(75,1,290,80,0);quartet();
  Uint8 touched[64000];s_native_writes(1,-28,80,touched);unsigned local=0;
  for(unsigned n=0;n<64000;n++)if(touched[n])for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){
   size_t z=((n/320)*d+sy)*canvas->w+(n%320)*d+sx;if(global_newshf_owner[z])++local;
  }
  CHECK(local>0);overlap_subpixels+=local;s_birth(0,1,-28,80,filters[f]);quartet();
  CHECK(!global_newshf_fault&&global_newshf_generations[0]==0);
  for(unsigned n=0;n<64000;n++)if(touched[n])for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){
   unsigned xx=(n%320)*d+sx,yy=(n/320)*d+sy;size_t z=(size_t)yy*canvas->w+xx;
   CHECK(!global_newshf_owner[z]&&!hd_owner[z]);CHECK(*pixel(canvas,xx,yy)==palette_rgb(((Uint8*)game_screen->pixels)[n]));
  }
  finish_valid();Uint8 saved=bank_original[100];if(mutate)global_newshf_rgba[33][31]^=1;else bank_original[100]^=1;
  global_newshf_check_cache();CHECK(!ready&&!last_output_valid);bank_original[100]=saved;
 }
 /* Legal edge positions still obtain HD; right identity bounds stay strict. */
 const int legal[]={6,299},bad[]={300,310};
 for(int d=4;d<=8;d+=4)for(unsigned k=0;k<2;k++){
  s_setup(d);s_birth(75,1,110,80,0);quartet();s_birth(0,1,legal[k],80,0);quartet();
  CHECK(!global_newshf_fault&&global_newshf_generations[0]==newshf_validation_slots[0].generation);finish_valid();
  s_setup(d);s_birth(75,1,110,80,0);quartet();s_allocate(0,bad[k],80,0);render_mirror_newshf_validation_observe(0);
  CHECK(!newshf_validation_slots[0].role);quartet();finish_invalid();
 }
 /* Real late relocation cannot convert an already-contributed actor to a
  * harmless classical decline: the existing identity guard must revoke it. */
 s_setup(4);s_birth(0,1,110,80,0);quartet();enemy[0].ex=-5;tile(0);finish_invalid();
 /* A pending HD call is never ignored when a different wrapped actor starts. */
 s_setup(4);s_birth(75,1,110,80,0);
 G101EnemyContext c={165,75,0,1,0,0,0,1};
 render_mirror_enemy_tile(game_screen,104,73,enemySpriteSheets[0],49,0,0,&c);CHECK(global_newshf_call.live&&global_newshf_contributed);
 s_birth(0,1,-5,80,0);tile(0);CHECK(global_newshf_fault);finish_invalid();
 CHECK(overlap_subpixels>0);return overlap_subpixels;
}
int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=argv[1];read_exact(bank_original,sizeof(bank_original));read_exact(original_records,sizeof(original_records));
 read_exact(fighter_record,sizeof(fighter_record));read_exact(large_bank,sizeof(large_bank));read_exact(large_record,sizeof(large_record));
 read_exact(normal_palette,sizeof(normal_palette));Uint32 n;read_exact(&n,4);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);CHECK(fgetc(stdin)==EOF);
 CHECK(GLOBAL_NEWSHF_RESOURCE_COUNT==34&&COUNTOF(newshf_profiles)==19);
 unsigned wrap_overlap_subpixels=s_wrapping_matrix();
 /* Each original transparent cell is RGBA0; authored removal inside an
  * occupied native cell is intentional and must restore the proven underlay.
  * The full independent oracle below checks every such subpixel. */
 unsigned empty_cells[3]={0},native_counts[3]={274,265,263};
 for(unsigned pose=1;pose<=3;pose++){
  s_setup(8);CHECK(global_newshf_group_ready(30+pose));unsigned occupied=0;
  const unsigned parts[]={0,1,19,20};
  for(unsigned q=0;q<4;q++){
   Uint8 tiledata[336]={0};CHECK(decode_tile(enemySpriteSheets[0],newshf_profiles[18].bases[pose-1]+parts[q],tiledata,tiledata+168,12,0,0));
   for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++){
    bool native=tiledata[168+y*12+x]!=0,visible=false;if(native)++occupied;
    for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
     unsigned xx=(q%2*12+x)*8+sx,yy=(q/2*14+y)*8+sy;
     const Uint8 *rgba=global_newshf_rgba[30+pose]+4*(yy*192+xx);
     if(!native)CHECK(!(rgba[0]|rgba[1]|rgba[2]|rgba[3]));
     visible|=rgba[3]!=0;
    }
    if(native&&!visible)++empty_cells[pose-1];
   }
  }
  CHECK(occupied==native_counts[pose-1]&&empty_cells[pose-1]>0);
 }
 const unsigned slots[]={0,75,99};const int filters[]={0,0x70,0x80,9};
 for(int d=4;d<=8;d+=4)for(unsigned pose=1;pose<=3;pose++)for(unsigned f=0;f<COUNTOF(filters);f++)for(unsigned z=0;z<COUNTOF(slots);z++){
  s_setup(d);s_birth(slots[z],pose,110,80,filters[f]);quartet();
  CHECK(global_newshf_contributed&&!global_newshf_fault&&global_newshf_used_resources==UINT64_C(0x380000000));
  CHECK(global_newshf_bank_leases[0].object==&enemySpriteSheets[0]&&!global_newshf_bank_leases[1].object);
  CHECK(global_newshf_dual_preflight_state[slots[z]]==2);s_oracle(pose);
  enemy[slots[z]].ex+=3;enemy[slots[z]].ey+=2;enemy[slots[z]].filter=0;finish_valid();output_oracle(MIRROR_OUTPUT_ORDINARY,0,0);
 }
 const int ys[]={-25,-20,-13,-12,-6,0,181,182,195};
 for(int d=4;d<=8;d+=4)for(unsigned pose=1;pose<=3;pose++)for(unsigned y=0;y<COUNTOF(ys);y++){
  s_setup(d);s_birth(0,pose,110,ys[y],0);quartet();CHECK(!global_newshf_fault);s_oracle(pose);final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);
 }
 /* Finite 34-resource routing, including high bits; invalid indices cannot
  * reach indexing or a shift. Each high bit is tested alone before the full
  * family witness is exercised by real quartet draws below. */
 s_setup(4);Sprite2_array b10=enemySpriteSheets[0],b13=enemySpriteSheets[1];
 CHECK(sizeof(global_newshf_used_resources)==sizeof(uint64_t));
 CHECK(global_newshf_phase_bank_matches(27,b13)&&!global_newshf_phase_bank_matches(27,b10));
 CHECK(global_newshf_phase_bank_matches(28,b10)&&global_newshf_phase_bank_matches(30,b10));
 for(unsigned phase=31;phase<34;phase++){
  CHECK(global_newshf_phase_bank_matches(phase,b10)&&!global_newshf_phase_bank_matches(phase,b13));
  CHECK(global_newshf_group_ready(phase));
  global_newshf_used_resources=UINT64_C(1)<<phase;
  CHECK(global_newshf_assets_match());global_newshf_rgba[phase][31]^=1;
  CHECK(!global_newshf_assets_match());global_newshf_rgba[phase][31]^=1;
  CHECK(global_newshf_assets_match());
 }
 global_newshf_used_resources=UINT64_C(0x380000000);CHECK(global_newshf_assets_match());
 const unsigned invalid[]={34,63,64,UINT_MAX};
 for(unsigned k=0;k<COUNTOF(invalid);k++){
  s_setup(4);unsigned phase=invalid[k];
  CHECK(!global_newshf_phase_bank_matches(phase,b10)&&!global_newshf_phase_bank_matches(phase,b13));
  CHECK(!global_newshf_group_ready(phase));
  CHECK(global_newshf_draw_typed(game_screen,104,73,b10,49,0,phase,0,0,0,100)==0);
  CHECK(!global_newshf_contributed&&global_newshf_used_resources==0);finish_invalid();
 }
 for(unsigned mode=0;mode<2;mode++){
  s_setup(4);unsigned phase=mode?18:31;Sprite2_array bank=mode?enemySpriteSheets[0]:enemySpriteSheets[1];
  CHECK(global_newshf_draw_typed(game_screen,104,73,bank,49,0,phase,0,0,0,100)==0);
  CHECK(!global_newshf_contributed&&global_newshf_used_resources==0);finish_invalid();
 }
 /* Reject malformed allocation or pose without lending a partial quartet. */
 for(unsigned mode=0;mode<15;mode++){
  s_setup(4);s_allocate(75,110,80,0);
  if(mode==0)enemy[75].enemycycle=0;if(mode==1)enemy[75].enemycycle=4;if(mode==2)enemy[75].ani=2;
  if(mode==3)enemy[75].aniactive=1;if(mode==4)enemy[75].animax=3;if(mode==5)enemy[75].animin=0;
  if(mode==6)enemy[75].aniwhenfire=1;if(mode==7)enemy[75].edamaged=1;if(mode==8)enemy[75].sprite2s=&enemySpriteSheets[1];
  if(mode==9)enemy[75].egr[1]++;if(mode==10)enemy[75].enemytype=163;if(mode==11)enemy[75].enemydatofs=&enemyDat[163];
  if(mode==12)enemyDat[165].value++;if(mode==13)enemy[75].scoreitem=1;if(mode==14)enemy[75].evalue++;
  render_mirror_newshf_validation_observe(75);CHECK(!newshf_validation_slots[75].role&&!global_newshf_contributed);finish_invalid();
 }
 /* Complete contribution first, then nonvacuous final/cache mutation. */
 for(unsigned pose=1;pose<=3;pose++)for(unsigned cached=0;cached<2;cached++)for(unsigned mode=0;mode<21;mode++){
  s_setup(4);s_birth(99,pose,110,80,0);quartet();CHECK(global_newshf_contributed&&!global_newshf_fault);if(cached)finish_valid();
  Uint8 saved=bank_original[100];
  if(mode==0)enemy[99].enemycycle=pose%3+1;if(mode==1)enemy[99].edamaged=1;if(mode==2)enemy[99].ani=2;
  if(mode==3)enemy[99].evalue++;if(mode==4)enemyDat[165].tur[0]++;if(mode==5)enemy[99].enemydatofs=&enemyDat[163];
  if(mode==6)enemy[99].egr[2]++;if(mode==7)enemy[99].sprite2s=&enemySpriteSheets[1];if(mode==8)bank_original[100]^=1;
  if(mode==9)enemySpriteSheets[0].size--;if(mode==10)enemySpriteSheetIds[0]=13;
  if(mode==11){enemySpriteSheetIds[2]=10;enemySpriteSheets[2]=enemySpriteSheets[0];}
  if(mode>=12&&mode<=14)global_newshf_rgba[31+mode-12][31]^=1;
  if(mode==15)rgb_palette[0]^=1;if(mode==16)render_mirror_newshf_validation_allocated(enemy+99,165,0);
  if(mode==17)render_mirror_newshf_validation_bank_changed(&enemySpriteSheets[0]);if(mode==18)enemy[99].scoreitem=1;
  if(mode==19)enemy[99].aniactive=1;if(mode==20)enemy[99].enemytype=163;
  if(cached){global_newshf_check_cache();CHECK(!ready&&!last_output_valid);}else finish_invalid();bank_original[100]=saved;
 }
 /* Both bank leases persist after all owner bits have been occluded. */
 for(unsigned order=0;order<2;order++)for(unsigned mutate=0;mutate<2;mutate++){
  s_setup(4);if(order){old_birth(1,75,180);quartet();s_birth(0,3,110,80,0);quartet();}
  else{s_birth(0,3,110,80,0);quartet();old_birth(1,75,180);quartet();}
  CHECK(global_newshf_bank_leases[0].object&&global_newshf_bank_leases[1].object);finish_valid();
  memset(global_newshf_owner,0,global_newshf_capacity);Uint8 *bank=mutate?large_bank:bank_original;Uint8 saved=bank[100];bank[100]^=1;
  global_newshf_check_cache();CHECK(!ready&&!last_output_valid);bank[100]=saved;
 }
 for(unsigned cached=0;cached<2;cached++){
  s_setup(4);s_birth(0,1,110,80,0);quartet();talon();CHECK(global_newshf_contributed&&global_talon_contributed);if(cached)finish_valid();
  global_newshf_rgba[33][31]^=1;if(cached){global_newshf_check_cache();CHECK(!ready&&!last_output_valid);}else finish_invalid();
 }
 /* Nonborrowable foreign samples anywhere in quartet decline whole actor. */
 unsigned soft_cases=0;
 for(int d=4;d<=8;d+=4)for(unsigned pose=1;pose<=3;pose++)for(unsigned q=0;q<4;q++){
  s_setup(d);old_birth(0,75,180);quartet();s_birth(0,pose,110,80,0);size_t at;
  if(!s_unproven(pose,q,&at))continue;++soft_cases;quartet();
  CHECK(global_newshf_dual_preflight_state[0]==1&&!global_newshf_fault&&global_newshf_used_resources==0x1ffu);finish_valid();
 }
 CHECK(soft_cases>=6);
 /* A foreign writer arriving after preflight still hits the per-pixel guard. */
 unsigned midpass_cases=0;
 for(unsigned pose=1;pose<=3;pose++){
  s_setup(8);s_birth(0,pose,110,80,0);tile(0);
  CHECK(global_newshf_dual_preflight_state[0]==2&&global_newshf_contributed);
  size_t at;if(!s_unproven(pose,3,&at))continue;++midpass_cases;
  tile(1);tile(19);tile(20);CHECK(global_newshf_fault);finish_invalid();
 }
 CHECK(midpass_cases>=1);
 /* Stale allocation decisions cannot be reused; known-native retirement works. */
 s_setup(4);s_birth(0,1,110,80,0);quartet();uint64_t generation=newshf_validation_slots[0].generation;
 render_mirror_newshf_validation_allocated(enemy,5,0);CHECK(newshf_validation_slots[0].generation!=generation&&!newshf_validation_slots[0].role);finish_invalid();
 s_setup(4);s_birth(0,1,110,80,0);enemyAvail[0]=1;generation=newshf_validation_slots[0].generation;
 s_birth(0,3,110,80,0);CHECK(newshf_validation_slots[0].generation!=generation);quartet();s_oracle(3);finish_valid();
 s_setup(4);s_birth(0,1,110,80,0);tile(1);finish_invalid();
 s_setup(4);s_birth(0,1,110,80,0);tile(0);finish_invalid();
 /* Same actor changes its controlled native pose on later ticks; no stale
  * preflight decision from the prior frame may suppress either banked pose. */
 s_setup(4);s_birth(75,1,110,80,0);quartet();finish_valid();generation=newshf_validation_slots[75].generation;
 for(unsigned pose=2;pose<=3;pose++){
  SDL_FillRect(game_screen,NULL,0x1b);SDL_FillRect(VGAScreenSeg,NULL,0x1b);render_mirror_begin();
  CHECK(newshf_validation_slots[75].generation==generation&&global_newshf_dual_preflight_state[75]==0);
  enemy[75].enemycycle=pose;render_mirror_newshf_validation_observe(75);current_slot=75;quartet();
  CHECK(global_newshf_dual_preflight_state[75]==2);s_oracle(pose);finish_valid();
 }
 s_setup(4);s_birth(0,3,110,80,0);quartet();finish_valid();CHECK(global_newshf_cached);
 CHECK(render_mirror_set_global_assets(NULL));CHECK(!ready&&!last_output_valid&&!global_newshf_fighter165_loaded);
 for(unsigned phase=31;phase<34;phase++)CHECK(!global_newshf_rgba[phase]);
 /* Every malformed resource revokes only this optional group, in both orders. */
 const char *valid=resource_root,*modes[]={"missing","corrupt","header","trailing"};
 unsigned resource_cases=0;
 for(unsigned state=0;state<3;state++)for(unsigned mode=0;mode<4;mode++)for(unsigned family=0;family<2;family++)for(unsigned order=0;order<2;order++){
  char path[4096];snprintf(path,sizeof(path),"%s/%s-fighter%u",valid,modes[mode],state);resource_root=path;s_setup(4);
  if(!order){old_birth(family,75,180);quartet();}s_birth(0,state+1,110,80,0);quartet();
  CHECK(!global_newshf_fighter165_good&&!global_newshf_fault);for(unsigned p=31;p<34;p++)CHECK(!global_newshf_rgba[p]);
  if(order){old_birth(family,75,180);quartet();}CHECK(!(global_newshf_used_resources&UINT64_C(0x380000000)));finish_valid();++resource_cases;
 }
 const char *only[]={"fighter-only","no-large","no-old"};
 for(unsigned mode=0;mode<3;mode++)for(unsigned pose=1;pose<=3;pose++){
  char path[4096];snprintf(path,sizeof(path),"%s/%s",valid,only[mode]);resource_root=path;s_setup(4);s_birth(75,pose,110,80,0);quartet();
  CHECK(global_newshf_used_resources==UINT64_C(0x380000000)&&!global_newshf_fault);finish_valid();
 }
 {char path[4096];snprintf(path,sizeof(path),"%s/old-only",valid);resource_root=path;s_setup(4);s_birth(0,1,110,80,0);quartet();CHECK(!global_newshf_contributed&&!global_newshf_fault);old_birth(1,75,180);quartet();finish_valid();}
 resource_root=valid;s_setup(4);for(unsigned p=0;p<34;p++)CHECK(global_newshf_group_ready(p));global_newshf_shutdown();
 CHECK(!global_newshf_fighter165_loaded&&!global_newshf_fighter165_good);for(unsigned p=0;p<34;p++)CHECK(!global_newshf_rgba[p]);
 printf("fighter165-newshf PASS cases=%u checks=%u resource_negatives=%u soft_preflight_cases=%u midpass_cases=%u empty_native_cells=%u/%u/%u wrap_overlap_subpixels=%u; controlled poses; natural coverage is a separate gameplay receipt\n",cases,checks,resource_cases,soft_cases,midpass_cases,empty_cells[0],empty_cells[1],empty_cells[2],wrap_overlap_subpixels);return 0;
}
