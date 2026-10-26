#!/usr/bin/env python3
"""Finite dualmissile native matrix, composed with immutable historical helpers.

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
 source=source.replace('tests/newshf_compositor_validation.c','tests/dualmissile_newshf_native_validation.c')
 marker="+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big'))";assert source.count(marker)==1
 source=source.replace(marker,"+b''.join(raw[177182+p*77:177182+(p+1)*77] for p in range(3))+raw[164169:164246]+raw[202515:202592]"+marker)
 marker=" content=resource_root/'content'";assert source.count(marker)==1
 fixture='''
 for group in ('newshf-linked','newshf-dualmissile'):
  (resource_root/group).mkdir(exist_ok=True)
  for asset in (ROOT/'assets/hd/current-compat'/group).glob('*.hda'):shutil.copyfile(asset,resource_root/group/asset.name)
 groups={'newshf':current_paths,'newshf-linked':list((ROOT/'assets/hd/current-compat/newshf-linked').glob('*.hda')),'newshf-dualmissile':list((ROOT/'assets/hd/current-compat/newshf-dualmissile').glob('*.hda'))}
 assert len(groups['newshf-linked'])==6 and len(groups['newshf-dualmissile'])==1
 for mode in ('missing','corrupt','header','trailing','dual-only','no-linked','no-old'):
  fixture=resource_root/(mode+'-dual' if mode in ('missing','corrupt','header','trailing') else mode);fixture.mkdir(exist_ok=True)
  for group,assets in groups.items():
   if mode=='dual-only' and group!='newshf-dualmissile':continue
   if mode=='no-linked' and group=='newshf-linked':continue
   if mode=='no-old' and group=='newshf':continue
   (fixture/group).mkdir(exist_ok=True)
   for asset in assets:
    data=bytearray(asset.read_bytes())
    if group=='newshf-dualmissile':
     if mode=='missing':continue
     if mode=='corrupt':data[31]^=1
     if mode=='header':data[4]^=1
     if mode=='trailing':data+=b'!'
    (fixture/group/asset.name).write_bytes(data)
'''
 source=source.replace(marker,fixture+marker)
 start=source.index(' transfer_line=');end=source.index(' unchanged=',start)
 source=source[:start]+" accepted=r.returncode==0\n"+source[end:]
 source=source.replace("report={'scope':'Full native SDL production objects and actual sprite blits/JE_makeEnemy; no game loop or E1 acceptance'", "report={'scope':'Dualmissile records2/500 plus existing15 resources; actual production allocation/blits; no game loop or Windows acceptance'")
 exec(compile(source,str(ROOT/'tests/newshf_compositor_validation.py'),'exec'),{'__name__':'__main__','__file__':str(ROOT/'tests/newshf_compositor_validation.py')})
if __name__=='__main__':main()
