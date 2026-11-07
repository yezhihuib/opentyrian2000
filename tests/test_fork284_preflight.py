import contextlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preflight', ROOT/'scripts/preflight_fork284.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    # Synthetic structural fixture, never copied from original game data.
    rows = [(0,0,0,0,0,0,0,0)] * 731
    for n,t,x in m.ORIGINS:rows[n-1]=(t,7,284,x,2,0,0,0)
    raw = b''.join(struct.pack('<HBhhbbbB', *row) for row in rows)
    section = struct.pack('<cc3HHH',b'D',b'Z',1,1,1,0,731)+raw
    offsets = (18,19,20,20+len(section))
    return struct.pack('<H4i',4,*offsets)+b'xx'+section+b'x',raw


class ForkPreflightTests(unittest.TestCase):
    def test_synthetic_structure_and_pinned_full_stream(self):
        data,raw=fixture()
        self.assertEqual(m.parse_events(data),raw)
        # Real archives may carry an explicit final EOF offset.
        self.assertEqual(m.parse_events(data[:-1]),raw)
        # Production pin must reject this synthetic stream.
        with self.assertRaisesRegex(ValueError,'hash mismatch'):m.inspect_stream(raw)
        with patch.object(m,'STREAM_FNV64',m.fnv64(raw)):
            self.assertTrue(m.inspect_stream(raw)['four_origins_match'])
            bad=bytearray(raw);bad[700*11]^=1
            with self.assertRaisesRegex(ValueError,'hash mismatch'):m.inspect_stream(bad)
        bad=bytearray(raw);bad[11*11+7]=0
        with patch.object(m,'STREAM_FNV64',m.fnv64(bad)):
            with self.assertRaisesRegex(ValueError,'origin fields'):m.inspect_stream(bad)

    def test_invalid_offsets_counts_and_truncation(self):
        data,_=fixture()
        variants=[b'',data[:10],data[:-100]]
        for index,value in ((2,-1),(2,3),(2,len(data)+1),(3,21)):
            bad=bytearray(data);struct.pack_into('<i',bad,2+index*4,value);variants.append(bad)
        for at,value in ((28,65535),(30,732)):
            bad=bytearray(data);struct.pack_into('<H',bad,at,value);variants.append(bad)
        for bad in variants:
            with self.subTest(size=len(bad)):
                with self.assertRaises(ValueError):m.parse_events(bad)

    def test_asset_hash_header_and_transparency(self):
        data=m.ASSET.read_bytes();report=m.inspect_asset(data)
        self.assertEqual(sum(report['alpha_pixels'].values()),192*224)
        self.assertGreater(report['alpha_pixels']['transparent'],0)
        self.assertGreater(report['alpha_pixels']['partial'],0)
        for at in (0,4,100):
            bad=bytearray(data);bad[at]^=1
            with self.assertRaises(ValueError):m.inspect_asset(bad)
        with self.assertRaises(ValueError):m.inspect_asset(data[:-1])

    def test_main_success_read_only_and_cli_errors_from_other_cwd(self):
        data,raw=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);(directory/'tyrian1.lvl').write_bytes(data)
            before={p.name:p.read_bytes() for p in directory.iterdir()}
            output=io.StringIO()
            with patch.object(m,'STREAM_FNV64',m.fnv64(raw)),contextlib.redirect_stdout(output):
                self.assertEqual(m.main(['--data',str(directory)]),0)
            report=json.loads(output.getvalue());self.assertEqual(report['status'],'PASS')
            self.assertFalse(report['runtime_integrated']);self.assertNotIn('rows',report['events'])
            self.assertEqual(before,{p.name:p.read_bytes() for p in directory.iterdir()})
            run=subprocess.run([sys.executable,str(ROOT/'scripts/preflight_fork284.py'),'--data','.'],cwd=tmp,capture_output=True,text=True)
            self.assertEqual(run.returncode,1);self.assertEqual(json.loads(run.stdout)['status'],'FAIL');self.assertNotIn('Traceback',run.stderr)
            (directory/'tyrian1.lvl').unlink()
            run=subprocess.run([sys.executable,str(ROOT/'scripts/preflight_fork284.py'),'--data','.'],cwd=tmp,capture_output=True,text=True)
            self.assertEqual(run.returncode,1);self.assertEqual(json.loads(run.stdout)['status'],'FAIL')
            (directory/'large').write_bytes(b'1234')
            with self.assertRaisesRegex(ValueError,'limit'):m.read_bounded(directory/'large',3)


if __name__=='__main__':unittest.main()
