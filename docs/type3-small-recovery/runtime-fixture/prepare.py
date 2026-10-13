#!/usr/bin/env python3
"""Newly regenerated recovery fixture, source/build only; never launches game."""
from pathlib import Path
import hashlib,json,subprocess,shutil,os,shlex
ROOT=Path(__file__).resolve().parent
REPO=Path('/workspace/scratch/f67dd347fa0a/type3-small-recovery-20261013')
BASE='b2a6e4a1e924aed71630f9f63c0ba4648e920d6d'
HEAD='e976cb6a81aaa2eb99f5ffee14e58f9fc050dcb0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=lambda *a,**kw:subprocess.run(a,check=True,**kw)
def replace(text,a,b,count=1):
 assert text.count(a)==count,(a[:80],text.count(a),count)
 return text.replace(a,b)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()==HEAD
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
assert sha(REPO/'src/render_mirror.c')=='7a39ffd4959c307c23707ae63c41030cd92ef757375b95f680445ff4f3e85420'
assert not (ROOT/'build').exists()
build=ROOT/'build';build.mkdir();shutil.copytree(REPO/'src',build/'src')
shutil.copyfile(REPO/'Makefile',build/'Makefile')
src=build/'src'
t=(src/'tyrian2.c').read_text();t=replace(t,'void JE_starShowVGA(void)',(ROOT/'census.inc').read_text()+'\nvoid JE_starShowVGA(void)')
t=replace(t,'\t\tJE_eventSystem();\n','\t\tJE_eventSystem();\n\tif(asset_debug_enabled&&getenv("OT_LATE_TERRAIN_INVULNERABLE")&&player[0].is_alive&&player[0].invulnerable_ticks<2)player[0].invulnerable_ticks=2;\n\ttype3_census("post-events");\n')
for lane,name,count in ((50,'ground-50',1),(100,'ground-100',1),(25,'sky-25',2)):
 a='JE_drawEnemy(%d);'%lane;t=replace(t,a,'type3_census("pre-%s");%s type3_census("post-%s");'%(name,a,name),count)
t=replace(t,'\tasset_debug_projectile();','\ttype3_census("pre-projectiles");\n\tasset_debug_projectile();')
t=replace(t,'\t/* Player movement indicators for shots that track your ship */','\ttype3_census("post-projectiles");\n\t/* Player movement indicators for shots that track your ship */')
a='\tfor (uint i = 0; i < (twoPlayerMode ? 2 : 1); ++i)\n\t\tif (player[i].is_alive && !endLevel)\n\t\t\tJE_playerCollide(&player[i], i + 1);'
t=replace(t,a,'\ttype3_census("pre-body-collision");\n'+a+'\n\ttype3_census("post-body-collision");')
t=replace(t,'\tif (game_probe_end_tick())','\ttype3_census("end-tick");\n\tif (game_probe_end_tick())')
t=replace(t,'JE_setupExplosion(tempShotX, tempShotY, 0, 0, false, false);','type3_effect_witness(b,tempShotX,tempShotY,0);\n\t\t\t\t\t\t\t\t\tJE_setupExplosion(tempShotX, tempShotY, 0, 0, false, false);')
t=replace(t,'JE_setupExplosion(enemy_screen_x, enemy[temp2].ey, 0, 1, false, false);','type3_effect_witness(temp2,enemy_screen_x,enemy[temp2].ey,1);\n\t\t\t\t\t\t\t\t\t\t\tJE_setupExplosion(enemy_screen_x, enemy[temp2].ey, 0, 1, false, false);')
(src/'tyrian2.c').write_text(t)
a=(src/'asset_debug.c').read_text();a=replace(a,'#include "asset_debug.h"','#include "asset_debug.h"\n#include "tyrian2.h"\n#include "config.h"')
a=replace(a,'0,5999,"tick"','0,6531,"tick"');a=replace(a,'0,5999,"capture start"','0,6531,"capture start"')
a=replace(a,'void asset_debug_end_tick(void)',(ROOT/'pulses.inc').read_text()+'\nvoid asset_debug_end_tick(void)')
a=replace(a,'void asset_debug_end_tick(void)\n{','void asset_debug_end_tick(void)\n{\n type3_effect_pool();')
a=replace(a,'void asset_debug_projectile(void)\n{','void asset_debug_projectile(void)\n{\n type3_guard_pulse();')
a=replace(a,' shot_fixture=true;',' type3_check_shot(shot,s);\n shot_fixture=true;')
start=a.index('void asset_debug_readback(');end=a.index('void asset_debug_reference(',start)
a=a[:start]+(ROOT/'readback.inc').read_text()+'\n'+a[end:];(src/'asset_debug.c').write_text(a)
g=(src/'game_probe.c').read_text();assert g.count('6000')==3;g=g.replace('6000','6532');(src/'game_probe.c').write_text(g)
changed={p.name for p in src.iterdir() if p.is_file() and p.read_bytes()!=(REPO/'src'/p.name).read_bytes()};assert changed=={'tyrian2.c','asset_debug.c','game_probe.c'}
for name in sorted(changed):
 with (ROOT/(name+'.patch')).open('wb') as f:subprocess.run(['diff','-u',str(REPO/'src'/name),str(src/name)],stdout=f)
with (ROOT/'build.log').open('w') as f:run('make','-j2','VCS_IDREV=echo '+HEAD,cwd=build,stdout=f,stderr=subprocess.STDOUT)
bins=ROOT/'bin';bins.mkdir();shutil.copyfile(build/'opentyrian2000',bins/'candidate');(bins/'candidate').chmod(0o755)
shutil.copytree(build/'obj',ROOT/'candidate-objects')
base=subprocess.check_output(['git','show',BASE+':src/render_mirror.c'],cwd=REPO);assert hashlib.sha256(base).hexdigest()=='54bac8607c45879e0674344525e9f2f6af0d873c1537fac87cb80ef1cef376eb'
(src/'render_mirror.c').write_bytes(base)
with (ROOT/'baseline-build.log').open('w') as f:run('make','-j2','VCS_IDREV=echo '+HEAD,cwd=build,stdout=f,stderr=subprocess.STDOUT)
shutil.copyfile(build/'opentyrian2000',bins/'baseline');(bins/'baseline').chmod(0o755)
(src/'render_mirror.c').write_bytes((REPO/'src/render_mirror.c').read_bytes())
pack='packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test'
packs=ROOT/'packs';packs.mkdir()
for kind in ('candidate','baseline','missing266','corrupt209'):
 shutil.copytree(REPO/'assets/hd/packs'/pack,packs/kind)
 if kind=='baseline':
  for i in (171,190,209,228,247,266):(packs/kind/f'enemy-newsh2-{i}-8.hda').unlink()
 elif kind=='missing266':(packs/kind/'enemy-newsh2-266-8.hda').unlink()
 elif kind=='corrupt209':
  p=packs/kind/'enemy-newsh2-209-8.hda';b=bytearray(p.read_bytes());b[28]^=1;p.write_bytes(b)
objects={p.name:sha(p) for p in (build/'obj').glob('*.o')};candidate_objects={p.name:sha(p) for p in (ROOT/'candidate-objects').glob('*.o')};assert {n for n in objects if objects[n]!=candidate_objects[n]}=={'render_mirror.o'}
files={str(p.relative_to(ROOT)):sha(p) for folder in (src,build/'obj',ROOT/'candidate-objects',bins,packs) for p in sorted(folder.rglob('*')) if p.is_file()}
data=Path(os.environ['TYRIAN_DATA']);data_files={str(p.relative_to(data)):sha(p) for p in sorted(data.rglob('*')) if p.is_file()}
receipt={'status':'PREPARED_NO_GAME_RUN','recovery':'Newly regenerated fixture from retained approved contract, not exact historical fixture bytes','source_head':HEAD,'baseline':BASE,'production_source':{str(p.relative_to(REPO)):sha(p) for p in sorted((REPO/'src').iterdir()) if p.is_file()},'only_linked_object_difference':'render_mirror.o','files':files,'data_root':str(data),'data_files':data_files,'scripts':{p.name:sha(p) for p in ROOT.iterdir() if p.suffix in ('.py','.inc')},'windows':[[6181,6192],[6512,6531]],'pulses':[6513,6515,6517],'body_collision_coverage':False,'type16_or_boss_spawn_coverage':False,'artificial_original_projectiles':True}
(ROOT/'provenance.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
print(json.dumps({'status':receipt['status'],'executables':{p.name:sha(p) for p in bins.iterdir()},'file_pins':len(files),'original_data_pins':len(data_files)},indent=2))
