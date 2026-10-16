/* SPDX-License-Identifier: GPL-2.0-or-later
 * One actual JE_drawOptions transaction leases the original right-slot icon.
 * Rendering occurs only in the newly filled SDL texture; output/fade/canvas
 * storage is deliberately not a cache for this independently optional layer. */
static HudStormView storm_view(SDL_Surface *s)
{
 HudStormView v={0};
 if(s) {
  v.surface=s;v.pixels=s->pixels;v.format=s->format;
  v.width=s->w;v.height=s->h;v.pitch=s->pitch;
  if(s->format){v.bits=s->format->BitsPerPixel;v.bytes=s->format->BytesPerPixel;}
 }
 return v;
}
static HudStormSource storm_source(void)
{
 const Sprite *s=&sprite_table[OPTION_SHAPES].sprite[37];
 HudStormSource source={s->data,s->size,s->width,s->height,sprite_table[OPTION_SHAPES].count};
 return source;
}
static bool storm_scope(void)
{
 return episodeNum==1&&((lvlFileNum==9&&initialDifficulty==DIFFICULTY_NORMAL)||
  (lvlFileNum==15&&initialDifficulty==DIFFICULTY_HARD))&&!xmas&&!isNetworkGame&&
  !twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!play_demo&&!record_demo&&
  !onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&!timedBattleMode&&
  !bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent&&
  player[0].items.sidekick[LEFT_SIDEKICK]==0&&player[0].items.sidekick[RIGHT_SIDEKICK]==9&&
  options[9].icongr==38&&options[9].wpnum==88&&options[9].ammo==6&&
  player[0].sidekick[RIGHT_SIDEKICK].style==0&&player[0].sidekick[RIGHT_SIDEKICK].charge==0;
}
static void storm_start(SDL_Surface *s)
{
 HudStormView v=storm_view(s);HudStormSource source=storm_source();
 (void)hud_storm_start(game_probe_assets,&v,&source);
}
void render_mirror_hud_storm_begin(SDL_Surface *s,unsigned slot,unsigned option,unsigned icon,int x,int y)
{
 HudStormView v=storm_view(s);HudStormSource source=storm_source();
 hud_storm_begin(&v,&source,slot,option,icon,x,y,storm_scope());
}
void render_mirror_hud_storm_end(SDL_Surface *s,unsigned slot)
{
 HudStormView v=storm_view(s);HudStormSource source=storm_source();
 hud_storm_end(&v,&source,slot,storm_scope());
}
void render_mirror_hud_storm_source_reset(unsigned table)
{if(table==OPTION_SHAPES)hud_storm_reset();}
static void storm_pixel(SDL_Surface *s,const Uint8 *p)
{HudStormView v=storm_view(s);hud_storm_pixel(&v,p);}
static void storm_rect(SDL_Surface *s,const SDL_Rect *r)
{
 HudStormView v=storm_view(s);
 if(!s)return;
 /* SDL_FillRect applies this same surface clip. An incomplete clear cannot
  * establish ownership; subsequent pixel callbacks are not synthesized here. */
 int64_t x=r?r->x:0,y=r?r->y:0,w=r?r->w:s->w,h=r?r->h:s->h;
 int64_t cx=s->clip_rect.x,cy=s->clip_rect.y,cw=s->clip_rect.w,ch=s->clip_rect.h;
 if(cx<0||cy<0||cw<0||ch<0||cx+cw>s->w||cy+ch>s->h) {
  hud_storm_rect(&v,0,0,320,200);return;
 }
 if(w<=0||h<=0)return;
 int64_t x1=MIN(x+w,cx+cw),y1=MIN(y+h,cy+ch);
 x=MAX(x,cx);y=MAX(y,cy);
 if(x1<=x||y1<=y)return;
 /* A nonempty intersection lies entirely in the validated320x200 surface. */
 hud_storm_rect(&v,(int)x,(int)y,(int)(x1-x),(int)(y1-y));
}
static void storm_resume(void)
{HudStormView v=storm_view(VGAScreenSeg);hud_storm_resume(&v,storm_scope());}
static void storm_present(void *pixels,int pitch)
{
 HudStormView v=storm_view(VGAScreenSeg);HudStormSource source=storm_source();
 (void)hud_storm_present(&v,&source,!reject_reason&&storm_scope()&&
  mirror_enabled()&&!game_probe_original_reference,rgb_palette,output->pixels,output->pitch,
  pixels,pitch,output->w,output->h,game_probe_density);
}
