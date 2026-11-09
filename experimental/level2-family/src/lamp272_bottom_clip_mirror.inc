/* SPDX-License-Identifier: GPL-2.0-or-later
 * Separate default-off bottom-edge adapter. Original full-body path is unchanged.
 * This cannot create a level/event/frame lease: every original identity, source,
 * palette, ordered native-writer and Present gate remains authoritative. */
#include "lamp272_bottom_clip_contract.h"
static struct {
 bool enabled,native,contributed;
 uint64_t frame,generation,epoch;
 Lamp272BottomClipPlan plan;
 unsigned pixels;
 uint8_t source[168];
} lamp272_bottom_clip;
static bool lamp272_bottom_clip_requested(void)
{const char *p=getenv("LAMP272_BOTTOM_CLIP_ENABLE");return p&&!strcmp(p,"1");}
static void lamp272_bottom_clip_reset(void)
{memset(&lamp272_bottom_clip,0,sizeof lamp272_bottom_clip);}
static void lamp272_bottom_clip_tick(void)
{lamp272_bottom_clip_reset();lamp272_bottom_clip.enabled=lamp272_bottom_clip_requested();}

static bool lamp272_bottom_clip_tile(SDL_Surface *surface,unsigned slot,int x,int y,
                                 Sprite2_array *sheet,unsigned base,int part,int filter)
{
 Lamp272BottomClipPlan plan;
 if(!lamp272_bottom_clip.enabled||!lamp272_bottom_clip_requested()||
    !lamp272_bottom_clip_plan(x,y,part,&plan)||!private_lamp272_mode()||
    slot>=100||enemy[slot].enemytype!=272)return false;
 if(!fc.frame_active||fc.frame_failed||!private_lamp272_witness(slot))return false;
 if(private_lamp272_frame.contributed&&!private_lamp272_dependencies()){private_lamp272_fail();return false;}
 if((int64_t)plan.body_x!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||
    (int64_t)plan.body_y!=(int64_t)enemy[slot].ey-7)return false;
 if(!private_lamp272_frame_scope()||sheet!=enemy[slot].sprite2s||!sheet||filter||
    !private_lamp272_shape(slot,false)||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||
    !private_lamp272_source(*sheet)||!private_lamp272_colors()||!private_lamp272_ready())return false;
 uint8_t source[168];
 if(!lamp272_top_clip_source(sheet->data,sheet->size,base+(unsigned)part,source))return false;
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||lamp272_native||suppress||surface!=game_screen||surface!=VGAScreen||
    !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
    !b313_family_writer_draw_ready(fc_frame)||!family_prepare_canvas()){family_fault(FC_SOURCE);return false;}
 static const int parts[4]={0,1,19,20};
 if(!private_lamp272_frame.quartet){
  if(part||private_lamp272_frame.mask[slot]){family_fault(FC_ORDER);return false;}
  private_lamp272_frame.quartet=true;private_lamp272_frame.slot=slot;private_lamp272_frame.base=base;
  private_lamp272_frame.x=plan.body_x;private_lamp272_frame.y=plan.body_y;private_lamp272_frame.next=0;
 }
 if(private_lamp272_frame.slot!=slot||private_lamp272_frame.base!=base||
    private_lamp272_frame.next>=4||part!=parts[private_lamp272_frame.next]||
    plan.body_x!=private_lamp272_frame.x||plan.body_y!=private_lamp272_frame.y){family_fault(FC_ORDER);return false;}
 unsigned k=0;while(k<4&&private_lamp272_images[k].base!=base)++k;
 if(k==4){family_fault(FC_SOURCE);return false;}
 lamp272_bottom_clip.native=lamp272_bottom_clip.contributed=true;
 lamp272_bottom_clip.plan=plan;lamp272_bottom_clip.pixels=0;lamp272_bottom_clip.frame=fc_frame;
 lamp272_bottom_clip.generation=private_lamp272_slots[slot].generation;
 lamp272_bottom_clip.epoch=private_lamp272_slots[slot].epoch;
 memcpy(lamp272_bottom_clip.source,source,sizeof source);
 lamp272_native=true;lamp272_image=k;
 private_lamp272_frame.contributed=true;
 private_lamp272_frame.generations[slot]=private_lamp272_slots[slot].generation;
 private_lamp272_frame.used|=1u<<k;
 return true;
}
static bool lamp272_bottom_clip_pixel(unsigned x,unsigned y,int style)
{
 if(!lamp272_bottom_clip.native)return false;
 const Lamp272BottomClipPlan *p=&lamp272_bottom_clip.plan;
 unsigned n=lamp272_bottom_clip.pixels;
 if(!lamp272_native||fc_frame!=lamp272_bottom_clip.frame||!lamp272_bottom_clip_requested()||
    !lamp272_bottom_clip_store(p,n,x,y,style)||
    expected[y*320+x]!=lamp272_bottom_clip.source[n]){family_fault(FC_ORDER);return true;}
 const Asset *a=private_lamp272_resources.member+lamp272_image;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t off=(y*8+sy)*2560+x*8+sx;
  const Uint8 *color=a->rgba+lamp272_bottom_clip_rgba_offset(p,n,sx,sy);
  ((Uint32 *)canvas->pixels)[off]=0xff000000u|((Uint32)color[0]<<16)|((Uint32)color[1]<<8)|color[2];
  hd_owner[off]=1;cloud_owner[off]=0;green_first[off]=0;
 }
 longface573_clear(y*320+x);gray325_clear(y*320+x);lamp272_owned[y*320+x]=1;
 triple275_clear(y*320+x);private_ember269_clear(y*320+x);selected[y*320+x]=1;
 ++lamp272_bottom_clip.pixels;return true;
}
static void lamp272_bottom_clip_end(void)
{
 if(!lamp272_bottom_clip.native)return;
 unsigned slot=private_lamp272_frame.slot;
 if(!lamp272_native||lamp272_bottom_clip.pixels!=lamp272_bottom_clip.plan.stores||
    !lamp272_bottom_clip_requested()||lamp272_bottom_clip.frame!=fc_frame||
    !private_lamp272_witness(slot)||lamp272_bottom_clip.generation!=private_lamp272_slots[slot].generation||
    lamp272_bottom_clip.epoch!=private_lamp272_slots[slot].epoch||
    !b313_family_writer_draw_ready(fc_frame)){family_fault(FC_ORDER);}
 else {
  private_lamp272_frame.mask[slot]|=1u<<private_lamp272_frame.next;
  if(++private_lamp272_frame.next==4)private_lamp272_frame.quartet=false;
 }
 lamp272_bottom_clip.native=false;lamp272_native=false;
}
