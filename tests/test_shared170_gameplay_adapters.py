"""Pure-source bounded gameplay audit contracts; no game/original-data execution."""
import ast
import inspect,re
from pathlib import Path
import unittest
import aircraft170_controlled_gameplay as aircraft
import shapesy_bronze356_gameplay as bronze
import build_shared170_gameplay_probe as probe
ROOT=Path(__file__).resolve().parents[1]
class Shared170GameplayAdapters(unittest.TestCase):
    def test_exact_four_instrumented_sources_only(self):
        original={n:(ROOT/n).read_text() for n in aircraft.INSTRUMENTED_PATHS}
        changed=aircraft.instrument_texts(original)
        self.assertEqual(set(changed),set(original));self.assertEqual(len(changed),4)
        for name,text in original.items():self.assertNotEqual(text,changed[name])
        self.assertIn('eDatI>=302&&eDatI<=308)eDatI=170',changed['src/tyrian2.c'])
        self.assertIn('enemy[s].enemytype==170',changed['src/newshf_identity_validation.inc'])
    def test_unconditional_native_writes_and_palette_all256(self):
        text=aircraft.instrument_texts({n:(ROOT/n).read_text() for n in aircraft.INSTRUMENTED_PATHS})
        render=text['src/render_mirror.c'];sprite=text['src/sprite.c']
        for marker in ('native-game-screen.index8','native-vga-screen.index8','native-palette.rgb','for(unsigned i=0;i<256;i++)','if(fwrite(bytes,1,3,f)!=3)abort()'):
            self.assertIn(marker,render)
        self.assertIn('native-blend-writes.tsv',sprite)
        self.assertNotIn('assert(fwrite',render);self.assertNotIn('assert(fprintf',sprite)
    def test_controlled_three_poses_bounded_tick_and_original_support(self):
        text=Path(aircraft.__file__).read_text()
        for marker in ('a.start==362 and a.count==1','bases=(53,15,91)','drawn=={bases[a.pose-1]}','pose_changed[bases[a.pose-1]]>0',"p.add_argument('--build',type=Path,required=True)"):
            self.assertIn(marker,text)
        self.assertNotIn("cmd=['make'",text)
    def test_natural356_environment_never_overrides_actor_pose_or_map(self):
        tree=ast.parse(Path(bronze.__file__).read_text())
        assignments=[n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='e' for t in n.targets)]
        self.assertEqual(len(assignments),1)
        keys=[k.value for k in assignments[0].value.keys if isinstance(k,ast.Constant)]
        self.assertIn('AIRCRAFT170_DIFFERENTIAL_TICK',keys)
        self.assertFalse(any('POSE' in k or 'ACTOR' in k or 'PLACEMENT' in k for k in keys))
        self.assertNotIn('apply_instrumentation',Path(bronze.__file__).read_text())
    def test_instrumentation_reads_only_pose_control_and_output_tick_keys(self):
        keys=set(re.findall(r'getenv\("([A-Z0-9_]+)"\)',inspect.getsource(aircraft.instrument_texts)))
        self.assertEqual(keys,{'AIRCRAFT170_DIFFERENTIAL_POSE','AIRCRAFT170_DIFFERENTIAL_TICK'})
        self.assertIn("controlled_pose_key_present='AIRCRAFT170_DIFFERENTIAL_POSE' in e",Path(bronze.__file__).read_text())
    def test_poisoned_parent_pose_environment_is_removed_without_mutation(self):
        parent={'AIRCRAFT170_DIFFERENTIAL_POSE':'3','PATH':'retained','AIRCRAFT170_DIFFERENTIAL_TICK':'999'}
        result=bronze.natural_environment(parent)
        self.assertNotIn('AIRCRAFT170_DIFFERENTIAL_POSE',result)
        self.assertEqual(parent['AIRCRAFT170_DIFFERENTIAL_POSE'],'3')
        self.assertEqual(result['PATH'],'retained')
        self.assertIn('**natural_environment(env)',Path(bronze.__file__).read_text())
    def test_natural356_requires_actual_scoped_hd_and_old28_contribution(self):
        text=Path(bronze.__file__).read_text()
        for marker in ('a.start in (414,425) and a.count==1 and a.density==8 and a.native_capture',"x['outside356']==0","x['changed_pixels_matching_authored356']>512","x['authored_opaque_pixels_matched_missing356']>512",'assert target and oldrows',"int(x['coverage_mismatch'])==0"):
            self.assertIn(marker,text)
    def test_both_differentials_require_qualified_missing_and_native_equality(self):
        for module in (aircraft,bronze):
            text=Path(module.__file__).read_text()
            for marker in ('assert len(prior)==40',"'interceptor166_newshf','aircraft169_newshf'",'native-game-screen.index8','native-vga-screen.index8','native-palette.rgb','native-blend-writes.tsv',"p.add_argument('--baseline-build',type=Path,required=True"):
                self.assertIn(marker,text)
    def test_build_reuses_only_source_bound_objects_and_never_writes_links(self):
        text=Path(probe.__file__).read_text()
        for marker in ("proof['source_sha256']==source",'inventory(baseline)==source',"units=('render_mirror','tyrian2','sprite')",'if q.stem not in units:os.link','assert not target.exists()',"'already_fresh_objects_unchanged':objects==tree(baseline/'obj')",'verify_instrumented_build(root,a.out,report)'):
            self.assertIn(marker,text)
    def test_all_new_drivers_parse(self):
        for module in (aircraft,bronze,probe):ast.parse(Path(module.__file__).read_text())
if __name__=='__main__':unittest.main()
