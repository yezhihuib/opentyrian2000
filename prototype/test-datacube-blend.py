#!/usr/bin/env python3
"""Actual glyph/real compositor units. No game launch; prior make required."""
import argparse, hashlib, json, os, re, shlex, struct, subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--data',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args();root=Path(__file__).resolve().parents[1];out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
base='93008cc051b4b00c512dc9f8599849f6db1132e3'
def run(cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
 if r.returncode:raise RuntimeError(' '.join(map(str,cmd))+'\n'+r.stdout+r.stderr)
 return r.stdout+r.stderr
sha=lambda b:hashlib.sha256(b).hexdigest()
old=subprocess.check_output(['git','-C',root,'show',base+':src/render_mirror.c']).decode()
new=(root/'src/render_mirror.c').read_text()
addition=' /* The original Data pickup is fixed sprite266 with a warm0x70 glyph,\n  * unlike the blue/gray cash values. Keep it under the same source/Talon/\n  * monotone-ramp checks instead of restoring the connected HD scene. */\n bool data=index==266&&hue==0x70;\n'
assert new.count(addition)==1
assert new.replace(addition,'').replace('||(value&&(hue==0x80||hue==0x90))||data;', '||(value&&(hue==0x80||hue==0x90));')==old
changed=run(['git','-C',root,'diff',base,'--name-only','--','src','assets']).splitlines()
assert changed==['src/render_mirror.c'],changed
(out/'baseline-render-mirror.c').write_text(old)
cc=shlex.split(os.environ.get('CC','cc'));flags=shlex.split(run(['pkg-config','--cflags','sdl2','SDL2_net']));libs=shlex.split(run(['pkg-config','--libs','sdl2','SDL2_net']))+['-lm']
common=cc+['-std=c99','-DTARGET_UNIX','-DWITH_NETWORK','-DNDEBUG','-O1','-g','-I'+str(root/'src')]+flags
run(common+['-Dmain=unused_original_main','-c',root/'src/opentyr.c','-o',out/'opentyr.o'])
objects=[str(f) for f in sorted((root/'obj').glob('*.o')) if f.stem not in ('opentyr','render_mirror')]+[str(out/'opentyr.o')]
results=[]
for kind,source in [('baseline',out/'baseline-render-mirror.c'),('candidate',root/'src/render_mirror.c')]:
 run(common+['-DMIRROR_SOURCE="'+str(source)+'"',root/'prototype/test-datacube-blend.c']+objects+libs+['-o',out/kind])
 for density in (4,8):
  text=run([out/kind,a.data/'newsh6.shp',a.data/'palette.dat',density,int(kind=='baseline')]);(out/f'{kind}-{density}.log').write_text(text);results.append(text.strip());print(text,end='')
before=run([out/'baseline','--predicate']);after=run([out/'candidate','--predicate'])
assert len(before)==len(after)==400*256
delta=[(i//256,i%256,a,b)for i,(a,b)in enumerate(zip(before,after))if a!=b]
assert delta==[(266,0x70,'0','1')],delta
bank=(a.data/'newsh6.shp').read_bytes();pos=struct.unpack_from('<H',bank,265*2)[0];start=pos;values=[]
while bank[pos]!=15:
 count=bank[pos]>>4;pos+=1;values.extend(bank[pos:pos+count]);pos+=count
assert len(values)==85 and set(v&240 for v in values)=={0x70}
report={'status':'PASS','baseline':base,'results':results,'predicate_combinations':400*256,'only_changed_predicate':delta,'original_glyph266':{'opaque_pixels':len(values),'hues':[0x70],'record_sha256':sha(bank[start:pos+1])},'only_production_edit':'src/render_mirror.c exact266/0x70 predicate','baseline_mirror_sha256':sha(old.encode()),'candidate_mirror_sha256':sha(new.encode()),'data_sha256':{f:sha((a.data/f).read_bytes())for f in ['newsh6.shp','palette.dat']},'qualification':'Real renderer and original indexed sprite decoder; actual source glyph, synthetic connected HD underlay/ship ownership. No engine main, no natural gameplay or Windows claim.'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
