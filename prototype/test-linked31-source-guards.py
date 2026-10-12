#!/usr/bin/env python3
"""Bounded generated-only/source/import negative cases. Never runs the game."""
from pathlib import Path
import argparse,json,shutil,subprocess,sys
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];given=a.out.absolute();out=given.resolve()
if out.exists() or any(q.is_symlink() for q in [given,*given.parents]) or out==repo or out in repo.parents or repo in out.parents:p.error('Fresh output outside repository required')
out.mkdir(parents=True);script=repo/'prototype/build-linked31-art.py';checks=[]
def rejected(label,target,wrapper=script):
 r=subprocess.run([sys.executable,str(wrapper),'--output',str(target)],capture_output=True,text=True,timeout=90)
 assert r.returncode!=0,label;checks.append(label)
for label,target in [('existing',out),('repository',repo),('repository-child',repo/'linked31-forbidden-output'),('repository-parent',repo.parent)]:rejected(label,target)
assert not(repo/'linked31-forbidden-output').exists()
link=out/'link';link.symlink_to(out,target_is_directory=True);rejected('symlink-parent',link/'absent');assert not(out/'absent').exists()
direct=out/'direct';direct.symlink_to(out/'absent',target_is_directory=True);rejected('symlink-output',direct)
m=json.loads((repo/'assets/hd/manifest.json').read_text());src='assets/hd/artwork/linked31-assembly-v1';minimal=out/'pristine';(minimal/'prototype').mkdir(parents=True);shutil.copy2(script,minimal/'prototype/build-linked31-art.py');shutil.copytree(repo/src,minimal/src);shutil.copy2(repo/'assets/hd/manifest.json',minimal/'assets/hd/manifest.json')
files=set()
for c in json.loads((repo/src/'contract.json').read_text())['entries']:
 name=('terrain-shapesz' if c['kind']=='terrain' else 'enemy-newsh2')+f"-{c['source_id']}-8.hda"
 for key in ['default_preview_pack','default_debug_pack']:
  e=m['packs'][m[key]]['files'][name];files.add(e['source_png']);files.add(str(Path('assets/hd/packs')/m[key]/name))
for guard in json.loads((repo/src/'proof/context-proof.json').read_text())['guards']:files.add(guard['source_png'])
for rel in files:(minimal/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/rel,minimal/rel)
r=subprocess.run([sys.executable,str(minimal/'prototype/build-linked31-art.py'),'--output',str(out/'valid')],capture_output=True,text=True,timeout=90);r.check_returncode()
# Mutate one isolated minimal tree in place and restore immediately: no duplicate packs.
mutations={'master':src+'/sources/generated-paired-context.png','prompt':src+'/sources/prompt.txt','contract':src+'/contract.json','recipe':src+'/rebuild.py','inventory':src+'/inventory.json','proof':src+'/proof/composite-proof.json','canonical-png':m['packs'][m['default_preview_pack']]['files']['enemy-newsh2-15-8.hda']['source_png'],'packed-hda':str(Path('assets/hd/packs')/m['default_preview_pack']/'terrain-shapesz-161-8.hda')}
for label,rel in mutations.items():
 q=minimal/rel;raw=q.read_bytes();q.write_bytes(raw+b'\0');rejected(label,out/('bad-'+label),minimal/'prototype/build-linked31-art.py');q.write_bytes(raw)
for label in ['unlisted-source','source-symlink','widened4x']:
 if label=='unlisted-source':
  q=minimal/src/'reference.png';q.write_bytes(b'not-an-approved-input');rejected(label,out/('bad-'+label),minimal/'prototype/build-linked31-art.py');q.unlink()
 elif label=='source-symlink':
  q=minimal/src/'sources/generated-paired-context.png';raw=q.read_bytes();q.unlink();q.symlink_to(repo/src/'sources/generated-paired-context.png');rejected(label,out/('bad-'+label),minimal/'prototype/build-linked31-art.py');q.unlink();q.write_bytes(raw)
 else:
  q=minimal/'assets/hd/manifest.json';raw=q.read_bytes();changed=json.loads(raw);pack=changed['packs'][changed['default_debug_pack']];pack['files']['enemy-newsh2-15-4.hda']=pack['files']['enemy-newsh2-15-8.hda'];pack['count']+=1;q.write_text(json.dumps(changed));rejected(label,out/('bad-'+label),minimal/'prototype/build-linked31-art.py');q.write_bytes(raw)
report={'status':'passed','valid_generated_only_reproduction':True,'rejected_cases':checks,'original_RGB_inputs':False,'game_runs':0};(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
