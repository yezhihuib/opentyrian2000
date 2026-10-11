from pathlib import Path
import argparse,re,struct,subprocess,tempfile,os,json,hashlib,time
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=HERE.parents[1]/'src/render_mirror.c');p.add_argument('--sanitize',action='store_true');p.add_argument('--output',type=Path,help='report directory; defaults to a new temporary directory outside the checkout');a=p.parse_args();output=a.output or Path(tempfile.mkdtemp(prefix='rotor-review-result-'));output.mkdir(parents=True,exist_ok=True);source_bytes=a.source.read_bytes();s=source_bytes.decode();start_time=time.monotonic()
def extract(name):
 m=re.search(r'^[^\n;]*\b'+name+r'\([^\n;]*\)\s*\{',s,re.M);assert m,name
 begin=s.index('{',m.start());end=begin+1;depth=1
 while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[m.start():end]+'\n'
def pixels(base,d):
 alpha=[0,1,127,128,254,255];return bytes(v for y in range(28*d) for x in range(24*d) for v in [(base*7+x*3+y)%256,(base*11+x+y*5)%256,(base*13+x*7+y*2)%256,alpha[(x+2*y+base)%6]])
def raw(base,d):return struct.pack('<4s6I',b'HDR1',1010000+base,d,24,28,6,7)+pixels(base,d)
with tempfile.TemporaryDirectory(prefix='rotor-unit-') as temp:
 t=Path(temp);packs=t/'packs';packs.mkdir()
 for name in ['full8','full4','missing235','bad-anchor','bad-role','bad-size','bad-density','truncated','extra','empty']:
  out=packs/name;out.mkdir()
  if name=='empty':continue
  d=4 if name=='full4' else 8
  for base in range(229,244,2):
   if name=='missing235' and base==235:continue
   b=bytearray(raw(base,d))
   if base==235:
    if name=='bad-anchor':struct.pack_into('<I',b,20,12)
    if name=='bad-role':struct.pack_into('<I',b,4,2010000+base)
    if name=='bad-size':struct.pack_into('<I',b,12,23)
    if name=='bad-density':struct.pack_into('<I',b,8,4)
    if name=='truncated':b=b[:-7]
    if name=='extra':b+=b'X'
   (out/f'enemy-newsh2-{base}-{d}.hda').write_bytes(b)
 patterns=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{ Asset \*asset; int x,y; \} GreenHead;',r'typedef struct \{ Uint16 peak\[16\]\[14\]; \} GreenBackground;',r'typedef struct \{ SDL_Rect rect; int bank,index,style; bool live; \} HdRegion;',r'static Asset assets\[\d+\];']
 (t/'types.inc').write_text('\n'.join(re.search(q,s,re.S).group() for q in patterns))
 names=['palette_rgb','complete_turret_group','restore_classic_rect','blend_rgba','cloud_shadow_rgba','cloud_asset','darken_rgba','brightness_rgba','read_asset','explosion_asset_slot','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','scene_asset','render_mirror_enemy_tile','render_mirror_entity_end']
 (t/'functions.inc').write_text('\n'.join(extract(n) for n in names));(t/'test.c').write_bytes(Path(__file__).with_suffix('.c').read_bytes());exe=t/'test';cmd=['cc','-std=c99','-O1','-g','-Wall','-Wextra']
 if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 build=subprocess.run(cmd+[str(t/'test.c'),'-o',str(exe)],capture_output=True,text=True);(output/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
 env=dict(os.environ);env['ASAN_OPTIONS']='detect_leaks=0:halt_on_error=1';env['UBSAN_OPTIONS']='halt_on_error=1:print_stacktrace=1'
 run=subprocess.run([str(exe),str(packs)],capture_output=True,text=True,env=env);(output/'result.log').write_text(run.stdout+run.stderr);print(run.stdout+run.stderr);report={'source':str(a.source),'source_sha256':hashlib.sha256(source_bytes).hexdigest(),'source_stable_during_test':source_bytes==a.source.read_bytes(),'sanitize':a.sanitize,'leak_sanitizer':'disabled under ptrace','exit_code':run.returncode,'elapsed_seconds':time.monotonic()-start_time,'stdout':run.stdout,'stderr':run.stderr,'scope':'Extracted actual source functions and synthetic HDA files; no source edits or gameplay execution/captures.'};(output/'result.json').write_text(json.dumps(report,indent=2)+'\n');print('Report:',output/'result.json');assert run.returncode==0
