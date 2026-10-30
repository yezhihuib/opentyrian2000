"""Pure final-epoch native helper contracts; never compile or run a game.

An external candidate may be exercised through an explicitly recorded in-memory
source/asset overlay. Installed runs read only their actual current repository;
there is no hidden prior-checkout fallback or old object/executable lookup.
"""
from pathlib import Path
import ast,collections,hashlib,inspect,json,re,struct,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import projectile_blue_triplet_native_validation as d


def companion():return Path(d.__file__).with_name('projectile_blue_triplet_native_additions.c.inc').read_text()
def hdas():
    return {i:(ROOT/('assets/hd/current-compat/projectile'+str(i) if i in (91,145,61) else 'assets/hd/current-compat/projectile-blue-triplet')/d.HDA_NAMES[i]).read_bytes() for i in d.SELECTORS}
def cfunc(text,name):
    match=re.search(r'\b'+re.escape(name)+r'\([^;{}]*\)\s*\{',text);assert match,name
    start=match.start();pos=text.index('{',match.start());level=1;at=pos+1
    while level:
        if text[at]=='{':level+=1
        elif text[at]=='}':level-=1
        at+=1
    return text[start:at]


class BlueNativeFinalEpochAdapter(unittest.TestCase):
    def c_format(self,prefix):
        matches=re.findall(r'printf\("('+re.escape(prefix)+r'[^"\n]+)"',companion())
        self.assertEqual(len(matches),1);return matches[0].replace(r'\n','\n')
    def stdout(self,cases=365):
        lines=''.join(self.c_format('BLUE101_ZERO_NATIVE ')%p for p in (0,1))
        lines+=self.c_format('BLUE101_ZERO_HD ')
        lines+=''.join(self.c_format('BLUE_TO_TALON ')%(i,*d.TRANSFER_PINS[i],cached) for i in d.BLUE for cached in (0,1))
        return lines+self.c_format('PASS blue triplet native lifecycle: ')%(cases,1)

    def test_closed_six_members_26_blue_and_eight_legacy_packs(self):
        self.assertEqual(d.SELECTORS,(91,145,61,101,120,139));self.assertEqual(d.BLUE,(101,120,139))
        self.assertEqual(len(d.PACK_NAMES),26);self.assertEqual(len(set(d.PACK_NAMES)),26)
        self.assertEqual(set(d.PACK_NAMES),{'valid','old-only'}|{f'{k}{i}' for i in d.SELECTORS for k in ('missing','bad')}|{f'{k}{i}' for i in d.BLUE for k in ('only','header','short','trailing')})
        self.assertEqual(d.PACKS,(('valid',(),None),('missing91',(91,),None),('missing145',(145,),None),('bad145',(),145),('bad91',(),91),('missing61',(61,),None),('bad61',(),61),('only61',(91,145),None)))

    def test_each_missing_and_singleton_fixture_is_exact(self):
        b=bytes(range(256))*170
        for i in d.SELECTORS:
            for j in d.SELECTORS:self.assertEqual(d.fixture_bytes(b,j,'missing'+str(i)),None if i==j else b)
        for i in d.BLUE:
            for j in d.SELECTORS:self.assertEqual(d.fixture_bytes(b,j,'only'+str(i)),b if i==j else None)
        for i in d.SELECTORS:self.assertEqual(d.fixture_bytes(b,i,'old-only'),b if i not in d.BLUE else None)

    def test_each_bad_payload_mutates_one_byte_and_not_header(self):
        b=bytes(range(256))*170
        for i in d.SELECTORS:
            for j in d.SELECTORS:
                got=d.fixture_bytes(b,j,'bad'+str(i));self.assertEqual(len(got),len(b))
                self.assertEqual([k for k,(x,y) in enumerate(zip(b,got)) if x!=y],[128] if i==j else [])

    def test_header_length_suffix_distinct_and_bad_selector_rejected(self):
        b=bytes(range(256))*170
        for i in d.BLUE:
            got=d.fixture_bytes(b,i,'header'+str(i));self.assertEqual([k for k in range(len(b)) if b[k]!=got[k]],[4])
            self.assertEqual(d.fixture_bytes(b,i,'short'+str(i)),b[:-1]);self.assertEqual(d.fixture_bytes(b,i,'trailing'+str(i)),b+b'!')
        for selector,leaf in ((True,'valid'),(999,'valid'),(101,'unknown'),(101,'../valid')):
            with self.assertRaises(AssertionError):d.fixture_bytes(b,selector,leaf)

    def test_all_six_actual_hda_payloads_have_selected_header_and_sha(self):
        for i,b in hdas().items():
            self.assertEqual(len(b),43036);self.assertEqual(hashlib.sha256(b).hexdigest(),d.HDA_SHA[i])
            self.assertEqual(b[:28],struct.pack('<4s6I',b'HDR1',d.HDA_ID[i],8,12,14,0,0))
        self.assertEqual(d.HDA_SHA[101],'4f1cb932fa0418f3236d8240a3012ec19d65ab3d33a862190a75f53302db8ac6')
        self.assertEqual(d.HDA_SHA[120],'e8935de840d09ed83e65206664ba3a4ddf25b11764ba2b6038ac752140dcb83b')

    def test_fixture_payloads_regular_bytes_151_and_original264_content_unchanged(self):
        original=hdas();result=d.fixture_payloads(original)
        self.assertEqual(len(result),151);self.assertEqual(sum(k.startswith('legacy264/') for k in result),19)
        self.assertEqual(sum(k.startswith('blue-packs/') for k in result),132)
        for name,missing,bad in d.PACKS:
            for i in (91,145,61):
                key=f'legacy264/{name}/{d.HDA_NAMES[i]}'
                if i in missing:self.assertNotIn(key,result)
                else:
                    expected=bytearray(original[i])
                    if i==bad:expected[128]^=1
                    self.assertEqual(result[key],bytes(expected))
        self.assertTrue(all(type(v) is bytes for v in result.values()))
        self.assertTrue(all(not Path(k).is_absolute() and '..' not in Path(k).parts for k in result))

    def test_fixture_payloads_fail_closed_before_any_writes(self):
        original=hdas()
        for i in d.SELECTORS:
            modified=dict(original);modified[i]=original[i]+b'!'
            with self.assertRaises(AssertionError):d.fixture_payloads(modified)
            modified=dict(original);modified[i]=bytes([original[i][0]^1])+original[i][1:]
            with self.assertRaises(AssertionError):d.fixture_payloads(modified)
        with self.assertRaises(AssertionError):d.fixture_payloads({i:b for i,b in original.items() if i!=101})
        with self.assertRaises(AssertionError):d.fixture_payloads({**original,999:original[101]})
        source=inspect.getsource(d.fixture_payloads)
        for forbidden in ('.write_text(','.write_bytes(','.mkdir(','.symlink_to(','.unlink(','open('):self.assertNotIn(forbidden,source)

    def test_exact_original264_harness_and_entry_sources(self):
        sources=d.harness_sources(ROOT)
        self.assertEqual(set(sources),{'inherited145_harness.c','accepted_projectile61_native_additions.c.inc','accepted61_wrapper.c','projectile61_native_additions.c.inc','projectile_blue_triplet_native_additions.c.inc','harness.c'})
        for name,pin in (('inherited145_harness.c',d.LEGACY_SHA),('accepted_projectile61_native_additions.c.inc',d.COMPANION_SHA),('accepted61_wrapper.c',d.WRAPPER_SHA),('projectile_blue_triplet_native_additions.c.inc',d.BLUE_COMPANION_SHA)):
            self.assertEqual(hashlib.sha256(sources[name]).hexdigest(),pin)
        self.assertEqual(sources['projectile61_native_additions.c.inc'],b'#include "accepted_projectile61_native_additions.c.inc"\n#define main inherited61_dispatch\n')
        self.assertTrue(sources['harness.c'].startswith(b'#include "accepted61_wrapper.c"\n#undef main\n'))
        self.assertIn(b'return inherited61_dispatch(argc,argv);',sources['harness.c'])

    def test_changed_new_companion_is_not_silently_consumed(self):
        with self.assertRaises(AssertionError):d.harness_sources(ROOT,companion().encode()+b'\n')
        self.assertEqual(d.harness_sources(ROOT,companion().encode()),d.harness_sources(ROOT))

    def test_original264_stdout_exact_and_any_change_rejected(self):
        self.assertEqual(d.verify_legacy_stdout(d.LEGACY107_STDOUT,d.LEGACY61_STDOUT)['total_cases'],264)
        self.assertEqual(d.verify_legacy_stdout(d.LEGACY107_STDOUT,d.LEGACY61_STDOUT)['total_assertions'],1045894)
        for old,new in ((d.LEGACY107_STDOUT+'\n',d.LEGACY61_STDOUT),(d.LEGACY107_STDOUT,d.LEGACY61_STDOUT.replace('267','266')),('',d.LEGACY61_STDOUT)):
            with self.assertRaises(AssertionError):d.verify_legacy_stdout(old,new)

    def test_original_input_and_source_pins_are_explicit(self):
        self.assertEqual(d.OLD_STDIN_SHA,'7dedf7066696fc278f5fbb8dfb1462e7b6ac290cb5d08ae5260a6cdabc1ecca7')
        self.assertEqual(d.NEW_STDIN_SHA,'a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b')
        self.assertEqual(set(d.DATA_SHA),{'tyrian.shp','tyrianc.shp','palette.dat'})
        self.assertEqual(d.COMPANION_SHA,'5f80d681e84a6dff20873f7f05bb3a02e3fd0f22013edf2b5fbf133d36c51cfe')
        text=inspect.getsource(d.native_inputs)
        for term in ("bytes((v<<2)|(v>>4) for v in pal)",'hashlib.sha256(old).hexdigest()==OLD_STDIN_SHA','hashlib.sha256(new).hexdigest()==NEW_STDIN_SHA'):
            self.assertIn(term,text)
        self.assertNotIn('write',text)

    def test_actual_c_stdout_schema_exact_with_two_native_and_one_hd_proof(self):
        got=d.parse_blue_stdout(self.stdout());self.assertEqual(got['new_cases'],365)
        self.assertEqual(len(got['native_zero_rows']),2);self.assertEqual(len(got['hd_zero_rows']),1)
        self.assertEqual(got['zero_samples_each_phase'],384);self.assertEqual(len(got['actual_transfer_rows']),6)

    def test_wrong_case_or_transfer_old_epoch_count_duplicate_or_missing_rejected(self):
        raw=self.stdout()
        for bad in (self.stdout(364),self.stdout(366),raw.replace('copied=1756','copied=1866'),raw.replace('soft=1721','soft=1859'),raw.replace('copied=1864','copied=0'),raw+raw.splitlines()[3]+'\n','\n'.join(raw.splitlines()[1:])):
            with self.assertRaises(AssertionError):d.parse_blue_stdout(bad)

    def test_any_missing_or_weakened384_phase_or_underlay_identity_rejected(self):
        raw=self.stdout()
        for bad in (raw.replace('pattern=1','pattern=0'),raw.replace('prior=120','prior=139'),raw.replace('draw=384','draw=383'),raw.replace('finish=384','finish=383'),raw.replace('cache=384','cache=383'),raw.replace('BLUE101_ZERO_HD','OLD_ZERO_HD'),raw+'extra\n'):
            with self.assertRaises(AssertionError):d.parse_blue_stdout(bad)

    def test_fixed365_case_guard_and_setup_cardinality_unchanged(self):
        text=companion();self.assertIn('CHECK(cases-first_case==365)',text);self.assertEqual(text.count('blue_setup();'),23)
        groups=(6,15,12,24,12,24,5,9,42,86,3,66,20,12,15,1,6,7)
        self.assertEqual(sum(groups),365);self.assertEqual(264+sum(groups),629)
        self.assertIn('blue_positive();blue_bounds();blue_mixed();blue_absence();blue_palettes();blue_mutations(xb,xn);blue_callbacks();blue_cold_scope(xb,xn);blue_transfer();blue_lifecycle();',text)

    def test_exact_new_histograms_and_transparent_six_cell_geometry(self):
        arrays=hdas();zero=((12,0),(12,11),(13,0),(13,1),(13,10),(13,11));indices={((cy*8+sy)*96+cx*8+sx) for cy,cx in zero for sy in range(8) for sx in range(8)}
        self.assertEqual(len(indices),384)
        for i in indices:self.assertEqual(arrays[101][28+4*i:28+4*i+4],b'\0'*4)
        for i,want in ((101,(9240,152,1360)),(120,(10231,0,521)),(139,(7703,159,2890))):
            a=arrays[i][31::4];self.assertEqual((sum(0<x<255 for x in a),a.count(255),a.count(0)),want)
            self.assertIn(f'soft=={want[0]}&&opaque=={want[1]}&&clear=={want[2]}',companion())
        self.assertIn('{{12,0},{12,11},{13,0},{13,1},{13,10},{13,11}}',companion())

    def test_zero_oracle_requires_mask_alpha0_native_index_owner_used_and_phase(self):
        body=cfunc(companion(),'blue_zero_verify')
        for term in ('mask[cell]&&!a[0]&&!a[1]&&!a[2]&&!a[3]','==source[cell]','global_projectile91_owner[n]==1&&hd_owner[n]==1','global_projectile91_used_members&8u','global_projectile91_contributed','!global_projectile91_fault&&!global_projectile91_call.live','ready&&last_output_valid&&global_projectile91_cached','at(output,px-24*8,py)','==want[count]','CHECK(count==384)'):
            self.assertIn(term,body)
        self.assertNotIn('blueobs_tags',body);self.assertNotIn('rgba[4*i+3]>0',body)

    def test_native_positive_uses_captured_underlay_and_real_finish_cache(self):
        body=cfunc(companion(),'blue_positive')
        self.assertLess(body.index('blue_zero_native(under,zero_want)'),body.index('blue_draw(blue_new[s]'))
        self.assertIn('blue_zero_verify(110,80,zero_want,false)',body)
        self.assertEqual(body.count('blue_zero_verify(110,80,zero_want,true)'),2)
        self.assertIn('global_projectile91_check_cache();CHECK(ready&&last_output_valid)',body)
        self.assertIn('blue_player_classic(blue_new[s])',body)

    def test_mixed_zero_underlay_final_assertions_only_when101_is_last_writer(self):
        body=cfunc(companion(),'blue_mixed');pair=body.split('/* Every member')[0]
        self.assertIn('if(second==101){Uint32 before[96*112];blue_canvas_snapshot(before);blue_zero_tile(before,zero_want);if(first==120)blue_zero_owned(110,80);}',pair)
        self.assertEqual(pair.count('if(second==101)blue_zero_verify(110,80,zero_want,true)'),2)
        self.assertNotIn('if(first==101)blue_zero_verify',pair)
        self.assertIn('blue_output_expected(want)',body)
        self.assertIn('if(first==120&&second==101)printf("BLUE101_ZERO_HD',pair)
        step=cfunc(companion(),'blue_mix_step')
        self.assertIn('blue_zero_tile(before,zero_want)',step);self.assertIn('alpha(before[i],rgba+4*i)',step)

    def test_existing_resource_source_and_palette_mutations_keep_failure_guards(self):
        body=cfunc(companion(),'blue_mutations')
        for term in ('k<11','k<10','cached<2','a->rgba[100]^=1','a->rgba=NULL','livebank[100]^=1','spriteSheet8.size--','xmas=true','game_screen->pitch=321','global_projectile91_observed_preflight();CHECK(global_projectile91_fault)','CHECK(!ready&&!last_output_valid)'):
            self.assertIn(term,body)
        self.assertIn('blue_zero_verify(110,80,zero_want,false)',body);self.assertIn('blue_zero_verify(80,80,zero_want,true)',body)
        palette=cfunc(companion(),'blue_palettes');self.assertIn('blue_zero_verify(110,80,zero_want,false)',palette)
        self.assertIn('rgb_palette[colors[c]]^=1;if(cached)global_projectile91_check_cache();else finish();CHECK(!ready&&!last_output_valid)',palette)

    def test_all_six_real_nonempty_orders_used63_earlier_payload_failure_retained(self):
        body=cfunc(companion(),'blue_mixed')
        for row in ('{91,145,61,120,139,101}','{145,91,61,101,120,139}','{61,91,145,139,120,101}','{101,91,145,61,139,120}','{120,91,145,61,101,139}','{139,91,145,61,101,120}'):
            self.assertIn(row,body)
        for term in ('CHECK(common==100&&global_projectile91_used_members==63u','CHECK(blue_mix_step','blue_asset(blue_ids[first])->rgba[100]^=1','CHECK(!ready&&!last_output_valid)'):
            self.assertIn(term,body)

    def test_real_talon_fixed_position_new_counts_soft_rgb_witness_no_search(self):
        body=cfunc(companion(),'blue_transfer')
        for term in ('expected[]={1756,1864,1481},soft_expected[]={1721,1864,1454}','{{1,76,235,253},{17,79,228,29},{0,53,212,253}}','blit_sprite2x2(classic,107,78,spriteSheet9,233)','render_mirror_global_player_ship(game_screen,107,78','blit_sprite2x2(game_screen,107,78','prior[i]=global_projectile91_owner[n]&&blue_asset(id)->rgba[4*i+3]>0','copied>0&&copied==expected[s]&&soft==soft_expected[s]','global_talon_owner[witness]&&global_talon_foreign[witness]','*at(canvas,960,648)==want','*at(output,960-24*8,648)==want','blue_asset(id)->rgba[100]^=1','CHECK(!ready&&!last_output_valid)'):
            self.assertIn(term,body)
        self.assertNotIn('while(',body)

    def test_native_palette_state_rng_callbacks_scope_and_lifecycle_not_removed(self):
        text=companion()
        for name in ('blue_draw_bank','blue_player_classic'):
            b=cfunc(text,name)
            for term in ('!memcmp(classic->pixels,game_screen->pixels,64000)','rng==mt_state_fingerprint()','!memcmp(pal,rgb_palette,sizeof(pal))','!memcmp(actors,enemy,sizeof(enemy))','!memcmp(shots,enemyShot,sizeof(shots))'):self.assertIn(term,b)
        for name in ('blue_callbacks','blue_cold_scope','blue_lifecycle','blue_absence','blue_bounds'):self.assertIn(name,text)
        self.assertIn('spriteSheet8=(Sprite2_array){xn,(Uint8 *)xb}',text)
        self.assertIn('CHECK(!global_projectile91_used_members&&!global_projectile91_contributed)',text)

    def test_helper_has_no_old_object_or_executable_consumer_or_execution_entry(self):
        text=Path(d.__file__).read_text();tree=ast.parse(text)
        self.assertNotIn('def main(',text)
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):self.assertFalse({a.name for a in n.names}&{'subprocess','os','shutil','signal'})
        for forbidden in ('reused83_objects_sha256','native_linked_objects_sha256','fresh_dependency_file_sha256','fresh_dependency_sha256','opentyr-test.o','renderer-link','read_bytes(old_stdin)','write_bytes(old_stdin)','write_bytes(new_stdin)'):
            self.assertNotIn(forbidden,text)
        self.assertIn('projectile_blue_triplet_fresh_native_validation.py',text)
        self.assertIn('No compiler, subprocess, native process, old object/ELF',d.__doc__)

    def test_native_api_pure_source_and_fixture_calls_do_not_write(self):
        for name in ('native_inputs','harness_sources','legacy_harness','accepted_wrapper','fixture_payloads','parse_blue_stdout','verify_legacy_stdout'):
            text=inspect.getsource(getattr(d,name))
            for forbidden in ('.write_text(','.write_bytes(','.mkdir(','.unlink(','.symlink_to(','subprocess','Popen','system('):self.assertNotIn(forbidden,text)
        self.assertEqual(d.SAN,('-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie'))


if __name__=='__main__':unittest.main()
