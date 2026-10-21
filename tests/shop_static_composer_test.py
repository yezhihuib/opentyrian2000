#!/usr/bin/env python3
"""Isolated canonical quad composer checks. Synthetic shop fixture is NOT native navigation evidence.
Needs original game data and accepted startup resources.
Only authored resources are copied; original game data is read in memory.
"""
import argparse, hashlib, json, os, shlex, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for arg in ('data','startup','receipt'):p.add_argument('--'+arg,type=Path,required=True)
 p.add_argument('--sanitize',action='store_true');a=p.parse_args()
 paths=['src/'+x for x in ('shop_static_render.inc','shop_static_pins.h','pregame_font.c','shared_asset_reader.h','shared_asset_fd_reader.inc','pregame_font.h','sprite.c')]+['tests/shop_static_composer_test.c','tests/shop_static_composer_test.py']
 paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'assets/shop-static-v1').glob('*.hda'))]
 before={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in paths}
 with tempfile.TemporaryDirectory(prefix='shop-static-composer-') as t:
  tmp=Path(t);shutil.copytree(ROOT/'src',tmp/'src');shutil.copytree(ROOT/'tests',tmp/'tests');(tmp/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
  fixture=tmp/'tests/pregame_typography_reconstruction.c';fixture.write_text(fixture.read_text().replace('int main(int argc,char **argv)','int typography_main(int argc,char **argv)'))
  fixture.write_text(fixture.read_text().replace('shopSpriteSheet,1);snprintf','shopSpriteSheet,test_quad);if(test_occlude)fill_rectangle_xy(VGAScreen,160,y-4,183,y+23,0);snprintf'))
  shutil.copytree(a.startup,tmp/'startup')
  for path in (ROOT/'assets/shop-static-v1').glob('*.hda'):shutil.copyfile(path,tmp/'startup'/path.name)
  shutil.copytree(tmp/'startup',tmp/'bad-root')
  sources='src/hd_cursor.c tests/shop_static_composer_test.c src/common_menu_runs.c src/selector_font_output.c src/settings_font.c src/load_font.c src/selector_font.c src/helptext.c tests/load_font_globals.c src/font.c src/sprite.c src/data_text.c src/fonthand.c src/nortvars.c src/vga256d.c src/video_scale.c src/video_scale_hqNx.c'.split()
  cmd=shlex.split(os.environ.get('CC','cc'))+['-std=c99','-O0' if a.sanitize else '-O1','-g','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Isrc']
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  cmd+=shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True))+sources+['-Wl,--gc-sections']+shlex.split(subprocess.check_output(['pkg-config','--libs','sdl2'],text=True))+['-lm','-o','test']
  subprocess.run(cmd,cwd=tmp,check=True,timeout=120)
  result=subprocess.run([str(tmp/'test'),str(a.data.resolve()),str(tmp/'startup')],cwd=tmp,capture_output=True,text=True,timeout=120,env={**os.environ,'SDL_VIDEODRIVER':'dummy','ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
 unchanged=all(hashlib.sha256((ROOT/s).read_bytes()).hexdigest()==h for s,h in before.items())
 report={'status':'PASS' if result.returncode==0 and unchanged else 'FAIL','scope':__doc__,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'sanitizers':'ASan+UBSan; LSan disabled' if a.sanitize else 'none','source_sha256':before,'sources_unchanged':unchanged,'original_bytes_persisted':False}
 a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2)+'\n');print(result.stdout+result.stderr,end='');raise SystemExit(0 if report['status']=='PASS' else 1)
if __name__=='__main__':main()
