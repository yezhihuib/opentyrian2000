#!/usr/bin/env python3
"""Finite extracted-production rear534 proof. No game, capture or full pack copy."""
import argparse,hashlib,importlib.util,json,os,re,struct,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='ee2b90cfaf9f227ca394ecd01f2403e55dbf2ea0'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def module(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/'prototype'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prior=module('prior','test-cash25-seven.py');extract=prior.extract
art=module('art','build-rear534-three-art.py')
FUNCS=['palette_rgb','blend_rgba','cloud_asset','darken_rgba','decode_tile','read_asset','cash25_family_ready','cash75_family_ready','cash50_family_ready','gem100_family_ready','gem250_family_ready','rear534_family_ready','cash25_surface_ready','explosion_asset_slot','get_asset','talon_frame','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset','cash25_pickup','cash75_pickup','cash50_pickup','gem100_pickup','gem250_pickup','rear534_pickup','scene_asset','render_mirror_enemy_tile','enemy_energy_family_ready','enemy_tank_shell_family_ready','render_mirror_entity_end']
def previous(n):return subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+n])
def source_checks(main):
 s=(ROOT/'src/render_mirror.c').read_text();p=s
 for n in ['rear534_family_ready','rear534_pickup']:p=p.replace(extract(p,n)+'\n','')
 for line in ['/* Three frozen rear-power lamp phases; complete composites, never effect145.\n * Independent all-three-or-classic cache for the selected Asset lifetime. */\n','static bool rear534_checked,rear534_valid;\n','/* Keep every original ordered quadrant and its physical-row-wrap guard. */\n']:
  assert p.count(line)==1;p=p.replace(line,'')
 branch='  if(base==203||base==205||base==207) {\n   bool mirrored=rear534_pickup(surface,x,y,bank,base,part,filter,material_context);\n   game_probe_scene_draw(ASSET_REAR534_BODY,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);\n   return mirrored;\n  }\n'
 assert p.count(branch)==1;p=p.replace(branch,'')
 for old,new in [(', ASSET_REAR534_BODY=123',''),('assets[510]','assets[507]'),('a->bank==ASSET_REAR534_BODY?"rear534-bank11":','')]:assert p.count(old)==1;p=p.replace(old,new)
 assert p.encode()==previous('src/render_mirror.c'),'Exact renderer inverse failed'
 tracked=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only',BASE,'--','src'],text=True).splitlines();changed=[n for n in tracked if (ROOT/n).read_bytes()!=previous(n)];assert changed==['src/render_mirror.c']
 for n in ['draw_asset_filtered','cash25_surface_ready','render_mirror_entity','render_mirror_entity_end','render_mirror_enemy_shot','get_asset','recognized_value_effect','recognized_contact_effect','render_mirror_sprite2_blend_pixel']+[f'{f}_family_ready' for f in ['cash25','cash75','cash50','gem100','gem250','enemy_energy','enemy_tank_shell']]:assert extract(s,n)==extract(previous('src/render_mirror.c').decode(),n),n
 m=json.loads((ROOT/'assets/hd/manifest.json').read_text());base=json.loads(previous('assets/hd/manifest.json'));proj=json.loads(json.dumps(m));rows=proj.pop('rear534_three_v1')['entries']
 for row in rows:
  del proj['source_pngs'][row['HDA_sha256']]
  for pack in [m['default_preview_pack'],m['default_debug_pack']]:del proj['packs'][pack]['files'][f"rear534-bank11-{row['id']}-8.hda"];proj['packs'][pack]['count']-=1
 assert proj==base,'Exact manifest inverse failed';assert (main/'assets/hd/manifest.json').read_bytes()==previous('assets/hd/manifest.json')
 prior_files=0
 for pack,data in base['packs'].items():
  for name,item in data['files'].items():
   assert SHA((main/'assets/hd/packs'/pack/name).read_bytes())==item['sha256'],(pack,name);prior_files+=1
 for n in subprocess.check_output(['git','-C',str(ROOT),'diff','--name-only',BASE,'--','src','assets/hd/manifest.json'],text=True).splitlines():assert n in ['src/render_mirror.c','assets/hd/manifest.json'],n
 return {'status':'PASS','baseline':BASE,'only_changed_production_file':'src/render_mirror.c','source_inverse_exact':True,'all_other_src_exact':True,'manifest_inverse_exact':True,'prior_pack_resources_verified':prior_files,'source_sha256':SHA(s.encode()),'manifest_sha256':SHA((ROOT/'assets/hd/manifest.json').read_bytes()),'game_runs':0},s,m

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);ap.add_argument('--original-data',type=Path);ap.add_argument('--main-root',type=Path,required=True);ap.add_argument('--source-only',action='store_true');a=ap.parse_args();report,s,m=source_checks(a.main_root);report['art'],raws=art.validate()
 if a.source_only:print(json.dumps(report,indent=2));return
 assert a.out and a.original_data;out=a.out.resolve();assert not out.exists() and ROOT not in out.parents and out not in ROOT.parents
 assert os.statvfs(out.parent).f_bavail*os.statvfs(out.parent).f_frsize>4*1024**3+16*1024**2
 out.mkdir();data=a.original_data.resolve();original=(data/'tyrian.shp').read_bytes();xmas=(data/'tyrianc.shp').read_bytes();assert SHA(original)=='80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0' and SHA(xmas)=='e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d'
 def bank(raw):
  count=struct.unpack_from('<H',raw)[0];off=list(struct.unpack_from('<'+str(count)+'I',raw,2))+[len(raw)];return raw[off[10]:off[11]]
 b=bank(original);xb=bank(xmas);assert b==xb;(out/'bank11.bin').write_bytes(b);(out/'xmas-bank11.bin').write_bytes(xb)
 decode=module('energy','test-enemy-energy-seven.py').decode;(out/'index-reference.bin').write_bytes(b''.join(decode(b,i+p) for i in [203,205,207] for p in [0,1,19,20]))
 types=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'static Asset talon_frames\[13\];',r'enum \{ ASSET_NEWSH2=.*?\};']
 for f in ['rear534','cash25','cash75','cash50','gem100','gem250','enemy_energy','enemy_tank_shell']:types.append(r'static bool '+f+r'_checked,'+f+r'_valid;')
 for f in ['cash25','cash75','cash50','gem100','gem250']:types.append(r'static bool '+f+r'_fixed_value;')
 (out/'types.inc').write_text('\n'.join(re.search(p,s,re.S).group() for p in types));(out/'functions.inc').write_text('\n'.join(extract(s,n) for n in FUNCS));sprite=(ROOT/'src/sprite.c').read_text();(out/'blitters.inc').write_text('\n'.join(extract(sprite,n) for n in ['blit_sprite2','blit_sprite2_filter']));(out/'wrapper.inc').write_text(extract((ROOT/'src/tyrian2.c').read_text(),'blit_enemy'))
 cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(out),str(Path(__file__).with_suffix('.c')),'-o',str(out/'test')]
 r=subprocess.run(cmd,capture_output=True,text=True);(out/'compile.log').write_text(r.stdout+r.stderr);print(r.stderr,end='');r.check_returncode();env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
 def run(mode,pack,legacy,valid=True):
  r=subprocess.run([str(out/'test'),mode,str(pack),str(legacy),str(int(valid)),str(out),str(ROOT/'assets/hd/packs'/legacy.name)],capture_output=True,text=True,env=env,timeout=300)
  assert not r.returncode,(mode,str(pack),r.stdout,r.stderr);return json.loads(r.stdout)
 results={};packs=[m['default_preview_pack'],m['default_debug_pack']]
 for pack in packs:
  for mode in ['render','xmas']:
   key=pack+':'+mode;results[key]=run(mode,ROOT/'assets/hd/packs'/pack,a.main_root/'assets/hd/packs'/pack);(out/(('preview' if pack==packs[0] else 'debug')+'-'+mode+'.json')).write_text(json.dumps(results[key],indent=2)+'\n');print(key,results[key],flush=True)
 cases=[]
 with tempfile.TemporaryDirectory(prefix='rear534-negative-',dir=out) as tmp:
  pack=Path(tmp)
  for n,b in raws.items():(pack/n).write_bytes(b)
  legacy=a.main_root/'assets/hd/packs'/packs[0]
  # Policy remains a regular exact copy even though this tiny loader unit never reads it.
  policy=legacy/'forest13.policy';assert policy.is_file() and not policy.is_symlink();(pack/'forest13.policy').write_bytes(policy.read_bytes());assert not (pack/'forest13.policy').is_symlink()
  for name,raw in raws.items():
   variants={'missing':None,'magic':b'BAD!'+raw[4:],'short-header':raw[:27],'truncated':raw[:-1],'trailing':raw+b'X','rgb':raw[:28]+bytes([raw[28]^1])+raw[29:],'alpha':raw[:31]+bytes([raw[31]^1])+raw[32:]}
   for label,offset,value in [('role',4,1010203),('id',4,1230204),('density',8,4),('width',12,23),('height',16,27),('anchor-x',20,0),('anchor-y',24,0)]:bad=bytearray(raw);struct.pack_into('<I',bad,offset,value);variants[label]=bytes(bad)
   for label,bad in variants.items():
    if bad is None:(pack/name).unlink()
    else:(pack/name).write_bytes(bad)
    run('loader',pack,legacy,False);cases.append([name,label]);(pack/name).write_bytes(raw)
  for name,raw in raws.items():
   (pack/name).unlink();rgba=raw[28:];(pack/name.replace('-8.','-4.')).write_bytes(raw[:8]+struct.pack('<I',4)+raw[12:28]+b''.join(rgba[(2*y*192+2*x)*4:(2*y*192+2*x)*4+4] for y in range(112) for x in range(96)))
  run('loader',pack,legacy,False);cases.append(['all','4x-only'])
  for name in raws:(pack/name).write_bytes(b'bad')
  run('loader',pack,legacy,False);cases.append(['all','invalid8-valid4'])
 report.update({'sanitizers':['ASan','UBSan'],'renderer_results':results,'resource_rejections':cases,'function_sha256':{n:SHA(extract(s,n).encode()) for n in FUNCS},'harness_sha256':{p.name:SHA(p.read_bytes()) for p in [Path(__file__),Path(__file__).with_suffix('.c')]},'limitations':['Extracted production source units only; no game, runtime RGB or Windows/manual acceptance.','Original RLE and blit_enemy wrapper are exact; display pixel callbacks are isolated and compositor RGB is checked separately.','Unrelated material/font paths have no-op or fail-if-entered sinks.','LeakSanitizer disabled; ASan and UBSan active.']})
 assert source_checks(a.main_root)[0]['source_sha256']==report['source_sha256'];(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(cases),'negative resource cases;',out/'result.json')
if __name__=='__main__':main()
