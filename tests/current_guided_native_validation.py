#!/usr/bin/env python3
"""Finite adapter for CURRENT Guided; frozen historical fixtures are untouched.
Full native production renderer and indexed wrappers, not extracted stubs.
The legacy driver is SHA pinned; only current Guided pins, extra fixture files,
and the explicit new harness are injected. No original game bytes are saved.
Arguments are those of enemy_protron_reuse_validation.py, plus --source-root.
"""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DRIVER_SHA='7c367b5251439e18bf0ea7754584f4666639bcd2b9a871bf8a359044c10d20b8'

def replace_once(source,before,after):
    assert source.count(before)==1,before
    return source.replace(before,after)

def main():
    root=ROOT
    if '--source-root' in sys.argv:
        i=sys.argv.index('--source-root');root=Path(sys.argv[i+1]).resolve();del sys.argv[i:i+2]
    raw=(ROOT/'tests/enemy_protron_reuse_validation.py').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==DRIVER_SHA,'Frozen native driver changed: review adapter explicitly'
    source=replace_once(raw.decode(),'ROOT=Path(__file__).resolve().parents[1]',f'ROOT=Path({str(root)!r})')
    source=replace_once(source," current_sonic = None",''' sys.path.insert(0,str(ROOT/'scripts'))
 import current_guided_compatibility as guided
 guided.load(ROOT)
 selected,_,guided_derived=guided.generate(ROOT,guided.read(ROOT,guided.SELECTION))
 assert set(guided_derived)==set(guided.PAIRS)
 for (identity,density),blob in guided_derived.items():
  if identity in (80020,80021):pins[identity-80000]=SHA(blob)
 current_sonic = None''')
    source=replace_once(source,"list((ROOT/'tests').glob('*reuse_validation.*'))", "list((ROOT/'tests').glob('*reuse_validation.*'))+list((ROOT/'tests').glob('current_guided_native*'))")
    marker=" run(['cc',*flags,*sanitized,'-no-pie',str(ROOT/'tests'/('enemy_controlled_probe_validation.c' if a.controlled_session else 'enemy_observe_validation.c' if a.observe_session else 'enemy_protron_reuse_validation.c')),*objects,*libs,'-lm','-o',str(a.out/'test')])"
    source=replace_once(source,marker,""" assert not a.controlled_session and not a.observe_session and not a.negative_control, 'Current Guided finite native adapter only'
 legacy=(ROOT/'tests/enemy_protron_reuse_validation.c').read_text()
 assert legacy.count('int main(int argc,char **argv)')==1
 (a.out/'native_p09_current_helpers.inc').write_text(legacy.replace('int main(int argc,char **argv)','static int current_guided_legacy_p09_main(int argc,char **argv)'))
 run(['cc',*flags,*sanitized,'-no-pie',str(ROOT/'tests/current_guided_native_validation.c'),*objects,*libs,'-lm','-o',str(a.out/'test')])""")
    source=replace_once(source," content=fixture/'content'",''' for (identity,density),blob in guided_derived.items():
  frame=identity-80000;dest=fixture/guided.name(identity,density)
  if not dest.exists():dest.write_bytes(blob)
  assert dest.read_bytes()==blob
  for mode in ('missing','magic','header','short'):
   folder=fixture/f'player-{mode}-{frame}';folder.mkdir(exist_ok=True)
   if mode!='missing':
    bad=bytearray(blob)
    if mode=='magic':bad[0]^=1
    if mode=='header':bad[4]^=1
    if mode=='short':bad=bad[:-1]
    (folder/dest.name).write_bytes(bad)
 content=fixture/'content' ''')
    source=replace_once(source," report={'current_sonic_art':current_sonic", " report={'current_guided_selection_sha256':SHA(guided.read(ROOT,guided.SELECTION)),'current_guided_hda_sha256':{str(k):SHA(v) for k,v in guided_derived.items()},'adapter_sha256':SHA(Path(__file__).read_bytes()),'current_sonic_art':current_sonic")
    exec(compile(source,str(ROOT/'tests/enemy_protron_reuse_validation.py'),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})

if __name__=='__main__':main()
