from pathlib import Path
import ast,hashlib,json,os,sys,unittest
HERE=Path(__file__).resolve().parent;ROOT=Path(os.environ.get('PROJECTILE145_TEST_ROOT',str(HERE.parent)));sys.path.insert(0,str(HERE))
import projectile145_fresh_native_validation as fresh
class Projectile145FreshAdapter(unittest.TestCase):
 def test_four_exact_modes(self):
  self.assertEqual(list(fresh.MODES),['default-off','hd-on','mirror-disabled','hd-on-asan-ubsan'])
  self.assertEqual(fresh.MODES['default-off'],'');self.assertIn('RENDER_MIRROR_DISABLED',fresh.MODES['mirror-disabled'])
 def test_all_project_sanitizer_flags_and_zero_old_objects(self):
  self.assertIn('-fsanitize=address,undefined',fresh.SAN);text=Path(fresh.__file__).read_text()
  self.assertIn("'reused_project_objects':0",text);self.assertIn("compilelog.count(' -c -o obj/')==86",text)
  self.assertIn("build=q/'hd-on-asan-ubsan-build'",text);self.assertIn("assert len(objects)==84",text)
  self.assertNotIn('borrowed_objects',text)
 def test_old107_generated_harness_is_unchanged(self):
  tree=ast.parse((ROOT/'tests/test_projectile91_global_runtime.py').read_text());node=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HARNESS' for t in x.targets));old=ast.literal_eval(node.value)
  self.assertEqual(hashlib.sha256(old.encode()).hexdigest(),'4edcb186f10a47b8d331b6ecaefe15f12c620d7967145f5f9cdbf93c0e76ce89')
  text=Path(fresh.__file__).read_text();self.assertIn("prior['generated_harness_sha256']",text);self.assertIn("stdout==prior['stdout']",text)
 def test_real_full_tree_and_source_closure_preconditions(self):
  text=Path(fresh.__file__).read_text()
  for x in ("x.startswith(b'S ')","len(source)==308","len(units)==86","prior['source_sha256']==source","inv(build/'src')==source","shutil.copytree(r/'src',build/'src')"):
   self.assertIn(x,text)
  self.assertNotIn('os.link(',text)
 def test_fixed_budget_serial_make_and_failure_retention(self):
  text=Path(fresh.__file__).read_text()
  for x in ('peak=256*1024**2','reserve=250*1024**2',"['make','-j2'",'free>=reserve and used<=peak',"status='FAIL_RETAINED'","report['final_allocated_bytes']+4096<=peak","report['free_after']>=reserve+4096","'FAIL_BUDGET_RETAINED'",'if blocks(q)>peak or shutil.disk_usage(q).free<reserve:'):
   self.assertIn(x,text)
 def test_external_library_and_leak_scope_honest(self):
  text=Path(fresh.__file__).read_text();self.assertIn('external SDL/system libraries native',text);self.assertIn('detect_leaks=0:halt_on_error=1',text);self.assertIn('No game loop or full gate claim.',text)
if __name__=='__main__':unittest.main()
