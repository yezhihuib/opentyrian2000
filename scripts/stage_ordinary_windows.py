#!/usr/bin/env python3
"""Create a NEW isolated MSVC source stage. Never compile, launch or alter checkout.
No dependency download/installation. User must supply existing Windows x64 dependencies.
"""
import argparse,ast,hashlib,json,shutil,sys,xml.etree.ElementTree as ET
from pathlib import Path,PureWindowsPath
ROOT=Path(__file__).resolve().parents[1]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def stage(repo,destination,sdl2,sdl_net,sdk='10.0.26100.0',toolset='v143'):
 repo=Path(repo).resolve();dest=Path(destination).resolve()
 if dest.exists() or dest==repo or repo in dest.parents:raise ValueError('Use a new directory outside the checkout')
 for root in (sdl2,sdl_net):
  w=PureWindowsPath(root)
  if not w.is_absolute() or any(c in root for c in ('\r','\n',';','$','%')):raise ValueError('Supply an explicit absolute Windows dependency path')
 if not all(c.isdigit() or c=='.' for c in sdk) or toolset!='v143':raise ValueError('Unreviewed SDK/toolset')
 validation_raw=(repo/'packaging/current-production-validation.json').read_bytes()
 validation=json.loads(validation_raw)
 pins=validation['source_sha256']
 if len(pins)!=339:raise ValueError('Expected 339 exact canonical source pins')
 actual={f.relative_to(repo).as_posix() for f in (repo/'src').rglob('*') if f.is_file()}
 if actual!=set(pins):raise ValueError('Canonical source set differs from production binding')
 files={};origins={}
 for name,expected in pins.items():
  path=repo/name
  if not name.startswith('src/') or '..' in Path(name).parts or any(p.is_symlink() for p in (path,)+tuple(path.parents)):raise ValueError('Unsafe source path')
  raw=path.read_bytes()
  if digest(raw)!=expected:raise ValueError('Changed canonical source: '+name)
  files[name]=raw;origins[name[4:]]=name
 for name,expected in validation['build_input_sha256'].items():
  if digest((repo/name).read_bytes())!=expected:raise ValueError('Changed bound build input: '+name)
 units=sorted(x for x in origins if x.endswith('.c') and '/' not in x)
 if len(units)!=86:raise ValueError('Require canonical86 units, never family overlay')
 files['CURRENT-PRODUCTION-VALIDATION.json']=validation_raw
 for name in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h'):
  path='assets/hd/shared-menu-runs-v1/'+name;files[path]=(repo/path).read_bytes()
 for name in ('resources.rc','tyrian2000.ico'):files['visualc/'+name]=(repo/'visualc'/name).read_bytes()
 files['build_ordinary_windows.ps1']=(repo/'scripts/build_ordinary_windows.ps1').read_bytes()
 defs=['TARGET_WIN32',r'TYRIAN_DIR="C:\\TYRIAN"','WITH_NETWORK','_CRT_SECURE_NO_WARNINGS','_WINDOWS','NDEBUG','OPENTYRIAN_VERSION="ordinary-production-windows-candidate"']
 ns='http://schemas.microsoft.com/developer/msbuild/2003';ET.register_namespace('',ns)
 def e(parent,tag,text=None,**attrs):
  x=ET.SubElement(parent,'{'+ns+'}'+tag,attrs)
  if text is not None:x.text=text
  return x
 project=ET.Element('{'+ns+'}Project',DefaultTargets='Build',ToolsVersion='Current')
 configs=e(project,'ItemGroup',Label='ProjectConfigurations');cfg=e(configs,'ProjectConfiguration',Include='Release|x64');e(cfg,'Configuration','Release');e(cfg,'Platform','x64')
 g=e(project,'PropertyGroup',Label='Globals');e(g,'ImportDirectoryBuildProps','false');e(g,'ImportDirectoryBuildTargets','false');e(g,'ProjectGuid','{F795F3E7-BD51-4DD6-AFC1-79F6E8AA5886}');e(g,'Keyword','Win32Proj');e(g,'WindowsTargetPlatformVersion',sdk)
 e(project,'Import',Project='$(VCTargetsPath)\\Microsoft.Cpp.Default.props')
 g=e(project,'PropertyGroup',Label='Configuration');e(g,'ConfigurationType','Application');e(g,'PlatformToolset',toolset);e(g,'UseDebugLibraries','false');e(g,'CharacterSet','MultiByte')
 e(project,'Import',Project='$(VCTargetsPath)\\Microsoft.Cpp.props')
 g=e(project,'PropertyGroup');e(g,'OutDir','$(MSBuildProjectDirectory)\\bin\\');e(g,'IntDir','$(MSBuildProjectDirectory)\\obj\\');e(g,'TargetName','opentyrian2000-ordinary');e(g,'SDL2BaseDir',sdl2);e(g,'SDL2netBaseDir',sdl_net)
 g=e(project,'ItemDefinitionGroup');cc=e(g,'ClCompile');e(cc,'LanguageStandard_C','stdc17');e(cc,'CompileAs','CompileAsC');e(cc,'WarningLevel','Level3');e(cc,'Optimization','MaxSpeed');e(cc,'RuntimeLibrary','MultiThreadedDLL');e(cc,'PreprocessorDefinitions',';'.join(defs));e(cc,'AdditionalIncludeDirectories','$(MSBuildProjectDirectory)\\src;$(MSBuildProjectDirectory)\\assets;$(SDL2BaseDir)\\include;$(SDL2netBaseDir)\\include')
 e(cc,'AdditionalOptions','/source-charset:utf-8 %(AdditionalOptions)')
 rc=e(g,'ResourceCompile');e(rc,'AdditionalIncludeDirectories','$(MSBuildProjectDirectory)\\visualc')
 link=e(g,'Link');e(link,'SubSystem','Windows');e(link,'TargetMachine','MachineX64');e(link,'AdditionalLibraryDirectories','$(SDL2BaseDir)\\lib\\x64;$(SDL2netBaseDir)\\lib\\x64');e(link,'AdditionalDependencies','SDL2.lib;SDL2main.lib;SDL2_net.lib;user32.lib;gdi32.lib;winmm.lib;imm32.lib;ole32.lib;oleaut32.lib;version.lib;uuid.lib;advapi32.lib;shell32.lib;setupapi.lib;ws2_32.lib')
 group=e(project,'ItemGroup')
 for name in units:e(group,'ClCompile',Include='src\\'+name)
 e(e(project,'ItemGroup'),'ResourceCompile',Include='visualc\\resources.rc')
 e(project,'Import',Project='$(VCTargetsPath)\\Microsoft.Cpp.targets')
 files['ordinary-production.vcxproj']=ET.tostring(project,encoding='utf-8',xml_declaration=True)
 inputs={k:digest(v) for k,v in sorted(files.items())}
 receipt={'schema':1,'status':'STAGED_NOT_BUILT','translation_units':86,'build_flavor':'ordinary-production','production_validation_sha256':digest(validation_raw),'source_origins':origins,'inputs_sha256':inputs,'defines':defs,'sdk':sdk,'toolset':toolset,'dependencies':{'SDL2':sdl2,'SDL2_net':sdl_net,'SHA256':'No added crypto dependency in canonical production sources'},'source_digest':digest(json.dumps({x:digest(files['src/'+x]) for x in sorted(origins)},sort_keys=True).encode()),'build_started':False,'game_started':False,'repository_modified':False,'runtime_acceptance':False}
 # All source/XML validation complete before first write; no existing target reuse.
 dest.mkdir(parents=True,exist_ok=False)
 for name,raw in files.items():
  target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
  if digest(target.read_bytes())!=inputs[name]:raise OSError('Copy verification failed: '+name)
 (dest/'STAGE.json').write_text(json.dumps(receipt,indent=2)+'\n')
 return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True);p.add_argument('--sdl2',required=True);p.add_argument('--sdl-net',required=True);p.add_argument('--sdk',default='10.0.26100.0');a=p.parse_args()
 result=stage(a.repo,a.output,a.sdl2,a.sdl_net,a.sdk);print(json.dumps({'status':result['status'],'source_digest':result['source_digest'],'game_started':False},indent=2))
