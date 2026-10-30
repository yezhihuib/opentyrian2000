"""Pure gold source/fixture/schema helpers. No subprocess or native launch.
NEW RECOVERY EPOCH; original gold native result UNKNOWN.
Old six generated sources stay byte-exact. A separate derived outer shim only
renames the old entry and dispatches gold; it is not the old compiled harness.
"""
from pathlib import Path
import hashlib,re,struct,types,json,stat
BLUE_HELPER_SHA='38d904bf84c17ae9179c6c4bc4ca895f31393efcc774ac851d7db1bc6a23ef6d'
GOLD=(168,169);IDS=(91,145,61,101,120,139,168,169)
PACK_NAMES=('valid',)+tuple(n+str(i) for i in IDS for n in ('missing','bad'))+('only168','only169','old-only','header168','short168','trailing168','header169','short169','trailing169')
GROUPS=(('full_tile_native_patterns',4),('bounds',18),('pair_orders',26),('all8_early_dependency',16),('missing_bad',32),('singletons_oldonly',4),('malformed_gold',6),('unused_memory_payload_ready',8),('palette',40),('used_resource_shared',64),('callbacks',8),('cold_scope',10),('Talon_transfer',4),('lifecycle',5),('controlled_animation',6))
TAIL='\n#include "projectile_gold_pulse_native_additions.c.inc"\nint main(int argc,char **argv)\n{\n if(argc>=2&&!strcmp(argv[1],"--gold-pulse"))return gold_pulse_main(argc,argv);\n return inherited_blue_dispatch(argc,argv);\n}\n'
SHA=lambda data:hashlib.sha256(data).hexdigest()
def blue_helper(root):
 p=Path(root)/'tests/projectile_blue_triplet_native_validation.py';raw=p.read_bytes();assert SHA(raw)==BLUE_HELPER_SHA
 m=types.ModuleType('frozen_blue_native_helpers');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m

def outer_shim(raw):
 assert raw.count(b'int main(')==1 and b'inherited_blue_dispatch' not in raw
 out=raw.replace(b'int main(',b'int inherited_blue_dispatch(',1)+TAIL.encode()
 assert reverse_shim(out)==raw;return out

def reverse_shim(raw):
 assert raw.endswith(TAIL.encode());body=raw[:-len(TAIL.encode())]
 assert body.count(b'int inherited_blue_dispatch(')==1
 return body.replace(b'int inherited_blue_dispatch(',b'int main(',1)

SOURCE_PINS={'inherited145_harness.c': '8925fb11215446339f067124fa7223ec48dc7c86459e303d3803477773b2d9ac', 'accepted_projectile61_native_additions.c.inc': '5f80d681e84a6dff20873f7f05bb3a02e3fd0f22013edf2b5fbf133d36c51cfe', 'accepted61_wrapper.c': '59bfbe4d8e3bb8db4403eaabb199d8ff2f09b2eb2047769f39069c93dff7f4eb', 'projectile61_native_additions.c.inc': 'd894e392ce315b855d5a764fbb526b6d6568a14f223e7e577a4ebf303ecbf67a', 'projectile_blue_triplet_native_additions.c.inc': 'cf38a2c8582bf9c3299a84721d37dae83402b938c859a2489ad382844a9a6084', 'harness.c': 'd39e3b9633eff3abfc70604f96895f21184fa87ad7f344ffa64f2b7705b353e1'}
LEGACY_STDOUT={'inherited107_stdout': 'PASS inherited91 native lifecycle: 37 cases 81611 assertions\n145_TO_TALON copied=376 cached=0\n145_TO_TALON copied=376 cached=1\nPASS shared145 native lifecycle: 70 new cases 141992 new assertions; internal8 only; not gameplay/full build\n', 'inherited61_stdout': '61_TO_TALON copied=267 cached=0\n61_TO_TALON copied=267 cached=1\nPASS shared61 native lifecycle: 157 cases 822291 assertions; internal8 only; not gameplay/full build\n', 'new_blue_stdout': 'BLUE101_ZERO_NATIVE pattern=0 draw=384 finish=384 cache=384\nBLUE101_ZERO_NATIVE pattern=1 draw=384 finish=384 cache=384\nBLUE101_ZERO_HD prior=120 draw=384 finish=384 cache=384\nBLUE_TO_TALON selector=101 copied=1756 soft=1721 cached=0\nBLUE_TO_TALON selector=101 copied=1756 soft=1721 cached=1\nBLUE_TO_TALON selector=120 copied=1864 soft=1864 cached=0\nBLUE_TO_TALON selector=120 copied=1864 soft=1864 cached=1\nBLUE_TO_TALON selector=139 copied=1481 soft=1454 cached=0\nBLUE_TO_TALON selector=139 copied=1481 soft=1454 cached=1\nPASS blue triplet native lifecycle: 365 cases 11162937 assertions; internal8 only; not gameplay/full build\n'}
TRANSFER={168:(974,974,86),169:(735,735,85)}
GOLD_COMPANION_SHA='b00796c4d72265022da0e9e4e1c46acbbbff00ee754b5a51a61701aa778e6f46'
def source_bundle(root):
 sources=blue_helper(root).harness_sources(Path(root))
 assert len(sources)==6 and set(sources)==set(SOURCE_PINS)
 for name,data in sources.items():assert SHA(data)==SOURCE_PINS[name],name
 assert len(sources['harness.c'])==262
 companion=(Path(root)/'tests/projectile_gold_pulse_native_additions.c.inc').read_bytes()
 assert SHA(companion)==GOLD_COMPANION_SHA
 return sources,outer_shim(sources['harness.c'])

COVERAGE_PATH='authoring-inputs/projectile-gold-pulse-current/coverage-contract.json'
COVERAGE_SHA='ed516cc835d7858d27999c837160bd4a04d0f782e3affc9e803f87e1d83cd3cf'
def registration(root):
 p=Path(root)/COVERAGE_PATH;st=p.lstat();assert stat.S_ISREG(st.st_mode) and st.st_nlink==1 and not p.is_symlink()
 raw=p.read_bytes();assert SHA(raw)==COVERAGE_SHA
 j=json.loads(raw);assert set(j)=={'schema','members'} and j['schema']=='gold-pulse-selected-coverage-v1' and set(j['members'])=={'168','169'}
 return {'members':[dict(j['members'][str(i)],selector=i) for i in GOLD]}

def native_inputs(root,data):return blue_helper(root).native_inputs(Path(data))
def hda_name(i,blue):return blue.HDA_NAMES[i] if i not in GOLD else f'enemy-projectile-gold-pulse-{i}-8.hda'
def gold_fixture(raw,selector,leaf):
 assert selector in IDS and leaf in PACK_NAMES
 if leaf=='old-only' and selector in GOLD:return None
 if leaf.startswith('only') and selector!=int(leaf[4:]):return None
 if leaf=='missing'+str(selector):return None
 b=bytearray(raw)
 if leaf=='bad'+str(selector):b[128]^=1
 if leaf=='header'+str(selector):b[4]^=1
 if leaf=='short'+str(selector):b=b[:-1]
 if leaf=='trailing'+str(selector):b+=b'!'
 return bytes(b)

def fixture_payloads(root,hdas,registration):
 """Memory only; caller must write 335 independent regular files under budget."""
 assert set(hdas)==set(IDS);blue=blue_helper(root);members={x['selector']:x for x in registration['members']};assert set(members)==set(GOLD)
 for i in GOLD:
  assert SHA(hdas[i])==members[i]['hda_sha256'] and len(hdas[i])==43036
  assert hdas[i][:28]==struct.pack('<4s6I',b'HDR1',1530000+i,8,12,14,0,0)
 old=blue.fixture_payloads({i:hdas[i] for i in blue.SELECTORS});assert len(old)==151
 new={}
 for leaf in PACK_NAMES:
  for i in IDS:
   raw=gold_fixture(hdas[i],i,leaf)
   if raw is not None:new[f'gold-packs/{leaf}/{hda_name(i,blue)}']=raw
 assert len(new)==184 and not set(old)&set(new)
 return {**old,**new}

def verify_legacy_stdout(actual):
 keys=('inherited107_stdout','inherited61_stdout','new_blue_stdout')
 assert set(actual)==set(keys)
 for k in keys:assert actual[k]==LEGACY_STDOUT[k],('Original629 stdout differs',k)
 return {'cases':629,'assertions':12208831,'process_cases':[107,157,365]}

def parse_gold_stdout(stdout,transfer=None):
 if transfer is None:transfer=TRANSFER
 assert transfer==TRANSFER
 lines=stdout.splitlines();assert len(lines)==20,'exact15groups+4Talon+summary required'
 pos=0;observed=[]
 for name,count in GROUPS:
  if name=='Talon_transfer':
   for i in GOLD:
    copied,soft,alpha0=transfer[i]
    for cached in (0,1):
     want=f'GOLD_TO_TALON selector={i} copied={copied} soft={soft} alpha0={alpha0} cached={cached}'
     assert lines[pos]==want,('actual transfer schema/count',lines[pos]);observed.append(want);pos+=1
  assert lines[pos]==f'GOLD_GROUP name={name} cases={count}',('group missing/order/count',name);pos+=1
 match=re.fullmatch(r'PASS gold pulse native lifecycle: (\d+) cases (\d+) assertions; internal8 only; not gameplay/full build',lines[pos])
 assert match and int(match[1])==251 and int(match[2])>0 and sum(n for _,n in GROUPS)==251
 return {'cases':251,'assertions':int(match[2]),'groups':[{'name':n,'cases':c} for n,c in GROUPS],'transfers':observed,'scope':'Controlled internal8 production-TU probe; no game/fresh-fullbuild/fullgate claim.'}

if __name__=='__main__':raise SystemExit('Pure helpers only; use projectile_gold_pulse_fresh_native_validation.py for new authorized qualification.')
