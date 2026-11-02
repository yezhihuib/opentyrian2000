"""Combined real-owner qualification adapter. Pure generation, no processes.
The predecessor entrypoints remain present but combined selection runs only12.
No original game bytes or private paths are embedded in this public module.
"""
from pathlib import Path
import hashlib,types
ROOT=Path(__file__).resolve().parents[1]
MUZZLE_HELPER_SHA='d94c2fcb20fe14f38d225a24aa1d06b1f1c1e1c58b9d531613d6da337307364b'
MUZZLE_C_SHA='cbeb0430e9bc3e4063fa6f1e505fcca1c8dbd2440a785147df4b82e58818704d'
CASE_INVENTORY={'ordered_warning_then_shifted_and_reverse_with_repeat_blink_invalid_loader_substeps':2,'native_only_or_shifted_only_retired_samevalue_pixel_rect_normal_fade':8,'real_Green_retirement_with_nonoverlap_warning_isolation':2}
SCOPE='Real current renderer/HUF/SDL/Green;12 setups only, not old32/44, not full gameplay; Green WARNING isolation is nonoverlapping, not triple same-pixel proof.'
STDOUT_PATTERN=r'PASS combined WARNING/muzzle real-owner native: 12 setups [0-9]+ assertions; no old32/44 dispatch, not full gameplay\n'
assert sum(CASE_INVENTORY.values())==12
def sha(raw):return hashlib.sha256(raw).hexdigest()
def predecessor(root):
 p=Path(root)/'tests/tank_muzzle_native_validation.py';raw=p.read_bytes()
 if sha(raw)!=MUZZLE_HELPER_SHA:raise ValueError('Changed approved muzzle helper')
 m=types.ModuleType('combined_muzzle_predecessor');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m

def loader_prefix(root):
 raw=(Path(root)/'tests/tank_muzzle_native_additions.c.inc').read_bytes()
 if sha(raw)!=MUZZLE_C_SHA:raise ValueError('Changed approved muzzle companion')
 text=raw.decode();start='static int mu_main(int argc,char **argv)\n{\n';end=' unsigned initial=cases,assertions=checks;'
 if text.count(start)!=1 or text.count(end)!=1:raise ValueError('Changed finite initialization anchors')
 prefix=text.split(start,1)[1].split(end,1)[0]
 if prefix.count('"--tank-muzzle"')!=1 or prefix.count('CHECK(fgetc(stdin)==EOF);')!=1:raise ValueError('Changed initialization contract')
 return ('static void cw_load(int argc,char **argv)\n{\n'+prefix.replace('"--tank-muzzle"','"--warning-muzzle"',1)+'}\n').encode()

def source_bundle(root):
 root=Path(root);old=predecessor(root);sources,raw=old.source_bundle(root);sources=dict(sources)
 sources['warning_muzzle_input.c.inc']=loader_prefix(root)
 sources['warning_muzzle_native_additions.c.inc']=(root/'tests/warning_muzzle_native_additions.c.inc').read_bytes()
 if raw.count(b'int main(')!=1:raise ValueError('Changed predecessor entry')
 body=raw.replace(b'int main(',b'int inherited_muzzle_dispatch(',1)
 return sources,body+b'\n#include "warning_muzzle_input.c.inc"\n#include "warning_muzzle_native_additions.c.inc"\nint main(int argc,char **argv){if(argc>=2&&!strcmp(argv[1],"--warning-muzzle"))return cw_main(argc,argv);return inherited_muzzle_dispatch(argc,argv);}\n'

def fixture_payloads(hdas,pins,names,huf,root=ROOT):
 result=predecessor(root).fixture_payloads(hdas,pins,names,huf,root)
 if len(result)!=54 or result.get('muzzle-font/gameplay-hud-font-v1.hda')!=huf:raise ValueError('Changed finite predecessor fixtures')
 corrupt=bytearray(huf);corrupt[-1]^=1
 result['warning-bad/gameplay-hud-font-v1.hda']=bytes(corrupt)
 if len(result)!=55:raise ValueError('Combined fixture membership')
 return result

def native_input(base_stdin,hdt,smoke,bank20,pic,shp,root=ROOT):
 raw=predecessor(root).native_input(base_stdin,hdt,smoke,bank20,pic,shp,root)
 if len(raw)!=230615 or sha(raw)!='979b0bb1601f1acc9796c8c8977bd8a7d42bde179374a29174a6070a3025bbd7':raise ValueError('Changed original combined input')
 return raw
