#!/usr/bin/env python3
"""Mutation sensitivity for the reused finite250/five-family oracle. No game."""
import argparse,importlib.util,json,os,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('unit',R/'prototype/test-gem250-six.py');unit=importlib.util.module_from_spec(spec);spec.loader.exec_module(unit)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--units',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();u=a.units.resolve()/'250';out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);m=json.loads((R/'assets/hd/manifest.json').read_text());pack=R/'assets/hd/packs'/m['default_preview_pack']
mutations=[
 ('body-wrong-bank','gem250_pickup','bank.data!=spriteSheet11.data','bank.data!=spriteSheet8.data','render',1),
 ('body-wrong-slot','gem250_pickup','&assets[499+(int)base-14]','&assets[500+(int)base-14]','render',1),
 ('body-no-record-gate','gem250_pickup','||context->type!=395','','render',1),
 ('value-nonfixed-admitted','render_mirror_entity','if(fixed_value250&&bank.data&&','if(bank.data&&','render',1),
 ('value-context-leaks','render_mirror_entity','bool fixed_value250=gem250_fixed_value;gem250_fixed_value=false;','bool fixed_value250=gem250_fixed_value;','render',1),
 ('alpha-forced-opaque','draw_asset_filtered','talon_blend?(src[3]+1)/2:src[3]','talon_blend?(src[3]+1)/2:255','render',1),
 ('blend-no-value-average','explosion_asset_blend_rgba','unsigned int next=(source_peak+destination_peak+1)/2;','unsigned int next=source_peak;','render',1),
 ('family-allows-missing','gem250_family_ready','if(!a->valid)gem250_valid=false;','if(!a->valid)gem250_valid=true;','loader',0),
 ('skip-original-after-hd','wrapper','if (layout == ENTITY_QUAD)','if (mirrored) {render_mirror_entity_end();return;}\n\tif (layout == ENTITY_QUAD)','render',1),
 ('250-depends-on-25','gem250_family_ready','return gem250_valid;\n}','return gem250_valid&&cash25_family_ready();\n}','mixed',16),
 ('250-depends-on-75','gem250_family_ready','return gem250_valid;\n}','return gem250_valid&&cash75_family_ready();\n}','mixed',16),
 ('250-depends-on-50','gem250_family_ready','return gem250_valid;\n}','return gem250_valid&&cash50_family_ready();\n}','mixed',16),
 ('250-depends-on-100','gem250_family_ready','return gem250_valid;\n}','return gem250_valid&&gem100_family_ready();\n}','mixed',16),
 ('missing250-poisons100','gem250_family_ready','if(!a->valid)gem250_valid=false;','if(!a->valid){gem250_valid=false;gem100_valid=false;}','mixed',8),
 ('missing250-poisons50','gem250_family_ready','if(!a->valid)gem250_valid=false;','if(!a->valid){gem250_valid=false;cash50_valid=false;}','mixed',4),
 ('missing250-poisons75','gem250_family_ready','if(!a->valid)gem250_valid=false;','if(!a->valid){gem250_valid=false;cash75_valid=false;}','mixed',2),
 ('missing250-poisons25','gem250_family_ready','if(!a->valid)gem250_valid=false;','if(!a->valid){gem250_valid=false;cash25_valid=false;}','mixed',1),
]
results=[]
with tempfile.TemporaryDirectory(prefix='gem250-mutation-pack-') as tmp:
 fixture=Path(tmp)
 for label,func,old,new,mode,expected in mutations:
  d=out/label;d.mkdir()
  for n in ['types.inc','functions.inc','blitters.inc','wrapper.inc','driver.c']:
   text=(u/n).read_text()
   if n==('wrapper.inc' if func=='wrapper' else 'functions.inc'):
    scope=text if func=='wrapper' else unit.extract(text,func);assert scope.count(old)==1,(label,old);text=text.replace(scope,scope.replace(old,new))
   (d/n).write_text(text)
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(d),str(d/'driver.c'),'-o',str(d/'test')]
  r=subprocess.run(cmd,capture_output=True,text=True);(d/'compile.log').write_text(r.stdout+r.stderr);r.check_returncode();chosen=pack
  if mode!='render':
   for p in fixture.iterdir():p.unlink()
   for p in sorted(pack.glob('coin*-*.hda'))+sorted(pack.glob('gem100-*.hda'))+sorted(pack.glob('gem250-*.hda')):
    if mode=='loader' and p.name.startswith('gem250-') and 'value-' not in p.name or mode=='mixed' and p.name.startswith('coin25-' if expected==1 else 'coin75-' if expected==2 else 'coin50-' if expected==4 else 'gem100-' if expected==8 else 'gem250-'):(fixture/p.name).write_bytes(p.read_bytes())
   chosen=fixture
  r=subprocess.run([str(d/'test'),mode,str(chosen),str(expected),str(u)],capture_output=True,text=True,timeout=120,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'));assert r.returncode!=0 and ('FAIL line' in r.stderr or 'Sanitizer' in r.stderr),(label,r.returncode,r.stdout,r.stderr)
  (d/'result.log').write_text(r.stdout+r.stderr);results.append({'mutation':label,'status':'KILLED','returncode':r.returncode,'diagnostic':r.stderr[:1000]});print('KILLED',label,flush=True)
(out/'result.json').write_text(json.dumps({'status':'PASS','game_runs':0,'mutations':results},indent=2)+'\n')
