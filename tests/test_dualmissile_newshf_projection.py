"""Current1 / exact private68 inverse, no old ledger repinning."""
import copy,json,subprocess,unittest
from pathlib import Path
from unittest.mock import patch
import dualmissile_newshf_projection as p
class DualProjection(unittest.TestCase):
 def test_exact_scope_no_git_or_original_data(self):
  with patch.object(subprocess,'Popen',side_effect=AssertionError('Git forbidden')):
   proof=p.verified();self.assertEqual(len(proof['mapping']),1);self.assertEqual(set(proof['added_sources']),p.ADDED)
   for name in p.FILES:
    current=(p.ROOT/name).read_bytes();old=p.project_source(name,current)
    self.assertEqual(p.sha(old),p.ledger()['files'][name]['previous_sha256'])
    self.assertEqual(p.project_if_current(name,old),old)
    for raw in (current+b'\n',old):
     with self.assertRaises(AssertionError):p.project_source(name,raw)
 def test_every_qualified_input_is_rechecked(self):
  read=Path.read_bytes
  for name in p.qualified_paths()-{p.LEDGER,'tests/dualmissile_newshf_projection.py'}:
   def mutated(path):
    raw=read(path);return raw+b'\n' if path==p.ROOT/name else raw
   with self.subTest(name=name),patch.object(Path,'read_bytes',mutated),self.assertRaises((AssertionError,ValueError,OSError)):p.verified()
 def test_stale_previous_live_source_never_qualifies(self):
  read=Path.read_bytes
  for name in p.FILES:
   old=p.project_source(name,read(p.ROOT/name))
   def stale(path):return old if path==p.ROOT/name else read(path)
   with self.subTest(name=name),patch.object(Path,'read_bytes',stale),self.assertRaises(AssertionError):p.verified()
 def test_nested_shapesy_four_added_inputs_are_rechecked(self):
  import shapesy_platform_projection as y
  read=Path.read_bytes
  for name in y.ADDED:
   def changed(path):
    raw=read(path);return raw+b'\n' if path==p.ROOT/name else raw
   with self.subTest(name=name),patch.object(Path,'read_bytes',changed),self.assertRaises((AssertionError,ValueError,OSError)):y.verified()
 def test_hunk_and_previous_pins_independent(self):
  for name in p.FILES:
   for field in ('before','after'):
    spec=copy.deepcopy(p.ledger());spec['files'][name]['hunks'][0][field]+='bad'
    with patch.object(p,'ledger',return_value=spec),self.assertRaises(AssertionError):p.project_source(name,(p.ROOT/name).read_bytes())
   spec=copy.deepcopy(p.ledger());spec['files'][name]['previous_sha256']='0'*64
   with patch.object(p,'ledger',return_value=spec),self.assertRaises(AssertionError):p.project_source(name,(p.ROOT/name).read_bytes())
 def test_undeclared_family_file_rejected(self):
  rglob=Path.rglob
  def extra(path,pattern):
   values=list(rglob(path,pattern))
   if path==p.ROOT/'authoring-inputs/newshf-dualmissile':values.append(path/'unreviewed.png')
   return iter(values)
  is_file=Path.is_file
  def fake(path):return path.name=='unreviewed.png' or is_file(path)
  with patch.object(Path,'rglob',extra),patch.object(Path,'is_file',fake),self.assertRaises(AssertionError):p.verified()
 def test_nested_projectile91_render_chain(self):
  import accepted_later_changes as a
  name='src/render_mirror.c'
  result=a.project_current_projectile91_source(name,(p.ROOT/name).read_bytes())
  self.assertEqual(p.sha(result),a.current_projectile91_ledger()['files'][name]['previous_sha256'])
 def test_projection_dispatch_orders(self):
  import linked_newshf_projection as l, shapesy_platform_projection as y
  import accepted_later_changes as a
  linked=set(l.ledger()['files']);yscope=y.FILES|y.ADDED
  self.assertFalse(linked & yscope)
  for name in sorted(linked|yscope|{'src/player.c'}):
   raw=(p.ROOT/name).read_bytes()
   with self.subTest(name=name):
    if name in linked:
     self.assertEqual(y.project_source(name,raw),raw)
     expected=l.project_source(name,raw)
     self.assertEqual(p.sha(expected),l.ledger()['files'][name]['previous_sha256'])
    elif name in yscope:
     self.assertEqual(l.project_source(name,raw),raw)
     expected=y.project_source(name,raw)
     if name in y.FILES:self.assertEqual(p.sha(expected),y.ledger()['files'][name]['previous_sha256'])
     else:self.assertEqual(expected,p.project_if_current(name,raw))
    else:expected=raw
    self.assertEqual(l.project_source(name,y.project_source(name,raw)),expected)
    self.assertEqual(y.project_source(name,l.project_source(name,raw)),expected)
    chain=a.project_current_projectile91_source(name,raw)
    pin=a.current_projectile91_ledger()['files'].get(name)
    if pin:self.assertEqual(p.sha(chain),pin['previous_sha256'])
    else:self.assertEqual(chain,expected)
  # The two formerly failing real call orders are covered above, not emulated
  # by accepting arbitrary older bytes at a projection's owned paths.
  for module,names in ((l,linked),(y,y.FILES)):
   for name in names:
    with self.subTest(module=module.__name__,name=name),self.assertRaises(AssertionError):
     module.project_source(name,(p.ROOT/name).read_bytes()+b'\n')
 def test_new_module_and_ledger_are_cache_dependencies(self):
  import _projection_proof_context as guarded
  for family in ('dualmissile_newshf','protron'):
   context=guarded._ProjectionProofContext(p.ROOT,p.ROOT);self.addCleanup(context.close)
   deps=context._discover(family)
   self.assertTrue({p.ROOT/n for n in p.qualified_paths()} <= set(deps.files))
   context.get(family,lambda root:{'unit_cache_proof':True})
   stamp=guarded._repo_stamp;target=p.ROOT/'tests/dualmissile_newshf_projection.py'
   def drift(path):
    result=stamp(path);return result+('unit-module-byte-drift',) if path==target else result
   with patch.object(guarded,'_repo_stamp',drift),self.assertRaisesRegex(ValueError,'dependency'):
    context.get(family,lambda root:self.fail('Changed dependency must not reuse cached proof'))
 def test_actual_inventory_and_identity_entrypoints(self):
  import linked_newshf_projection as l, shapesy_platform_projection as y
  import accepted_later_changes as a
  from verify_current_production import source_inventory
  self.assertEqual(a.verified_newshf_identity_sources(),a.load('newshf-identity-source.json')['added_sources'])
  for name in y.ADDED:
   self.assertEqual(y.checked_read(p.ROOT,name),p.project_if_current(name,(p.ROOT/name).read_bytes()))
  before_y=y.before_inventory(source_inventory(p.ROOT))
  self.assertEqual(before_y,y.ledger()['public_source_inventory'])
  expected=dict(before_y)
  for name in l.ledger()['added_sources']:expected.pop(name)
  for name,pin in l.ledger()['files'].items():expected[name]=pin['previous_sha256']
  self.assertEqual(l.before_inventory(before_y),expected)
  rows=json.loads((p.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files']
  result=a.before_current_projectile91_runtime(rows)
  self.assertEqual(len(result),1029)
 def test_complete_source_and_runtime_inverse(self):
  import sys;sys.path.insert(0,str(p.ROOT/'scripts'))
  from verify_current_production import source_inventory
  current=source_inventory(p.ROOT);old=p.before_inventory(current)
  self.assertEqual(old,p.ledger()['base_source_inventory'])
  for name in p.ADDED|p.FILES:
   bad=dict(current);bad[name]='0'*64
   with self.assertRaises((AssertionError,KeyError)):p.before_inventory(bad)
  rows=json.loads((p.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files'];mapping=p.verified()['mapping'];old=p.before_runtime(rows)
  self.assertEqual(old,[r for r in rows if r['destination'] not in mapping])
  for kind in ('missing','duplicate','changed'):
   bad=copy.deepcopy(rows);row=next(r for r in bad if r['destination'] in mapping)
   if kind=='missing':bad.remove(row)
   elif kind=='duplicate':bad.append(row)
   else:row['group']='wrong'
   with self.assertRaises(AssertionError):p.before_runtime(bad)
if __name__=='__main__':unittest.main()
