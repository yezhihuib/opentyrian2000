#!/usr/bin/env python3
"""Extract exact production Mint body loader, guard, wrapper, dispatch, compositor and RLE. Never launch the engine."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, os, re, shlex, struct, subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='8b71966b59315b7ee67163e160925e0d60a0ae39'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def extract(s,n):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+n+r'\([^;{}]*\)\s*\{',s,re.M);assert m,n
 e=s.index('{',m.start())+1;depth=1
 while depth:depth+=(s[e]=='{')-(s[e]=='}');e+=1
 return s[m.start():e]+'\n'
def run(cmd,log,**kw):
 r=subprocess.run(cmd,capture_output=True,text=True,**kw);log.write_text('$ '+shlex.join(map(str,cmd))+'\n'+r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(f'{log}: exit {r.returncode}\n{r.stdout[-1000:]}{r.stderr[-5000:]}')
 return r

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--compile-engine',action='store_true');a=p.parse_args();out=a.out.resolve();
 if out==ROOT or ROOT in out.parents:p.error('--out must be outside the candidate checkout')
 out.mkdir(parents=True,exist_ok=True)
 rs=(ROOT/'src/render_mirror.c').read_text();sp=(ROOT/'src/sprite.c').read_text();ed=(ROOT/'src/entity_draw.c').read_text();mi=(ROOT/'src/mainint.c').read_text();original=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':src/mainint.c'],text=True)
 names=['decode_tile','read_asset','mint27_source_matches','explosion_asset_slot','marlo152_source_matches','marlo152_asset','mint_body_source_matches','mint_body_asset','get_asset','talon_frame','talon_frames_ready','palette_rgb','blend_rgba','darken_rgba','cloud_asset','cloud_shadow_rgba','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset','render_mirror_pixel','render_mirror_entity_end','render_mirror_marlo_body','render_mirror_mint_body','render_mirror_entity']
 funcs={n:extract(rs,n)for n in names};hashes={n:SHA(s.encode())for n,s in funcs.items()}
 # Observation changes only the exported function name. Bodies remain byte-exact.
 funcs['render_mirror_pixel']=funcs['render_mirror_pixel'].replace('void render_mirror_pixel(', 'void production_render_mirror_pixel(',1)
 (out/'functions.inc').write_text('\n'.join(s[:s.index('{')].strip()+';'for s in funcs.values())+'\n'+''.join(funcs.values()))
 patterns=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'enum \{ ASSET_NEWSH2=.*?\};',r'typedef struct \{ SDL_Rect rect;.*?\} HdRegion;',r'typedef struct \{ Asset \*asset; int x,y; \} GreenHead;',r'typedef struct \{ Uint16 peak\[16\]\[14\]; \} GreenBackground;']
 (out/'types.inc').write_text('\n'.join(re.search(p,rs,re.S).group()for p in patterns)+'\n')
 blit=extract(sp,'blit_sprite2');hashes['blit_sprite2']=SHA(blit.encode());(out/'blitters.inc').write_text(blit.replace('void blit_sprite2(', 'void production_blit_sprite2(',1))
 wrappers=[extract(ed,n)for n in ['draw_sidekick_body_sprite2','draw_mint_body_sprite2']];hashes.update({n:SHA(w.encode())for n,w in zip(['draw_sidekick_body_sprite2','draw_mint_body_sprite2'],wrappers)});(out/'wrapper.inc').write_text('\n'.join(wrappers))
 def block(s):
  start=s.index('\t// draw sidekicks\n');end=s.index('\n}\n\nvoid JE_mainGamePlayerFunctions',start)
  return s[start:end]
 dispatch=block(mi);base_dispatch=block(original);hashes['dispatch_block']=SHA(dispatch.encode());hashes['baseline_dispatch_block']=SHA(base_dispatch.encode())
 (out/'dispatch.inc').write_text('static void candidate_dispatch(Player *this_player,unsigned playerNum_)\n{\n'+dispatch+'\n}\nstatic void baseline_dispatch(Player *this_player,unsigned playerNum_)\n{\n'+base_dispatch+'\n}\n')
 for fn,num in [('tyrian.shp',9),('tyrianc.shp',9),('tyrian.shp',8)]:
  raw=(a.data/fn).read_bytes();count=struct.unpack_from('<H',raw)[0];pos=list(struct.unpack_from('<'+str(count)+'I',raw,2))+[len(raw)];(out/(fn+f'.bank{num}')).write_bytes(raw[pos[num-1]:pos[num]])
 expected={112:'ddbfe03b540bc10c46570ef4ac1fadfcbb66dc9a2dc8f9386146a1b8c4fd1c2b',131:'75c2301bb9ae5b7dd96195b3e04993a4c7dd436ef61d5449d013898bafcac4b6',150:'29da5df5d364527ea9eaa62b7bc1c457f40c5da3bab129e01d3f487ba11eeb27'}
 hdas={i:(ROOT/f'assets/hd/artwork/option-mint-body-three-v1/output/option-mint-bank9-{i}-8.hda').read_bytes()for i in expected}
 for i,hda in hdas.items():
  assert SHA(hda)==expected[i],f'Unreviewed body resource {i}'
  assert struct.unpack_from('<4s6I',hda)==(b'HDR1',1270000+i,8,12,14,0,0)and len(hda)==43036
 work=out/'fixtures';work.mkdir(exist_ok=True);rows=[]
 def add(name,transform=None,valid=0,density=8,extra4=False):
  q=work/name;q.mkdir(exist_ok=True);rows.append((name,valid,density))
  for i,hda in hdas.items():
   for d in [4,8]:(q/f'option-mint-bank9-{i}-{d}.hda').unlink(missing_ok=True)
   if transform is not None:(q/f'option-mint-bank9-{i}-8.hda').write_bytes(transform(hda,i))
   if extra4:
    rgba=hda[28:];small=b''.join(rgba[(y*2*96+x*2)*4:(y*2*96+x*2)*4+4]for y in range(56)for x in range(48));(q/f'option-mint-bank9-{i}-4.hda').write_bytes(struct.pack('<4s6I',b'HDR1',1270000+i,4,12,14,0,0)+small)
 add('valid',lambda h,i:h,1);add('missing');add('only4',None,1,4,True);add('invalid8-valid4',lambda h,i:b'bad',1,4,True)
 for name,off,value in [('role',4,1260000),('identity',4,1270152),('density',8,4),('width',12,11),('height',16,13),('anchor-x',20,5),('anchor-y',24,7)]:
  def changed(h,i,off=off,value=value,name=name):
   raw=bytearray(h);struct.pack_into('<I',raw,off,value+i if name=='role'else value);return raw
  add(name,changed)
 for name,fn in [('magic',lambda h,i:b'BAD!'+h[4:]),('short-header',lambda h,i:h[:27]),('truncated',lambda h,i:h[:-1]),('extra',lambda h,i:h+b'X')]:add(name,fn)
 for name,alpha in [('transparent',0),('half-alpha',128),('opaque',255)]:
  def alpha_changed(h,i,alpha=alpha):
   raw=bytearray(h);raw[31::4]=bytes([alpha])*10752;return raw
  add(name,alpha_changed,1)
 (work/'variants.tsv').write_text(''.join(f'{n} {v} {d}\n'for n,v,d in rows))
 # Fetch old sparse Git blobs without materializing or modifying tracked resources.
 oldpack='assets/hd/packs/packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test/'
 oldnames=[f'ship-{i}-8.hda'for i in [229,231,233,235,237]]+[f'talon-bank-{i}-8.hda'for i in [1,3,4,5,7,8,9,11]]+['bullet-27-8.hda','bullet-67-8.hda','bullet-70-8.hda','option-marlo-bank9-152-8.hda']
 for name in oldnames:(work/'valid'/name).write_bytes(subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+oldpack+name]))
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');runs={}
 for name,flags in [('optimized',['-O2']),('sanitized',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
  cmd=['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-function',*flags,'-I'+str(out),str(Path(__file__).with_suffix('.c')),'-lm','-o',str(out/name)]
  run(cmd,out/(name+'-compile.log'));r=run([str(out/name),str(out/'tyrian.shp.bank9'),str(out/'tyrianc.shp.bank9'),str(out/'tyrian.shp.bank8'),str(work)],out/(name+'.log'),env=env,timeout=300);runs[name]=json.loads(r.stdout);print(name+': '+r.stdout.strip(),flush=True)
 engine=None
 if a.compile_engine:
  build=out/'full-engine';build.mkdir(exist_ok=True);flags=shlex.split(subprocess.check_output(['pkg-config','sdl2','SDL2_net','--cflags'],text=True));libs=shlex.split(subprocess.check_output(['pkg-config','sdl2','SDL2_net','--libs'],text=True));srcs=sorted((ROOT/'src').glob('*.c'));vh=(ROOT/'src/opentyrian_version.h').read_bytes()
  def comp(src):
   obj=build/(src.stem+'.o');run(['cc','-std=c99','-O2','-DNDEBUG','-DWITH_NETWORK','-DTARGET_UNIX','-DTYRIAN_DIR="/unused"',*flags,'-c',str(src),'-o',str(obj)],build/(src.stem+'.log'));return obj
  with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:objects=list(ex.map(comp,srcs))
  run(['cc',*map(str,objects),'-lm',*libs,'-o',str(build/'opentyrian2000')],build/'link.log');assert vh==(ROOT/'src/opentyrian_version.h').read_bytes()
  for src in ['entity_draw.c','render_mirror.c']:
   run(['cc','-std=c99','-O2','-DRENDER_MIRROR_DISABLED',*flags,'-c',str(ROOT/'src'/src),'-o',str(build/(src+'.classic.o'))],build/(src+'.classic.log'))
  engine={'translation_units':len(srcs),'linked':True,'executed':False,'classic_disabled_units':['entity_draw.c','render_mirror.c'],'version_header_unchanged':True}
 report={'status':'PASS','baseline':BASE,'asset_sha256':{str(i):SHA(h)for i,h in hdas.items()},'production_source_functions_sha256':hashes,'resource_variants':rows,'frame_ids':[112,131,150],'normal_source_full_tile_writes_per_frame':94,'scene_palette':'synthetic grayscale; actual game palette and NIGHT coverage are separate runtime evidence','runs':runs,'full_engine':engine,'game_runs':0,'observation_shims':['Function-name-only rename: production blit observed by counted blit shim; production pixel bridge observed by address/value/style shim. Function bodies unchanged.','Exact candidate/baseline sidekick draw block wrapped in isolated test function. Only the existing late draw/state block is extracted; unrelated simulation not executed.'],'collaborator_stubs':['Font lifecycle/callbacks no-op; terrain/material selectors, Vulcan shadow, unsupported other family paths abort if accidentally reached.','Gameplay outside the existing late draw/state block, RNG, shots, HUD and shops are checked unchanged by source inverse; this unit does not launch or simulate the full engine.'],'limitations':['LeakSanitizer disabled for executor compatibility; AddressSanitizer and UndefinedBehaviorSanitizer remain enabled.','Malformed source is tested at HD guard only; classic raw RLE is deliberately not run on malformed source.','Horizontal wrapping coordinates reject HD and retain exact original physical-row indexed writes.','Finite no-game verification does not establish Windows, GPU, performance, full-level survival or actual-play aesthetics.']}
 (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
