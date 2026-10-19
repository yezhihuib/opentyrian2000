#!/usr/bin/env python3
"""Finite Data7/8 integration, retained source/art, and runtime closure."""
from pathlib import Path
import hashlib,json,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
# Historical pre-cursor fingerprints are self-contained; private Git history is not required.
HISTORICAL_SHA256={'src/pregame_font.c': 'da3474dc1930771d9fc84a11c2a2f0fce79938f53bf3c3ec70499e40d8eba9b1', 'src/tyrian2.c': '38efa746a6add0ccc02efc7a5fb64138523e31c1e0a0d710470eaaac9f44eb08', 'src/mtrand.c': '9bb519b6b67d990184da25f1d373858760d2952a782c3e850e2f21c972c01f95', 'src/font.c': 'a4d9125a15ac161efb1f97e8bc2f37c537647339902c0f5ad875874150a71cc8', 'src/fonthand.c': '1d6c63d81e02538272a9225f70c26731c86a2048640a41e5857096cdeb03825e', 'src/sprite.c': '4b78f9e792509fcd490549a81a86bf18c2f524368d9bb8d00ee573cc47775a52', 'scripts/export_shop_sprite.py': 'e3cdc66f05edb08ab4a5c426c5f56250192fd0f70d301235c90be504005bca47', 'scripts/export_shop_frame.py': '6cbf878a716593a5897a13c489b487d7c9a38387fa78d1a16913964cfeecfca5', 'assets/shop-frame-v1/shop-frame-metal-v1.hda': '639f0c723e1058628e32b052a9613d09a478ff1d2fb4ce28235a94aaa8235260'}

def historical_source_bytes(test, name):
 data=(ROOT/name).read_bytes()
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

class DataFrameIntegration(unittest.TestCase):
 def test_old_shop_geometry_and_game_sources_unchanged(self):
  for name,digest in HISTORICAL_SHA256.items():
   self.assertEqual(hashlib.sha256(historical_source_bytes(self,name)).hexdigest(),digest,name)
 def test_render_order_and_write_observers(self):
  source=(ROOT/'src/video.c').read_text();frame=source.index('data_frame_present(main_window_renderer');text=source.index('data_text_present(main_window_renderer');cursor=source.index('data_text_cursor_present(main_window_renderer');readback=source.index('asset_debug_readback(main_window_renderer)',frame)
  self.assertLess(frame,text);self.assertLess(text,cursor);self.assertLess(cursor,readback)
  source=(ROOT/'src/render_mirror.c').read_text()
  for method,hook in (('pixel','data_frame_pixel(surface,address);'),('rect','data_frame_rect(s,rect);')):
   body=source[source.index('void render_mirror_'+method+'('):];self.assertLess(body.index(hook),body.index('if(!active'))
  source=(ROOT/'src/game_menu.c').read_text();a=source.index('data_frame_surround_begin(');b=source.index('blit_sprite(VGAScreenSeg, 1, 1, OPTION_SHAPES, 20)',a);c=source.index('data_frame_surround_end(',b);face=source.index('blit_sprite(VGAScreenSeg, face_x, face_y, FACE_SHAPES, face_sprite)',c)
  self.assertLess(a,b);self.assertLess(b,c);self.assertLess(c,face)
 def test_english_cursor_does_not_depend_on_chinese_font(self):
  source=(ROOT/'src/data_text.c').read_text();self.assertIn('(resources_ok || frame_cursor_owner)',source)
  mouse=(ROOT/'src/mouse.c').read_text();self.assertIn('data_text_cursor_frame_owner(data_frame_active(VGAScreen) || data_portrait_active(VGAScreen))',mouse);self.assertIn('data_frame_cursor_restored(VGAScreen)',mouse)
 def test_resource_exact_header_and_no_native_portrait_art(self):
  p=ROOT/'assets/data-frame-v1/data-frame-v1.hda';raw=p.read_bytes();self.assertEqual(len(raw),4096128);self.assertEqual(raw[:4],b'DFM1')
  self.assertEqual(hashlib.sha256(raw).hexdigest(),'585ab4852480e2a4ff3e8df86bbc3a56d25ad797daafda83df54fa4015bc9f5e')
  source=(ROOT/'assets/data-frame-v1/source-v3.png').read_bytes();self.assertEqual(hashlib.sha256(source).hexdigest(),'34c464d5a05d0dd091a4d1cb3a11d53567ab094768bdb8253b27fcd35d53904d')
  self.assertLess(sum(p.stat().st_size for p in (ROOT/'assets/data-frame-v1').glob('*.png')),5*1024*1024)
 def test_windows_and_cli_inventory(self):
  source=(ROOT/'visualc/opentyrian.vcxproj').read_text()
  for name in ('data_frame.c','data_frame.h','data_frame_pins.inc'):self.assertIn(name,source)
  self.assertIn('"data-frame-assets"',(ROOT/'src/params.c').read_text())
 def test_reset_revokes_and_cursor_uses_native_sampler(self):
  frame=(ROOT/'src/data_frame.c').read_text();self.assertIn('release_texture();data_frame_end();',frame);self.assertIn('df.blocked[cell]||(!hd_cursor_active()&&df.cursor_mask[cell])',frame)
  text=(ROOT/'src/data_text.c').read_text();self.assertIn('SDL_RenderCopy(renderer,cursor_texture,NULL,output)',text);self.assertNotIn('cursor_mapped',text)
if __name__=='__main__':unittest.main()
