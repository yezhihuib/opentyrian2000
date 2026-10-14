#!/usr/bin/env python3
"""Exact finite production/resource inverse for the normal front Multi checkpoint.
No original game data, game execution, complete pack extraction or network access.
"""
import argparse,hashlib,importlib.util,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='7df8368acb90a73b170b1238b3161eefddb7a8e1'
INVENTORY='b14abd722c64358ab3d465ad213d64eb6c9ab39a57cefc4c907ddbd0818f1084'
IDS=[121,122,163,164,201,202,279,280]
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();assert not out.exists() and ROOT not in out.parents
 spec=importlib.util.spec_from_file_location('front_multi_binding',ROOT/'prototype/test-front-multi-binding.py');binding=importlib.util.module_from_spec(spec);spec.loader.exec_module(binding)
 sources,scope=binding.source_scope(ROOT,a.baseline.resolve())
 mpath=ROOT/'assets/hd/manifest.json';original=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':assets/hd/manifest.json']);manifest=json.loads(mpath.read_bytes());before=json.loads(original)
 art=ROOT/'assets/hd/artwork/player-front-multi-eight-v1';raw=(art/'inventory.json').read_bytes();assert sha(raw)==INVENTORY;inv=json.loads(raw);assert inv['ids']==IDS
 for name,digest in inv['inputs'].items():assert sha((art/name).read_bytes())==digest,name
 entries=[];added=[];packs={}
 for q in inv['outputs']:
  i=IDS.index(q['id']);assert q['slot']==524+i
  hda=(art/'output'/q['hda']).read_bytes();png=(art/'output'/q['png']).read_bytes()
  assert hda[:28]==struct.pack('<4s6I',b'HDR1',80000+q['id'],8,12,14,0,0) and len(hda)==43036
  assert sha(hda)==q['HDA_SHA256'] and sha(png)==q['PNG_SHA256'] and sha(hda[28:])==q['RGBA_SHA256'] and sha(hda[31::4])==q['ALPHA_SHA256']
  source=f"assets/hd/source/bullet-{q['id']}-8-{q['HDA_SHA256'][:12]}.png";assert (ROOT/source).read_bytes()==png
  assert manifest['source_pngs'][q['HDA_SHA256']]=={'path':source,'sha256':q['PNG_SHA256'],'RGBA_sha256':q['RGBA_SHA256']};added.append(source)
  for kind in ['preview','debug']:
   name=manifest['default_'+kind+'_pack'];path=f'assets/hd/packs/{name}/{q["hda"]}';assert (ROOT/path).read_bytes()==hda
   assert not (ROOT/path.replace('-8.hda','-4.hda')).exists()
   assert manifest['packs'][name]['files'][q['hda']]=={'header_u32':[80000+q['id'],8,12,14,0,0],'sha256':q['HDA_SHA256'],'source_png':source,'source_png_sha256':q['PNG_SHA256']};added.append(path)
  entries.append({'id':q['id'],'slot':q['slot'],'HDA_sha256':q['HDA_SHA256']})
 restored=json.loads(mpath.read_bytes());family=restored.pop('player_front_multi_eight_v1');assert family['entries']==entries and family['inventory_sha256']==INVENTORY
 for q in entries:
  del restored['source_pngs'][q['HDA_sha256']]
  for kind in ['preview','debug']:
   name=restored['default_'+kind+'_pack'];del restored['packs'][name]['files'][f"bullet-{q['id']}-8.hda"];restored['packs'][name]['count']-=1
 assert (json.dumps(restored,indent=2,ensure_ascii=False)+'\n').encode()==original,'Manifest inverse must be byte-exact'
 for kind in ['preview','debug']:
  name=manifest['default_'+kind+'_pack'];prefix=f'assets/hd/packs/{name}/';oldpaths=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only',BASE,'--',prefix],text=True).splitlines();old_hda=[n for n in oldpaths if n.endswith('.hda')];listed=before['packs'][name]['files'];unlisted=[n for n in old_hda if n[len(prefix):]not in listed]
  assert len(old_hda)==538 and len(listed)==before['packs'][name]['count']==532 and len(unlisted)==6
  assert len(manifest['packs'][name]['files'])==manifest['packs'][name]['count']==540
  for n in oldpaths:
   materialized=ROOT/n
   if materialized.exists():assert materialized.read_bytes()==subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+n]),'Changed old resource '+n
  packs[kind]={'pack':name,'listed_before':532,'listed_after':540,'physical_before':538,'physical_after':546,'preserved_unlisted':unlisted,'old_materialized_files_verified':sum((ROOT/n).exists()for n in oldpaths)}
 # Every tracked source/art/test outside the finite production and manifest delta stays pinned.
 changes=[line.split('\t')for line in subprocess.check_output(['git','-C',str(ROOT),'diff','--name-status',BASE],text=True).splitlines()]
 assert all(row[0]in {'A','M'}for row in changes),changes
 modified={row[1]for row in changes if row[0]=='M'}
 assert modified-{'README.md','README.zh-CN.md'}=={'src/render_mirror.c','assets/hd/manifest.json'},changes
 new=set(subprocess.check_output(['git','-C',str(ROOT),'ls-files','--others','--exclude-standard'],text=True).splitlines())|{row[1]for row in changes if row[0]=='A'}
 allowed={'prototype/test-front-multi-'+kind+suffix for kind in ['original','binding']for suffix in ['.py','.c']}|{'prototype/test-front-multi-scope.py'}
 optional_docs={f'docs/player-front-multi-eight-v1/{name}'for name in ['README.md','source-scope.json','original-unit-summary.json','renderer-unit-summary.json','build-result.json','runtime-summary.json','author-review-summary.json']}
 allowed|=new&optional_docs
 package_names={'README.md','inventory.json','author-geometry.cjs','rebuild.cjs','output/rebuild-receipt.json'}|{f'sources/multi-{i}.svg'for i in IDS}|{f'output/bullet-{i}-8.{ext}'for i in IDS for ext in ['png','hda']}|{f'proof/{n}'for n in ['offline-author-gate.json','verify-nearest.log','v3-shading-only-check.json','geometry-alpha-checks.json','renderer-versions.json','verify-nearest.c','relocated-rebuild-check.json']}
 assert {str(p.relative_to(art))for p in art.rglob('*')if p.is_file()}==package_names,'Unexpected frozen package content'
 expected_art={str(art.relative_to(ROOT)/n)for n in package_names}
 assert new==set(added)|expected_art|allowed,'Unexpected new files: '+str(new^(set(added)|expected_art|allowed))
 report={'status':'PASS','baseline':BASE,'game_runs':0,'production_scope':scope,'manifest_inverse_exact_bytes':True,'frozen_inventory_sha256':INVENTORY,'packs':packs,'new_resource_files':added,'frozen_package_sha256':{str(p.relative_to(art)):sha(p.read_bytes())for p in art.rglob('*')if p.is_file()},'historical_tests_unchanged':True,'updated_root_readmes':sorted(modified&{'README.md','README.zh-CN.md'}),'only_production_file_changed':'src/render_mirror.c','no_full_pack_materialization':True,'harness_sha256':sha(Path(__file__).read_bytes())};out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('PASS: three renderer semantics + comment, exact manifest inverse, eight frozen heads per default pack; historical code/art/tests unchanged outside the declared delta; bounded docs allowed.')
if __name__=='__main__':main()
