"""Finite combined-epoch inverse contracts; stdlib and repository bytes only."""
from pathlib import Path
import hashlib,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_warning_source_bridge as warning
import current_tank_muzzle_source_bridge as muzzle
class CombinedSourceBridge(unittest.TestCase):
 def inventory(self):return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((ROOT/'src').rglob('*'))if p.is_file()and p.name!='current_tank_shell_payload_pins.h'}
 def test_four_whole_inputs_exact_inverse_to_muzzle(self):
  for name,pin in warning.MUZZLE_PINS.items():
   with self.subTest(name=name):self.assertEqual(warning.sha(warning.restore(name,(ROOT/name).read_text()).encode()),pin)
 def test_all_warning_hunks_missing_duplicate_unrelated_rejected(self):
  for name,pairs in warning.INVERSE.items():
   text=(ROOT/name).read_text()
   for current,prior in pairs:
    for bad in (text.replace(current,'',1),text+current,text+'\n'):
     with self.subTest(name=name),self.assertRaises(ValueError):warning.restore(name,bad)
 def test_original_font28_inverse_constant_unchanged(self):
  from test_warning_hud_preparation import FONT_INVERSE,restore_font
  self.assertEqual(warning.INVERSE['src/gameplay_hud_font_mirror.inc'],FONT_INVERSE)
  self.assertEqual(len(FONT_INVERSE),28)
  self.assertEqual(warning.restore('src/gameplay_hud_font_mirror.inc',(ROOT/'src/gameplay_hud_font_mirror.inc').read_text()),restore_font((ROOT/'src/gameplay_hud_font_mirror.inc').read_text()))
 def test_seven_actual_reads_and_composed_historical_digest(self):
  sources=self.inventory();seen=[]
  def read(name):seen.append(name);return(ROOT/name).read_bytes()
  result=muzzle.project(sources,read)
  self.assertEqual(seen,list(warning.COMBINED_PINS)+[n for n in muzzle.MUZZLE_PINS if n not in warning.COMBINED_PINS])
  self.assertEqual(len(seen),7);self.assertEqual(muzzle.inventory_digest(result),muzzle.BASE_SOURCE_DIGEST)
 def test_unknown_mixed_missing_inventory_rejects_before_read(self):
  source=self.inventory();name=next(iter(warning.COMBINED_PINS));missing=dict(source);del missing[name]
  mixed=dict(source);mixed[name]=warning.MUZZLE_PINS[name];changed=dict(source);changed[name]='0'*64
  for bad in (missing,mixed,changed,dict(source,unexpected='0'*64)):
   with self.assertRaises(ValueError):muzzle.project(bad,lambda n:self.fail('Invalid inventory performed source I/O'))
 def test_actual_bytes_must_match_all_seven_authorized_inputs(self):
  sources=self.inventory()
  for target in dict.fromkeys((*warning.COMBINED_PINS,*muzzle.MUZZLE_PINS)):
   with self.subTest(target=target),self.assertRaises(ValueError):muzzle.project(sources,lambda name:(ROOT/name).read_bytes()+(b'\n'if name==target else b''))
 def test_previous_muzzle_epoch_preserves_original_six_read_path(self):
  source,restored=warning.project(self.inventory(),lambda name:(ROOT/name).read_bytes());seen=[]
  def read(name):seen.append(name);return restored[name]if name in restored else(ROOT/name).read_bytes()
  result=muzzle.project(source,read)
  self.assertEqual(seen,list(muzzle.MUZZLE_PINS));self.assertEqual(muzzle.inventory_digest(result),muzzle.BASE_SOURCE_DIGEST)
if __name__=='__main__':unittest.main()
