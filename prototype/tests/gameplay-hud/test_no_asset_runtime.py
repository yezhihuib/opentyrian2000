#!/usr/bin/env python3
"""Linux hash-only no-HUD runtime regression; reads existing game data and pack.
No screenshots, game-data copies, or art are created. TSV streams use FIFOs.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import subprocess
import time

ROOT=Path(__file__).resolve().parents[3]
IMPORTANT={'state.tsv','collisions.tsv','rgb-audit.tsv','frames.tsv','presentation.tsv','sdl-runtime.tsv'}

def run(executable,mode,directory,pack,data,ticks):
    directory.mkdir(parents=True)
    names=set()
    for p in (ROOT/'src').glob('*.c'):
        names.update(re.findall(r'fopen\("([^"/]+\.tsv)"\s*,\s*"w"',p.read_text()))
    names.update(IMPORTANT)
    selector=selectors.DefaultSelector()
    records={}
    for name in sorted(names):
        fifo=directory/name
        os.mkfifo(fifo)
        fd=os.open(fifo,os.O_RDWR|os.O_NONBLOCK)
        record={'sha':hashlib.sha256(),'bytes':0,'lines':0,'first':b'', 'gzip':None}
        if name in IMPORTANT:record['gzip']=gzip.open(str(fifo)+'.gz','wb',compresslevel=6)
        records[name]=record
        selector.register(fd,selectors.EVENT_READ,name)
    home=directory/'home';home.mkdir()
    env=dict(os.environ,HOME=str(home),XDG_CONFIG_HOME=str(home),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software')
    command=[str(executable),'--data='+str(data),'--no-sound','--no-joystick','--no-xmas','--render-test='+mode,'--render-ticks='+str(ticks),'--render-assets='+str(pack),'--render-talon-bank=13','--render-local-blend','--render-known-explosion-blend','--render-scene=enemy-hit','--render-scene-assets=all','--render-no-capture']
    (directory/'command.json').write_text(json.dumps(command,indent=2)+'\n')
    start=time.monotonic()
    with (directory/'stdout.log').open('wb') as out,(directory/'stderr.log').open('wb') as err:
        process=subprocess.Popen(command,cwd=directory,env=env,stdout=out,stderr=err)
        while True:
            events=selector.select(.1)
            for key,_ in events:
                chunk=os.read(key.fd,1024*1024)
                if not chunk:continue
                record=records[key.data]
                record['sha'].update(chunk);record['bytes']+=len(chunk);record['lines']+=chunk.count(b'\n')
                if len(record['first'])<1024:record['first']=(record['first']+chunk)[:1024]
                if record['gzip']:record['gzip'].write(chunk)
            if process.poll() is not None and not events:break
            if time.monotonic()-start>180:
                process.kill();process.wait();raise RuntimeError('Runtime regression timed out')
    result={}
    for key in list(selector.get_map().values()):
        os.close(key.fd);selector.unregister(key.fd)
    selector.close()
    for name,record in records.items():
        if record['gzip']:record['gzip'].close()
        (directory/name).unlink()
        if record['bytes']:
            result[name]={'sha256':record['sha'].hexdigest(),'bytes':record['bytes'],'lines':record['lines']}
    if process.returncode:raise RuntimeError(f'{executable}: exited {process.returncode}; see {directory}/stderr.log')
    assert result['state.tsv']['lines']==ticks+1
    assert result['rgb-audit.tsv']['lines']==ticks+1
    assert not list(directory.glob('*.bmp'))
    result['executable_sha256']=hashlib.sha256(executable.read_bytes()).hexdigest()
    result['seconds']=round(time.monotonic()-start,3)
    (directory/'hashes.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('baseline','candidate','pack','data','output'):p.add_argument('--'+name,required=True,type=Path)
    p.add_argument('--ticks',type=int,default=120)
    args=p.parse_args()
    for name in ('baseline','candidate','pack','data','output'):setattr(args,name,getattr(args,name).resolve())
    assert not (args.pack/'gameplay-hud-v1.hda').exists(),'The selected pack must have no HUD resource'
    assert not args.output.exists(),'Use a new bounded output directory'
    results={}
    for mode in ('classic','8'):
        pair={}
        for variant in ('baseline','candidate'):
            pair[variant]=run(getattr(args,variant),mode,args.output/(mode+'-'+variant),args.pack,args.data,args.ticks)
        comparable=lambda r:{k:v for k,v in r.items() if k.endswith('.tsv')}
        assert comparable(pair['baseline'])==comparable(pair['candidate']),(mode,pair)
        results[mode]=pair
        print(mode+': identical full runtime TSV hashes, including original state/RNG/indexed output/collisions and rendered RGB',flush=True)
    assert results['classic']['candidate']['state.tsv']==results['8']['candidate']['state.tsv']
    assert results['classic']['candidate']['collisions.tsv']==results['8']['candidate']['collisions.tsv']
    (args.output/'summary.json').write_text(json.dumps({'ticks_per_run':args.ticks,'captures':0,'copied_pack_bytes':0,'results':results},indent=2)+'\n')
    print('PASS: four bounded runs; original gameplay is identical across C/H and before/after HUD hooks.')
if __name__=='__main__':main()
