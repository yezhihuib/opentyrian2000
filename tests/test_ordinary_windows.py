"""Ordinary canonical stage and offline runtime contract. No game process."""
import argparse,importlib.util,json,os,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import stage_ordinary_windows as stage
import windows_ordinary_runtime as runtime
import test_windows_runtime as fixtures

class OrdinaryWindowsTests(unittest.TestCase):
 def test_exact_canonical_source_project_and_flavor(self):
  with tempfile.TemporaryDirectory() as tmp:
   dest=Path(tmp)/'build';r=stage.stage(ROOT,dest,r'C:\deps\SDL2',r'C:\deps\SDL2_net')
   self.assertEqual(r['translation_units'],86);self.assertEqual(len(r['source_origins']),339)
   self.assertEqual(r['build_flavor'],'ordinary-production')
   text=(dest/'ordinary-production.vcxproj').read_text()
   self.assertEqual(text.count('<ClCompile Include='),86)
   self.assertIn('opentyrian2000-ordinary',text);self.assertIn('TYRIAN_DIR="C:\\\\TYRIAN"',text)
   for bad in ['experimental/','BUILDING313_FAMILY_CANVAS_ENABLE','CopyPropsTemplates','user.props','bcrypt.lib']:self.assertNotIn(bad,text)
   for name,source in r['source_origins'].items():self.assertEqual((dest/'src'/name).read_bytes(),(ROOT/source).read_bytes())
   with self.assertRaises(ValueError):stage.stage(ROOT,dest,r'C:\deps\SDL2',r'C:\deps\SDL2_net')
 def inputs(self,base):
  a=fixtures.WindowsRuntimeTests().inputs(base);a.hd=True;a.assets=str(base/'package')
  for file in ('stage_receipt','build_receipt'):
   path=Path(getattr(a,file));d=json.loads(path.read_text());d.update(translation_units=86,build_flavor='ordinary-production',production_validation_sha256=runtime.VALIDATION_SHA)
   if file=='build_receipt':d['stage_sha256']=a.stage_sha256
   path.write_text(json.dumps(d));setattr(a,('stage' if file=='stage_receipt' else 'build')+'_sha256',fixtures.h(path.read_bytes()))
  package=Path(a.assets);package.mkdir()
  for item in json.loads((ROOT/'packaging/runtime-assets-v1.json').read_text())['files']:
   target=package/item['destination'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/item['source_path'],target)
  return a
 def test_ordinary_prepare_and_normal_CLI_read_only(self):
  import subprocess
  with tempfile.TemporaryDirectory() as tmp:
   a=self.inputs(Path(tmp));result=runtime.prepare(a);self.assertEqual(result['status'],'CHECK_ONLY');self.assertFalse(Path(a.output).exists())
   a.prepare=True;result=runtime.prepare(a);root=Path(a.output)
   b=argparse.Namespace(root=a.output,trust_sha256=result['runtime_receipt_sha256'],hd=True,launch=False,observer_present=False)
   checked=runtime.run(b);self.assertEqual(len(checked['argv']),10);self.assertEqual(checked['cwd'],str(root))
   self.assertIn('--startup-assets='+str(root/'assets/startup'),checked['argv'])
   self.assertEqual((root/'opentyrian.cfg').read_bytes(),runtime.CONFIG)
   self.assertFalse((root/'tyrian1.lvl').exists())
   env={k:v for k,v in os.environ.items() if k.upper() not in ('PYTHONDONTWRITEBYTECODE','PYTHONPYCACHEPREFIX','PYTHONPATH')}
   command=[sys.executable,str(root/'tools/windows_ordinary_runtime.py'),'run','--root',str(root),'--trust-sha256',b.trust_sha256,'--hd']
   p=subprocess.run(command,env=env,text=True,capture_output=True);self.assertEqual(p.returncode,0,p.stderr)
   self.assertFalse(any(root.rglob('__pycache__')))
   with self.assertRaises(ValueError):runtime.prepare(a)
   b.launch=True
   with patch.object(runtime.core.subprocess,'Popen') as proc:
    with self.assertRaisesRegex(ValueError,'person must be present'):runtime.run(b)
    proc.assert_not_called()
   extra=root/'foreign.dll';extra.write_bytes(b'bad')
   with self.assertRaisesRegex(ValueError,'Unexpected'):runtime.verify(b)
 def test_family_stage_and_candidates_rejected_without_output(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=fixtures.WindowsRuntimeTests().inputs(Path(tmp));a.hd=True;a.assets=str(ROOT)
   with self.assertRaisesRegex(ValueError,'Unsupported source stage'):runtime.prepare(a)
   a.public_candidates=True
   with self.assertRaisesRegex(ValueError,'cannot be combined'):runtime.prepare(a)
   self.assertFalse(Path(a.output).exists())
 def test_runtime_manifest_exact_destinations_and_ordinary_args(self):
  resources=runtime.resources();self.assertEqual(len(resources),1163)
  self.assertEqual(sum(x['bytes'] for x in resources.values()),166516707)
  self.assertEqual(len(runtime.arguments(Path('/example'))),8)
  self.assertEqual(len(runtime.exact_files()),1172)
  build=(ROOT/'scripts/build_ordinary_windows.ps1').read_text()
  for text in ['translation_units=86',"build_flavor='ordinary-production'",'production_validation_sha256','/noAutoResponse','ImportDirectoryBuildProps=false']:
   self.assertIn(text,build)
if __name__=='__main__':unittest.main()
