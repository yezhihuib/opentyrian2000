#!/usr/bin/env python3
"""Source-only original sequence/input preservation and production entrypoint gate."""
from pathlib import Path
import hashlib, os, subprocess, tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE_HASHES={'src/tyrian2.c': '7faab1f034b737b2413952f8c9ba5c7cdc307d407f4346eb08c0834332ea1ae7', 'src/picload.c': '78246fbde5101cb4a6de0a0dc3621e9f4fea56bb524056ea6e75b641ececef7b', 'src/video.c': '5f6e317f172eeed1e6b06c18216a0ecd67c2b7f395a0aca49c6ef6562d1892f7', 'src/palette.c': '785e3692e71a5507e442b6191fd85da9cb83eed092e5a0abfe0e2463a67f1ae6', 'src/nortsong.c': '0d0a1cbe9432a3263f80cf9e932339f76be0747d4f163b0430a36aff3011ae72', 'src/keyboard.c': '4bf6666634899388416e32f0b3ad09b0995833f8f6a29587c198ce1d5545d440', 'src/joystick.c': 'a2eafce5f709c792b44a7859e57270fd25d14100ef86df241312e0ae8c556014'}

def extract(text,name):
 start=text.index('void '+name+'(void)');first=text.index('{',start);depth=1;end=first+1
 while depth:
  depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[start:end]

def main():
 for path,want in BASE_HASHES.items():
  text=(ROOT/path).read_text()
  stripped=''.join(line for line in text.splitlines(keepends=True) if 'startup_logos_' not in line and '#include "startup_logos.h"' not in line)
  assert hashlib.sha256(stripped.encode()).hexdigest()==want,(path,'Original source changed beyond display-only hooks')
 main=(ROOT/'src/opentyr.c').read_text();params=(ROOT/'src/params.c').read_text();module=(ROOT/'src/startup_logos.c').read_text()
 assert '#ifdef NDEBUG\n\tif (!isNetworkGame && !game_probe_enabled)\n\t\tintro_logos();\n#endif' in main
 assert 'startup_logos_configured()' in main and 'isNetworkGame || game_probe_enabled' in main
 assert 'Startup assets require a release/NDEBUG build' in main
 assert '"startup-assets"' in params and 'startup_logos_set_directory(option.arg)' in params
 for forbidden in ('game_probe_', 'mt_rand', 'SDL_PushEvent', 'SDL_RenderReadPixels', 'setDelay(', 'wait_delay', 'exit(', 'getenv('):assert forbidden not in module,forbidden
 intro=extract((ROOT/'src/tyrian2.c').read_text(),'intro_logos')
 prelude=r'''#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
static void *VGAScreen=(void *)1;
static void *colors=(void *)2;
static bool moveTyrianLogoUp;
static unsigned count,shown,waits,loads,bindings;
static void startup_logos_begin(void){assert(count++==0);}
static void SDL_FillRect(void *s,void *r,int v){assert(s==VGAScreen&&!r&&!v&&count++==1);}
static void JE_showVGA(void){++shown;}
static void fade_white(int n){assert(count++==2&&n==25);shown+=(unsigned)n;}
static void JE_loadPic(void *s,int pic,bool pal){assert(s==VGAScreen&&!pal);assert(pic==(loads++?12:10));assert(count++==(pic==10?3:8));}
static void startup_logos_bind(void *s,int pic,void *p){assert(s==VGAScreen&&p==colors);assert(pic==(bindings++?12:10));}
static void fade_palette(void *p,int n,int first,int last){assert(p==colors&&first==0&&last==255);assert(n==(loads==1?25:10));assert(count++==(loads==1?4:9));shown+=(unsigned)n;}
static void setDelay(int n){assert(n==200&&count++==(loads==1?5:10));}
static void wait_delayorinput(void){assert(count++==(loads==1?6:11));++waits;}
static void fade_black(int n){assert(n==10&&count++==(loads==1?7:12));shown+=(unsigned)n;}
static void startup_logos_end(void){assert(count++==13);}
'''
 with tempfile.TemporaryDirectory(prefix='mfg-sequence-') as temp:
  source=Path(temp)/'sequence.c';exe=Path(temp)/'sequence'
  source.write_text(prelude+intro+'\nint main(void){intro_logos();assert(count==14&&shown==82&&waits==2&&loads==2&&bindings==2&&moveTyrianLogoUp);puts("Original82-presentation/two-wait sequence and explicit context hooks preserved");return 0;}\n')
  subprocess.run([os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror',str(source),'-o',str(exe)],check=True)
  subprocess.run([str(exe)],check=True)
 gate=main[main.index('\tif (startup_logos_configured())'):main.index('\n\tif (!override_xmas)')]
 with tempfile.TemporaryDirectory(prefix='mfg-selector-') as temp:
  source=Path(temp)/'gate.c'
  source.write_text('#include <assert.h>\n#include <stdbool.h>\n#include <stdio.h>\nstatic bool selected,isNetworkGame,game_probe_enabled;static int quits;static bool startup_logos_configured(void){return selected;}static void SDL_Quit(void){++quits;}\nstatic int check_config(void){\n'+gate+'\nreturn 0;}\nint main(void){for(int s=0;s<2;s++)for(int n=0;n<2;n++)for(int p=0;p<2;p++){selected=s;isNetworkGame=n;game_probe_enabled=p;quits=0;int blocked=s&&(n||p\n#ifndef NDEBUG\n||1\n#endif\n);assert(check_config()==(blocked?2:0));assert(quits==blocked);}return 0;}\n')
  for mode in ('release','debug'):
   exe=Path(temp)/mode
   cmd=[os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror',str(source),'-o',str(exe)]
   if mode=='release':cmd+=['-DNDEBUG']
   # NDEBUG removes assert, so compile an independent non-assert CHECK macro.
   test=source.read_text().replace('assert(', 'CHECK(')
   source.write_text('#define CHECK(x) do {if(!(x))return 99;} while(0)\n'+test if '#define CHECK' not in test else test)
   subprocess.run(cmd,check=True);subprocess.run([str(exe)],check=True,stderr=subprocess.DEVNULL)
  options=params[params.index('\tconst Options options[]'):params.index('\n\tOption option;')]
  source.write_text('#include "arg_parse.h"\n#include <stdio.h>\nint main(int argc,char **argv){\n'+options+'\nOption p=parse_args(argc,(const char **)argv,options);printf("%d|%s",p.value,p.arg?p.arg:"<none>");return 0;}\n')
  exe=Path(temp)/'args';subprocess.run([os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src'),str(source),str(ROOT/'src/arg_parse.c'),'-o',str(exe)],check=True)
  for args,want in [(['--startup-assets=pack'],'258|pack'),(['--startup-assets','pack'],'258|pack'),(['--startup-assets='],'258|'),(['--startup-assets'],'-3|<none>')]:
   assert subprocess.check_output([str(exe),*args],text=True,stderr=subprocess.DEVNULL)==want
 print('Executable release/debug x configured/network/probe selector matrix and original argument parser passed')
 print('Original source restoration hashes, input code, title boundary and startup-only entrypoint gates passed')
if __name__=='__main__':main()
