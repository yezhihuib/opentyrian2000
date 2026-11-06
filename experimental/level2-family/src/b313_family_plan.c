#include "b313_family_plan.h"
#include <string.h>
/* Same fixed record313..316 graphics mapping already verified against hdt.
 * Every real actor callback retains the engine's own20-cycle dwell schedule. */
static const unsigned bases[4][3]={{191,195,199},{193,197,201},{153,157,161},{155,159,163}};
static const unsigned cycle_phase[20]={0,0,0,0,1,1,2,2,1,1,0,0,0,0,0,0,0,0,0,0};
static bool reject(B313FamilyPlan *out,unsigned why){out->reasons=why;return false;}
bool b313_family_plan(const B313FamilyCall *call,B313FamilyPlan *out)
{
 if(!out)return false;
 memset(out,0,sizeof(*out));
 if(!call)return reject(out,B313FP_INPUT);
 const B313Snapshot *a=&call->actor;
 if(a->type<313||a->type>316||a->record!=a->type||!a->record_verified||!a->graphics_verified||
    a->slot>=100||a->pool>=4||a->bank!=20||!a->sheet_identity||!a->data_identity||
    a->avail||a->size!=1||a->damaged||a->scoreitem)return reject(out,B313FP_IDENTITY);
 if(call->density!=8||a->filter)return reject(out,B313FP_MODE);
 unsigned component=a->type-313;
 if(a->cycle<1||a->cycle>20)return reject(out,B313FP_PHASE);
 unsigned phase=cycle_phase[a->cycle-1];
 if(a->base!=bases[component][phase])return reject(out,B313FP_PHASE);
 unsigned q=call->part==0?0:call->part==1?1:call->part==19?2:call->part==20?3:4;
 if(q==4)return reject(out,B313FP_PART);
 /* Reject original raw-RLE row wrapping and partial/offscreen native calls.
  * Bounds precede arithmetic; x/y may be any signed caller input. */
 if(call->surface_width!=320||call->surface_height!=200||call->surface_pitch!=320||
    call->x<0||call->x>308||call->y<0||call->y>186)return reject(out,B313FP_GEOMETRY);
 out->component=component;out->phase=phase;out->cycle=a->cycle;out->part=call->part;
 out->part_x=(int)(q%2)*12;out->part_y=(int)(q/2)*14;
 out->actor_x=call->x-out->part_x;out->actor_y=call->y-out->part_y;
 out->atlas_component_x=(int)(component%2)*24;
 out->atlas_component_y=component<2?28:0;
 out->atlas_tile_x=out->atlas_component_x+out->part_x;
 out->atlas_tile_y=out->atlas_component_y+out->part_y;
 out->source_x_hd=out->atlas_tile_x*8;out->source_y_hd=out->atlas_tile_y*8;
 out->destination_x=call->x;out->destination_y=call->y;
 out->destination_x_hd=call->x*8;out->destination_y_hd=call->y*8;
 out->width=12;out->height=14;out->width_hd=96;out->height_hd=112;
 out->planned=true;
 /* Success means coordinates only. It does not validate the caller's source
  * assertion, lifetime, current SDL context, assets, or suppression/occlusion. */
 return true;
}
