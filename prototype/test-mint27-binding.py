#!/usr/bin/env python3
"""Bounded Mint27 production-source/resource units. No game run or art painting."""
from pathlib import Path
import argparse,hashlib,json,os,re,struct,subprocess
ROOT=Path(__file__).resolve().parents[1];BASE='a7157ccac97494ecbe3b1d54ba03a9ef42646ffd';SHA=lambda b:hashlib.sha256(b).hexdigest()
def extract(s,n):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+n+r'\([^;{}]*\)\s*\{',s,re.M);assert m,n;e=s.index('{',m.start())+1;depth=1
 while depth:depth+=(s[e]=='{')-(s[e]=='}');e+=1
 return s[m.start():e]+'\n'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();assert not out.exists()and ROOT not in out.parents;out.mkdir(parents=True)
 rs=(ROOT/'src/render_mirror.c').read_text();original=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':src/render_mirror.c']).decode()
 helper=extract(rs,'mint27_source_matches');bind=''' /* Normal Mint-O-Ship: one static player head; alternate source stays original. */\n if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index==27) {\n  if(!mint27_source_matches(bank))return NULL;\n  slot=535;role=8;\n }\n''';shadow=''' /* Mint-O-Ship retains its original indexed shadow silhouette and origin. */\n if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index==27&&style==MIRROR_SHADOW)return false;\n'''
 comment='''/* Mint-O-Ship normal bank8/27: validate decoded source before every cold or\n * warm lookup, including reload into the same allocation. No source-pointer lease. */\n'''
 restored=rs
 for before,after in [('static Asset assets[536];','static Asset assets[535];'),(comment+helper+'\n',''),(bind,''),(shadow,'')]:assert restored.count(before)==1;restored=restored.replace(before,after)
 assert restored==original,'Unexpected renderer change'
 paths=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only',BASE,'--','src'],text=True).splitlines()
 for name in paths:
  if name=='src/render_mirror.c':continue
  assert (ROOT/name).read_bytes()==subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+name]),name
 funcs=['decode_tile','read_asset','explosion_asset_slot','mint27_source_matches','get_asset','render_mirror_entity'];f={n:extract(rs,n)for n in funcs}
 patterns=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',r'static Asset assets\[\d+\];',r'enum \{ ASSET_NEWSH2=.*?\};']
 (out/'types.inc').write_text('\n'.join(re.search(p,rs,re.S).group()for p in patterns))
 (out/'functions.inc').write_text('\n'.join(s[:s.index('{')].strip()+';'for s in f.values())+'\n'+''.join(f.values()))
 sp=(ROOT/'src/sprite.c').read_text();blits={n:extract(sp,n)for n in ['blit_sprite2','blit_sprite2_darken']};(out/'blitters.inc').write_text(''.join(blits.values()))
 bank=[]
 for fn in ['tyrian.shp','tyrianc.shp']:
  raw=(a.data/fn).read_bytes();count=struct.unpack_from('<H',raw)[0];pos=list(struct.unpack_from('<'+str(count)+'I',raw,2))+[len(raw)];b=raw[pos[7]:pos[8]];bank.append(b);(out/(fn+'.bank8')).write_bytes(b)
 work=out/'fixtures';work.mkdir();hda=(ROOT/'assets/hd/artwork/player-mint27-one-v1/output/bullet-27-8.hda').read_bytes();rows=[]
 def add(name,raw=None,valid=0,density=8,extra4=False):
  q=work/name;q.mkdir();rows.append((name,valid,density))
  if raw is not None:(q/'bullet-27-8.hda').write_bytes(raw)
  if extra4:
   rgba=hda[28:];small=b''.join(rgba[(y*2*96+x*2)*4:(y*2*96+x*2)*4+4]for y in range(56)for x in range(48));(q/'bullet-27-4.hda').write_bytes(struct.pack('<4s6I',b'HDR1',80027,4,12,14,0,0)+small)
 add('valid',hda,1);add('missing');add('only4',None,1,4,True);add('invalid8-valid4',b'bad',1,4,True)
 for name,off,value in [('role',4,1110027),('identity',4,80026),('density',8,4),('width',12,11),('height',16,13),('anchor-x',20,1),('anchor-y',24,1)]:
  r=bytearray(hda);struct.pack_into('<I',r,off,value);add(name,r)
 for name,r in [('magic',b'BAD!'+hda[4:]),('short-header',hda[:27]),('truncated',hda[:-1]),('extra',hda+b'X')]:add(name,r)
 (work/'variants.tsv').write_text(''.join(f'{n} {v} {d}\n'for n,v,d in rows));runs={};env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
 for name,flags in [('optimized',['-O2']),('sanitized',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
  cmd=['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',*flags,'-I'+str(out),str(Path(__file__).with_suffix('.c')),'-o',str(out/name)]
  r=subprocess.run(cmd,capture_output=True,text=True);(out/(name+'-compile.log')).write_text(r.stdout+r.stderr)
  if r.returncode:print(r.stderr)
  r.check_returncode();r=subprocess.run([str(out/name),str(out/'tyrian.shp.bank8'),str(out/'tyrianc.shp.bank8'),str(work)],capture_output=True,text=True,env=env,timeout=120);(out/(name+'.log')).write_text(r.stdout+r.stderr)
  if r.returncode:print(r.stdout+r.stderr)
  r.check_returncode();runs[name]=json.loads(r.stdout);print(name+': '+r.stdout.strip())
 report={'status':'PASS','baseline':BASE,'exact_source_inverse':True,'production_source_files_checked':len(paths),'only_production_file_changed':'src/render_mirror.c','asset_sha256':SHA(hda),'source_functions_sha256':{n:SHA(s.encode())for n,s in {**f,**blits}.items()},'bank8_sha256':list(map(SHA,bank)),'resource_variants':rows,'runs':runs,'game_runs':0,'limitations':['Focused extracted loader/source/hook and original RLE tests; head RGBA compositor is a metadata-checking stub.','Full engine native output and actual-play aesthetics require separate paired runtime.','LeakSanitizer disabled for ptrace executor; ASan/UBSan enabled.']}
 (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
