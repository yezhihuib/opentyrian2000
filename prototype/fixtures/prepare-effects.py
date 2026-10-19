"""Prepare exact archived fixture sources and optionally rebuild their retired assets.

No executable is built or test run. Resource packs must use a new external output.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
repo=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--family',choices=['white-smoke-v1','shield-v1','green-trail'],required=True)
p.add_argument('--output',type=Path,required=True,help='New external directory for archived sources')
p.add_argument('--assets-output',type=Path,help='Rebuild the exact historical pack into a new absolute external directory')
a=p.parse_args();out=a.output.resolve()
if out.exists():p.error('Choose a new fixture output directory')
if out==repo or repo in out.parents:p.error('Keep fixture output outside the production checkout')
assets_out=None
if a.assets_output is not None:
 if not a.assets_output.is_absolute():p.error('Choose an absolute resource-pack output directory')
 assets_out=a.assets_output.resolve()
 if assets_out.exists():p.error('Choose a new resource-pack output directory')
 if assets_out==repo or repo in assets_out.parents:p.error('Keep resource-pack output outside the production checkout')
 if assets_out==out or out in assets_out.parents or assets_out in out.parents:p.error('Keep source and resource-pack outputs separate')
source=Path(__file__).parent/'effects'/a.family;m=json.loads((source/'manifest.json').read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
def production_matches(data,digest):
 if hashlib.sha256(data).hexdigest()==digest:return True
 # Accept only LF/CRLF checkout differences against the archived production
 # bytes, without ignoring content changes or normalizing exact overrides.
 lf=data.replace(b'\r\n',b'\n')
 # Never reinterpret a bare/extra CR as a second line-ending conversion.
 if b'\r' in lf:return False
 crlf=lf.replace(b'\n',b'\r\n')
 return digest in (hashlib.sha256(lf).hexdigest(),hashlib.sha256(crlf).hexdigest())
# Explicit reviewed production deltas only; every reversion must still match
# the historical manifest. Replacements preserve the checkout's line endings.
REVIEWED_DELTAS = {
 'src/tyrian2.c': [
  (b'\t\t\t\trender_mirror_bind_terrain(2,z+1,megaData2.shapes[x].sh);\n', b''),
  (b'\t\t\t\t\t\t{\n\t\t\t\t\t\t\tunsigned int sprite = enemyShot[z].sgr + enemyShot[z].animate;\n\t\t\t\t\t\t\tif (sprite == 112 || sprite == 113)\n\t\t\t\t\t\t\t\tdraw_enemy_shot_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);\n\t\t\t\t\t\t\telse\n\t\t\t\t\t\t\t\tblit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);\n\t\t\t\t\t\t}\n', b'\t\t\t\t\t\t\tblit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, enemyShot[z].sgr + enemyShot[z].animate);\n'),
 ],
 'src/entity_draw.h': [(b'/* Dedicated surviving enemy-shot normal tile; no player-shadow binding. */\nvoid draw_enemy_shot_sprite2(SDL_Surface *, int x, int y, Sprite2_array, unsigned int index);\n\n', b'')],
}
def historical_source(rel,data):
 changed=False
 for current,original in REVIEWED_DELTAS.get(rel,[]):
  variants=[(current,original),(current.replace(b'\n',b'\r\n'),original.replace(b'\n',b'\r\n'))]
  counts=[data.count(before) for before,after in variants]
  if sum(counts)>1:return None
  if sum(counts)==1:
   i=counts.index(1);before,after=variants[i]
   data=data.replace(before,after,1);changed=True
 return data if changed else None
historical_sources={}
for rel,digest in m['same_other_production_src_sha256'].items():
 data=(repo/rel).read_bytes()
 if production_matches(data,digest):continue
 archived=historical_source(rel,data)
 if archived is not None and production_matches(archived,digest):
  historical_sources[rel]=archived
  continue
 p.error('Production base changed; review fixture compatibility: '+rel)
# Check every frozen override before either output is created.
for rel,digest in m['tested_exact_source_overrides'].items():
 assert sha(source/'overrides'/rel)==digest
if assets_out is not None:
 sys.path.insert(0,str(repo/'prototype'))
 from rebuild_retired_hd_pack import build_pack
 try:build_pack(repo,m['test_resource_pack'],assets_out)
 except (OSError,ValueError) as exc:p.error('Historical resource-pack rebuild failed: '+str(exc))
out.mkdir(parents=True);shutil.copytree(repo/'src',out/'src');shutil.copytree(repo/'visualc',out/'visualc',ignore=shutil.ignore_patterns('Release','Debug','x64','ipch','*.obj','*.tlog'))
for rel,data in historical_sources.items():(out/rel).write_bytes(data)
for rel,digest in m['tested_exact_source_overrides'].items():
 assert sha(source/'overrides'/rel)==digest;shutil.copy2(source/'overrides'/rel,out/rel)
shutil.copy2(repo/'Makefile',out/'Makefile');(out/'prototype').mkdir();shutil.copy2(repo/'prototype/build-game.ps1',out/'prototype/build-game.ps1')
for n in ['SDL2.dll','SDL2_net.dll']:
 if (repo/n).exists():shutil.copy2(repo/n,out/n)
print('Prepared archived diagnostic sources:',out)
print('Required historical asset pack:',m['test_resource_pack'])
if assets_out is not None:print('Rebuilt exact archived asset pack:',assets_out)
else:
 print('Rebuild retired pack separately:',sys.executable,'prototype/rebuild_retired_hd_pack.py',m['test_resource_pack'],'--output ABS_NEW_EXTERNAL_DIRECTORY')
 print('Or pass --assets-output ABS_NEW_EXTERNAL_DIRECTORY to this preparation command.')
print('Use original legal game data separately; private hooks never enter production.')
