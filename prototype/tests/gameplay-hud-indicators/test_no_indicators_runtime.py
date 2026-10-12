#!/usr/bin/env python3
"""No-indicator regression against the accepted HUD1/HUC1 checkpoint; no captures/copies."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'gameplay-hud'))
from test_no_asset_runtime import run

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('baseline','candidate','pack','data','output'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--ticks',type=int,default=120);a=p.parse_args()
 for n in ('baseline','candidate','pack','data','output'):setattr(a,n,getattr(a,n).resolve())
 assert not a.output.exists() and not (a.pack/'gameplay-hud-indicators-v1.hda').exists()
 result={}
 for mode in ('classic','8'):
  pair={v:run(getattr(a,v),mode,a.output/(mode+'-'+v),a.pack,a.data,a.ticks) for v in ('baseline','candidate')}
  streams=lambda r:{k:v for k,v in r.items() if k.endswith('.tsv')}
  assert streams(pair['baseline'])==streams(pair['candidate']),(mode,pair)
  result[mode]=pair;print(mode+': exact accepted HUC1 baseline/candidate TSV and RGB match',flush=True)
 assert result['classic']['candidate']['state.tsv']==result['8']['candidate']['state.tsv']
 assert result['classic']['candidate']['collisions.tsv']==result['8']['candidate']['collisions.tsv']
 (a.output/'summary.json').write_text(json.dumps({'ticks_each':a.ticks,'captures':0,'asset_copies':0,'results':result},indent=2)+'\n')
if __name__=='__main__':main()
