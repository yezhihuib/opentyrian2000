"""Windows staged preprocessor default regression; no game or MSVC execution."""
import importlib.util,json,tempfile,unittest,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('data_dir_stage',ROOT/'scripts/stage_level2_windows.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class WindowsDataDirectoryMacroTests(unittest.TestCase):
    def test_stage_matches_canonical_windows_string_and_receipt(self):
        ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'}
        canonical=ET.parse(ROOT/'visualc/opentyrian.props.template').find('.//m:TYRIAN_DIR',ns).text
        self.assertEqual(json.loads(canonical),r'C:\TYRIAN')
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/'fresh-stage03'
            receipt=module.stage(ROOT,dest,r'C:\deps\SDL2',r'C:\deps\SDL2_net')
            tree=ET.parse(dest/'level2-family.vcxproj')
            macros=tree.find('.//m:ClCompile/m:PreprocessorDefinitions',ns).text.split(';')
            values=[x.split('=',1)[1] for x in macros if x.startswith('TYRIAN_DIR=')]
            self.assertEqual(values,[canonical])
            self.assertEqual(json.loads(values[0]),r'C:\TYRIAN')
            self.assertIn('TYRIAN_DIR='+canonical,receipt['defines'])
            self.assertEqual(json.loads((dest/'STAGE.json').read_text())['defines'],receipt['defines'])
            self.assertNotIn('/usr/local',values[0]);self.assertNotIn('Users',values[0])
            self.assertFalse(receipt['build_started']);self.assertFalse(receipt['game_started'])
            # Explicit runtime data still has precedence; source is not patched.
            copied=(dest/'src/file.c').read_text()
            self.assertLess(copied.index('custom_data_dir,',copied.index('const char *data_dir')),copied.index('TYRIAN_DIR,',copied.index('const char *data_dir')))
if __name__=='__main__':unittest.main()
