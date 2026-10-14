#!/usr/bin/env python3
"""Small exact-source Vulcan creation/movement/cadence unit; never launches a game."""
import argparse,hashlib,importlib.util,json,os,re,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='ee2b90cfaf9f227ca394ecd01f2403e55dbf2ea0'
SHA=lambda b:hashlib.sha256(b).hexdigest()
DATA={'tyrian.hdt':'fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b','tyrian4.lvl':'6589b898094887925e7717c8663c4b8b5e4b76f3c89a7898ed9f4691c1f2cc16','tyrian5.lvl':'275b5aaf55caecee8dc95e26f7cf118a9ee265f095ce61945b9ece56a4523323'}
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original-data',type=Path,required=True);p.add_argument('--source-packet',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();O=a.out.resolve();assert not O.exists() and ROOT not in O.parents
files=['src/shots.c','src/shots.h','src/mainint.c','src/episodes.c','src/episodes.h','src/lvlmast.h']
s={n:(ROOT/n).read_bytes() for n in files}
for n,b in s.items():assert b==subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+n]),n
spec=importlib.util.spec_from_file_location('binding',ROOT/'prototype/test-vulcan-binding.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
packet_raw=a.source_packet.read_bytes();assert SHA(packet_raw)==m.PACKET_SHA;packet=json.loads(packet_raw)
O.mkdir();extracted={}
def write(name,raw):
 if isinstance(raw,str):raw=raw.encode()
 (O/name).write_bytes(raw);extracted[name]=SHA(raw)
for name in ['player_shot_create','player_shot_move_and_draw']:write(name+'.inc',m.extract(s['src/shots.c'].decode(),name))
for file,start,end,out in [('src/episodes.h','typedef struct\n{\n\tJE_word     drain;','} JE_WeaponType;','weapon_type.inc'),('src/episodes.h','typedef struct\n{\n\tchar    name[31];','} JE_WeaponPortType[PORT_NUM + 1];','port_type.inc'),('src/shots.h','typedef struct {','} PlayerShotDataType;','shot_type.inc')]:
 text=s[file].decode();b=text.index(start);e=text.index(end,b)+len(end);write(out,text[b:e]+'\n')
text=s['src/mainint.c'].decode();b=text.index('if (!(twoPlayerLinked && playerNum_ == 2))');e=text.index('{',b)+1;depth=1
while depth:depth+=(text[e]=='{')-(text[e]=='}');e+=1
write('cadence.inc',text[b:e]+'\n')
# Fresh original-byte decode using the unchanged loader schema; fixtures stay outside Git.
fmt={'u8':'B','s8':'b','u16':'H','s16':'h'};schema=[(name,fmt[code],int(n)) for code,name,n in re.findall(r'fread_(u8|s8|u16|s16)_die\(\s*&?weapons\[i\]\.(\w+),\s*(\d+),\s*f\)',s['src/episodes.c'].decode())]
bounds={k:int(v) for k,v in re.findall(r'#define\s+(\w+)\s+(\d+)',s['src/lvlmast.h'].decode())};tables=[];spans=[]
for filename,digest in DATA.items():
 raw=(a.original_data/filename).read_bytes();assert SHA(raw)==digest
 offset=struct.unpack_from('<i',raw)[0] if filename.endswith('.hdt') else struct.unpack_from('<i',raw,2+4*(struct.unpack_from('<H',raw)[0]-1))[0];pos=offset+14;rows=[]
 for rid in list(range(bounds['WEAP_END1']+1))+list(range(bounds['WEAP_START2'],bounds['WEAP_NUM']+1)):
  start=pos;rec={}
  for field,code,n in schema:
   v=list(struct.unpack_from('<'+str(n)+code,raw,pos));pos+=n*struct.calcsize(code);rec[field]=v[0] if n==1 else v
  if 221<=rid<=231:
   used={k:(v[:rec['max']] if isinstance(v,list) else v) for k,v in rec.items()};expected=dict(packet['family']['modes'][0]['powers'][rid-221]['record_used']);expected.pop('id');expected['shipblastfilter']=208 if filename=='tyrian.hdt' else 112;assert used==expected
   rows.append(rec);spans.append({'table':filename,'record':rid,'offset':start,'bytes':pos-start,'sha256':SHA(raw[start:pos])})
 port=pos+7*82;assert raw[port+31]==1 and list(struct.unpack_from('<11H',raw,port+32))==list(range(221,232)) and struct.unpack_from('<H',raw,port+80)[0]==20
 tables.append(rows)
def literal(v):return '{'+','.join(map(str,v))+'}' if isinstance(v,list) else str(v)
write('records.inc','static const JE_WeaponType fixture[3][11]={\n'+',\n'.join('{'+',\n'.join('{'+','.join('.'+k+'='+literal(v) for k,v in r.items())+'}' for r in rows)+'}' for rows in tables)+'};\n')
common=[os.environ.get('CC','cc'),'-std=c99','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I'+str(O),str(Path(__file__).with_suffix('.c'))];results={}
for label,flags in [('optimized',['-O2']),('sanitized',['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
 cmd=common+flags+['-o',str(O/label)];r=subprocess.run(cmd,capture_output=True,text=True);(O/(label+'-compile.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');r=subprocess.run([str(O/label)],capture_output=True,text=True,env=env,timeout=120);(O/(label+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr;results[label]=json.loads(r.stdout);print(label+': '+r.stdout)
assert results['optimized']==results['sanitized']
for n,b in s.items():assert (ROOT/n).read_bytes()==b
report={'status':'PASS','baseline':BASE,'game_runs':0,'source_sha256':{n:SHA(b) for n,b in s.items()},'original_data_sha256':DATA,'source_packet_sha256':SHA(packet_raw),'extracted_sha256':extracted,'record_spans':spans,'results':results,'limitations':['Exact production functions and main-weapon cadence block, isolated caller-owned fields and read-only draw/probe observers.','Power and shot pools reset by the unit to cover phases; no live-game power, encounter, acquisition or runtime claim.','All 11 powers in three table groups; runtime remains a separate four-case P1/P7 gate.'],'harness_sha256':{q.name:SHA(q.read_bytes()) for q in [Path(__file__),Path(__file__).with_suffix('.c')]}}
(O/'result.json').write_text(json.dumps(report,indent=2)+'\n')
