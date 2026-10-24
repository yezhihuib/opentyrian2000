#!/usr/bin/env python3
"""Native production-object enemy reuse renderer test; not game-loop acceptance.
Private original data is verified then transferred on stdin, never persisted.
"""
import argparse, hashlib, json, os, resource, shutil, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHA=lambda b:hashlib.sha256(b).hexdigest()
FRAMES=(105,106,124,125,20,21)
HDA_SHA=('d12fde24b67f6b57ede3483e07a155b95cd5f538cf9f96c64e0d80fc2e0eba78','1a47b5701ecbdef673251cd1de7b975e42291cef29ab9a0bfd10f1c48facb2ba','b37e9664609365b53a250c0a711b6ae863ab55299904794051091b206aeef158','11ffdf82296ed985ec9534ba19a555eb22594c14e5fc92414531a47e36383752','328f9831389399fa7c8d623889732bbc1574dac458a30b97511e2d031dd7aed8','a8fbcb2952ec4a4b3f84388f1b410ec70648052cbaff35487d2ed930c9b5dc55')
def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ('original-data','sysroot','base-build','assets','out'):p.add_argument('--'+key,type=Path,required=True)
 p.add_argument('--negative-control',choices=('bank-pin','rgb-store'))
 a=p.parse_args();a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=True)
 for key in ('original_data','sysroot','base_build','assets'):setattr(a,key,getattr(a,key).resolve())
 assert shutil.disk_usage(a.out).free>5*1024**3
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu'),'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
 cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 flags=['-std=c99','-O0','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DENEMY_REUSE_HD_PROTOTYPE=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(ROOT/'src')]
 sanitized=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 # Reuse immutable unchanged baseline objects only; compile every modified TU.
 rebuild={'sprite','tyrian2','entity_draw','enemy_reuse_identity'}
 # Rebuild every changed/new production unit; reuse only source-identical objects.
 rebuild.update(p.stem for p in (ROOT/'src').glob('*.c') if p.stem not in {'render_mirror','opentyr'} and (not (a.base_build/'src'/p.name).exists() or (a.base_build/'src'/p.name).read_bytes()!=p.read_bytes()))
 objects=[str(x) for x in sorted((a.base_build/'obj').glob('*.o')) if x.stem not in rebuild|{'render_mirror','opentyr'}]
 for obj in objects:
  source=Path(obj).stem+'.c';assert (a.base_build/'src'/source).read_bytes()==(ROOT/'src'/source).read_bytes(), 'Cannot reuse modified production unit '+source
 log=[]
 def run(cmd):
  r=subprocess.run(cmd,env=env,capture_output=True,text=True);log.append(' '.join(cmd)+'\n'+r.stdout+r.stderr);(a.out/'compile.log').write_text('\n'.join(log));
  if r.returncode:raise RuntimeError(r.stderr)
 for unit in sorted(rebuild):
  target=a.out/(unit+'.o');source=ROOT/'src'/(unit+'.c');signature=SHA(source.read_bytes()+b''.join(h.read_bytes() for h in sorted(list((ROOT/'src').glob('*.h'))+list((ROOT/'src').glob('*.inc')))));pin=a.out/(unit+'.build-pin')
  if not target.exists() or not pin.exists() or pin.read_text()!=signature:
   run(['cc',*flags,*sanitized,'-c',str(source),'-o',str(target)]);pin.write_text(signature)
  objects.append(str(target))
 target=a.out/'opentyr.o';run(['cc',*flags,'-Dmain=enemy_reuse_unused_game_main','-c',str(ROOT/'src/opentyr.c'),'-o',str(target)]);objects.append(str(target))
 if a.negative_control:
  mutant=a.out/'mutant';mutant.mkdir(exist_ok=True);code=(ROOT/'src/render_mirror.c').read_text()
  if a.negative_control=='bank-pin':
   inc=(ROOT/'src/enemy_reuse_mirror.inc').read_text();guard='&&enemy_reuse_hash(bank.data,bank.size)==UINT64_C(0x2b63027f74aaa21e)';assert inc.count(guard)==1;(mutant/'enemy_reuse_mirror.inc').write_text(inc.replace(guard,''))
  else:
   store='else *p=blend_rgba(*p,src,talon_blend?(src[3]+1)/2:src[3]);';assert code.count(store)==1;code=code.replace(store,'else *p=*p; /* deliberate compositor-store mutation */')
  (mutant/'render_mirror.c').write_text(code);flags.insert(0,'-I'+str(mutant))
 run(['cc',*flags,*sanitized,'-no-pie',str(ROOT/'tests/enemy_reuse_validation.c'),*objects,*libs,'-lm','-o',str(a.out/'test')])
 raw=(a.original_data/'tyrian.hdt').read_bytes();assert SHA(raw)=='fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b'
 shape=(a.original_data/'tyrian.shp').read_bytes();offsets=struct.unpack_from('<13I',shape,2);bank=shape[offsets[7]:offsets[8]]
 assert len(bank)==32060 and SHA(bank)=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
 pal=(a.original_data/'palette.dat').read_bytes();assert SHA(pal)=='f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0';rgb=bytes((v<<2)|(v>>4) for v in pal[5*768:6*768])
 payload=bank+b''.join(raw[o:o+77] for o in (206365,182495))+b''.join(raw[o:o+80] for o in (27268,32628))+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big')) for n in range(0,768,3))
 payload+=(a.original_data/'newshs.shp').read_bytes()+(a.original_data/'newshc.shp').read_bytes()
 fixture=a.out/'fixture';fixture.mkdir(exist_ok=True)
 for frame,pin in zip(FRAMES,HDA_SHA):
  source=a.assets/f'bullet-{frame}-8.hda';assert SHA(source.read_bytes())==pin
  dest=fixture/source.name
  if not dest.exists():dest.symlink_to(source)
 for i,frame in enumerate(FRAMES):
  for mode in ('missing','corrupt','header','anchor','trailing','short'):
   root=fixture/(mode+str(i));root.mkdir(exist_ok=True)
   for f in FRAMES:
    source=a.assets/f'bullet-{f}-8.hda';dest=root/source.name
    if dest.exists() or dest.is_symlink():dest.unlink()
    if f!=frame:dest.symlink_to(source)
    elif mode!='missing':
     b=bytearray(source.read_bytes())
     if mode=='corrupt':b[31]^=1
     if mode=='header':b[4]^=1
     if mode=='anchor':b[20]=1
     if mode=='trailing':b+=b'!'
     if mode=='short':b=b[:-1]
     dest.write_bytes(b)
 r=subprocess.run([str(a.out/'test'),str(fixture)],input=payload,env=env,cwd=a.out,capture_output=True,timeout=300,preexec_fn=no_core)
 (a.out/'harness.log').write_bytes(r.stdout+r.stderr);print((r.stdout+r.stderr).decode())
 accepted=r.returncode==0
 if a.negative_control:
  marker=b'draws==0' if a.negative_control=='bank-pin' else b'*pixel(output,dx-24*8,dy)==want'
  accepted=r.returncode!=0 and marker in r.stderr and b'AddressSanitizer' not in r.stderr and b'runtime error:' not in r.stderr
 report={'status':'PASS' if accepted else 'FAIL','negative_control':a.negative_control,'returncode':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode(),'scope':'Native SDL production renderer, allocation, wrapper, identity and sprite blits; not gameplay acceptance','sanitizers':'ASan+UBSan renderer/sprite/tyrian2/entity_draw/identity/harness; remaining baseline production objects native optimized','original_bytes_persisted':False,'harness_sha256':{n:SHA((ROOT/'tests'/n).read_bytes()) for n in ('enemy_reuse_validation.c','enemy_reuse_validation.py')},'production_source_sha256':{p.name:SHA(p.read_bytes()) for p in sorted((ROOT/'src').iterdir()) if p.is_file()},'reused_baseline_objects':{Path(p).name:SHA(Path(p).read_bytes()) for p in objects if '/obj/' in p},'free_disk_bytes':shutil.disk_usage(a.out).free}
 (a.out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(not accepted)
if __name__=='__main__':main()
