#!/usr/bin/env python3
"""Isolated composer checks. Synthetic command arms are NOT native birth evidence.
Needs original game data, accepted startup resources and global resource root.
Only authored resources are copied; original game data is read in memory.
"""
import argparse, hashlib, json, os, re, shlex, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for arg in ('data','startup','global-root','receipt'):p.add_argument('--'+arg,type=Path,required=True)
 p.add_argument('--sanitize',action='store_true');a=p.parse_args()
 paths=['src/'+x for x in ('shop_vulcan.h','shop_vulcan_proof.inc','shop_vulcan_render.inc','pregame_font.c','pregame_font.h','shop_pulse.h','shop_pulse_proof.inc','shop_pulse_render.inc','shop_ship_render.inc','shop_static_render.inc','global_asset_registry.h','shared_asset_reader.h','shared_asset_fd_reader.inc','sprite.c','shots.c','game_menu.c','episodes.c','render_mirror.c')]+['visualc/opentyrian.vcxproj','tests/shop_vulcan_composer_test.c','tests/shop_vulcan_composer_test.py','tests/pregame_font_test.c','tests/pregame_typography_reconstruction.c']
 before={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in paths}
 with tempfile.TemporaryDirectory(prefix='shop-vulcan-composer-') as t:
  tmp=Path(t);shutil.copytree(ROOT/'src',tmp/'src');shutil.copytree(ROOT/'tests',tmp/'tests');(tmp/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
  alloc_fixture=tmp/'tests/pregame_font_test.c';alloc_fixture.write_text(alloc_fixture.read_text().replace('allocations[16]','allocations[64]').replace('i<16','i<64').replace('i==16','i==64'))
  fixture=tmp/'tests/pregame_typography_reconstruction.c';fixture.write_text(fixture.read_text().replace('int main(int argc,char **argv)','int typography_main(int argc,char **argv)'))
  fixture.write_text(fixture.read_text().replace('shopSpriteSheet,1);snprintf','shopSpriteSheet,test_quad);snprintf'))
  registry=(ROOT/'src/global_asset_registry.h').read_text();(tmp/'bad-root/content').mkdir(parents=True)
  for identity in (80067,80070):
   path=re.search(r'\{'+str(identity)+r'u,[^\n]*?"([^"]+)"',registry)[1];shutil.copyfile(a.global_root.resolve()/path,tmp/'bad-root'/path)
  sources='src/hd_cursor.c tests/shop_vulcan_composer_test.c src/common_menu_runs.c src/selector_font_output.c src/settings_font.c src/load_font.c src/selector_font.c src/helptext.c tests/load_font_globals.c src/font.c src/sprite.c src/data_text.c src/fonthand.c src/nortvars.c src/vga256d.c src/video_scale.c src/video_scale_hqNx.c'.split()
  cmd=shlex.split(os.environ.get('CC','cc'))+['-std=c99','-O0' if a.sanitize else '-O1','-g','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Isrc']
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  cmd+=shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True))+sources+['-Wl,--gc-sections']+shlex.split(subprocess.check_output(['pkg-config','--libs','sdl2'],text=True))+['-lm','-o','test']
  subprocess.run(cmd,cwd=tmp,check=True,timeout=120)
  result=subprocess.run([str(tmp/'test'),str(a.data.resolve()),str(a.startup.resolve()),str(a.global_root.resolve())],cwd=tmp,capture_output=True,text=True,timeout=120,env={**os.environ,'SDL_VIDEODRIVER':'dummy','ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
 unchanged=all(hashlib.sha256((ROOT/s).read_bytes()).hexdigest()==h for s,h in before.items())
 report={'status':'PASS' if result.returncode==0 and unchanged else 'FAIL','scope':__doc__,'returncode':result.returncode,'compiler_command':cmd,'stdout':result.stdout,'stderr':result.stderr,'sanitizers':'ASan+UBSan; LSan disabled' if a.sanitize else 'none','source_sha256':before,'sources_unchanged':unchanged,'original_bytes_persisted':False}
 a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2)+'\n');print(result.stdout+result.stderr,end='');raise SystemExit(0 if report['status']=='PASS' else 1)
if __name__=='__main__':main()
