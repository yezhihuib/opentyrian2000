#!/usr/bin/env python3
"""Complete bounded18-entry presentation with reproducible source-exact art."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,struct,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
# Historical native/source-art fingerprints require no unpublished Git objects.
HISTORICAL_SHA256={'src/sprite.c': '4b78f9e792509fcd490549a81a86bf18c2f524368d9bb8d00ee573cc47775a52', 'src/font.c': 'a4d9125a15ac161efb1f97e8bc2f37c537647339902c0f5ad875874150a71cc8', 'src/fonthand.c': '1d6c63d81e02538272a9225f70c26731c86a2048640a41e5857096cdeb03825e', 'src/mtrand.c': '9bb519b6b67d990184da25f1d373858760d2952a782c3e850e2f21c972c01f95', 'src/tyrian2.c': '38efa746a6add0ccc02efc7a5fb64138523e31c1e0a0d710470eaaac9f44eb08', 'src/pregame_font.c': 'da3474dc1930771d9fc84a11c2a2f0fce79938f53bf3c3ec70499e40d8eba9b1', 'assets/data-frame-v1/data-frame-v1.hda': '585ab4852480e2a4ff3e8df86bbc3a56d25ad797daafda83df54fa4015bc9f5e', 'assets/data-frame-v1/option20-source-support-320x200.bin': '9cf12bc96e544f8f00c78e03f9635dc67164ccb82433847dcac43f2e09544211', 'assets/data-frame-v1/source-v3.png': '34c464d5a05d0dd091a4d1cb3a11d53567ab094768bdb8253b27fcd35d53904d', 'assets/data-portrait-v1/source-face07-v3.png': '646237fab8e96ae5c2400a098aec8c76f19f6e37b1610919faf2fd18213ad7ad', 'assets/data-portrait-v1/face07-v1.hda': '9c861bd247753c3801ee73fd1fe2e8bf518a27550b58b01d311da3d815b450aa', 'assets/data-text-zh-CN-v1/data-text-zh-CN-v1.dzf': 'd124cd1ac996ec152e8f1dc5ac56ddbd09623c5877710d97d24a24dc66cab235', 'assets/data-text-zh-CN-v1/data-exit-v1.hda': 'f0610cbf5be4956b124ea35b5edd0c42b07ae21c76a2b57209b3354527804891'}

def historical_source_bytes(test, name):
 from accepted_later_changes import project_source
 data=project_source("data",name,(ROOT/name).read_bytes())
 if name=='src/pregame_font.c':
  # These four exact, accepted HD-cursor edits are the only permitted delta
  # from the retained native-shop baseline. Validate every edit before undoing it.
  edits=(
   (b'#include "hd_cursor.h"\n',b''),
   (b' for(unsigned p=0;p<SF_N;p++)if(sf.cursor_mask[p]){sf.replay[p]=sf.cursor_index[p];if(!hd_cursor_active())sf.underlay[p]=sf.cursor_index[p];}\n',
    b' for(unsigned p=0;p<SF_N;p++)if(sf.cursor_mask[p])sf.replay[p]=sf.underlay[p]=sf.cursor_index[p];\n'),
   (b' if(metal_visible()||sf.sprite_drawn)return selector_font_output_present_smooth_guarded(renderer,reference,&underlay,scalers[scaler].scaler32,destination,sf.output,&support,hd_cursor_active()?NULL:sf.cursor_mask,radius,sf.metal_blocked);\n',
    b' if(metal_visible()||sf.sprite_drawn)return selector_font_output_present_smooth_guarded(renderer,reference,&underlay,scalers[scaler].scaler32,destination,sf.output,&support,sf.cursor_mask,radius,sf.metal_blocked);\n'),
   (b' return selector_font_output_present(renderer,reference,&underlay,scalers[scaler].scaler32,destination,sf.output,&support,hd_cursor_active()?NULL:sf.cursor_mask,radius);\n',
    b' return selector_font_output_present(renderer,reference,&underlay,scalers[scaler].scaler32,destination,sf.output,&support,sf.cursor_mask,radius);\n'),
  )
  for current,baseline in edits:
   test.assertEqual(data.count(current),1,(name,current))
   data=data.replace(current,baseline,1)
 return data

SPEC=importlib.util.spec_from_file_location('portrait_export',ROOT/'scripts/export_data_portrait.py');EXPORT=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(EXPORT)
class DataPortraitIntegration(unittest.TestCase):
 def test_native_sources_existing_art_and_text_unchanged(self):
  for name,digest in HISTORICAL_SHA256.items():
   self.assertEqual(hashlib.sha256(historical_source_bytes(self,name)).hexdigest(),digest,name)
  # The approved concise-name DCT evolves independently of frozen portrait/font art.
  self.assertEqual(hashlib.sha256((ROOT/'assets/data-text-zh-CN-v1/data-text-zh-CN-v1.dct').read_bytes()).hexdigest(),'974940781a19a8ca6470cb99bbb5437064c36be91942bbc39226fe8837bed2fe')
 def test_all_source_exact_payloads_and_pins_reproduce(self):
  rows=EXPORT.sources();self.assertEqual(len(rows),18)
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp)/'out';pins=Path(temp)/'pins';report=EXPORT.export(out,pins);self.assertEqual(report['portrait_count'],18)
   for face,row in enumerate(rows):
    for suffix in ('hda','json'):
     name=f'face{face:02d}-v1.{suffix}';self.assertEqual((out/name).read_bytes(),(EXPORT.ASSETS/name).read_bytes(),name)
    raw=(out/f'face{face:02d}-v1.hda').read_bytes();w,h=EXPORT.SIZES[face];fields=struct.unpack_from('<15I',raw,4)
    self.assertEqual(raw[:4],b'DPR1');self.assertEqual(len(raw),128+w*h*64);self.assertEqual(fields,(1,320,200,4,w,h,w*4,h*4,*row['anchor'],face,face+1,row['palette_index'],w*h*64,0));self.assertEqual(raw[104:128],bytes(24))
    with EXPORT.Image.open(EXPORT.ASSETS/row['approved_png']) as im:self.assertEqual(raw[128:],im.tobytes())
    self.assertEqual(hashlib.sha256((EXPORT.ASSETS/row['approved_png']).read_bytes()).hexdigest(),row['approved_png_sha256'])
   self.assertEqual(pins.read_bytes(),(ROOT/'src/data_portrait_pins.inc').read_bytes())
 def test_export_rejects_changed_png_manifest_and_geometry(self):
  with tempfile.TemporaryDirectory() as temp:
   asset=Path(temp)/'assets';shutil.copytree(EXPORT.ASSETS,asset)
   with patch.object(EXPORT,'ASSETS',asset):
    original=(asset/'source-pack.json').read_bytes();manifest=json.loads(original)
    manifest['portraits'][15]['anchor'][1]-=1;(asset/'source-pack.json').write_text(json.dumps(manifest))
    with self.assertRaises(ValueError):EXPORT.export(Path(temp)/'rejected',Path(temp)/'pins')
    self.assertFalse((Path(temp)/'rejected').exists());(asset/'source-pack.json').write_bytes(original)
    source=asset/manifest['portraits'][16]['approved_png'];source.write_bytes(source.read_bytes()+b'x')
    with self.assertRaises(ValueError):EXPORT.export(Path(temp)/'rejected',Path(temp)/'pins')
    self.assertFalse((Path(temp)/'rejected').exists())
 def test_capture_render_and_write_ownership_order(self):
  menu=(ROOT/'src/game_menu.c').read_text();capture=menu.index('data_portrait_capture(');native=menu.index('blit_sprite(VGAScreenSeg, face_x, face_y, FACE_SHAPES, face_sprite)',capture);done=menu.index('data_portrait_face_done(',native);self.assertLess(capture,native);self.assertLess(native,done)
  video=(ROOT/'src/video.c').read_text();order=['data_frame_present(main_window_renderer','data_portrait_present(main_window_renderer','data_text_present(main_window_renderer','data_text_cursor_present(main_window_renderer'];offsets=[video.index(x) for x in order];self.assertEqual(offsets,sorted(offsets))
  mirror=(ROOT/'src/render_mirror.c').read_text()
  for name in ('pixel','rect'):
   body=mirror[mirror.index('void render_mirror_'+name+'('):];self.assertLess(body.index('data_portrait_'+name+'('),body.index('if(!active'))
 def test_compiled_bounds_independent_cache_and_full_underlay(self):
  source=(ROOT/'src/data_portrait.c').read_text()
  for check in ('DP_COUNT=18','DP_MAX_W=70','DP_MAX_H=77','DP_N=5390','menu!=7&&menu!=8','face>=DP_COUNT','resources[face].attempted','resources[face].valid','!source_ok(pin,rle,bytes)','dp.blocked[cell]||(!hd_cursor_active()&&dp.cursor_mask[cell])','dp.frame_owned[cell]','data_frame_underlay_sample','data_frame_underlay_ready(s,rgb,format)','dp.transition','palette_ok(dp.pin,rgb,format)','DP_REGULAR','st.st_size!=128+pin->bytes'):self.assertIn(check,source)
  self.assertEqual(source.count('data_frame_underlay_ready(s,rgb,format)'),1)
  self.assertNotIn('mt_rand',source);self.assertNotIn('SDL_FillRect(s',source);self.assertNotIn('SDL_BlitSurface',source)
  self.assertIn('data_portrait_active(VGAScreen)',(ROOT/'src/mouse.c').read_text())
  pins=(ROOT/'src/data_portrait_pins.inc').read_text();self.assertEqual(pins.count('/* FACE'),18)
 def test_runtime_closure_compact_provenance_and_cli(self):
  selected=json.loads((ROOT/'packaging/runtime-selection-v1.json').read_text());expected=[f'assets/data-portrait-v1/face{f:02d}-v1.hda' for f in range(18)];self.assertEqual(selected['data_portrait_runtime_files'],expected)
  manifest=json.loads((ROOT/'packaging/runtime-assets-v1.json').read_text());rows=[r for r in manifest['files'] if r['group']=='data-portrait'];self.assertEqual(len(rows),18);self.assertEqual(manifest['closure']['data_portrait_files'],18)
  for row in rows:self.assertEqual(hashlib.sha256((ROOT/row['source_path']).read_bytes()).hexdigest(),row['sha256'])
  asset=EXPORT.ASSETS;self.assertLess(sum(p.stat().st_size for p in asset.iterdir() if p.is_file()),8*1024**2)
  for name in ('source-pack.json','DATA-PORTRAIT-PROVENANCE.txt','LICENSE-Data-Portrait.txt','imagegen-provenance.txt','remaining17-imagegen-provenance.json'):self.assertTrue((asset/name).is_file())
  source=json.loads((asset/'source-pack.json').read_text());self.assertEqual(len(source['portraits']),18);self.assertEqual(sum(len(p['entries']) for p in source['portraits']),136);self.assertEqual(source['entries_intentionally_without_face'],13)
  project=(ROOT/'visualc/opentyrian.vcxproj').read_text()
  for name in ('data_portrait.c','data_portrait.h','data_portrait_pins.inc'):self.assertIn(name,project)
  for name in ('start-hd.sh','start-hd.ps1'):self.assertIn('--data-portrait-assets=',(ROOT/'packaging'/name).read_text())

class AcceptedCurrentSources(unittest.TestCase):
    def test_current_source_inventory(self):
        from accepted_later_changes import validate_current_sources
        validate_current_sources(ROOT)

if __name__=='__main__': unittest.main()
