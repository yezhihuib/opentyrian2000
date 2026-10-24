#!/usr/bin/env python3
"""Finite adapter for CURRENT Mint27; frozen historical fixtures are untouched.
Full native production renderer and indexed wrappers, not extracted stubs.
The legacy driver is SHA pinned; only current Mint27 pins, extra fixture files,
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
    raw=(root/'tests/enemy_protron_reuse_validation.py').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==DRIVER_SHA,'Frozen native driver changed: review adapter explicitly'
    source=replace_once(raw.decode(),'ROOT=Path(__file__).resolve().parents[1]',f'ROOT=Path({str(root)!r})')
    source=replace_once(source," current_sonic = None",''' sys.path.insert(0,str(ROOT/'scripts'))
 import current_mint27_compatibility as mint27
 mint27.load(ROOT)
 selected,_,mint27_derived=mint27.generate(ROOT,mint27.read(ROOT,mint27.SELECTION))
 assert set(mint27_derived)==set(mint27.PAIRS)
 for (identity,density),blob in mint27_derived.items():
  assert identity==80027
 current_sonic = None''')
    source=replace_once(source,"list((ROOT/'tests').glob('*reuse_validation.*'))", "list((ROOT/'tests').glob('*reuse_validation.*'))+list((ROOT/'tests').glob('current_mint27_native*'))")
    marker=" run(['cc',*flags,*sanitized,'-no-pie',str(ROOT/'tests'/('enemy_controlled_probe_validation.c' if a.controlled_session else 'enemy_observe_validation.c' if a.observe_session else 'enemy_protron_reuse_validation.c')),*objects,*libs,'-lm','-o',str(a.out/'test')])"
    source=replace_once(source,marker,""" assert not a.controlled_session and not a.observe_session and not a.negative_control, 'Current Mint27 finite native adapter only'
 legacy=(ROOT/'tests/enemy_protron_reuse_validation.c').read_text()
 assert legacy.count('int main(int argc,char **argv)')==1
 (a.out/'native_p09_current_helpers.inc').write_text(legacy.replace('int main(int argc,char **argv)','static int current_mint27_legacy_p09_main(int argc,char **argv)'))
 run(['cc',*flags,*sanitized,'-no-pie',str(ROOT/'tests/current_mint27_native_validation.c'),*objects,*libs,'-lm','-o',str(a.out/'test')])""")
    source=replace_once(source," content=fixture/'content'",''' for (identity,density),blob in mint27_derived.items():
  frame=identity-80000;dest=fixture/mint27.name(identity,density)
  if not dest.exists():dest.write_bytes(blob)
  assert dest.read_bytes()==blob
  for mode in ('missing','magic','header','short','anchor','trailing','payload'):
   folder=fixture/f'player-{mode}-{frame}';folder.mkdir(exist_ok=True)
   if mode!='missing':
    bad=bytearray(blob)
    if mode=='magic':bad[0]^=1
    if mode=='header':bad[4]^=1
    if mode=='short':bad=bad[:-1]
    if mode=='anchor':bad[20]=1
    if mode=='trailing':bad+=b'!'
    if mode=='payload':bad[31]^=1
    (folder/dest.name).write_bytes(bad)
 content=fixture/'content' ''')
    source=replace_once(source," report={'current_sonic_art':current_sonic", " report={'current_mint27_selection_sha256':SHA(mint27.read(ROOT,mint27.SELECTION)),'current_mint27_hda_sha256':{str(k):SHA(v) for k,v in mint27_derived.items()},'adapter_sha256':SHA(Path(__file__).read_bytes()),'current_sonic_art':current_sonic")
    exec(compile(source,str(ROOT/'tests/enemy_protron_reuse_validation.py'),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})

if __name__=='__main__':main()
