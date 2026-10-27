#!/usr/bin/env python3
"""Finite record166 native matrix, exact historical driver adapter.

Three fresh production configurations, ASan/UBSan renderer/sprite/tyrian2
and harness. LSan disabled for the established environment limitation.
Original inputs remain private stdin bytes. This is not natural gameplay.
"""
import hashlib,json,sys
from pathlib import Path
from current_newshf_native_validation import transformed,ROOT

def main():
 global ROOT
 if '--source-root' in sys.argv:
  i=sys.argv.index('--source-root');ROOT=Path(sys.argv[i+1]).resolve();del sys.argv[i:i+2]
 assert not any(x in sys.argv for x in ('--skip-build','--negative-control','--compose-negative-control')), 'Use a new output directory and fresh production builds'
 if '--out' in sys.argv:assert not Path(sys.argv[sys.argv.index('--out')+1]).exists(), 'Native proof output must be new'
 source=transformed(ROOT,(ROOT/'tests/newshf_compositor_validation.py').read_bytes())
 def once(old,new):
  nonlocal source
  assert source.count(old)==1,('historical driver marker drift',old)
  source=source.replace(old,new)
 once('assert shutil.disk_usage(a.out).free>5*1024**3',
      '# Three fresh builds plus16 bounded fixtures require under300MiB; retain512MiB floor.\n assert shutil.disk_usage(a.out).free>512*1024**2')
 once(" rows=current.load(ROOT)"," rows=current.load(ROOT)\n import current_interceptor166_newshf_compatibility as fighter\n from check_interceptor166_newshf_pins import verify as verify_fighter_pins\n assert len(fighter.load(ROOT))==3\n verify_fighter_pins(ROOT,a.original_data)")
 once("   cmd=['make','-j3'","   shutil.copytree(ROOT/'src/third_party',build/'src/third_party',dirs_exist_ok=True)\n   cmd=['make','-j3'")
 source=source.replace('timeout=240','timeout=900')
 source=source.replace('tests/newshf_compositor_validation.c','tests/interceptor166_newshf_native_validation.c')
 once(" snap={str(x.relative_to(ROOT)):SHA(x.read_bytes()) for x in (ROOT/'src').iterdir() if x.is_file()}",""" snap={str(x.relative_to(ROOT)):SHA(x.read_bytes()) for x in (ROOT/'src').rglob('*') if x.is_file()}
 test_names=['tests/interceptor166_newshf_native_validation.c','tests/interceptor166_newshf_native_validation.py','tests/newshf_compositor_validation.c','tests/newshf_compositor_validation.py','tests/current_newshf_native_validation.py','Makefile']
 test_names += [p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*.py')]
 test_snap={n:SHA((ROOT/n).read_bytes()) for n in test_names}
 groups=('newshf','newshf-linked','newshf-dualmissile','newshf-turret','newshi-large','newshf-scout164','newshf-fighter165','newshf-interceptor166')
 def asset_snapshot():
  paths={p for g in groups for p in (ROOT/'assets/hd/current-compat'/g).rglob('*') if p.is_file()}
  paths |= {ROOT/n for n in current.input_paths(ROOT)|fighter.input_paths(ROOT)}
  paths |= {p for p in (ROOT/'authoring-inputs/newshf-interceptor166').rglob('*') if p.is_file()}
  return {str(p.relative_to(ROOT)):SHA(p.read_bytes()) for p in paths}
 assets_before=asset_snapshot()
 original_names=('newshf.shp','newshi.shp','tyrian.hdt','palette.dat','tyrian.shp')
 originals_before={n:SHA((a.original_data/n).read_bytes()) for n in original_names}
 assert originals_before['newshi.shp']=='226da9b33b9b16f7a4212b9cc785fbd82c9517172b3a15a7f58798a38b0a12e4'
 assert SHA((a.original_data/'tyrian.hdt').read_bytes()[176797:176874])=='ebed7f3f1d90d73c439412e79cc69d03e640dc75e619ab31c27c4440e9904378'
""")
 once("'source_sha256':snap,","'source_sha256':snap,'test_sha256':test_snap,'asset_sha256':assets_before,'original_sha256':originals_before,")
 once("+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big'))", "+raw[176797:176874]+raw[176720:176797]+(a.original_data/'newshi.shp').read_bytes()+raw[187269:187346]+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big'))")
 once(" content=resource_root/'content'", """
 for group in groups[1:]:
  (resource_root/group).mkdir(exist_ok=True)
  for asset in (ROOT/'assets/hd/current-compat'/group).glob('*.hda'):shutil.copyfile(asset,resource_root/group/asset.name)
 group_assets={'newshf':current_paths,**{g:sorted((ROOT/'assets/hd/current-compat'/g).glob('*.hda')) for g in groups[1:]}}
 assert [len(group_assets[g]) for g in groups]==[9,6,1,2,10,3,3,3]
 for mode in ('missing','corrupt','header','trailing','interceptor-only','old-only','no-large','no-old','no-fighter165'):
  for state in range(3 if mode in ('missing','corrupt','header','trailing') else 1):
   fixture=resource_root/(mode+'-interceptor'+str(state) if mode in ('missing','corrupt','header','trailing') else mode);fixture.mkdir(exist_ok=True)
   for group,assets in group_assets.items():
    if mode=='interceptor-only' and group!='newshf-interceptor166':continue
    if mode=='old-only' and group=='newshf-interceptor166':continue
    if mode=='no-large' and group=='newshi-large':continue
    if mode=='no-old' and group=='newshf':continue
    if mode=='no-fighter165' and group=='newshf-fighter165':continue
    (fixture/group).mkdir(exist_ok=True)
    for asset in assets:
     data=bytearray(asset.read_bytes())
     if group=='newshf-interceptor166' and asset==group_assets[group][state]:
      if mode=='missing':continue
      if mode=='corrupt':data[31]^=1
      if mode=='header':data[4]^=1
      if mode=='trailing':data+=b'!'
     (fixture/group/asset.name).write_bytes(data)
 content=resource_root/'content'""")
 start=source.index(' transfer_line=');end=source.index(' unchanged=',start)
 source=source[:start]+" accepted=r.returncode==0\n"+source[end:]
 once('accepted=accepted and unchanged',"""test_unchanged=all(SHA((ROOT/n).read_bytes())==h for n,h in test_snap.items())
 assets_unchanged=asset_snapshot()==assets_before
 originals_after={n:SHA((a.original_data/n).read_bytes()) for n in original_names}
 originals_unchanged=originals_after==originals_before
 accepted=accepted and unchanged and test_unchanged and assets_unchanged and originals_unchanged""")
 once('source_unchanged=unchanged,free_disk_bytes','source_unchanged=unchanged,test_unchanged=test_unchanged,assets_unchanged=assets_unchanged,originals_unchanged=originals_unchanged,original_after_sha256=originals_after,free_disk_bytes')
 source=source.replace("Full native SDL production objects and actual sprite blits/JE_makeEnemy; no game loop or E1 acceptance","NEWSHF166 three controlled poses, finite37-resource bank routing and group isolation; actual production allocation/blits; no natural banking or Windows acceptance")
 exec(compile(source,str(ROOT/'tests/newshf_compositor_validation.py'),'exec'),{'__name__':'__main__','__file__':str(ROOT/'tests/newshf_compositor_validation.py')})
if __name__=='__main__':main()
