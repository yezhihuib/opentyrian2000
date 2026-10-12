#!/usr/bin/env python3
"""Read-only Visual Studio source-list checks; this does not compile Windows."""
from pathlib import Path
import argparse,json,xml.etree.ElementTree as ET

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
a=p.parse_args();repo=a.repo.resolve();project=repo/'visualc/opentyrian.vcxproj'
ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'}
tree=ET.parse(project)
def entries(kind):
    names=[e.attrib['Include'] for e in tree.findall('.//m:'+kind,ns) if 'Include' in e.attrib]
    assert len(names)==len(set(names)), 'Duplicate '+kind+' entry'
    paths=[(project.parent/Path(n.replace('\\','/'))).resolve() for n in names]
    assert len(paths)==len(set(paths)), 'Duplicate resolved '+kind+' path'
    assert all(x.is_file() and repo in x.parents for x in paths), 'Missing/outside project file'
    return names,paths
names,sources=entries('ClCompile');_,headers=entries('ClInclude')
_,resources=entries('ResourceCompile')
expected=set((repo/'src').glob('*.c'))
assert set(sources)==expected, 'C source list differs from current src/*.c inventory'
materials=['ground101_material','world_material','world_material_fast','plateau_cap_material','forest13_material']
for name in materials:
    assert repo/'src'/(name+'.c') in sources
    assert repo/'src'/(name+'.h') in headers
for name in ['ground101_bundle_index.h','plateau_cap_bundle_index.h','forest13_bundle_index.h']:
    assert repo/'src'/name in headers
assert 'visualc\\opentyrian.sln' in (repo/'prototype/build-game.ps1').read_text()
assert 'opentyrian.vcxproj' in (repo/'visualc/opentyrian.sln').read_text()
assert tree.find('.//m:LanguageStandard_C',ns).text=='stdc17'
print(json.dumps({'status':'passed','C_sources':len(sources),'listed_headers':len(headers),'resources':len(resources),
 'material_modules':materials,'all_current_C_sources_listed_once':True,
 'scope':'Project XML, paths and source inventory only; no Windows compilation or runtime claim'},indent=2))
