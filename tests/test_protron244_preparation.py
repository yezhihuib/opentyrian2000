"""Finite244 reuse preparation checks; no native/game invocation or generated art."""
from pathlib import Path
import hashlib,json,re,struct,unittest
ROOT=Path(__file__).resolve().parents[1]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def function(s,name):
 start=s.rfind('\n',0,s.index(name+'('))+1;op=s.index('{',start);depth=0
 for end in range(op,len(s)):
  depth+=(s[end]=='{')-(s[end]=='}')
  if not depth:return s[start:end+1]
 raise ValueError('unclosed')
PIN='901b61b1da6f538d6aac9bbd06a2f7d34e5e9d1e4d9df50c3f3eb01b1cd7b452'
RLE='0c5382838382810472838889898783810391828a8c8c8c8b87818102b080868c8e8f8e8c8a85818401b080888c8f8f8f8c8b86838501b081878c8e8f8e8c8a86848701b081848b8c8c8c8a8884898901b08281868989898784888c8b0191838185868484888d8b0272848283888c8d8b0353888a8d8c8b0f'
COLORS=[2381165, 2907509, 3697021, 4289930, 5079698, 5607070, 6396582, 7186098, 8237754, 9092807, 10144719, 10933207, 12247011, 13364203, 14415863, 15728639]
OLD_IDS=(91, 145, 61, 101, 120, 139, 168, 169, 162, 260, 166, 94, 7, 45, 153, 154, 155, 70, 20, 21, 105, 106, 124, 125, 112, 113, 226, 227)
UNCHANGED={'src/render_mirror.c': 'f2fba333b4d229d40fef4110510b42ee5937f8b9f4abe9433ee3d9ac7fe7500e', 'src/entity_draw.c': 'e16290b936f6212c7ce3b6a63d758c6b66ec9a0af269ebccd2cac889c83b4529', 'src/global_green_mirror.inc': '7992448caada923a3e7a4fcc59282c4d86603a503b36dc3ac321b1d84131ca60', 'src/global_green_identity.inc': 'aa6febe5e8c65e872357bd7fa36d16aa0d3beeac59d7a9ef8d58befa4d4006ca', 'src/global_vulcan_mirror.inc': '7f07c65ae3628e81a6b0c58f322c799fc9678679ed2f1a5619d6a6acfe652c1f', 'src/enemy_reuse_mirror.inc': 'ed4dce9e3183c7d5dd31962217849ecebfa46e3fa23cc5f8afd50bc06cf34858', 'src/current_art_payload_pins.h': '241a99017c7eb9f7d999e49b69683abdc9a408762bc0eb1afa91216121fc4d82', 'src/current_protron_payload_pins.h': 'bf982da11154061bdf56683270ef23a12200f014a060cfcf6482b97d31de88fb', 'src/global_asset_registry.h': '0c96a8b30482ecc5224e73de98efbb4e2cf5bbaa3478f717bc9118cf86570b69', 'assets/hd/global-assets-v1/registry.json': 'b224adfc0b12aee5a4753e32aa12e30c8594eb4237727a983148776239162860'}
TYRIAN_BASE='376471c7177b20312694fe44419dc3f9e89653fb9040e1b94cc5c4dcd591204c'
LOADER_BASE='5900e6a48481f1c1efa32b575584de5b6c090ab079cc8a86ea03bc6810c3c795'
OLD_ALIAS_ROWS=[{'bytes': 43036, 'canonical_source': 'assets/hd/current-compat/enemy-orb/enemy-orb112113-113-8.hda', 'density': 8, 'destination': 'assets/global/content/20a9b6480d91a324a4ca375e79f596504103a80f165512fa33d8c5ffeeac7fba.hda', 'encoding': 'rgba-straight-alpha-v1', 'git_blob': 'e46c6fafe8c1090f3f4964b21d183017dc6ce613', 'group': 'global-source-identity', 'identity': 1420113, 'revision': 'canonical-enemy-orb-protron-aliases-v1', 'sha256': '20a9b6480d91a324a4ca375e79f596504103a80f165512fa33d8c5ffeeac7fba', 'source_path': 'assets/hd/global-assets-v1/content/20a9b6480d91a324a4ca375e79f596504103a80f165512fa33d8c5ffeeac7fba.hda'}, {'bytes': 43036, 'canonical_source': 'assets/hd/current-compat/protron/bullet-226-8.hda', 'density': 8, 'destination': 'assets/global/content/231a78b2ebc6a2410da297d05703b4c548f38926e7bd6e6b28c4fe6c4fa7071c.hda', 'encoding': 'rgba-straight-alpha-v1', 'git_blob': 'f6ed73ade096e04d14fb7fd6de212845477fb421', 'group': 'global-source-identity', 'identity': 80226, 'revision': 'canonical-enemy-orb-protron-aliases-v1', 'sha256': '231a78b2ebc6a2410da297d05703b4c548f38926e7bd6e6b28c4fe6c4fa7071c', 'source_path': 'assets/hd/global-assets-v1/content/231a78b2ebc6a2410da297d05703b4c548f38926e7bd6e6b28c4fe6c4fa7071c.hda'}, {'bytes': 43036, 'canonical_source': 'assets/hd/current-compat/enemy-orb/enemy-orb112113-112-8.hda', 'density': 8, 'destination': 'assets/global/content/84546804885d7c602449fe0c4783d1873e60f30a8abde3e3095356fc3d8bd720.hda', 'encoding': 'rgba-straight-alpha-v1', 'git_blob': '505bf63eca854e4003c5e9c796bda6831fdfefbc', 'group': 'global-source-identity', 'identity': 1420112, 'revision': 'canonical-enemy-orb-protron-aliases-v1', 'sha256': '84546804885d7c602449fe0c4783d1873e60f30a8abde3e3095356fc3d8bd720', 'source_path': 'assets/hd/global-assets-v1/content/84546804885d7c602449fe0c4783d1873e60f30a8abde3e3095356fc3d8bd720.hda'}, {'bytes': 43036, 'canonical_source': 'assets/hd/current-compat/protron/enemy-protron-p09-227-8.hda', 'density': 8, 'destination': 'assets/global/content/9de332ec5d8d7f5c0e7eb56445aabebe22897b27a6fde1ee7f36da822076aac7.hda', 'encoding': 'rgba-straight-alpha-v1', 'git_blob': '368dfb72ff27a62e19fc18c99819fcf15fd42502', 'group': 'global-source-identity', 'identity': 1470227, 'revision': 'canonical-enemy-orb-protron-aliases-v1', 'sha256': '9de332ec5d8d7f5c0e7eb56445aabebe22897b27a6fde1ee7f36da822076aac7', 'source_path': 'assets/hd/global-assets-v1/content/9de332ec5d8d7f5c0e7eb56445aabebe22897b27a6fde1ee7f36da822076aac7.hda'}]
class Protron244Preparation(unittest.TestCase):
 def src(self,n):return(ROOT/'src'/n).read_text()
 def test_append_only29_unsigned(self):
  s=self.src('global_projectile91_mirror.inc');pairs=[(int(a),int(b))for a,b in re.findall(r'index==(\d+)\?(\d+)u',function(s,'global_projectile91_member'))];self.assertEqual(pairs,[(i,1<<n)for n,i in enumerate(OLD_IDS+(244,))]);self.assertEqual(sum(b for a,b in pairs),536870911);self.assertIn('UINT_MAX < 536870911u',s);self.assertNotIn('1u<<32',s)
 def test_boolean_owner_and_sparse_unchanged(self):
  s=self.src('global_projectile91_mirror.inc');line=next(x for x in s.splitlines()if x.startswith('static const unsigned global_projectile91_sparse_rgba_members='));self.assertEqual(list(map(int,re.findall(r'(\d+)u',line))),[1<<n for n in range(17,24)]+[1<<27]);self.assertNotIn('268435456',line);self.assertIn('static Uint8 *global_projectile91_owner',self.src('render_mirror.c'))
 def test_exact80244_bytes_one_alias(self):
  raw=(ROOT/'assets/hd/current-compat/protron/bullet-244-8.hda').read_bytes();self.assertEqual(digest(raw),PIN);self.assertEqual(raw,(ROOT/f'assets/hd/global-assets-v1/content/{PIN}.hda').read_bytes());self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',80244,8,12,14,0,0));self.assertEqual(len(raw),43036)
 def test_native97_cells_fractional_no_halo(self):
  r=bytes.fromhex(RLE);o=p=0;mask=[0]*168;used=set()
  while r[o]!=15:
   c=r[o];o+=1;p+=c&15;n=c>>4
   for k in range(n):mask[p+k]=1;used.add(r[o+k])
   p+=n;o+=n
  self.assertEqual((sum(mask),used),(97,set(range(128,144))));alpha=(ROOT/'assets/hd/current-compat/protron/bullet-244-8.hda').read_bytes()[31::4];self.assertEqual(sum(a>0 for a in alpha),6056);self.assertEqual(sum(0<a<255 for a in alpha),6056);self.assertFalse(any(a and not mask[n//96//8*12+n%96//8]for n,a in enumerate(alpha)))
 def test_exact16_live_colors_not_union(self):
  s=self.src('enemy_orb_protron_mirror.inc');block=s.split('if(index==244){',1)[1].split('return true;}',1)[0];values=[int(v,16)for v in re.search(r'colors\[16\]=\{([^}]+)',block)[1].split(',')];self.assertEqual(values,COLORS);self.assertIn('rgb_palette[128+n]',block)
 def test_old_four_loader_inverse_exact(self):
  s=self.src('enemy_orb_protron_mirror.inc');row=' {244u,80244u,"'+PIN+'",CURRENT_PROTRON_80244_D8_PAYLOAD_FNV},\n';self.assertEqual(s.count(row),1);s=s.replace(row,'',1);start=s.index(' if(index==244){');end=s.index('return true;}',start)+len('return true;}\n');s=s[:start]+s[end:];s=s.replace('enemy_orb_protron_specs[5]','enemy_orb_protron_specs[4]').replace('enemy_orb_protron_resources[5]','enemy_orb_protron_resources[4]').replace('i<5;i++','i<4;i++');self.assertEqual(digest(s.encode()),LOADER_BASE)
 def test_independent_fifth_lease_strict_warm(self):
  s=self.src('enemy_orb_protron_mirror.inc')
  for token in ('resources[5]','i<5;i++)free','REAR_REGULAR','REAR_READ(fd,&extra,1)==0','a->index!=index','a->bank!=enemy_orb_protron_specs[k].identity/10000u','strcmp(enemy_orb_protron_resources[k].root,root)','asteroid1_stamp(a->rgba'):self.assertIn(token,s)
  self.assertNotIn('global_green_rgba',s);self.assertNotIn('global_green_head_assets',s)
 def test_used244_dependency_palette_and_legacy(self):
  s=self.src('global_projectile91_mirror.inc');self.assertIn('(!(global_projectile91_used_members&268435456u)||enemy_orb_protron_palette_matches(244))',s);self.assertIn('(!(global_projectile91_used_members&268435456u)||(orb_protron_ordinary_allowed(244)&&enemy_orb_protron_resource(global_asset_directory,244)!=NULL))',s);self.assertIn('return index==226||index==227||index==244;',self.src('enemy_orb_protron_policy.h'))
 def test_original_gameplay_exact_inverse(self):
  s=self.src('tyrian2.c');a='|| (orb_protron_protron_index(sprite) && widget_sonic_legacy_intent()))';b='|| (orb_protron_protron_index(sprite) && widget_sonic_legacy_intent()) || sprite == 244)';self.assertEqual(s.count(a),1);self.assertEqual(digest(s.replace(a,b,1).encode()),TYRIAN_BASE)
 def test_no_green_admission(self):
  p=self.src('enemy_orb_protron_policy.h');self.assertFalse(any('index=='+str(i)in p for i in (214,215,216)));self.assertIn('|| sprite == 214 || sprite == 215 || sprite == 216 ||',self.src('tyrian2.c'))
 def test_original_players_renderer_and_pins_exact(self):
  for name,pin in UNCHANGED.items():
   raw=(ROOT/name).read_bytes()
   if name=='src/render_mirror.c':
    # Only the reviewed declarations and public pre-final calls are additive.
    for added in (b'static bool global_projectile91_pre_final_pixel(SDL_Surface *,Uint8 *);\n',b'static void global_projectile91_pre_final_rect(SDL_Surface *,const SDL_Rect *);\n',b' global_projectile91_pre_final_pixel(surface,address);\n',b' global_projectile91_pre_final_rect(s,rect);\n'):
     self.assertEqual(raw.count(added),1);raw=raw.replace(added,b'',1)
   self.assertEqual(digest(raw),pin,name)
 def test_old_four_package_rows_exact_and_single244(self):
  rows=json.loads((ROOT/'packaging/runtime-assets-v1.json').read_text())['files'];by={x['destination']:x for x in rows}
  for row in OLD_ALIAS_ROWS:self.assertEqual(by[row['destination']],row)
  selected=[x for x in rows if x.get('identity')==80244];self.assertEqual(len(selected),1);self.assertEqual(selected[0]['sha256'],PIN);self.assertEqual(selected[0]['density'],8);self.assertEqual(selected[0]['encoding'],'rgba-straight-alpha-v1')
if __name__=='__main__':unittest.main()
