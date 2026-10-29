#!/usr/bin/env python3
"""Output-only bounded61 observer transformations; no game or build execution.

Input is a mapping of three or four complete current production C texts. Output
has the same keys. Ordinary diagnostic TSV rows are retained at tick0 only;
headers and stdout/stderr are always retained. Four custom logs observe actual
normal61 emission/dispatch/admission/final presentation at ticks140..260.
Neither event time150 nor a potential placement is an observed game tick.
"""
import re

FIRST, LAST = 140, 260
REQUIRED = frozenset(('game_probe.c', 'tyrian2.c', 'render_mirror.c'))
OPTIONAL = frozenset(('asset_debug.c',))
FRESH_TUS = ('asset_debug', 'entity_draw', 'game_probe', 'render_mirror', 'tyrian2')
INSTRUMENTED_TUS = ('asset_debug', 'game_probe', 'render_mirror', 'tyrian2')

LOG_FILTER = r'''
#include <stdarg.h>
/* Output only. Original arguments are evaluated before this wrapper runs;
 * no diagnostic return value is consumed by production control flow. */
static int projectile61_tickzero_fprintf(FILE *stream,const char *format,...)
{
 if(stream!=stdout&&stream!=stderr&&game_probe_tick!=0&&strchr(format,'%'))return 0;
 va_list args;va_start(args,format);int result=vfprintf(stream,format,args);va_end(args);return result;
}
#define fprintf projectile61_tickzero_fprintf
'''

ADMISSION_LOG = r'''
/* Defined before the ordinary-row filter: this independent finite diagnostic
 * records the real wrapper's mirrored result, not an inferred owner bit. */
static void projectile61_admission_log(int role,unsigned index,int x,int y,int part,int style,bool mirrored)
{
 if(!game_probe_enabled||game_probe_tick<140||game_probe_tick>260||role!=151||index!=61)return;
 static FILE *f;
 if(!f){f=fopen("actual61-admission.tsv","w");if(!f)abort();
  if(fprintf(f,"tick\tcurLoc\trole\tindex\tx\ty\tpart\tstyle\tmirrored\n")<0)abort();}
 if(fprintf(f,"%u\t%u\t%d\t%u\t%d\t%d\t%d\t%d\t%d\n",game_probe_tick,(unsigned)curLoc,role,index,x,y,part,style,mirrored)<0)abort();
 if(fflush(f))abort();
}
'''

SHOT_LOG = r'''
static void projectile61_actual_log(const char *kind,unsigned slot,int weapon,int actor_slot,int actor,int link,unsigned raw,unsigned index,int x,int y,unsigned animation,unsigned animation_max)
{
 if(!game_probe_enabled||game_probe_tick<140||game_probe_tick>260||index!=61)return;
 static FILE *f;
 if(!f){f=fopen("actual61-native.tsv","w");if(!f)abort();
  if(fprintf(f,"kind\ttick\tcurLoc\tslot\tweapon\tactor_slot\tactor\tlink\traw\tindex\tx\ty\tanimation\tanimation_max\n")<0)abort();}
 if(fprintf(f,"%s\t%u\t%u\t%u\t%d\t%d\t%d\t%d\t%u\t%u\t%d\t%d\t%u\t%u\n",kind,game_probe_tick,(unsigned)curLoc,slot,weapon,actor_slot,actor,link,raw,index,x,y,animation,animation_max)<0)abort();
 if(fflush(f))abort();
}
'''

FINISH_OBSERVER = r'''
/* Read-only final observer. Do not call ready/resource/cache mutators here.
 * No original state, owner bit, palette, actor, weapon or shot is changed. */
void render_mirror_finish(MirrorOutputKind kind,int lightx,int lighty)
{
 projectile61_observation_inner_finish(kind,lightx,lighty);
 if(!game_probe_enabled||game_probe_tick<140||game_probe_tick>260)return;
 static FILE *f;
 static bool palette_written;
 for(unsigned slot=0;slot<ENEMY_SHOT_MAX;slot++) {
  if(enemyShotAvail[slot]||enemyShot[slot].sgr+enemyShot[slot].animate!=61)continue;
  if(!f){f=fopen("actual61-final.tsv","w");if(!f)abort();
   if(fprintf(f,"tick\tcurLoc\tslot\tx\ty\tdensity\trole\tindex\tready\tlast_valid\tmember_mask\tcached\tfault\tresource_valid\tmetadata_ok\tpalette12_ok\tnormal_bank_ok\tnative_mask_ok\tlayout_ok\topaque_authored_total\topaque_visible_supported\topaque_owned\topaque_authored_not_classic\topaque_outside_native_mask\n")<0)abort();}
  if(!palette_written) {
   FILE *p=fopen("actual61-palette.tsv","w");if(!p)abort();
   if(fprintf(p,"tick\tindex\tr\tg\tb\traw32\n")<0)abort();
   for(unsigned c=0;c<256;c++)if(fprintf(p,"%u\t%u\t%u\t%u\t%u\t%08x\n",game_probe_tick,c,(rgb_palette[c]>>16)&255,(rgb_palette[c]>>8)&255,rgb_palette[c]&255,(unsigned)rgb_palette[c])<0)abort();
   if(fclose(p))abort();palette_written=true;
  }
  static const Uint32 colors[12]={0x380000,0x510000,0x6d0400,0x860400,0x9e0800,0xba0c00,0xd31400,0xdf3c00,0xe7610c,0xeb8a18,0xf3ae24,0xfbcb30};
  bool palette_ok=true;
  for(unsigned c=0;c<12;c++)if((rgb_palette[113+c]&0xffffffu)!=colors[c])palette_ok=false;
  const Asset *a=&projectile61_resources.member;
  bool metadata_ok=projectile61_resources.valid&&a->initialized&&a->valid&&
   a->bank==ASSET_ENEMY_PROJECTILE61&&a->index==61&&a->w==12&&a->h==14&&
   a->anchor_x==0&&a->anchor_y==0&&a->density==8&&a->rgba;
  bool normal_bank_ok=!xmas&&spriteSheet8.data&&spriteSheet8.data!=spriteSheet12.data&&
   spriteSheet8.size==32060&&asteroid1_stamp(spriteSheet8.data,spriteSheet8.size)==UINT64_C(0x2b63027f74aaa21e);
  Uint8 source[168]={0},mask[168]={0};unsigned occupied=0,left=0,right=0;
  bool mask_ok=normal_bank_ok&&decode_tile(spriteSheet8,61,source,mask,12,0,0);
  if(mask_ok)for(unsigned cell=0;cell<168;cell++)if(mask[cell]) {
   occupied++;if(cell%12<4)left++;if(cell%12>=8)right++;
  }
  mask_ok=mask_ok&&occupied==74&&left==37&&right==37;
  bool layout_ok=game_probe_density==8&&canvas&&output&&output->pixels&&output->format&&
   canvas->w==2560&&canvas->h==1600&&output->w==2560&&output->h==1600&&
   output->pitch>=2560*4&&output->format->format==SDL_PIXELFORMAT_ARGB8888&&
   global_projectile91_owner&&global_projectile91_capacity>=(size_t)2560*1600&&
   VGAScreenSeg&&VGAScreenSeg->pixels&&VGAScreenSeg->format&&
   VGAScreenSeg->w==320&&VGAScreenSeg->h==200&&VGAScreenSeg->pitch>=320&&
   VGAScreenSeg->format->format==SDL_PIXELFORMAT_INDEX8;
  bool observed_valid=ready&&last_output_valid&&global_projectile91_cached&&
   !global_projectile91_fault&&(global_projectile91_used_members&4u)&&
   metadata_ok&&palette_ok&&mask_ok&&layout_ok;
  int x=enemyShot[slot].sx,y=enemyShot[slot].sy;
  unsigned opaque_total=0,visible_supported=0,owned=0,witness=0,outside_mask=0;
  if(metadata_ok)for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
   const Uint8 *pixel=a->rgba+4*(ay*96+ax);if(pixel[3]!=255)continue;
   opaque_total++;
   if(!mask_ok||!mask[(ay/8)*12+ax/8]){outside_mask++;continue;}
   int px=x*8+ax,py=y*8+ay;
   /* Crop is the actual internal8 game-to-output x-24 mapping. Clipped
    * pixels are skipped individually, not used as an entire-tile shortcut. */
   if(px<24*8||px>=288*8||py<0||py>=184*8)continue;
   visible_supported++;
   if(!observed_valid)continue;
   size_t n=(size_t)py*2560+px;
   if(!global_projectile91_owner[n])continue;
   owned++;
   Uint32 got=((Uint32*)((Uint8*)output->pixels+py*output->pitch))[px-24*8];
   Uint32 want=0xff000000u|((Uint32)pixel[0]<<16)|((Uint32)pixel[1]<<8)|pixel[2];
   Uint32 classic=palette_rgb(((Uint8*)VGAScreenSeg->pixels)[(py/8)*VGAScreenSeg->pitch+px/8-24]);
   if(got==want&&got!=classic)witness++;
  }
  if(fprintf(f,"%u\t%u\t%u\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%u\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%u\t%u\t%u\t%u\t%u\n",game_probe_tick,(unsigned)curLoc,slot,x,y,game_probe_density,a->bank,a->index,ready,last_output_valid,global_projectile91_used_members,global_projectile91_cached,global_projectile91_fault,projectile61_resources.valid,metadata_ok,palette_ok,normal_bank_ok,mask_ok,layout_ok,opaque_total,visible_supported,owned,witness,outside_mask)<0)abort();
 }
 if(f&&fflush(f))abort();
}
'''

PROBE_MARKER = 'static unsigned int tick_limit = 600;'
ASSET_MARKER = 'static bool window_only,explosion_log_enabled;'
SHOT_DECL = 'inline static void blit_enemy(SDL_Surface *surface, unsigned int i, signed int x_offset, signed int y_offset, signed int sprite_offset);'
EMIT_MARKER = 'enemyShot[b].sgr = weapons[temp3].sg[tempPos];'
# This is the final statement of the real if/else dispatch, so the inserted
# read-only log runs AFTER either production draw call without changing it.
DRAW_MARKER = 'blit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);'
EMIT_CALL = 'projectile61_actual_log("emit",b,temp3,i,enemy[i].enemytype,enemy[i].linknum,enemyShot[b].sgr,enemyShot[b].sgr,enemyShot[b].sx,enemyShot[b].sy,enemyShot[b].animate,enemyShot[b].animax);'
DRAW_CALL = 'projectile61_actual_log("draw",z,-1,-1,-1,-1,enemyShot[z].sgr,sprite,enemyShot[z].sx,enemyShot[z].sy,enemyShot[z].animate,enemyShot[z].animax);'
ADMISSION_DECL = 'void game_probe_scene_draw(int role,unsigned int index,int x,int y,int part,int style,bool mirrored)\n{'
ADMISSION_CALL = ' projectile61_admission_log(role,index,x,y,part,style,mirrored);'
FINISH_DECL = 'void render_mirror_finish(MirrorOutputKind kind,int lightx,int lighty)'
RENAMED_FINISH_DECL = 'static void projectile61_observation_inner_finish(MirrorOutputKind kind,int lightx,int lighty)'


def _once(text, marker, replacement, label):
    if text.count(marker) != 1:
        raise ValueError('Expected exactly one production marker: ' + label)
    return text.replace(marker, replacement, 1)


def _diagnostics_only(text, label):
    # The known production calls discard their result. Reject an input drift
    # that could let dropped diagnostic output choose a gameplay branch.
    if re.search(r'(?:\breturn\s+|=\s*|\b(?:if|while|switch)\s*\(\s*)fprintf\s*\(', text):
        raise ValueError('Consumed fprintf return in ' + label)


def instrument(texts):
    """Return exact-marker output-only derivatives, never edit input/files."""
    from global_talon_reconstruction import extract
    if not isinstance(texts, dict) or not REQUIRED <= texts.keys() or not set(texts) <= REQUIRED | OPTIONAL:
        raise ValueError('Expected game_probe, tyrian2, renderer and optional asset_debug texts')
    if any(not isinstance(value, str) for value in texts.values()):
        raise ValueError('Expected complete source text strings')
    if any('projectile61_observation_inner_finish' in value or 'projectile61_actual_log' in value or 'projectile61_tickzero_fprintf' in value for value in texts.values()):
        raise ValueError('Refusing duplicate observer instrumentation')
    out = dict(texts)
    _diagnostics_only(texts['game_probe.c'], 'game_probe.c')
    out['game_probe.c'] = _once(out['game_probe.c'], PROBE_MARKER, ADMISSION_LOG + '\n' + LOG_FILTER + '\n' + PROBE_MARKER, 'probe filter')
    out['game_probe.c'] = _once(out['game_probe.c'], ADMISSION_DECL, ADMISSION_DECL + '\n' + ADMISSION_CALL, 'actual role151 admission')
    if 'asset_debug.c' in out:
        _diagnostics_only(texts['asset_debug.c'], 'asset_debug.c')
        out['asset_debug.c'] = _once(out['asset_debug.c'], ASSET_MARKER, LOG_FILTER + '\n' + ASSET_MARKER, 'asset output filter')
    out['tyrian2.c'] = _once(out['tyrian2.c'], SHOT_DECL, SHOT_LOG + '\n' + SHOT_DECL, 'shot logger declaration')
    out['tyrian2.c'] = _once(out['tyrian2.c'], EMIT_MARKER, EMIT_MARKER + '\n ' + EMIT_CALL, 'actual native emission')
    out['tyrian2.c'] = _once(out['tyrian2.c'], DRAW_MARKER, DRAW_MARKER + '\n ' + DRAW_CALL, 'completed native dispatch')
    original = extract(out['render_mirror.c'], 'render_mirror_finish')
    renamed = _once(original, FINISH_DECL, RENAMED_FINISH_DECL, 'finish signature')
    out['render_mirror.c'] = _once(out['render_mirror.c'], original, renamed + '\n' + FINISH_OBSERVER, 'finish body')
    return out
