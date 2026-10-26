/* Fresh current-source fixture adapter. Not a recovered historical test.
 * The runner generates this include by renaming only the existing fixture's
 * main and resolving its two relative include paths. No production edits.
 * Pause callbacks in that existing fixture are inactive-owner stubs; SHOP
 * presenter, sprites, sampler and common_menu_runs are production code. */
#include "shop_current_fixture.inc"
JE_byte shotAvail[MAX_PWEAPON];
PlayerShotDataType playerShotData[MAX_PWEAPON+1];
/* Isolated command-boundary negative witness: an idle write must never mutate
 * a retained static classic command, even when its last pixel is identical. */
static void retained_classic_boundary(void)
{
 memset(&sf,0,sizeof(sf));sf.stage=S_BUILD;sf.product=true;
 product_pixel(20*SF_W+20,77,0);REQUIRE(sf.count==1&&sf.event_count==1);
 struct SfCommand saved=sf.commands[0];struct SfEvent event_saved=sf.events[0];
 sf.static_count=sf.count;sf.static_events=sf.event_count;sf.updating=true;
 product_pixel(20*SF_W+20,88,0);
 REQUIRE(sf.count==2&&sf.event_count==2);
 REQUIRE(!memcmp(&saved,&sf.commands[0],sizeof(saved)));
 REQUIRE(!memcmp(&event_saved,&sf.events[0],sizeof(event_saved)));
 REQUIRE(sf.events[1].index==88);memset(&sf,0,sizeof(sf));
}
int main(int argc,char **argv)
{
 if(argc>1&&!strcmp(argv[1],"--core")){retained_classic_boundary();return pregame_baseline_main(argc-1,argv+1);}
 return typography_original_main(argc,argv);
}
