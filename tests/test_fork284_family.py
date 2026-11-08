"""Isolated fork admission/alpha/order tests; never start SDL or a game."""
import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'experimental/level2-family/src'
TEXT = (SRC / 'fork284_family_mirror.inc').read_text()
spec = importlib.util.spec_from_file_location('fork_launcher', ROOT / 'scripts/launch_level2_family.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


def function(name):
    return re.search(r'(?:static )?(?:bool|void|uint64_t) ' + name + r'\([^\n]*\)\n\{.*?\n\}', TEXT, re.S).group()


def compile_run(source):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)
        (path / 'test.c').write_text(source)
        subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-I', str(SRC), str(path / 'test.c'), '-o', str(path / 'test')], check=True, capture_output=True, text=True)
        subprocess.run([str(path / 'test')], check=True, capture_output=True, text=True)


class Fork284FamilyTests(unittest.TestCase):
    def test_default_off_launcher_and_opt_in(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp); binary=p/'never-run'; binary.write_text('#!/bin/sh\nexit 99\n'); binary.chmod(0o700)
            base=['--data',temp,'--binary',str(binary)]
            inherited={'FORK284_ENABLE':'1','FORK284_ASSET_DIR':'poison','FORK284_OTHER':'1','DISPLAY':':7'}
            for flags in ([], ['--hd']):
                plan,env=launcher.build_plan(launcher.parser().parse_args(base+flags),inherited)
                self.assertFalse(plan['fork284_enabled'])
                self.assertFalse(any(k.startswith('FORK284_') for k in env))
                self.assertEqual(env['DISPLAY'],':7')
            with self.assertRaisesRegex(ValueError,'requires --hd'):
                launcher.build_plan(launcher.parser().parse_args(base+['--fork284']),{})
            plan,env=launcher.build_plan(launcher.parser().parse_args(base+['--hd','--fork284']),inherited)
            self.assertTrue(plan['fork284_enabled'])
            self.assertEqual(plan['assets_sha256_verified'],52)
            self.assertEqual(plan['fork284_assets_sha256_verified'],1)
            self.assertEqual(env['FORK284_ENABLE'],'1')
            self.assertFalse(plan['game_started'])
            self.assertFalse(Path(plan['profile']).exists())

    def test_changed_asset_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);binary=p/'never-run';binary.write_text('');binary.chmod(0o700)
            asset=p/launcher.REUSED_ROOT/'enemy-newshd-121-8.hda';asset.parent.mkdir(parents=True)
            payload=(ROOT/launcher.REUSED_ROOT/asset.name).read_bytes();asset.write_bytes(payload[:-1]+bytes([payload[-1]^1]))
            args=launcher.parser().parse_args(['--data',temp,'--binary',str(binary),'--hd','--fork284'])
            with patch.object(launcher,'verify_assets',return_value=52),self.assertRaisesRegex(ValueError,'Changed Fork284'):
                launcher.build_plan(args,{},p)

    @unittest.skipUnless(shutil.which('cc'), 'C compiler unavailable')
    def test_native_alpha_and_retirement(self):
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "fork284_family.h"
typedef uint8_t Uint8; typedef uint32_t Uint32;
#include "fork284_native.inc"
#define MIRROR_NORMAL 0
#define MIRROR_SHADOW 1
#define MIRROR_BLEND 2
#define FC_ORDER 1
static uint8_t f284_owned[64000],f284_shadows[64000],selected[64000],expected[64000],native[64000];
static uint8_t hd_owner[4096000],cloud_owner[4096000];static unsigned green_first[4096000];
static uint32_t rgb[4096000];
static struct {void *pixels;} surface={rgb},*canvas=&surface;
static void *fc_source_pixels=native;
static struct {bool active,pending,contributed,fault;unsigned slot,part,pixels;Fork284Draw draw[25];Fork284Write writes[25][270];} f284_frame;
static uint64_t f284_blend_retirements,f284_normal_retirements,f284_shadow_writes,f284_contract_faults,fc_frame;
static unsigned failure,clears;
typedef struct {uint8_t *rgba;} Asset;
static uint8_t rgba[172032];static struct {Asset member;} f284_resources={{rgba}};
static void f284_fail(unsigned r){failure=r;f284_frame.active=f284_frame.pending=false;f284_frame.fault=true;}
static void family_fault(unsigned r){(void)r;}
static bool b313_family_writer_draw_ready(uint64_t f){(void)f;return true;}
static void lamp272_clear(unsigned x){(void)x;clears++;}
#define triple275_clear lamp272_clear
#define private_ember269_clear lamp272_clear
#define gray325_clear lamp272_clear
#define longface573_clear lamp272_clear
static uint32_t blend_rgba(uint32_t dst,const uint8_t *art,unsigned a){
 unsigned r=(((dst>>16)&255)*(255-a)+art[0]*a)/255;
 unsigned g=(((dst>>8)&255)*(255-a)+art[1]*a)/255;
 unsigned b=((dst&255)*(255-a)+art[2]*a)/255;
 return 0xff000000u|(r<<16)|(g<<8)|b;
}
''' + '\n'.join(function(n) for n in ('f284_retire','f284_pixel','f284_shadow','f284_end')) + r'''
int main(void){
 assert(f284_palette[0].index==1);
 f284_frame.slot=50;f284_frame.pending=true;f284_frame.contributed=true;
 Fork284Draw *d=f284_frame.draw;d->x=40;d->y=20;
 for(unsigned n=0;n<4096000;n++)rgb[n]=0xff204060;
 for(unsigned n=0;n<172032;n+=4){rgba[n]=224;rgba[n+1]=128;rgba[n+2]=32;rgba[n+3]=127;}
 /* Three subpixels of the first callback exercise zero/partial/full alpha. */
 unsigned lx=f284_native[0][0].x,ly=f284_native[0][0].y;
 size_t art=(ly*8*192+lx*8)*4;rgba[art+3]=0;rgba[art+7]=127;rgba[art+11]=255;
 for(unsigned k=0;k<4;k++){
  f284_frame.part=k;f284_frame.pixels=0;f284_frame.active=true;
  for(unsigned i=0;i<f284_counts[k];i++){
   const Fork284Write *w=f284_native[k]+i;
   unsigned x=d->x+f284_px[k]+w->x,y=d->y+f284_py[k]+w->y,off=y*320+x;
   native[off]=expected[off]=w->index;
   assert(f284_pixel(x,y,MIRROR_NORMAL));assert(!failure&&f284_owned[off]==51&&selected[off]);
  }
  f284_end();assert(!failure);
 }
 assert(d->complete&&d->mask==15&&d->callback_count==270&&!f284_frame.pending);
 assert(clears==270*5);
 unsigned x=d->x+lx,y=d->y+ly,off=y*320+x;size_t n=y*8*2560+x*8;
 assert(rgb[n]==0xff204060&&rgb[n+2]==0xffe08020);
 assert(rgb[n+1]==blend_rgba(0xff204060,rgba+art+4,127));
 /* An untouched hole retains its exact underlay and no fabricated ownership. */
 assert(rgb[20*8*2560+40*8]==0xff204060&&!f284_owned[20*320+40]);
 assert(f284_retire(off,MIRROR_SHADOW)&&f284_owned[off]==51);
 f284_shadow(off);assert(f284_shadows[off]==1&&f284_shadow_writes==1);
 assert(f284_retire(off,MIRROR_BLEND)&&!f284_owned[off]&&!f284_shadows[off]&&f284_blend_retirements==1);
 assert(!f284_retire(off,MIRROR_BLEND));
 f284_owned[off]=51;assert(f284_retire(off,MIRROR_NORMAL)&&f284_normal_retirements==1);
 assert(!f284_retire(64000,MIRROR_NORMAL));
 /* Bad native ordering and incomplete parts never become accepted. */
 memset(&f284_frame,0,sizeof f284_frame);f284_frame.slot=50;f284_frame.active=true;f284_frame.pending=true;d=f284_frame.draw;d->x=40;d->y=20;
 assert(f284_pixel(0,0,MIRROR_NORMAL)&&failure==16&&!d->complete);
 failure=0;f284_frame.active=true;f284_end();assert(failure==18);
 return 0;
}
'''
        compile_run(source)

    @unittest.skipUnless(shutil.which('cc'), 'C compiler unavailable')
    def test_exact_event_admission_and_consumption(self):
        source=r"""
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#define B313_FAMILY_CANVAS_DIAGNOSTIC 1
typedef uint8_t Uint8;
struct JE_EventRecType {uint16_t eventtime;uint8_t eventtype;int16_t eventdat,eventdat2;int8_t eventdat3,eventdat5,eventdat6;uint8_t eventdat4;};
struct JE_EventRecType eventRec[731];
static const struct {unsigned time;int x;} f284_events[4]={{140,70},{140,280},{160,120},{160,230}};
static struct {const struct JE_EventRecType *events;unsigned consumed;uint64_t serial,epoch;bool exhausted;
 struct {bool live,bg3x1,bg3x1b;uint64_t token,epoch,generation;unsigned event;int slot,x,y,map1,map3;} call;
} f284_life;
static unsigned maxEvent=731,eventLoc,curLoc,failures;
static bool background3x1=true,background3x1b=false;
static int mapX=1,mapX3=1;
static bool f284_scope(void){return !f284_life.exhausted;}
static void f284_fail(unsigned r){(void)r;failures++;}
"""+'\n'.join(function(n) for n in ('f284_enabled','f284_event_matches','f284_stream_matches','render_mirror_fork284_event_begin'))+r"""
int main(void){
 unsetenv("FORK284_ENABLE");unsetenv("BUILDING313_FAMILY_CANVAS_ENABLE");assert(!f284_enabled());
 setenv("FORK284_ENABLE","1",1);assert(!f284_enabled());
 setenv("BUILDING313_FAMILY_CANVAS_ENABLE","1",1);assert(f284_enabled());
 setenv("FORK284_ENABLE","true",1);assert(!f284_enabled());setenv("FORK284_ENABLE","1",1);
 assert(!f284_stream_matches(NULL)&&!f284_stream_matches(eventRec));
 f284_life.events=eventRec;f284_life.epoch=3;
 for(unsigned e=12;e<=15;e++){
  struct JE_EventRecType *r=eventRec+e-1;
  *r=(struct JE_EventRecType){f284_events[e-12].time,7,284,f284_events[e-12].x,2,0,0,0};
  assert(f284_event_matches(e));
  r->eventdat2++;assert(!f284_event_matches(e));r->eventdat2--;
  r->eventdat4=1;assert(!f284_event_matches(e));r->eventdat4=0;
  eventLoc=e;curLoc=r->eventtime;
  assert(!render_mirror_fork284_event_begin(e,0,25,0));
  assert(!render_mirror_fork284_event_begin(e,1,50,0));
  assert(!render_mirror_fork284_event_begin(e,0,50,1));
  background3x1b=true;assert(!render_mirror_fork284_event_begin(e,0,50,0));background3x1b=false;
  uint64_t token=render_mirror_fork284_event_begin(e,0,50,0);
  assert(token==e-11&&f284_life.call.epoch==3&&f284_life.call.x==r->eventdat2-12&&f284_life.call.y==-28);
  /* Allocation may fail; the exact original event remains consumed. */
  f284_life.call.live=false;assert(!render_mirror_fork284_event_begin(e,0,50,0));
 }
 assert(f284_life.consumed==15&&!failures);
 assert(!f284_event_matches(0)&&!f284_event_matches(11)&&!f284_event_matches(16)&&!f284_event_matches(UINT32_MAX));
 maxEvent=730;assert(!f284_event_matches(12));maxEvent=731;
 f284_life.events=NULL;assert(!f284_event_matches(12));
 f284_life.call.live=true;assert(!render_mirror_fork284_event_begin(12,0,50,0)&&failures==1);
 return 0;
}
"""
        compile_run(source)

    def test_lifecycle_and_all_canvas_gates_connected(self):
        canvas=(SRC/'b313_family_canvas_mirror.inc').read_text()
        self.assertLess(canvas.index('f284_retire((unsigned)off,style)'),canvas.index('if(lamp272_pixel'))
        self.assertLess(canvas.index('f284_before_tile(slot,part)'),canvas.index('return lamp272_tile'))
        for token in ('f284_reset();','f284_tick();','f284_end();','f284_accept();','!f284_finish()','!f284_guard()','f284_write_current()','!fork_owned&&!terrain_retire'):
            self.assertIn(token,canvas)
        t=(SRC/'tyrian2.c').read_text(); self.assertIn('f284_stream_matches(events)',TEXT)
        for suffix in ('retired','level_begin','enemy_allocated','enemy_initialized','event_begin','event_commit'):
            self.assertIn('render_mirror_fork284_'+suffix,t)
        self.assertEqual((SRC/'sprite.c').read_text().count('render_mirror_fork284_bank_changed(sprite2s);'),2)

if __name__=='__main__':unittest.main()
