# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os

import pytest

import pymorphy2
from pymorphy2.opencorpora_dict.compile import (
    _to_paradigm,
    convert_to_pymorphy2
)
from pymorphy2.opencorpora_dict.parse import parse_opencorpora_xml
from pymorphy2.dawg import assert_can_create
from pymorphy2 import lang


class TestToyDictionary:

    XML_PATH = os.path.join(
        os.path.dirname(__file__),
        '..',
        'dev_data',
        'toy_dict.xml'
    )

    def test_parse_xml(self):
        dct = parse_opencorpora_xml(self.XML_PATH)
        assert dct.version == '0.92'
        assert dct.revision == '389440'

        assert dct.links[0] == ('5', '6', '1')
        assert len(dct.links) == 13

        assert dct.grammemes[1] == ('NOUN', 'POST', 'СУЩ', 'имя существительное')
        assert len(dct.grammemes) == 114

        assert dct.lexemes['14'] == [('ёжиться', 'INFN,impf,intr')]

        # bad values should be dropped
        assert dct.lexemes['111111'] == []
        assert dct.lexemes['222222'] == []

    def test_convert_to_pymorphy2(self, tmpdir):

        # import logging
        # from pymorphy2.opencorpora_dict.compile import logger
        # logger.setLevel(logging.DEBUG)
        # logger.addHandler(logging.StreamHandler())

        try:
            assert_can_create()
        except NotImplementedError as e:
            raise pytest.skip(str(e))

        # create a dictionary
        out_path = str(tmpdir.join('dicts'))
        options = {
            'min_paradigm_popularity': 0,
            'min_ending_freq': 0,
            'paradigm_prefixes': lang.ru.PARADIGM_PREFIXES,
        }
        convert_to_pymorphy2(self.XML_PATH, out_path,
                             source_name='toy', language_code='ru',
                             overwrite=True, compile_options=options)

        # use it
        morph = pymorphy2.MorphAnalyzer(out_path)
        assert morph.tag('ёжиться') == [morph.TagClass('INFN,impf,intr')]

        # tag simplification should work
        assert morph.tag("ёж")[0] == morph.tag("ванька-встанька")[0]

        # Init tags should be handled correctly
        assert 'Init' in morph.tag("Ц")[0]
        assert 'Init' not in morph.tag("ц")[0]

        # normalization tests
        assert morph.normal_forms('абсурднее') == ['абсурдный']
        assert morph.normal_forms('а') == ['а']


class TestToParadigm(object):

    def test_simple(self):
        lexeme = [
            ["ярче", "COMP,Qual"],
            ["ярчей", "COMP,Qual V-ej"],
        ]
        stem, forms = _to_paradigm(lexeme, lang.ru.PARADIGM_PREFIXES)
        assert stem == "ярче"
        assert forms == (
            ("", "COMP,Qual", ""),
            ("й", "COMP,Qual V-ej", ""),
        )

    def test_single_prefix(self):
        lexeme = [
            ["ярче", "COMP,Qual"],
            ["поярче", "COMP,Qual Cmp2"],
        ]
        stem, forms = _to_paradigm(lexeme, lang.ru.PARADIGM_PREFIXES)
        assert stem == "ярче"
        assert forms == (
            ("", "COMP,Qual", ""),
            ("", "COMP,Qual Cmp2", "по"),
        )

    def test_multiple_prefixes(self):
        lexeme = [
            ["ярче", "COMP,Qual"],
            ["ярчей", "COMP,Qual V-ej"],
            ["поярче", "COMP,Qual Cmp2"],
            ["поярчей", "COMP,Qual Cmp2,V-ej"],
            ["наиярчайший", "ADJF,Supr,Qual masc,sing,nomn"],
        ]
        stem, forms = _to_paradigm(lexeme, lang.ru.PARADIGM_PREFIXES)
        assert stem == 'ярч'

    def test_multiple_prefixes_2(self):
        lexeme = [
            ["подробнейший", 1],
            ["наиподробнейший", 2],
            ["поподробнее", 3]
        ]
        stem, forms = _to_paradigm(lexeme, lang.ru.PARADIGM_PREFIXES)
        assert stem == 'подробне'
        assert forms == (
            ("йший", 1, ""),
            ("йший", 2, "наи"),
            ("е", 3, "по"),
        )

    def test_platina(self):
        lexeme = [
            ["платиновее", 1],
            ["платиновей", 2],
            ["поплатиновее", 3],
            ["поплатиновей", 4],
        ]
        stem, forms = _to_paradigm(lexeme, lang.ru.PARADIGM_PREFIXES)
        assert forms == (
            ("е", 1, ""),
            ("й", 2, ""),
            ("е", 3, "по"),
            ("й", 4, "по"),
        )
        assert stem == 'платинове'

    def test_no_prefix(self):
        lexeme = [["английский", 1], ["английского", 2]]
        stem, forms = _to_paradigm(lexeme, lang.ru.PARADIGM_PREFIXES)
        assert stem == 'английск'
        assert forms == (
            ("ий", 1, ""),
            ("ого", 2, ""),
        )

    def test_single(self):
        lexeme = [["английски", 1]]
        stem, forms = _to_paradigm(lexeme, lang.ru.PARADIGM_PREFIXES)
        assert stem == 'английски'
        assert forms == (("", 1, ""),)


