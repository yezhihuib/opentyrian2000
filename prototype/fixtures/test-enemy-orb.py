"""Bounded extracted-production oracle for the enemy-only bank8 orb hook."""
from pathlib import Path
import argparse,re,struct,subprocess,tempfile,os,json,hashlib,time
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
default_source=HERE.parents[1]/'src/render_mirror.c'
if not default_source.exists(): default_source=HERE.parents[1]/'opentyrian2000-cloud/src/render_mirror.c'
p.add_argument('--source',type=Path,default=default_source)
p.add_argument('--sanitize',action='store_true')
p.add_argument('--output',type=Path)
a=p.parse_args(); output=a.output or Path(tempfile.mkdtemp(prefix='enemy-orb-result-'));output.mkdir(parents=True,exist_ok=True)
paths={n:a.source.parent/n for n in ['render_mirror.c','entity_draw.c','sprite.c','tyrian2.c','render_mirror.h','entity_draw.h']};sources={n:p.read_bytes() for n,p in paths.items()};s=sources['render_mirror.c'].decode();start=time.monotonic()
def extract(name,source=s):
 m=re.search(r'^[^\n;]*\b'+name+r'\([^\n;]*\)\s*\{',source,re.M);assert m,name
 begin=source.index('{',m.start());end=begin+1;depth=1
 while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[m.start():end]+'\n'
def pixels(index,d):
 alphas=[0,1,127,128,254,255]
 return bytes(v for y in range(14*d) for x in range(12*d) for v in [(index*7+x*3+y)%256,(index*11+x+y*5)%256,(index*13+x*7+y*2)%256,alphas[(x+2*y+index)%6]])
def raw(index,d):return struct.pack('<4s6I',b'HDR1',80000+index,d,12,14,0,0)+pixels(index,d)
def original(index):
 out=bytearray()
 for y in range(14):
  pos=0;x=0
  while x<12:
   if (x+y+index)%5==0:x+=1;continue
   first=x
   while x<12 and (x+y+index)%5!=0:x+=1
   out.append(((x-first)<<4)|(first-pos));out.extend((index+3*k+7*y)%240+1 for k in range(first,x));pos=x
  out.append(12-pos)
 out.append(15);return out
with tempfile.TemporaryDirectory(prefix='enemy-orb-unit-') as temp:
 t=Path(temp);packs=t/'packs';packs.mkdir()
 for name in ['full8','full4','missing112','missing113','bad-anchor','bad-role','bad-size','bad-density','truncated','extra','empty']:
  out=packs/name;out.mkdir()
  if name=='empty':continue
  d=4 if name=='full4' else 8
  for idx in [112,113]:
   if name=='missing'+str(idx):continue
   b=bytearray(raw(idx,d))
   if idx==112:
    if name=='bad-anchor':struct.pack_into('<I',b,20,1)
    if name=='bad-role':struct.pack_into('<I',b,4,1080000+idx)
    if name=='bad-size':struct.pack_into('<I',b,12,24)
    if name=='bad-density':struct.pack_into('<I',b,8,4)
    if name=='truncated':b=b[:-1]
    if name=='extra':b+=b'X'
   (out/f'bullet-{idx}-{d}.hda').write_bytes(b)
 bank=bytearray(256*2)
 for idx in range(1,257):
  struct.pack_into('<H',bank,(idx-1)*2,len(bank));bank+=original(idx)
 (packs/'original-bank.bin').write_bytes(bank)
 types=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{ Asset \*asset; int x,y; \} GreenHead;',r'typedef struct \{ Uint16 peak\[16\]\[14\]; \} GreenBackground;',r'typedef struct \{ SDL_Rect rect; int bank,index,style; bool live; \} HdRegion;',r'static Asset assets\[\d+\];']
 (t/'types.inc').write_text('\n'.join(re.search(q,s,re.S).group() for q in types))
 names=['palette_rgb','complete_turret_group','restore_classic_rect','blend_rgba','cloud_shadow_rgba','cloud_asset','darken_rgba','decode_tile','read_asset','explosion_asset_slot','get_asset','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset','render_mirror_enemy_shot','render_mirror_pixel','render_mirror_entity_end']
 (t/'functions.inc').write_text('\n'.join(extract(n) for n in names))
 (t/'blitter.inc').write_text(extract('blit_sprite2',sources['sprite.c'].decode()))
 (t/'wrapper.inc').write_text(extract('draw_enemy_shot_sprite2',sources['entity_draw.c'].decode()))
 # Explicitly verify call-site placement leaves original bank12 and all other bank8 IDs on the old path.
 ty=sources['tyrian2.c'].decode();draw=ty[ty.index('/* Draw Enemy Shots */'):ty.index('/* Draw Enemy Shots */')+8000]
 assert 'if (sprite == 112 || sprite == 113)' in draw
 assert 'draw_enemy_shot_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);' in draw
 assert 'blit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet12, enemyShot[z].sgr + enemyShot[z].animate - 500);' in draw
 assert 'blit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);' in draw
 (t/'test.c').write_bytes(Path(__file__).with_suffix('.c').read_bytes());exe=t/'test';cmd=['cc','-std=c99','-O1','-g','-Wall','-Wextra']
 if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 build=subprocess.run(cmd+[str(t/'test.c'),'-o',str(exe)],capture_output=True,text=True);(output/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
 header=sources['render_mirror.h'].decode()
 macros='\n'.join(re.search(r'^#define '+n+r'\(.*$',header,re.M).group() for n in ['render_mirror_enemy_shot','render_mirror_entity_end'])
 disabled='#include <assert.h>\n#include <stdbool.h>\n#include <stdio.h>\ntypedef struct {int unused;} SDL_Surface;\ntypedef struct {void *data;unsigned size;} Sprite2_array;\nstatic unsigned calls;\nstatic void blit_sprite2(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned i){assert(s&&x==3&&y==4&&b.size==1&&i==112);calls++;}\n#define RENDER_MIRROR_DISABLED\n'+macros+'\n'+extract('draw_enemy_shot_sprite2',sources['entity_draw.c'].decode())+'\nint main(void){SDL_Surface s={0};Sprite2_array b={0,1};draw_enemy_shot_sprite2(&s,3,4,b,112);assert(calls==1);puts("PASS disabled build: production wrapper retains one original blit");return 0;}\n'
 (t/'disabled.c').write_text(disabled);disabled_exe=t/'disabled';dr=subprocess.run(['cc','-std=c99','-Wall','-Wextra',str(t/'disabled.c'),'-o',str(disabled_exe)],capture_output=True,text=True);assert dr.returncode==0,dr.stderr
 disabled_run=subprocess.run([str(disabled_exe)],capture_output=True,text=True);assert disabled_run.returncode==0;print(disabled_run.stdout);(output/'disabled.log').write_text(disabled_run.stdout+disabled_run.stderr)
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
 run=subprocess.run([str(exe),str(packs)],capture_output=True,text=True,env=env);(output/'result.log').write_text(run.stdout+run.stderr);print(run.stdout+run.stderr)
 report={'source_files':{n:{'path':str(paths[n]),'sha256':hashlib.sha256(v).hexdigest(),'stable_during_test':v==paths[n].read_bytes()} for n,v in sources.items()},'harness_sha256':{str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_suffix('.c')]},'disabled_build_exit_code':disabled_run.returncode,'sanitize':a.sanitize,'leak_sanitizer':'disabled under ptrace','exit_code':run.returncode,'elapsed_seconds':time.monotonic()-start,'stdout':run.stdout,'stderr':run.stderr,'scope':'Actual extracted mirror helper, wrapper and original RLE blitter. Synthetic HDA/RLE source assets, independent byte-channel/index oracles. No production edits or runtime captures.'}
 (output/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('Report:',output/'result.json');assert run.returncode==0
 assert all(v['stable_during_test'] for v in report['source_files'].values()),'source changed during test'
