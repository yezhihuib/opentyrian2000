"""Compile the actual opt-in readers; a top-only request must not enable bottom."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ClipSwitchTests(unittest.TestCase):
    def test_production_lower_half_dispatch_boundary(self):
        source = (ROOT / 'experimental/level2-family/src/tyrian2.c').read_text()
        self.assertRegex(source, r'if \(enemy\[i\]\.ey > -26 && enemy\[i\]\.ey < 182\)')

    @unittest.skipUnless(shutil.which('cc'), 'requires a C compiler')
    def test_independent_exact_opt_in(self):
        functions = []
        for edge in ('top', 'bottom'):
            source = (ROOT / 'experimental/level2-family/src' /
                      f'lamp272_{edge}_clip_mirror.inc').read_text()
            match = re.search(r'static bool lamp272_' + edge +
                              r'_clip_requested\(void\)\s*\{[^}]*\}', source)
            self.assertIsNotNone(match)
            functions.append(match.group())
        harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <string.h>
static const char *top, *bottom;
static const char *test_getenv(const char *key) {
 if (!strcmp(key,"LAMP272_TOP_CLIP_ENABLE")) return top;
 if (!strcmp(key,"LAMP272_BOTTOM_CLIP_ENABLE")) return bottom;
 assert(0); return 0;
}
#define getenv test_getenv
''' + '\n'.join(functions) + r'''
int main(void) {
 const char *values[]={0,"","0","1","true","01","1 "};
 for (unsigned i=0;i<7;i++) for(unsigned j=0;j<7;j++) {
  top=values[i]; bottom=values[j];
  assert(lamp272_top_clip_requested()==(i==3));
  assert(lamp272_bottom_clip_requested()==(j==3));
 }
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            c = Path(directory) / 'switches.c'
            binary = Path(directory) / 'switches'
            c.write_text(harness)
            subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror',
                            '-pedantic', str(c), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    unittest.main()
