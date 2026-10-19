#!/usr/bin/env python3
"""Exact polished Chinese inputs, agreed names, generated text and glyph closure."""
import collections
import hashlib
import json
from pathlib import Path
import re
import struct
import unittest
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets/data-text-zh-CN-v1'
SOURCE=ASSETS/'source-translations'
class DataTextNames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_files=[SOURCE/f'zh-CN-episode-{n}.json' for n in range(1,6)]
        cls.inputs=[json.loads(p.read_text(encoding='utf-8')) for p in cls.input_files]
        cls.rows=[row for d in cls.inputs for row in d['entries']]
        cls.merged=json.loads((ASSETS/'data-text-zh-CN-v1.json').read_text(encoding='utf-8'))
        cls.by_id={row['id']:row for row in cls.rows}
    def test_approved_inputs_and_merged_translation_are_exact(self):
        pins=[('f5d802f9d9adda2b115258601e1977e3f61f2394882d29e24c437158dda0d03e', 42876), ('1172fedaf31d51fe1899465405d9ca443b5320519034cb31ed4ebd8f013b66ff', 10502), ('629105d6995c08261c5a024019958d3d5a9b34ca6309db967abbf9276f6458b3', 16780), ('f3753523039326362255b5e01e997fe165288483655a3aadbcb46e3ddd8d1335', 76754), ('9d7b13a4eb6cbcbdc964fd8ef60bcf466cc97493a832c804fe49440beba9e754', 10117)]
        self.assertEqual([len(d['entries']) for d in self.inputs],[37,12,21,67,12])
        self.assertEqual(len(self.by_id),149)
        self.assertEqual(sum(len(row['paragraphs']) for row in self.rows),936)
        self.assertEqual(sum(not p for row in self.rows for p in row['paragraphs']),14)
        catalog=json.loads((ASSETS/'source-catalog.json').read_text(encoding='utf-8'))['entries']
        self.assertEqual(sum(bool(row['placeholder']) for row in catalog),3)
        self.assertEqual(sum(value.count('~') for row in self.rows for value in [row['title'],row['header'],*row['paragraphs']]),1236)
        for path,(digest,size) in zip(self.input_files,pins):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest)
            self.assertEqual(path.stat().st_size,size)
        self.assertEqual([r['id'] for r in self.merged['entries']],[r['id'] for r in self.rows])
        for row in self.merged['entries']:
            for key in ('id','episode','cube_index','source_sha256','title','header','paragraphs'):
                self.assertEqual(row[key],self.by_id[row['id']][key])
    def test_runtime_dct_has_all_exact_fields_and_occurrence_order(self):
        blob=(ASSETS/'data-text-zh-CN-v1.dct').read_bytes()
        magic,version,count,payload_size,payload_fnv=struct.unpack_from('<4sIIIQ',blob)
        self.assertEqual((magic,version,count,payload_size),(b'DZT1',1,149,len(blob)-24))
        offset=24
        for row in self.merged['entries']:
            ep,occ,*tail=struct.unpack_from('<HHIIIQ',blob,offset);offset+=24
            self.assertEqual((ep,occ),(row['episode'],row['cube_index']))
            lengths=tail[:3]
            self.assertEqual(tail[3],int(row['source_fnv1a64'],16))
            for length,expected in zip(lengths,[row['title'],row['header'],'\n\n'.join(row['paragraphs'])]):
                self.assertEqual(blob[offset:offset+length].decode('utf-8'),expected)
                self.assertEqual(blob[offset+length],0);offset+=length+1
        self.assertEqual(offset,len(blob))
    def test_glossary_and_all_visible_latin_are_reviewed(self):
        glossary=json.loads((SOURCE/'glossary.json').read_text(encoding='utf-8'))['entries']
        self.assertEqual(len(glossary),213)
        self.assertEqual(len({r['canonical_english'] for r in glossary}),213)
        for row in glossary:
            self.assertTrue(re.search('[\u3400-\u9fff]',row['chinese']))
            self.assertTrue(set(row['source_entries']).issubset(self.by_id))
        whitelist=json.loads((SOURCE/'remaining-latin-whitelist.json').read_text(encoding='utf-8'))
        self.assertEqual(whitelist['unclassified'],[])
        self.assertEqual(len(whitelist['occurrences']),89)
        actual=collections.Counter()
        expected=collections.Counter()
        for row in self.rows:
            for field,value in [('title',row['title']),('header',row['header']),*[(f'paragraphs[{i}]',p) for i,p in enumerate(row['paragraphs'])]]:
                for char in re.findall('[A-Za-z]',value):actual[row['id'],field,char]+=1
        for row in whitelist['occurrences']:
            self.assertTrue(row['category']);self.assertTrue(row['reason'])
            entry=self.by_id[row['id']];field=row['field']
            value=entry['paragraphs'][int(field[11:-1])] if field.startswith('paragraphs[') else entry[field]
            self.assertIn(row['literal'].replace('~',''),value.replace('~',''))
            for char in re.findall('[A-Za-z]',row['literal']):expected[row['id'],row['field'],char]+=1
        self.assertEqual(actual,expected)
        self.assertEqual(self.by_id['ep1.cube11']['header'],'特兰森')
        self.assertIn('特兰森·洛克',''.join(self.by_id['ep1.cube11']['paragraphs']))
        self.assertNotRegex(''.join(row['title']+row['header']+''.join(row['paragraphs']) for row in self.rows),r'(?i)Transon|Trent|Microsol|Gencore|Tyrian|Savara')
    def test_concise_aliases_and_formal_personal_identities(self):
        glossary={r['canonical_english']:r for r in json.loads((SOURCE/'glossary.json').read_text(encoding='utf-8'))['entries']}
        aliases={'Ixmucane':'伊克斯','Microsol':'米克罗',
                 'Ixmucane Task Force Alpha':'伊克斯阿尔法特遣队',
                 'Microsol Super Fleet Alpha':'米克罗阿尔法超级舰队',
                 'Microsol Research Control':'米克罗研究控制中心'}
        for english,chinese in aliases.items():
            self.assertEqual(glossary[english]['chinese'],chinese)
            self.assertNotEqual(glossary[english]['previous_chinese'],chinese)
        visible=''.join(row['title']+row['header']+''.join(row['paragraphs']) for row in self.rows)
        self.assertNotIn('伊克斯穆卡内',visible)
        self.assertNotIn('米克罗索尔',visible)
        self.assertEqual(visible.count('特兰森·洛克'),3)
        self.assertEqual(visible.count('~哈布尔~·~沃姆~'),2)
        self.assertIn('特兰森气急败坏',self.by_id['ep3.cube20']['paragraphs'][0])
        self.assertEqual(self.by_id['ep4.cube48']['paragraphs'][0],'特伦特，我是特兰森。')
        self.assertIn('收到了~哈布尔~的消息',self.by_id['ep4.cube18']['paragraphs'][4])
        self.assertEqual(self.by_id['ep4.cube06']['paragraphs'][-1],'特兰森·洛克')
        self.assertIn('~哈布尔~·~沃姆~',self.by_id['ep4.cube04']['paragraphs'][2])
        self.assertIn('~哈布尔~·~沃姆~',self.by_id['ep4.cube07']['paragraphs'][1])
        for english,short in [('Transon Lohk','特兰森'),('Harble Wom','哈布尔')]:
            self.assertEqual(glossary[english]['short_chinese'],short)
        # Emphasis boundaries split components in the stories, so normalize them.
        for identity,english in [('ep4.cube09','Ixmucane Task Force Alpha'),
                                  ('ep4.cube49','Microsol Super Fleet Alpha'),
                                  ('ep4.cube64','Microsol Research Control')]:
            self.assertIn(aliases[english],''.join(self.by_id[identity]['paragraphs']).replace('~',''))
    def test_pinned_font_and_package_cover_all_updated_glyphs(self):
        manifest=json.loads((ASSETS/'data-text-zh-CN-v1-font-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['glyph_count'],1905)
        self.assertEqual(manifest['font_source']['sha256'],'b76b0433203017ca80401b2ee0dd69350349871c4b19d504c34dbdd80541690a')
        self.assertEqual(manifest['font_source']['ttc_index'],2)
        glyphs={r['char'] for r in manifest['glyphs']}
        glossary=json.loads((SOURCE/'glossary.json').read_text(encoding='utf-8'))['entries']
        self.assertTrue(set(''.join(row['chinese'] for row in glossary)+'Exit').issubset(glyphs))
        for row in self.rows:
            self.assertTrue((set(row['title']+row['header']+''.join(row['paragraphs']))-{'~'}).issubset(glyphs))
        self.assertEqual(manifest['catalog']['translation_inputs'],[{'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in self.input_files])
        package=json.loads((ROOT/'packaging/runtime-assets-v1.json').read_text())
        self.assertEqual(package['closure']['data_text_font_glyphs'],1905)
        for row in package['files']:
            if row['group']=='data-text':
                path=ROOT/row['source_path'];self.assertEqual(row['bytes'],path.stat().st_size)
                self.assertEqual(row['sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
