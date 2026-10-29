"""Finite61 inverse, actual caller inventories and distinct91 live/stage hashes."""
import copy,json,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
import projectile61_projection as p
sys.path.insert(0,str(p.ROOT/'scripts'))
from verify_current_production import source_inventory
import current_projectile61_compatibility as c

class Projectile61Projection(unittest.TestCase):
 def test_one_producer_once_no_git_or_original_data(self):
  with patch.object(subprocess,'Popen',side_effect=AssertionError('Git forbidden')),patch.object(c,'load',wraps=c.load) as load:
   proof=p.verified()
  self.assertEqual(load.call_count,1)
  self.assertEqual(len(proof['mapping']),1);self.assertEqual(len(proof['assets']),3)
  self.assertEqual(set(proof['added_sources']),p.ADDED)
  self.assertEqual({q['identity'] for q in proof['mapping'].values()},{1510061})
 def test_exact_inverse_and_independent_hunk_preimage_checks(self):
  for name in p.FILES:
   raw=(p.ROOT/name).read_bytes();old=p.project_source(name,raw)
   self.assertEqual(p.sha(old),p.ledger()['files'][name]['previous_sha256'])
   self.assertEqual(p.project_if_current(name,old),old)
   for bad in (raw+b'\n',old):
    with self.subTest(name=name),self.assertRaises(AssertionError):p.project_source(name,bad)
   for field in ('before','after'):
    spec=copy.deepcopy(p.ledger());spec['files'][name]['hunks'][0][field]+='bad'
    with patch.object(p,'ledger',return_value=spec),self.assertRaises(AssertionError):p.project_source(name,raw)
   spec=copy.deepcopy(p.ledger());spec['files'][name]['previous_sha256']='0'*64
   with patch.object(p,'ledger',return_value=spec),self.assertRaises(AssertionError):p.project_source(name,raw)
  self.assertEqual(p.project_source('unowned',b'exact bytes'),b'exact bytes')
 def test_every_qualified_input_is_rechecked(self):
  read=Path.read_bytes
  for name in p.qualified_paths()-{p.LEDGER,'tests/projectile61_projection.py'}:
   def changed(path):return read(path)+(b'\n' if path==p.ROOT/name else b'')
   with self.subTest(name=name),patch.object(Path,'read_bytes',changed),self.assertRaises((AssertionError,ValueError,OSError)):p.verified()
 def test_stale_live_preimages_rejected(self):
  read=Path.read_bytes
  for name in p.FILES:
   previous=p.project_source(name,read(p.ROOT/name))
   def stale(path):return previous if path==p.ROOT/name else read(path)
   with self.subTest(name=name),patch.object(Path,'read_bytes',stale),self.assertRaises(AssertionError):p.verified()
 def test_input_and_output_directory_closures(self):
  rglob=Path.rglob;is_file=Path.is_file
  for directory in (c.INPUT_ROOT,c.ROOT):
   extra=p.ROOT/directory/'unapproved.bin'
   def paths(path,pattern):return iter(list(rglob(path,pattern))+([extra] if path==p.ROOT/directory else []))
   def regular(path):return path==extra or is_file(path)
   with self.subTest(directory=directory),patch.object(Path,'rglob',paths),patch.object(Path,'is_file',regular),self.assertRaises(AssertionError):p.verified()
 def test_live_whole_source_unknown_file_and_unrelated_drift(self):
  read=Path.read_bytes;rglob=Path.rglob;is_file=Path.is_file
  target=p.ROOT/'src/player.c'
  def drift(path):return read(path)+(b'\n' if path==target else b'')
  with patch.object(Path,'read_bytes',drift),self.assertRaises(AssertionError):p.verified()
  extra=p.ROOT/'src/unapproved-source.inc'
  def paths(path,pattern):return iter(list(rglob(path,pattern))+([extra] if path==p.ROOT/'src' else []))
  def regular(path):return path==extra or is_file(path)
  def content(path):return b'unapproved source' if path==extra else read(path)
  with patch.object(Path,'rglob',paths),patch.object(Path,'is_file',regular),patch.object(Path,'read_bytes',content),self.assertRaises(AssertionError):p.verified()
 def test_actual_caller_whole_inventory_and_exact308_stage(self):
  live=source_inventory(p.ROOT)
  self.assertEqual(len(live),310)
  old=p.before_inventory(live);self.assertEqual(old,p.ledger()['base_source_inventory']);self.assertEqual(len(old),308)
  for name in sorted(p.ADDED|p.SRC_FILES|{'src/player.c'}):
   for kind in ('missing','wrong'):
    bad=dict(live)
    if kind=='missing':bad.pop(name)
    else:bad[name]='0'*64
    with self.subTest(name=name,kind=kind),self.assertRaises((AssertionError,KeyError)):p.before_inventory(bad)
  bad=dict(live);bad['src/unknown.inc']='0'*64
  with self.assertRaises(AssertionError):p.before_inventory(bad)
 def test_one_complete_runtime_row_and_order(self):
  rows=json.loads((p.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files'];proof=p.verified();mapping=proof['mapping']
  self.assertEqual(p.before_runtime(rows),[r for r in rows if r['destination'] not in mapping])
  self.assertEqual(sum(r['destination'] in mapping for r in rows),1)
  for kind in ('missing','duplicate','destination','source_path','sha256','bytes','git_blob','group','revision','extra_field'):
   bad=copy.deepcopy(rows);row=next(r for r in bad if r['destination'] in mapping)
   if kind=='missing':bad.remove(row)
   elif kind=='duplicate':bad.append(row)
   elif kind=='bytes':row[kind]+=1
   else:row[kind]='wrong'
   with self.subTest(kind=kind),self.assertRaises(AssertionError):p.before_runtime(bad)
 def test_qualified145_exact_stage_bad_hash_missing_extra_reject(self):
  import projectile145_projection as prior
  live=source_inventory(p.ROOT)
  self.assertEqual(prior.before_inventory(live),prior.ledger()['base_source_inventory'])
  for kind in ('wrong','missing','extra'):
   bad=dict(live)
   if kind=='wrong':bad['src/player.c']='0'*64
   elif kind=='missing':bad.pop('src/player.c')
   else:bad['src/unknown.inc']='0'*64
   with self.subTest(kind=kind),self.assertRaises(AssertionError):prior.before_inventory(bad)
 def test_projectile91_historical_and_live_added_hashes_are_distinct(self):
  import accepted_later_changes as a
  proof=a.verified_current_projectile91(p.ROOT);name='src/global_projectile91_mirror.inc';raw=(p.ROOT/name).read_bytes()
  self.assertEqual(proof['added_sources'][name],p.sha(raw))
  self.assertEqual(proof['historical_added_sources'][name],a.current_projectile91_ledger()['added_sources'][name])
  import projectile145_projection as prior
  self.assertEqual(p.sha(prior.project_source(name,p.project_source(name,raw))),proof['historical_added_sources'][name])
  self.assertNotEqual(proof['added_sources'][name],proof['historical_added_sources'][name])
  spec=copy.deepcopy(a.current_projectile91_ledger());spec['added_sources'][name]='0'*64
  with patch.object(a,'current_projectile91_ledger',return_value=spec),self.assertRaises(AssertionError):a.verified_current_projectile91(p.ROOT)
  live=source_inventory(p.ROOT)
  for digest in ('0'*64,proof['historical_added_sources'][name]):
   bad=dict(live);bad[name]=digest
   with self.assertRaises((AssertionError,KeyError)):a.before_current_projectile91_inventory(bad,p.ROOT)
 def test_four_changed_sources_reach_old_projectile91_oracle(self):
  import accepted_later_changes as a
  for name in p.SRC_FILES:
   raw=(p.ROOT/name).read_bytes();old=p.project_source(name,raw)
   self.assertEqual(a.project_current_projectile91_source(name,raw),a.project_current_projectile91_source(name,old))
   with self.assertRaises(AssertionError):a.project_current_projectile91_source(name,raw+b'\n')
 def test_new_closure_is_old_and_new_context_dependency(self):
  import _projection_proof_context as guarded
  for family in ('projectile61','projectile145','shared170_bronze356','protron'):
   context=guarded._ProjectionProofContext(p.ROOT,p.ROOT);self.addCleanup(context.close);deps=context._discover(family)
   self.assertTrue({p.ROOT/n for n in p.qualified_paths()}<=set(deps.files))
   self.assertTrue({p.ROOT/c.INPUT_ROOT,p.ROOT/c.ROOT,p.ROOT/'src'}<=set(deps.directories))
   context.get(family,lambda root:{'unit':True})
   stamp=guarded._repo_stamp;target=p.ROOT/'scripts/current_projectile61_compatibility.py'
   def drift(path):
    value=stamp(path);return value+('unit-projectile61-drift',) if path==target else value
   with patch.object(guarded,'_repo_stamp',drift),self.assertRaisesRegex(ValueError,'dependency'):context.get(family,lambda root:self.fail('stale proof'))
if __name__=='__main__':unittest.main()
