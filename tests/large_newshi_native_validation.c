/* NEWSHI bank13 bounded runtime matrix; production allocation and sprite blits.
 * Original bytes supplied over stdin only. Controlled, not natural gameplay. */
#define main historical_newshf_main
#include "newshf_compositor_validation.c"
#undef main
static Uint8 linked_records[3][77],dual_records[2][77],turret_records[2][77];
static Uint8 large_records[7][77],large_bank[NEWSHI_LARGE_BANK_BYTES];
static void l_restore(void)
{
 for(unsigned p=0;p<3;p++){current_record=171+p;record_load(linked_records[p]);}
 for(unsigned p=0;p<2;p++){current_record=newshf_dualmissile_record_ids[p];record_load(dual_records[p]);current_record=newshf_turret_record_ids[p];record_load(turret_records[p]);}
 for(unsigned p=0;p<7;p++){current_record=302+p;record_load(large_records[p]);}
}
static void l_setup(int d,bool only)
{
 l_restore();setup(d);
 enemySpriteSheetIds[1]=13;enemySpriteSheets[1]=(Sprite2_array){NEWSHI_LARGE_BANK_BYTES,large_bank};
 if(only){enemySpriteSheetIds[0]=0;memset(enemyDat+163,0,sizeof(enemyDat[163]));}
}
static void l_allocate(unsigned slot,unsigned p,int x,int y)
{
 current_slot=slot;current_record=302+p;unsigned avail=JE_makeEnemy(enemy+slot,current_record,0);CHECK(avail==0);enemyAvail[slot]=avail;
 CHECK(newshf_validation_slots[slot].role);enemy[slot].ex=x;enemy[slot].ey=y;
}
/* Exact unchanged native threshold state block from tyrian2.c, verified by
 * the driver before compilation. Controlled trigger; no collision claim. */
static void l_hit(unsigned slot)
{
 unsigned temp3=slot;
											enemy[temp3].enemycycle = 1;

											enemy[temp3].edamaged = !enemy[temp3].edamaged;

											if (enemy[temp3].edani != 0)
											{
												enemy[temp3].ani = abs(enemy[temp3].edani);
												enemy[temp3].aniactive = 1;
												enemy[temp3].animax = 0;
												enemy[temp3].animin = enemy[temp3].edgr;
												enemy[temp3].enemycycle = enemy[temp3].animin - 1;

											}
											else if (enemy[temp3].edgr > 0)
											{
												enemy[temp3].egr[1-1] = enemy[temp3].edgr;
												enemy[temp3].ani = 1;
												enemy[temp3].aniactive = 0;
												enemy[temp3].animax = 0;
												enemy[temp3].animin = 1;
											}
											else
											{
												enemyAvail[temp3] = 1;
												enemyKilled++;
											}

											enemy[temp3].aniwhenfire = 0;

											if (enemy[temp3].armorleft > (unsigned char)enemy[temp3].edlevel)
												enemy[temp3].armorleft = enemy[temp3].edlevel;
}
static void l_birth(unsigned slot,unsigned p,unsigned cycle,int x,int y)
{
 l_allocate(slot,p,x,y);if(p==6&&cycle>=2)l_hit(slot);enemy[slot].enemycycle=cycle;render_mirror_newshf_validation_observe(slot);
}
static void finish_valid(void){final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(ready&&last_output_valid);}
static void finish_invalid(void){final_copy();render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready&&!last_output_valid);}
static void l_oracle(unsigned phase){oracle(phase/3,phase%3+1);}
static bool l_unproven(unsigned phase,unsigned q)
{
 CHECK(global_newshf_group_ready(phase));int d=game_probe_density;
 Uint8 tiledata[336]={0};const unsigned parts[]={0,1,19,20};unsigned base=enemy[current_slot].egr[enemy[current_slot].enemycycle-1];
 CHECK(decode_tile(*enemy[current_slot].sprite2s,base+parts[q],tiledata,tiledata+168,12,0,0));
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++){
  int sx=(q%2)*96+ax*8/d,sy=(q/2)*112+ay*8/d;unsigned alpha=global_newshf_rgba[phase][4*(sy*192+sx)+3];
  if(alpha<255&&(alpha||tiledata[168+(ay/d)*12+ax/d])){
   int x=(110-6+(int)(q%2)*12)*d+ax,y=(80-7+(int)(q/2)*14)*d+ay;size_t n=(size_t)y*canvas->w+x;
   hd_owner[n]=1;*pixel(canvas,x,y)=0xff123456u;return true;
  }
 }
 return false;
}
static void l_animate(unsigned i)
{
				if (enemy[i].aniactive == 1)
				{
					enemy[i].enemycycle++;

					if (enemy[i].enemycycle == enemy[i].animax)
						enemy[i].aniactive = enemy[i].aniwhenfire;
					else if (enemy[i].enemycycle > enemy[i].ani)
						enemy[i].enemycycle = enemy[i].animin;
				}
}
static bool l_fire_eligible(unsigned i)
{
			if (enemy[i].edamaged == 1)
				goto draw_enemy_end;
 return true;
draw_enemy_end:
 return false;
}
static void l_quartet(void)
{
 uint64_t rng=mt_state_fingerprint();quartet();CHECK(rng==mt_state_fingerprint());
}
#define quartet l_quartet
int main(int argc,char **argv)
{
 CHECK(argc==2);resource_root=argv[1];read_exact(bank_original,sizeof(bank_original));read_exact(original_records,sizeof(original_records));
 read_exact(linked_records,sizeof(linked_records));read_exact(dual_records,sizeof(dual_records));read_exact(turret_records,sizeof(turret_records));
 read_exact(large_bank,sizeof(large_bank));read_exact(large_records,sizeof(large_records));
 read_exact(normal_palette,sizeof(normal_palette));Uint32 bank_size;read_exact(&bank_size,4);spriteSheet9.size=bank_size;spriteSheet9.data=malloc(bank_size);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,bank_size);CHECK(fgetc(stdin)==EOF);
 /* Deterministic sparse-decoder regression: transparent bytes preserve
  * poison unless caller initialized them. Covers old phase15 and all10 new
  * phases; the driver additionally enforces the production zero initializer. */
 const unsigned soft_bases[]={169,201,203,237,239,241,243,278,268,270,272};
 const unsigned soft_parts[]={0,1,19,20};unsigned transparent_samples=0;
 for(unsigned p=0;p<COUNTOF(soft_bases);p++)for(unsigned q=0;q<4;q++){
  Sprite2_array b=p?(Sprite2_array){NEWSHI_LARGE_BANK_BYTES,large_bank}:(Sprite2_array){NEWSHF_PROTOTYPE_BANK_BYTES,bank_original};
  Uint8 clean[336]={0},poison[336];memset(poison,0xa5,sizeof(poison));
  CHECK(decode_tile(b,soft_bases[p]+soft_parts[q],clean,clean+168,12,0,0));
  CHECK(decode_tile(b,soft_bases[p]+soft_parts[q],poison,poison+168,12,0,0));
  for(unsigned n=0;n<168;n++)if(!clean[168+n]){CHECK(clean[n]==0&&poison[n]==0xa5&&poison[168+n]==0xa5);++transparent_samples;}
   else CHECK(clean[168+n]==255&&poison[168+n]==255&&clean[n]==poison[n]);
 }
 CHECK(transparent_samples>100);
 for(int d=4;d<=8;d+=4)for(unsigned only=0;only<2;only++)for(unsigned p=0;p<7;p++)for(unsigned cycle=1;cycle<=(p==6?12:1);cycle++){
  if(cycle==2)continue;l_setup(d,only);l_birth(0,p,cycle,110,80);quartet();
  CHECK(global_newshf_contributed&&!global_newshf_fault&&global_newshf_used_resources==UINT32_C(0x0ffc0000));
  unsigned phase=newshf_profiles[10+p].resources[cycle-1];l_oracle(phase);finish_valid();output_oracle(MIRROR_OUTPUT_ORDINARY,0,0);
 }
 /* All old eighteen poses, both densities, exact same independent pixel oracle. */
 for(int d=4;d<=8;d+=4)for(unsigned p=0;p<10;p++)for(unsigned cycle=1;cycle<=newshf_profiles[p].cycles;cycle++){
  l_setup(d,false);current_slot=0;current_record=newshf_profiles[p].record;unsigned avail=JE_makeEnemy(enemy,current_record,0);CHECK(avail==0);enemyAvail[0]=avail;CHECK(newshf_validation_slots[0].role);
  enemy[0].ex=110;enemy[0].ey=80;enemy[0].enemycycle=cycle;render_mirror_newshf_validation_observe(0);quartet();l_oracle(newshf_profiles[p].resources[cycle-1]);finish_valid();
 }
 /* Native legal hit after frozen normal draw, including cycle2 final/cache. */
 for(unsigned p=0;p<7;p++){
  l_setup(4,true);l_birth(0,p,1,110,80);quartet();l_hit(0);finish_valid();CHECK(global_newshf_cache_source_matches());
  if(p==6){render_mirror_newshf_validation_frame();global_newshf_frame_begin();enemy[0].enemycycle=3;render_mirror_newshf_validation_observe(0);CHECK(newshf_validation_slots[0].role);}
 }
 /* Execute the unchanged native increment/wrap block after the unchanged
  * hit transition. Fire remains gated while normal, enabled when damaged;
  * neither the clock nor original weapon151/freq8/shot countdown is replaced. */
 l_setup(4,true);l_allocate(0,6,110,80);
 CHECK(enemyDat[308].tur[0]==151&&enemyDat[308].freq[0]==8);
 CHECK(enemy[0].tur[0]==151&&enemy[0].freq[0]==8&&!l_fire_eligible(0));
 Uint8 fire_wait=enemy[0].eshotwait[0];l_hit(0);CHECK(l_fire_eligible(0)&&enemy[0].eshotwait[0]==fire_wait);
 for(unsigned step=0;step<21;step++){
  unsigned expected_cycle=3+step%10;l_animate(0);CHECK(enemy[0].enemycycle==expected_cycle);
  CHECK(enemy[0].tur[0]==151&&enemy[0].freq[0]==8&&enemy[0].eshotwait[0]==fire_wait);
  CHECK(newshf_validation_shape(0)&&newshf_validation_pose(0));
 }
 /* Upper static actors retain the exact picture after independent damage. */
 for(unsigned p=0;p<6;p++){l_setup(4,true);l_allocate(0,p,110,80);l_hit(0);render_mirror_newshf_validation_observe(0);quartet();l_oracle(18+p);finish_valid();}
 for(unsigned mode=0;mode<13;mode++){
  l_setup(4,true);l_allocate(0,6,110,80);
  if(mode==0)enemy[0].enemycycle=2;if(mode==1)enemy[0].edamaged=false;if(mode==2)enemy[0].ani=12;
  if(mode>=3)l_hit(0);
  if(mode==3)enemy[0].enemycycle=2;else if(mode>=4)enemy[0].enemycycle=3;
  if(mode==4)enemy[0].animin=1;if(mode==5)enemy[0].aniwhenfire=2;if(mode==6)enemy[0].aniactive=0;
  if(mode==7)enemy[0].animax=12;if(mode==8)enemy[0].ani=11;if(mode==9)enemy[0].enemycycle=13;
  if(mode==10)enemy[0].egr[2]++;if(mode==11)enemy[0].sprite2s=&enemySpriteSheets[0];if(mode==12)enemy[0].edamaged=true;
  render_mirror_newshf_validation_observe(0);CHECK(!newshf_validation_slots[0].role&&!global_newshf_contributed);
 }
 /* Nonvacuous final/cache corruption of both the actor and independent bank. */
 for(unsigned cached=0;cached<2;cached++)for(unsigned mode=0;mode<20;mode++){
  l_setup(4,true);l_birth(0,6,3,110,80);quartet();CHECK(global_newshf_contributed);if(cached)finish_valid();
  Uint8 saved=large_bank[100];
  if(mode==0)enemy[0].enemycycle=4;if(mode==1)enemy[0].edamaged=true;if(mode==2)enemy[0].ani=1;if(mode==3)enemy[0].animin=1;
  if(mode==4)enemy[0].evalue++;if(mode==5)enemyDat[308].tur[0]++;if(mode==6)enemy[0].enemydatofs=&enemyDat[307];if(mode==7)enemy[0].egr[11]++;
  if(mode==8)large_bank[100]^=1;if(mode==9)enemySpriteSheets[1].size--;if(mode==10)enemySpriteSheetIds[1]=10;
  if(mode==11){enemySpriteSheetIds[2]=13;enemySpriteSheets[2]=enemySpriteSheets[1];}
  if(mode==12)global_newshf_rgba[18][31]^=1;if(mode==13)global_newshf_rgba[27][31]^=1;if(mode==14)rgb_palette[0]^=1;
  if(mode==15)render_mirror_newshf_validation_allocated(enemy,308,0);if(mode==16)render_mirror_newshf_validation_bank_changed(&enemySpriteSheets[1]);
  if(mode==17)enemy[0].scoreitem=true;if(mode==18)enemy[0].edani=0;if(mode==19)enemy[0].aniwhenfire=1;
  if(cached){global_newshf_check_cache();CHECK(!ready&&!last_output_valid);}else finish_invalid();large_bank[100]=saved;
 }
 /* Both draw orders retain every contributed bank through foreign ownership. */
 for(unsigned order=0;order<2;order++)for(unsigned mutate=0;mutate<2;mutate++){
  l_setup(4,false);
  if(order){l_birth(1,0,1,180,80);quartet();birth_at(0,0,1,110,80,0);quartet();}
  else {birth_at(0,0,1,110,80,0);quartet();l_birth(1,0,1,180,80);quartet();}
  CHECK(global_newshf_bank_leases[0].object&&global_newshf_bank_leases[1].object);finish_valid();
  /* Erase owner bits to model complete later coverage; dependency must survive. */
  memset(global_newshf_owner,0,global_newshf_capacity);Uint8 *b=mutate?large_bank:bank_original;Uint8 saved=b[100];b[100]^=1;
  global_newshf_check_cache();CHECK(!ready&&!last_output_valid);b[100]=saved;
 }
 /* Independent slots/links and absence do not impose a composite gameplay actor. */
 for(unsigned missing=0;missing<7;missing++){
  l_setup(4,true);for(unsigned p=0;p<7;p++)if(p!=missing){l_birth(p,p,1,40+(p%4)*50,50+(p/4)*60);enemy[p].linknum=p+1;quartet();}
  finish_valid();CHECK(global_newshf_used_resources==UINT32_C(0x0ffc0000));
  render_mirror_newshf_validation_frame();enemyAvail[(missing+1)%7]=1;render_mirror_newshf_validation_frame();CHECK(!newshf_validation_slots[(missing+1)%7].role);
 }
 const int ys[]={-25,-20,-13,-12,0,181,182,195};
 for(int d=4;d<=8;d+=4)for(unsigned y=0;y<COUNTOF(ys);y++){l_setup(d,true);l_birth(0,6,8,110,ys[y]);quartet();CHECK(!global_newshf_fault);l_oracle(27);}
 l_setup(4,true);l_birth(0,0,1,110,80);tile(1);CHECK(!newshf_validation_slots[0].role);
 l_setup(4,true);l_birth(0,0,1,110,80);tile(0);finish_invalid();
 /* Unknown foreign partial-alpha samples decline the entire actor before
  * any quadrant, including a late bottom quadrant. Old actors stay valid. */
 unsigned soft_cases=0;
 for(int d=4;d<=8;d+=4)for(unsigned phase=18;phase<28;phase++)for(unsigned q=0;q<4;q++){
  l_setup(d,false);birth_at(1,0,1,180,80,0);quartet();
  unsigned p=phase<25?phase-18:6,cycle=phase<25?1:phase==25?3:phase==26?5:8;l_birth(0,p,cycle,110,80);
  if(!l_unproven(phase,q))continue;++soft_cases;quartet();if(global_newshf_dual_preflight_state[0]!=1||global_newshf_fault)fprintf(stderr,"soft fail d=%d phase=%u q=%u state=%u fault=%u role=%u\n",d,phase,q,global_newshf_dual_preflight_state[0],global_newshf_fault,newshf_validation_slots[0].role);CHECK(global_newshf_dual_preflight_state[0]==1&&!global_newshf_fault);
  CHECK(global_newshf_used_resources==0x1ffu);finish_valid();
 }
 CHECK(soft_cases>=20);
 /* Each missing/malformed new resource declines the entire optional group,
  * but preserves independent bank10 HD. Root changes reload rather than leak. */
 const char *root=resource_root;const char *modes[]={"missing","corrupt","header","trailing"};
 for(unsigned m=0;m<4;m++)for(unsigned n=0;n<10;n++){
  char path[4096];snprintf(path,sizeof(path),"%s/%s-large%u",root,modes[m],n);resource_root=path;
  l_setup(4,false);birth_at(0,0,1,110,80,0);quartet();CHECK(global_newshf_contributed);
  l_birth(1,6,3,180,80);quartet();CHECK(!global_newshf_fault&&global_newshf_used_resources==0x1ffu);finish_valid();
  for(unsigned phase=18;phase<28;phase++)CHECK(!global_newshf_rgba[phase]);
 }
 resource_root=root;
 /* Actual later-owner transfer retains NEWSHI source dependency at final
  * and cache, not just the synthetic owner-bit erasure test above. */
 for(unsigned cached=0;cached<2;cached++){
  l_setup(4,false);l_birth(0,6,3,110,80);quartet();talon();CHECK(global_newshf_contributed&&global_talon_contributed);
  if(cached)finish_valid();Uint8 saved=large_bank[100];large_bank[100]^=1;
  if(cached){global_newshf_check_cache();CHECK(!ready&&!last_output_valid);}else finish_invalid();large_bank[100]=saved;
 }
 /* Every optional new-group pointer retires on root switch/shutdown. */
 l_setup(4,false);for(unsigned phase=0;phase<28;phase++)CHECK(global_newshf_group_ready(phase));global_newshf_shutdown();
 for(unsigned i=0;i<28;i++)CHECK(!global_newshf_rgba[i]);
 printf("large-newshi PASS cases=%u checks=%u\n",cases,checks);return 0;
}
