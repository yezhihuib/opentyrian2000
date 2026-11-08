"""Offline real public-art checks with synthetic PE, never a game launch."""
import argparse,importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import windows_hd_runtime as hd
from test_windows_runtime import WindowsRuntimeTests

class WindowsHDRuntimeTests(unittest.TestCase):
 def inputs(self,base,public=False):
  a=WindowsRuntimeTests().inputs(base);a.hd=True;a.public_candidates=public;a.assets=str(ROOT)
  Path(a.exe).chmod(0o700)
  return a
 def prepared(self,base,public=False):
  a=self.inputs(base,public);a.prepare=True;r=hd.prepare(a)
  b=argparse.Namespace(root=a.output,trust_sha256=r['runtime_receipt_sha256'],hd=True,public_candidates=public,launch=False,observer_present=False)
  return a,b,r
 def test_explicit_optin_check_only_and_no_pollution(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=self.inputs(Path(tmp));cwd=os.getcwd();env=dict(os.environ)
   a.hd=False
   with self.assertRaisesRegex(ValueError,'Explicit --hd'):hd.prepare(a)
   a.hd=True;r=hd.prepare(a)
   self.assertEqual(r['status'],'CHECK_ONLY');self.assertEqual(r['mode'],'hd');self.assertFalse(Path(a.output).exists())
   self.assertEqual(cwd,os.getcwd());self.assertEqual(env,dict(os.environ))
 def test_exact_art_and_relative_terrain_rebased_controls(self):
  with tempfile.TemporaryDirectory() as tmp:
   a,b,r=self.prepared(Path(tmp));root,receipt,data,env=hd.verify(b)
   self.assertEqual(r['immutable_files'],91);self.assertEqual(set(receipt['files']),hd.exact_files())
   self.assertTrue((root/'assets/hd/current-terrain24/terrain-shapesz-340-8.hda').is_file())
   self.assertNotIn('NORMAL270_ENABLE',env);self.assertFalse((root/'tyrian1.lvl').exists())
   for key,value in env.items():
    if key.endswith('_ASSET_DIR') or key.startswith('BUILDING313_V6_PHASE'):self.assertTrue(Path(value).is_relative_to(root))
   with patch.object(hd.core.subprocess,'Popen') as process:result=hd.run(b);process.assert_not_called()
   self.assertFalse(result['game_started'])
   with self.assertRaisesRegex(ValueError,'Output must be new'):hd.prepare(a)
 def test_public_choice_observer_requirement_and_clean_environment(self):
  with tempfile.TemporaryDirectory() as tmp:
   a,b,r=self.prepared(Path(tmp),True);root,receipt,data,env=hd.verify(b)
   self.assertEqual(env['NORMAL270_ENABLE'],'1');self.assertEqual(env['FORK284_ENABLE'],'1')
   self.assertFalse(any('REDVENT' in k for k in env));self.assertNotIn('HOME',env)
   b.public_candidates=False
   with self.assertRaisesRegex(ValueError,'choice must match'):hd.verify(b)
   b.public_candidates=True;b.launch=True
   with patch.object(hd.core.subprocess,'Popen') as process:
    with self.assertRaisesRegex(ValueError,'person present'):hd.run(b)
    process.assert_not_called()
   windows=Path(tmp)/'Windows';windows.mkdir()
   inherited={'SystemRoot':str(windows),'sDl_VideoDriver':'dummy','NORMAL270_ENABLE':'evil','PATH':'evil'}
   clean=hd.core.child_environment(root,inherited);clean.update(env)
   self.assertNotIn('SDL_VIDEODRIVER',clean);self.assertEqual(clean['NORMAL270_ENABLE'],'1');self.assertNotIn('evil',clean['PATH'])
 def test_asset_tamper_unknown_file_and_receipt_tamper_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   a,b,r=self.prepared(Path(tmp));root=Path(a.output)
   name=next(iter(hd.pins()));asset=root/name;old=asset.read_bytes();asset.write_bytes(b'bad')
   with self.assertRaises(ValueError):hd.verify(b)
   asset.write_bytes(old);extra=root/'injected.dll';extra.write_bytes(b'bad')
   with self.assertRaisesRegex(ValueError,'Unexpected'):hd.verify(b)
   extra.unlink();b.trust_sha256='0'*64
   with self.assertRaisesRegex(ValueError,'SHA256'):hd.verify(b)
 def test_symlink_resource_rejected_before_writes(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=self.inputs(Path(tmp));alias=Path(tmp)/'alias'
   try:alias.symlink_to(ROOT,target_is_directory=True)
   except OSError:self.skipTest('No symlink permission')
   a.assets=str(alias);a.prepare=True
   with self.assertRaisesRegex(ValueError,'Symlink/reparse'):hd.prepare(a)
   self.assertFalse(Path(a.output).exists())
 def test_real_copied_cli_without_B_does_not_write_bytecode(self):
  import subprocess
  with tempfile.TemporaryDirectory() as tmp:
   a,b,r=self.prepared(Path(tmp));root=Path(a.output)
   before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
   env={k:v for k,v in os.environ.items() if k.upper() not in ('PYTHONDONTWRITEBYTECODE','PYTHONPYCACHEPREFIX','PYTHONPATH')}
   command=[sys.executable,str(root/'tools/windows_hd_runtime.py'),'run','--root',str(root),'--trust-sha256',b.trust_sha256,'--hd']
   result=subprocess.run(command,env=env,cwd=tmp,text=True,capture_output=True)
   self.assertEqual(result.returncode,0,result.stdout+result.stderr)
   self.assertEqual(json.loads(result.stdout)['status'],'CHECK_ONLY')
   self.assertFalse(any(root.rglob('__pycache__')))
   after={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
   self.assertEqual(before,after)
 def test_public_pins_and_metadata_are_independently_fixed(self):
  self.assertEqual(len(hd.pins()),81);self.assertEqual(sum(x['bytes'] for x in hd.pins().values()),15485064)
  self.assertEqual(hd.core.sha((ROOT/hd.FAMILY_MANIFEST).read_bytes()),hd.FAMILY_SHA)
  self.assertEqual(len(hd.exact_files()),91)
if __name__=='__main__':unittest.main()
