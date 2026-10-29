"""Exact private 89dde3ae aircraft169, owned-path inverses, immutable prior ledgers."""
import copy,json,subprocess,unittest
from pathlib import Path
from unittest.mock import patch
import aircraft169_newshf_projection as p
import shared170_bronze356_projection as shared
class Aircraft169Projection(unittest.TestCase):
 def test_exact_scope_no_git_or_original_data(self):
  with patch.object(subprocess,'Popen',side_effect=AssertionError('Git forbidden')):
   proof=p.verified();self.assertEqual(len(proof['mapping']),3);self.assertEqual(set(proof['added_sources']),p.ADDED)
   for name in p.FILES:
    current=p.checked_read(p.ROOT,name);old=p.project_source(name,current)
    self.assertEqual(p.sha(old),p.ledger()['files'][name]['previous_sha256'])
    self.assertEqual(p.project_if_current(name,old),old)
    for raw in (current+b'\n',old):
     with self.assertRaises(AssertionError):p.project_source(name,raw)
 def test_every_qualified_input_is_rechecked(self):
  read=Path.read_bytes
  for name in p.qualified_paths()-{p.LEDGER,'tests/aircraft169_newshf_projection.py','tests/shared170_bronze356_projection.py','tests/projectile145_projection.py','tests/projectile61_projection.py'}:
   def mutated(path):
    raw=read(path);return raw+b'\n' if path==p.ROOT/name else raw
   with self.subTest(name=name),patch.object(Path,'read_bytes',mutated),self.assertRaises((AssertionError,ValueError,OSError)):p.verified()
 def test_stale_previous_live_source_never_qualifies(self):
  read=Path.read_bytes
  for name in p.FILES:
   old=p.project_source(name,read(p.ROOT/name))
   def stale(path):return old if path==p.ROOT/name else read(path)
   with self.subTest(name=name),patch.object(Path,'read_bytes',stale),self.assertRaises(AssertionError):p.verified()
 def test_hunk_and_previous_pins_independent(self):
  for name in p.FILES:
   for field in ('before','after'):
    spec=copy.deepcopy(p.ledger());spec['files'][name]['hunks'][0][field]+='bad'
    with patch.object(p,'ledger',return_value=spec),self.assertRaises(AssertionError):p.project_source(name,p.checked_read(p.ROOT,name))
   spec=copy.deepcopy(p.ledger());spec['files'][name]['previous_sha256']='0'*64
   with patch.object(p,'ledger',return_value=spec),self.assertRaises(AssertionError):p.project_source(name,p.checked_read(p.ROOT,name))
 def test_undeclared_family_file_rejected(self):
  rglob=Path.rglob
  def extra(path,pattern):
   values=list(rglob(path,pattern))
   if path==p.ROOT/'authoring-inputs/newshf-aircraft169':values.append(path/'unreviewed.png')
   return iter(values)
  is_file=Path.is_file
  def fake(path):return path.name=='unreviewed.png' or is_file(path)
  with patch.object(Path,'rglob',extra),patch.object(Path,'is_file',fake),self.assertRaises(AssertionError):p.verified()
 def test_whole_source_membership_and_unrelated_bytes_rejected(self):
  # Newest proof rejects even source changes outside its edited four files.
  read=Path.read_bytes;target=p.ROOT/'src/player.c'
  def changed(path):return read(path)+(b'\n' if path==target else b'')
  with patch.object(Path,'read_bytes',changed),self.assertRaises(AssertionError):p.verified()
  rglob=Path.rglob;extra=p.ROOT/'src/unapproved-source.inc'
  def extra_file(path,pattern):return iter(list(rglob(path,pattern))+([extra] if path==p.ROOT/'src' else []))
  is_file=Path.is_file
  def fake(path):return path==extra or is_file(path)
  def content(path):return b'extraneous source' if path==extra else read(path)
  with patch.object(Path,'rglob',extra_file),patch.object(Path,'is_file',fake),patch.object(Path,'read_bytes',content),self.assertRaises(AssertionError):p.verified()
 def test_complete_source_and_runtime_inverse(self):
  import sys;sys.path.insert(0,str(p.ROOT/'scripts'))
  from verify_current_production import source_inventory
  current=source_inventory(p.ROOT);old=p.before_inventory(current)
  self.assertEqual(old,p.ledger()['base_source_inventory'])
  for name in p.ADDED|p.SRC_FILES:
   bad=dict(current);bad[name]='0'*64
   with self.assertRaises((AssertionError,KeyError)):p.before_inventory(bad)
  rows=json.loads((p.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files'];mapping=p.verified()['mapping'];old=p.before_runtime(rows)
  self.assertEqual(old,[r for r in shared.before_runtime(rows) if r['destination'] not in mapping])
  for kind in ('missing','duplicate','changed'):
   bad=copy.deepcopy(rows);row=next(r for r in bad if r['destination'] in mapping)
   if kind=='missing':bad.remove(row)
   elif kind=='duplicate':bad.append(row)
   else:row['group']='wrong'
   with self.assertRaises(AssertionError):p.before_runtime(bad)
 def test_legacy_inventory_removes_exact_scout_headers(self):
  import accepted_later_changes as a
  from verify_current_production import source_inventory
  current=source_inventory(p.ROOT)
  projected=a.before_current_newshf_inventory(current,p.ROOT)
  self.assertEqual(len(projected),268+len(a.verified_enemy_probe_sources(p.ROOT)))
  self.assertFalse(p.ADDED & set(projected))
  # The legacy route must reject a missing or stale added header, not merely
  # subtract two arbitrary entries to satisfy its historical source count.
  for name in p.ADDED:
   for missing in (False,True):
    bad=dict(current)
    if missing:bad.pop(name)
    else:bad[name]='0'*64
    with self.assertRaises((AssertionError,KeyError)):
     a.before_current_newshf_inventory(bad,p.ROOT)
 def test_prior_qualified_wrappers_restore_exactly(self):
  import dualmissile_newshf_projection as d, shapesy_platform_projection as y
  self.assertEqual(len(d.verified()['mapping']),1)
  self.assertEqual(len(y.verified()['mapping']),28)
  for name in set(d.ledger()['qualified'])&p.FILES:
   self.assertEqual(p.sha(d.checked_read(p.ROOT,name)),d.ledger()['qualified'][name])
 def test_actual_consumer_orders_and_cache_closure(self):
  from test_dualmissile_newshf_projection import DualProjection
  for name in ('test_projection_dispatch_orders','test_actual_inventory_and_identity_entrypoints'):
   case=DualProjection(name);getattr(case,name)()
  import _projection_proof_context as guarded
  for family in ('aircraft169_newshf','shapesy_cyan','turret_newshf','dualmissile_newshf','protron'):
   context=guarded._ProjectionProofContext(p.ROOT,p.ROOT);self.addCleanup(context.close)
   deps=context._discover(family)
   self.assertTrue({p.ROOT/n for n in p.qualified_paths()}<=set(deps.files))
   context.get(family,lambda root:{'unit_cache_proof':True})
   stamp=guarded._repo_stamp;target=p.ROOT/'tests/aircraft169_newshf_projection.py'
   def drift(path):
    value=stamp(path);return value+('unit-turret-drift',) if path==target else value
   with patch.object(guarded,'_repo_stamp',drift),self.assertRaisesRegex(ValueError,'dependency'):context.get(family,lambda root:self.fail('stale cache'))
 def test_new_family_directory_closure_is_cache_dependency(self):
  import _projection_proof_context as guarded
  for family in ('aircraft169_newshf','shapesy_cyan','turret_newshf','protron'):
   context=guarded._ProjectionProofContext(p.ROOT,p.ROOT);self.addCleanup(context.close)
   deps=context._discover(family)
   targets={p.ROOT/n for n in ('authoring-inputs/newshf-aircraft169','authoring-inputs/newshf-aircraft169/derived','assets/hd/current-compat/newshf-aircraft169','src')}
   self.assertTrue(targets<=set(deps.directories))
   context.get(family,lambda root:{'unit_cache_proof':True})
   stamp=guarded._directory_stamp;target=p.ROOT/'src'
   def drift(path):
    value=stamp(path);return value+('unit-new-file',) if path==target else value
   with patch.object(guarded,'_directory_stamp',drift),self.assertRaisesRegex(ValueError,'dependency'):context.get(family,lambda root:self.fail('stale directory closure'))
 def test_original_runtime_paths_restore_exactly(self):
  import interceptor166_newshf_projection as old
  for name in p.SRC_FILES:
   self.assertEqual(p.sha(p.project_source(name,p.checked_read(p.ROOT,name))),p.ledger()['base_source_inventory'][name])
  old.verified()
if __name__=='__main__':unittest.main()
