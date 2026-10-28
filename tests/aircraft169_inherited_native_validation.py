#!/usr/bin/env python3
"""SHA-locked inherited matrices against the same already-fresh configurations.

Only interceptor166, fighter165 and scout164 finite counts and obsolete
invalid-index probes are adapted for the finite40 contract. Original harness/driver files stay
byte-exact. This does not claim three additional production configuration builds.
"""
import argparse,hashlib,json,os,sys,time
from pathlib import Path

PINS={
 'tests/interceptor166_newshf_native_validation.c':'a000fd49c74ca602bdf1427a766e745ac9a2ca2c3948e24dfff8b4954d555861',
 'tests/interceptor166_newshf_native_validation.py':'6a29f252fbbe4222c1d3ddd54d918a1f2fab542a5947ee157763da33f5e500a9',
 'tests/interceptor166_inherited_native_validation.py':'d4ffd780c9391c262500931a9750702c87a06c5f5bc525924d4d8102766ef5c5',
 'tests/newshf_compositor_validation.c':'c7243a9208e1f1f1bee7c26d3d3af66caf7028f69429478011b10da4b9ba306e',
 'tests/newshf_compositor_validation.py':'d1d47d070ffa7f819366b9183b41a584c3b53a12dccd7487f6d3969fb6810620',
 'tests/current_newshf_native_validation.py':'2d77edef23d2f384bb12b04cac801f215082ab324c06bb212d5b9047e219981d',

 'tests/fighter165_newshf_native_validation.c':'30bceace4ffe7b16a2d808436f79196d35a5d2b54499c6f1e64739c1a4b43eee',
 'tests/fighter165_newshf_native_validation.py':'85b43e34ee31b44debbfe7f53dd6a2d937f82621513c55f7dc7998f981c788bb',
 'tests/fighter165_inherited_native_validation.py':'a54c7b4111ccfe0e7e06fa0f965c4f4e8452c20723831938bae8048288454cab',
 'tests/scout164_newshf_native_validation.c':'c96170cc68b3cb114a0dc54826c4a26cb46d9b76e30d510d009878322464f385',
 'tests/scout164_newshf_native_validation.py':'0ee258d9ec7ee3bb4706dbe6ce059cfc832c059355e13cf855a75f6cfd60c773',
 'tests/large_newshi_native_validation.py':'26fed438470afe36d9a13bfcd0555b92d416c2e063ed1a1fc38bedf4a2f2c2f5',
 'tests/large_newshi_native_validation.c':'76980e2dd67e97b4150ceecb28bf99b54ff243154d2e1f8b19e8943efd150b32',
}
SHA=lambda b:hashlib.sha256(b).hexdigest()
def digest(p):return SHA(p.read_bytes())
def tree(p):return {q.relative_to(p).as_posix():digest(q) for q in sorted(p.rglob('*')) if q.is_file() and '__pycache__' not in q.parts}
def replace_once(s,a,b):
 assert s.count(a)==1,('adapter marker drift',a)
 return s.replace(a,b)
def adapt_scout(raw):
 assert SHA(raw)==PINS['tests/scout164_newshf_native_validation.c'],'historical scout harness drift'
 text=raw.decode()
 for old,new in [
 ('GLOBAL_NEWSHF_RESOURCE_COUNT==31&&COUNTOF(newshf_profiles)==18','GLOBAL_NEWSHF_RESOURCE_COUNT==40&&COUNTOF(newshf_profiles)==21'),
 ('!global_newshf_phase_bank_matches(31,b10)&&!global_newshf_phase_bank_matches(32,b10)','!global_newshf_phase_bank_matches(40,b10)&&!global_newshf_phase_bank_matches(41,b10)'),
 ('!global_newshf_group_ready(31)&&!global_newshf_group_ready(32)','!global_newshf_group_ready(40)&&!global_newshf_group_ready(41)'),
 ('mode==0?28:mode==1?18:31','mode==0?28:mode==1?18:40')]:text=replace_once(text,old,new)
 return text.encode()
def adapt_fighter(raw):
 assert SHA(raw)==PINS['tests/fighter165_newshf_native_validation.c'],'historical fighter harness drift'
 text=raw.decode()
 for old,new in [
 ('GLOBAL_NEWSHF_RESOURCE_COUNT==34&&COUNTOF(newshf_profiles)==19','GLOBAL_NEWSHF_RESOURCE_COUNT==40&&COUNTOF(newshf_profiles)==21'),
 ('const unsigned invalid[]={34,63,64,UINT_MAX}','const unsigned invalid[]={40,63,64,UINT_MAX}')]:text=replace_once(text,old,new)
 return text.encode()
def adapt_interceptor(raw):
 assert SHA(raw)==PINS['tests/interceptor166_newshf_native_validation.c'],'historical interceptor harness drift'
 text=raw.decode()
 for old,new in [
 ('GLOBAL_NEWSHF_RESOURCE_COUNT==37&&COUNTOF(newshf_profiles)==20','GLOBAL_NEWSHF_RESOURCE_COUNT==40&&COUNTOF(newshf_profiles)==21'),
 ('const unsigned invalid[]={37,63,64,UINT_MAX}','const unsigned invalid[]={40,63,64,UINT_MAX}')]:text=replace_once(text,old,new)
 # Both terminal whole-registry loops extend to include the optional new group.
 old='for(unsigned p=0;p<37;p++)'
 assert text.count(old)==2,('adapter marker drift',old)
 return text.replace(old,'for(unsigned p=0;p<40;p++)').encode()

def adapt_driver(raw,suite,adapted):
 # Existing immutable already-fresh objects protocol; no new cache or build skip.
 if suite not in ('fighter165_newshf','scout164_newshf','interceptor166_newshf'):return raw
 raw=replace_once(raw,"assert not any(x in sys.argv for x in ('--skip-build','--negative-control','--compose-negative-control'))", "assert not any(x in sys.argv for x in ('--negative-control','--compose-negative-control'))")
 raw=replace_once(raw,"if '--out' in sys.argv:assert not Path(sys.argv[sys.argv.index('--out')+1]).exists(), 'Native proof output must be new'", "# Output was exclusively created and bound by the outer immutable-reuse adapter.")
 raw=replace_once(raw,"source=source.replace('tests/newshf_compositor_validation.c','tests/"+suite+"_native_validation.c')", "source=source.replace(\"str(ROOT/'tests/newshf_compositor_validation.c')\", "+repr('str(Path('+repr(str(adapted))+'))')+")")
 if suite=='interceptor166_newshf':
  # Its unchanged oracle still exercises phases34–36; only fixture inventory
  # expands so the two whole-registry checks also see the new optional group.
  raw=replace_once(raw,"'newshf-fighter165','newshf-interceptor166')","'newshf-fighter165','newshf-interceptor166','newshf-aircraft169')")
  raw=replace_once(raw,'[9,6,1,2,10,3,3,3]','[9,6,1,2,10,3,3,3,3]')
 return raw

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--fresh-proof',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True);p.add_argument('--original-data',type=Path,required=True);p.add_argument('--sysroot',type=Path,required=True)
 p.add_argument('--suite',choices=['interceptor166','fighter165','scout164','old361'],required=True);a=p.parse_args()
 root=a.source_root.resolve();fresh=a.fresh_proof.resolve();out=a.out.resolve();assert not out.exists(),'fresh output required'
 for name,h in PINS.items():assert digest(root/name)==h,('historical native input changed',name)
 proof=json.loads((fresh/'native-receipt.json').read_text());assert proof['status']=='PASS'
 for name,h in proof['source_sha256'].items():
  assert digest(root/name)==h,('current source differs from fresh proof',name)
  assert digest(fresh/'hd-on-build'/name)==h,('compiled source differs',name)
 configs={m:digest(fresh/(m+'-build')/'opentyrian2000') for m in ('default-off','hd-on','mirror-disabled')}
 assert all(h==proof['modes'][m]['binary_sha256'] for m,h in configs.items())
 objects=tree(fresh/'hd-on-build/obj');assert objects
 source_before=tree(root/'src');scripts_before=tree(root/'scripts');tests_before=tree(root/'tests')
 assets_before={t:tree(root/t) for t in ('assets/hd/current-compat','assets/hd/global-assets-v1/content','authoring-inputs')}
 originals_before={n:digest(a.original_data/n) for n in ('newshf.shp','newshi.shp','tyrian.hdt','palette.dat','tyrian.shp')}
 out.mkdir();build=out/'hd-on-build';(build/'obj').mkdir(parents=True)
 for q in (fresh/'hd-on-build/obj').iterdir():
  if q.is_file():os.link(q,build/'obj'/q.name)
 suite={'interceptor166':'interceptor166_newshf','fighter165':'fighter165_newshf','scout164':'scout164_newshf','old361':'large_newshi'}[a.suite]
 driver=root/('tests/'+suite+'_native_validation.py');raw=driver.read_text()
 if a.suite in ('interceptor166','fighter165','scout164'):
  adapted=out/(a.suite+'-native-adapted.c');adapted.write_bytes({'interceptor166':adapt_interceptor,'fighter165':adapt_fighter,'scout164':adapt_scout}[a.suite]((root/('tests/'+suite+'_native_validation.c')).read_bytes()))
  # Quoted include is resolved from the original tests directory, never by
  # altering the inherited helper's bytes or production include search order.
  adapted.write_text(adapted.read_text().replace('#include "newshf_compositor_validation.c"','#include '+json.dumps(str(root/'tests/newshf_compositor_validation.c'))))
  raw=adapt_driver(raw,suite,adapted)
 report=dict(status='RUNNING',suite=a.suite,original_sha256=PINS,adapter_sha256=digest(Path(__file__)),adapted_driver_sha256=SHA(raw.encode()),fresh_proof_sha256=digest(fresh/'native-receipt.json'),configuration_binary_sha256=configs,objects_before=objects,source_before=source_before,originals_before=originals_before,reuse_scope='Exact already-fresh three configuration binaries/objects; freshly compiled ASan/UBSan inherited harness, not additional configuration builds.')
 if a.suite in ('interceptor166','fighter165','scout164'):report['adapted_harness_sha256']=digest(adapted)
 receipt=out/'inherited-binding.json';receipt.write_text(json.dumps(report,indent=2)+'\n')
 sys.path.insert(0,str(root/'scripts'));sys.path.insert(0,str(root/'tests'))
 sys.argv=[str(driver),'--source-root',str(root),'--original-data',str(a.original_data),'--sysroot',str(a.sysroot),'--out',str(out),'--skip-build']
 started=time.time()
 try:exec(compile(raw,str(driver),'exec'),{'__name__':'__main__','__file__':str(driver)});code=0
 except SystemExit as e:code=e.code or 0
 nr=json.loads((out/'native-receipt.json').read_text()) if (out/'native-receipt.json').exists() else {'status':'MISSING'}
 checks=dict(source_unchanged=tree(root/'src')==source_before,scripts_unchanged=tree(root/'scripts')==scripts_before,tests_unchanged=tree(root/'tests')==tests_before,assets_unchanged=all(tree(root/t)==v for t,v in assets_before.items()),originals_unchanged=all(digest(a.original_data/n)==h for n,h in originals_before.items()),objects_unchanged=tree(fresh/'hd-on-build/obj')==objects,configs_unchanged=all(digest(fresh/(m+'-build')/'opentyrian2000')==h for m,h in configs.items()))
 report.update(status='PASS' if code==0 and nr.get('status')=='PASS' and all(checks.values()) else 'FAIL',returncode=code,seconds=time.time()-started,checks=checks,native_stdout=nr.get('stdout'),native_receipt_sha256=digest(out/'native-receipt.json'))
 receipt.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('objects_before','source_before')},indent=2));raise SystemExit(report['status']!='PASS')
if __name__=='__main__':main()
