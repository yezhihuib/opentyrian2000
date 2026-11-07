import importlib.util
from pathlib import Path
import tempfile
import unittest
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/build_redvent_pair.py'
spec = importlib.util.spec_from_file_location('redvent', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class RedventTests(unittest.TestCase):
    def test_truncated_shapes_rejected(self):
        with self.assertRaises(ValueError):
            mod.decode_shapes(b'\x00\x01')

    def test_checked_input_rejects_changed_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'x'
            p.write_bytes(b'input')
            self.assertEqual(mod.checked(p, mod.digest(b'input'), 5), b'input')
            with self.assertRaisesRegex(ValueError, 'hash'):
                mod.checked(p, 'wrong')
            with self.assertRaisesRegex(ValueError, 'size'):
                mod.checked(p, mod.digest(b'input'), 4)

    def test_symlink_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'source'
            source.write_bytes(b'input')
            link = Path(temp) / 'link'
            link.symlink_to(source)
            with self.assertRaisesRegex(ValueError, 'non-symlink'):
                mod.checked(link, mod.digest(b'input'))

    def test_opaque_exact_native_border_and_generated_center(self):
        native = Image.new('RGB', (24, 28), (32, 40, 48))
        raw = Image.new('RGB', (600, 700), (80, 60, 40))
        output, gains = mod.register(raw, native)
        self.assertEqual(output.size, (192, 224))
        self.assertEqual(output.getextrema()[3], (255, 255))
        count = 0
        for y in range(224):
            for x in range(192):
                if min(x, y, 191 - x, 223 - y) <= 7:
                    self.assertEqual(output.getpixel((x, y)), (32, 40, 48, 255))
                    count += 1
        self.assertEqual(count, 6400)
        self.assertNotEqual(output.getpixel((96, 112))[:3], (32, 40, 48))
        self.assertTrue(all(.75 <= x <= 1.25 for x in gains))

    def test_output_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, 'exists'):
                mod.build('missing', 'missing', temp)

    def test_wrong_inputs_create_no_output(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'new'
            with self.assertRaises(ValueError):
                mod.build(Path(temp) / 'data', Path(temp) / 'raw', output)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
