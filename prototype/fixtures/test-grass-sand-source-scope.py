"""Strict private candidate source-scope oracle against reviewed7c7 baseline.

The baseline file inventory is recorded as SHA256 values, not fetched over the
network. Exact reversal of only the finite grass/sand edits must recover the
baseline renderer. All other source and header files must be byte-identical.
No game, artwork, output capture, source mutation or publication is performed.
"""
import argparse, hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,default=HERE.parents[1])
p.add_argument('--report',type=Path)
a=p.parse_args()
baseline=json.loads((HERE/'grass-sand-baseline-sha256.json').read_text())
source={str(f.relative_to(a.source)):f.read_bytes() for f in sorted((a.source/'src').rglob('*')) if f.is_file()}
assert set(source)==set(baseline['files']), 'Source/header file inventory differs from baseline'
changed=[name for name,data in source.items() if hashlib.sha256(data).hexdigest()!=baseline['files'][name]]
assert changed==['src/render_mirror.c'], changed
s=source['src/render_mirror.c'].decode()
helper='''/* Finite low-grass/sand Layer1 family; neighboring forest remains original. */
static int grass_sand_slot(unsigned int id)
{
 static const unsigned int ids[9]={66,67,69,76,78,79,80,89,90};
 for(int i=0;i<9;i++)if(id==ids[i])return 312+i;
 return -1;
}
'''
changes=[('static Asset assets[321];','static Asset assets[312];'),
 ('terrain_sources[162];','terrain_sources[153];'),
 (helper,''),
 ('layer==1&&(grass_sand_slot(id)>=0||','layer==1&&('),
 ('terrain_source_count<162','terrain_source_count<153'),
 ('  int grass_slot=grass_sand_slot(id);\n',''),
 ('  if(slot<0)slot=grass_slot;\n',''),
 ('||purple_slot>=0||grass_slot>=0)&&!a','||purple_slot>=0)&&!a')]
for new,old in changes:
 assert s.count(new)==1,(new,s.count(new))
 s=s.replace(new,old)
assert hashlib.sha256(s.encode()).hexdigest()==baseline['files']['src/render_mirror.c'], 'Unexpected renderer changes outside finite grass/sand edits'
report={'status':'passed','baseline_commit':baseline['commit'],'source':str(a.source),'changed_source_files':changed,
 'source_and_header_files_checked':len(source),'byte_identical_files':len(source)-1,'exact_reversed_changes':len(changes),
 'baseline_renderer_sha256':baseline['files']['src/render_mirror.c'],
 'candidate_renderer_sha256':hashlib.sha256(source['src/render_mirror.c']).hexdigest(),
 'asset_capacity':321,'terrain_registry_capacity':162,'grass_sand_ids':[66,67,69,76,78,79,80,89,90],'grass_sand_slots':list(range(312,321)),
 'unchanged_contracts':['All original assets0..311 and entity mappings','Original tyrian2.c loader and backgrnd.c Layer1 NORMAL path','Original compositor, draw/blend/filter/shadow/pixel/ownership helpers','Original game-state, timeline, collision, movement and firing source'],
 'excluded':['Any grass runtime visibility claim','Any game run or capture','Canonical grass/sand art validation or visual acceptance'],
 'scope':'Exact source bytes and synthetic unit tests only. The known80 entering fragment at3099–3131 does not establish a whole grass/sand motif.'}
out=a.report or Path('grass-sand-source-scope.json');out.write_text(json.dumps(report,indent=2)+'\n')
print('PASS:',len(source),'source/header files;',len(source)-1,'byte-identical; only8 exact finite grass/sand edits. Report:',out)
