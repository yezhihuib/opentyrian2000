"""Rebuild original authored set, then apply approved imagegen-derived narrow fringe."""
from pathlib import Path
from PIL import Image
import tempfile,subprocess,hashlib,json
from export_base import export as export_base
P=Path(__file__).resolve().parent
def export(out):
 export_base(out)
 with tempfile.TemporaryDirectory() as t:
  t=Path(t);exe=t/'apply'
  subprocess.run(['g++','-std=c++17','-O2',str(P/'fringe-source/apply_fringe_strip.cpp'),'-o',str(exe)],check=True)
  for k in [273,275,277]:
   target=out/f'newsh2-base{k}-8.png';im=Image.open(target).convert('RGBA');strip=Image.open(P/f'fringe-source/generated-fringe-actor-{k}.png').convert('RGBA')
   (t/'old.rgba').write_bytes(im.tobytes());(t/'strip.rgba').write_bytes(strip.tobytes())
   subprocess.run([str(exe),str(t/'old.rgba'),str(t/'strip.rgba'),str(t/'new.rgba')],check=True)
   Image.frombytes('RGBA',im.size,(t/'new.rgba').read_bytes()).save(target)
 return {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(out.glob('*.png'))}
if __name__=='__main__':print(json.dumps(export(P/'frames8x'),indent=2))
