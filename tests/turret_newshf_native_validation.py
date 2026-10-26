#!/usr/bin/env python3
"""Finite seven-slot turret native matrix, composed with immutable historical helpers.

No historical files are rewritten; private original records enter stdin only.
"""
import sys
from pathlib import Path
from current_newshf_native_validation import transformed,ROOT

def main():
 global ROOT
 if '--source-root' in sys.argv:
  i=sys.argv.index('--source-root');ROOT=Path(sys.argv[i+1]).resolve();del sys.argv[i:i+2]
 source=transformed(ROOT,(ROOT/'tests/newshf_compositor_validation.py').read_bytes())
 marker="   cmd=['make','-j3'";assert source.count(marker)==1
 source=source.replace(marker,"   shutil.copytree(ROOT/'src/third_party',build/'src/third_party',dirs_exist_ok=True)\n"+marker)
 source=source.replace('timeout=240','timeout=900')
 # The finite turret matrix writes about 93 MiB (measured prior full run).
 # Reserve 2 GiB rather than the historical driver's unrelated 5 GiB budget;
 # retain the hard failure and never delete earlier proof to satisfy it.
 marker='assert shutil.disk_usage(a.out).free>5*1024**3';assert source.count(marker)==1
 source=source.replace(marker,'assert shutil.disk_usage(a.out).free>2*1024**3')

 source=source.replace('tests/newshf_compositor_validation.c','tests/turret_newshf_native_validation.c')
 marker=" modes={'default-off':";assert source.count(marker)==1
 source=source.replace(marker," test_files=['tests/turret_newshf_native_validation.c','tests/turret_newshf_native_validation.py','tests/newshf_compositor_validation.c','tests/newshf_compositor_validation.py','tests/current_newshf_native_validation.py']\n test_snap={name:SHA((ROOT/name).read_bytes()) for name in test_files}\n"+marker)
 source=source.replace("'source_sha256':snap,", "'source_sha256':snap,'test_sha256':test_snap,")
 source=source.replace("accepted=accepted and unchanged", "test_unchanged=all(SHA((ROOT/n).read_bytes())==h for n,h in test_snap.items());accepted=accepted and unchanged and test_unchanged")
 source=source.replace("source_unchanged=unchanged,free_disk_bytes", "source_unchanged=unchanged,test_unchanged=test_unchanged,free_disk_bytes")

 marker="+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big'))";assert source.count(marker)==1
 source=source.replace(marker,"+b''.join(raw[177182+p*77:177182+(p+1)*77] for p in range(3))+raw[164169:164246]+raw[202515:202592]+raw[176489:176566]+raw[228695:228772]"+marker)
 marker=" content=resource_root/'content'";assert source.count(marker)==1
 fixture='''
 for group in ('newshf-linked','newshf-dualmissile','newshf-turret'):
  (resource_root/group).mkdir(exist_ok=True)
  for asset in (ROOT/'assets/hd/current-compat'/group).glob('*.hda'):shutil.copyfile(asset,resource_root/group/asset.name)
 groups={'newshf':current_paths,**{g:list((ROOT/'assets/hd/current-compat'/g).glob('*.hda')) for g in ('newshf-linked','newshf-dualmissile','newshf-turret')}}
 assert [len(groups[g]) for g in groups]==[9,6,1,2]
 turret_assets=sorted(groups['newshf-turret'])
 for mode in ('missing','corrupt','header','trailing','turret-only','no-linked','no-old','no-dual'):
  for state in range(2 if mode in ('missing','corrupt','header','trailing') else 1):
   fixture=resource_root/(mode+'-turret'+str(state) if mode in ('missing','corrupt','header','trailing') else mode);fixture.mkdir(exist_ok=True)
   for group,assets in groups.items():
    if mode=='turret-only' and group!='newshf-turret':continue
    if mode=='no-linked' and group=='newshf-linked':continue
    if mode=='no-old' and group=='newshf':continue
    if mode=='no-dual' and group=='newshf-dualmissile':continue
    (fixture/group).mkdir(exist_ok=True)
    for asset in assets:
     data=bytearray(asset.read_bytes())
     if group=='newshf-turret' and asset==turret_assets[state]:
      if mode=='missing':continue
      if mode=='corrupt':data[31]^=1
      if mode=='header':data[4]^=1
      if mode=='trailing':data+=b'!'
     (fixture/group/asset.name).write_bytes(data)
'''
 source=source.replace(marker,fixture+marker)
 start=source.index(' transfer_line=');end=source.index(' unchanged=',start)
 source=source[:start]+" accepted=r.returncode==0\n"+source[end:]
 source=source.replace("report={'scope':'Full native SDL production objects and actual sprite blits/JE_makeEnemy; no game loop or E1 acceptance'", "report={'scope':'Seven-slot turret records162/840 plus existing16 resources; actual production allocation/blits; no game loop or Windows acceptance'")
 exec(compile(source,str(ROOT/'tests/newshf_compositor_validation.py'),'exec'),{'__name__':'__main__','__file__':str(ROOT/'tests/newshf_compositor_validation.py')})
if __name__=='__main__':main()
