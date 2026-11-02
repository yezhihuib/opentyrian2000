"""Read-only producer closure checks; never invokes load/generate/derive/build."""
import ast,importlib,json,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_current_tank_shell as builder
class TankAuthoringClosure(unittest.TestCase):
 def test_all_current_declared_producer_inputs_are_covered(self):
  selected=builder.selection(ROOT,(ROOT/builder.SELECTION).read_bytes())
  paths=builder.rebuild_input_paths(ROOT,selected)
  source=(ROOT/'scripts/rebuild_recovered_runtime_manifest.py').read_text()
  modules=sorted({n.module for n in ast.walk(ast.parse(source))if isinstance(n,ast.ImportFrom)and n.module and(ROOT/'scripts'/f'{n.module}.py').is_file()})
  # Existing fixed runtime/source/build inputs cover load-only modules; this
  # regression checks every declared independent producer input set.
  runtime=json.loads((ROOT/builder.RUNTIME).read_bytes())
  base=json.loads((ROOT/'packaging/runtime-assets-public63a89b3.json').read_bytes())
  available=paths|{r['source_path']for r in runtime['files']+base['files']}|set(builder.BUILD_INPUTS)|{p.relative_to(ROOT).as_posix()for p in(ROOT/'src').rglob('*')if p.is_file()}
  declared=[]
  for name in modules:
   text=(ROOT/'scripts'/f'{name}.py').read_text()
   if not any(isinstance(n,ast.FunctionDef)and n.name=='input_paths'for n in ast.parse(text).body):continue
   m=importlib.import_module(name)
   if name=='build_enemy_protron_p09':
    # Its helper invokes derive; enumerate its exact finite return instead.
    wanted={m.MASTER,m.HEADER}|{m.DIRECTORY+'/'+n for n in ('identity.json','recipe.json','source227.png','enemy-protron-p09-227-8.hda')}
   else:wanted=m.input_paths(ROOT)
   self.assertLessEqual(wanted,available,name);declared.append(name)
  self.assertIn('current_projectile_bolts745_compatibility',declared);self.assertIn('current_projectile_animated153_compatibility',declared)
  builder.validate_input_closure(ROOT,paths)
 def test_missing_set_and_symlink_are_rejected_before_children(self):
  with tempfile.TemporaryDirectory()as d:
   root=pathlib.Path(d);(root/'ok').write_bytes(b'ok');(root/'link').symlink_to(root/'ok')
   with mock.patch.object(builder.subprocess,'run',side_effect=AssertionError('No child permitted')):
    with self.assertRaises(ValueError)as error:builder.validate_input_closure(root,{'ok','missing-a','missing-b','link'})
   for name in ('missing-a','missing-b','link'):self.assertIn(name,str(error.exception))
 def test_actual_derive_prechecks_both_source_and_staged_tree(self):
  tree=ast.parse(pathlib.Path(builder.__file__).read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='derive')
  checks=[n for n in ast.walk(fn)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='validate_input_closure']
  self.assertEqual(len(checks),2)
  context=next(n for n in fn.body if isinstance(n,ast.With));self.assertLess(checks[0].lineno,context.lineno)
  children=[n for n in ast.walk(context)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='subprocess']
  self.assertTrue(children);self.assertLess(checks[1].lineno,min(n.lineno for n in children))
if __name__=='__main__':unittest.main()
