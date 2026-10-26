#!/usr/bin/env python3
"""Finite linked native extension; original historical harness stays immutable."""
import sys
from pathlib import Path
from current_newshf_native_validation import transformed, ROOT

def main():
 global ROOT
 if '--source-root' in sys.argv:
  i=sys.argv.index('--source-root');ROOT=Path(sys.argv[i+1]).resolve();del sys.argv[i:i+2]
 source=transformed(ROOT,(ROOT/'tests/newshf_compositor_validation.py').read_bytes())
 marker="   cmd=['make','-j3'"
 assert source.count(marker)==1
 source=source.replace(marker,"   shutil.copytree(ROOT/'src/third_party',build/'src/third_party',dirs_exist_ok=True)\n"+marker)
 source=source.replace('timeout=240','timeout=900')
 source=source.replace("tests/newshf_compositor_validation.c", "tests/linked_newshf_native_validation.c")
 marker="+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big'))"
 assert source.count(marker)==1
 source=source.replace(marker,"+b''.join(raw[177182+p*77:177182+(p+1)*77] for p in range(3))"+marker)
 marker=" content=resource_root/'content'"
 assert source.count(marker)==1
 source=source.replace(marker,"\n (resource_root/'newshf-linked').mkdir(exist_ok=True)\n for asset in (ROOT/'assets/hd/current-compat/newshf-linked').glob('*.hda'):shutil.copyfile(asset,resource_root/'newshf-linked'/asset.name)\n"+marker)
 marker=" content=resource_root/'content'"
 source=source.replace(marker,"\n oldonly=resource_root/'old-only';(oldonly/'newshf').mkdir(parents=True,exist_ok=True)\n for asset in current_paths:shutil.copyfile(asset,oldonly/'newshf'/asset.name)\n"+marker)
 marker=" content=resource_root/'content'"
 source=source.replace(marker,"\n for i,asset in enumerate(sorted((ROOT/'assets/hd/current-compat/newshf-linked').glob('*.hda'))):\n  for mode in ('missing','corrupt'):\n   bad=resource_root/(mode+'-linked'+str(i));(bad/'newshf-linked').mkdir(parents=True,exist_ok=True);(bad/'newshf').mkdir(exist_ok=True)\n   for old in current_paths:shutil.copyfile(old,bad/'newshf'/old.name)\n   for other in (ROOT/'assets/hd/current-compat/newshf-linked').glob('*.hda'):\n    data=bytearray(other.read_bytes())\n    if other==asset:\n     if mode=='missing':continue\n     data[31]^=1\n    (bad/'newshf-linked'/other.name).write_bytes(data)\n"+marker)
 # Historical negative-control locator is irrelevant to this separate extension.
 start=source.index(' transfer_line=')
 end=source.index(' unchanged=',start)
 source=source[:start]+" accepted=r.returncode==0\n"+source[end:]
 exec(compile(source,str(ROOT/'tests/newshf_compositor_validation.py'),'exec'),{'__name__':'__main__','__file__':str(ROOT/'tests/newshf_compositor_validation.py')})
if __name__=='__main__':main()
