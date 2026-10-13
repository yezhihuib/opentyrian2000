#!/usr/bin/env python3
"""Finite extracted-production coin25 proof. Never starts the game or captures images.
One seven-file temporary pack is reused for malformed-resource tests.
"""
import argparse, hashlib, json, os, re, struct, subprocess, tempfile
from pathlib import Path
from PIL import Image
PIN='72ace9e51651158cd43da9209a2cd483bc741314'
INV='75b4973e91204d3fd35969237ff2e4d7f217d64ca23c7d15670712f14955697b'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def extract(s,n):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+n+r'\([^;{}]*\)\s*\{',s,re.M);assert m,n
 e=s.index('{',m.start())+1;d=1
 while d:d+=(s[e]=='{')-(s[e]=='}');e+=1
 return s[m.start():e]+'\n'
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--original-data',type=Path,required=True);a=ap.parse_args();root=Path(__file__).resolve().parents[1];out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
 names=subprocess.check_output(['git','-C',str(root),'ls-tree','-r','--name-only',PIN,'--','src'],text=True).splitlines();old={n:subprocess.check_output(['git','-C',str(root),'show',PIN+':'+n]) for n in names};changed=[n for n,b in old.items() if (root/n).read_bytes()!=b];assert set(changed)=={'src/render_mirror.c','src/render_mirror.h','src/tyrian2.c'},changed
 s=(root/'src/render_mirror.c').read_text();prior=old['src/render_mirror.c'].decode()
 unchanged=['get_asset','explosion_asset_slot','render_mirror_enemy_shot','enemy_energy_family_ready','recognized_value_effect','recognized_contact_effect','render_mirror_sprite2_blend_pixel','explosion_asset_blend_rgba','render_mirror_pixel']
 for n in unchanged:assert extract(s,n)==extract(prior,n),n
 insertion='\t\t\t\t/* Display-only eligibility for this original fixed value draw. */\n\t\t\t\trender_mirror_coin25_value_begin(explosions[j].fixedPosition && !explosions[j].followPlayer &&\n\t\t\t\t                                explosions[j].deltaY == 0 && explosions[j].sprite == 184 && explosions[j].ttl <= 8);\n'
 ty=(root/'src/tyrian2.c').read_text();assert ty.count(insertion)==1 and ty.replace(insertion,'').encode()==old['src/tyrian2.c']
 entity=extract(s,'render_mirror_entity');assert entity.index('cash25_fixed_value=false;')<entity.index('if(');assert 'cash25_fixed_value=false;' in extract(s,'render_mirror_begin') and 'cash25_fixed_value=false;' in extract(s,'render_mirror_entity_end')
 m=json.loads((root/'assets/hd/manifest.json').read_text());baseline=json.loads(subprocess.check_output(['git','-C',str(root),'show',PIN+':assets/hd/manifest.json']));packs=[m['default_preview_pack'],m['default_debug_pack']];art=root/'assets/hd/artwork/cash25-seven-v1';invraw=(art/'inventory.json').read_bytes();assert SHA(invraw)==INV;inv=json.loads(invraw);raws={};outputs=[]
 for name,digest in inv['inputs'].items():assert SHA((art/name).read_bytes())==digest,name
 for row in inv['outputs']:
  idx=row['id'];name=f"{row['prefix']}-{idx}-8.hda";raw=(art/'output'/name).read_bytes();assert len(raw)==43036 and raw[:28]==struct.pack('<4s6I',b'HDR1',row['key'],8,12,14,0,0) and SHA(raw)==row['HDA_SHA256'] and SHA(raw[28:])==row['RGBA_SHA256'];raws[name]=raw
  png=art/'output'/name.replace('.hda','.png');assert SHA(png.read_bytes())==row['PNG_SHA256'];im=Image.open(png);assert im.mode=='RGBA' and im.size==(96,112) and im.tobytes()==raw[28:]
  support=Image.open(art/f'masks/mask-{idx}.png').resize((96,112),Image.Resampling.NEAREST).tobytes();alpha=raw[31::4];assert all(not x or y for x,y in zip(alpha,support));assert sum(0<x<255 for x in alpha)==row['fractional_samples'];assert 0 in alpha
  for pack in packs:assert (root/'assets/hd/packs'/pack/name).read_bytes()==raw and not (root/'assets/hd/packs'/pack/name.replace('-8.','-4.')).exists()
  item=m['source_pngs'][SHA(raw)];assert (root/item['path']).read_bytes()==png.read_bytes();outputs.append({'name':name,'sha256':SHA(raw),'fractional_alpha':row['fractional_samples']})
 for pack,data in baseline['packs'].items():
  assert m['packs'][pack]['count']==len(m['packs'][pack]['files'])
  assert set(m['packs'][pack]['files'])-set(data['files'])==(set(raws) if pack in packs else set())
  for name,entry in data['files'].items():assert m['packs'][pack]['files'][name]==entry and SHA((root/'assets/hd/packs'/pack/name).read_bytes())==entry['sha256']
 # The preceding full existing-pack hashes rule out unrelated resource mutations.
 funcs=['palette_rgb','blend_rgba','cloud_asset','darken_rgba','decode_tile','read_asset','cash25_family_ready','cash25_surface_ready','render_mirror_coin25_value_begin','explosion_asset_slot','get_asset','talon_frame','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset','cash25_pickup','render_mirror_entity','enemy_energy_slot','enemy_energy_family_ready','render_mirror_enemy_shot','render_mirror_entity_end']
 types=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'static Asset talon_frames\[13\];',r'static bool enemy_energy_checked,enemy_energy_valid;',r'static bool cash25_checked,cash25_valid;',r'static bool cash25_fixed_value;']
 data=a.original_data.resolve();pins={'tyrian.shp': '80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0', 'newsh6.shp': '49e3d08e122ea71d6a621d2de127da00ce8a26ff73a0fb40d0cdd7ca2909d075'};original=(data/'tyrian.shp').read_bytes();effects=(data/'newsh6.shp').read_bytes();assert SHA(original)==pins['tyrian.shp'] and SHA(effects)==pins['newsh6.shp'];count=struct.unpack_from('<H',original)[0];offsets=list(struct.unpack_from('<'+str(count)+'I',original,2))+[len(original)];bank=original[offsets[10]:offsets[11]];(out/'bank11.bin').write_bytes(bank);(out/'newsh6.bin').write_bytes(effects)
 def decode(raw,idx):
  pos=struct.unpack_from('<H',raw,(idx-1)*2)[0];cell=0;values=bytearray(168);mask=bytearray(168)
  while raw[pos]!=15:
   code=raw[pos];pos+=1;cell+=code&15
   for _ in range(code>>4):
    assert 0<=cell<168;values[cell]=raw[pos];mask[cell]=255;pos+=1;cell+=1
  return values+mask
 (out/'index-reference.bin').write_bytes(b''.join(decode(bank,idx) for idx in range(7,13))+decode(effects,185))
 sprite=(root/'src/sprite.c').read_text();wrapper=(root/'src/entity_draw.c').read_text();(out/'blitters.inc').write_text('\n'.join(extract(sprite,n) for n in ['blit_sprite2','blit_sprite2_blend','blit_sprite2_darken']));(out/'wrapper.inc').write_text(extract(wrapper,'draw_entity_sprite2'))
 (out/'types.inc').write_text('\n'.join(re.search(p,s,re.S).group() for p in types));(out/'functions.inc').write_text('\n'.join(extract(s,n) for n in funcs))
 cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(out),str(Path(__file__).with_suffix('.c')),'-o',str(out/'test')];r=subprocess.run(cmd,capture_output=True,text=True);(out/'compile.log').write_text(r.stdout+r.stderr);print(r.stderr,end='');r.check_returncode()
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
 def run(mode,pack,valid=True):
  r=subprocess.run([str(out/'test'),mode,str(pack),str(int(valid)),str(out)],capture_output=True,text=True,env=env,timeout=120);assert r.returncode==0,(mode,str(pack),r.stdout,r.stderr);return r.stdout.strip()
 result={p:run('render',root/'assets/hd/packs'/p) for p in packs};print(result,flush=True)
 cases=[]
 with tempfile.TemporaryDirectory(prefix='coin25-seven-unit-') as tmp:
  pack=Path(tmp)
  for name,raw in raws.items():(pack/name).write_bytes(raw)
  assert run('loader',pack)
  for name,raw in raws.items():
   variants={'missing':None,'magic':b'BAD!'+raw[4:],'short-header':raw[:27],'truncated':raw[:-1],'trailing':raw+b'X','rgba':raw[:28]+bytes([raw[28]^1])+raw[29:],'alpha':raw[:31]+bytes([raw[31]^1])+raw[32:]}
   for label,offset,value in [('key',4,1),('density',8,4),('width',12,11),('height',16,13),('anchor-x',20,1),('anchor-y',24,1)]:
    bad=bytearray(raw);struct.pack_into('<I',bad,offset,value);variants[label]=bad
   for label,bad in variants.items():
    if bad is None:(pack/name).unlink()
    else:(pack/name).write_bytes(bad)
    run('loader',pack,False);cases.append([name,label]);(pack/name).write_bytes(raw)
  for name,raw in raws.items():
   (pack/name).unlink();rgba=raw[28:];(pack/name.replace('-8.','-4.')).write_bytes(raw[:8]+struct.pack('<I',4)+raw[12:28]+b''.join(rgba[(2*y*96+2*x)*4:(2*y*96+2*x)*4+4] for y in range(56) for x in range(48)))
  run('loader',pack,False);cases.append(['all','4x-only'])
  for name in raws:(pack/name).write_bytes(b'bad')
  run('loader',pack,False);cases.append(['all','invalid8-valid4'])
 report={'status':'PASS','game_runs':0,'sanitizers':['ASan','UBSan'],'baseline_commit':PIN,'changed_production_files':changed,'unchanged_functions':unchanged,'original_callsite_inverse':'byte-identical','immutable_inventory_sha256':INV,'art':outputs,'renderer_results':result,'resource_rejections':cases,'extracted_functions_sha256':{n:SHA(extract(s,n).encode()) for n in funcs},'source_sha256':{n:SHA((root/n).read_bytes()) for n in changed},'limitations':['No game or RGB runtime evidence; original-routine edge cases are in a separate extracted test.','Indexed RLE96-case differential uses actual unchanged blitters/wrapper, with display pixel hooks isolated; RGB compositor is tested separately.']};(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(cases),'resource rejections; report',out/'result.json')
if __name__=='__main__':main()
