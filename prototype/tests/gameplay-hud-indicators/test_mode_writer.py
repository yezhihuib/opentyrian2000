#!/usr/bin/env python3
"""Execute the unchanged original paired MODE writer with a scalar blit oracle."""
from pathlib import Path
import argparse,os,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'gameplay-hud'));from test_writers import extract,normalized

def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');a=p.parse_args()
 source=(ROOT/'src/mainint.c').read_text();body=extract(source,'JE_drawPortConfigButtons')
 baseline=subprocess.check_output(['git','show','dc1a2cf3e175e5e28f6c9f67df6ff614aa1c5c74:src/mainint.c'],cwd=ROOT,text=True)
 event='render_mirror_hud_mode_drawn(VGAScreenSeg, player[0].weapon_mode);'
 assert body.count(event)==1 and body.index(event)>body.rindex('blit_sprite(')
 assert normalized(body.replace(event,''))==normalized(extract(baseline,'JE_drawPortConfigButtons'))
 assert source.count(event)==1
 with tempfile.TemporaryDirectory(prefix='hul-writer-') as d:
  d=Path(d);(d/'writer.inc').write_text(body)
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-I'+str(d),str(HERE/'test_mode_writer.c'),'-o',str(d/'test')]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  subprocess.run(cmd,check=True);subprocess.run([str(d/'test')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
 print('PASS original writer source is token-exact after removing the sole post-completion display notification')
if __name__=='__main__':main()
