#!/usr/bin/env python3
"""Actual adapter/loader/decoder/wrapper, strict C99 and ASan/UBSan.
Every fixture byte is synthetic. No SDL installation or game data is needed.
An optional output directory preserves the complete fixture/test receipt.
"""
from pathlib import Path
import sys,re,struct,json,hashlib,subprocess,os,tempfile
root=Path(__file__).resolve().parents[1]
temporary=tempfile.TemporaryDirectory(prefix="rear-p1-adapter-") if len(sys.argv)==1 else None
out=Path(sys.argv[1]).resolve() if temporary is None else Path(temporary.name)/"fixture"
out.mkdir(parents=True,exist_ok=False)
sha=lambda b:hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for c in b:h=((h^c)*1099511628211)&((1<<64)-1)
 return h

def extract(s,name):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',s,re.M);assert m,name
 a=m.start();b=s.index('{',a)+1;depth=1
 while depth:depth+=(s[b]=='{')-(s[b]=='}');b+=1
 return s[a:b]+'\n'
s=(root/'src/render_mirror.c').read_text()
asset=s[s.index('typedef struct {\n bool initialized,valid;'):s.index('/* Roads220')]
episodes=(root/'src/episodes.h').read_text();m=re.search(r'typedef struct\s*\{.*?\} JE_WeaponType;',episodes,re.S);assert m
m2=re.search(r'typedef struct\s*\{\s*char\s+name\[31\];.*?\} JE_WeaponPortType\[PORT_NUM \+ 1\];',episodes,re.S);assert m2
shots=(root/'src/shots.h').read_text();m3=re.search(r'typedef struct\s*\{.*?\} PlayerShotDataType;',shots,re.S);assert m3
(out/'types.inc').write_text(asset+'\n'+m[0]+'\n'+m2[0]+'\n'+m3[0]+'\n')
(out/'functions.inc').write_text(extract(s,'decode_tile'))
create=extract((root/'src/shots.c').read_text(),'player_shot_create')
(out/'create.inc').write_text(create)
shots_source=(root/'src/shots.c').read_text()
arrays=shots_source[shots_source.index('static const JE_word linkMultiGr'):shots_source.index('void player_shot_set_direction')]
linked=(root/'src/varz.c').read_text();route=re.search(r'const JE_word linkGunWeapons\[38\].*?=\s*\{.*?\};',linked,re.S)[0]
(out/'direction.inc').write_text(arrays+route+'\n'+extract(shots_source,'player_shot_set_direction'))

# Independent old gameplay path: strip only observer lines, keeping every
# original statement/return and the other pre-existing renderer/probe hooks.
baseline='\n'.join(line for line in create.split('\n') if 'rear_p1_' not in line)
(out/'create_baseline.inc').write_text(baseline.replace('player_shot_create(', 'baseline_shot_create(', 1))
(out/'wrapper.inc').write_text(extract((root/'src/entity_draw.c').read_text(),'draw_player_shot_sprite2'))
ids=[39,1,281,282,301,300,40,2,77,182,183,277,278,41,3,296,297,294,295,298,299,203,222,43,5]
observed=ids[:11]+[163,164]+ids[11:]
bank=bytearray(602);pins=[]
for k,i in enumerate(observed):
 struct.pack_into('<H',bank,2*(i-1),len(bank));v=bytes((k*23+y*12+x)%256 for y in range(14) for x in range(12))
 for y in range(14):bank+=bytes([0xc0])+v[y*12:(y+1)*12]+b'\x00'
 bank+=b'\x0f';pins.append(fnv(v+bytes([255])*168))
(out/'bank.bin').write_bytes(bank)
records=[];recordpins=[]
for k in range(6):
 # All unused tails are deliberately nonzero, with signed and 16-bit edges.
 mode=k%2 if k<4 else int(k==4)
 vals=[0x1234+k,[4,3,6,4,6,6][k],[1,1,2,2,4,2][k],0,2+2*mode,5,6,0]
 a=[1,1,1,1,25+k,0,198,255];dele=[255]*8;sx=([-10,10,0,0] if mode==0 else [-9,9,9,-9])+[-128,127,-1,0];sy=([0,0,0,0] if mode==0 else [2,2,-2,-2])+[-128,127,-1,0];bx=[0,-2,2,0,-128,127,-1,0];by=[0,0,0,0,-128,127,-1,0];sg=([40,2,0,0] if k==5 else [39,1,0,0] if mode==0 else [281,282,301,300])+[301,300,0x1234,0xff80]
 r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',*vals,*a,*dele,*sx,*sy,*bx,*by,*sg,0,0,0,25,255,208);assert len(r)==80
 records.append(r);recordpins.append(fnv(r))
# New record257 is synthetic too; append without changing any old fixture.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x1240,6,5,0,5,5,6,0,
 *([1]*5+[198,25,255]),*([255]*8),*[-9,9,9,-9,0,-128,127,-1],
 *[2,2,-2,-2,-10,-128,127,-1],*[-2,2,2,-2,0,-128,127,-1],
 *[0,0,0,0,0,-128,127,-1],*[281,282,301,300,77,0x1234,0xff80,301],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# Mode2 includes two canonical observed-only heads. Nonzero tails remain synthetic.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x1241,6,5,0,5,5,6,0,
 *([1]*5+[198,25,255]),*([255]*8),*[-6,6,6,-6,0,-128,127,-1],
 *[6,6,-6,-6,-10,-128,127,-1],*[-4,4,4,-4,0,-128,127,-1],
 *[0,0,0,0,0,-128,127,-1],*[163,164,183,182,77,0x1234,0xff80,301],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P5 mode2 is independently synthetic; exact invocation budget is four, not five.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x1242,6,4,0,4,5,6,0,
 *([2,2,1,1,198,25,255,19]),*([255]*8),*[-9,9,6,-6,0,-128,127,-1],
 *[2,2,-6,-6,0,-128,127,-1],*[-2,2,4,-4,0,-128,127,-1],
 *[0,0,0,0,0,-128,127,-1],*[277,278,183,182,77,0x1234,0xff80,301],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P5 mode1 remains synthetic, including intentionally different unused tails.
# Its two-allocation budget is independent of its selected power index4.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x1243,6,2,0,2,5,6,0,
 *([3,3,29,71,198,25,255,19]),*([255]*8),*[-10,10,0,0,0,-128,127,-1],
 *[0,0,0,0,0,-128,127,-1],*[0,0,4,-4,0,-128,127,-1],
 *[0,0,0,0,0,-128,127,-1],*[41,3,183,182,77,0x1234,0xff80,301],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P6 mode1 synthetic record: three successful allocations and a three-phase cycle.
# Distinct unused tails prevent accidental reuse of the preceding record fixture.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x1244,6,3,0,3,5,6,0,
 *([3,3,1,71,197,24,254,18]),*([255]*8),*[-10,10,0,0,0,-128,127,-1],
 *[0,0,-10,0,0,-128,127,-1],*[0,0,0,-4,0,-128,127,-1],
 *[0,0,0,0,0,-128,127,-1],*[41,3,77,182,183,0x1234,0xff80,301],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P6 mode2 is independently synthetic: five allocations and five phases.
# Distinct unused tails prevent accidental aliases to P4/P5 fixtures.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x1245,6,5,0,5,5,6,0,
 *([2,2,1,1,1,23,253,17]),*([255]*8),*[-9,9,6,-6,0,-128,127,-1],
 *[2,2,-6,-6,-10,-128,127,-1],*[-2,2,4,-4,0,-128,127,-1],
 *[0,0,0,0,0,-128,127,-1],*[277,278,183,182,77,0x4321,0xfe70,300],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P7 mode1 has four reflected twin phases; all fixture bytes remain synthetic.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x1246,6,4,0,4,5,6,0,
 *([2,2,2,2,197,22,252,16]),*([255]*8),*[-9,9,9,-9,0,-128,127,-1],
 *[2,2,-2,-2,0,-128,127,-1],*[-2,2,2,-2,0,-128,127,-1],
 *[0,0,0,0,0,-128,127,-1],*[277,278,297,296,77,0x3412,0xfd60,301],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P7 mode2: independent synthetic five-phase record, with nonzero tails.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x1247,6,5,0,5,5,6,0,
 *([2,2,2,2,1,21,251,15]),*([255]*8),*[-9,9,6,-6,0,-128,127,-1],
 *[2,2,-6,-6,-10,-128,127,-1],*[-2,2,4,-4,0,-128,127,-1],
 *[0,0,0,0,0,-128,127,-1],*[277,278,295,294,77,0x2513,0xfc50,300],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P8 mode1 synthetic six-shot record. Distinct full80-byte identity and tails.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x1248,6,6,0,6,5,6,0,
 *([2,2,2,2,1,1,250,14]),*([255]*8),*[-9,9,9,-9,-10,10,127,-1],
 *[2,2,-2,-2,0,0,127,-1],*[-2,2,2,-2,0,0,127,-1],
 *[0,0,0,0,0,0,127,-1],*[277,278,297,296,39,1,0xfb40,301],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P8 mode2 synthetic seven-shot record. All unused tails remain distinct.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x1249,6,7,0,7,5,6,0,
 *([2,2,2,2,1,1,1,13]),*([255]*8),*[-9,9,6,-6,0,-10,10,-1],
 *[2,2,-6,-6,-10,0,0,-1],*[-2,2,4,-4,0,0,0,-1],
 *[0,0,0,0,0,0,0,-1],*[277,278,295,294,77,39,1,0xfa30],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P9 mode1 synthetic six-shot record: deliberately unique unused full80 tails.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x124a,6,6,0,6,5,6,0,
 *([2,2,2,2,1,1,249,12]),*([255]*8),*[-9,9,9,-9,-10,10,126,-2],
 *[2,2,-2,-2,0,0,126,-2],*[-2,2,2,-2,0,0,126,-2],
 *[0,0,0,0,0,0,126,-2],*[277,278,297,296,41,3,0xfa20,302],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P9 mode2 seven-shot fixture; deliberately unique unused full80 tail.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x124b,6,7,0,7,5,6,0,
 *([2,2,2,2,1,2,2,11]),*([255]*8),*[-9,9,6,-6,0,-2,2,-3],
 *[2,2,-6,-6,-10,-9,-9,-3],*[-2,2,4,-4,0,-4,4,-3],
 *[0,0,0,0,0,0,0,-3],*[277,278,295,294,77,298,299,0xfb21],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P10 mode1: synthetic full80 with its own nonzero inactive tails.
# No original copyrighted record bytes are embedded in this public fixture.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x124c,6,6,0,6,5,6,0,
 *([2,2,2,2,4,4,247,10]),*([255]*8),*[-9,9,9,-9,-10,10,125,-4],
 *[2,2,-2,-2,0,0,125,-4],*[-2,2,2,-2,0,0,125,-4],
 *[0,0,0,0,0,0,125,-4],*[277,278,297,296,203,222,0xfc22,303],0,0,0,25,255,208)
assert len(r)==80
records.append(r);recordpins.append(fnv(r))
# P10 mode2 eight-shot fixture, independent of all original payload bytes.
# All eight active entries deliberately differ from prior record identities.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x124d,6,8,0,8,5,6,0,
 *[2,2,2,2,2,2,1,1],*([255]*8),*[-9,9,6,-6,-2,2,-10,10],
 *[2,2,-6,-6,-9,-9,0,0],*[-2,2,4,-4,-4,4,0,0],
 *([0]*8),*[277,278,295,294,298,299,39,1],0,0,0,25,255,208)
assert len(r)==80 and r not in records
records.append(r);recordpins.append(fnv(r))
# P11 SECOND is synthetic, with a distinct drain/coordinates/sound identity.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x124e,6,8,0,8,5,6,0,
 *([2]*8),*([255]*8),*[-9,9,6,-6,-2,2,-10,10],
 *[2,2,-6,-6,-9,-9,0,0],*[-2,2,4,-4,-4,4,0,0],
 *([0]*8),*[277,278,295,294,298,299,40,2],0,0,0,25,255,208)
assert len(r)==80 and r not in records
records.append(r);recordpins.append(fnv(r))
# P11 FIRST: independently synthetic full80 identity, including inactive tails7/8.
r=struct.pack('<HBBHBBBB8B8B8b8b8b8b8HbbBBBB',0x124f,6,6,0,6,5,6,0,
 *[2,2,2,2,5,5,246,9],*([255]*8),*[-9,9,9,-9,-10,10,124,-5],
 *[2,2,-2,-2,0,0,124,-5],*[-2,2,2,-2,0,0,124,-5],
 *[0,0,0,0,0,0,124,-5],*[277,278,297,296,43,5,0xfd23,304],0,0,0,25,255,208)
assert len(r)==80 and r not in records
records.append(r);recordpins.append(fnv(r))
(out/'records.bin').write_bytes(b''.join(records))
resources=out/'full';resources.mkdir();rgba_pins=[]
for k,i in enumerate(ids):
 row=[]
 for d in (4,8):
  rgba=bytes(c for j in range(168*d*d) for c in ((j+k*17)%256,(j*7+k)%256,(j*11)%256,[0,64,128,255][j%4]))
  h=struct.pack('<4s4I2i',b'HDR1',1310000+i,d,12,14,0,0);raw=h+rgba
  (resources/f'rear-multicannon-p1-bank8-{i}-{d}.hda').write_bytes(raw);row.append(0 if i in (182,183) and d==4 else fnv(rgba))
 rgba_pins.append(row)
header=lambda name,x:'#define '+name+' {'+','.join('UINT64_C(0x%016x)'%a for a in x)+'}\n'
rgba_header=lambda rows:'#define REAR_P1_RGBA_PINS {'+','.join('{'+','.join('UINT64_C(0x%016x)'%a for a in row)+'}' for row in rows)+'}\n'
(out/'fixture_pins.h').write_text('#define REAR_P1_BANK_SIZE '+str(len(bank))+'\n'+header('REAR_P1_SOURCE_PINS',pins)+header('REAR_P1_RECORD_PINS',recordpins)+'#ifdef REAR_P1_TEST_PENDING_ART\n'+rgba_header(rgba_pins[:21]+[[0,0],[0,0]]+rgba_pins[23:])+'#elif defined(REAR_P1_TEST_P11_PENDING_ART)\n'+rgba_header(rgba_pins[:-2]+[[0,0],[0,0]])+'#else\n'+rgba_header(rgba_pins)+'#endif\n')
# Each malformed family is a standalone directory; all other heads remain valid.
variants=[]
for d in (4,8):
 for k,i in enumerate(ids):
  source=resources/f'rear-multicannon-p1-bank8-{i}-{d}.hda';raw=source.read_bytes()
  for kind in ['missing','empty','magic','key','density','w','h','ax','ay','short','trunc','extra','payload','fifo','directory','device']:
   name=f'{i}-{d}-{kind}';p=out/name;p.mkdir();b=bytearray(raw)
   if kind=='empty':b=bytearray()
   if kind=='magic':b[0]^=1
   if kind in ['key','density','w','h','ax','ay']:b[{'key':4,'density':8,'w':12,'h':16,'ax':20,'ay':24}[kind]]^=1
   if kind=='short':b=b[:27]
   if kind=='trunc':b=b[:-1]
   if kind=='extra':b+=b'\x00'
   if kind=='payload':b[-1]^=1
   if kind=='fifo':os.mkfifo(p/source.name)
   elif kind=='directory':(p/source.name).mkdir()
   elif kind=='device':(p/source.name).symlink_to('/dev/null')
   elif kind!='missing':(p/source.name).write_bytes(b)
   otherd=8 if d==4 else 4
   (p/f'rear-multicannon-p1-bank8-{i}-{otherd}.hda').write_bytes((resources/f'rear-multicannon-p1-bank8-{i}-{otherd}.hda').read_bytes())
   variants.append((name,observed.index(i),d))
# Isolation negatives keep every other exact resource present.
for d in (4,8):
 for mask in (1,2,3):
  dest=out/f'p7-isolation-{d}-{mask}';dest.mkdir()
  for source in resources.glob('*.hda'):
   if source.name==f'rear-multicannon-p1-bank8-296-{d}.hda' and mask&1:continue
   raw=bytearray(source.read_bytes())
   if source.name==f'rear-multicannon-p1-bank8-297-{d}.hda' and mask&2:raw[-1]^=1
   (dest/source.name).write_bytes(raw)
# P7 mode2 isolation keeps every old and shared resource exact.
for d in (4,8):
 for mask in (1,2,3):
  dest=out/f'p7m2-isolation-{d}-{mask}';dest.mkdir()
  for source in resources.glob('*.hda'):
   if source.name==f'rear-multicannon-p1-bank8-294-{d}.hda' and mask&1:continue
   raw=bytearray(source.read_bytes())
   if source.name==f'rear-multicannon-p1-bank8-295-{d}.hda' and mask&2:raw[-1]^=1
   (dest/source.name).write_bytes(raw)
# Every P8 reused head independently missing or corrupt, with all other files exact.
for d in (4,8):
 for phase,i in enumerate([277,278,297,296,39,1],1):
  for kind in (0,1):
   dest=out/f'p8m1-isolation-{d}-{phase}-{kind}';dest.mkdir()
   for source in resources.glob('*.hda'):
    selected=source.name==f'rear-multicannon-p1-bank8-{i}-{d}.hda'
    if selected and kind==0:continue
    raw=bytearray(source.read_bytes())
    if selected:raw[-1]^=1
    (dest/source.name).write_bytes(raw)
# Every P8 mode2 resource independently missing or corrupt at exact density.
for d in (4,8):
 for phase,i in enumerate([277,278,295,294,77,39,1],1):
  for kind in (0,1):
   dest=out/f'p8m2-isolation-{d}-{phase}-{kind}';dest.mkdir()
   for source in resources.glob('*.hda'):
    selected=source.name==f'rear-multicannon-p1-bank8-{i}-{d}.hda'
    if selected and kind==0:continue
    raw=bytearray(source.read_bytes())
    if selected:raw[-1]^=1
    (dest/source.name).write_bytes(raw)
# Every P9 reused head independently missing or corrupt at the selected density.
for d in (4,8):
 for phase,i in enumerate([277,278,297,296,41,3],1):
  for kind in (0,1):
   dest=out/f'p9m1-isolation-{d}-{phase}-{kind}';dest.mkdir()
   for source in resources.glob('*.hda'):
    selected=source.name==f'rear-multicannon-p1-bank8-{i}-{d}.hda'
    if selected and kind==0:continue
    raw=bytearray(source.read_bytes())
    if selected:raw[-1]^=1
    (dest/source.name).write_bytes(raw)
# Every P9 mode2 resource independently missing/corrupt, including new tails.
for d in (4,8):
 for phase,i in enumerate([277,278,295,294,77,298,299],1):
  for kind in (0,1):
   dest=out/f'p9m2-isolation-{d}-{phase}-{kind}';dest.mkdir()
   for source in resources.glob('*.hda'):
    selected=source.name==f'rear-multicannon-p1-bank8-{i}-{d}.hda'
    if selected and kind==0:continue
    raw=bytearray(source.read_bytes())
    if selected:raw[-1]^=1
    (dest/source.name).write_bytes(raw)
# Every P10 selected head independently missing or corrupt at the selected density.
for d in (4,8):
 for phase,i in enumerate([277,278,297,296,203,222],1):
  for kind in (0,1):
   dest=out/f'p10m1-isolation-{d}-{phase}-{kind}';dest.mkdir()
   for source in resources.glob('*.hda'):
    selected=source.name==f'rear-multicannon-p1-bank8-{i}-{d}.hda'
    if selected and kind==0:continue
    raw=bytearray(source.read_bytes())
    if selected:raw[-1]^=1
    (dest/source.name).write_bytes(raw)
# Each exact P10 mode2 resource fails independently at the selected density.
for d in (4,8):
 for phase,i in enumerate([277,278,295,294,298,299,39,1],1):
  for kind in (0,1):
   dest=out/f'p10m2-isolation-{d}-{phase}-{kind}';dest.mkdir()
   for source in resources.glob('*.hda'):
    selected=source.name==f'rear-multicannon-p1-bank8-{i}-{d}.hda'
    if selected and kind==0:continue
    raw=bytearray(source.read_bytes())
    if selected:raw[-1]^=1
    (dest/source.name).write_bytes(raw)
# Each exact P11 SECOND phase fails independently at its selected density.
for d in (4,8):
 for phase,i in enumerate([277,278,295,294,298,299,40,2],1):
  for kind in (0,1):
   dest=out/f'p11m2-isolation-{d}-{phase}-{kind}';dest.mkdir()
   for source in resources.glob('*.hda'):
    selected=source.name==f'rear-multicannon-p1-bank8-{i}-{d}.hda'
    if selected and kind==0:continue
    raw=bytearray(source.read_bytes())
    if selected:raw[-1]^=1
    (dest/source.name).write_bytes(raw)
# P11 FIRST includes the two isolated new five-lobe horizontal roles.
for d in (4,8):
 for phase,i in enumerate([277,278,297,296,43,5],1):
  for kind in (0,1):
   dest=out/f'p11m1-isolation-{d}-{phase}-{kind}';dest.mkdir()
   for source in resources.glob('*.hda'):
    selected=source.name==f'rear-multicannon-p1-bank8-{i}-{d}.hda'
    if selected and kind==0:continue
    raw=bytearray(source.read_bytes())
    if selected:raw[-1]^=1
    (dest/source.name).write_bytes(raw)
reload=out/'reload';reload.mkdir()
for p in resources.glob('*.hda'):(reload/p.name).write_bytes(p.read_bytes())
(out/'variants.inc').write_text('static const struct {const char*name;unsigned member;int density;} variants[]={'+','.join('{"%s",%d,%d}'%v for v in variants)+'};\n')
(out/'fixture_receipt.json').write_text(json.dumps({'generated_only':True,'original_inputs':False,'source_pins':pins,'record_pins':recordpins,'rgba_pins':rgba_pins,'variants':len(variants),'production_sha256':{str(p.relative_to(root)):sha(p.read_bytes()) for p in [root/'src/rear_multi_p1.c',root/'src/rear_multi_p1.h',root/'src/rear_multi_p1_mirror.inc',root/'src/render_mirror.c',root/'src/entity_draw.c']},'extracted_sha256':{p.name:sha(p.read_bytes()) for p in out.glob('*.inc')}},indent=2)+'\n')
harness=Path(__file__).with_name('rear_multi_p1_adapter_test.c')
for mode in ['plain','sanitize','pending-plain','pending-sanitize','p11-pending-plain','p11-pending-sanitize']:
 exe=out/('adapter-'+mode);cmd=['cc','-std=c99','-Wall','-Wextra','-Werror','-pedantic','-O1','-g','-I'+str(root/'src'),'-I'+str(out),str(harness),str(root/'src/rear_multi_p1.c'),'-o',str(exe),'-lm']
 if mode.startswith('pending-'):cmd+=['-DREAR_P1_TEST_PENDING_ART']
 if mode.startswith('p11-pending-'):cmd+=['-DREAR_P1_TEST_P11_PENDING_ART']
 if mode.endswith('sanitize'):cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 subprocess.run(cmd,check=True)
 r=subprocess.run([str(exe),str(out)],env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1'},text=True,capture_output=True,timeout=180);print(mode,r.stdout,end='');print(r.stderr,end='',file=sys.stderr);(out/(mode+'.log')).write_text(r.stdout+r.stderr);r.check_returncode()

if temporary is not None:temporary.cleanup()
