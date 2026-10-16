#!/usr/bin/env python3
"""Exact production authored Storm units. Original inputs and binaries stay private."""
import argparse,hashlib,importlib.util,json,os,shlex,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='18a54527795971a4aa8492f86a0fc4996a51961d'
spec=importlib.util.spec_from_file_location('compat',ROOT/'prototype/test-plasma-projectile-blend.py');compat=importlib.util.module_from_spec(spec);spec.loader.exec_module(compat)
SHA=lambda b:hashlib.sha256(b).hexdigest()
START='/* Three authored Storm pieces are leased by actual emission identity'
END='static bool recognized_value_effect('

def sources(out=None):
 functions,candidate,baseline=compat.source_units()
 text=(ROOT/'src/render_mirror.c').read_text();block=text[text.index(START):text.index(END,text.index(START))]
 reader=compat.extract(text,'read_asset')
 assert 'plasma_art_source_value' in block and 'read_asset(a,d)' in block
 if out:
  extracted=dict(functions)
  for name in ['hud_sprite_decode',*compat.ADDED,'render_mirror_pixel']:
   extracted[name]=extracted[name].replace(name+'(','production_'+name+'(',1)
  (out/'functions.inc').write_text('\n'.join(b[:b.index('{')].strip()+';' for b in extracted.values())+'\n'+''.join(extracted.values()))
  (out/'candidate-blit.inc').write_text(candidate.replace('void blit_sprite_blend(','void production_blit_sprite_blend(',1))
  (out/'baseline-blit.inc').write_text(baseline.replace('void blit_sprite_blend(','void production_baseline_blit_sprite_blend(',1))
  sprite_types='typedef struct\n'+(ROOT/'src/sprite.h').read_text().split('typedef struct\n',1)[1].split('extern Sprite_array',1)[0]
  (out/'sprite-types.inc').write_text(sprite_types)
  (out/'art-functions.inc').write_text(reader+'\n'+block)
  enum=text[text.index('enum { ASSET_NEWSH2='):text.index('};',text.index('enum { ASSET_NEWSH2='))+2].replace('ASSET_NEWSH2=101, ','')
  (out/'asset-enum.inc').write_text(enum)
  names=['normal15_branch','normal15_index','normal15_channel','normal15_rgba','normal15_compose']
  (out/'normal15-functions.inc').write_text(''.join(compat.extract(text,n) for n in names))
 return {'block':SHA(block.encode()),'reader':SHA(reader.encode()),'original_blit':SHA(candidate.encode()),**{n:SHA(f.encode()) for n,f in functions.items()}}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--data',type=Path);ap.add_argument('--out',type=Path);ap.add_argument('--assets',type=Path);ap.add_argument('--source-only',action='store_true');a=ap.parse_args()
 if a.source_only: print(json.dumps({'status':'PASS','baseline':BASE,'exact_compatibility_and_raw_blit_unchanged':True,'source_sha256':sources()},indent=2));return
 assert a.data and a.out and a.assets
 out=a.out.resolve();assert not out.exists() and ROOT not in out.parents;out.mkdir(parents=True,mode=0o700)
 hashes=sources(out);test_pins={str(p.relative_to(ROOT)):SHA(p.read_bytes())for p in [Path(__file__),Path(__file__).with_suffix('.c'),ROOT/'prototype/test-plasma-projectile-blend.c',ROOT/'prototype/test-plasma-projectile-blend.py']};input_pins={n:SHA((a.data/n).read_bytes()) for n in [*compat.DATA_PINS,'palette.dat']}
 for name in compat.DATA_PINS:
  records,_=compat.original_records(a.data/name);(out/(name+'.pieces')).write_bytes(b''.join(struct.pack('<3H',w,h,len(d))+d+p+m for w,h,d,p,m in records))
 (out/'palette.bin').write_bytes((a.data/'palette.dat').read_bytes()[5*768:6*768])
 # Real complete HDA resource bytes are copied, never replaced by synthetic textures.
 resources=[]
 for i in (22,23,24):
  for d in (4,8):
   n=f'option-plasma-projectile-{i}-{d}.hda';raw=(a.assets/n).read_bytes();(out/n).write_bytes(raw);resources.append({'name':n,'sha256':SHA(raw)})
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');runs={}
 for kind,flags in [('optimized',['-O2']),('sanitized',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
  command=[*shlex.split(os.environ.get('CC','cc')),'-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-function',*flags,'-I'+str(out),str(Path(__file__).with_suffix('.c')),'-o',str(out/kind)]
  compat.run(command,out/(kind+'-compile.log'))
  result=compat.run([str(out/kind),str(out/'tyrian.shp.pieces'),str(out/'tyrianc.shp.pieces'),str(out/'palette.bin'),str(out)],out/(kind+'.log'),env)
  runs[kind]=json.loads(result);print(kind+': '+result.strip(),flush=True)
 assert sources()==hashes,'Production sources changed during the run'
 assert test_pins=={n:SHA((ROOT/n).read_bytes())for n in test_pins},'Harness changed during the run'
 assert runs['optimized']==runs['sanitized'],'Optimized and sanitizer results differ'
 assert input_pins=={n:SHA((a.data/n).read_bytes())for n in input_pins}
 report={'status':'PASS','baseline':BASE,'source_sha256':hashes,'test_sha256':test_pins,'isolated_stubs':['Font interception and unrelated fixed-effect collaborators are stubs inherited from the unchanged compatibility harness. Retained-font production integration is covered by a separate independent supplement.'],'resources':resources,'inputs':input_pins,'runs':runs,'engine_launches':0}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
