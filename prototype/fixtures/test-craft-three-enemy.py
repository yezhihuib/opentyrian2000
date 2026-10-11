from pathlib import Path
import argparse,re,struct,subprocess,tempfile,os,json,hashlib,time,zipfile,io,shutil
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=HERE.parents[1]/'src/render_mirror.c');p.add_argument('--sanitize',action='store_true');p.add_argument('--assets',type=Path,default=HERE.parents[1]/'assets/hd/packs/packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test');p.add_argument('--runtime-zip',type=Path,help='optional approved calibrated PNG zip; verifies exact PNG-to-HDA pixel transport');p.add_argument('--output',type=Path,help='report directory; defaults to a new temporary directory outside the checkout');a=p.parse_args();output=a.output or Path(tempfile.mkdtemp(prefix='craft-three-review-result-'));output.mkdir(parents=True,exist_ok=True);source_bytes=a.source.read_bytes();s=source_bytes.decode();start_time=time.monotonic()
def extract(name):
 m=re.search(r'^[^\n;]*\b'+name+r'\([^\n;]*\)\s*\{',s,re.M);assert m,name
 begin=s.index('{',m.start());end=begin+1;depth=1
 while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[m.start():end]+'\n'
def pixels(base,d):
 alpha=[0,1,127,128,254,255];return bytes(v for y in range(28*d) for x in range(24*d) for v in [(base*7+x*3+y)%256,(base*11+x+y*5)%256,(base*13+x*7+y*2)%256,alpha[(x+2*y+base)%6]])
def raw(base,d):return struct.pack('<4s6I',b'HDR1',1010000+base,d,24,28,6,7)+pixels(base,d)
with tempfile.TemporaryDirectory(prefix='craft-three-unit-') as temp:
 t=Path(temp);packs=t/'packs';packs.mkdir()
 ids=[267,269,271];old_ids=[77,79,115,117,85,87,123,125,191,193,195,197,199,201,203,205,229,231,233,235,237,239,241,243,81,83,119,121,153,155,157]
 for name,d,bases in [('full8',8,ids),('full4',4,ids),('all-bindings',8,old_ids+ids)]:
  out=packs/name;out.mkdir()
  for base in bases:(out/f'enemy-newsh2-{base}-{d}.hda').write_bytes(raw(base,d))
 (packs/'empty').mkdir()
 for invalid_id in ids:
  for bad in range(-1,10):
   out=packs/f'invalid-{invalid_id}-{bad}';out.mkdir()
   for base in ids:
    if base==invalid_id and bad==-1:continue
    b=bytearray(raw(base,8))
    if base==invalid_id:
     if 0<=bad<6:struct.pack_into('<I',b,4+4*bad,struct.unpack_from('<I',b,4+4*bad)[0]+1)
     if bad==6:b[:4]=b'BAD1'
     if bad==7:b=b[:28]
     if bad==8:b=b[:-7]
     if bad==9:b+=b'X'
    (out/f'enemy-newsh2-{base}-8.hda').write_bytes(b)
 (packs/'actual8').mkdir();asset_report=[];approved=None
 if a.runtime_zip:
  assert hashlib.sha256(a.runtime_zip.read_bytes()).hexdigest()=='054a16d53c0d9c69a844c6c5a4ad15e400e39ba184256a21153ff56364177d47'
  from PIL import Image
  approved=zipfile.ZipFile(a.runtime_zip)
 for base in ids:
  path=a.assets/f'enemy-newsh2-{base}-8.hda';b=path.read_bytes();assert len(b)==172060 and struct.unpack_from('<4s6I',b)==(b'HDR1',1010000+base,8,24,28,6,7)
  png_hash=None
  if approved:
   png=approved.read(f'frames8x/newsh2-base-{base}-192x224.png');im=Image.open(io.BytesIO(png)).convert('RGBA');assert im.size==(192,224) and im.tobytes()==b[28:];png_hash=hashlib.sha256(png).hexdigest()
  (packs/'actual8'/path.name).write_bytes(b);(packs/f'actual-{base}.rgba').write_bytes(b[28:]);asset_report.append({'id':base,'hda_sha256':hashlib.sha256(b).hexdigest(),'rgba_sha256':hashlib.sha256(b[28:]).hexdigest(),'approved_png_sha256':png_hash,'approved_PNG_to_HDA_exact':bool(approved)})
 if approved:approved.close()
 patterns=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{ Asset \*asset; int x,y; \} GreenHead;',r'typedef struct \{ Uint16 peak\[16\]\[14\]; \} GreenBackground;',r'typedef struct \{ SDL_Rect rect; int bank,index,style; bool live; \} HdRegion;',r'static Asset assets\[\d+\];']
 (t/'types.inc').write_text('\n'.join(re.search(q,s,re.S).group() for q in patterns))
 names=['palette_rgb','complete_turret_group','restore_classic_rect','blend_rgba','cloud_asset','darken_rgba','read_asset','explosion_asset_slot','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','scene_asset','render_mirror_enemy_tile','render_mirror_entity_end']
 (t/'functions.inc').write_text('\n'.join(extract(n) for n in names));(t/'test.c').write_bytes(Path(__file__).with_suffix('.c').read_bytes());exe=t/'test';cmd=['cc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror']
 if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 build=subprocess.run(cmd+[str(t/'test.c'),'-o',str(exe)],capture_output=True,text=True);(output/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
 env=dict(os.environ);env['ASAN_OPTIONS']='detect_leaks=0:halt_on_error=1';env['UBSAN_OPTIONS']='halt_on_error=1:print_stacktrace=1'
 run=subprocess.run([str(exe),str(packs)],capture_output=True,text=True,env=env);(output/'result.log').write_text(run.stdout+run.stderr);print(run.stdout+run.stderr);report={'source':str(a.source),'source_sha256':hashlib.sha256(source_bytes).hexdigest(),'source_stable_during_test':source_bytes==a.source.read_bytes(),'sanitize':a.sanitize,'leak_sanitizer':'disabled under ptrace','exit_code':run.returncode,'elapsed_seconds':time.monotonic()-start_time,'stdout':run.stdout,'stderr':run.stderr,'assets':asset_report,'approved_runtime_zip_sha256':hashlib.sha256(a.runtime_zip.read_bytes()).hexdigest() if a.runtime_zip else None,'scope':'Extracted actual source functions, synthetic HDA/header cases and actual calibrated assets; no source edits or gameplay execution/captures.'};(output/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('Report:',output/'result.json');assert run.returncode==0
