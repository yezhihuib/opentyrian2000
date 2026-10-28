"""Combined170/356 exact preimage, two producer closures and all-row rejection."""
import copy,json,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
import shared170_bronze356_projection as p
sys.path.insert(0,str(p.ROOT/'scripts'))
from verify_current_production import source_inventory
import current_aircraft170_newshf_compatibility as aircraft
import current_shapesy_bronze356_compatibility as bronze

class Shared170Bronze356Projection(unittest.TestCase):
 def test_two_producers_once_no_git_or_original_data(self):
  with patch.object(subprocess,'Popen',side_effect=AssertionError('Git forbidden')),patch.object(aircraft,'load',wraps=aircraft.load) as a,patch.object(bronze,'load',wraps=bronze.load) as b:
   proof=p.verified()
  self.assertEqual((a.call_count,b.call_count),(1,1))
  self.assertEqual(len(proof['mapping']),4);self.assertEqual(len(proof['assets']),6)
  self.assertEqual(set(proof['added_sources']),p.ADDED)
  self.assertEqual({q['identity'] for q in proof['mapping'].values()},{2100040,2100041,2100042,2020356})
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
  for name in p.qualified_paths()-{p.LEDGER,'tests/shared170_bronze356_projection.py'}:
   def changed(path):return read(path)+(b'\n' if path==p.ROOT/name else b'')
   with self.subTest(name=name),patch.object(Path,'read_bytes',changed),self.assertRaises((AssertionError,ValueError,OSError)):p.verified()
 def test_stale_live_preimages_rejected(self):
  read=Path.read_bytes
  for name in p.FILES:
   previous=p.project_source(name,read(p.ROOT/name))
   def stale(path):return previous if path==p.ROOT/name else read(path)
   with self.subTest(name=name),patch.object(Path,'read_bytes',stale),self.assertRaises(AssertionError):p.verified()
 def test_both_input_directory_closures(self):
  rglob=Path.rglob;is_file=Path.is_file
  for directory in (aircraft.INPUT_ROOT,aircraft.ROOT,bronze.INPUT_ROOT,bronze.ROOT):
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
 def test_actual_caller_whole_inventory_and_exact35de_stage(self):
  live=source_inventory(p.ROOT)
  self.assertEqual(p.before_inventory(live),p.ledger()['base_source_inventory'])
  for name in sorted(p.ADDED|p.SRC_FILES|{'src/player.c'}):
   for kind in ('missing','wrong'):
    bad=dict(live)
    if kind=='missing':bad.pop(name)
    else:bad[name]='0'*64
    with self.subTest(name=name,kind=kind),self.assertRaises((AssertionError,KeyError)):p.before_inventory(bad)
  bad=dict(live);bad['src/unknown.inc']='0'*64
  with self.assertRaises(AssertionError):p.before_inventory(bad)
 def test_four_complete_runtime_rows_and_order(self):
  rows=json.loads((p.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files'];proof=p.verified();mapping=proof['mapping']
  self.assertEqual(p.before_runtime(rows),[r for r in rows if r['destination'] not in mapping])
  self.assertEqual(sum(r['destination'] in mapping for r in rows),4)
  for dest in mapping:
   for kind in ('missing','duplicate','source_path','sha256','bytes','git_blob','group','revision','extra_field'):
    bad=copy.deepcopy(rows);row=next(r for r in bad if r['destination']==dest)
    if kind=='missing':bad.remove(row)
    elif kind=='duplicate':bad.append(row)
    elif kind=='bytes':row[kind]+=1
    else:row[kind]='wrong'
    with self.subTest(destination=dest,kind=kind),self.assertRaises(AssertionError):p.before_runtime(bad)
 def test_aircraft169_exact_stage_preserved(self):
  import aircraft169_newshf_projection as prior
  live=source_inventory(p.ROOT)
  self.assertEqual(prior.before_inventory(live),prior.ledger()['base_source_inventory'])
  for name in p.FILES & prior.FILES:
   self.assertEqual(prior.sha(prior.checked_read(p.ROOT,name)),prior.ledger()['files'][name]['current_sha256'])
  for name in ('tests/current_aircraft169_newshf_source_projection.json','tests/current_interceptor166_newshf_source_projection.json'):
   self.assertEqual(p.project_source(name,(p.ROOT/name).read_bytes()),(p.ROOT/name).read_bytes())
 def test_both_closures_are_old_and_new_context_dependencies(self):
  import _projection_proof_context as guarded
  for family in ('shared170_bronze356','aircraft169_newshf','protron'):
   context=guarded._ProjectionProofContext(p.ROOT,p.ROOT);self.addCleanup(context.close);deps=context._discover(family)
   self.assertTrue({p.ROOT/n for n in p.qualified_paths()}<=set(deps.files))
   self.assertTrue({p.ROOT/aircraft.INPUT_ROOT,p.ROOT/bronze.INPUT_ROOT,p.ROOT/'src'}<=set(deps.directories))
   context.get(family,lambda root:{'unit':True})
   stamp=guarded._repo_stamp;target=p.ROOT/'scripts/current_shapesy_bronze356_compatibility.py'
   def drift(path):
    value=stamp(path);return value+('unit-combined-drift',) if path==target else value
   with patch.object(guarded,'_repo_stamp',drift),self.assertRaisesRegex(ValueError,'dependency'):context.get(family,lambda root:self.fail('stale proof'))
if __name__=='__main__':unittest.main()
