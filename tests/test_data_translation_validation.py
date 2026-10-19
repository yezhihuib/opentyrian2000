#!/usr/bin/env python3
"""Reflow preserves source passages and explicit empty paragraph semantics."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from data_translation_validation import validate_paragraphs

class DataTranslationStructure(unittest.TestCase):
    def test_allows_splitting_and_joining_within_passage(self):
        validate_paragraphs(['one'],['甲','乙'],'split')
        validate_paragraphs(['one','two'],['甲乙'],'join')
    def test_preserves_explicit_empty_separators(self):
        validate_paragraphs(['one','','two'],['甲','乙','','丙'],'blank')
        validate_paragraphs(['','one','','','two',''],['','甲','乙','','','丙',''],'multiple')
    def test_rejects_added_removed_or_shifted_empty_separators(self):
        for before,after in [(['one'],['甲','','乙']),(['one','','two'],['甲乙']),(['one','','two'],['','甲乙']),(['one','','two'],['甲乙',''])]:
            with self.subTest(before=before,after=after),self.assertRaises(ValueError):validate_paragraphs(before,after,'invalid')
    def test_preserves_bodyless_placeholder_and_todo(self):
        validate_paragraphs([],[],'bodyless')
        for after in [['甲'],['']]:
            with self.assertRaises(ValueError):validate_paragraphs([],after,'bodyless')
    def test_rejects_removed_content_passage(self):
        for after in [[],[''],['甲','','']]:
            with self.assertRaises(ValueError):validate_paragraphs(['one','','two'],after,'missing')
    def test_rejects_malformed_paragraph_array(self):
        for after in [None,'甲',[1],['甲',' ']]:
            with self.assertRaises(ValueError):validate_paragraphs(['one'],after,'type')
if __name__=='__main__':unittest.main()
