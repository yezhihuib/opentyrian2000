#!/usr/bin/env python3
"""Fresh actual SDL software presenter captures from synthetic SHOP fixture.
Requires existing run_shop_current_acceptance.sh output; no game loop, historical
screenshots, Windows or GPU acceptance. Writes only to requested output directory.
"""
import argparse,os,shlex,subprocess,json,hashlib
from pathlib import Path
from shop_current_runtime_mutations import SOURCES,limits,build_limits
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('data',type=Path);p.add_argument('output',type=Path);a=p.parse_args();o=a.output.resolve();(o/'captures').mkdir(exist_ok=True)
 assert (o/'shop_current_fixture.inc').is_file(),'Run the current acceptance preparation first'
 cmd=shlex.split(os.environ.get('CC','cc'))+['-std=c99','-O1','-g','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',*shlex.split(os.environ['SDL_CFLAGS']),'-Isrc','-I'+str(o),'tests/shop_current_capture.c',*SOURCES,'-Wl,--gc-sections',*shlex.split(os.environ['SDL_LIBS']),'-lm','-o',str(o/'capture')]
 with (o/'capture-build.log').open('w') as log:subprocess.run(cmd,cwd=R,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=180,preexec_fn=build_limits)
 args=[str(o/'capture'),str(a.data.resolve()),*[str(o/'resources'/x) for x in ('fonts','metal','talon','front','generator','menu')],str(o/'captures')]
 with (o/'capture.log').open('w') as log:subprocess.run(args,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=180,env={**os.environ,'SDL_VIDEODRIVER':'dummy'},preexec_fn=limits)
 with (o/'capture-inspect.log').open('w') as log:subprocess.run(['python3',str(R/'tests/shop_current_capture_inspect.py'),str(o)],check=True,stdout=log,stderr=subprocess.STDOUT,timeout=60)
 receipt={'status':'PASS','scope':__doc__,'dimensions':[[640,400],[1280,800],[913,599]],'root_variants':['fonts','metal','talon','front','generator','current RFR3 menu'],'product_categories':list(range(2,9)),'source_sha256':{str(x.relative_to(R)):hashlib.sha256(x.read_bytes()).hexdigest() for x in (R/'tests/shop_current_capture.c',R/'tests/shop_current_capture_inspect.py',Path(__file__))}}
 (o/'capture-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
