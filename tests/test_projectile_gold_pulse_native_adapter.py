"""Current-root pure source/fixture/schema contracts; no compiler/native/historical build reads."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,re,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'tests/projectile_gold_pulse_native_validation.py';spec=importlib.util.spec_from_file_location('gold_portable_helper',p);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
class GoldNativeAdapter(unittest.TestCase):
 def stdout(self):
  rows=[]
  for name,n in h.GROUPS:
   if name=='Talon_transfer':
    for i in h.GOLD:
     c,s,z=h.TRANSFER[i]
     for cached in (0,1):rows.append(f'GOLD_TO_TALON selector={i} copied={c} soft={s} alpha0={z} cached={cached}')
   rows.append(f'GOLD_GROUP name={name} cases={n}')
  return '\n'.join(rows+['PASS gold pulse native lifecycle: 251 cases 38046959 assertions; internal8 only; not gameplay/full build'])+'\n'
 def test_01_exact15_groups251(self):self.assertEqual([n for _,n in h.GROUPS],[4,18,26,16,32,4,6,8,40,64,8,10,4,5,6]);self.assertEqual(sum(n for _,n in h.GROUPS),251)
 def test_02_valid_single_schema(self):self.assertEqual(h.parse_gold_stdout(self.stdout())['cases'],251)
 def test_03_wrong_count_assertions_or_extra_rejected(self):
  for bad in [self.stdout().replace('251 cases','250 cases'),self.stdout().replace('38046959 assertions','0 assertions'),self.stdout()+'EXTRA\n',self.stdout().replace('name=bounds cases=18','name=bounds cases=19')]:
   with self.assertRaises(AssertionError):h.parse_gold_stdout(bad)
 def test_04_missing_duplicate_or_wrong_name_rejected(self):
  row='GOLD_GROUP name=bounds cases=18\n'
  for bad in [self.stdout().replace(row,''),self.stdout().replace(row,row+row),self.stdout().replace('name=bounds','name=clip_wrap_and_empty_visible')]:
   with self.assertRaises(AssertionError):h.parse_gold_stdout(bad)
 def test_05_fixed_transfer_974735_plus_alpha0(self):
  self.assertEqual(h.TRANSFER,{168:(974,974,86),169:(735,735,85)})
  for a,b in [('copied=974','copied=0'),('soft=735','soft=734'),('alpha0=86','alpha0=85'),('cached=1','cached=0')]:
   with self.assertRaises(AssertionError):h.parse_gold_stdout(self.stdout().replace(a,b))
  with self.assertRaises(AssertionError):h.parse_gold_stdout(self.stdout(),{168:(931,931,86),169:(697,697,85)})
 def test_06_actual_C_byte_exact_and_print_schema(self):
  p=ROOT/'tests/projectile_gold_pulse_native_additions.c.inc';self.assertEqual(h.SHA(p.read_bytes()),h.GOLD_COMPANION_SHA)
  s=p.read_text();self.assertEqual(tuple((n,int(c)) for n,c in re.findall(r'gold_group\("([^\"]+)",b,(\d+)\)',s)),h.GROUPS)
  self.assertIn('GOLD_GROUP name=%s cases=%u\\n',s);self.assertIn('GOLD_TO_TALON selector=%u copied=%u soft=%u alpha0=%u cached=%u\\n',s)
 def test_07_six_original_sources_and262byte_reverse(self):
  originals,shim=h.source_bundle(ROOT);self.assertEqual(len(originals),6);self.assertEqual(len(originals['harness.c']),262)
  self.assertEqual({k:h.SHA(v) for k,v in originals.items()},h.SOURCE_PINS);self.assertEqual(h.reverse_shim(shim),originals['harness.c'])
  self.assertEqual(shim.count(b'int inherited_blue_dispatch('),1);self.assertNotEqual(shim,originals['harness.c'])
 def test_08_shim_badmarkers_refused(self):
  originals,shim=h.source_bundle(ROOT)
  for raw in [b'',originals['harness.c']*2,originals['harness.c'].replace(b'int main(',b'int renamed(')]:
   with self.assertRaises(AssertionError):h.outer_shim(raw)
  with self.assertRaises(AssertionError):h.reverse_shim(shim+b'x')
 def test_09_strict_current_helper_no_external_fallback(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'tests').mkdir();(root/'tests/projectile_blue_triplet_native_validation.py').write_bytes(b'changed')
   with self.assertRaises(AssertionError):h.blue_helper(root)
  source=(ROOT/'tests/projectile_gold_pulse_native_validation.py').read_text()
  self.assertNotIn('/workspace/',source);self.assertNotIn('q,receipt',source);self.assertNotIn('receipt.json',source)
 def test_10_legacy629_stdout_exact(self):
  self.assertEqual(h.verify_legacy_stdout(dict(h.LEGACY_STDOUT))['cases'],629)
  for key in h.LEGACY_STDOUT:
   bad=dict(h.LEGACY_STDOUT);bad[key]+=' '
   with self.assertRaises(AssertionError):h.verify_legacy_stdout(bad)
 def test_11_legacy_CRLF_not_normalized(self):
  bad=dict(h.LEGACY_STDOUT);bad['new_blue_stdout']=bad['new_blue_stdout'].replace('\n','\r\n')
  with self.assertRaises(AssertionError):h.verify_legacy_stdout(bad)
 def test_12_old_stdin_pins_and_no_hidden_data(self):
  blue=h.blue_helper(ROOT);self.assertEqual(blue.OLD_STDIN_SHA,'7dedf7066696fc278f5fbb8dfb1462e7b6ac290cb5d08ae5260a6cdabc1ecca7');self.assertEqual(blue.NEW_STDIN_SHA,'a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b')
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(OSError):h.native_inputs(ROOT,Path(td))
 def test_13_fixture_small_synthetic_mutations(self):
  raw=bytes(range(256))+b'X'*44
  self.assertIsNone(h.gold_fixture(raw,168,'missing168'));self.assertIsNone(h.gold_fixture(raw,169,'only168'));self.assertEqual(h.gold_fixture(raw,168,'only168'),raw)
  self.assertEqual(h.gold_fixture(raw,168,'bad168')[128],raw[128]^1);self.assertEqual(h.gold_fixture(raw,168,'header168')[4],raw[4]^1)
  self.assertEqual(len(h.gold_fixture(raw,168,'short168')),299);self.assertEqual(len(h.gold_fixture(raw,168,'trailing168')),301)
 def test_14_exact26_leaves184_new_files(self):
  self.assertEqual(len(h.PACK_NAMES),26);self.assertEqual(len(set(h.PACK_NAMES)),26)
  self.assertEqual(sum(h.gold_fixture(bytes(300),i,n) is not None for n in h.PACK_NAMES for i in h.IDS),184)
 def test_15_actual335_memory_fixtures_original151_exact(self):
  blue=h.blue_helper(ROOT);hdas={}
  for i in h.IDS:
   family='projectile-gold-pulse' if i in h.GOLD else 'projectile-blue-triplet' if i in blue.BLUE else f'projectile{i}'
   hdas[i]=(ROOT/'assets/hd/current-compat'/family/h.hda_name(i,blue)).read_bytes()
  actual=h.fixture_payloads(ROOT,hdas,h.registration(ROOT));old=blue.fixture_payloads({i:hdas[i] for i in blue.SELECTORS})
  self.assertEqual(len(actual),335);self.assertEqual({k:actual[k] for k in old},old)
  for i in h.GOLD:
   bad=dict(hdas);bad[i]=bad[i][:-1]+bytes([bad[i][-1]^1])
   with self.assertRaises(AssertionError):h.fixture_payloads(ROOT,bad,h.registration(ROOT))
 def test_16_registration_exact_root_hash(self):
  r=h.registration(ROOT);self.assertEqual([x['selector'] for x in r['members']],[168,169]);self.assertEqual([x['pixels']['native_alpha0'] for x in r['members']],[314,841])
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=root/h.COVERAGE_PATH;p.parent.mkdir(parents=True);p.write_bytes((ROOT/h.COVERAGE_PATH).read_bytes()+b'x')
   with self.assertRaises(AssertionError):h.registration(root)
 def test_17_no_compiler_process_or_old_objects(self):
  source=(ROOT/'tests/projectile_gold_pulse_native_validation.py').read_text();tree=ast.parse(source)
  imports=[a.name for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom)) for a in n.names]
  self.assertFalse(set(imports)&{'subprocess','os','shutil'});self.assertNotIn('.o\'',source);self.assertNotIn('.d\'',source)
 def test_18_full_member255_bit128_and_native_alpha0_assertions_retained(self):
  s=(ROOT/'tests/projectile_gold_pulse_native_additions.c.inc').read_text()
  for token in ('gold_all8','gold_animation','blue_player_classic(id)','gold_full','gold_transfer','gold_mutations','gold_palettes','gold_lifecycle'):self.assertIn(token,s)
  self.assertIn('255',s);self.assertIn('128',s);self.assertIn('314',s);self.assertIn('841',s)
if __name__=='__main__':unittest.main()
