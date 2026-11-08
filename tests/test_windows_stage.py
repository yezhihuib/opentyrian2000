"""Source-stage generation tests; not Windows compilation or runtime."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('win_stage',ROOT/'scripts/stage_level2_windows.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class WindowsStageTests(unittest.TestCase):
    def test_exact112_overlay_and_isolated_project(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/'new-stage'
            receipt=module.stage(ROOT,dest,r'C:\deps\SDL2',r'C:\deps\SDL2_net')
            self.assertEqual(receipt['translation_units'],112);self.assertFalse(receipt['build_started']);self.assertFalse(receipt['game_started'])
            xml=ET.parse(dest/'level2-family.vcxproj');ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'}
            c=xml.findall('.//m:ClCompile[@Include]',ns);self.assertEqual(len(c),112);self.assertEqual(len({x.attrib['Include'] for x in c}),112)
            text=(dest/'level2-family.vcxproj').read_text()
            for forbidden in ('CopyPropsTemplates','user.props','sdl_paths.props','opentyrian.sln','libcrypto','OpenSSL'):
                self.assertNotIn(forbidden,text)
            self.assertIn('ImportDirectoryBuildProps',text);self.assertIn('ImportDirectoryBuildTargets',text)
            rc=xml.find('.//m:ResourceCompile/m:AdditionalIncludeDirectories',ns)
            self.assertEqual(rc.text,'$(MSBuildProjectDirectory)\\visualc')
            self.assertIn('bcrypt.lib',text);self.assertIn('TARGET_WIN32',text);self.assertNotIn('TARGET_UNIX',text)
            self.assertIn('$(MSBuildProjectDirectory)\\bin\\',text);self.assertIn('$(MSBuildProjectDirectory)\\obj\\',text)
            for name,source in receipt['source_origins'].items():
                self.assertEqual((dest/'src'/name).read_bytes(),(ROOT/source).read_bytes())
            self.assertTrue((dest/'src/b313_platform.h').is_file())
            for name in ('tyrian.cfg','tyrian.sav','opentyrian.cfg'):self.assertFalse((dest/name).exists())
            with self.assertRaises(ValueError):module.stage(ROOT,dest,r'C:\deps\SDL2',r'C:\deps\SDL2_net')
    def test_reject_bad_roots_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/'never-created'
            for invalid in ('relative','C:drive-relative',r'C:\evil;value',r'C:\$(evil)'):
                with self.assertRaises(ValueError):module.stage(ROOT,dest,invalid,r'C:\deps\SDL2_net')
                self.assertFalse(dest.exists())
            with self.assertRaises(ValueError):module.stage(ROOT,ROOT/'never-stage',r'C:\deps\SDL2',r'C:\deps\SDL2_net')
    def test_launcher_guards_remain_intact_and_build_is_opt_in(self):
        launch=(ROOT/'scripts/launch_level2_family.py').read_text();build=(ROOT/'scripts/build_level2_windows.ps1').read_text()
        self.assertIn('Windows profile isolation is not implemented',launch)
        self.assertIn('if (-not $Build)',build);self.assertNotIn('Start-Process',build);self.assertNotIn('Copy-Item',build)
        self.assertIn('$plan.validation_error=$_.Exception.Message',build)
        self.assertLess(build.index('$plan.validation_error='),build.index('| Set-Content'))
        self.assertIn('Existing build output',build);self.assertIn('BUILT_NOT_RUN',build)
if __name__=='__main__':unittest.main()
