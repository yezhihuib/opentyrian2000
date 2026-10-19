#!/usr/bin/env python3
"""Data-local gold whole-run font is reproducible and runtime-bounded."""
from pathlib import Path
import hashlib,importlib.util,json,struct,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('exit_export',ROOT/'scripts/export_data_exit_font.py');EXPORT=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(EXPORT)
class DataExitFont(unittest.TestCase):
 def test_rebuild_and_planes(self):
  base=ROOT/'assets/data-text-zh-CN-v1'
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp)/'out';pins=Path(temp)/'pins';EXPORT.export(out,pins)
   for name in ('data-exit-v1.hda','data-exit-v1.json'):self.assertEqual((out/name).read_bytes(),(base/name).read_bytes())
   self.assertEqual(pins.read_bytes(),(ROOT/'src/data_exit_pins.inc').read_bytes())
  raw=(base/'data-exit-v1.hda').read_bytes();self.assertEqual(raw[:4],b'DEX1')
  version,w,h,size,shadow,payload,reserved=struct.unpack_from('<7I',raw,4)
  self.assertEqual((version,size,shadow,reserved),(1,52,8,0));self.assertEqual(len(raw),64+payload);self.assertEqual(payload,w*h*2)
  alpha=raw[64:64+w*h];roles=raw[64+w*h:]
  self.assertTrue(all((r in range(12,16)) if a else r==0 for a,r in zip(alpha,roles)))
  self.assertGreater(sum(0<a<255 for a in alpha),100);self.assertLess(len(raw),16*1024)
 def test_boundaries_and_closure(self):
  s=(ROOT/'src/data_text.c').read_text()
  self.assertIn('read_resource(directory,"data-exit-v1.hda",DATA_EXIT_BYTES',s)
  self.assertIn('fnv(exit_bytes,n)!=DATA_EXIT_FNV',s)
  self.assertIn('if (!prepare_exit(r)) return;',s)
  self.assertIn('SDL_GetRGB(rgb_palette[index],main_window_tex_format',s)
  self.assertIn('selected_slot==slots',s)
  self.assertNotIn('draw_string(r,dst,"Exit"',s)
  manifest=json.loads((ROOT/'packaging/runtime-assets-v1.json').read_text());rows=[r for r in manifest['files'] if r['source_path'].endswith('/data-exit-v1.hda')];self.assertEqual(len(rows),1)
  data=(ROOT/rows[0]['source_path']).read_bytes();self.assertEqual(rows[0]['sha256'],hashlib.sha256(data).hexdigest());self.assertEqual(rows[0]['bytes'],len(data))
if __name__=='__main__':unittest.main()
