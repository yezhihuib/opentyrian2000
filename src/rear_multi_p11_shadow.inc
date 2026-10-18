/* SPDX-License-Identifier: GPL-2.0-or-later
 * Record263/264/274/275 shadow pilots. Reuse each frozen head alpha, never its RGB.
 * No global bank8 binding; every command retains its admitted birth identity. */
static bool rear_p11_shadow_birth(const VulcanShadowCall *v)
{
 if(!v->rear||v->slot>=REAR_P1_SLOTS||v->generation!=rear_p1_state.generation||
    v->birth_identity!=rear_p1_state.birth_identity[v->slot])return false;
 const RearP1Birth *b=&rear_p1_state.birth[v->slot];
 return b->qualified&&(((b->record==263||b->record==264)&&b->mode==1)||
   ((b->record==274||b->record==275)&&b->mode==2))&&b->raw==v->index&&
  b->generation==v->generation;
}

static Asset *rear_p11_shadow_current(const VulcanShadowCall *v,SDL_Surface *surface,
 int x,int y,Sprite2_array bank,unsigned index)
{
 if(!rear_p11_shadow_birth(v))return NULL;
 RearP1Shot shot=rear_p1_shot(v->slot);
 if(!rear_p1_current(&rear_p1_state,v->slot,index,v->index,&shot,
    rear_p1_scope(),rear_p1_table(rear_p1_state.birth[v->slot].record),rear_p1_source(bank,v->index)))return NULL;
 /* First-level Normal only. Preserve the original shadow eligibility and
  * offset, including the last drawn lifetime tick whose counter is now zero. */
 if(lvlFileNum!=9||!background2||game_probe_density!=8||
    !rear_p1_view(surface,x,y)||x!=(int)playerShotData[v->slot].shotX+1||
    y!=(int)playerShotData[v->slot].shotY+(int)shadowYDist||y>=190)return NULL;
 return rear_p1_asset(v->index);
}

bool render_mirror_rear_p11_shadow(SDL_Surface *surface,int x,int y,Sprite2_array bank,
 unsigned index,unsigned slot,unsigned raw)
{
 render_mirror_shadow_end();
 if(slot>=REAR_P1_SLOTS||index!=raw||
    (rear_p1_state.birth[slot].record!=263&&rear_p1_state.birth[slot].record!=264&&
     rear_p1_state.birth[slot].record!=274&&rear_p1_state.birth[slot].record!=275))return false;
 VulcanShadowCall call={0};
 call.rear=true;call.slot=slot;call.index=index;
 call.generation=rear_p1_state.generation;call.birth_identity=rear_p1_state.birth_identity[slot];
 Asset *a=rear_p11_shadow_current(&call,surface,x,y,bank,index);
 if(!a||region_count>=sizeof(regions)/sizeof(regions[0]))return false;
 Uint8 source[12*14*2]={0};
 if(!decode_tile(bank,index,source,source+12*14,12,0,0))return false;
 call.surface=surface;call.pixels=surface->pixels;call.format=surface->format;
 call.canvas_pixels=canvas->pixels;call.canvas_pitch=canvas->pitch;
 call.pitch=surface->pitch;call.bank_data=bank.data;call.bank_size=bank.size;
 call.tick=mirror_logic_tick;call.x=x;call.y=y;call.shadow_rgba=a->rgba;
 memcpy(call.coverage,source+12*14,sizeof(call.coverage));
 call.live=true;vulcan_shadow=call;
 return true;
}
