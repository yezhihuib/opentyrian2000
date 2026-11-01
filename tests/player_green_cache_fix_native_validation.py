"""Portable finite cache regression adapter. No compile/process/write side effects.
Caller supplies original game bytes; no private workspace/receipt dependency.
Four cache setups + retained56 dispatch; NOT enemy-Green integration/gameplay.
"""
from pathlib import Path
import hashlib,re,struct,types
ROOT=Path(__file__).resolve().parents[1]
P244_HELPER_SHA='179336753b0e3aa60aad3000e358ed69765eb1d253c7e595f02b738ca4a9cd01'
COMPANION_SHA='3928faf78396149ea7f36559b9349128bbde0f73fb9fd310e73bf184eeef83f3'
HDT_SHA='fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b'
SMOKE_SHA='49e3d08e122ea71d6a621d2de127da00ce8a26ff73a0fb40d0cdd7ca2909d075'
RECORD_SHA='ad09f93950502e9faf7fabf00c8349fe1d07b35fcddb5cc548b673ab7398a9c9'
# Public registry: logical71 -> packed71; logical1071 -> packed890.
RECORD_OFFSETS=(26868,92388)
ASSETS={80214: 'cd2fe29818aa734481be907ba27d764b58cb178f6252ee9f3fa358f8560b8740', 80215: '917ebcb0f1044b55e025d9cc160546c96192f5e142e950ccf08415f947cfa7bf', 80216: 'f06bd83d10dbab85d50afc0d7946da52d1a4a9bf496cfaba172e6856b772187e', 80217: '9610d3cab03120754e0d57dca628851ac9ec336bde1712818a17cd6e1425021f', 1060078: 'd3bbf0c8db73e668a6568b1c8f7761d15f0afcacc60a9833716c6a0e75a73570', 1060079: 'cf4d7631aeca4fcd16580d4c469ffe347399db216c20ae2b558806edb9e1ff52', 1060080: 'addfb289ae0515c7e8e242413a781bdeaf50dc7639ded379d02e950e7a966a53', 1060081: 'fbf3acbd3398b41235e12c0d6154856fb97a521027b6ea840837277ba2f21170', 1060082: '6f9267129302b03c4cf5cb0f18bd92c641f26c8a8e5dae11be7f6fe46de0fffb', 1060083: 'a8f74a576c27990158f53a6e16bef740419a235719231073cd893d28be872151', 1060084: '7512c324cb607c492c673534991a5e05e6e0967ec5a3ee03fb27a97ce292dd60', 1470227: '9de332ec5d8d7f5c0e7eb56445aabebe22897b27a6fde1ee7f36da822076aac7'}
SOURCE_FUNCTION_PINS={'global_projectile91_pre_final_pixel': 'e21bc1c11e4927f675725fc225b9cd9c61d7766e06baf156d0cdf7be1f0bb149', 'global_projectile91_final_rect_walk': '6e04fc01d8ded77b69206788e7585312d35a7f4d9c2b69752b946fa923844e8b', 'global_projectile91_pre_final_rect': 'c333c34e871afc05fd32b875e0215d33fb9f2243d2718e629b43a7cdb52e48f4'}
CASE_INVENTORY={'pixel_ordinary':1,'rect_ordinary':1,'pixel_real_fade7':1,'rect_real_fade7':1}
RETAINED_SETUP_COUNT=56
COMPANIONS=('projectile_gold_pulse_native_additions.c.inc','projectile_statics_native_additions.c.inc','projectile_pulses16694_native_additions.c.inc','projectile_bolts745_native_additions.c.inc','projectile_animated153_background_native.c.inc','projectile_animated153_native_additions.c.inc','enemy_vulcan70_native_additions.c.inc','widget_sonic_native_additions.c.inc','orb_protron_native_additions.c.inc','protron244_native_additions.c.inc')
def sha(b):return hashlib.sha256(b).hexdigest()
def p244_helper(root):
 p=Path(root)/'tests/protron244_native_validation.py';raw=p.read_bytes()
 if sha(raw)!=P244_HELPER_SHA:raise ValueError('Changed inherited adapter')
 m=types.ModuleType('p244_cache_predecessor');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m
def companion(root):
 b=(Path(root)/'tests/player_green_cache_fix_native_additions.c.inc').read_bytes()
 if sha(b)!=COMPANION_SHA:raise ValueError('Changed focused companion')
 return b
def outer_shim(raw,root):
 old=p244_helper(root).source_bundle(root)[1]
 if raw!=old or raw.count(b'int main(int argc,char **argv)')!=1:raise ValueError('Changed historical dispatcher')
 return raw.replace(b'int main(int argc,char **argv)',b'int inherited_p244_diagnostic_dispatch(int argc,char **argv)',1)+b'\n'+companion(root)
def reverse_shim(raw,root):
 suffix=b'\n'+companion(root)
 if not raw.endswith(suffix):raise ValueError('Changed companion suffix')
 body=raw[:-len(suffix)]
 if body.count(b'int inherited_p244_diagnostic_dispatch(')!=1:raise ValueError('Changed historical entry')
 old=body.replace(b'int inherited_p244_diagnostic_dispatch(',b'int main(',1)
 if old!=p244_helper(root).source_bundle(root)[1]:raise ValueError('Changed old dispatcher bytes')
 return old
def source_bundle(root):
 root=Path(root);sources,raw=p244_helper(root).source_bundle(root);sources=dict(sources)
 for name in COMPANIONS:
  if name in sources:raise ValueError('Unexpected generated source collision')
  sources[name]=(root/'tests'/name).read_bytes()
 return sources,outer_shim(raw,root)
def native_input(base_stdin,hdt,smoke,root=ROOT):
 if any(type(b)is not bytes for b in (base_stdin,hdt,smoke)):raise ValueError('Original bytes required')
 if sha(hdt)!=HDT_SHA or len(smoke)!=17810 or sha(smoke)!=SMOKE_SHA:raise ValueError('Changed original game sources')
 records=[hdt[o:o+80]for o in RECORD_OFFSETS]
 if any(sha(r)!=RECORD_SHA for r in records):raise ValueError('Changed canonical Green records')
 base=p244_helper(root).native_input(base_stdin,hdt)
 if len(base)!=99142:raise ValueError('Unexpected predecessor stdin')
 return base+b''.join(records)+smoke
def green_payloads(hdas):
 if type(hdas)is not dict or set(hdas)!=set(ASSETS) or any(type(i)is not int for i in hdas):raise ValueError('Exact12 material identities required')
 result={}
 for i,pin in ASSETS.items():
  b=hdas[i]
  if type(b)is not bytes or len(b)!=43036 or sha(b)!=pin:raise ValueError('Changed canonical HDA')
  if struct.unpack('<4s6I',b[:28])!=(b'HDR1',i,8,12,14,0,0):raise ValueError('Changed identity/geometry')
  result['content/'+pin+'.hda']=b
 return result
def function_text(text,name):
 matches=list(re.finditer(r'(?:static )?(?:void|bool) '+name+r'\([^;]*?\)\n\{',text))
 if len(matches)!=1:raise ValueError('Missing/duplicate source function '+name)
 m=matches[0];i=m.end();depth=1
 while depth and i<len(text):depth+=(text[i]=='{')-(text[i]=='}');i+=1
 if depth:raise ValueError('Unterminated source function')
 return text[m.start():i]
def validate_source_contract(mirror,shared):
 for name,pin in SOURCE_FUNCTION_PINS.items():
  if sha(function_text(shared,name).encode())!=pin:raise ValueError('Changed preflight predicate/lease/clip walker')
 for name,statement in [('render_mirror_pixel','global_projectile91_pre_final_pixel(surface,address);'),('render_mirror_rect','global_projectile91_pre_final_rect(s,rect);')]:
  body=function_text(mirror,name).split('{',1)[1].lstrip()
  if not body.startswith(statement):raise ValueError('Preflight must precede all final writers')
 return True
