#!/usr/bin/env python3
"""Exact four-row runtime projection; old destination scopes stay frozen."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

import accepted_later_changes as a
sys.path.insert(0, str(a.ROOT/'scripts'))
import current_sonic_compatibility as c
from build_current_art import fnv

BASE = '013560593b3ea9e033906116b849a9508f6d621a'

class SonicRuntimeProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sonic_paths=a.sonic_runtime_input_paths()
        if len(sonic_paths) != 14: raise AssertionError('unexpected Sonic proof closure')
        cls.baseline = {name:(a.ROOT/name).read_bytes()
                        for name in sonic_paths | a.guided_runtime_input_paths()}
        cls.current = json.loads((a.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files']
        cls.previous = json.loads(subprocess.check_output(
            ['git','show',BASE+':packaging/runtime-assets-v1.json'],cwd=a.ROOT))['files']

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sonic-runtime-inverse-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name,raw in self.baseline.items(): self.write(name,raw)
        self.rows = copy.deepcopy(self.current)

    def write(self,name,raw):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        return p

    def assert_previous_rows(self, rows):
        self.assertEqual([r['destination'] for r in rows],[r['destination'] for r in self.previous])
        for current,previous in zip(rows,self.previous):
            if current['destination']=='CURRENT-PRODUCTION-VALIDATION.json':
                # Guided adds one generated C header, updating only this current
                # binding's content metadata; historical source authority stays pinned.
                fields={'sha256','git_blob','bytes'}
                self.assertEqual({k:v for k,v in current.items() if k not in fields},
                                 {k:v for k,v in previous.items() if k not in fields})
            else:
                self.assertEqual(current,previous)

    def test_exact_four_row_inverse_preserves_all_previous_rows(self):
        original=copy.deepcopy(self.rows)
        self.assert_previous_rows(a.before_sonic_runtime(self.rows,self.root))
        self.assertEqual(self.rows,original)
        self.assertEqual(len(self.previous),1025)
        self.assertEqual(len(self.rows),1029)
        self.assertEqual({r['destination'] for r in self.rows}-{r['destination'] for r in self.previous},
                         {'assets/gameplay/bullet-%d-8.hda'%i for i in (105,106,124,125)})
        self.assertEqual(a.sha(('\n'.join(sorted(r['destination'] for r in self.previous))+'\n').encode()),
                         a.PRE_SONIC_RUNTIME_DESTINATIONS_SHA)

    def test_missing_all_missing_one_duplicate_fifth_and_replaced_old_path_rejected(self):
        one=next(r for r in self.rows if r['destination'] in a.SONIC_RUNTIME_DESTINATIONS)
        absent=[r for r in self.rows if r['destination']!=one['destination']]
        all_absent=[r for r in self.rows if r['destination'] not in a.SONIC_RUNTIME_DESTINATIONS]
        extra=dict(one,destination='assets/gameplay/bullet-107-8.hda')
        replacement=copy.deepcopy(self.rows)
        next(r for r in replacement if r['destination'] not in a.SONIC_RUNTIME_DESTINATIONS)['destination']='unknown-runtime-member'
        for rows in (absent,all_absent,self.rows+[one],self.rows+[extra],replacement):
            with self.subTest(length=len(rows)),self.assertRaises(AssertionError):
                a.before_sonic_runtime(rows,self.root)

    def test_each_runtime_field_and_unknown_field_rejected(self):
        mutations={'source_path':'assets/hd/current-compat/sonic/not-approved.hda',
                   'destination':'assets/gameplay/bullet-107-8.hda',
                   'group':'sonic-optin','revision':'frozen-or-unreviewed',
                   'bytes':0,'git_blob':'0'*40,'sha256':'0'*64,'identity':80105}
        for destination in a.SONIC_RUNTIME_DESTINATIONS:
            for field,value in mutations.items():
                rows=copy.deepcopy(self.rows)
                next(r for r in rows if r['destination']==destination)[field]=value
                with self.subTest(destination=destination,field=field),self.assertRaises(AssertionError):
                    a.before_sonic_runtime(rows,self.root)

    def test_every_local_input_is_required_and_tampering_rejected(self):
        for name,raw in self.baseline.items():
            p=self.root/name
            for mutation in ('missing','changed'):
                try:
                    if mutation=='missing':p.unlink()
                    else:p.write_bytes(raw+b'broken')
                    with self.subTest(name=name,mutation=mutation),self.assertRaises((ValueError,AssertionError,OSError)):
                        a.before_sonic_runtime(self.rows,self.root)
                finally:p.write_bytes(raw)

    def test_coherent_current_edit_changes_only_pair_and_preserves_old_rows(self):
        selected=json.loads((self.root/c.SELECTION).read_bytes())
        request=copy.deepcopy(selected);request.pop('resources');request['schema']=c.CANDIDATE_SCHEMA
        request['version']='runtime-projection-master105-edit'
        master=next(r for r in request['masters'] if r['selector']==105)
        with Image.open(self.root/master['source_png']) as original:
            channels=original.split()
            edited=Image.merge('RGBA',(channels[0].point(lambda x:(x+37)%256),*channels[1:]))
        stream=io.BytesIO();edited.save(stream,format='PNG');raw=stream.getvalue()
        self.write(master['source_png'],raw);master['source_sha256']=a.sha(raw)
        selected,pngs,blobs=c.generate(self.root,json.dumps(request).encode(),candidate=True)
        self.write(c.SELECTION,json.dumps(selected).encode())
        for name,raw in pngs.items():self.write(name,raw)
        mapping=[];pins={};changed=set()
        for pair,raw in blobs.items():
            source=c.ROOT+'/'+c.name(*pair);destination='assets/gameplay/'+c.name(*pair)
            if self.baseline[source]!=raw:changed.add(pair)
            self.write(source,raw);pins[pair]=fnv(raw[28:])
            mapping.append(dict(identity=pair[0],density=pair[1],source_path=source,destination=destination,sha256=a.sha(raw)))
            row=next(r for r in self.rows if r['destination']==destination)
            row.update(bytes=len(raw),sha256=a.sha(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
        self.write(c.MAPPING,json.dumps(dict(schema='opentyrian-current-sonic-compatibility-v1',selection=c.SELECTION,version=selected['version'],files=mapping)).encode())
        self.write(c.HEADER,c.payload_header(pins))
        self.assertEqual(changed,{(80105,8),(80106,8)})
        self.assert_previous_rows(a.before_sonic_runtime(self.rows,self.root))
        # A self-consistent current transport proof does not waive stale rows.
        with self.assertRaises(AssertionError):a.before_sonic_runtime(self.current,self.root)

if __name__=='__main__':unittest.main()
