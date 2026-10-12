#!/usr/bin/env python3
"""Reproduce the selected generated-only sand21 refresh in a new external directory."""
from pathlib import Path
from PIL import Image
import sys,json,subprocess,tempfile,hashlib,struct
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;S=P/'source'
def call(*a):subprocess.run([str(x) for x in a],check=True,stdout=subprocess.DEVNULL)
def rgba(p):return Image.open(p).convert('RGBA').tobytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def main(out):
 rawout=out.absolute()
 if rawout.exists() or rawout.is_symlink():raise ValueError('Output must be a NEW external directory, not any existing path or symlink')
 out=rawout.resolve()
 if out==P or P in out.parents or out in P.parents:raise ValueError('Output cannot overlap the immutable source package')
 out.mkdir(parents=True)
 E=json.loads((P/'expected-output.json').read_text());H=json.loads((P/'headers.json').read_text());C=json.loads((P/'contracts/road-curves.json').read_text());G=json.loads((P/'contracts/grass-pure-sand-masks.rle.json').read_text())
 # Independent frozen source-weight proof; creates no artwork or files.
 call(sys.executable,S/'grass-mask-proof/derive_masks.py')
 with tempfile.TemporaryDirectory(prefix='tyrian-sand21-') as td:
  t=Path(td)
  call('convert',S/'new-sand/generated-matte-sand-master.png','-resize','192x224!','-alpha','on','-strip','PNG32:'+str(t/'registered.png'))
  assert rgba(t/'registered.png')==rgba(S/'new-sand/registered-raw.png')
  call('/usr/bin/python3',S/'new-sand/periodize_fill.py',t/'registered.png',t/'periodic.png')
  assert rgba(t/'periodic.png')==rgba(S/'new-sand/periodic-before-palette.png')
  call('convert',t/'periodic.png','-channel','R','-evaluate','Subtract','3.62269%','-channel','G','-evaluate','Subtract','3.16461%','+channel','-alpha','on','-strip','PNG32:'+str(t/'new47.png'))
  new47=rgba(t/'new47.png');assert new47==rgba(S/'new-sand/terrain-shapesz-47-8.png');(t/'new47.rgba').write_bytes(new47)
  for k in ['road','grass']:call('c++','-O2','-std=c++17',S/'cpp'/f'compose_{k}_sand.cpp','-o',t/k)
  receipt={}
  for name,expected in E.items():
   i=int(name.split('-')[2]);old=rgba(S/'accepted'/(name+'.png'));assert sha(old)==expected['baseline_rgba_sha256'];(t/'old.rgba').write_bytes(old)
   if str(i) in C['curves']:
    curve=C['curves'][str(i)];(t/'curve').write_text(f"{curve['axis'][0]} {curve['side']} {C['feather_hd']} {len(curve['points'])}\n"+'\n'.join(f'{a} {b}' for a,b in curve['points']))
    call(t/'road',t/'old.rgba',t/'new47.rgba',t/'curve',t/'out.rgba',t/'weight',t/'road-receipt')
    assert (t/'weight').read_bytes()==Image.open(P/'contracts/road-weights'/f'sand-mask-{i}.png').convert('L').tobytes()
   else:
    z=G['tiles'][str(i)];mask=bytearray(192*224)
    for start,n in z['runs']:mask[start:start+n]=bytes([1])*n
    assert sha(mask)==z['sha256_u8'];(t/'mask').write_bytes(mask)
    call(t/'grass',t/'old.rgba',t/'new47.rgba',t/'mask',t/'out.rgba',t/'weight')
    assert (t/'weight').read_bytes()==Image.open(P/'contracts/grass-weights'/f'final-sand-weight-{i}.png').convert('L').tobytes()
   b=(t/'out.rgba').read_bytes();assert sha(b)==expected['rgba_sha256'],name
   im=Image.frombytes('RGBA',(192,224),b);assert im.getchannel('A').getextrema()==(255,255);im.save(out/(name+'.png'))
   blob=b'HDR1'+struct.pack('<6i',*H[name])+b;assert sha(blob)==expected['hda_sha256'];(out/(name+'.hda')).write_bytes(blob)
   receipt[name]={'rgba_sha256':sha(b),'hda_sha256':sha(blob),'png_sha256':sha((out/(name+'.png')).read_bytes()),'changed':expected['changed']}
  (out/'rebuild-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({'status':'passed','exact_rgba_and_hda':len(E),'changed':sum(e['changed'] for e in E.values()),'output':str(out)}))
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: rebuild.py NEW_OUTPUT_DIRECTORY_OUTSIDE_PACKAGE')
 main(Path(sys.argv[1]))
