"""Normal turret body only. Isolated native-observer tests; no game execution."""
import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'experimental/level2-family/src'
TEXT=(SRC/'turret273_family_mirror.inc').read_text()
spec=importlib.util.spec_from_file_location('turret_launcher',ROOT/'scripts/launch_level2_family.py')
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)


def function(name):
    return re.search(r'(?:static )?(?:bool|void|uint64_t|int) '+name+r'\([^\n]*\)\n\{.*?\n\}',TEXT,re.S).group()


def run_c(source):
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp);(p/'test.c').write_text(source)
        result=subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-unused-const-variable','-I',str(SRC),str(p/'test.c'),'-o',str(p/'test')],capture_output=True,text=True)
        if result.returncode:raise AssertionError(result.stderr)
        subprocess.run([str(p/'test')],check=True,capture_output=True,text=True)


class Turret273Tests(unittest.TestCase):
    def test_launcher_off_and_explicit_combination(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);b=p/'never-run';b.write_text('');b.chmod(0o700)
            args=['--data',temp,'--binary',str(b)]
            inherited={'TURRET273_COMBAT_ENABLE':'1','TURRET273_BODY_ASSET_DIR':'wrong','TURRET273_OTHER':'1','FORK284_ENABLE':'1'}
            for flags in ([],['--hd']):
                plan,env=launcher.build_plan(launcher.parser().parse_args(args+flags),inherited)
                self.assertFalse(plan['turret273_enabled']);self.assertFalse(any(k.startswith('TURRET273_') for k in env))
            with self.assertRaisesRegex(ValueError,'requires --hd'):
                launcher.build_plan(launcher.parser().parse_args(args+['--turret273']),{})
            plan,env=launcher.build_plan(launcher.parser().parse_args(args+['--hd','--turret273','--fork284']),{})
            self.assertEqual(plan['assets_sha256_verified'],52);self.assertEqual(plan['turret273_assets_sha256_verified'],9)
            self.assertTrue(plan['turret273_enabled'] and plan['fork284_enabled']);self.assertFalse(plan['game_started'])
            self.assertNotIn('PROJECTILE304_ENABLE',env)

    def test_all_nine_assets_and_damage_rejection(self):
        self.assertEqual(set(launcher.TURRET273_SHA256),{169,193,195,197,199,201,203,205,207})
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);b=p/'never-run';b.write_text('');b.chmod(0o700)
            directory=p/launcher.REUSED_ROOT;directory.mkdir(parents=True)
            for base in launcher.TURRET273_SHA256:
                name=f'enemy-newshd-{base}-8.hda';raw=(ROOT/launcher.REUSED_ROOT/name).read_bytes()
                self.assertEqual(set(raw[31::4]),{255});(directory/name).write_bytes(raw)
            name='enemy-newshd-207-8.hda';raw=(directory/name).read_bytes();(directory/name).write_bytes(raw[:-1]+b'\x00')
            args=launcher.parser().parse_args(['--data',temp,'--binary',str(b),'--hd','--turret273'])
            with patch.object(launcher,'verify_assets',return_value=52),self.assertRaisesRegex(ValueError,'Changed Turret273'):
                launcher.build_plan(args,{},p)

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_continuous_twenty_cycle_animation(self):
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include "turret273_family.h"
static struct {bool live;unsigned cycle,gate;uint64_t phase_tick;Turret273Birth birth;} tp_slots[100];
static struct {int ex;unsigned enemycycle,aniactive,eshotwait;} enemy[100];
static uint64_t fc_frame,tp_phase_observations;static int tempMapXOfs;static unsigned retired;
static bool scope=true,witness=true,shape=true;
static bool tp_scope(void){return scope;}
static bool tp_witness(unsigned s){(void)s;return witness;}
static bool tp_shape(unsigned s,unsigned stage){(void)s;(void)stage;return shape&&enemy[s].aniactive==1;}
static void render_mirror_turret273_retired(unsigned s){retired++;tp_slots[s].live=false;}
''' +function('render_mirror_turret273_enemy_animated')+r'''
int main(void){
 unsigned s=25;tp_slots[s].live=true;tp_slots[s].phase_tick=UINT64_MAX;enemy[s].ex=50;enemy[s].aniactive=1;
 for(unsigned i=1;i<=60;i++){
  fc_frame=i;enemy[s].enemycycle=(i-1)%20+1;
  /* The normal body's firing countdown changes independently, never gate2. */
  enemy[s].eshotwait=20-(i%20);
  render_mirror_turret273_enemy_animated(s);
  assert(!retired&&tp_slots[s].cycle==enemy[s].enemycycle&&tp_slots[s].gate==1);
 }
 assert(tp_phase_observations==60&&tp_slots[s].birth.phase_observations==60);
 render_mirror_turret273_enemy_animated(s);assert(retired==1); /* duplicate frame */
 tp_slots[s].live=true;fc_frame++;enemy[s].aniactive=2;render_mirror_turret273_enemy_animated(s);assert(retired==2);
 tp_slots[s].live=true;enemy[s].aniactive=1;enemy[s].enemycycle=7;render_mirror_turret273_enemy_animated(s);assert(retired==3);
 tp_slots[s].live=true;enemy[s].enemycycle=1;enemy[s].ex=300;render_mirror_turret273_enemy_animated(s);assert(retired==4);
 render_mirror_turret273_enemy_animated(100);assert(retired==4);
 return 0;
}
'''
        run_c(source)

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_nine_native_images_order_and_retirement(self):
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "turret273_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
#include "turret273_family_pins.inc"
#define MIRROR_NORMAL 0
#define MIRROR_SHADOW 1
#define MIRROR_BLEND 2
#define FC_ORDER 1
static uint8_t tp_owned[64000],tp_shadows[64000],selected[64000],expected[64000],native[64000];
static uint8_t hd_owner[4096000],cloud_owner[4096000];static unsigned green_first[4096000];static uint32_t rgb[4096000];
static struct {void *pixels;} surface={rgb},*canvas=&surface;static void *fc_source_pixels=native;
static struct {bool active,pending,contributed;unsigned slot,part,pixels,image;Turret273Draw draw[100];Turret273Write writes[100][672];} tp_frame;
static uint64_t tp_blend_retirements,tp_normal_retirements,tp_shadow_writes,tp_contract_faults;
static unsigned failure,clears;
typedef struct {uint8_t *rgba;} Asset;static uint8_t rgba[172032];static struct {Asset member[9];} tp_resources;
static void tp_fail(unsigned r){failure=r;tp_frame.active=tp_frame.pending=false;}
static void family_fault(unsigned r){(void)r;}
static void lamp272_clear(unsigned x){(void)x;clears++;}
#define triple275_clear lamp272_clear
#define private_ember269_clear lamp272_clear
#define gray325_clear lamp272_clear
#define longface573_clear lamp272_clear
static uint32_t blend_rgba(uint32_t dst,const uint8_t *art,unsigned a){(void)dst;assert(a==255);return 0xff000000u|art[0]<<16|art[1]<<8|art[2];}
'''+'\n'.join(function(n) for n in ('tp_retire','tp_pixel','tp_shadow'))+r'''
int main(void){
 assert(tp_records[0].record==273&&tp_events[0].event==476&&tp_events[1].event==477);
 for(unsigned i=0;i<172032;i+=4){rgba[i]=60;rgba[i+1]=80;rgba[i+2]=120;rgba[i+3]=255;}
 for(unsigned image=0;image<9;image++){
  memset(&tp_frame,0,sizeof tp_frame);tp_frame.slot=25;tp_frame.image=image;tp_frame.pending=true;tp_frame.contributed=true;
  tp_resources.member[image].rgba=rgba;Turret273Draw *d=tp_frame.draw+25;d->x=40;d->y=20;
  assert(tp_images[image].extra==0&&tp_totals[image]==672);
  for(unsigned k=0;k<4;k++){
   tp_frame.part=k;tp_frame.active=true;tp_frame.pixels=0;
   for(unsigned i=0;i<tp_counts[image][k];i++){
    const Turret273Write *w=tp_native[image][k]+i;
    unsigned x=d->x+tp_px[k]+w->x,y=d->y+tp_py[k]+w->y,off=y*320+x;
    native[off]=expected[off]=w->index;assert(tp_pixel(x,y,MIRROR_NORMAL)&&!failure);
    assert(tp_owned[off]==26&&selected[off]&&rgb[y*8*2560+x*8]==0xff3c5078);
   }
  }
  assert(d->callback_count==672);
  unsigned off=20*320+40;assert(tp_retire(off,MIRROR_SHADOW)&&tp_owned[off]==26);tp_shadow(off);assert(tp_shadows[off]==1);
  assert(tp_retire(off,MIRROR_BLEND)&&!tp_owned[off]&&!tp_shadows[off]);
  tp_owned[off]=26;assert(tp_retire(off,MIRROR_NORMAL)&&!tp_owned[off]);
 }
 assert(clears==9*672*5&&tp_blend_retirements==9&&tp_normal_retirements==9&&tp_shadow_writes==9);
 tp_frame.part=0;tp_frame.pixels=0;tp_frame.active=true;assert(tp_pixel(0,0,MIRROR_NORMAL)&&failure==16);
 return 0;
}
'''
        run_c(source)

    def test_hooks_and_scope(self):
        canvas=(SRC/'b313_family_canvas_mirror.inc').read_text();native=(SRC/'tyrian2.c').read_text()
        for prefix in ('tp_','f284_'):
            self.assertLess(canvas.index(prefix+'retire((unsigned)off,style)'),canvas.index('if(f284_pixel'))
        # Preserve these gates while allowing later families before terrain.
        self.assertRegex(canvas,r'!turret_owned&&!linked_owned&&!linked_prop_owned&&!late_actor_owned&&!normal270_owned(?:&&![a-z0-9_]+)*&&!terrain_retire')
        self.assertIn('tp_write_current()',canvas);self.assertIn('!tp_finish()',canvas);self.assertIn('!tp_guard()',canvas)
        self.assertIn('tp_before_tile(slot,part)',canvas)
        self.assertIn('!f284_stream_matches(events)',TEXT)
        self.assertIn('e->ani!=20||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive!=1',TEXT)
        self.assertNotIn('turret273_emitter',TEXT)
        self.assertLess(native.index('render_mirror_turret273_enemy_animated(i);'),native.index('if (enemy[i].egr[enemy[i].enemycycle - 1] == 999)'))
        for suffix in ('event_begin','event_commit','level_begin','enemy_allocated','enemy_initialized','retired'):
            self.assertIn('render_mirror_turret273_'+suffix,native)
        self.assertEqual((SRC/'sprite.c').read_text().count('render_mirror_turret273_bank_changed(sprite2s);'),2)

if __name__=='__main__':unittest.main()
