from pathlib import Path
import subprocess,os,json,hashlib
from PIL import Image
q=Path(__file__).resolve().parent;b=q.parent;out=q/'native1280-correct-config';out.mkdir(exist_ok=False)
cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text('section video\nitem scaler 4x\nitem fullscreen -1\n')
exe=b/'linked171-native-final/hd-on-build/opentyrian2000';pack=q/'pack'
env=os.environ.copy();env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software',LD_LIBRARY_PATH=str(b/'dependencies/sysroot/usr/lib/x86_64-linux-gnu'),HOME=str(out),XDG_CONFIG_HOME=str(out/'config'))
argv=[str(exe),f'--data={b}/dependencies/data','--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=1','--asset-debug-level=12','--asset-debug-tick=158','--asset-debug-running','--render-test=8','--render-ticks=160',f'--render-assets={pack}',f'--global-assets={pack}','--asset-debug-capture','--asset-debug-capture-start=158','--asset-debug-capture-count=2','--asset-debug-window-only']
with (out/'stdout.log').open('w') as f,(out/'stderr.log').open('w') as e:r=subprocess.run(argv,cwd=out,env=env,stdout=f,stderr=e,timeout=240)
assert r.returncode==0
captures=[]
for p in sorted(out.glob('*.bmp')):
 im=Image.open(p);assert im.size==(1280,800),im.size
 name='linked171-173-cold-native1280.png' if p.stem.endswith('0158') else 'linked171-173-firing-native1280.png'
 target=q/name;im.save(target);captures.append(dict(tick=int(p.stem.split('-')[-1]),file=str(target),pixels=list(im.size),sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
assert len(captures)==2
(out/'receipt.json').write_text(json.dumps(dict(binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),argv=argv,internal_density=8,scaler='4x',native_window_pixels=[1280,800],resized=False,captures=captures),indent=2)+'\n');print(json.dumps(captures,indent=2))
