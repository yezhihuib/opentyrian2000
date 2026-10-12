"""Retain a bounded proof of a new blend TSV stream, without saving its raw rows.
Accepts an existing regular baseline TSV or a FIFO opened by the unchanged game.
Never deletes inputs; output must be new. Original indexed columns are separate
from HD ownership/composited-color fields that may intentionally change with art.
"""
from pathlib import Path
import argparse,hashlib,json,os,stat
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists() or a.output.is_symlink():p.error('Output must be new')
expected=b'tick\tknown_sheet\tindex\torigin_x\torigin_y\tx\ty\tbefore\tsource\tafter\thd_subpixels_before\trestored_blocks\trgba'
raw=hashlib.sha256();indexed=hashlib.sha256();count=size=0;ticks={}
with a.input.open('rb') as f:
 h=f.readline();assert h.rstrip(b'\r\n')==expected;raw.update(h);size+=len(h);ih=b'\t'.join(expected.split(b'\t')[:10])+b'\n';indexed.update(ih)
 for line in f:
  raw.update(line);size+=len(line);cols=line.rstrip(b'\r\n').split(b'\t');assert len(cols)==13;tick=int(cols[0]);norm=b'\t'.join(cols[:10])+b'\n';indexed.update(norm);count+=1
  if tick not in ticks:ticks[tick]={'rows':0,'indexed':hashlib.sha256(),'hd_owned_rows':0,'restored_blocks_sum':0}
  t=ticks[tick];t['rows']+=1;t['indexed'].update(norm);t['hd_owned_rows']+=int(int(cols[10])>0);t['restored_blocks_sum']+=int(cols[11])
j={'status':'passed','input_kind':'fifo' if stat.S_ISFIFO(a.input.stat().st_mode) else 'retained regular baseline','raw_bytes':size,'raw_rows':count,'raw_sha256':raw.hexdigest(),'original_columns':expected.decode().split('\t')[:10],'original_normalized_sha256':indexed.hexdigest(),'tick_proofs':[{**{k:v for k,v in t.items() if k!='indexed'},'tick':tick,'original_normalized_sha256':t['indexed'].hexdigest()} for tick,t in sorted(ticks.items())],'retained_raw_copy':False,'deleted_inputs':False}
with a.output.open('x') as f:json.dump(j,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in j.items() if k!='tick_proofs'}))
