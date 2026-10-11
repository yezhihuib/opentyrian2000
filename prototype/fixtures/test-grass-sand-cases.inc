/* Independent finite Layer1 oracle, supplementing the existing purple suite.
 * All payloads are synthetic test inputs. No art or runtime claim is made. */
static void grass_cases(void)
{
 CHECK(sizeof(assets)/sizeof(*assets)==321);CHECK(sizeof(terrain_sources)/sizeof(*terrain_sources)==162);
 for(unsigned id=0;id<=1000;id++){
  int expected=-1;for(unsigned j=0;j<9;j++)if(id==grass[j])expected=312+(int)j;
  CHECK(grass_sand_slot(id)==expected);
 }
 CHECK(grass_sand_slot(UINT_MAX)==-1);
 for(unsigned j=0;j<9;j++)for(unsigned layer=0;layer<5;layer++){
  reset("full8");render_mirror_bind_terrain(layer,grass[j],bank[layer][grass[j]]);
  CHECK(terrain_source_count==(unsigned)(layer==1));
  CHECK(draw_pointer(bank[layer][grass[j]],MIRROR_NORMAL)==(unsigned)(layer==1));
  CHECK(draws==(unsigned)(layer==1)&&traces==draws&&!suppress);
 }
 for(unsigned byte=0;byte<256;byte++)for(unsigned j=0;j<9;j++){
  reset("full8");render_mirror_map_begin((char)byte);render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);
  CHECK(terrain_source_count==(unsigned)(byte=='Z'||byte=='z'));
 }
 reset("full8");render_mirror_bind_terrain(UINT_MAX,grass[0],bank[1][grass[0]]);render_mirror_bind_terrain(1,UINT_MAX,bank[1][grass[0]]);CHECK(!terrain_source_count);
 /* Content-equal but distinct pointers, wrong-layer pointers, unknown IDs,
  * and null map cells cannot alias a registered grass/sand member. */
 reset("full8");for(unsigned j=0;j<9;j++)render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);
 for(unsigned layer=0;layer<5;layer++)if(layer!=1)for(unsigned j=0;j<9;j++){
  CHECK(!draw_pointer(bank[layer][grass[j]],MIRROR_NORMAL));CHECK(!draws&&!traces);
 }
 for(unsigned j=0;j<sizeof(forest)/sizeof(*forest);j++){
  CHECK(!accepted(1,forest[j]));render_mirror_bind_terrain(1,forest[j],bank[1][forest[j]]);
  CHECK(terrain_source_count==9);CHECK(!draw_pointer(bank[1][forest[j]],MIRROR_NORMAL));CHECK(!draws&&!traces);
 }
 reset("full8");render_mirror_bind_terrain(1,grass[0],NULL);CHECK(!draw_pointer(NULL,MIRROR_NORMAL));CHECK(!draws&&!traces);
 for(unsigned unknown=0;unknown<601;unknown++)if(!accepted(1,unknown)&&!accepted(2,unknown)&&!accepted(3,unknown)){
  reset("full8");terrain_sources[0].data=bank[1][unknown];terrain_sources[0].id=unknown;terrain_source_count=1;
  CHECK(!draw_pointer(bank[1][unknown],MIRROR_NORMAL));CHECK(!draws&&!traces);
  for(unsigned slot=0;slot<321;slot++)CHECK(!assets[slot].initialized);
 }
 /* Every current disabled guard and the original drawable NORMAL contract. */
 for(unsigned j=0;j<9;j++)for(int flag=0;flag<7;flag++){
  reset("full8");render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);
  if(flag==0)game_probe_missing=true;
  if(flag==1)game_probe_invalid=true;
  if(flag==2)game_probe_density=1;
  if(flag==3)game_probe_assets=NULL;
  if(flag==4)game_probe_scene_assets=0;
  if(flag==5)active=false;
  if(flag==6)reject_reason="test";
  CHECK(!draw_pointer(bank[1][grass[j]],MIRROR_NORMAL));CHECK(!draws&&!traces&&!suppress);
 }
 for(unsigned j=0;j<9;j++)for(int style=MIRROR_NORMAL;style<=MIRROR_SHADOW;style++){
  reset("full8");render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);
  CHECK(draw_pointer(bank[1][grass[j]],style)==1);CHECK(draws==1&&traces==1&&trace_style[0]==style&&!suppress);
 }
 /* The prior Layer1 families forward supplied styles as well. The real
  * draw_background_1 callsite always supplies NORMAL; no new style route. */
 reset("full8");render_mirror_bind_terrain(1,grass[0],bank[1][grass[0]]);draw_success=false;
 CHECK(!draw_pointer(bank[1][grass[0]],MIRROR_NORMAL));CHECK(draws==1&&traces==1&&!trace_mirrored[0]&&!suppress);
 reset("empty");for(unsigned j=0;j<9;j++){
  render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);CHECK(!draw_pointer(bank[1][grass[j]],MIRROR_NORMAL));
  CHECK(!draws&&!traces&&!suppress&&assets[312+j].initialized&&!assets[312+j].valid);
 }
 for(unsigned j=0;j<9;j++)for(unsigned bad=0;bad<38;bad++){
  char label[80];snprintf(label,sizeof(label),"grass%u-bad%u",grass[j],bad);reset(label);
  render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);CHECK(!draw_pointer(bank[1][grass[j]],MIRROR_NORMAL));
  CHECK(!draws&&!traces&&!suppress&&assets[312+j].initialized&&!assets[312+j].valid);
  /* Every malformed member preserves unrelated prior64/131/purple and all
   * other family slots. Cached rejection is stable across path switches. */
  choose("full8");unsigned other=(j+1)%9;render_mirror_bind_terrain(1,grass[other],bank[1][grass[other]]);
  render_mirror_bind_terrain(2,64,bank[2][64]);render_mirror_bind_terrain(3,131,bank[3][131]);render_mirror_bind_terrain(3,169,bank[3][169]);
  CHECK(!draw_pointer(bank[1][grass[j]],MIRROR_NORMAL));CHECK(!draws&&!traces);
  CHECK(draw_pointer(bank[1][grass[other]],MIRROR_NORMAL)==1);CHECK(assets[312+other].valid);
  CHECK(draw_pointer(bank[2][64],MIRROR_NORMAL)==1);CHECK(assets[199].valid);CHECK(!draw_pointer(bank[2][64],MIRROR_BLEND));CHECK(!draws&&!traces);
  CHECK(draw_pointer(bank[3][131],MIRROR_NORMAL)==1);CHECK(assets[277].valid);CHECK(!draw_pointer(bank[3][131],MIRROR_SHADOW));CHECK(!draws&&!traces);
  CHECK(draw_pointer(bank[3][169],MIRROR_NORMAL)==1);CHECK(assets[298].valid);
  reserved_untouched();
 }
 for(unsigned missing=0;missing<9;missing++){
  char label[80];snprintf(label,sizeof(label),"missing-grass%u",grass[missing]);reset(label);
  for(unsigned j=0;j<9;j++)render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);
  for(unsigned j=0;j<9;j++){CHECK(draw_pointer(bank[1][grass[j]],MIRROR_NORMAL)==(unsigned)(j!=missing));CHECK(draws==(unsigned)(j!=missing)&&traces==draws&&!suppress);}
 }
 reset("full4");for(unsigned j=0;j<9;j++){
  render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);CHECK(draw_pointer(bank[1][grass[j]],MIRROR_NORMAL)==1);CHECK(assets[312+j].valid&&assets[312+j].density==4);
 }
 /* Exact replacement bits, stable row ordering, all nine start offsets,
  * forward/reverse ordering, and full/partial/null/unbound mixed rows. */
 reset("full8");for(unsigned j=0;j<9;j++)render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);
 const unsigned masks[]={0,1,2048,0x555,0xaaa,0xfff,0xa91};
 for(unsigned start=0;start<9;start++)for(unsigned reverse=0;reverse<2;reverse++)for(unsigned m=0;m<7;m++){
  Uint8 *row[12];unsigned ids[12],n=0;
  for(unsigned j=0;j<12;j++){ids[j]=grass[(start+(reverse?11-j:j))%9];row[j]=(masks[m]&(1u<<j))?bank[1][ids[j]]:j%2?NULL:bank[4][ids[j]];}
  clear_draws();CHECK(render_mirror_terrain_row(game_screen,16,-13,row,MIRROR_NORMAL)==masks[m]);
  for(unsigned j=0;j<12;j++)if(masks[m]&(1u<<j)){CHECK(draw_ids[n]==ids[j]&&trace_ids[n]==ids[j]);CHECK(draw_x[n]==16+(int)j*24&&draw_y[n]==-13&&trace_style[n]==MIRROR_NORMAL&&trace_mirrored[n]);n++;}
  CHECK(draws==n&&traces==n&&!suppress);reserved_untouched();
 }
 /* Co-residency with every previously allocated cache position, including
  * all entity/ship/effect slots. Sentinel metadata and payload pointers must
  * survive all nine terrain loads byte-for-byte; no prior slot is repurposed. */
 reset("full8");Asset prior[312];
 for(unsigned i=0;i<312;i++){
  Uint8 *sentinel=malloc(1);CHECK(sentinel);*sentinel=(Uint8)i;
  assets[i]=(Asset){true,(i%2)==0,101+(int)(i%3),(int)(1000+i),24,28,6,7,8,sentinel};
 }
 memcpy(prior,assets,sizeof(prior));
 for(unsigned j=0;j<9;j++){
  render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);CHECK(draw_pointer(bank[1][grass[j]],MIRROR_NORMAL)==1);
  CHECK(!memcmp(prior,assets,sizeof(prior)));for(unsigned i=0;i<312;i++)CHECK(assets[i].rgba[0]==(Uint8)i);
 }
 reset("full8");for(unsigned j=0;j<9;j++){render_mirror_bind_terrain(1,grass[j],bank[1][grass[j]]);CHECK(draw_pointer(bank[1][grass[j]],MIRROR_NORMAL)==1);}
 /* Numeric coincidence with old asset slot IDs must not touch their cache.
  * First-binding precedence remains exact, including cross-family aliases. */
 for(unsigned slot=0;slot<312;slot++)CHECK(!assets[slot].initialized);
 reset("full8");render_mirror_bind_terrain(1,66,bank[1][66]);render_mirror_bind_terrain(3,131,bank[1][66]);
 CHECK(draw_pointer(bank[1][66],MIRROR_NORMAL)==1);CHECK(draw_ids[0]==66&&!assets[277].initialized);
 render_mirror_map_begin('Z');render_mirror_bind_terrain(3,131,bank[1][66]);render_mirror_bind_terrain(1,66,bank[1][66]);
 CHECK(draw_pointer(bank[1][66],MIRROR_NORMAL)==1);CHECK(draw_ids[0]==131);
 reset("full8");for(unsigned i=0;i<601;i++)render_mirror_bind_terrain(1,66,bank[1][i]);CHECK(terrain_source_count==162);
 for(unsigned i=0;i<162;i++)CHECK(terrain_sources[i].data==bank[1][i]&&terrain_sources[i].id==66);
 CHECK(draw_pointer(bank[1][161],MIRROR_NORMAL)==1);CHECK(!draw_pointer(bank[1][162],MIRROR_NORMAL));CHECK(!draws&&!traces);
 render_mirror_map_begin('Z');CHECK(!terrain_source_count);CHECK(!draw_pointer(bank[1][161],MIRROR_NORMAL));
}
