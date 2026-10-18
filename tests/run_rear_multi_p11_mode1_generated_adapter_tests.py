#!/usr/bin/env python3
"""Validate the reviewed generated role pack through the real adapter/wrapper.
Usage: SCRIPT /path/to/accepted-pack /path/to/synthetic-adapter-fixture /new/output
No game data is read. Prepare the synthetic fixture with the public adapter runner.
"""
from pathlib import Path
import hashlib,json,os,re,shutil,struct,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)!=4:raise SystemExit(__doc__)
pack,fixture,out=map(lambda s:Path(s).resolve(),sys.argv[1:])
out.mkdir(parents=True,exist_ok=False)
receipt=json.loads((fixture/'fixture_receipt.json').read_text())
assert receipt['generated_only'] is True and receipt['original_inputs'] is False
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fnv(raw):
 h=14695981039346656037
 for b in raw:h=((h^b)*1099511628211)&((1<<64)-1)
 return h
header=(ROOT/'src/rear_multi_p1_pins.h').read_text()
rgba_macro=re.search(r'^#define REAR_P1_RGBA_PINS .*$',header,re.M)[0]
rgba=[int(x,0) for x in re.findall(r'UINT64_C\((0x[0-9a-f]+|0)\)',rgba_macro)]
ids=[39,1,281,282,301,300,40,2,77,182,183,277,278,41,3,296,297,294,295,298,299,203,222,43,5]
assert len(rgba)==50 and all(rgba[-4:]),'New43/5 must be parent-reviewed and pinned before this test.'
assets=[]
for k,raw in enumerate(ids):
 for col,d in enumerate((4,8)):
  pin=rgba[2*k+col]
  if not pin:continue
  p=pack/f'rear-multicannon-p1-bank8-{raw}-{d}.hda';b=p.read_bytes()
  assert len(b)==28+168*d*d*4 and struct.unpack_from('<4s4I2i',b)==(b'HDR1',1310000+raw,d,12,14,0,0),p
  assert fnv(b[28:])==pin,p
  assets.append({'file':p.name,'sha256':sha(p),'rgba_fnv1a64':f'{pin:016x}'})
for name in ('types.inc','functions.inc','create.inc','create_baseline.inc','direction.inc','wrapper.inc','variants.inc','bank.bin','records.bin'):
 shutil.copyfile(fixture/name,out/name)
synthetic_header=(fixture/'fixture_pins.h').read_text().split('#ifdef REAR_P1_TEST_PENDING_ART')[0]
(out/'fixture_pins.h').write_text(synthetic_header+rgba_macro+'\n')
full=out/'full';full.mkdir()
for p in pack.glob('rear-multicannon-p1-bank8-*.hda'):shutil.copyfile(p,full/p.name)
# Independent whole-pack isolation, keeping every other role and both densities.
for d in (4,8):
 for phase,raw in enumerate((277,278,297,296,43,5),1):
  for kind in (0,1):
   dest=out/f'p11m1-isolation-{d}-{phase}-{kind}';dest.mkdir()
   for p in full.glob('*.hda'):
    selected=p.name==f'rear-multicannon-p1-bank8-{raw}-{d}.hda'
    if selected and kind==0:continue
    b=bytearray(p.read_bytes())
    if selected:b[-1]^=1
    (dest/p.name).write_bytes(b)
# All16 malformed-file families for the four new exact-density resources.
variants=[]
for raw in (43,5):
 for d in (4,8):
  name=f'rear-multicannon-p1-bank8-{raw}-{d}.hda';exact=(full/name).read_bytes()
  for kind in ('missing','empty','magic','key','density','w','h','ax','ay','short','trunc','extra','payload','fifo','directory','device'):
   dest=out/f'new-{raw}-{d}-{kind}';dest.mkdir();b=bytearray(exact)
   if kind=='empty':b=bytearray()
   if kind=='magic':b[0]^=1
   if kind in ('key','density','w','h','ax','ay'):b[{'key':4,'density':8,'w':12,'h':16,'ax':20,'ay':24}[kind]]^=1
   if kind=='short':b=b[:27]
   if kind=='trunc':b=b[:-1]
   if kind=='extra':b+=b'\0'
   if kind=='payload':b[-1]^=1
   if kind=='fifo':os.mkfifo(dest/name)
   elif kind=='directory':(dest/name).mkdir()
   elif kind=='device':(dest/name).symlink_to('/dev/null')
   elif kind!='missing':(dest/name).write_bytes(b)
   other=8 if d==4 else 4;othername=f'rear-multicannon-p1-bank8-{raw}-{other}.hda';shutil.copyfile(full/othername,dest/othername)
   variants.append((dest.name,25+(raw==5),d))
(out/'generated_variants.inc').write_text('static const struct {const char *name;unsigned member;int density;} generated_variants[]={'+','.join('{"%s",%d,%d}'%v for v in variants)+'};\n')
source='''#define main complete_suite_main
#include "HARNESS"
#undef main
#include "generated_variants.inc"
int main(int argc,char **argv){
 CHECK(argc==2);snprintf(work,sizeof work,"%s",argv[1]);snprintf(full,sizeof full,"%s/full",work);snprintf(path,sizeof path,"%s/bank.bin",work);FILE*f=fopen(path,"rb");CHECK(f);banksize=fread(originalbank,1,sizeof originalbank,f);CHECK(banksize>602&&banksize<sizeof originalbank);fclose(f);snprintf(path,sizeof path,"%s/records.bin",work);f=fopen(path,"rb");CHECK(f);CHECK(fread(recordbytes,1,1760,f)==1760);fclose(f);
 test_p11_mode1_actual_allocations();test_p11_mode1_adapter_protocol();test_p11_mode1_resources();test_p11_mode1_linked_negatives();test_p11_mode1_coexistence();test_p11_mode1_tail_boundary();
 for(int d=4;d<=8;d+=4)for(unsigned phase=1;phase<=6;phase++)for(unsigned kind=0;kind<2;kind++){snprintf(path,sizeof path,"%s/p11m1-isolation-%d-%u-%u",work,d,phase,kind);p11m1_resource_isolation(path,d,phase,kind);}
 for(unsigned i=0;i<sizeof generated_variants/sizeof *generated_variants;i++){
  unsigned k=generated_variants[i].member;int d=generated_variants[i].density;snprintf(path,sizeof path,"%s/%s",work,generated_variants[i].name);defaults(d,path);test_power=18;emit(k,0);unsigned before=generics,opens=role_opens;PlayerShotDataType saved=playerShotData[0];Uint8 indexed[64000];memcpy(indexed,pixels,sizeof indexed);
  draw_player_shot_sprite2(&surface,101,100,spriteSheet8,ids[k],0,ids[k]);CHECK(!last_mirrored&&generics==before+1&&role_opens==opens+1&&!suppress);CHECK(!memcmp(indexed,pixels,sizeof indexed)&&!memcmp(&saved,&playerShotData[0],sizeof saved));CHECK(rear_p1_state.birth[0].qualified&&!checked_head(k,0));CHECK(!rear_p1_resources.cache[rear_p1_member(ids[k])][d!=8].attempted);
 }
 rear_p1_shutdown();printf("Reviewed generated P11 FIRST adapter PASS: %u checks,64 malformed new-role variants,24 whole-pack isolation cases\\n",checks);return 0;
}
'''.replace('HARNESS',str(ROOT/'tests/rear_multi_p1_adapter_test.c'))
(out/'generated_adapter.c').write_text(source)
results=[]
for mode in ('plain','sanitize'):
 exe=out/f'generated-{mode}';cmd=['cc','-std=c99','-Wall','-Wextra','-Werror','-pedantic','-O1','-g','-I'+str(ROOT/'src'),'-I'+str(out),str(out/'generated_adapter.c'),str(ROOT/'src/rear_multi_p1.c'),'-o',str(exe),'-lm']
 if mode=='sanitize':cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 subprocess.run(cmd,check=True)
 r=subprocess.run([str(exe),str(out)],text=True,capture_output=True,timeout=180,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1'})
 (out/f'{mode}.log').write_text(r.stdout+r.stderr);print(mode,r.stdout,end='');print(r.stderr,end='',file=sys.stderr);r.check_returncode();results.append(mode)
(out/'generated-pack-receipt.json').write_text(json.dumps({'status':'PASS','pack':str(pack),'generated_art_only':True,'synthetic_gameplay_inputs_only':True,'modes':results,'assets':assets,'new_role_malformed_variants':len(variants),'whole_pack_isolation_cases':24,'production_pins_sha256':sha(ROOT/'src/rear_multi_p1_pins.h')},indent=2)+'\n')
