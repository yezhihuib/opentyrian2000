"""Execute the independent finite Pulse compositor with synthetic data only."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class PulseTransactionTest(unittest.TestCase):
    def test_ordered_transaction(self):
        with tempfile.TemporaryDirectory() as directory:
            exe = str(Path(directory) / 'pulse-transaction')
            command = [os.environ.get('CC', 'cc'), '-std=c11', '-Wall', '-Wextra', '-Werror',
                       '-I' + str(ROOT / 'experimental/level2-family/src'),
                       str(ROOT / 'tests/family_pulse_transaction.c'), '-o', exe]
            if os.environ.get('PULSE_TEST_SANITIZE') == '1':
                command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
            subprocess.run(command, check=True, capture_output=True)
            result = subprocess.run([exe], check=True, capture_output=True, text=True)
            self.assertIn('435 transaction cases passed', result.stdout)

if __name__ == '__main__':
    unittest.main()
