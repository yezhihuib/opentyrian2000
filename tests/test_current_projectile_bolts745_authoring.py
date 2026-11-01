"""Focused indexed authoring/transport tests; NOT C/native/gameplay proof."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,shutil,struct,sys,tempfile,unittest
ROOT=Path(os.environ.get('BOLTS745_TEST_ROOT',str(Path(__file__).resolve().parents[1])))
sys.path.insert(0,str(ROOT/'scripts'))
import current_projectile_bolts745_compatibility as c
import build_current_projectile_bolts745 as builder

class Bolts745Authoring(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.selection=c.read(ROOT,c.SELECTION);cls.selected,cls.pngs,cls.blobs=c.generate(ROOT,cls.selection);cls.rows=c.rows_for(cls.selected,cls.blobs)
 def temp_root(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);r=Path(t.name)
  for n in c.input_paths(ROOT):
   p=r/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)
  return r
 def mutate_selection(self,edit):
  s=copy.deepcopy(c.SELECTION_SPEC);edit(s)
  with self.assertRaises(ValueError):c.selection(ROOT,json.dumps(s).encode())
 def payload(self,s=7):return bytearray(self.blobs[(1560000+s,8)][28:])
 def changed_payload(self,edit,s=7):
  p=self.payload(s);edit(p)
  with self.assertRaises(ValueError):c.validate_payload(ROOT,s,p)
 def test_authoring_products_current(self):
  self.assertEqual(set(c.load(ROOT)),{r['destination']for r in self.rows})
  for n,b in builder.products(ROOT).items():self.assertEqual(c.read(ROOT,n),b)
 def test_exact_registered_mirror(self):
  a=self.blobs[(1560007,8)][28:];b=self.blobs[(1560045,8)][28:]
  self.assertEqual(b,b''.join(a[4*(y*96+95-x):4*(y*96+96-x)]for y in range(112)for x in range(96)))
 def test_independent_original_rle_witnesses(self):
  ref=c.source_reference(ROOT)
  for s in (7,45):
   src,mask=c.decode_rle(bytes.fromhex(ref[str(s)]['rle_hex']));self.assertEqual(sum(mask),70);self.assertEqual(src,ref[str(s)]['palette_indices_row_major'])
 def test_rle_trailing_truncated_geometry_rejected(self):
  ref=c.source_reference(ROOT);raw=bytes.fromhex(ref['7']['rle_hex'])
  for bad in (raw+b'\0',raw[:-1],b'\xff'+b'\x01'*15+b'\x0f',b''):
   with self.subTest(bad=bad),self.assertRaises(ValueError):c.decode_rle(bad)
 def test_exact_70_cells_4029_pixels_both(self):
  for s in (7,45):
   p=self.payload(s);self.assertEqual(len(c.validate_payload(ROOT,s,p)),70);self.assertEqual(p[3::4].count(255),4029);self.assertEqual(set(p[3::4]),{0,255})
 def test_index_encoding_not_baked_rgb(self):
  p=self.payload();self.assertFalse(any(p[1::4]));self.assertFalse(any(p[2::4]));self.assertEqual(sorted(set(p[0::4])-{0}),[112,113,114,115,116,117,119,120,122,123,125])
 def test_index_palette_roundtrip_and_dynamic_alternate(self):
  # Pure representation test. Runtime palette resolution is a separate native test.
  from PIL import Image
  p=self.payload();palette=c.source_reference(ROOT)['7']['observed_palette_rgb768'];actual=Image.open(ROOT/c.CANONICAL).tobytes()
  resolved=b''.join(bytes(palette[p[i]*3:p[i]*3+3])+b'\xff' if p[i+3] else bytes(4)for i in range(0,len(p),4))
  alternate=b''.join(bytes([p[i],255-p[i],17,255])if p[i+3]else bytes(4)for i in range(0,len(p),4))
  self.assertEqual(resolved,actual);self.assertNotEqual(resolved,alternate);self.assertEqual(resolved[3::4],alternate[3::4])
 def test_raw_registration_matches_accepted_canonical(self):
  im=c.regenerate_canonical(ROOT,c.source_reference(ROOT));self.assertEqual(im.size,(96,112))
  from PIL import Image
  self.assertEqual(im.tobytes(),Image.open(ROOT/c.CANONICAL).tobytes())
 def test_single_canonical_source_contract(self):
  self.assertEqual(c.SELECTION_SPEC['canonical_selector'],7);self.assertEqual(c.SELECTION_SPEC['derived_selector'],45)
  self.assertEqual(sum(n.endswith('registered.png')for n in c.INPUT_PINS),1)
 def test_unknown_identity_and_density(self):
  for i,d in ((1560008,8),(1560007,1),(1560045,4),(True,8),(1560007,True)):
   with self.subTest(i=i,d=d),self.assertRaises(ValueError):c.name(i,d)
 def test_selector_type_and_payload_length(self):
  for s,p in ((True,self.payload()),(45,self.payload()[:-1]),(8,self.payload()),(7,list(self.payload()))):
   with self.subTest(s=s),self.assertRaises(ValueError):c.validate_payload(ROOT,s,p)
 def test_index_not_in_original_set_rejected(self):
  at=next(i for i in range(0,43008,4)if self.payload()[i+3]);self.changed_payload(lambda p:p.__setitem__(at,118))
 def test_reserved_channel_nonzero_rejected(self):
  at=next(i for i in range(0,43008,4)if self.payload()[i+3]);self.changed_payload(lambda p:p.__setitem__(at+1,1));self.changed_payload(lambda p:p.__setitem__(at+2,1))
 def test_nonbinary_alpha_rejected(self):
  at=next(i for i in range(0,43008,4)if self.payload()[i+3]);self.changed_payload(lambda p:p.__setitem__(at+3,254))
 def test_transparent_hidden_rgb_rejected(self):self.changed_payload(lambda p:p.__setitem__(0,112))
 def test_outside_mask_rejected(self):self.changed_payload(lambda p:p.__setitem__(slice(0,4),bytes([112,0,0,255])))
 def test_inside_index_swap_rejected_by_complete_pin(self):
  at=next(i for i in range(0,43008,4)if self.payload()[i+3]);self.changed_payload(lambda p:p.__setitem__(at,113 if p[at]!=113 else 114))
 def test_missing_pixel_rejected(self):
  at=next(i for i in range(0,43008,4)if self.payload()[i+3]);self.changed_payload(lambda p:p.__setitem__(slice(at,at+4),bytes(4)))
 def test_hda_all_header_fields_reject(self):
  b=self.blobs[(1560007,8)]
  for off in (0,4,8,12,16,20,24):
   q=bytearray(b);q[off]^=1
   with self.subTest(off=off),self.assertRaises(ValueError):c.validate_hda(ROOT,1560007,bytes(q))
 def test_hda_trailing_short_reject(self):
  b=self.blobs[(1560007,8)]
  for q in (b[:-1],b+b'\0'):
   with self.assertRaises(ValueError):c.validate_hda(ROOT,1560007,q)
 def test_selection_extra_missing_reject(self):
  self.mutate_selection(lambda s:s.update(extra=True));self.mutate_selection(lambda s:s.pop('encoding'))
 def test_selection_reversed_or_second_source_reject(self):
  self.mutate_selection(lambda s:s.update(canonical_selector=45,derived_selector=7));self.mutate_selection(lambda s:s.update(second_source='other.png'))
 def test_selection_boolean_and_float_reject(self):
  self.mutate_selection(lambda s:s.update(canonical_selector=True));self.mutate_selection(lambda s:s.update(canonical_selector=7.0))
 def test_duplicate_nonfinite_json_rejected(self):
  for raw in (b'{"a":1,"a":1}',b'{"a":NaN}',b'{"a":Infinity}'):
   with self.assertRaises(ValueError):c.parse(raw)
 def test_noncanonical_paths_rejected(self):
  for n in ('../a','/a','a//b','a/./b','a\\b','a:b','a\nb',''):
   with self.subTest(n=n),self.assertRaises(ValueError):c.path(ROOT,n)
 def test_symlink_input_rejected(self):
  r=self.temp_root();p=r/c.CANONICAL;p.unlink();p.symlink_to(ROOT/c.CANONICAL)
  with self.assertRaises(ValueError):c.selection(r,self.selection)
 def test_hardlink_input_rejected(self):
  r=self.temp_root();p=r/c.CANONICAL;extra=p.with_suffix('.copy');p.rename(extra);os.link(extra,p)
  with self.assertRaises(ValueError):c.selection(r,self.selection)
 def test_raw_and_prompt_mutation_rejected(self):
  r=self.temp_root()
  for n in (c.RAW,c.INPUT_ROOT+'/prompt-v1.txt'):
   p=r/n;b=p.read_bytes();p.write_bytes(b+b'!')
   with self.assertRaises(ValueError):c.selection(r,self.selection)
   p.write_bytes(b)
 def test_derivative_mutation_rejected(self):
  r=self.temp_root();p=r/self.rows[0]['source_path'];b=bytearray(p.read_bytes());b[-1]^=1;p.write_bytes(b)
  with self.assertRaises(ValueError):c.load(r)
 def test_header_mapping_mutation_rejected(self):
  r=self.temp_root()
  for n in (c.HEADER,c.MAPPING):
   p=r/n;b=p.read_bytes();p.write_bytes(b+b'!')
   with self.assertRaises(ValueError):c.load(r)
   p.write_bytes(b)
 def test_runtime_rows_exact_pair(self):
  rows=[dict(r,group='gameplay',revision=c.REVISION)for r in self.rows];c.validate_runtime_rows(ROOT,{'files':rows},True)
 def test_rebuilder_preserves_exact_indexed_metadata(self):
  from rebuild_recovered_runtime_manifest import _bolts745_runtime_metadata
  self.assertEqual({r['identity']for r in self.rows},{1560007,1560045})
  for row in self.rows:
   expected=dict(identity=row['identity'],density=8,encoding=c.ENCODING)
   self.assertEqual(_bolts745_runtime_metadata(dict(row,unrelated='not copied')),expected)
   for key in expected:
    missing=dict(row);missing.pop(key)
    with self.subTest(identity=row['identity'],key=key),self.assertRaises(KeyError):_bolts745_runtime_metadata(missing)
 def test_runtime_identity_and_density_cannot_be_omitted(self):
  good=[dict(r,group='gameplay',revision=c.REVISION)for r in self.rows]
  for index in range(2):
   for key in ('identity','density'):
    rows=copy.deepcopy(good);rows[index].pop(key)
    with self.subTest(index=index,key=key),self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':rows},True)
 def test_runtime_missing_duplicate_forged_and_extra_rows_reject(self):
  good=[dict(r,group='gameplay',revision=c.REVISION)for r in self.rows]
  for rows in (good[:1],good+[good[0]], [dict(good[0],sha256='0'*64),good[1]], [dict(good[0],density=True),good[1]], [dict(good[0],revision='other'),good[1]], [dict(good[0],destination='assets/gameplay/ENEMY-PROJECTILE-BOLTS745-7-8.HDA'),good[1]]):
   with self.subTest(rows=rows),self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':rows},True)
 def test_runtime_explicit_index_encoding_required(self):
  good=[dict(r,group='gameplay',revision=c.REVISION)for r in self.rows]
  self.assertEqual(c.SELECTION_SPEC['encoding'],c.ENCODING)
  self.assertEqual(c.ENCODING,'palette-index-r0-g0-binary-alpha-v1')
  for row in self.rows:self.assertEqual(row['encoding'],c.ENCODING)
  for value in (None,'straight-rgba-v1','palette-index-zero-zero-binary-alpha-v1',True):
   rows=copy.deepcopy(good)
   if value is None:rows[0].pop('encoding')
   else:rows[0]['encoding']=value
   with self.subTest(value=value),self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':rows},True)
 def test_historical_manifest_without_family_is_optional(self):
  c.validate_runtime_rows(ROOT,{'files':[]})
  with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':[]},True)
 def test_complete_coverage_argument_cannot_override(self):
  contract=copy.deepcopy(c.COVERAGE_SPEC);contract['members']['7']['opaque_hd_pixels']=1
  with self.assertRaises(ValueError):c.validate_payload(ROOT,7,self.payload(),contract)
 def test_no_unselected_output_in_rows(self):
  b=dict(self.blobs);b[(1560008,8)]=b[(1560007,8)]
  with self.assertRaises(ValueError):c.rows_for(self.selected,b)
 def test_payload_header_finite(self):
  pins={k:c.fnv(v[28:])for k,v in self.blobs.items()};self.assertEqual(c.read(ROOT,c.HEADER),c.payload_header(pins));pins[(1560007,8)]='0'*16
  with self.assertRaises(ValueError):c.payload_header(pins)

if __name__=='__main__':unittest.main()
