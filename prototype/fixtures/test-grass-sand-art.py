"""Independently audit frozen v3 art, exact7c7 pack delta and deterministic rebuild.

All outputs and temporary compiler products are retained outside source roots.
No original game data, game execution, screenshots, network or generation.
"""
from pathlib import Path
import argparse, json, os, subprocess, sys, tempfile
import grass_sand_art_oracle as oracle
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[2])
p.add_argument('--package',type=Path,required=True)
p.add_argument('--pack',type=Path,required=True,help='Frozen329-file debug candidate pack')
p.add_argument('--baseline-manifest',type=Path,help='Exact7c7 manifest for archive/no-Git use')
p.add_argument('--rebuild',action='store_true',help='Run frozen corrected rebuilder from unrelated directory')
p.add_argument('--report',type=Path)
a=p.parse_args();source=a.source.resolve();package=a.package.resolve();pack=a.pack.resolve()
raw=a.baseline_manifest.read_bytes() if a.baseline_manifest else subprocess.check_output(['git','-C',str(source),'show',oracle.BASE+':assets/hd/manifest.json'])
base=oracle.baseline(raw);before={str(f.relative_to(package)):oracle.sha(f.read_bytes()) for f in package.rglob('*') if f.is_file()}
package_report=oracle.package(package)
prior=base['packs'][base['default_debug_pack']]['files'];current={f.name for f in pack.glob('*.hda')}
assert len(prior)==320 and len(current)==329 and current-set(prior)==oracle.NEW and not(set(prior)-current), 'Candidate must be exactly320 current7c7 peers plus nine selected additions'
for name,record in prior.items():assert oracle.sha((pack/name).read_bytes())==record['sha256'], ('Changed baseline peer',name)
for r in oracle.freeze()['assets']:
 assert (pack/Path(r['hda']).name).read_bytes()==oracle.owned(package,r['hda']).read_bytes(), ('Pack differs from frozen selected art',r['source_id'])
assert oracle.sha((pack/'terrain-shapesz-64-8.hda').read_bytes())==oracle.CLOUD64_HDA
# Frozen sand47 is the same accepted generated texture, not an added asset.
sand=oracle.image_bytes((package/'source/frozen-generated-sand47.png').read_bytes(),[192,224])
assert (pack/'terrain-shapesz-47-8.hda').read_bytes()[28:]==sand
for relative,digest in oracle.FROZEN_PURPLE_METADATA.items():assert oracle.sha(oracle.owned(source,relative).read_bytes())==digest, relative
work=Path(tempfile.mkdtemp(prefix='grass9-art-independent-'));results=[];guards=[]
if a.rebuild:
 # Retention is the sole wrapper change: the rebuilder's TemporaryDirectory
 # becomes an undeleted test directory. Actual rebuilder source is untouched.
 wrapper="""import runpy,sys,tempfile
class Retained:
 def __init__(self,*args,**kwargs):self.name=tempfile.mkdtemp(*args,**kwargs)
 def __enter__(self):return self.name
 def __exit__(self,*args):print('Retained compiler work:',self.name)
tempfile.TemporaryDirectory=Retained
script=sys.argv[1];sys.argv=sys.argv[1:];runpy.run_path(script,run_name='__main__')
"""
 command=[sys.executable,'-c',wrapper,str(package/'rebuild.py'),'--output-dir',str(work/'rebuilt in unrelated path')]
 run=subprocess.run(command,cwd=work,text=True,capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 (work/'rebuild.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 out=work/'rebuilt in unrelated path';assert {f.name for f in (out/'runtime-overlay').glob('*.hda')}==oracle.NEW
 for r in oracle.freeze()['assets']:
  png=(out/r['png']).read_bytes();rgba=oracle.image_bytes(png,[192,224]);hda=(out/r['hda']).read_bytes()
  assert oracle.sha(rgba)==r['rgba_sha256'] and hda==oracle.owned(package,r['hda']).read_bytes()
  results.append({'id':r['source_id'],'rgba_exact':True,'hda_exact':True,'png_encoder_file_exact':oracle.sha(png)==r['png_sha256']})
 # Exercise rejection on a private minimal package path, without risking the
 # frozen source: validation occurs before any output creation or compile.
 guarded=work/'guard package';guarded.mkdir()
 for name in ['rebuild.py','contract.json']:(guarded/name).write_bytes((package/name).read_bytes())
 occupied=work/'occupied';occupied.mkdir();(occupied/'sentinel').write_text('Keep this file unchanged.\n')
 for label,target in [('same-package',guarded),('ancestor',work),('nested-package',guarded/'must not be written'),('occupied-output',occupied)]:
  command=[sys.executable,str(guarded/'rebuild.py'),'--output-dir',str(target)]
  run=subprocess.run(command,cwd=work,text=True,capture_output=True)
  assert run.returncode!=0 and 'Use an empty, separate output directory' in run.stderr,(label,run.stderr)
  assert not(guarded/'must not be written').exists() and (occupied/'sentinel').read_text()=='Keep this file unchanged.\n'
  guards.append({'case':label,'rejected_before_write':True})
assert before=={str(f.relative_to(package)):oracle.sha(f.read_bytes()) for f in package.rglob('*') if f.is_file()}, 'Frozen package mutated during audit'
report={'status':'passed','baseline_commit':oracle.BASE,'baseline_manifest_sha256':oracle.BASE_MANIFEST_SHA,'candidate_pack_count':329,'exact_nine_additions':True,'all320_prior_hda_unchanged':True,'current64_hda_sha256':oracle.CLOUD64_HDA,'frozen47_generated_input_matches_prior_hda':True,'package':package_report,'rebuild_run':a.rebuild,'rebuilt':results,'output_guards':guards,'package_unchanged':True,'retained_work':str(work),'scope':'Independent file/hash/header/pixel/rebuild audit only; no game/capture/visual acceptance; no original data required for rebuild.'}
out=a.report or work/'result.json';out.write_text(json.dumps(report,indent=2)+'\n')
print('PASS: frozen grass9 v3; exact current7c7 +9 with320 peers unchanged; '+('all9 rebuilt RGBA/HDA exact; four output guards reject.' if a.rebuild else 'rebuild not requested.'));print('Report:',out)
