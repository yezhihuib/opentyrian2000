#!/usr/bin/env python3
"""Private HUD-only ownership probe. Requires a built Linux tree, external HUD1
resource and original runtime data. Never copies either; never creates captures.
Instrumentation is compiled into a temporary object, not production source.
"""
import argparse
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
from test_no_asset_runtime import ROOT, run
from test_renderer import extract


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('pack','data','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--ticks',type=int,default=60)
    args=parser.parse_args()
    args.pack=args.pack.resolve();args.data=args.data.resolve();args.output=args.output.resolve()
    assert not args.output.exists()
    assert sorted(p.name for p in args.pack.glob('*.hda'))==['gameplay-hud-v1.hda'], 'HUD-only package required'
    source=(ROOT/'src/render_mirror.c').read_text()
    original_source_sha=hashlib.sha256(source.encode()).hexdigest()
    source='#include <time.h>\nstatic unsigned long diag_calls,diag_sprites,diag_bytes;\nstatic clock_t diag_clocks;\n'+source
    runtime=extract(source,'hud_runtime_compatible')
    modified=runtime.replace('{\n','{\n clock_t diag_begin=clock();++diag_calls;\n',1)
    modified=modified.replace('return true;', 'do {diag_clocks+=clock()-diag_begin;return true;} while(0);')
    source=source.replace(runtime,modified)
    sprite=extract(source,'hud_sprite_decode')
    source=source.replace(sprite,sprite.replace('return true;', '++diag_sprites;diag_bytes+=s->size;return true;'))
    marker='active=false;ready=game_probe_density>1;'
    assert source.count(marker)==1
    probe=r'''
 {unsigned owners=0,different=0,bad=0;int d=game_probe_density;
  for(int y=0;y<200;y++)for(int x=0;x<320;x++)if(hud_output_owner[y*320+x]) {
   ++owners;Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x];
   for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
    const Uint8 *rgba=gameplay_hud_sample(x,y,sx,sy,d,index);
    Uint32 actual=((Uint32 *)((Uint8 *)output->pixels+(y*d+sy)*output->pitch))[x*d+sx];
    Uint32 expected_rgb=rgba?0xff000000u|((Uint32)rgba[0]<<16)|((Uint32)rgba[1]<<8)|rgba[2]:0;
    bad+=!rgba||actual!=expected_rgb;different+=actual!=palette_rgb(index);
   }
  }
  fprintf(stderr,"HUD_DIAG %u %u %u %u %lu %lu %lu %.9f\n",game_probe_tick,owners,different,bad,diag_calls,diag_sprites,diag_bytes,(double)diag_clocks/CLOCKS_PER_SEC);
 }
'''
    source=source.replace(marker,probe+marker)
    commands=subprocess.check_output(['make','-n','-B','opentyrian2000'],cwd=ROOT,text=True).splitlines()
    compile_cmd=next(shlex.split(c) for c in commands if ' -c -o obj/render_mirror.o ' in c)
    link_cmd=shlex.split(commands[-1])
    with tempfile.TemporaryDirectory(prefix='hud-runtime-instrument-') as temp:
        temp=Path(temp);instrument=temp/'render_mirror.c';instrument.write_text(source)
        obj=temp/'render_mirror.o';exe=temp/'hud-ownership-probe'
        compile_cmd=[str(obj) if p=='obj/render_mirror.o' else str(instrument) if p=='src/render_mirror.c' else p for p in compile_cmd]
        compile_cmd+=['-I'+str(ROOT/'src')]
        subprocess.run(compile_cmd,cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        link_cmd=[str(obj) if p=='obj/render_mirror.o' else str(exe) if p=='opentyrian2000' else p for p in link_cmd]
        subprocess.run(link_cmd,cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        empty=temp/'no-resource';empty.mkdir()
        base=run(exe,'8',args.output/'without-hud',empty,args.data,args.ticks)
        trial=run(exe,'8',args.output/'with-hud',args.pack,args.data,args.ticks)
    records=[]
    for line in (args.output/'with-hud/stderr.log').read_text().splitlines():
        if not line.startswith('HUD_DIAG '):continue
        values=line.split()[1:];record=dict(zip(('tick','owned_logical','different_subpixels','rgba_mismatches','guard_calls','decoded_sprites','decoded_bytes'),map(int,values[:7])))
        record['guard_cpu_seconds']=float(values[7]);records.append(record)
    assert len(records)==args.ticks and all(r['owned_logical']==6667 and r['different_subpixels']>0 and r['rgba_mismatches']==0 for r in records),records
    assert base['state.tsv']==trial['state.tsv'] and base['collisions.tsv']==trial['collisions.tsv']
    assert base['rgb-audit.tsv']!=trial['rgb-audit.tsv']
    frames=list(csv.DictReader(gzip.open(args.output/'with-hud/frames.tsv.gz','rt'),delimiter='\t'))
    assert all(r['hd_draws']=='0' and r['reason']=='hd-ordered' for r in frames)
    summary={'ticks':args.ticks,'captures':0,'copies_of_data_or_art':0,'source_sha256':original_source_sha,
      'resource_sha256':hashlib.sha256((args.pack/'gameplay-hud-v1.hda').read_bytes()).hexdigest(),
      'exact_generated_RGBA_every_owned_subpixel':True,'original_state_and_collision_streams_identical':True,
      'first':records[0],'last':records[-1],'no_hud':base,'hud':trial}
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('no_hud','hud')},indent=2))
    assert hashlib.sha256((ROOT/'src/render_mirror.c').read_bytes()).hexdigest()==original_source_sha

if __name__=='__main__':main()
