#!/usr/bin/env python3
"""Differential current readers against frozen pre-refactor IO code, with injected IO faults.
No original game data required. The legacy fragments come from an immutable ancestor;
the runner verifies SHA256 and compiles them alongside the actual new helper.
"""
import argparse,hashlib,json,os,pathlib,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='76757030842b19397353152c6ea326f95ef50c33'
def extract(text,start,end):return text.split(start,1)[1].split(end,1)[0]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 paths=['src/global_talon_mirror.inc','src/shop_ship_render.inc','src/shop_pulse_render.inc'];old={x:subprocess.check_output(['git','show',f'{BASE}:{x}'],cwd=ROOT,text=True) for x in paths}
 g=extract(old[paths[0]],' FILE *f=fopen(path,"rb");','\nstatic bool global_talon_family_ready')
 g=' FILE *f=fopen(path,"rb");'+g
 g=g[:g.rfind('}')]
 ship=extract(old[paths[1]],' int fd=SF_OPEN(path);','\n}\nstatic bool shop_ship_valid')
 ship=' int fd=SF_OPEN(path);'+ship
 ship=ship.replace('if(fd<0)return;','if(fd<0)return NULL;').replace('if(ok){shop_ship.rgba=p;shop_ship.bank=spriteSheet9.data;shop_ship.bank_size=spriteSheet9.size;}else free(p);','if(!ok){free(p);return NULL;}return p;')
 pulse=extract(old[paths[2]],'  int fd=SF_OPEN(path);','\n }\n if(!shop_pulse_art.good)')
 pulse='  int fd=SF_OPEN(path);'+pulse
 pulse=pulse.replace('if(fd<0){shop_pulse_art.good=false;break;}','if(fd<0)return NULL;').replace('if(!ok){free(p);shop_pulse_art.good=false;break;}shop_pulse_art.rgba[i]=p;','if(!ok){free(p);return NULL;}return p;')
 legacy='''#define global_bytes_hash independent_hash
#define global_u32 old_u32
#define u32 old_u32
#define hash independent_hash
static Uint8 *legacy_stdio(const GlobalAssetResource *r){const char *path="mock";
'''+g+'''\n}
static Uint8 *legacy_ship(const GlobalAssetResource *r){const char *path="mock";Uint8 h[28],extra,*p=NULL;SF_STAT st;bool ok=false;
'''+ship+'''\n}
static Uint8 *legacy_projectile(const GlobalAssetResource *r){const char *path="mock";Uint8 h[28];SF_STAT st;
'''+pulse+'''\n}
#undef global_bytes_hash
#undef global_u32
#undef u32
#undef hash
'''
 selected=['src/shared_asset_reader.h','src/shared_asset_fd_reader.inc','src/global_asset_registry.h','src/global_talon_mirror.inc','src/shop_ship_render.inc','src/shop_pulse_render.inc','src/shop_vulcan_render.inc','tests/shared_asset_reader_test.c','tests/shared_asset_reader_test.py'];before={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in selected}
 (a.out/'shared_asset_reader_legacy.inc').write_text(legacy)
 exe=a.out/'differential'
 cmd=['cc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie','-I'+str(ROOT/'src'),'-I'+str(a.out.resolve()),str(ROOT/'tests/shared_asset_reader_test.c'),'-o',str(exe.resolve())]
 subprocess.run(cmd,check=True)
 r=subprocess.run([str(exe.resolve()),str(ROOT/'assets/hd/global-assets-v1')],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'},timeout=180)
 unchanged=all(hashlib.sha256((ROOT/x).read_bytes()).hexdigest()==h for x,h in before.items())
 report={'status':'PASS' if r.returncode==0 and unchanged else 'FAIL','baseline_commit':BASE,'baseline_sha256':{x:hashlib.sha256(v.encode()).hexdigest() for x,v in old.items()},'source_sha256':before,'unchanged_during_run':unchanged,'compile':cmd,'returncode':r.returncode,'output':r.stdout,'scope':'Actual shared helper IO differential, synthetic faults; no rendering authority or OS permission claims.'}
 (a.out/'review.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout,end='');r.check_returncode();assert unchanged
if __name__=='__main__':main()
